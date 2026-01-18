"""
Rulial Probe V2 - Proper Implementation per Mapping-Infinite-Rulial-Space.md

This probe correctly uses:
1. Compression Progress (derivative of compressibility) - NOT raw entropy
2. Persistent Homology (betti_1 for loops/gliders)
3. Logical Depth proxy (steps * compression ratio)
4. Classification per Table 1 from the spec
"""

import json
from dataclasses import asdict, dataclass
from typing import List

import numpy as np
from rich.console import Console
from rich.progress import Progress
from rich.table import Table as RichTable

from rulial.compression.metrics import TelemetryAnalyzer
from rulial.engine.totalistic import Totalistic2DEngine
from rulial.mapper.topology import TopologyMapper


@dataclass
class RuleAnalysis:
    """Complete analysis of a single rule per the spec."""

    rule_id: int
    rule_str: str

    # Compression Metrics (Section 3.1)
    compression_ratio: float  # 0 = fully compressible, 1 = incompressible
    compression_progress: float  # Negative = learning = Class 4 candidate

    # Topological Metrics (Section 4.1)
    betti_0: int  # Connected components
    betti_1: int  # Loops (gliders/oscillators)
    max_persistence: float  # Longest-lived feature
    persistence_entropy: float  # Complexity of barcode

    # Derived Metrics
    logical_depth_proxy: float  # steps * (1 - compression_ratio)

    # Classification (Table 1)
    wolfram_class: int  # 1, 2, 3, or 4
    classification_reason: str

    # Raw stats
    final_population: int
    dynamism: int  # Changes between last 2 frames


def int_to_rule_str(n: int) -> str:
    """Convert 18-bit integer to B.../S... rule string."""
    bin_str = format(n, "018b")
    b_bits = bin_str[0:9]
    s_bits = bin_str[9:18]
    born = [i for i, bit in enumerate(b_bits) if bit == "1"]
    survive = [i for i, bit in enumerate(s_bits) if bit == "1"]
    return f"B{''.join(map(str, born))}/S{''.join(map(str, survive))}"


def classify_rule(
    cr: float, cp: float, betti_1: int, max_p: float, dynamism: int
) -> tuple:
    """
    Classify a rule per Empirical Data from 64x64 Grid Validation.

    Ground Truths observed:
    - Class 1 (Frozen): CR ~0.0012, B1 ~700
    - Class 3 (Chaos):  CR ~0.0430, B1 ~14
    - Class 4 (Life):   CR ~0.0022, B1 ~500
    - Class 4 (HiLife): CR ~0.0032, B1 ~240

    Calibration:
    - Class 1: CR < 0.0015
    - Class 3: CR > 0.01
    - Class 4: CR in [0.0015, 0.01] AND Betti_1 > 50
    """

    # Class 1: Frozen / Empty
    # Extremely compressible (mostly zeros)
    if cr < 0.0015:
        return (1, "Frozen: Extremely compressible (empty/dust)")

    # Class 3: Chaos / Dense
    # "High" compressibility for this domain (>1%), Loop destruction (low Betti)
    if cr > 0.01:
        if betti_1 < 50:
            return (3, "Chaos: High density, loop destruction")
        else:
            return (3, "Chaos: High density")

    # Class 4: Complex / Filaments
    # The Sweet Spot:
    # 1. Not empty (CR > 0.0015)
    # 2. Not full chaos (CR < 0.01)
    # 3. Preserves topological structure (Betti_1 > 50)
    if 0.0015 <= cr <= 0.01:
        if betti_1 > 50:
            return (4, "Complex: Goldilocks compression, rich topology")
        else:
            return (2, "Periodic: Goldilocks compression, simple topology")

    # Fallback
    return (2, "Periodic: Default")


