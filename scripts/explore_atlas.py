#!/usr/bin/env python3
"""
Atlas Data Explorer - Interactive analysis of V6 GPU scan results.

Usage:
    uv run python scripts/explore_atlas.py --db data/atlas_full_v6_gpu.db

    # Or with specific analysis:
    uv run python scripts/explore_atlas.py --db data/atlas_full_v6_gpu.db --top-goldilocks 20
    uv run python scripts/explore_atlas.py --db data/atlas_full_v6_gpu.db --visualize
    uv run python scripts/explore_atlas.py --db data/atlas_full_v6_gpu.db --find-similar "B3/S23"
"""

import argparse
import sqlite3
from pathlib import Path

import numpy as np


def connect(db_path: str):
    """Connect to atlas database."""
    return sqlite3.connect(db_path)


def overview(conn):
    """Print overview statistics."""
    cur = conn.cursor()

    print("\n" + "═" * 60)
    print("  ATLAS OVERVIEW")
    print("═" * 60)

    # Total rules
    total = cur.execute("SELECT COUNT(*) FROM explorations").fetchone()[0]
    print(f"\n📊 Total rules scanned: {total:,}")

    # Wolfram class distribution
    print("\n🧠 Wolfram Class Distribution:")
    for class_id, name in [
        (1, "Dies out"),
        (2, "Stable/Periodic"),
        (3, "Chaotic"),
        (4, "Complex"),
    ]:
        count = cur.execute(
            "SELECT COUNT(*) FROM explorations WHERE wolfram_class=?", (class_id,)
        ).fetchone()[0]
        pct = 100 * count / total if total > 0 else 0
        bar = "█" * int(pct / 2)
        print(f"  Class {class_id} ({name:15}): {count:6,} ({pct:5.1f}%) {bar}")

    # Goldilocks zone
    goldilocks = cur.execute(
        "SELECT COUNT(*) FROM explorations WHERE harmonic_overlap BETWEEN 0.3 AND 0.6"
    ).fetchone()[0]
    print(
        f"\n🌟 Goldilocks Zone (H=0.3-0.6): {goldilocks:,} rules ({100*goldilocks/total:.1f}%)"
    )

    # Harmonic overlap stats
    stats = cur.execute(
        """
        SELECT 
            MIN(harmonic_overlap), 
            MAX(harmonic_overlap), 
            AVG(harmonic_overlap)
        FROM explorations
    """
    ).fetchone()
    print(
        f"\n📈 Harmonic Overlap: min={stats[0]:.3f}, max={stats[1]:.3f}, avg={stats[2]:.3f}"
    )

    # Fractal class distribution
    print("\n🔬 Fractal Class Distribution:")
    for row in cur.execute(
        "SELECT fractal_class, COUNT(*) FROM explorations GROUP BY fractal_class ORDER BY COUNT(*) DESC"
    ):
        pct = 100 * row[1] / total
        print(f"  {row[0]:15}: {row[1]:6,} ({pct:5.1f}%)")


def top_goldilocks(conn, n: int = 20):
    """Show top N rules in the Goldilocks zone."""
    cur = conn.cursor()

    print("\n" + "═" * 60)
    print(f"  TOP {n} GOLDILOCKS RULES (H closest to 0.5)")
    print("═" * 60)
    print(f"\n{'Rule':<20} {'H':>8} {'d_f':>8} {'Class':>6} {'Fractal':>15}")
    print("-" * 60)

    rows = cur.execute(
        """
        SELECT rule_str, harmonic_overlap, fractal_dimension, wolfram_class, fractal_class
        FROM explorations 
        WHERE harmonic_overlap BETWEEN 0.3 AND 0.6
        ORDER BY ABS(harmonic_overlap - 0.5)
        LIMIT ?
    """,
        (n,),
    ).fetchall()

    for row in rows:
        print(f"{row[0]:<20} {row[1]:>8.3f} {row[2]:>8.3f} {row[3]:>6} {row[4]:>15}")


def find_similar(conn, rule_str: str, n: int = 10):
    """Find rules similar to the given rule."""
    cur = conn.cursor()

    # Get target rule metrics
    target = cur.execute(
        """
        SELECT harmonic_overlap, fractal_dimension, wolfram_class
        FROM explorations WHERE rule_str = ?
    """,
        (rule_str,),
    ).fetchone()

    if not target:
        print(f"\n❌ Rule '{rule_str}' not found in database.")
        return

    h, d_f, wc = target
    print(
        f"\n🔍 Finding rules similar to {rule_str} (H={h:.3f}, d_f={d_f:.3f}, Class {wc})"
    )
    print("=" * 60)

    # Find similar by H and d_f
    rows = cur.execute(
        """
        SELECT rule_str, harmonic_overlap, fractal_dimension, wolfram_class,
               ABS(harmonic_overlap - ?) + ABS(fractal_dimension - ?) as distance
        FROM explorations 
        WHERE rule_str != ?
        ORDER BY distance
        LIMIT ?
    """,
        (h, d_f, rule_str, n),
    ).fetchall()

    print(f"\n{'Rule':<20} {'H':>8} {'d_f':>8} {'Class':>6} {'Distance':>10}")
    print("-" * 60)
    for row in rows:
        print(f"{row[0]:<20} {row[1]:>8.3f} {row[2]:>8.3f} {row[3]:>6} {row[4]:>10.4f}")


