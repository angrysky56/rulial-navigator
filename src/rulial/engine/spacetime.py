import numpy as np
import networkx as nx
from typing import Optional

class SpacetimeUtil:
    """Utilities for handling CA space-time diagrams."""
    
    @staticmethod
    def to_bytes(spacetime: np.ndarray) -> bytes:
        """Convert space-time diagram to bytes for rigid compression analysis."""
        return spacetime.tobytes()
    
    @staticmethod
    def to_ascii(spacetime: np.ndarray, char_zero: str = " ", char_one: str = "█") -> str:
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
        
        # Add nodes for all active cells (or all cells? Usually we track 1s for structure)
        # Tracking all cells creates a huge lattice.
        # Tracking only active cells (1s) captures the "particle" history.
        # Let's track ALL cells to represent the full computational fabric, 
        # but TDA usually analyzes the manifold of "on" bits.
        # Decision: Track ALL because even 0s are causal in CAs (0-0-0 -> 0).
        # But for topological definition of "gliders", we usually look at the structure of 1s.
        # Let's add nodes for all, but maybe filter edges? No, graph topology depends on connection.
        
        # Optimization: Only add active nodes maybe?
        # For ZX calculus mapping, we need the logic gate structure.
        # Each cell update is a gate.
        
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
                    (prev_t, (x + 1) % cols)
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
