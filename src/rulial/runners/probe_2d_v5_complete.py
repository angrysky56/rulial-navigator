"""
V5 COMPLETE: The Discovery Engine

Integrates:
1. LLL Combinatorial Filter (The 72,000x Speedup)
2. Sheaf Harmonic Overlap (The "Goldilocks" Physics)
3. Fractal Dimension (The Geometric Proof)
4. Titans Neural Navigator (Intelligent Exploration)

Modes:
- 'sample': Random sample scan
- 'full': Exhaustive scan of all totalistic rules
- 'titans': LLL pre-filter + Titans-guided exploration

This is the final form of the rule scanner.
"""

import argparse
import json
import logging
import time
from dataclasses import asdict, dataclass
from functools import partial
from multiprocessing import Pool, cpu_count

import numpy as np

from rulial.mapper.fractal import (
    classify_by_fractal_dimension,
    compute_fractal_dimension,
)
from rulial.mapper.lll_complexity import analyze_rule_combinatorially


@dataclass
class V5Discovery:
    """Complete discovery record for a rule."""

    rule_str: str

    # Phase 1: LLL Combinatorics (no simulation)
    p_birth: float
    p_survive: float
    p_active: float
    lll_predicted: bool

    # Phase 2: Physics Validation (simulation)
    harmonic_overlap: float = 0.0
    monodromy_index: float = 0.0
    fractal_dimension: float = 0.0
    equilibrium_density: float = 0.0

    # Phase 3: Classification
    is_goldilocks: bool = False
    fractal_class: str = ""  # 'percolation', 'subcritical', etc.
    wolfram_class: int = 0

    # Timing
    lll_time_us: float = 0.0
    physics_time_ms: float = 0.0


def generate_all_totalistic_rules() -> list[str]:
    """Generate all 2^18 = 262,144 totalistic 2D rules."""
    rules = []
    digits = "012345678"

    for b_bits in range(512):
        for s_bits in range(512):
            b_str = "".join(d for i, d in enumerate(digits) if b_bits & (1 << i))
            s_str = "".join(d for i, d in enumerate(digits) if s_bits & (1 << i))
            rules.append(f"B{b_str}/S{s_str}")

    return rules


def lll_filter(
    rule_str: str, p_min: float = 0.15, p_max: float = 0.55
) -> tuple[bool, dict]:
    """
    Phase 1: LLL combinatorial filter.
    ~150,000 rules/second. No simulation needed.
    """
    start = time.perf_counter_ns()

    try:
        lll = analyze_rule_combinatorially(rule_str)
    except Exception:
        return False, {}

    elapsed_us = (time.perf_counter_ns() - start) / 1000

    # Goldilocks filter
    is_candidate = p_min <= lll.p_active <= p_max

    return is_candidate, {
        "p_birth": lll.p_birth,
        "p_survive": lll.p_survive,
        "p_active": lll.p_active,
        "lll_predicted": lll.structure_predicted,
        "lll_time_us": elapsed_us,
    }


