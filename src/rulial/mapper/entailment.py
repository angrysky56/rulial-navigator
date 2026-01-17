import networkx as nx
import numpy as np

from ..engine.spacetime import SpacetimeUtil


class EntailmentCone:
    """
    Constructs the 'Entailment Cone' (Causal Graph) of a rule.
    Visualizes the flow of information.
    """

    @staticmethod
    def build(spacetime: np.ndarray) -> nx.DiGraph:
        """
        Builds the raw causal graph.
        """
        return SpacetimeUtil.extract_causal_graph(spacetime)

    @staticmethod
    def coarse_grain(graph: nx.DiGraph) -> nx.DiGraph:
        """
        Approximates the 'Computational Manifold' by collapsing linear chains.

        Simplification rules:
        - If Node A has 1 child B, and B has 1 parent A, merge A-B.
        - This reduces 'wires' to single edges, highlighting logical branching/merging.
        """
        # Work on a copy
        G = graph.copy()

        # Iterative contraction
        # We look for nodes with in_degree=1 and out_degree=1 (Linear pipes)
        # And remove them, connecting parent directly to child.

        while True:
            # Find candidates (re-evaluate every pass to handle chains)
            candidates = [
                n for n in G.nodes() if G.in_degree(n) == 1 and G.out_degree(n) == 1
            ]

            if not candidates:
                break

            # Process one batch of independent candidates?
            # Safest to process one by one or careful batching to avoid index errors.
            # Let's do a simple pass.

            applied_change = False
            for n in candidates:
                if n not in G:
                    continue

                preds = list(G.predecessors(n))
                succs = list(G.successors(n))

                # Validation
                if len(preds) != 1 or len(succs) != 1:
                    continue

                p = preds[0]
                s = succs[0]

                # Avoid contracting self-loops into oblivion if not careful,
                # but A->B->A becoming A->A is fine.
                if p == n or s == n:
                    continue

                # Contract: Remove n, add p->s
                G.add_edge(p, s)
                G.remove_node(n)
                applied_change = True

            if not applied_change:
                break

        return G
