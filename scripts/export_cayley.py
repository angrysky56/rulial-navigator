import gzip
import sqlite3

import numpy as np
import torch
from tqdm import tqdm

from rulial.learning.hypercube import generate_hypercube_graph
from rulial.learning.sheaf_learner import SheafLearner


def rule_str_to_index(rule_str: str) -> int:
    """Convert 'B.../S...' string to 18-bit integer index."""
    b_part, s_part = rule_str.split("/")
    b_digits = [int(c) for c in b_part[1:]]
    s_digits = [int(c) for c in s_part[1:]]

    idx = 0
    for d in b_digits:
        idx |= 1 << d
    for d in s_digits:
        idx |= 1 << (d + 9)
    return idx


def load_data(db_path="data/atlas_full_v6_gpu.db"):
    print(f"Loading data from {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    rows = cur.execute("SELECT rule_str, wolfram_class FROM explorations").fetchall()
    conn.close()

    num_nodes = 2**18
    labels = torch.zeros(num_nodes, dtype=torch.long)
    mask = torch.zeros(num_nodes, dtype=torch.bool)

    for r_str, wc in rows:
        idx = rule_str_to_index(r_str)
        if wc == 4:
            labels[idx] = 1
        else:
            labels[idx] = 0
        mask[idx] = True
    return labels, mask


def index_to_rule_str(idx: int) -> str:
    b_set = []
    s_set = []
    for b in range(9):
        if (idx >> b) & 1:
            b_set.append(str(b))
    for s in range(9):
        if (idx >> (s + 9)) & 1:
            s_set.append(str(s))
    return f"B{''.join(b_set) if b_set else ''}/S{''.join(s_set) if s_set else ''}"


def export_cayley(output_path="data/rule_space.nq.gz"):
    print("Exporting Rule Space for Cayley...")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 1. Load Model
    model = SheafLearner(hidden_dim=32).to(device)
    model.load_state_dict(
        torch.load("data/sheaf_model.pt", map_location=device, weights_only=True)
    )
    model.eval()

    # 2. Generate Graph
    edge_index, x = generate_hypercube_graph(18)
    edge_index = edge_index.to(device)
    x = x.to(device)

    # 3. Compute Restrictions (Layer 1)
    # We want to know which edges are "Resonant" (+1) vs "Tense" (-1)
    print("Computing Sheaf Geometry...")

    row, col = edge_index
    # Process in chunks to save memory
    num_edges = edge_index.shape[1]
    chunk_size = 100000

    restrictions = []

    with torch.no_grad():
        # Get Node Embeddings from Encoder first
        h = torch.relu(model.encoder(x))

        for i in tqdm(range(0, num_edges, chunk_size)):
            chunk_row = row[i : i + chunk_size]
            chunk_col = col[i : i + chunk_size]

            edge_input = torch.cat([h[chunk_row], h[chunk_col]], dim=-1)
            # Use layer 1 learner
            rho = torch.tanh(model.sheaf1.restriction_learner(edge_input))
            restrictions.append(rho.cpu().numpy())

    restrictions = np.concatenate(restrictions)

    # 4. Load Metadata (Wolfram Class, H)
    conn = sqlite3.connect("data/atlas_full_v6_gpu.db")
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT rule_str, wolfram_class, harmonic_overlap FROM explorations"
    ).fetchall()
    metadata = {r[0]: (r[1], r[2]) for r in rows}
    conn.close()

    # 5. Write N-Quads
    print(f"Writing N-Quads to {output_path}...")

    with gzip.open(output_path, "wt") as f:
        # Write Nodes
        # Only write nodes that are in our atlas OR are connected by strong edges?
        # Writing all 262k nodes is fine.

        nodes_written = set()

        # Helper to format quad
        def write_quad(s, p, o, label=""):
            # Escape strings? Cayley assumes typical IRIs
            # Use <rule:B3/S23> format

            # Helper to format term
            def fmt(term):
                return term if term.startswith('"') else f"<{term}>"

            s_fmt = fmt(s)
            p_fmt = fmt(p)
            o_fmt = fmt(o)

            if label:
                f.write(f"{s_fmt} {p_fmt} {o_fmt} <{label}> .\n")
            else:
                f.write(f"{s_fmt} {p_fmt} {o_fmt} .\n")

        # Write Edges with Sheaf Type
        # Only write "interesting" edges to keep graph sparse?
        # Threshold: |rho| > 0.8

        edge_count = 0
        src_np = edge_index[0].cpu().numpy()
        dst_np = edge_index[1].cpu().numpy()

        for i in tqdm(range(num_edges)):
            rho = restrictions[i].item()

            if abs(rho) < 0.5:
                continue  # Weak connection (neutral)

            u_idx = src_np[i]
            v_idx = dst_np[i]

            # Use smaller index as source to deduplicate undirected edges?
            # Creating Directed edges for Cayley visualization flow

            u_str = index_to_rule_str(u_idx)
            v_str = index_to_rule_str(v_idx)

            rel = "resonant" if rho > 0 else "tense"

            # Edge quad
            write_quad(f"rule:{u_str}", f"rel:{rel}", f"rule:{v_str}")
            edge_count += 1

            nodes_written.add(u_str)
            nodes_written.add(v_str)

        # Write Node Properties
        for rule_str in nodes_written:
            if rule_str in metadata:
                wc, h = metadata[rule_str]
                write_quad(f"rule:{rule_str}", "prop:wolfram_class", f'"{wc}"')
                if h is not None:
                    write_quad(
                        f"rule:{rule_str}", "prop:harmonic_overlap", f'"{h:.3f}"'
                    )

                # Add "is_goldilocks"
                if 0.3 <= (h or 0) <= 0.6:
                    write_quad(f"rule:{rule_str}", "type:goldilocks", "true")
            else:
                write_quad(f"rule:{rule_str}", "prop:wolfram_class", '"unknown"')

    print(f"Exported {edge_count} significant edges to {output_path}")


if __name__ == "__main__":
    export_cayley()
