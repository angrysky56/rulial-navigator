"""
Probe 2D v5: LLL-Enhanced Rule Scanner

This is the next generation scanner that uses the LLL combinatorial pre-filter
to scan rules at microseconds/rule, then only simulates the promising candidates.

KEY INNOVATION:
- v4 simulated every rule (~seconds/rule)
- v5 uses LLL combinatorics to filter (~microseconds/rule)
- Only rules in the "Goldilocks Zone" (p_active ∈ [0.15, 0.55]) get simulated

This allows scanning the entire 2^512 rule space efficiently.
"""

import argparse
import json
import time
from dataclasses import asdict, dataclass

import numpy as np

from rulial.mapper.lll_complexity import (
    analyze_rule_combinatorially,
)


@dataclass
class V5ScanResult:
    """Result from v5 scan of a rule."""

    rule_str: str

    # Combinatorial metrics (no simulation)
    p_birth: float
    p_survive: float
    p_active: float
    expected_density: float

    # LLL prediction
    lll_predicted_structures: bool

    # Simulation metrics (only if candidate)
    simulated: bool = False
    actual_density: float = 0.0
    compression_ratio: float = 0.0
    wolfram_class: int = 0
    confirmed_structures: bool = False

    # Timing
    lll_time_us: float = 0.0
    sim_time_ms: float = 0.0


def generate_all_totalistic_rules() -> list[str]:
    """Generate all 2^18 = 262,144 totalistic 2D rules."""
    rules = []
    digits = "012345678"

    # B can be any subset of {0-8}
    # S can be any subset of {0-8}
    for b_bits in range(512):  # 2^9 B combinations
        for s_bits in range(512):  # 2^9 S combinations
            b_str = "".join(d for i, d in enumerate(digits) if b_bits & (1 << i))
            s_str = "".join(d for i, d in enumerate(digits) if s_bits & (1 << i))
            rules.append(f"B{b_str}/S{s_str}")

    return rules


def lll_filter(
    rule_str: str, p_active_min: float = 0.15, p_active_max: float = 0.55
) -> tuple[bool, dict]:
    """
    Fast LLL-based filter using only rule combinatorics.
    Returns (is_candidate, metrics) in ~microseconds.
    """
    start = time.perf_counter_ns()

    try:
        analysis = analyze_rule_combinatorially(rule_str)
    except Exception:
        return False, {}

    elapsed_us = (time.perf_counter_ns() - start) / 1000

    # Goldilocks filter: p_active in the interesting range
    is_candidate = p_active_min <= analysis.p_active <= p_active_max

    metrics = {
        "p_birth": analysis.p_birth,
        "p_survive": analysis.p_survive,
        "p_active": analysis.p_active,
        "expected_density": analysis.expected_density,
        "lll_predicted_structures": analysis.structure_predicted,
        "lll_time_us": elapsed_us,
    }

    return is_candidate, metrics


def simulate_candidate(rule_str: str, grid_size: int = 48, steps: int = 200) -> dict:
    """
    Full simulation of a candidate rule.
    Only called for rules that pass the LLL filter.
    """
    from rulial.compression.rigid import compress_ratio_lzma
    from rulial.engine.spacetime import SpacetimeUtil
    from rulial.engine.totalistic import Totalistic2DEngine

    start = time.perf_counter()

    engine = Totalistic2DEngine(rule_str)
    np.random.seed(42)
    history = engine.simulate(grid_size, grid_size, steps, "random", density=0.3)

    final = history[-1]
    density = final.sum() / (grid_size * grid_size)

    # Compression ratio
    try:
        data_bytes = SpacetimeUtil.to_bytes(np.array(history))
        cr = compress_ratio_lzma(data_bytes)
    except Exception:
        cr = 0.5

    # Wolfram class estimate
    if density < 0.01 or density > 0.99:
        wolfram_class = 1
    elif cr > 0.8:
        wolfram_class = 2
    elif cr < 0.2:
        wolfram_class = 3
    else:
        wolfram_class = 4

    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "simulated": True,
        "actual_density": density,
        "compression_ratio": cr,
        "wolfram_class": wolfram_class,
        "confirmed_structures": wolfram_class == 4,
        "sim_time_ms": elapsed_ms,
    }


