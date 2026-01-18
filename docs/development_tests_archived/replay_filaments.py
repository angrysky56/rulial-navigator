import json
import time

import numpy as np
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel

from rulial.engine.totalistic import Totalistic2DEngine


def int_to_bits(n: int, num_bits: int) -> np.ndarray:
    bin_str = format(n, f"0{num_bits}b")
    return np.array([int(x) for x in bin_str], dtype=np.float32)


def replay_filaments():
    console = Console()
    console.print("[bold cyan]Loading Golden Filaments...[/bold cyan]")

    try:
        with open("golden_filaments.json", "r") as f:
            filaments = json.load(f)
    except FileNotFoundError:
        console.print("[red]No golden_filaments.json found![/red]")
        return

    if not filaments:
        console.print("[yellow]Filament file is empty.[/yellow]")
        return

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="universe", ratio=1),
        Layout(name="footer", size=3),
    )

    with Live(layout, refresh_per_second=10, screen=True):
        for idx, item in enumerate(filaments):
            rule_int = item["rule"]
            entropy = item["entropy"]

            # Decode Rule Key
            # We need to reconstruct the B/S string from the int
            # Same logic as probe_2d
            rule_bits = int_to_bits(rule_int, 18)
            b_indices = [i for i, b in enumerate(rule_bits[0:9]) if b == 1]
            s_indices = [i for i, b in enumerate(rule_bits[9:18]) if b == 1]
            b_str = "".join(map(str, b_indices))
            s_str = "".join(map(str, s_indices))
            rule_str = f"B{b_str}/S{s_str}"

            # Run a short demo for each
            engine = Totalistic2DEngine(rule_str)
            # Use a slightly larger grid for the gallery
            h, w = 40, 80
            history = engine.simulate(h, w, 60, "random")  # 60 frames

            for grid in history:
                # Viz
                viz_str = ""
                for r in range(h):
                    for c in range(w):
                        viz_str += "█" if grid[r, c] else " "
                    viz_str += "\n"

                layout["header"].update(
                    Panel(
                        f"FILAMENT {idx+1}/{len(filaments)} | Rule: {rule_int} ({rule_str}) | Entropy: {entropy:.4f}",
                        style="bold white on gold1",
                    )
                )
                layout["universe"].update(
                    Panel(viz_str, title="Replaying...", style="green")
                )
                layout["footer"].update(
                    Panel(
                        "Displaying captured computationally active universe.",
                        style="dim",
                    )
                )

                time.sleep(0.05)

            # Pause between rules
            time.sleep(1.0)


if __name__ == "__main__":
    replay_filaments()
