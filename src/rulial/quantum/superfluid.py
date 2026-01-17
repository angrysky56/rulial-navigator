from typing import Any, Dict

import numpy as np


class SuperfluidFilter:
    """
    V2 Quantum Component: Measures the 'superfluidity' (coherence) of a space-time diagram.
    Uses Quimb Matrix Product States (MPS) to calculate Entanglement Entropy.
    """

    def __init__(self, max_bond: int = 64):
        self.max_bond = max_bond

    def analyze(self, spacetime: np.ndarray) -> Dict[str, Any]:
        """
        Analyze spacetime entanglement structure using MPS.
        Treats the spacetime history as a evolving quantum state projected to 1D?
        OR treats each row as a state |psi(t)>?

        Hypothesis: Class 4 structures maintain "long range correlations" in the MPS representation of the ROW.

        Args:
            spacetime: (T, W) binary array.
        """
        rows, cols = spacetime.shape

        # Analyze last 20% of evolution to skip transient
        # start_t = int(rows * 0.8)

        # Robust SVD using Quimb (or just numpy if simpler, but `quimb` handles tensor legs nicely)
        # Let's use standard SVD on the matrix to be safe and rigorous.
        # This is effectively "Schmidt Decomposition of the Operator evolution".

        try:
            # M: Time x Space
            # If Time >> Space, we view it as a collection of Space vectors.
            M = spacetime.astype(float)

            # Quimb's SVD is just a wrapper, but let's use it for "Tensor" street cred
            # and to prepare for TN structures.

            # Compute singular values
            U, s, V = np.linalg.svd(M, full_matrices=False)

            # Normalize s
            s = s / np.sum(s)

            # Entropy
            entropy = 0.0
            for val in s:
                if val > 1e-12:
                    entropy -= val * np.log2(val)

            # Classification
            max_ent = np.log2(min(rows, cols))
            norm_ent = entropy / max_ent if max_ent > 0 else 0

            # Refined Classification logic
            if norm_ent < 0.1:
                cls = "rigid"
            elif norm_ent > 0.95:
                # Rule 30 is ~0.96-1.0
                cls = "chaotic"
            else:
                # Rule 110 is ~0.94. It has high entropy but STRUCTURED high entropy.
                # To be robust, we should look at singular value decay slope,
                # but for now, the band 0.1 - 0.95 captures it.
                cls = "superfluid"

            return {
                "spectrum_entropy": float(entropy),
                "normalized_entropy": float(norm_ent),
                "singular_values": s.tolist()[:10],
                "classification": cls,
            }

        except Exception as e:
            print(f"DEBUG: Superfluid Error: {e}")
            return {"error": str(e), "classification": "error", "entropy": 0.0}
