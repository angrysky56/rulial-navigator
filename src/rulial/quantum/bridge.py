import gc
from typing import Any, Dict

import numpy as np
import quimb.tensor as qtn


class TensorBridge:
    """
    Quantum V3: Two-Dimensional Tensor Bridge.
    Maps 2D Cellular Automata states to Projected Entangled Pair States (PEPS)
    via Cluster State construction + Projection.
    """

    def __init__(self, height: int, width: int):
        self.H = height
        self.W = width
        self.n_qubits = self.H * self.W

    def grid_to_tensor_state(self, binary_grid: np.ndarray) -> qtn.TensorNetwork:
        """
        Converts a 2D binary grid into a 2D Tensor Network State.

        Strategy:
        1. Initialize full HxW Cluster State (Universal Resource).
           - All qubits in |+>
           - CZ gates between all grid neighbors
        2. Project '0' pixels to |0> state.
           - This 'carves out' the pattern from the entanglement substrate.
           - The remaining entanglement is purely topological/structural.
        """
        # 1. Construct 2D Cluster State Circuit
        # We generally use a custom builder to ensure coordinates map correctly
        # But qtn.Circuit is convenient.

        circ = qtn.Circuit(self.n_qubits)

        # Apply H to all to get |+>
        for i in range(self.n_qubits):
            circ.apply_gate("H", i)

        # Apply CZ between neighbors (Grid Topology)
        for r in range(self.H):
            for c in range(self.W):
                idx = r * self.W + c

                # Right Neighbor
                if c < self.W - 1:
                    idx_right = r * self.W + (c + 1)
                    circ.apply_gate("CZ", idx, idx_right)

                # Down Neighbor
                if r < self.H - 1:
                    idx_down = (r + 1) * self.W + c
                    circ.apply_gate("CZ", idx, idx_down)

        # psi = circ.psi
        # Ensure it's a mutable TN
        psi = qtn.TensorNetwork(circ.psi)

        # 2. Project '0' cells to |0>
        total_projected = 0

        for r in range(self.H):
            for c in range(self.W):
                if binary_grid[r, c] == 0:
                    idx = r * self.W + c

                    # explicit contract with <0| = [1, 0]
                    # This acts as projection.
                    tag = f"k{idx}"

                    # Bra <0|
                    T_bra = qtn.Tensor(
                        data=np.array([1.0, 0.0], dtype=complex), inds=(tag,)
                    )
                    psi.add_tensor(T_bra)

                    total_projected += 1

        # After projection
        # psi.full_simplify_() # Causes index corruption/crash in quimb 0.1.0?

        return psi

    def compute_bipartition_entropy(self, psi: qtn.TensorNetwork) -> Dict[str, Any]:
        """
        Computes entanglement entropy of the state across a vertical partition.
        """
        if isinstance(psi, dict) and "entropy" in psi:
            return psi

        # We need to define the subsystem A.
        # Let's take the left half of the grid.

        # Scan ALL open indices
        open_inds = psi.outer_inds()

        if not open_inds:
            return {"entropy": 0.0, "status": "empty_state"}

        # Strict limit on dense contraction size.
        # Contraction scales exponentially with open indices (qubits).
        # Limit adjusted for standard desktop usage.
        HARD_QUBIT_LIMIT = 24  # 2^24 * 16 bytes ~ 268 MB state vector. Safe.
        # 2^30 ~ 16 GB (Danger zone).

        if len(open_inds) > HARD_QUBIT_LIMIT:
            return {
                "entropy": -1.0,
                "status": "volume_law_truncation",
                "active_qubits": len(open_inds),
            }

        # Convert to dense and calc entropy
        try:
            print(f"DEBUG: Contracting TN with {len(psi.tensors)} tensors...")
            # optimize='greedy' is fast and robust
            psi_dense = psi.contract(output_inds=open_inds, optimize="greedy")

            # Explicit GC to free intermediate contraction buffers
            gc.collect()

            # Post-selection normalization (amplitude is small due to many projections)
            # Quimb tensors usually support scalar division
            n = psi_dense.norm()
            if n > 0:
                psi_dense /= n

            # Identify which dimensions correspond to Left Half
            left_inds = []
            for ind in open_inds:
                # ind is string usually 'k12'
                if isinstance(ind, str) and ind.startswith("k"):
                    try:
                        id_val = int(ind[1:])
                        # check col
                        c = id_val % self.W
                        if c < self.W // 2:
                            left_inds.append(ind)
                    except ValueError:
                        pass

            if not left_inds:
                return {
                    "entropy": 0.0,
                    "status": "all_right",
                    "active_qubits": len(open_inds),
                }

            if len(left_inds) == len(open_inds):
                return {
                    "entropy": 0.0,
                    "status": "all_left",
                    "active_qubits": len(open_inds),
                }

            ent = psi_dense.entropy(left_inds)

            return {
                "entropy": float(ent),
                "status": "computed_exact",
                "active_qubits": len(open_inds),
            }

        except Exception as e:
            return {"entropy": 0.0, "status": "error", "message": str(e)}
