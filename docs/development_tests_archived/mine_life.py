"""
Validation script for The Miner.
Attempts to mine the 'Glider' from simple Game of Life soup.
"""

import sys

from rich.console import Console

from rulial.mining.extractor import ParticleMiner


def mine_life():
    console = Console()
    rule = "B3/S23"
    console.print(f"[bold]Mining {rule} (Game of Life)...[/bold]")

    miner = ParticleMiner(rule)
    # Mine 100 soups
    # Low density helps find gliders (less chaos)
    particles = miner.mine(attempts=100, steps=1000, density=0.1)

    console.print(f"Found {len(particles)} unique particles.")

    glider_found = False

    for p in particles:
        console.print(f"- [cyan]{p.name}[/cyan] (Size: {p.pattern.shape})")
        if "Spaceship" in p.name or "Glider" in p.name:
            glider_found = True
            console.print(
                "  [bold green]>>> GLIDER/SPACESHIP DETECTED! <<<[/bold green]"
            )

    if glider_found:
        console.print(
            "[bold green]SUCCESS: Extracted usable physics (movement)![/bold green]"
        )
    else:
        console.print(
            "[bold red]FAILURE: No spaceships found. Try increasing attempts?[/bold red]"
        )
        sys.exit(1)


if __name__ == "__main__":
    mine_life()
