#!/usr/bin/env python
"""
S-Parameter Sweep: Systematic Phase Transition Analysis

This script fixes B=B0 and sweeps S from empty to full (S=012345678)
to identify phase transitions and density jumps.

Goal: Find where the 58% density jump occurs and what structures change.
"""

import json
import sys
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rulial.mapper.condensate import VacuumCondensateAnalyzer


def s_set_to_sum(s_str: str) -> int:
    """Convert S-set string to sum of digits."""
    return sum(int(c) for c in s_str if c.isdigit())


def generate_systematic_sweep():
    """Generate B0 rules with increasing S-complexity."""
    rules = []
    digits = "012345678"

    # Generate all possible S-sets and sort by sum
    for r in range(10):
        for combo in combinations(digits, r):
            s_str = "".join(combo)
            s_sum = sum(int(c) for c in s_str)
            rules.append(
                {
                    "rule": f"B0/S{s_str}" if s_str else "B0/S",
                    "s_str": s_str,
                    "s_sum": s_sum,
                    "s_count": len(s_str),
                }
            )

    # Sort by S-sum for systematic sweep
    rules.sort(key=lambda x: (x["s_sum"], x["s_count"]))

    return rules


def run_sweep(sample_size: int = 80):
    """Run the S-parameter sweep."""
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   S-PARAMETER SWEEP: PHASE TRANSITION ANALYSIS           ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    all_rules = generate_systematic_sweep()
    print(f"Total possible B0 rules: {len(all_rules)}")

    # Sample uniformly across S-sum range
    np.random.seed(42)
    indices = np.linspace(0, len(all_rules) - 1, sample_size, dtype=int)
    sample_rules = [all_rules[i] for i in indices]

    print(f"Sampling {len(sample_rules)} rules across S-sum range")
    print()

    analyzer = VacuumCondensateAnalyzer(grid_size=48, steps=300)
    results = []

    for i, r in enumerate(sample_rules):
        print(f"\r[{i+1}/{len(sample_rules)}] {r['rule']:<20}", end="", flush=True)

        try:
            result = analyzer.analyze(r["rule"])
            r["density"] = result.equilibrium_density
            r["expansion"] = result.expansion_factor
            r["is_condensate"] = result.is_condensate
            results.append(r)
        except Exception as e:
            print(f" ERROR: {e}")

    print()
    print()

    return results


def analyze_results(results: list):
    """Analyze the sweep results for phase transitions."""
    print("═══ DENSITY vs S-SUM ═══")
    print()

    # Sort by S-sum
    results.sort(key=lambda x: x["s_sum"])

    # Print table
    print(f"{'S-sum':>6} {'S-count':>8} {'Density':>10} {'Rule':<20}")
    print("-" * 50)

    prev_density = None
    for r in results:
        jump = ""
        if prev_density is not None:
            diff = abs(r["density"] - prev_density)
            if diff > 0.2:
                jump = f"← JUMP: {diff*100:.0f}%"

        print(
            f"{r['s_sum']:>6} {r['s_count']:>8} {r['density']*100:>8.1f}% {r['rule']:<20} {jump}"
        )
        prev_density = r["density"]

    print()

    # Statistical analysis
    s_sums = [r["s_sum"] for r in results]
    densities = [r["density"] for r in results]

    # Correlation
    r_corr = np.corrcoef(s_sums, densities)[0, 1]

    print("═══ STATISTICAL ANALYSIS ═══")
    print()
    print(f"   Correlation (S-sum ↔ Density): r = {r_corr:.3f}")
    print(f"   Density range: {min(densities)*100:.1f}% - {max(densities)*100:.1f}%")
    print()

    # Find jumps
    print("═══ DENSITY JUMPS ═══")
    print()

    jumps = []
    for i in range(1, len(results)):
        diff = results[i]["density"] - results[i - 1]["density"]
        if abs(diff) > 0.15:
            jumps.append({"from": results[i - 1], "to": results[i], "diff": diff})

    if jumps:
        for j in jumps:
            print(
                f"   {j['from']['rule']} ({j['from']['density']*100:.1f}%) → {j['to']['rule']} ({j['to']['density']*100:.1f}%)"
            )
            print(f"   Jump: {j['diff']*100:+.1f}%")
            print()
    else:
        print("   No major jumps detected (all < 15%)")

    print()

    # Group by S-sum and compute mean
    from collections import defaultdict

    by_ssum = defaultdict(list)
    for r in results:
        by_ssum[r["s_sum"]].append(r["density"])

    print("═══ MEAN DENSITY BY S-SUM ═══")
    print()

    ssum_means = []
    for s in sorted(by_ssum.keys()):
        mean_d = np.mean(by_ssum[s])
        ssum_means.append((s, mean_d))
        bar = "█" * int(mean_d * 50)
        print(f"   S-sum={s:2d}: {bar} {mean_d*100:.1f}%")

    print()

    return results, ssum_means


def create_visualization(results: list, ssum_means: list):
    """Create visualization of the sweep."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Plot 1: Density vs S-sum (all rules)
    ax1 = axes[0]
    s_sums = [r["s_sum"] for r in results]
    densities = [r["density"] * 100 for r in results]

    ax1.scatter(s_sums, densities, alpha=0.6, c="steelblue", s=50)
    ax1.set_xlabel("S-sum", fontsize=12)
    ax1.set_ylabel("Equilibrium Density (%)", fontsize=12)
    ax1.set_title("Density vs S-sum (B0 Rules)", fontsize=14)
    ax1.axhline(y=18, color="red", linestyle="--", label="Percolation threshold (~18%)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Mean density by S-sum
    ax2 = axes[1]
    s_vals = [x[0] for x in ssum_means]
    mean_densities = [x[1] * 100 for x in ssum_means]

    ax2.bar(s_vals, mean_densities, color="coral", alpha=0.7)
    ax2.set_xlabel("S-sum", fontsize=12)
    ax2.set_ylabel("Mean Equilibrium Density (%)", fontsize=12)
    ax2.set_title("Mean Density by S-sum", fontsize=14)
    ax2.axhline(y=18, color="red", linestyle="--", label="Percolation threshold")
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()

    output_path = Path(__file__).parent.parent / "fig_s_parameter_sweep.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"📊 Figure saved: {output_path}")
    plt.close()


def main():
    results = run_sweep(sample_size=60)
    results, ssum_means = analyze_results(results)
    create_visualization(results, ssum_means)

    # Save results
    output_path = Path(__file__).parent.parent / "s_parameter_sweep.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {output_path}")

    print()
    print("═══ CONCLUSION ═══")
    print()
    print("If density increases monotonically with S-sum:")
    print("   → Continuous crossover, NOT phase transition")
    print()
    print("If there are abrupt jumps:")
    print("   → Potential first-order phase transition")
    print()


if __name__ == "__main__":
    main()