def physics_validation(rule_str: str, grid_size: int = 48, steps: int = 100) -> dict:
    """
    Phase 2: Full physics validation with Sheaf + Fractal analysis.
    ~2-5 seconds per rule. Only called for LLL candidates.
    """
    start = time.perf_counter()

    result = {
        "harmonic_overlap": 0.0,
        "monodromy_index": 0.0,
        "fractal_dimension": 0.0,
        "equilibrium_density": 0.0,
        "is_goldilocks": False,
        "fractal_class": "unknown",
        "wolfram_class": 0,
    }

    try:
        # A. Sheaf Analysis (Harmonic Overlap + Monodromy)
        from rulial.mapper.sheaf import SheafAnalyzer

        sheaf = SheafAnalyzer(grid_size=grid_size, steps=steps)
        sheaf_result = sheaf.analyze(rule_str)

        result["harmonic_overlap"] = sheaf_result.harmonic_overlap
        result["monodromy_index"] = sheaf_result.monodromy_index

    except Exception:
        logging.exception(f"Sheaf analysis failed for rule {rule_str}")

    try:
        # B. Fractal Dimension (Geometry)
        from rulial.engine.totalistic import Totalistic2DEngine

        engine = Totalistic2DEngine(rule_str)
        np.random.seed(42)
        history = engine.simulate(grid_size, grid_size, steps, "random", density=0.3)
        final_grid = history[-1]

        result["equilibrium_density"] = final_grid.sum() / (grid_size * grid_size)
        result["fractal_dimension"] = compute_fractal_dimension(final_grid)
        result["fractal_class"] = classify_by_fractal_dimension(
            result["fractal_dimension"]
        )

    except Exception:
        logging.exception(f"Fractal analysis failed for rule {rule_str}")

    # C. Goldilocks Classification
    H = result["harmonic_overlap"]
    result["is_goldilocks"] = 0.3 <= H <= 0.6

    # D. Wolfram Class (enhanced)
    density = result["equilibrium_density"]
    d_f = result["fractal_dimension"]

    if density < 0.02 or density > 0.98:
        result["wolfram_class"] = 1  # Trivial
    elif result["is_goldilocks"]:
        result["wolfram_class"] = 4  # Computational
    elif d_f > 1.9:
        result["wolfram_class"] = 2  # Periodic/stable
    else:
        result["wolfram_class"] = 3  # Chaotic

    result["physics_time_ms"] = (time.perf_counter() - start) * 1000

    return result


def physics_validation_gpu(
    rule_str: str, grid_size: int = 48, steps: int = 100
) -> dict:
    """
    Phase 2: GPU-accelerated physics validation with Sheaf + Fractal.
    Uses PyTorch for Sheaf analysis on GPU.
    """
    start = time.perf_counter()

    result = {
        "harmonic_overlap": 0.0,
        "monodromy_index": 0.0,
        "fractal_dimension": 0.0,
        "equilibrium_density": 0.0,
        "is_goldilocks": False,
        "fractal_class": "unknown",
        "wolfram_class": 0,
    }

    try:
        # A. GPU Sheaf Analysis
        from rulial.mapper.sheaf_gpu import analyze_rule_gpu

        sheaf_result = analyze_rule_gpu(rule_str, grid_size, steps, device="cuda")

        result["harmonic_overlap"] = sheaf_result.harmonic_overlap
        result["monodromy_index"] = sheaf_result.monodromy_index

    except Exception:
        logging.exception(f"GPU Sheaf analysis failed for rule {rule_str}")
        # Fallback to CPU
        try:
            from rulial.mapper.sheaf import SheafAnalyzer

            sheaf = SheafAnalyzer(grid_size=grid_size, steps=steps)
            sheaf_result = sheaf.analyze(rule_str)
            result["harmonic_overlap"] = sheaf_result.harmonic_overlap
            result["monodromy_index"] = sheaf_result.monodromy_index
        except Exception:
            pass

    try:
        # B. Fractal Dimension (still CPU - fast enough)
        from rulial.engine.totalistic import Totalistic2DEngine

        engine = Totalistic2DEngine(rule_str)
        np.random.seed(42)
        history = engine.simulate(grid_size, grid_size, steps, "random", density=0.3)
        final_grid = history[-1]

        result["equilibrium_density"] = final_grid.sum() / (grid_size * grid_size)
        result["fractal_dimension"] = compute_fractal_dimension(final_grid)
        result["fractal_class"] = classify_by_fractal_dimension(
            result["fractal_dimension"]
        )

    except Exception:
        logging.exception(f"Fractal analysis failed for rule {rule_str}")

    # C. Goldilocks Classification
    H = result["harmonic_overlap"]
    result["is_goldilocks"] = 0.3 <= H <= 0.6

    # D. Wolfram Class (enhanced)
    density = result["equilibrium_density"]
    d_f = result["fractal_dimension"]

    if density < 0.02 or density > 0.98:
        result["wolfram_class"] = 1  # Trivial
    elif result["is_goldilocks"]:
        result["wolfram_class"] = 4  # Computational
    elif d_f > 1.9:
        result["wolfram_class"] = 2  # Periodic/stable
    else:
        result["wolfram_class"] = 3  # Chaotic

    result["physics_time_ms"] = (time.perf_counter() - start) * 1000

    return result


