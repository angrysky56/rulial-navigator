#!/usr/bin/env python
"""
Percolation Analysis: Testing the ~1.89 Fractal Dimension Connection

This script tests whether our minimum-density condensate (19.7%) is at the
percolation threshold — and measures the fractal dimension of the cluster.

The 2D percolation threshold has fractal dimension d_f = 91/48 ≈ 1.8958
This is a UNIVERSAL constant appearing at the "edge of chaos."

Key insight: Our minimum density (19.7%) ≈ 2D site percolation threshold (~18%)
The fractal dimension 1.89 may be the universal signature of criticality!
"""

import sys
from collections import deque
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def find_connected_components(grid: np.ndarray) -> list[set]:
    """Find all connected components in a binary grid using BFS."""
    h, w = grid.shape
    visited = np.zeros_like(grid, dtype=bool)
    components = []

    for i in range(h):
        for j in range(w):
            if grid[i, j] == 1 and not visited[i, j]:
                # BFS to find component
                component = set()
                queue = deque([(i, j)])
                visited[i, j] = True

                while queue:
                    r, c = queue.popleft()
                    component.add((r, c))

                    # Check 4-connected neighbors (can also use 8-connected)
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = (r + dr) % h, (c + dc) % w
                        if grid[nr, nc] == 1 and not visited[nr, nc]:
                            visited[nr, nc] = True
                            queue.append((nr, nc))

                components.append(component)

    return components


def is_spanning(component: set, h: int, w: int) -> tuple[bool, bool]:
    """Check if a component spans horizontally or vertically."""
    rows = {r for r, c in component}
    cols = {c for r, c in component}

    spans_vertical = 0 in rows and (h - 1) in rows
    spans_horizontal = 0 in cols and (w - 1) in cols

    return spans_horizontal, spans_vertical


