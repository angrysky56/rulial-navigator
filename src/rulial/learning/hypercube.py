from typing import Tuple

import torch


def generate_hypercube_graph(dim: int = 18) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Generate the adjacency list (edge_index) for the hypercube graph Q_n.

    Args:
        dim: Dimension of the hypercube (18 for rule space).

    Returns:
        edge_index: (2, num_edges) LongTensor of edges.
        nodes: (num_nodes, dim) FloatTensor of node features (bit vectors).
    """
    num_nodes = 2**dim

    # 1. Generate node features (binary representation of index)
    # This is equivalent to rule vectors
    indices = torch.arange(num_nodes)

    # Clever trick to get bit representation
    mask = 2 ** torch.arange(dim)
    nodes = (indices.unsqueeze(-1).bitwise_and(mask).ne(0)).float()

    # 2. Generate edges
    # For each node i, its neighbors are i XOR 2^k for k in range(dim)

    # We can do this efficiently using broadcasting
    # neighbors = indices.unsqueeze(1) ^ mask.unsqueeze(0)  # (2^18, 18) matrix of neighbors

    # Flatten to get source and dest
    # src = indices.repeat_interleave(dim)
    # dst = neighbors.flatten()

    # However, for 2^18 (262k nodes), this might be memory intensive on GPU directly.
    # 262144 * 18 * 8 bytes ≈ 37 MB. That's fine.

    src = indices.repeat_interleave(dim)
    dst = (indices.unsqueeze(1) ^ mask.unsqueeze(0)).flatten()

    edge_index = torch.stack([src, dst], dim=0)

    return edge_index, nodes


if __name__ == "__main__":
    edge_index, nodes = generate_hypercube_graph(18)
    print(f"Graph generated: {nodes.shape[0]} nodes, {edge_index.shape[1]} edges")
    print(f"Node 0 neighbors: {edge_index[1][edge_index[0] == 0]}")
