"""
Probe 2D V4: Modern Atlas Scanner.

Incorporates:
- VacuumCondensateAnalyzer for phase detection
- T-P+E Framework for dynamics classification
- Multi-signal voting for Wolfram class
- Topology (β₁) from GUDHI
"""

import argparse
import json
import logging
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from rulial.compression.flow import CompressionFlowAnalyzer
from rulial.engine.totalistic import Totalistic2DEngine
from rulial.mapper.condensate import VacuumCondensateAnalyzer
from rulial.mapper.topology import TopologyMapper
from rulial.mapper.tpe import TPEAnalyzer

console = Console()
logging.basicConfig(level=logging.WARNING)


@dataclass
class RuleAnalysis:
    """Complete analysis of a single rule."""

    # Identity
    rule_str: str
    b_set: str
    s_set: str

    # Grid location (for visualization)
    x: int  # x = B index (0-511)
    y: int  # y = S index (0-511)

    # Core metrics
    compression_ratio: float
    signal: str  # CURIOSITY, FRUSTRATION, BOREDOM

    # T-P+E
    toroidal: float
    poloidal: float
    emergence: float
    tpe_mode: str  # T-dominant, P-dominant, balanced, dead

    # Condensate
    is_condensate: bool
    equilibrium_density: float
    expansion_factor: float

    # Topology
    betti_1: int

    # Population
    final_population: int

    # Classification
    wolfram_class: int  # 1, 2, 3, 4
    phase: str  # particle, condensate, hybrid, n/a

    def to_dict(self) -> dict:
        return asdict(self)


def parse_rule_to_sets(rule_str: str) -> tuple[str, str]:
    """Extract B and S sets from rule string."""
    parts = rule_str.replace("B", "").split("/S")
    return parts[0], parts[1] if len(parts) > 1 else ""


def sets_to_indices(b_str: str, s_str: str) -> tuple[int, int]:
    """Convert B/S strings to grid indices 0-511."""
    b_bits = sum(1 << int(c) for c in b_str) if b_str else 0
    s_bits = sum(1 << int(c) for c in s_str) if s_str else 0
    return b_bits, s_bits


def classify_rule(metrics: dict) -> tuple[int, str]:
    """
    Multi-signal voting for Wolfram class and phase.

    Returns (wolfram_class, phase)
    """
    cr = metrics.get("compression_ratio", 0)
    tpe_mode = metrics.get("tpe_mode", "unknown")
    is_condensate = metrics.get("is_condensate", False)
    betti_1 = metrics.get("betti_1", 0)
    final_pop = metrics.get("final_population", 0)
    signal = metrics.get("signal", "")

    # Class 1: Dead (everything dies)
    if final_pop == 0:
        return 1, "n/a"

    # Class 2: Periodic (very low CR, stable structure, low topology)
    if cr < 0.02 and betti_1 < 5 and tpe_mode in ("dead", "P-dominant"):
        return 2, "n/a"

    # Class 4: Complex (multiple signals agree)
    class4_votes = 0

    # Signal says CURIOSITY
    if signal == "CURIOSITY":
        class4_votes += 2

    # T-P balanced
    if tpe_mode == "balanced":
        class4_votes += 2

    # Is condensate (spontaneous expansion)
    if is_condensate:
        class4_votes += 3

    # High topology
    if betti_1 > 20:
        class4_votes += 2
    elif betti_1 > 10:
        class4_votes += 1

    # Moderate compression ratio (not too simple, not chaos)
    if 0.02 <= cr <= 0.15:
        class4_votes += 1

    # Determine class
    if class4_votes >= 4:
        # Determine phase
        if is_condensate:
            phase = "condensate"
        elif betti_1 > 10:
            phase = "particle"
        else:
            phase = "hybrid"
        return 4, phase

    # Class 3: Chaos (high activity, T-dominant, or high CR)
    if tpe_mode == "T-dominant" or cr > 0.15 or signal == "FRUSTRATION":
        return 3, "n/a"

    # Default to Class 2 (periodic/stable)
    return 2, "n/a"


