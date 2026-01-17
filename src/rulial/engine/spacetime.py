import networkx as nx
import numpy as np


class SpacetimeUtil:
    """Utilities for handling CA space-time diagrams."""

    @staticmethod
    def to_bytes(spacetime: np.ndarray) -> bytes:
        """Convert space-time diagram to bytes for rigid compression analysis."""
        return spacetime.tobytes()

    @staticmethod
    def to_ascii(
        spacetime: np.ndarray, char_zero: str = " ", char_one: str = "█"
    ) -> str:
        """Convert space-time diagram to ASCII visual representation."""
        lines = []
        for row in spacetime:
            line = "".join(char_one if cell else char_zero for cell in row)
            lines.append(line)
        return "\n".join(lines)

    @staticmethod
    def extract_causal_graph(spacetime: np.ndarray) -> nx.DiGraph:
        """
        Extract the causal structure as a Directed Acyclic Graph (DAG).
        Nodes are (t, x) tuples. Edges represent causal influence (light cone).

        In ECA (radius=1), cell (t, x) is influenced by (t-1, x-1), (t-1, x), (t-1, x+1).
        This graph captures the 'flow' of information for TDA/ZX analysis.
        """
        rows, cols = spacetime.shape
        G = nx.DiGraph()

        # Decision: Track ALL cells.
        # In a Cellular Automaton, '0' is not just 'void', it is a state carrying information
        # (e.g., a wire carrying 'False'). A full causal graph (Logic Circuit) must include
        # the propagation of 0s to correctly model the light cone and logic gates (ZX Calculus).
        #
        # For purely topological analysis of 'active structures' (gliders), use
        # `SpacetimeUtil.active_cell_cloud` or the EntailmentCone simplification.

        for t in range(1, rows):
            for x in range(cols):
                # Target node
                target = (t, x)
                G.add_node(target, position=x, layer=t, state=spacetime[t, x])

                # Source parents (periodic boundary conditions)
                prev_t = t - 1
                parents = [
                    (prev_t, (x - 1) % cols),
                    (prev_t, x),
                    (prev_t, (x + 1) % cols),
                ]

                for p in parents:
                    G.add_edge(p, target)

        return G

    @staticmethod
    def active_cell_cloud(spacetime: np.ndarray) -> np.ndarray:
        """
        Extract coordinates of active cells (value 1) as a point cloud.
        Used for Persistent Homology (TDA).

        Returns:
            np.ndarray of shape (N, 2) where N is number of active cells.
            Columns are [time, position].
        """
        # np.argwhere returns (row, col) which maps to (time, position)
        return np.argwhere(spacetime == 1)
