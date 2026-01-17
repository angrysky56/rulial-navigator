from typing import Any, Dict

import networkx as nx
import pyzx as zx


class ZXReducer:
    """
    V2 Quantum Component: Measures Computational Irreducibility using ZX Calculus.
    """

    def analyze(self, causal_graph: nx.DiGraph) -> Dict[str, Any]:
        """
        Analyze the causal graph by converting to ZX-diagram and reducing.
        """
        try:
            print(f"DEBUG: Full graph has {causal_graph.number_of_nodes()} nodes")

            # Filter for EFFECTIVE graph (Active cells only)
            # We assume nodes have 'state' attribute from SpacetimeUtil
            active_nodes = [
                n for n, d in causal_graph.nodes(data=True) if d.get("state", 0) == 1
            ]
            effective_graph = causal_graph.subgraph(active_nodes)

            print(f"DEBUG: Active graph has {effective_graph.number_of_nodes()} nodes")

            if effective_graph.number_of_nodes() == 0:
                return {"skeleton_structure": "void", "reduction_ratio": 0.0}

            # 1. Convert DAG to Circuit
            # Heuristic Mapping:
            # Node -> Z Spider (Green)
            # Edge -> Hadamard Edge (interaction)

            g = zx.Graph()

            # Map NX nodes to ZX vertices
            mapping = {}
            for node in effective_graph.nodes():
                v = g.add_vertex(ty=zx.VertexType.Z)
                mapping[node] = v

            # Map Edges
            for u, v in effective_graph.edges():
                # Use Hadamard edge to create graph state structure
                g.add_edge(zx.EdgeType.HADAMARD, mapping[u], mapping[v])

            # 2. Reduce
            original_order = g.num_vertices()
            if original_order == 0:
                return {"reduction_ratio": 0.0}

            # Apply simplification designed for graph-states / Clifford circuits
            zx.simplify.full_reduce(g)

            reduced_order = g.num_vertices()

            # 3. Metrics
            # Reduction Ratio: How much vanished?
            # 1.0 = Nothing left (Fully reducible / Trivial identity)
            # 0.0 = Nothing changed (Fully irreducible)

            ratio = 1.0 - (reduced_order / original_order)

            # Classification
            if ratio > 0.95:
                structure = "trivial"  # Collapsed to identity
            elif ratio < 0.1:
                structure = "noise"  # Incompressible spaghetti
            else:
                structure = "structured"  # The irreducible skeleton

            return {
                "original_nodes": original_order,
                "reduced_nodes": reduced_order,
                "reduction_ratio": ratio,
                "skeleton_structure": structure,
            }

        except Exception as e:
            return {"error": str(e), "structure": "error"}
