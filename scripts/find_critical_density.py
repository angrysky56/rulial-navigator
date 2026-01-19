#!/usr/bin/env python
"""
Critical Density Finder: Locate the Exact Percolation Threshold

This script systematically generates B0 rules with varying S-parameters
to find the exact density at which percolation breaks down.

Hypothesis: The critical density is ~18-20%, near the 2D percolation threshold.
"""

import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rulial.mapper.condensate import VacuumCondensateAnalyzer


def generate_all_b0_s_combinations():
    """Generate all possible B0/S... rules."""
    rules = []
    # S can be any subset of {0,1,2,3,4,5,6,7,8}
    digits = "012345678"

    for r in range(10):  # 0 to 9 S-parameters
        for combo in combinations(digits, r):
            s_str = "".join(combo)
            rule = f"B0/S{s_str}" if s_str else "B0/S"
            rules.append(rule)

    return rules


def measure_density(rule_str: str, grid_size: int = 48, steps: int = 300) -> float:
    """Measure equilibrium density of a rule."""
    try:
        analyzer = VacuumCondensateAnalyzer(grid_size=grid_size, steps=steps)
        result = analyzer.analyze(rule_str)
        return result.equilibrium_density
    except Exception:
        return -1.0


def find_critical_density():
    """Find the critical density by scanning B0 rules."""
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   FINDING THE CRITICAL PERCOLATION DENSITY               ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print("Scanning B0/S... rules to find minimum stable density...")
    print()

    rules = generate_all_b0_s_combinations()
    print(f"Generated {len(rules)} possible B0 rules")
    print()

    # Sample a subset for speed
    np.random.seed(42)
    sample_rules = np.random.choice(rules, size=min(100, len(rules)), replace=False)

    results = []

    for i, rule in enumerate(sample_rules):
        print(f"\r[{i+1}/{len(sample_rules)}] Testing {rule:<20}", end="", flush=True)
        density = measure_density(rule)
        if density >= 0:
            results.append(
                {
                    "rule": rule,
                    "density": density,
                    "s_set": rule.split("/S")[1] if "/S" in rule else "",
                    "s_sum": (
                        sum(int(c) for c in rule.split("/S")[1] if c.isdigit())
                        if "/S" in rule
                        else 0
                    ),
                }
            )

    print()
    print()

    # Sort by density
    results.sort(key=lambda x: x["density"])

    # Find the critical zone
    print("═══ LOWEST DENSITY RULES ═══")
    print()
    print(f"{'Rule':<20} {'Density':>10} {'S-sum':>8}")
    print("-" * 40)

    for r in results[:20]:
        marker = "← CRITICAL?" if r["density"] < 0.25 else ""
        print(f"{r['rule']:<20} {r['density']*100:>8.1f}% {r['s_sum']:>8} {marker}")

    print()

    # Identify the threshold
    low_density_rules = [r for r in results if r["density"] < 0.25]

    if low_density_rules:
        min_rule = low_density_rules[0]
        print(f"📊 MINIMUM DENSITY FOUND: {min_rule['density']*100:.1f}%")
        print(f"   Rule: {min_rule['rule']}")
        print()

        # Analyze what S-combinations give low density
        print("📈 PATTERN ANALYSIS (low-density rules):")
        s_sums = [r["s_sum"] for r in low_density_rules]
        s_counts = [len(r["s_set"]) for r in low_density_rules]

        print(f"   Mean S-sum: {np.mean(s_sums):.1f}")
        print(f"   Mean S-count: {np.mean(s_counts):.1f}")

    print()

    # Density histogram
    densities = [r["density"] for r in results]
    print("📊 DENSITY DISTRIBUTION:")

    bins = [0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    for i in range(len(bins) - 1):
        count = sum(1 for d in densities if bins[i] <= d < bins[i + 1])
        bar = "█" * count
        print(f"   {bins[i]*100:>3.0f}%-{bins[i+1]*100:<3.0f}%: {bar} ({count})")

    print()
    print("💡 INTERPRETATION:")
    print("   If minimum density ≈ 18-20%, this is the percolation threshold")
    print("   Below this, the membrane cannot remain connected")
    print()

    return results


def main():
    results = find_critical_density()

    # Save results
    output_path = Path(__file__).parent.parent / "critical_density_scan.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
