"""
Oligon Counter: Enumerate small stable structures.

Oligons are the "dark matter scaffolding" of the Ruliad:
- Still lifes (period 1)
- Blinkers (period 2)
- Small oscillators (period 3-4)

These small, stable structures provide the tension network
that scaffolds larger solitonic structures (gliders, spaceships).
"""

from dataclasses import dataclass
from typing import Set

import numpy as np
from scipy import ndimage

from rulial.engine.totalistic import Totalistic2DEngine


@dataclass
class OligonCensus:
    """Census of oligons (small stable structures) in a rule."""

    rule_str: str
    still_lifes: int  # Period 1 structures
    oscillators_p2: int  # Period 2 oscillators
    oscillators_p3_plus: int  # Period 3+ oscillators
    total_oligons: int  # Total count
    unique_patterns: int  # Distinct pattern types
    density: float  # Oligons per 100 cells

    def summary(self) -> str:
        return (
            f"═══ Oligon Census: {self.rule_str} ═══\n"
            f"  Still Lifes (P1): {self.still_lifes}\n"
            f"  Oscillators (P2): {self.oscillators_p2}\n"
            f"  Oscillators (P3+): {self.oscillators_p3_plus}\n"
            f"  ─────────────────────────────\n"
            f"  Total Oligons: {self.total_oligons}\n"
            f"  Unique Patterns: {self.unique_patterns}\n"
            f"  Density: {self.density:.2f} per 100 cells"
        )


class OligonCounter:
    """
    Count oligons (small stable structures) in a rule.

    Method:
    1. Run simulation until it stabilizes
    2. Identify connected components
    3. Track each component's period
    4. Count by period class
    """

    def __init__(self, max_period: int = 10):
        self.max_period = max_period

    def _extract_component(
        self, grid: np.ndarray, label: int, labeled: np.ndarray
    ) -> np.ndarray:
        """Extract a single component as a minimal bounding box array."""
        mask = labeled == label
        coords = np.where(mask)
        if len(coords[0]) == 0:
            return np.array([[]])

        min_y, max_y = coords[0].min(), coords[0].max()
        min_x, max_x = coords[1].min(), coords[1].max()

        return grid[min_y : max_y + 1, min_x : max_x + 1].copy()

    def _pattern_hash(self, pattern: np.ndarray) -> str:
        """Create a rotation/reflection-invariant hash of a pattern."""
        if pattern.size == 0:
            return ""

        # Generate all 8 transformations (4 rotations × 2 reflections)
        transforms = []
        p = pattern
        for _ in range(4):
            transforms.append(p.tobytes())
            transforms.append(np.fliplr(p).tobytes())
            p = np.rot90(p)

        # Return lexicographically smallest as canonical form
        return min(transforms).hex()[:32]

    def _find_period(
        self, engine: Totalistic2DEngine, pattern: np.ndarray, max_period: int = 10
    ) -> int:
        """
        Find the period of a pattern.

        Returns:
            0 if pattern dies
            1 if still life
            p if oscillator with period p
            -1 if period > max_period (probably moving/chaotic)
        """
        # Pad pattern to give it room
        pad = max_period + 2
        h, w = pattern.shape
        grid = np.zeros((h + 2 * pad, w + 2 * pad), dtype=np.uint8)
        grid[pad : pad + h, pad : pad + w] = pattern

        # Run simulation
        history = engine.simulate(
            grid.shape[0], grid.shape[1], max_period + 5, "custom", custom_grid=grid
        )

        # Check if died
        if history[-1].sum() == 0:
            return 0

        # Check for periodicity
        initial_hash = self._pattern_hash(history[0])
        for p in range(1, min(len(history), max_period + 1)):
            if self._pattern_hash(history[p]) == initial_hash:
                return p

        return -1  # Not periodic within max_period

    def count(
        self,
        rule_str: str,
        steps: int = 500,
        grid_size: int = 64,
        density: float = 0.15,
    ) -> OligonCensus:
        """
        Count oligons in a rule.
        """
        engine = Totalistic2DEngine(rule_str)

        # 1. Run simulation to let structures form
        history = engine.simulate(
            grid_size, grid_size, steps, "random", density=density
        )
        final_grid = history[-1]

        # 2. Label connected components
        labeled, num_components = ndimage.label(final_grid)

        if num_components == 0:
            return OligonCensus(
                rule_str=rule_str,
                still_lifes=0,
                oscillators_p2=0,
                oscillators_p3_plus=0,
                total_oligons=0,
                unique_patterns=0,
                density=0.0,
            )

        # 3. Analyze each component
        still_lifes = 0
        oscillators_p2 = 0
        oscillators_p3_plus = 0
        seen_patterns: Set[str] = set()

        for label_id in range(
            1, min(num_components + 1, 100)
        ):  # Limit to 100 components
            pattern = self._extract_component(final_grid, label_id, labeled)
            if pattern.size == 0 or pattern.sum() == 0:
                continue

            # Skip large patterns (not oligons)
            if pattern.sum() > 20:
                continue

            # Record pattern
            phash = self._pattern_hash(pattern)
            seen_patterns.add(phash)

            # Find period
            period = self._find_period(engine, pattern)

            if period == 1:
                still_lifes += 1
            elif period == 2:
                oscillators_p2 += 1
            elif period > 2:
                oscillators_p3_plus += 1
            # period 0 (died) or -1 (chaotic) are not oligons

        total = still_lifes + oscillators_p2 + oscillators_p3_plus
        area = grid_size * grid_size

        return OligonCensus(
            rule_str=rule_str,
            still_lifes=still_lifes,
            oscillators_p2=oscillators_p2,
            oscillators_p3_plus=oscillators_p3_plus,
            total_oligons=total,
            unique_patterns=len(seen_patterns),
            density=total * 100 / area,
        )


def count_oligons(rule_str: str) -> OligonCensus:
    """Quick oligon count for a single rule."""
    counter = OligonCounter()
    return counter.count(rule_str)


if __name__ == "__main__":
    counter = OligonCounter()

    test_rules = [
        ("B3/S23", "Game of Life"),
        ("B36/S23", "HighLife"),
        ("B/S", "Empty"),
    ]

    for rule, name in test_rules:
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print("=" * 60)
        result = counter.count(rule)
        print(result.summary())