class Probe2DV4:
    """V4 Atlas Scanner with modern classification."""

    def __init__(
        self,
        grid_size: int = 48,
        steps: int = 150,
        output_file: str = "atlas_v4.json",
    ):
        self.grid_size = grid_size
        self.steps = steps
        self.output_file = Path(output_file)

        # Analyzers
        self.flow_analyzer = CompressionFlowAnalyzer(window_size=20)
        self.tpe_analyzer = TPEAnalyzer()
        self.condensate_analyzer = VacuumCondensateAnalyzer(
            grid_size=32, steps=80  # Faster for scanning
        )
        self.topo_mapper = TopologyMapper()

        # Results
        self.results: List[RuleAnalysis] = []

    def analyze_rule(self, rule_str: str) -> Optional[RuleAnalysis]:
        """Perform full analysis on a single rule."""
        try:
            b_str, s_str = parse_rule_to_sets(rule_str)
            x, y = sets_to_indices(b_str, s_str)

            # 1. Simulate to get final state
            engine = Totalistic2DEngine(rule_str)
            history = engine.simulate(
                self.grid_size, self.grid_size, self.steps, "random", density=0.3
            )
            final_grid = history[-1]
            final_pop = int(final_grid.sum())

            # 2. Compression Flow
            flow_result = self.flow_analyzer.analyze(
                rule_str, steps=self.steps, grid_size=self.grid_size
            )

            # 3. T-P+E
            tpe_result = self.tpe_analyzer.analyze(
                rule_str, steps=100, grid_size=self.grid_size
            )

            # 4. Condensate (only if population survived)
            if final_pop > 0:
                cond_result = self.condensate_analyzer.analyze(rule_str)
                is_condensate = cond_result.is_condensate
                eq_density = cond_result.equilibrium_density
                expansion = cond_result.expansion_factor
            else:
                is_condensate = False
                eq_density = 0.0
                expansion = 0.0

            # 5. Topology - need spacetime (3D array) for persistence
            import numpy as np

            spacetime = np.stack(history[-50:], axis=0)  # Last 50 frames
            topo_result = self.topo_mapper.compute_persistence(spacetime)
            betti_1 = topo_result.betti_1

            # 6. Classification
            metrics = {
                "compression_ratio": flow_result.mean_rigid_ratio,
                "tpe_mode": tpe_result.dominant_mode,
                "is_condensate": is_condensate,
                "betti_1": betti_1,
                "final_population": final_pop,
                "signal": flow_result.signal.name,
            }
            wolfram_class, phase = classify_rule(metrics)

            return RuleAnalysis(
                rule_str=rule_str,
                b_set=b_str,
                s_set=s_str,
                x=x,
                y=y,
                compression_ratio=flow_result.mean_rigid_ratio,
                signal=flow_result.signal.name,
                toroidal=tpe_result.toroidal,
                poloidal=tpe_result.poloidal,
                emergence=tpe_result.emergence,
                tpe_mode=tpe_result.dominant_mode,
                is_condensate=is_condensate,
                equilibrium_density=eq_density,
                expansion_factor=expansion,
                betti_1=betti_1,
                final_population=final_pop,
                wolfram_class=wolfram_class,
                phase=phase,
            )

        except Exception as e:
            logging.warning(f"Failed to analyze {rule_str}: {e}")
            return None

    def generate_rules(
        self, mode: str, samples: int, b_range: tuple = None, s_range: tuple = None
    ) -> List[str]:
        """Generate rules to scan based on mode."""

        if mode == "full":
            # Systematic grid (sample from full space)
            rules = []
            for b in range(512):
                for s in range(512):
                    b_str = "".join(str(i) for i in range(9) if b & (1 << i))
                    s_str = "".join(str(i) for i in range(9) if s & (1 << i))
                    rules.append(f"B{b_str}/S{s_str}")
            random.shuffle(rules)
            return rules[:samples]

        elif mode == "quick":
            # Random sampling
            rules = []
            for _ in range(samples):
                # trunk-ignore(bandit/B311)
                b = random.randint(0, 511)
                # trunk-ignore(bandit/B311)
                s = random.randint(0, 511)
                b_str = "".join(str(i) for i in range(9) if b & (1 << i))
                s_str = "".join(str(i) for i in range(9) if s & (1 << i))
                rules.append(f"B{b_str}/S{s_str}")
            return rules

        elif mode == "region":
            # Targeted B/S region
            b_min, b_max = b_range or (0, 7)
            s_min, s_max = s_range or (0, 4)
            rules = []
            for b in range(512):
                b_str = "".join(str(i) for i in range(9) if b & (1 << i))
                b_nums = [int(c) for c in b_str] if b_str else []
                if not all(b_min <= n <= b_max for n in b_nums):
                    continue
                for s in range(512):
                    s_str = "".join(str(i) for i in range(9) if s & (1 << i))
                    s_nums = [int(c) for c in s_str] if s_str else []
                    if not all(s_min <= n <= s_max for n in s_nums):
                        continue
                    rules.append(f"B{b_str}/S{s_str}")
            random.shuffle(rules)
            return rules[:samples]

        elif mode == "condensate":
            # Focus on B0 rules (likely condensates)
            rules = []
            for b in range(512):
                if not (b & 1):  # B0 not set
                    continue
                for s in range(512):
                    b_str = "".join(str(i) for i in range(9) if b & (1 << i))
                    s_str = "".join(str(i) for i in range(9) if s & (1 << i))
                    rules.append(f"B{b_str}/S{s_str}")
            random.shuffle(rules)
            return rules[:samples]

        return []

    def scan(self, mode: str = "quick", samples: int = 200, **kwargs):
        """Run the atlas scan."""
        rules = self.generate_rules(mode, samples, **kwargs)

        console.print(
            f"[bold cyan]Probe 2D V4 - Scanning {len(rules)} rules[/bold cyan]"
        )
        console.print(f"Mode: {mode} | Output: {self.output_file}")

        class_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        phase_counts = {"particle": 0, "condensate": 0, "hybrid": 0, "n/a": 0}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Scanning...", total=len(rules))

            for i, rule in enumerate(rules):
                progress.update(task, description=f"[cyan]{rule}[/cyan]")

                result = self.analyze_rule(rule)
                if result:
                    self.results.append(result)
                    class_counts[result.wolfram_class] += 1
                    phase_counts[result.phase] += 1

                progress.advance(task)

                # Periodic save every 50 rules
                if (i + 1) % 50 == 0:
                    self.save()

        # Final save
        self.save()

        # Summary
        self._print_summary(class_counts, phase_counts)

    def save(self):
        """Save results to JSON."""
        data = [r.to_dict() for r in self.results]
        with open(self.output_file, "w") as f:
            json.dump(data, f, indent=2)

    def _print_summary(self, class_counts: dict, phase_counts: dict):
        """Print scan summary."""
        console.print("\n[bold green]═══ Scan Complete ═══[/bold green]")

        table = Table(title="Wolfram Class Distribution")
        table.add_column("Class", style="cyan")
        table.add_column("Count", style="magenta")
        table.add_column("Percent", style="yellow")

        total = sum(class_counts.values())
        for cls, count in sorted(class_counts.items()):
            pct = count / total * 100 if total > 0 else 0
            table.add_row(f"Class {cls}", str(count), f"{pct:.1f}%")

        console.print(table)

        # Phase table
        table2 = Table(title="Phase Distribution (Class 4 only)")
        table2.add_column("Phase", style="cyan")
        table2.add_column("Count", style="magenta")

        for phase, count in phase_counts.items():
            if phase != "n/a" and count > 0:
                table2.add_row(phase, str(count))

        console.print(table2)
        console.print(f"\n[dim]Results saved to: {self.output_file}[/dim]")


def main():
    parser = argparse.ArgumentParser(description="Probe 2D V4 - Modern Atlas Scanner")
    parser.add_argument(
        "--mode",
        choices=["full", "quick", "region", "condensate"],
        default="quick",
        help="Scanning mode",
    )
    parser.add_argument(
        "--samples", type=int, default=200, help="Number of rules to scan"
    )
    parser.add_argument(
        "--output", type=str, default="atlas_v4.json", help="Output file"
    )
    parser.add_argument(
        "--grid-size", type=int, default=48, help="Simulation grid size"
    )
    parser.add_argument("--steps", type=int, default=150, help="Simulation steps")

    args = parser.parse_args()

    probe = Probe2DV4(
        grid_size=args.grid_size,
        steps=args.steps,
        output_file=args.output,
    )

    probe.scan(mode=args.mode, samples=args.samples)


if __name__ == "__main__":
    main()
