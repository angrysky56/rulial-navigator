"""
T-P+E Analyzer: Toroidal-Poloidal Emergence Framework.

Models the dynamics of cellular automata as a dialectic between:
- Toroidal (T): Expansion, circulation, divergence
- Poloidal (P): Contraction, flux, convergence
- Emergence (E): Structure × Change = (T·P) × |T-P|

Theory: Maximum emergence occurs when T ≈ P ≈ 0.5

Based on the Metastable Superfluid Membrane framework.
"""

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from scipy import ndimage

from rulial.engine.totalistic import Totalistic2DEngine


@dataclass
class TPEAnalysis:
    """Result of T-P+E analysis."""

    rule_str: str
    toroidal: float  # T: expansion/circulation (0-1)
    poloidal: float  # P: contraction/mass (0-1)
    emergence: float  # E = T·P × |T-P|
    stability: float  # Persistence ratio (0-1)
    dominant_mode: str  # "T-dominant", "P-dominant", "balanced", "dead"

    # Time series for visualization
    t_curve: List[float]
    p_curve: List[float]

    def summary(self) -> str:
        mode_icons = {
            "T-dominant": "🌀 EXPANSION",
            "P-dominant": "⚛️ CONTRACTION",
            "balanced": "✨ BALANCED",
            "dead": "❄️ DEAD",
        }

        return (
            f"═══ T-P+E Analysis: {self.rule_str} ═══\n"
            f"  Toroidal (T): {self.toroidal:.3f} [expansion/circulation]\n"
            f"  Poloidal (P): {self.poloidal:.3f} [contraction/mass]\n"
            f"  ─────────────────────────────\n"
            f"  Emergence (E): {self.emergence:.4f}\n"
            f"  Stability: {self.stability:.1%}\n"
            f"  Mode: {mode_icons.get(self.dominant_mode, self.dominant_mode)}\n"
            f"  ─────────────────────────────\n"
            f"  T·P = {self.toroidal * self.poloidal:.4f}\n"
            f"  |T-P| = {abs(self.toroidal - self.poloidal):.4f}"
        )