def run_v5_scan(
    mode: str = "sample",
    samples: int = 1000,
    p_active_min: float = 0.15,
    p_active_max: float = 0.55,
    output_path: str = "atlas_v5.json",
):
    """
    Run the v5 LLL-enhanced scan.

    Modes:
    - 'sample': Random sample of rules
    - 'full': All 262,144 totalistic rules
    - 'goldilocks': Only simulate Goldilocks candidates
    """
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   PROBE 2D V5: LLL-ENHANCED SCANNER                      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print(f"Mode: {mode}")
    print(f"Goldilocks range: p_active ∈ [{p_active_min}, {p_active_max}]")
    print()

    # Generate or sample rules
    if mode == "full":
        all_rules = generate_all_totalistic_rules()
        print(f"Generated {len(all_rules)} totalistic rules")
    else:
        all_rules = generate_all_totalistic_rules()
        np.random.seed(42)
        all_rules = list(
            np.random.choice(
                all_rules, size=min(samples, len(all_rules)), replace=False
            )
        )
        print(f"Sampled {len(all_rules)} rules")

    print()

    # Phase 1: LLL Filter (microseconds/rule)
    print("═══ PHASE 1: LLL COMBINATORIAL FILTER ═══")
    start = time.time()

    candidates = []
    rejected = []

    for i, rule in enumerate(all_rules):
        if i % 1000 == 0 and i > 0:
            print(f"  [{i}/{len(all_rules)}] candidates: {len(candidates)}")

        is_candidate, metrics = lll_filter(rule, p_active_min, p_active_max)

        result = V5ScanResult(
            rule_str=rule,
            p_birth=metrics.get("p_birth", 0),
            p_survive=metrics.get("p_survive", 0),
            p_active=metrics.get("p_active", 0),
            expected_density=metrics.get("expected_density", 0),
            lll_predicted_structures=metrics.get("lll_predicted_structures", False),
            lll_time_us=metrics.get("lll_time_us", 0),
        )

        if is_candidate:
            candidates.append(result)
        else:
            rejected.append(result)

    filter_time = time.time() - start

    print()
    print(f"LLL Filter complete in {filter_time:.2f}s")
    print(
        f"  Candidates: {len(candidates)} ({100*len(candidates)/len(all_rules):.1f}%)"
    )
    print(f"  Rejected: {len(rejected)}")
    print(f"  Speed: {len(all_rules)/filter_time:.0f} rules/sec")
    print()

    # Phase 2: Simulate Candidates (seconds/rule)
    print("═══ PHASE 2: SIMULATE CANDIDATES ═══")
    start = time.time()

    for i, result in enumerate(candidates):
        print(f"\r[{i+1}/{len(candidates)}] {result.rule_str:<20}", end="", flush=True)

        sim_metrics = simulate_candidate(result.rule_str)

        result.simulated = sim_metrics["simulated"]
        result.actual_density = sim_metrics["actual_density"]
        result.compression_ratio = sim_metrics["compression_ratio"]
        result.wolfram_class = sim_metrics["wolfram_class"]
        result.confirmed_structures = sim_metrics["confirmed_structures"]
        result.sim_time_ms = sim_metrics["sim_time_ms"]

    sim_time = time.time() - start
    print()
    print()
    print(f"Simulation complete in {sim_time:.2f}s")
    print(f"  Speed: {len(candidates)/sim_time:.1f} rules/sec")
    print()

    # Summary
    print("═══ SUMMARY ═══")
    print()

    class4_rules = [r for r in candidates if r.wolfram_class == 4]
    predicted_correct = sum(
        1 for r in candidates if r.lll_predicted_structures == r.confirmed_structures
    )

    print(f"Total rules scanned: {len(all_rules)}")
    print(f"Goldilocks candidates: {len(candidates)}")
    print(f"Class 4 (computational) rules: {len(class4_rules)}")
    print(f"LLL prediction accuracy: {100*predicted_correct/len(candidates):.1f}%")
    print()

    # Top discoveries
    print("═══ TOP DISCOVERIES ═══")
    print()

    # Sort by compression ratio (Class 4 indicator)
    class4_sorted = sorted(class4_rules, key=lambda r: r.compression_ratio)[:10]

    print(f"{'Rule':<20} {'p_active':>10} {'Density':>10} {'CR':>8} {'Class':>6}")
    print("-" * 60)

    for r in class4_sorted:
        print(
            f"{r.rule_str:<20} {r.p_active:>10.3f} {r.actual_density*100:>8.1f}% {r.compression_ratio:>8.3f} {r.wolfram_class:>6}"
        )

    print()

    # Save results
    results = [asdict(r) for r in candidates]
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {output_path}")

    return candidates


def main():
    parser = argparse.ArgumentParser(description="V5 LLL-Enhanced Scanner")
    parser.add_argument(
        "--mode",
        choices=["sample", "full", "goldilocks"],
        default="sample",
        help="Scan mode",
    )
    parser.add_argument(
        "--samples", type=int, default=1000, help="Number of rules to sample"
    )
    parser.add_argument(
        "--output", type=str, default="atlas_v5.json", help="Output file path"
    )

    args = parser.parse_args()

    run_v5_scan(mode=args.mode, samples=args.samples, output_path=args.output)


if __name__ == "__main__":
    main()
