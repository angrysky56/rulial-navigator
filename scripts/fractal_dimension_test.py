#!/usr/bin/env python
"""
Fractal Dimension Analysis: Box-Counting Method

This script measures the actual fractal dimension of CA spacetimes
to validate (or refute) the hypothesis that Goldilocks rules exhibit
percolation-like fractal dimension d_f ≈ 91/48 ≈ 1.896.

IMPORTANT: We must actually MEASURE this, not just assert it.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rulial.engine.totalistic import Totalistic2DEngine


def box_counting_dimension(grid: np.ndarray, box_sizes: list[int] = None) -> float:
    """
    Compute fractal dimension using box-counting method.

    For a fractal of dimension d_f:
        N(r) ~ r^(-d_f)
    where N(r) is the number of boxes of size r that contain at least one point.

    Returns:
        Estimated fractal dimension.
    """
    h, w = grid.shape

    if box_sizes is None:
        # Use powers of 2 that fit in the grid
        box_sizes = [2**k for k in range(1, int(np.log2(min(h, w))))]

    if len(box_sizes) < 2:
        return 2.0  # Not enough scale range

    log_counts = []
    log_sizes = []

    for box_size in box_sizes:
        # Count boxes that contain at least one live cell
        count = 0
        for i in range(0, h, box_size):
            for j in range(0, w, box_size):
                box = grid[i : min(i + box_size, h), j : min(j + box_size, w)]
                if box.sum() > 0:
                    count += 1

        if count > 0:
            log_counts.append(np.log(count))
            log_sizes.append(np.log(1 / box_size))

    if len(log_counts) < 2:
        return 2.0

    # Linear regression: log(N) = d_f * log(1/r) + const
    coeffs = np.polyfit(log_sizes, log_counts, 1)
    d_f = coeffs[0]

    return d_f


def analyze_fractal_dimension(
    rule_str: str, grid_size: int = 128, steps: int = 200
) -> dict:
    """
    Analyze the fractal dimension of a rule's equilibrium state.
    """
    engine = Totalistic2DEngine(rule_str)

    # Run simulation
    np.random.seed(42)
    history = engine.simulate(grid_size, grid_size, steps, "random", density=0.3)

    # Take final frame
    final_grid = history[-1]

    # Compute fractal dimension
    d_f = box_counting_dimension(final_grid)

    # Compute density
    density = final_grid.sum() / (grid_size * grid_size)

    return {
        "rule": rule_str,
        "fractal_dimension": d_f,
        "density": density,
        "near_percolation": abs(d_f - 1.896) < 0.2,
    }


def main():
    print("═══ FRACTAL DIMENSION ANALYSIS ═══")
    print()
    print("Testing if Goldilocks rules exhibit d_f ≈ 91/48 ≈ 1.896")
    print("(the percolation threshold fractal dimension)")
    print()
    print("Grid: 128x128, 200 steps, box-counting method")
    print()

    # Test rules across different categories
    test_rules = [
        ("B3/S23", "Game of Life", "Goldilocks"),
        ("B6/S123467", "Goldilocks rule", "Goldilocks"),
        ("B36/S23", "HighLife", "Goldilocks"),
        ("B0/S058", "Min density condensate", "Threshold?"),
        ("B0/S012345678", "Dense condensate", "Dense"),
        ("B0/S", "Trivial condensate", "Sparse"),
        ("B35678/S5678", "Diamoeba", "Goldilocks"),
    ]

    print(f"{'Rule':<20} {'Type':<15} {'d_f':>8} {'Density':>10} {'~1.896?':>10}")
    print("-" * 70)

    results = []
    for rule, _name, category in test_rules:
        result = analyze_fractal_dimension(rule)
        check = "✓ YES" if result["near_percolation"] else "✗ NO"
        print(
            f"{rule:<20} {category:<15} {result['fractal_dimension']:>8.3f} {result['density']*100:>8.1f}% {check:>10}"
        )
        results.append(result)

    print()
    print("═══ PERCOLATION THRESHOLD REFERENCE ═══")
    print()
    print("2D site percolation threshold:")
    print("  Critical probability: p_c ≈ 0.5927")
    print("  Fractal dimension: d_f = 91/48 ≈ 1.8958")
    print()

    # Check if any rules match
    matches = [r for r in results if r["near_percolation"]]

    if matches:
        print("═══ RULES NEAR PERCOLATION THRESHOLD ═══")
        for r in matches:
            diff = abs(r["fractal_dimension"] - 1.896)
            print(f"  {r['rule']}: d_f = {r['fractal_dimension']:.3f} (Δ = {diff:.3f})")
    else:
        print("⚠️  NO RULES MATCHED PERCOLATION THRESHOLD (d_f ≈ 1.896)")
        print("    The 91/48 hypothesis may need revision.")

    print()
    print("═══ CONCLUSION ═══")
    print()

    goldilocks_df = np.mean(
        [
            r["fractal_dimension"]
            for r in results
            if "olds" in r["rule"].lower() or r["rule"] in ["B3/S23", "B36/S23"]
        ]
    )
    all_df = np.mean([r["fractal_dimension"] for r in results])

    print(f"Mean d_f (Goldilocks rules): {goldilocks_df:.3f}")
    print(f"Mean d_f (all tested rules): {all_df:.3f}")
    print("Percolation threshold: 1.896")
    print()

    if abs(goldilocks_df - 1.896) < 0.3:
        print("✓ Goldilocks rules ARE near the percolation threshold!")
    else:
        print("✗ Goldilocks rules do NOT match percolation threshold.")
        print("  The 91/48 connection should be labeled as HYPOTHESIS, not fact.")


if __name__ == "__main__":
    main()