class TPEAnalyzer:
    """
    Analyze cellular automata using the T-P+E framework.

    Toroidal (T): Measures expansion/divergence
    - Population growth rate
    - Center of mass movement outward
    - Component fragmentation

    Poloidal (P): Measures contraction/convergence
    - Population decay rate
    - Center of mass movement inward
    - Component coalescence
    """

    def __init__(self, warmup: int = 30):
        self.warmup = warmup  # Skip initial transient

    def _measure_toroidal(self, history: List[np.ndarray]) -> Tuple[float, List[float]]:
        """
        Measure Toroidal (expansion) component.

        Returns (mean_T, T_curve)
        """
        t_values = []

        for i in range(1, len(history)):
            prev, curr = history[i - 1], history[i]

            # 1. Population growth
            pop_prev = int(prev.sum())
            pop_curr = int(curr.sum())
            if pop_prev > 0:
                growth = (pop_curr - pop_prev) / pop_prev
            else:
                growth = 0.0

            # 2. Dispersion (spread from center)
            if pop_curr > 0:
                h, w = curr.shape
                y_coords, x_coords = np.where(curr > 0)
                center_y, center_x = h / 2, w / 2
                dispersion = np.mean(
                    np.sqrt((y_coords - center_y) ** 2 + (x_coords - center_x) ** 2)
                ) / (
                    h / 2
                )  # Normalize
            else:
                dispersion = 0

            # 3. Component count (fragmentation)
            labeled, num_components = ndimage.label(curr)
            fragmentation = min(1.0, num_components / 50)  # Normalize

            # Combine into T metric
            # Positive growth + high dispersion + fragmentation = high T
            t = np.clip(
                0.3 * max(0, growth)  # Growth contributes
                + 0.4 * dispersion  # Spread contributes
                + 0.3 * fragmentation,  # Fragmentation contributes
                0,
                1,
            )
            t_values.append(t)

        return float(np.mean(t_values[self.warmup :])), t_values

    def _measure_poloidal(self, history: List[np.ndarray]) -> Tuple[float, List[float]]:
        """
        Measure Poloidal (contraction/mass) component.

        Returns (mean_P, P_curve)
        """
        p_values = []

        for i in range(1, len(history)):
            prev, curr = history[i - 1], history[i]

            # 1. Population stability (not growing wildly)
            pop_prev = int(prev.sum())
            pop_curr = int(curr.sum())
            if pop_prev > 0:
                stability = 1.0 - abs(pop_curr - pop_prev) / pop_prev
            else:
                stability = 0.0

            # 2. Density (concentration of mass)
            if curr.sum() > 0:
                labeled, num_components = ndimage.label(curr)
                if num_components > 0:
                    # Average component size
                    avg_size = curr.sum() / num_components
                    density = min(1.0, avg_size / 20)  # Normalize
                else:
                    density = 0
            else:
                density = 0

            # 3. Structure (presence of patterns)
            # Use local variance as structure indicator
            if curr.sum() > 0:
                local_var = ndimage.generic_filter(
                    curr.astype(float), np.var, size=3
                ).mean()
                structure = min(1.0, local_var * 10)
            else:
                structure = 0

            # Combine into P metric
            # Stable population + dense clusters + structure = high P
            p = np.clip(0.3 * max(0, stability) + 0.4 * density + 0.3 * structure, 0, 1)
            p_values.append(p)

        return float(np.mean(p_values[self.warmup :])), p_values

    def _measure_stability(self, history: List[np.ndarray]) -> float:
        """
        Measure stability as persistence of structures.
        """
        if len(history) < 10:
            return 0.0

        # Compare first and last frames (after warmup)
        start_idx = min(self.warmup, len(history) - 10)
        early = history[start_idx]
        late = history[-1]

        early_pop = early.sum()
        late_pop = late.sum()

        if early_pop == 0:
            return 0.0 if late_pop == 0 else 1.0

        # Stability = how much of the population persists
        return min(1.0, late_pop / early_pop)

    def analyze(
        self,
        rule_str: str,
        steps: int = 300,
        grid_size: int = 64,
        density: float = 0.3,
    ) -> TPEAnalysis:
        """
        Perform T-P+E analysis on a rule.
        """
        # 1. Simulate
        engine = Totalistic2DEngine(rule_str)
        history = engine.simulate(
            grid_size, grid_size, steps, "random", density=density
        )

        # 2. Measure T and P
        t_mean, t_curve = self._measure_toroidal(history)
        p_mean, p_curve = self._measure_poloidal(history)

        # 3. Calculate Emergence: E = (T·P) × |T-P|
        emergence = (t_mean * p_mean) * abs(t_mean - p_mean)

        # 4. Measure stability
        stability = self._measure_stability(history)

        # 5. Classify dominant mode
        if t_mean < 0.1 and p_mean < 0.1:
            mode = "dead"
        elif abs(t_mean - p_mean) < 0.15:
            mode = "balanced"
        elif t_mean > p_mean:
            mode = "T-dominant"
        else:
            mode = "P-dominant"

        return TPEAnalysis(
            rule_str=rule_str,
            toroidal=t_mean,
            poloidal=p_mean,
            emergence=emergence,
            stability=stability,
            dominant_mode=mode,
            t_curve=t_curve,
            p_curve=p_curve,
        )


def analyze_tpe(rule_str: str) -> TPEAnalysis:
    """Quick T-P+E analysis of a single rule."""
    analyzer = TPEAnalyzer()
    return analyzer.analyze(rule_str)


if __name__ == "__main__":
    # Test with known rules
    analyzer = TPEAnalyzer()

    test_rules = [
        ("B3/S23", "Game of Life - expected P-dominant"),
        ("B36/S23", "HighLife - expected balanced"),
        ("B/S", "Empty - expected dead"),
        ("B12345678/S12345678", "Dense - expected T-dominant"),
    ]

    for rule, description in test_rules:
        print(f"\n{'='*60}")
        print(f"Testing: {description}")
        print("=" * 60)
        result = analyzer.analyze(rule)
        print(result.summary())