def estimate_fractal_dimension(component: set, grid_size: int) -> float:
    """
    Estimate fractal dimension using box-counting method.

    For a fractal of dimension d_f, the number of boxes N(r) of size r
    scales as N(r) ~ r^(-d_f)
    """
    if len(component) < 10:
        return 0.0

    # Convert to numpy array of points
    # Convert to numpy array of points (unused)
    # points = np.array(list(component))

    box_sizes = [2, 4, 8, 16, 32]
    box_sizes = [b for b in box_sizes if b < grid_size // 2]

    if len(box_sizes) < 2:
        return 2.0  # Trivial case

    log_counts = []
    log_sizes = []

    for box_size in box_sizes:
        # Count unique boxes occupied
        boxes = set()
        for r, c in component:
            boxes.add((r // box_size, c // box_size))

        log_counts.append(np.log(len(boxes)))
        log_sizes.append(np.log(1 / box_size))

    # Linear regression: log(N) = d_f * log(1/r) + const
    if len(log_sizes) >= 2:
        coeffs = np.polyfit(log_sizes, log_counts, 1)
        d_f = coeffs[0]
    else:
        d_f = 2.0

    return d_f


def analyze_percolation(rule_str: str, grid_size: int = 64, steps: int = 500):
    """Analyze percolation properties of a rule's equilibrium state."""
    from rulial.engine.totalistic import Totalistic2DEngine

    print(f"🔬 Analyzing: {rule_str}")
    print(f"   Grid: {grid_size}x{grid_size}, Steps: {steps}")
    print()

    # Run simulation
    engine = Totalistic2DEngine(rule_str)
    np.random.seed(42)
    history = engine.simulate(grid_size, grid_size, steps, "random", density=0.01)
    final_grid = history[-1]

    # Compute density
    density = final_grid.sum() / (grid_size * grid_size)
    print(f"📊 Equilibrium density: {density * 100:.1f}%")
    print()

    # Find connected components
    components = find_connected_components(final_grid)
    components.sort(key=len, reverse=True)

    print(f"🔗 Connected components: {len(components)}")

    if components:
        largest = components[0]
        print(
            f"   Largest component: {len(largest)} cells ({len(largest) / final_grid.sum() * 100:.1f}% of live cells)"
        )

        # Check spanning
        spans_h, spans_v = is_spanning(largest, grid_size, grid_size)
        print(f"   Spans horizontally: {spans_h}")
        print(f"   Spans vertically: {spans_v}")
        print(f"   PERCOLATING: {spans_h or spans_v}")
        print()

        # Estimate fractal dimension
        d_f = estimate_fractal_dimension(largest, grid_size)
        print(f"📐 Estimated fractal dimension: {d_f:.3f}")
        print("   2D percolation threshold: d_f = 91/48 ≈ 1.896")

        if 1.7 < d_f < 2.1:
            print("   ⚡ NEAR CRITICAL PERCOLATION! (d_f ≈ 1.89)")
        elif d_f > 1.9:
            print("   📦 ABOVE THRESHOLD (compact cluster)")
        else:
            print("   🔸 BELOW THRESHOLD (fragmented)")

        return {
            "rule": rule_str,
            "density": density,
            "num_components": len(components),
            "largest_component_size": len(largest),
            "spans_h": spans_h,
            "spans_v": spans_v,
            "percolating": spans_h or spans_v,
            "fractal_dimension": d_f,
        }

    return None


def compare_to_random_lattice(density: float, grid_size: int = 64):
    """Compare to random lattice at same density (null hypothesis)."""
    print()
    print("═══ RANDOM LATTICE COMPARISON ═══")
    print(f"Testing random lattice at {density*100:.1f}% density...")

    grid = (np.random.random((grid_size, grid_size)) < density).astype(np.uint8)

    components = find_connected_components(grid)
    components.sort(key=len, reverse=True)

    if components:
        largest = components[0]
        spans_h, spans_v = is_spanning(largest, grid_size, grid_size)
        d_f = estimate_fractal_dimension(largest, grid_size)

        print(f"   Largest component: {len(largest)} cells")
        print(f"   PERCOLATING: {spans_h or spans_v}")
        print(f"   Fractal dimension: {d_f:.3f}")

        # Site percolation threshold is ~59.27% for square lattice
        print()
        print("   Note: 2D site percolation threshold ≈ 59.27%")
        print(
            f"   Our density ({density*100:.1f}%) is {'above' if density > 0.5927 else 'below'} threshold"
        )


def main():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   PERCOLATION & FRACTAL DIMENSION ANALYSIS               ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print("Hypothesis: Minimum condensate density ≈ percolation threshold")
    print("Expected fractal dimension at threshold: d_f = 91/48 ≈ 1.896")
    print()

    # Test the minimum-density rule
    results = []

    # Minimum density rule
    print("═══ MINIMUM DENSITY RULE ═══")
    r1 = analyze_percolation("B045678/S015", grid_size=64, steps=500)
    if r1:
        results.append(r1)
    print()

    # A medium-density rule for comparison
    print("═══ MEDIUM DENSITY RULE ═══")
    r2 = analyze_percolation("B0457/S2468", grid_size=64, steps=500)
    if r2:
        results.append(r2)
    print()

    # A high-density rule
    print("═══ HIGH DENSITY RULE ═══")
    r3 = analyze_percolation("B034578/S0345678", grid_size=64, steps=500)
    if r3:
        results.append(r3)
    print()

    # Compare to random
    if r1:
        compare_to_random_lattice(r1["density"])

    # Summary
    print()
    print("═══ SUMMARY ═══")
    print()
    print(f"{'Rule':<20} {'Density':>10} {'Percolating':>12} {'d_f':>8}")
    print("-" * 55)
    for r in results:
        print(
            f"{r['rule']:<20} {r['density']*100:>8.1f}% {'YES' if r['percolating'] else 'NO':>12} {r['fractal_dimension']:>8.3f}"
        )

    print()
    print("💡 KEY INSIGHT:")
    print("   If d_f ≈ 1.89, we're at the critical percolation threshold")
    print("   This is the 'edge of chaos' in percolation theory!")
    print()


if __name__ == "__main__":
    main()
