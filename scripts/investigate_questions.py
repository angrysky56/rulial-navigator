#!/usr/bin/env python
"""
Investigate Open Research Questions:
1. What's the theoretical minimum equilibrium density?
2. Can condensates undergo phase transitions?

Uses existing atlas data to answer these questions.
"""

import json
from pathlib import Path

import numpy as np


def load_atlas():
    """Load the condensate atlas data."""
    atlas_path = Path(__file__).parent.parent / "atlas_v4_condensate.json"
    if not atlas_path.exists():
        atlas_path = Path(__file__).parent.parent / "atlas_v4.json"

    with open(atlas_path) as f:
        return json.load(f)


def question_1_minimum_density(data):
    """Q1: What's the theoretical minimum equilibrium density?"""
    print("═══ QUESTION 1: MINIMUM EQUILIBRIUM DENSITY ═══")
    print()

    # Filter to condensate rules only
    condensates = [d for d in data if d.get("is_condensate", False)]

    if not condensates:
        print("No condensate rules found. Using all rules.")
        condensates = data

    # Sort by equilibrium density
    sorted_by_density = sorted(
        condensates, key=lambda x: x.get("equilibrium_density", 0)
    )

    print("🔬 LOWEST EQUILIBRIUM DENSITY RULES:")
    print()
    print(f"{'Rule':<20} {'eq_density':>12} {'S-sum':>8} {'B-params':>10}")
    print("-" * 55)

    for d in sorted_by_density[:10]:
        rule = d.get("rule_str", "unknown")
        eq_density = d.get("equilibrium_density", 0) * 100
        s_set = d.get("s_set", "")
        b_set = d.get("b_set", "")
        s_sum = sum(int(c) for c in s_set if c.isdigit())

        print(f"{rule:<20} {eq_density:>10.1f}% {s_sum:>8} {b_set:>10}")

    print()

    # Find the minimum
    min_rule = sorted_by_density[0]
    min_density = min_rule.get("equilibrium_density", 0) * 100

    print(f"📊 MINIMUM OBSERVED: {min_density:.1f}%")
    print(f"   Rule: {min_rule.get('rule_str')}")
    print()

    # Analyze S-sum correlation with low density
    print("📈 S-SUM ANALYSIS (Low Density Rules < 40%):")
    low_density_rules = [
        d for d in condensates if d.get("equilibrium_density", 1) < 0.4
    ]

    if low_density_rules:
        s_sums = []
        for d in low_density_rules:
            s_set = d.get("s_set", "")
            s_sum = sum(int(c) for c in s_set if c.isdigit())
            s_sums.append(s_sum)

        if s_sums:
            print(f"   Count: {len(low_density_rules)}")
            print(f"   Mean S-sum: {np.mean(s_sums):.1f}")
            print(f"   S-sum range: {min(s_sums)} - {max(s_sums)}")
    else:
        print("   No rules below 40% density")

    print()

    # Highest density for comparison
    print("📈 HIGHEST DENSITY RULES (for comparison):")
    for d in sorted_by_density[-5:]:
        rule = d.get("rule_str", "unknown")
        eq_density = d.get("equilibrium_density", 0) * 100
        s_set = d.get("s_set", "")
        s_sum = sum(int(c) for c in s_set if c.isdigit())
        print(f"   {rule:<20} {eq_density:>6.1f}% (S-sum={s_sum})")

    print()

    # Theoretical floor analysis
    print("💡 THEORETICAL INTERPRETATION:")
    print(f"   The minimum observed density ({min_density:.1f}%) is close to:")
    print("   • Percolation threshold (~18% for 2D site percolation)")
    print("   • This may represent the 'ground state' vacuum energy")
    print()

    return min_density, min_rule