def rule_to_vector(rule_str: str) -> np.ndarray:
    """Convert B/S rule string to 18-bit binary vector for Titans."""
    digits = "012345678"
    vector = np.zeros(18, dtype=np.float32)

    parts = rule_str.upper().replace(" ", "").split("/")
    for part in parts:
        if part.startswith("B"):
            for i, d in enumerate(digits):
                if d in part[1:]:
                    vector[i] = 1.0
        elif part.startswith("S"):
            for i, d in enumerate(digits):
                if d in part[1:]:
                    vector[9 + i] = 1.0

    return vector


def vector_to_rule(vector: np.ndarray) -> str:
    """Convert 18-bit binary vector back to B/S rule string."""
    digits = "012345678"
    b_str = "".join(d for i, d in enumerate(digits) if vector[i] > 0.5)
    s_str = "".join(d for i, d in enumerate(digits) if vector[9 + i] > 0.5)
    return f"B{b_str}/S{s_str}"


def _physics_worker(rule_str: str) -> tuple:
    """Worker function for multiprocessing - must be at module level for pickle."""
    return (rule_str, physics_validation(rule_str))


def _physics_worker_gpu(rule_str: str) -> tuple:
    """GPU worker function for multiprocessing - must be at module level for pickle."""
    return (rule_str, physics_validation_gpu(rule_str))