def analyze_rule(
    rule_id: int, width: int = 64, height: int = 64, steps: int = 200
) -> RuleAnalysis:
    """
    Perform complete analysis of a single rule.
    """
    rule_str = int_to_rule_str(rule_id)

    # 1. Simulate
    engine = Totalistic2DEngine(rule_str)
    grid_history = engine.simulate(height, width, steps, "random")

    # 2. Build Spacetime Array (T x H x W -> Flatten to T x H*W for analysis)
    # For TDA, we need (Time, Space) point cloud
    # For Compression, we need the raw spacetime
    spacetime = np.stack(grid_history, axis=0)  # Shape: (steps+1, H, W)

    # 3. Compression Analysis
    analyzer = TelemetryAnalyzer()
    # Flatten spatial dims for compression analysis
    spacetime_flat = spacetime.reshape(spacetime.shape[0], -1)
    telemetry = analyzer.analyze(spacetime_flat)

    # 4. Topological Analysis
    topo_mapper = TopologyMapper()
    topo_sig = topo_mapper.compute_persistence(spacetime)

    # 5. Derived Metrics
    last_grid = grid_history[-1]
    prev_grid = grid_history[-2] if len(grid_history) > 1 else grid_history[-1]

    dynamism = int(np.sum(np.abs(last_grid.astype(int) - prev_grid.astype(int))))
    final_pop = int(np.sum(last_grid))

    # Logical Depth Proxy: How much "work" did the universe do?
    # Approximation: steps * (1 - compression_ratio)
    # Highly compressible = shallow, incompressible = could be deep or chaotic
    logical_depth = steps * (1 - telemetry.rigid_ratio_lzma)

    # 6. Classification
    wolfram_class, reason = classify_rule(
        telemetry.rigid_ratio_lzma,
        telemetry.loss_derivative,
        topo_sig.betti_1,
        topo_sig.max_persistence,
        dynamism,
    )

    return RuleAnalysis(
        rule_id=rule_id,
        rule_str=rule_str,
        compression_ratio=telemetry.rigid_ratio_lzma,
        compression_progress=telemetry.loss_derivative,
        betti_0=topo_sig.betti_0,
        betti_1=topo_sig.betti_1,
        max_persistence=topo_sig.max_persistence,
        persistence_entropy=topo_sig.persistence_entropy,
        logical_depth_proxy=logical_depth,
        wolfram_class=wolfram_class,
        classification_reason=reason,
        final_population=final_pop,
        dynamism=dynamism,
    )


def scan_rule_space(
    start: int = 0, end: int = 2**18, sample_size: int = 500
) -> List[RuleAnalysis]:
    """
    Scan a sample of the rule space and analyze each rule.
    """
    console = Console()
    results = []

    # Sample rules (can't do all 262k)
    if end - start <= sample_size:
        rules_to_scan = list(range(start, end))
    else:
        rules_to_scan = sorted(
            np.random.choice(range(start, end), sample_size, replace=False)
        )

    console.print(f"[bold]Scanning {len(rules_to_scan)} rules...[/bold]")

    with Progress() as progress:
        task = progress.add_task("Analyzing rules...", total=len(rules_to_scan))

        for rule_id in rules_to_scan:
            try:
                analysis = analyze_rule(rule_id, steps=100)  # Shorter for speed
                results.append(analysis)
            except Exception as e:
                console.print(f"[red]Error analyzing rule {rule_id}: {e}[/red]")

            progress.update(task, advance=1)

    return results


def generate_atlas_data(
    results: List[RuleAnalysis], output_file: str = "atlas_data.json"
):
    """
    Generate the Atlas of Ignorance data file.
    """
    # Convert to dicts and ensure all values are JSON-serializable
    data = []
    for r in results:
        d = asdict(r)
        # Convert numpy types to native Python types
        for k, v in d.items():
            if hasattr(v, "item"):  # numpy scalar
                d[k] = v.item()
            elif isinstance(v, np.ndarray):
                d[k] = v.tolist()
        data.append(d)

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Atlas data saved to {output_file}")

    # Print summary
    class_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for r in results:
        class_counts[r.wolfram_class] = class_counts.get(r.wolfram_class, 0) + 1

    console = Console()
    table = RichTable(title="Atlas Summary")
    table.add_column("Class", style="cyan")
    table.add_column("Count", style="magenta")
    table.add_column("Color", style="white")

    table.add_row("Class 1 (Frozen)", str(class_counts[1]), "Blue")
    table.add_row("Class 2 (Periodic)", str(class_counts[2]), "Blue")
    table.add_row("Class 3 (Chaos)", str(class_counts[3]), "Red")
    table.add_row(
        "Class 4 (Complex)", str(class_counts[4]), "[bold gold1]GOLD[/bold gold1]"
    )

    console.print(table)

    return data


if __name__ == "__main__":
    import sys

    sample_size = int(sys.argv[1]) if len(sys.argv) > 1 else 100

    results = scan_rule_space(sample_size=sample_size)
    generate_atlas_data(results)