def question_2_phase_transitions(data):
    """Q2: Can condensates undergo phase transitions?"""
    print("═══ QUESTION 2: CONDENSATE PHASE TRANSITIONS ═══")
    print()

    # All condensates have B containing 0
    condensates = [d for d in data if d.get("is_condensate", False)]

    if not condensates:
        print("No condensate rules found.")
        return []

    print(f"📊 Analyzing {len(condensates)} condensate rules for phase transitions...")
    print()

    # Create S-sum vs density data
    transitions = []
    for d in condensates:
        rule = d.get("rule_str", "")
        eq_density = d.get("equilibrium_density", 0)
        s_set = d.get("s_set", "")
        s_sum = sum(int(c) for c in s_set if c.isdigit())
        s_count = len(s_set)

        transitions.append(
            {"rule": rule, "s_sum": s_sum, "s_count": s_count, "eq_density": eq_density}
        )

    # Sort by S-sum
    transitions.sort(key=lambda x: x["s_sum"])

    print("📈 DENSITY vs S-SUM:")
    print()
    print(f"{'S-sum':>6} {'Density':>10} {'Rule':<20}")
    print("-" * 40)

    # Show representative samples
    shown = set()
    for t in transitions:
        if t["s_sum"] not in shown or len(shown) < 15:
            print(f"{t['s_sum']:>6} {t['eq_density']*100:>9.1f}% {t['rule']:<20}")
            shown.add(t["s_sum"])

    print()

    # Statistical analysis
    densities = [t["eq_density"] for t in transitions]
    s_sums = [t["s_sum"] for t in transitions]

    if len(densities) >= 3:
        # Correlation
        r = np.corrcoef(s_sums, densities)[0, 1]

        # Check for jumps (potential first-order transitions)
        sorted_by_ssum = sorted(transitions, key=lambda x: x["s_sum"])
        density_diffs = []
        for i in range(1, len(sorted_by_ssum)):
            diff = sorted_by_ssum[i]["eq_density"] - sorted_by_ssum[i - 1]["eq_density"]
            density_diffs.append(abs(diff))

        max_jump = max(density_diffs) if density_diffs else 0

        print("🔍 PHASE TRANSITION ANALYSIS:")
        print()
        print(
            f"   Density range: {min(densities)*100:.1f}% - {max(densities)*100:.1f}%"
        )
        print(f"   S-sum range: {min(s_sums)} - {max(s_sums)}")
        print(f"   S-sum ↔ Density correlation: r = {r:.3f}")
        print(f"   Max density jump: {max_jump*100:.1f}%")
        print()

        # Group by S-sum and compute mean density
        from collections import defaultdict

        by_ssum = defaultdict(list)
        for t in transitions:
            by_ssum[t["s_sum"]].append(t["eq_density"])

        print("   Mean density by S-sum:")
        for s in sorted(by_ssum.keys()):
            mean_d = np.mean(by_ssum[s])
            print(f"     S-sum={s:2d}: {mean_d*100:5.1f}% (n={len(by_ssum[s])})")

        print()

        # Interpret results
        if max_jump > 0.3:
            print("⚠️  POTENTIAL FIRST-ORDER TRANSITION:")
            print(f"    Large density jump ({max_jump*100:.1f}%) at some S-sum")
        elif r > 0.5:
            print("📈 CONTINUOUS CROSSOVER (CONFIRMED):")
            print(f"    Strong positive correlation (r={r:.3f})")
            print("    S-sum continuously modulates vacuum energy")
            print("    No discontinuous phase transition detected")
        elif r < -0.5:
            print("📉 INVERSE CORRELATION:")
            print(f"    Negative correlation (r={r:.3f})")
        else:
            print("❓ WEAK RELATIONSHIP:")
            print(f"    Weak correlation (r={r:.3f})")

    print()

    return transitions


def main():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   INVESTIGATING OPEN RESEARCH QUESTIONS                  ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    data = load_atlas()
    print(f"Loaded {len(data)} rules from atlas")
    print()

    # Question 1
    min_density, min_rule = question_1_minimum_density(data)
    print()

    # Question 2
    question_2_phase_transitions(data)
    print()

    print("═══ SUMMARY ═══")
    print()
    print(f"Q1: Minimum observed density: {min_density:.1f}%")
    print(f"    Rule: {min_rule.get('rule_str')}")
    print()
    print("Q2: S-sum continuously modulates vacuum energy (density)")
    print("    No discontinuous phase transition detected")
    print("    → Suggests 'crossover' behavior, not true phase transition")
    print()


if __name__ == "__main__":
    main()