def _write_batch_to_db(atlas, discoveries: list):
    """Write a batch of discoveries to the database efficiently."""
    try:
        for discovery in discoveries:
            atlas.conn.execute(
                """
                INSERT OR REPLACE INTO explorations (
                    rule_str, wolfram_class, phase, is_condensate,
                    equilibrium_density, harmonic_overlap, monodromy, 
                    sheaf_phase, p_birth, p_survive, p_active, lll_predicted,
                    fractal_dimension, fractal_class, b_set, s_set
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    discovery.rule_str,
                    discovery.wolfram_class,
                    "goldilocks" if discovery.is_goldilocks else "candidate",
                    0,  # is_condensate
                    discovery.equilibrium_density,
                    discovery.harmonic_overlap,
                    discovery.monodromy_index,
                    discovery.fractal_class,
                    discovery.p_birth,
                    discovery.p_survive,
                    discovery.p_active,
                    1 if discovery.lll_predicted else 0,
                    discovery.fractal_dimension,
                    discovery.fractal_class,
                    "",  # b_set
                    "",  # s_set
                ),
            )
        atlas.conn.commit()
    except Exception:
        logging.exception("Failed to write batch to database")


def run_titans_exploration(
    start_rules: list[str] = None,
    steps: int = 100,
    db_path: str = "atlas_v5_titans.db",
):
    """
    Titans-Guided Exploration Mode.

    Uses LLL to pre-filter, then Titans neural navigator to
    intelligently explore promising regions of rule space.

    Args:
        start_rules: Initial rules to seed exploration (defaults to known Goldilocks)
        steps: Number of exploration steps
        db_path: SQLite database path
    """
    from rulial.mapper.atlas import Atlas
    from rulial.navigator.titans import TitansNavigator

    print("╔══════════════════════════════════════════════════════════╗")
    print("║   V5 TITANS MODE: Intelligent Exploration               ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    # Initialize
    atlas = Atlas(db_path)
    titans = TitansNavigator(rule_size_bits=18)  # 9 B bits + 9 S bits

    # Default start rules (known Goldilocks)
    if start_rules is None:
        start_rules = ["B3/S23", "B36/S23", "B6/S123467"]

    print(f"Starting exploration from {len(start_rules)} seed rules")
    print(f"Steps: {steps}")
    print()

    # Track discoveries
    explored = set()
    goldilocks_found = []

    # Start with seed rules
    current_rules = [rule_to_vector(r) for r in start_rules]

    for step in range(steps):
        # Pick a current rule to explore from
        current_vec = current_rules[step % len(current_rules)]
        current_rule_str = vector_to_rule(current_vec)

        # Skip if already explored
        if current_rule_str in explored:
            # Mutate to find new territory
            idx = np.random.randint(0, 18)
            current_vec = current_vec.copy()
            current_vec[idx] = 1 - current_vec[idx]
            current_rule_str = vector_to_rule(current_vec)

        explored.add(current_rule_str)

        # Phase 1: LLL pre-check
        is_candidate, lll_metrics = lll_filter(current_rule_str)

        if not is_candidate:
            # Not in Goldilocks zone, let Titans hallucinate a better neighbor
            best_neighbor, predicted = titans.hallucinate_neighbors(
                current_vec, num_neighbors=20
            )
            current_rules.append(best_neighbor)
            continue

        # Phase 2: Full physics validation (only for LLL candidates)
        physics = physics_validation(current_rule_str)

        # Phase 3: Teach Titans about this rule
        # Use harmonic_overlap as the "entropy" signal
        entropy_signal = physics["harmonic_overlap"]
        surprise = titans.probe_and_learn(current_vec, entropy_signal)

        # Record discovery
        if physics["is_goldilocks"]:
            goldilocks_found.append(current_rule_str)
            print(
                f"[{step+1}/{steps}] 🌟 {current_rule_str}: H={physics['harmonic_overlap']:.3f} (surprise={surprise:.3f})"
            )
        else:
            print(
                f"\r[{step+1}/{steps}] {current_rule_str}: H={physics['harmonic_overlap']:.3f}",
                end="",
                flush=True,
            )

        # Store in database
        try:
            atlas.conn.execute(
                """
                INSERT OR REPLACE INTO explorations (
                    rule_str, wolfram_class, phase, harmonic_overlap, 
                    monodromy, fractal_dimension, fractal_class,
                    p_birth, p_survive, p_active, lll_predicted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    current_rule_str,
                    physics["wolfram_class"],
                    "goldilocks" if physics["is_goldilocks"] else "candidate",
                    physics["harmonic_overlap"],
                    physics["monodromy_index"],
                    physics["fractal_dimension"],
                    physics["fractal_class"],
                    lll_metrics.get("p_birth", 0),
                    lll_metrics.get("p_survive", 0),
                    lll_metrics.get("p_active", 0),
                    1 if lll_metrics.get("lll_predicted", False) else 0,
                ),
            )
            atlas.conn.commit()
        except Exception:
            logging.exception(f"Failed to insert rule {current_rule_str} into database")

        # Titans suggests next neighbor to explore
        best_neighbor, predicted = titans.hallucinate_neighbors(
            current_vec, num_neighbors=20
        )
        current_rules.append(best_neighbor)

    print()
    print()
    print("═══ TITANS EXPLORATION COMPLETE ═══")
    print()
    print(f"Rules explored: {len(explored)}")
    print(f"Goldilocks found: {len(goldilocks_found)}")
    print(f"Discovery rate: {100*len(goldilocks_found)/len(explored):.1f}%")
    print()

    if goldilocks_found:
        print("Top Goldilocks discoveries:")
        for rule in goldilocks_found[:10]:
            print(f"  🌟 {rule}")

    atlas.close()
    print(f"\nDatabase saved to {db_path}")

    return goldilocks_found