def visualize(conn, output_dir: str = "data/visualizations"):
    """Generate visualizations of the atlas data."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("❌ matplotlib not installed. Run: uv pip install matplotlib")
        return

    cur = conn.cursor()
    Path(output_dir).mkdir(exist_ok=True)

    print("\n📊 Generating visualizations...")

    # Fetch data
    rows = cur.execute(
        """
        SELECT harmonic_overlap, fractal_dimension, wolfram_class, equilibrium_density
        FROM explorations
    """
    ).fetchall()

    H = np.array([r[0] for r in rows])
    d_f = np.array([r[1] for r in rows])
    wc = np.array([r[2] for r in rows])

    # 1. Harmonic Overlap Distribution
    plt.figure(figsize=(10, 6))
    plt.hist(H, bins=50, edgecolor="black", alpha=0.7, color="steelblue")
    plt.axvline(0.3, color="red", linestyle="--", label="Goldilocks Zone")
    plt.axvline(0.6, color="red", linestyle="--")
    plt.xlabel("Harmonic Overlap (H)")
    plt.ylabel("Count")
    plt.title("Distribution of Harmonic Overlap in Rule Space")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/harmonic_distribution.png", dpi=150)
    print(f"  ✓ {output_dir}/harmonic_distribution.png")

    # 2. H vs Fractal Dimension scatter colored by Wolfram class
    plt.figure(figsize=(12, 8))
    colors = {1: "gray", 2: "blue", 3: "orange", 4: "green"}
    labels = {
        1: "Class 1 (Dies)",
        2: "Class 2 (Stable)",
        3: "Class 3 (Chaotic)",
        4: "Class 4 (Complex)",
    }

    for c in [1, 2, 3, 4]:
        mask = wc == c
        plt.scatter(H[mask], d_f[mask], c=colors[c], alpha=0.3, s=10, label=labels[c])

    plt.axvline(0.3, color="red", linestyle="--", alpha=0.5)
    plt.axvline(0.6, color="red", linestyle="--", alpha=0.5)
    plt.xlabel("Harmonic Overlap (H)")
    plt.ylabel("Fractal Dimension (d_f)")
    plt.title("Phase Space: Harmonic Overlap vs Fractal Dimension")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/phase_space.png", dpi=150)
    print(f"  ✓ {output_dir}/phase_space.png")

    # 3. Wolfram class pie chart
    plt.figure(figsize=(8, 8))
    class_counts = [np.sum(wc == c) for c in [1, 2, 3, 4]]
    plt.pie(
        class_counts,
        labels=["Class 1", "Class 2", "Class 3", "Class 4"],
        autopct="%1.1f%%",
        colors=["gray", "blue", "orange", "green"],
    )
    plt.title("Wolfram Class Distribution")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/wolfram_classes.png", dpi=150)
    print(f"  ✓ {output_dir}/wolfram_classes.png")

    print(f"\n✅ Visualizations saved to {output_dir}/")


def simulate_rule(rule_str: str, size: int = 64, steps: int = 100):
    """Simulate a rule and display ASCII animation."""
    try:
        from rulial.engine.totalistic import Totalistic2DEngine
    except ImportError:
        print("❌ Could not import rulial engine")
        return

    import time

    engine = Totalistic2DEngine(rule_str)
    np.random.seed(42)
    history = engine.simulate(size, size, steps, "random", density=0.3)

    print(f"\n🎬 Simulating {rule_str} ({size}x{size}, {steps} steps)")
    print("Press Ctrl+C to stop\n")

    try:
        for i, grid in enumerate(history):
            # Clear screen
            print("\033c", end="")
            print(f"Rule: {rule_str} | Step: {i+1}/{steps} | Population: {grid.sum()}")

            # ASCII render (downsample for terminal)
            scale = max(1, size // 40)
            for y in range(0, min(size, 40), scale):
                row = ""
                for x in range(0, min(size, 80), scale):
                    if grid[y, x] > 0:
                        row += "██"
                    else:
                        row += "  "
                print(row)

            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n\nStopped.")


def main():
    parser = argparse.ArgumentParser(description="Atlas Data Explorer")
    parser.add_argument(
        "--db", default="data/atlas_full_v6_gpu.db", help="Database path"
    )
    parser.add_argument(
        "--overview", action="store_true", help="Show overview statistics"
    )
    parser.add_argument(
        "--top-goldilocks", type=int, metavar="N", help="Show top N Goldilocks rules"
    )
    parser.add_argument(
        "--find-similar", type=str, metavar="RULE", help="Find rules similar to RULE"
    )
    parser.add_argument(
        "--visualize", action="store_true", help="Generate visualizations"
    )
    parser.add_argument(
        "--simulate", type=str, metavar="RULE", help="Simulate a rule (ASCII animation)"
    )

    args = parser.parse_args()

    # Default to overview if no specific action requested
    if not any([args.top_goldilocks, args.find_similar, args.visualize, args.simulate]):
        args.overview = True

    conn = connect(args.db)

    if args.overview:
        overview(conn)

    if args.top_goldilocks:
        top_goldilocks(conn, args.top_goldilocks)

    if args.find_similar:
        find_similar(conn, args.find_similar)

    if args.visualize:
        visualize(conn)

    if args.simulate:
        simulate_rule(args.simulate)

    conn.close()


if __name__ == "__main__":
    main()
