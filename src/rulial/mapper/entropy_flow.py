"""
Entropy Flow Analyzer: Track the direction of entropy over time.

Implements the philosophical perspective that computation is "knots
dissolving in entropy towards the resolving void."

Three flow states:
- DISSOLVING: Entropy increases (system relaxes toward void/equilibrium)
- CRYSTALLIZING: Entropy decreases (structure emerges from chaos)
- BALANCED: Entropy stable (edge of chaos, solitons maintain themselves)
"""

from dataclasses import dataclass
from typing import List

import numpy as np
import scipy.stats

from rulial.engine.totalistic import Totalistic2DEngine


@dataclass
class EntropyFlow:
    """Result of entropy flow analysis."""

    rule_str: str
    flow_direction: str  # 'dissolving', 'crystallizing', 'balanced'
    entropy_slope: float  # dS/dt
    initial_entropy: float
    final_entropy: float
    entropy_curve: List[float]
    interpretation: str

    def summary(self) -> str:
        arrow = {
            "dissolving": "→ void",
            "crystallizing": "← void",
            "balanced": "≈ edge",
        }.get(self.flow_direction, "?")

        return (
            f"Entropy Flow: {self.rule_str}\n"
            f"  Direction: {self.flow_direction.upper()} {arrow}\n"
            f"  Slope: {self.entropy_slope:.6f} nats/step\n"
            f"  Initial: {self.initial_entropy:.4f} → Final: {self.final_entropy:.4f}\n"
            f"  {self.interpretation}"
        )


class EntropyFlowAnalyzer:
    """
    Analyze the thermodynamic direction of a rule.

    Interpretation:
    - Dissolving: The rule tends toward maximum entropy (uniform randomness).
                  All structure is temporary; everything returns to void.
    - Crystallizing: The rule tends toward minimum entropy (frozen order).
                     Structure emerges and persists; creates "frozen knots."
    - Balanced: The rule maintains intermediate entropy.
                Solitons (particles) persist but interact dynamically.
                This is the "edge of chaos" where computation lives.
    """

    def __init__(self, steps: int = 300, warmup: int = 50):
        self.steps = steps
        self.warmup = warmup  # Skip initial transient

    def _compute_grid_entropy(self, grid: np.ndarray) -> float:
        """Compute Shannon entropy of a binary grid."""
        flat = grid.flatten()
        if len(flat) == 0:
            return 0.0

        # Count 0s and 1s
        counts = np.bincount(flat.astype(int), minlength=2)
        probs = counts / len(flat)

        # Remove zeros to avoid log(0)
        probs = probs[probs > 0]
        return float(scipy.stats.entropy(probs, base=2))

    def analyze(self, rule_str: str, initial_density: float = 0.5) -> EntropyFlow:
        """
        Analyze entropy flow for a given rule.

        Args:
            rule_str: The rule to analyze (e.g., "B3/S23")
            initial_density: Starting density of live cells

        Returns:
            EntropyFlow dataclass with analysis results
        """
        engine = Totalistic2DEngine(rule_str)
        history = engine.simulate(64, 64, self.steps, "dense")

        # Compute entropy at each timestep
        entropies = []
        for grid in history:
            S = self._compute_grid_entropy(grid)
            entropies.append(S)

        # Analyze post-warmup region
        analysis_region = entropies[self.warmup:]

        if len(analysis_region) < 10:
            return EntropyFlow(
                rule_str=rule_str,
                flow_direction="unknown",
                entropy_slope=0.0,
                initial_entropy=entropies[0] if entropies else 0.0,
                final_entropy=entropies[-1] if entropies else 0.0,
                entropy_curve=entropies,
                interpretation="Insufficient data for analysis."
            )

        # Linear regression to get slope
        x = np.arange(len(analysis_region))
        slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(
            x, analysis_region
        )

        # Classify flow direction
        # Thresholds tuned empirically
        if slope > 0.0001:
            direction = "dissolving"
            interpretation = (
                "Entropy increases over time. Structure dissolves toward equilibrium. "
                "This rule tends toward the void—all patterns are temporary."
            )
        elif slope < -0.0001:
            direction = "crystallizing"
            interpretation = (
                "Entropy decreases over time. Order emerges from chaos. "
                "This rule creates persistent structure—frozen knots."
            )
        else:
            direction = "balanced"
            interpretation = (
                "Entropy is stable. The system maintains dynamic equilibrium. "
                "This is the edge of chaos where solitons persist and interact."
            )

        return EntropyFlow(
            rule_str=rule_str,
            flow_direction=direction,
            entropy_slope=float(slope),
            initial_entropy=entropies[0],
            final_entropy=entropies[-1],
            entropy_curve=entropies,
            interpretation=interpretation,
        )

    def classify_batch(self, rules: List[str]) -> dict:
        """Classify multiple rules by entropy flow."""
        results = {
            "dissolving": [],
            "crystallizing": [],
            "balanced": [],
        }

        for rule_str in rules:
            try:
                flow = self.analyze(rule_str)
                results[flow.flow_direction].append(rule_str)
            except Exception as e:
                print(f"Error analyzing {rule_str}: {e}")

        return results


# Quick test
if __name__ == "__main__":
    analyzer = EntropyFlowAnalyzer()

    test_rules = [
        "B3/S23",  # Game of Life - expected balanced
        "B1/S1",   # Simple rule - probably crystallizing
        "B12345678/S12345678",  # Dense rule - probably dissolving
        "B36/S23",  # HighLife - expected balanced
    ]

    for rule in test_rules:
        result = analyzer.analyze(rule)
        print(result.summary())
        print()
