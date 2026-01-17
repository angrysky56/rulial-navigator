from dataclasses import dataclass
from typing import List, Tuple

from ..compression.metrics import CompressionTelemetry


@dataclass
class ProbeResult:
    rule: int
    telemetry: CompressionTelemetry
    wolfram_class: int
    interestingness: float


class GradientCalculator:
    """
    Calculates the 'vector' of interestingness in Rulial Space.
    Determines which neighbor to move towards.
    """

    @staticmethod
    def compute_interestingness(telemetry: CompressionTelemetry) -> float:
        """
        Scalar score of how 'interesting' a rule is.
        High interestingness = High potential for complexity (Class 4).

        Formula components:
        1. Learning Rate (-loss_derivative): Faster learning is better.
        2. Complexity Sweet Spot: Rigid ratio should be balanced (0.3 - 0.7).
        """
        # 1. Learning Score (The "Derivative" component)
        # loss_derivative is typically negative for learning.
        # We want to maximize (-derivative).
        learning_score = -telemetry.loss_derivative * 1000  # Scale up
        learning_score = max(0, learning_score)  # Clamp

        # 2. Complexity Filter (The "Goldilocks" component)
        ratio = telemetry.rigid_ratio_lzma
        if 0.2 <= ratio <= 0.8:
            complexity_multiplier = 1.0
        elif 0.1 < ratio < 0.9:
            complexity_multiplier = 0.5
        else:
            complexity_multiplier = 0.1  # Too simple or too random

        # Combine
        score = learning_score * complexity_multiplier
        return score

    @staticmethod
    def calculate_gradient(center: int, probes: List[ProbeResult]) -> Tuple[int, float]:
        """
        Evaluate probes and return the best rule to move to.
        Returns: (best_rule, improvement_magnitude)
        """
        if not probes:
            return center, 0.0

        # Find current interestingness (center rule)
        center_score = 0.0
        for p in probes:
            if p.rule == center:
                center_score = p.interestingness
                break

        # Find max interestingness
        best_probe = max(probes, key=lambda p: p.interestingness)

        # If best is center, magnitude is 0 (local peak)
        magnitude = best_probe.interestingness - center_score

        return best_probe.rule, magnitude