def run_discovery_engine(
    mode: str = "sample",
    samples: int = 500,
    db_path: str = "atlas_v5.db",
    output_json: str = "discoveries_v5.json",
    use_titans: bool = True,  # Enable Titans learning by default
    workers: int = 1,  # Number of parallel workers (1 = sequential)
    use_gpu: bool = False,  # Use GPU-accelerated Sheaf analysis
):
    """
    The complete V5 Discovery Engine with SQLite persistence.

    If use_titans=True, also trains a Titans neural model on all scanned rules.
    If workers > 1, uses multiprocessing for Phase 2 physics validation.
    """
    from rulial.mapper.atlas import Atlas

    # Determine actual worker count
    if workers <= 0:
        workers = max(1, cpu_count() - 1)  # Leave one core free

    print("╔══════════════════════════════════════════════════════════╗")
    if use_gpu:
        print("║   V5 DISCOVERY ENGINE: LLL + GPU SHEAF + FRACTAL         ║")
    elif use_titans:
        print("║   V5 DISCOVERY ENGINE: LLL + SHEAF + FRACTAL + TITANS   ║")
    else:
        print("║   V5 DISCOVERY ENGINE: LLL + SHEAF + FRACTAL             ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print(f"Database: {db_path}")
    print(f"GPU Sheaf: {'Enabled' if use_gpu else 'Disabled'}")
    print(f"Titans Learning: {'Enabled' if use_titans else 'Disabled'}")
    print(f"Workers: {workers} {'(parallel)' if workers > 1 else '(sequential)'}")
    print()

    # Initialize Titans if enabled (only in main process for sequential mode)
    titans = None
    if use_titans and workers == 1:
        try:
            from rulial.navigator.titans import TitansNavigator

            titans = TitansNavigator(rule_size_bits=18)
        except Exception as e:
            print(f"Warning: Could not initialize Titans: {e}")
            titans = None

    # Generate rules
    if mode == "full":
        all_rules = generate_all_totalistic_rules()
        print(f"Generated all {len(all_rules)} totalistic rules")
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

    # ═══ PHASE 1: LLL FILTER ═══
    print("═══ PHASE 1: LLL COMBINATORIAL FILTER ═══")
    start = time.time()

    candidates = []

    for i, rule in enumerate(all_rules):
        if i % 10000 == 0 and i > 0:
            print(f"  [{i}/{len(all_rules)}] candidates: {len(candidates)}")

        is_candidate, lll_metrics = lll_filter(rule)

        if is_candidate:
            discovery = V5Discovery(
                rule_str=rule,
                p_birth=lll_metrics["p_birth"],
                p_survive=lll_metrics["p_survive"],
                p_active=lll_metrics["p_active"],
                lll_predicted=lll_metrics["lll_predicted"],
                lll_time_us=lll_metrics["lll_time_us"],
            )
            candidates.append(discovery)

    filter_time = time.time() - start

    print()
    print(f"LLL Filter: {filter_time:.2f}s")
    print(
        f"  Candidates: {len(candidates)} ({100*len(candidates)/len(all_rules):.1f}%)"
    )
    print(f"  Speed: {len(all_rules)/filter_time:,.0f} rules/sec")
    print()

    # ═══ PHASE 2: PHYSICS VALIDATION ═══
    print("═══ PHASE 2: PHYSICS VALIDATION (Sheaf + Fractal) ═══")
    start = time.time()

    # Initialize Atlas database
    atlas = Atlas(db_path)

    goldilocks_count = 0
    candidate_rules = [d.rule_str for d in candidates]

    # Create a dict to look up discoveries by rule string
    discovery_map = {d.rule_str: d for d in candidates}

    def process_results(results_iter, total):
        """Process physics results (works for both sequential and parallel)."""
        nonlocal goldilocks_count
        batch = []

        for i, (rule_str, physics) in enumerate(results_iter):
            discovery = discovery_map[rule_str]
            discovery.harmonic_overlap = physics["harmonic_overlap"]
            discovery.monodromy_index = physics["monodromy_index"]
            discovery.fractal_dimension = physics["fractal_dimension"]
            discovery.equilibrium_density = physics["equilibrium_density"]
            discovery.is_goldilocks = physics["is_goldilocks"]
            discovery.fractal_class = physics["fractal_class"]
            discovery.wolfram_class = physics["wolfram_class"]
            discovery.physics_time_ms = physics["physics_time_ms"]

            # Titans learning (only in sequential mode)
            if titans is not None:
                rule_vec = rule_to_vector(discovery.rule_str)
                entropy_signal = discovery.harmonic_overlap
                titans.probe_and_learn(rule_vec, entropy_signal)

            # Batch database writes for efficiency
            batch.append(discovery)

            if discovery.is_goldilocks:
                goldilocks_count += 1
                print(
                    f"\r[{i+1}/{total}] {discovery.rule_str:<20} 🌟 H={discovery.harmonic_overlap:.3f} d_f={discovery.fractal_dimension:.3f}"
                )
            else:
                print(f"\r[{i+1}/{total}] {discovery.rule_str:<20}", end="", flush=True)

            # Write batch every 50 rules
            if len(batch) >= 50:
                _write_batch_to_db(atlas, batch)
                batch = []

        # Write remaining batch
        if batch:
            _write_batch_to_db(atlas, batch)

    if workers > 1:
        # Parallel processing
        worker_fn = _physics_worker_gpu if use_gpu else _physics_worker
        print(f"Using {workers} workers for parallel physics validation...")
        if use_gpu:
            print("  (GPU Sheaf analysis enabled)")

        with Pool(workers) as pool:
            results = pool.imap_unordered(worker_fn, candidate_rules, chunksize=10)
            process_results(results, len(candidates))
    else:
        # Sequential processing
        def sequential_results():
            if use_gpu:
                for rule_str in candidate_rules:
                    yield (rule_str, physics_validation_gpu(rule_str))
            else:
                for rule_str in candidate_rules:
                    yield (rule_str, physics_validation(rule_str))

        process_results(sequential_results(), len(candidates))

    physics_time = time.time() - start
    print()
    print()
    print(f"Physics Validation: {physics_time:.2f}s")
    print(f"  Speed: {len(candidates)/physics_time:.1f} rules/sec")
    print()

    # ═══ RESULTS ═══
    print("═══ DISCOVERY SUMMARY ═══")
    print()

    print(f"Total rules scanned: {len(all_rules)}")
    print(
        f"LLL candidates: {len(candidates)} ({100*len(candidates)/len(all_rules):.1f}%)"
    )
    print(
        f"Goldilocks (H=0.3-0.6): {goldilocks_count} ({100*goldilocks_count/len(candidates):.1f}% of candidates)"
    )
    print()

    # Class distribution
    class_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for d in candidates:
        if d.wolfram_class in class_counts:
            class_counts[d.wolfram_class] += 1

    print("Wolfram Class Distribution:")
    for c, count in class_counts.items():
        bar = "█" * (count // 5)
        print(f"  Class {c}: {bar} ({count})")
    print()

    # Fractal class distribution
    fractal_counts = {}
    for d in candidates:
        fc = d.fractal_class
        fractal_counts[fc] = fractal_counts.get(fc, 0) + 1

    print("Fractal Class Distribution:")
    for fc, count in sorted(fractal_counts.items(), key=lambda x: -x[1]):
        bar = "█" * (count // 5)
        print(f"  {fc}: {bar} ({count})")
    print()

    # Top discoveries
    print("═══ TOP GOLDILOCKS DISCOVERIES ═══")
    print()

    goldilocks = [d for d in candidates if d.is_goldilocks]
    goldilocks.sort(key=lambda d: d.harmonic_overlap, reverse=True)

    print(f"{'Rule':<20} {'H':>8} {'d_f':>8} {'Density':>10} {'Fractal Class':<15}")
    print("-" * 70)

    for d in goldilocks[:15]:
        print(
            f"{d.rule_str:<20} {d.harmonic_overlap:>8.3f} {d.fractal_dimension:>8.3f} "
            f"{d.equilibrium_density*100:>8.1f}% {d.fractal_class:<15}"
        )

    print()

    # Close database
    atlas.close()
    print(f"Database saved to {db_path}")

    # Also save JSON backup
    results = [asdict(d) for d in candidates]
    with open(output_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"JSON backup saved to {output_json}")

    return candidates


def main():
    parser = argparse.ArgumentParser(description="V5 Discovery Engine")
    parser.add_argument(
        "--mode",
        choices=["sample", "full", "titans"],
        default="sample",
        help="Scan mode: sample, full, or titans",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=500,
        help="Number of rules to sample (sample mode)",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=100,
        help="Number of exploration steps (titans mode)",
    )
    parser.add_argument(
        "--db", type=str, default="atlas_v5.db", help="SQLite database path"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="discoveries_v5.json",
        help="JSON output file path",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of parallel workers (0 = auto, 1 = sequential)",
    )
    parser.add_argument(
        "--gpu",
        action="store_true",
        help="Use GPU-accelerated Sheaf analysis (requires CUDA)",
    )

    args = parser.parse_args()

    if args.mode == "titans":
        run_titans_exploration(
            steps=args.steps,
            db_path=args.db,
        )
    else:
        run_discovery_engine(
            mode=args.mode,
            samples=args.samples,
            db_path=args.db,
            output_json=args.output,
            workers=args.workers,
            use_gpu=args.gpu,
        )


if __name__ == "__main__":
    main()
