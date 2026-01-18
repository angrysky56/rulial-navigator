"""
Vacuum Condensate Analyzer.

Detects and characterizes rules that exhibit vacuum condensate behavior:
- Single cells spontaneously expand to fill space
- System relaxes to a characteristic equilibrium density
- No isolated particles exist - the vacuum IS the structure

Based on the discovery of B078/S012478 and MSM Theory.
"""

from dataclasses import dataclass

import numpy as np

from rulial.engine.totalistic import Totalistic2DEngine


@dataclass
class CondensateAnalysis:
    """Result of vacuum condensate analysis."""

    rule_str: str
    is_condensate: bool  # Single cell expands?
    equilibrium_density: float  # Characteristic density (0-1)
    critical_density: float  # Phase transition point
    relaxation_time: int  # Steps to reach equilibrium
    expansion_factor: float  # How much single cell grows
    stability_variance: float  # Variance at equilibrium

    def summary(self) -> str:
        if self.is_condensate:
            phase = "🌊 CONDENSATE"
        else:
            phase = "⚛️ PARTICLE-BASED"

        return (
            f"═══ Vacuum Condensate Analysis: {self.rule_str} ═══\n"
            f"  Phase: {phase}\n"
            f"  ─────────────────────────────\n"
            f"  Equilibrium Density: {self.equilibrium_density:.1%}\n"
            f"  Critical Density: {self.critical_density:.1%}\n"
            f"  Relaxation Time: {self.relaxation_time} steps\n"
            f"  ─────────────────────────────\n"
            f"  Single Cell → {self.expansion_factor:.0f} cells\n"
            f"  Stability σ²: {self.stability_variance:.2f}"
        )


class VacuumCondensateAnalyzer:
    """
    Analyze rules for vacuum condensate behavior.

    A vacuum condensate rule has these properties:
    1. Single cells cannot exist - they spontaneously expand
    2. The system relaxes to a characteristic equilibrium density
    3. Starting from any initial density, it reaches the same equilibrium
    """

    def __init__(self, grid_size: int = 64, steps: int = 200):
        self.grid_size = grid_size
        self.steps = steps

    def _measure_equilibrium(
        self,
        engine: Totalistic2DEngine,
        initial_density: float,
    ) -> tuple[float, float, int]:
        """
        Measure equilibrium density from a given starting density.

        Returns: (final_density, variance, relaxation_time)
        """
        history = engine.simulate(
            self.grid_size,
            self.grid_size,
            self.steps,
            "random",
            density=initial_density,
        )

        total_cells = self.grid_size * self.grid_size
        populations = [h.sum() / total_cells for h in history]

        # Equilibrium = last 20% of simulation
        equil_start = int(len(populations) * 0.8)
        equil_pops = populations[equil_start:]

        final_density = np.mean(equil_pops)
        variance = np.var(equil_pops)

        # Relaxation time: when does it reach 90% of final value?
        target = 0.9 * final_density
        relax_time = self.steps
        for i, pop in enumerate(populations):
            if pop >= target:
                relax_time = i
                break

        return float(final_density), float(variance), relax_time

    def _test_single_cell(self, engine: Totalistic2DEngine) -> int:
        """Test what a single cell expands to."""
        grid = np.zeros((32, 32), dtype=np.uint8)
        grid[16, 16] = 1

        history = engine.simulate(32, 32, 100, "custom", custom_grid=grid)
        return int(history[-1].sum())

    def _find_critical_density(
        self,
        engine: Totalistic2DEngine,
        equilibrium: float,
    ) -> float:
        """
        Find the critical density where growth ≈ decay.

        This is the phase transition point.
        """
        # Binary search between 0 and equilibrium
        low, high = 0.01, min(0.5, equilibrium * 2)

        for _ in range(8):  # 8 iterations for precision
            mid = (low + high) / 2

            history = engine.simulate(
                self.grid_size, self.grid_size, 50, "random", density=mid
            )

            initial = history[0].sum()
            final = history[-1].sum()

            if initial == 0:
                low = mid
            elif final > initial:  # Growth phase
                low = mid
            else:  # Decay phase
                high = mid

        return (low + high) / 2

    def analyze(self, rule_str: str) -> CondensateAnalysis:
        """Perform full vacuum condensate analysis."""
        engine = Totalistic2DEngine(rule_str)

        # 1. Test single cell expansion
        single_cell_result = self._test_single_cell(engine)
        is_condensate = single_cell_result > 10  # Expanded significantly

        # 2. Measure equilibrium from low density
        eq_density_low, var_low, _ = self._measure_equilibrium(engine, 0.05)

        # 3. Measure equilibrium from high density
        eq_density_high, var_high, _ = self._measure_equilibrium(engine, 0.4)

        # 4. Average equilibrium density
        equilibrium = (eq_density_low + eq_density_high) / 2

        # 5. Measure relaxation time
        _, _, relax_time = self._measure_equilibrium(engine, 0.1)

        # 6. Find critical density
        critical = self._find_critical_density(engine, equilibrium)

        # 7. Stability variance
        variance = (var_low + var_high) / 2

        return CondensateAnalysis(
            rule_str=rule_str,
            is_condensate=is_condensate,
            equilibrium_density=equilibrium,
            critical_density=critical,
            relaxation_time=relax_time,
            expansion_factor=single_cell_result,
            stability_variance=variance,
        )


def analyze_condensate(rule_str: str) -> CondensateAnalysis:
    """Quick vacuum condensate analysis of a single rule."""
    analyzer = VacuumCondensateAnalyzer()
    return analyzer.analyze(rule_str)


if __name__ == "__main__":
    analyzer = VacuumCondensateAnalyzer()

    test_rules = [
        ("B078/S012478", "Discovery - expected condensate"),
        ("B3/S23", "Game of Life - expected particle-based"),
        ("B/S", "Empty - baseline"),
    ]

    for rule, description in test_rules:
        print(f"\n{'='*60}")
        print(f"Testing: {description}")
        print("=" * 60)
        result = analyzer.analyze(rule)
        print(result.summary())
