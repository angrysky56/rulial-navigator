"""
Compression Compass: The Navigator's Sextant.

Implements the "Compression Gradient" logic for the AIR (Autonomous Inverse Ruliology) protocol.
Calculates:
1. Compression Ratio (r_c): r_c =Compressed / Raw
2. Compression Progress (d(r_c)/dt): Learning rate of the model.
3. Logical Depth (Proxy): Ratio of execution time (sim steps) to description length.

Theory:
- Class 1/2: High compression (r_c -> 0), Zero progress (d/dt = 0).
- Class 3: Low compression (r_c -> 1), Zero progress (d/dt = 0).
- Class 4: Med compression, POSITIVE progress (d/dt < 0, ratio improves over time).
"""

import lzma
from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass
class CompassReading:
    rule_str: str
    compression_ratio_start: float
    compression_ratio_end: float
    compression_progress: float  # Negative is good (ratio decreasing)
    logical_depth_proxy: float
    is_interesting: bool
    status_msg: str


class CompressionCompass:
    def __init__(self, use_lzma_filters: bool = True):
        self.use_lzma_filters = use_lzma_filters

    def measure(self, rule_str: str, history: List[np.ndarray]) -> CompassReading:
        """
        Take a spacetime history and calculate its "Interestingness".

        Args:
            rule_str: The rule string (for logging).
            history: List of 2D numpy arrays (steps).
        """
        if not history:
            return CompassReading(rule_str, 0.0, 0.0, 0.0, 0.0, False, "Empty History")

        # Split history into "Early" and "Late" to measure progress
        # T0 -> T_mid vs T_mid -> T_end?
        # Better: Compress T0..Ti and Ti..Tend?
        # Or: Compress full history vs history of first few steps?

        # Method:
        # 1. Compress first 20% of steps. Calculate ratio r_start.
        # 2. Compress last 20% of steps. Calculate ratio r_end.
        # 3. Progress = r_end - r_start.
        # If model "learns" structure (gliders emerge), r_end might be lower (more compressible)
        # OR higher (chaos spreads)?

        # Actually, "Compression Progress" usually means the compressor predicts better over time.
        # But standard LZMA is static.
        # Proxy: If structure emerges (gliders), the space becomes MORE compressible than chaos,
        # but LESS compressible than void.

        # Let's use specific slices.
        steps = len(history)
        slice_len = max(1, steps // 5)

        early_slice = history[:slice_len]
        late_slice = history[-slice_len:]

        r_start = self._calc_ratio(early_slice)
        r_end = self._calc_ratio(late_slice)

        # Progress:
        # If r_end < r_start: Exploring order?
        # If r_end > r_start: Exploring chaos/entropy increase?
        progress = r_end - r_start

        # Logical Depth Proxy:
        # Depth ≈ Steps / CompressedSize
        # (How much computation is packed into the description)
        full_bytes = self._to_bytes(history)
        compressed_len = len(lzma.compress(full_bytes))
        if compressed_len > 0:
            logical_depth = steps / compressed_len
        else:
            logical_depth = 0.0

        # Classification
        # Class 1/2: r_end approx 0.
        # Class 3: r_end approx 1.
        # Class 4: 0.2 < r_end < 0.7 AND |progress| is small?
        # Actually in documentation:
        # "Class 4: Medium (0.3-0.7), Positive/Sustained Progress" (Meaning derivative is non-zero?)
        # Let's target the "Goldilocks" bandwidth of compressibility.

        is_interesting = False
        msg = "Boring"

        if r_end < 0.05:
            msg = "Frozen (Class 1/2)"
        elif r_end > 0.95:
            msg = "Chaotic (Class 3)"
        elif 0.1 <= r_end <= 0.6:
            # The sweet spot
            is_interesting = True
            msg = "Complex (Class 4 Candidate)"

        return CompassReading(
            rule_str=rule_str,
            compression_ratio_start=r_start,
            compression_ratio_end=r_end,
            compression_progress=progress,
            logical_depth_proxy=logical_depth,
            is_interesting=is_interesting,
            status_msg=msg,
        )

    def _calc_ratio(self, frames: List[np.ndarray]) -> float:
        data = self._to_bytes(frames)
        if not data:
            return 0.0
        compressed = lzma.compress(data)
        return len(compressed) / len(data)

    def _to_bytes(self, frames: List[np.ndarray]) -> bytes:
        # Pack binary grids
        return b"".join(f.tobytes() for f in frames)
