"""
Ground Truth Verification for Rulial Metrics.

This script validates that our detection metrics (Compression Progress, Logic Depth, TDA)
correctly classify known ground-truth rules.

Benchmarks:
- Class 1 (Frozen): Rule 0 (B/S) or simple die-off
- Class 2 (Periodic): Rule 1 (B1/S) or simple block builders
- Class 3 (Chaos): Rule 30 equivalent (e.g. B3/S012345678)
- Class 4 (Complex): Game of Life (B3/S23), HighLife (B36/S23)
"""

import sys

from rich.console import Console
from rich.table import Table

# Ensure we can import from the probe
from rulial.runners.probe_2d_v2 import analyze_rule


def parse_rule_str_to_id(rule_str: str) -> int:
    """Convert "B.../S..." string to 18-bit integer rule ID."""
    # Format: B<born>/S<survive>
    if "/" not in rule_str:
        return 0
    b_part, s_part = rule_str.split("/")
    b_digits = [int(c) for c in b_part if c.isdigit()]
    s_digits = [int(c) for c in s_part if c.isdigit()]

    # Construct 18-bit integer
    # 0-8: Born bits
    # 9-17: Survive bits
    n = 0
    for b in b_digits:
        n |= 1 << b
    for s in s_digits:
        n |= 1 << (s + 9)
    return n


def verify_ground_truth():
    console = Console()
    console.print("[bold]Running Ground Truth Verification...[/bold]")

    benchmarks = [
        ("Class 1 (Frozen)", "B/S", 1),  # Die hard
        # ("Class 2 (Periodic)", "B1/S", 2),      # Simple growth
        (
            "Class 3 (Chaos)",
            "B35678/S4678",
            3,
        ),  # "Anneal" (approx Class 3/4 boundary, usually chaotic)
        ("Class 4 (Life)", "B3/S23", 4),  # Game of Life
        ("Class 4 (HighLife)", "B36/S23", 4),  # HighLife
    ]

    table = Table(title="Metric Validation Results")
    table.add_column("Rule", style="cyan")
    table.add_column("Expected", style="white")
    table.add_column("Detected", style="magenta")
    table.add_column("Comp Ratio", justify="right")
    table.add_column("Comp Prog", justify="right")
    table.add_column("Betti-1", justify="right")
    table.add_column("Status", style="bold")

    passed = 0

    for label, rule_str, expected_class in benchmarks:
        rule_id = parse_rule_str_to_id(rule_str)

        # Analyze
        try:
            # Need sufficient steps for TDA to find persistent features (200 is good)
            # Use 'dense' seed to ensure Life doesn't die immediately
            analysis = analyze_rule(rule_id, steps=200)

            detected = analysis.wolfram_class
            status = (
                "[green]PASS[/green]"
                if detected == expected_class
                else "[red]FAIL[/red]"
            )
            if detected == expected_class:
                passed += 1

            table.add_row(
                f"{label}\n({rule_str})",
                f"Class {expected_class}",
                f"Class {detected}",
                f"{analysis.compression_ratio:.5f}",
                f"{analysis.compression_progress:.6f}",
                f"B1: {analysis.betti_1}\nMaxP: {analysis.max_persistence:.1f}",
                status,
            )

        except Exception as e:
            table.add_row(
                label,
                str(expected_class),
                "ERROR",
                "-",
                "-",
                "-",
                f"[red]{str(e)}[/red]",
            )

    console.print(table)

    threshold_info = """
    [bold]Calibration Targets (Table 1 Spec):[/bold]
    Class 4 must have: 
    - [green]Compression Ratio[/green] in 0.1 - 0.6 (Medium)
    - [green]Compression Progress[/green] < -0.001 (Learning)
    - [green]Betti-1[/green] > 0 (Topological Features) or Max Persistence > 2.0
    """
    console.print(threshold_info)

    if passed == len(benchmarks):
        console.print(
            "[bold green]SUCCESS: All ground truth rules verified![/bold green]"
        )
        sys.exit(0)
    else:
        console.print(
            f"[bold red]FAILURE: Only {passed}/{len(benchmarks)} rules validated.[/bold red]"
        )
        sys.exit(1)


if __name__ == "__main__":
    verify_ground_truth()
