from dataclasses import dataclass
from typing import List, Tuple

import gudhi
import numpy as np

from ..engine.spacetime import SpacetimeUtil


@dataclass
class TopologicalSignature:
    betti_0: int
    betti_1: int
    persistence_entropy: float
    max_persistence: float
    barcode: List[Tuple[float, float]]


class TopologyMapper:
    """
    Topological Data Analysis (TDA) mapper using GUDHI.
    Extracts the 'shape' of computation.
    """

    def __init__(self):
        pass

    def compute_persistence(self, spacetime: np.ndarray) -> TopologicalSignature:
        """
        Compute persistent homology of the spacetime structure.
        We treat active cells (1s) as a point cloud in (Time, Space) coordinates.
        """
        # 1. Extract Point Cloud
        points = SpacetimeUtil.active_cell_cloud(spacetime)
        if len(points) == 0:
            return TopologicalSignature(0, 0, 0.0, 0.0, [])

        # 2. Build Simplicial Complex (Alpha Complex is faster for 2D/3D than Rips)
        # However, for (Time, Space) usually Rips is fine.
        # Time distance vs Space distance might need scaling.
        # Let's assume isotropic for now.

        # Approximate check to avoid heavy compute on huge clouds
        if len(points) > 2000:
            # Subsample for performance
            indices = np.random.choice(len(points), 2000, replace=False)
            points = points[indices]

        rips = gudhi.RipsComplex(points=points, max_edge_length=5.0)
        simplex_tree = rips.create_simplex_tree(max_dimension=2)

        # 3. Compute Persistence
        diag = simplex_tree.persistence(min_persistence=0.1)

        # 4. Analyze Barcode
        betti_0 = 0
        betti_1 = 0
        max_persist = 0.0
        lifetimes = []

        # GUDHI returns list of (dimension, (birth, death))
        cleaned_diag = []

        for dim, (birth, death) in diag:
            lifetime = death - birth
            if death == float("inf"):
                lifetime = 100.0  # Cap infinity

            lifetimes.append(lifetime)
            max_persist = max(max_persist, lifetime)

            if dim == 0:
                betti_0 += 1
            elif dim == 1:
                betti_1 += 1

            cleaned_diag.append((birth, death))

        # Entropy
        total_life = sum(lifetimes)
        entropy = 0.0
        if total_life > 0:
            probs = [lifetime / total_life for lifetime in lifetimes]
            entropy = -sum(p * np.log2(p) for p in probs)

        return TopologicalSignature(
            betti_0=betti_0,
            betti_1=betti_1,
            persistence_entropy=entropy,
            max_persistence=max_persist,
            # Sort by lifetime (descending) to keep most significant features
            barcode=sorted(
                cleaned_diag,
                key=lambda x: (100.0 if x[1] == float("inf") else x[1] - x[0]),
                reverse=True,
            )[:50],
        )
