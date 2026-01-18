"""
Rulial Probe V3 - The 2D Atlas Mapper.

This probe maps the 18-bit Totalistic Rule Space onto a 2D Grid:
- X-Axis: Born Bits (9 bits -> 0-511)
- Y-Axis: Survive Bits (9 bits -> 0-511)

It uses the EMPIRICALLY CALIBRATED metrics from verify_ground_truth.py to classify rules.
"""

import json
from dataclasses import asdict, dataclass

import numpy as np
from rich.console import Console
from rich.progress import Progress

from rulial.compression.metrics import TelemetryAnalyzer
from rulial.engine.totalistic import Totalistic2DEngine
from rulial.mapper.topology import TopologyMapper


# --- CALIBRATED CLASSIFIER ---
def classify_rule_calibrated(cr: float, betti_1: int) -> int:
    """
    Classify based on verify_ground_truth.py findings.

    Calibration:
    - Class 1 (Frozen): CR < 0.0015
    - Class 3 (Chaos): CR > 0.01 (and usually low Betti due to noise)
    - Class 4 (Complex): CR in [0.0015, 0.01] AND Betti_1 > 50
    """
    # 1. Frozen / Empty
    if cr < 0.0015:
        return 1

    # 3. Chaos / High Density
    if cr > 0.01:
        return 3

    # 4. The Goldilocks Zone
    if 0.0015 <= cr <= 0.01:
        if betti_1 > 50:
            return 4  # Complex
        else:
            return 2  # Periodic/Simple

    return 2  # Default fallback


@dataclass
class GridPoint:
    x: int  # Born (0-511)
    y: int  # Survive (0-511)
    rule_str: str
    wolfram_class: int
    compression_ratio: float
    betti_1: int


def get_rule_str(born: int, survive: int) -> str:
    """Convert int coords to B.../S... string."""
    b_bin = format(born, "09b")  # 0-8
    s_bin = format(survive, "09b")  # 0-8

    # Note: verify_ground_truth used 18-bit int where 0-8 are Born, 9-17 are Survive.
    # Here we map explicitly.
    # classic Game of Life 'B3/S23':
    # B3 means if 3 neighbors active, born.
    # S23 means if 2 or 3 neighbors active, survive.
    # Let's assume standard bitmask: bit k set means k neighbors.

    b_part = "".join([str(i) for i, bit in enumerate(reversed(b_bin)) if bit == "1"])
    s_part = "".join([str(i) for i, bit in enumerate(reversed(s_bin)) if bit == "1"])

    return f"B{b_part}/S{s_part}"


def analyze_grid_point(born: int, survive: int, steps: int = 200) -> GridPoint:
    rule_str = get_rule_str(born, survive)

    # 1. Simulate
    engine = Totalistic2DEngine(rule_str)
    # Use 'dense' seed per validation findings
    grid_history = engine.simulate(64, 64, steps, "dense")
    spacetime = np.stack(grid_history, axis=0)

    # 2. Metrics
    analyzer = TelemetryAnalyzer()
    telemetry = analyzer.analyze(spacetime.reshape(spacetime.shape[0], -1))

    # Only run TDA if compression is in the interesting range to save time?
    # Spec says "Mapper" runs TDA. Let's run it.
    topo_mapper = TopologyMapper()
    # Optimization: TDA is slow. Only run if CR is "kinda" interesting (> frozen)
    if telemetry.rigid_ratio_lzma > 0.0010:
        topo_sig = topo_mapper.compute_persistence(spacetime)
        betti_1 = topo_sig.betti_1
    else:
        betti_1 = 0

    w_class = classify_rule_calibrated(telemetry.rigid_ratio_lzma, betti_1)

    return GridPoint(
        x=born,
        y=survive,
        rule_str=rule_str,
        wolfram_class=w_class,
        compression_ratio=telemetry.rigid_ratio_lzma,
        betti_1=betti_1,
    )


def scan_region(x_start=0, x_end=512, y_start=0, y_end=512, sample_count=1000):
    """
    Scan a random subset of points within a region of the map.
    """
    console = Console()
    console.print(
        f"[bold]Mapping Region: Born[{x_start}-{x_end}] x Survive[{y_start}-{y_end}][/bold]"
    )

    # Generate all possible coords in region
    all_coords = [(x, y) for x in range(x_start, x_end) for y in range(y_start, y_end)]

    # Sample
    if len(all_coords) > sample_count:
        indices = np.random.choice(len(all_coords), sample_count, replace=False)
        coords_to_scan = [all_coords[i] for i in indices]
    else:
        coords_to_scan = all_coords

    results = []

    with Progress() as progress:
        task = progress.add_task("Mapping...", total=len(coords_to_scan))

        for x, y in coords_to_scan:
            try:
                pt = analyze_grid_point(x, y)
                results.append(asdict(pt))
            except Exception as e:
                console.print(f"[red]Error at {x},{y}: {e}[/red]")

            progress.update(task, advance=1)

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=100)
    parser.add_argument("--output", type=str, default="atlas_grid.json")
    args = parser.parse_args()

    data = scan_region(sample_count=args.samples)

    # Save
    with open(args.output, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Saved {len(data)} points to {args.output}")
