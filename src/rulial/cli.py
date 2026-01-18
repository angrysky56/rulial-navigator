import time

import typer
from rich.console import Console
from rich.table import Table

from .compression.metrics import TelemetryAnalyzer
from .engine.eca import ECAEngine
from .navigator.classifier import RuleClassifier
from .navigator.gradient import GradientCalculator, ProbeResult
from .navigator.swarm import SwarmNavigator
from .server.rpc import start_server

app = typer.Typer()
console = Console()


@app.command()
def serve(port: int = 8000):
    """Start the RPC backend server."""
    start_server(port)


@app.command()
def probe(rule: int, steps: int = 500):
    """Analyze a single rule."""
    console.print(f"[bold cyan]Probing Rule {rule}...[/bold cyan]")

    # Simulate
    engine = ECAEngine(rule)
    st = engine.simulate(200, steps, "random")

    # V1 Analysis
    analyzer = TelemetryAnalyzer()
    tel = analyzer.analyze(st)
    w_class = RuleClassifier.classify(tel)

    # V2 Analysis
    # Superfluid Filter (Quimb)
    from .quantum.superfluid import SuperfluidFilter

    sf_filter = SuperfluidFilter()
    sf_data = sf_filter.analyze(st)

    # ZX Reducer (PyZX)
    # Extract graph first
    from .engine.spacetime import SpacetimeUtil
    from .quantum.zx_reducer import ZXReducer

    causal_graph = SpacetimeUtil.extract_causal_graph(st)
    zx_reducer = ZXReducer()
    zx_data = zx_reducer.analyze(causal_graph)

    # Display
    table = Table(title=f"Analysis of Rule {rule} (V1 + V2)")
    table.add_column("Metric", style="magenta")
    table.add_column("Value", style="green")

    # V1 Section
    table.add_row("Wolfram Class", str(w_class))
    table.add_row("Rigid Ratio", f"{tel.rigid_ratio_lzma:.4f}")
    table.add_row("Entropy", f"{tel.shannon_entropy:.4f}")
    table.add_row("Learning Slope", f"{tel.loss_derivative:.6f}")

    # V2 Section
    table.add_section()
    table.add_row("[bold]Quantum V2[/bold]", "")
    table.add_row("Superfluid Ent.", f"{sf_data.get('normalized_entropy', 0):.4f}")
    table.add_row("SF Class", str(sf_data.get("classification", "N/A")))
    table.add_row("ZX Reduction", f"{zx_data.get('reduction_ratio', 0):.4f}")
    table.add_row("Logical Core", str(zx_data.get("skeleton_structure", "N/A")))

    console.print(table)

    if w_class == 4:
        console.print("[bold gold1]GOLD FILAMENT DETECTED![/bold gold1]")
    elif w_class == 3:
        console.print("[bold red]Chaos detected.[/bold red]")
    else:
        console.print("[bold blue]Frozen/Periodic.[/bold blue]")


@app.command()
def navigate(start_rule: int = 110, steps: int = 20):
    """Start an autonomous navigation session."""
    current_rule = start_rule
    swarm = SwarmNavigator()
    gradient = GradientCalculator()

    console.print(
        f"[bold green]Starting Navigation Swarm at Rule {current_rule}[/bold green]"
    )

    for i in range(steps):
        console.print(f"\n[bold]Step {i+1}/{steps}: Center {current_rule}[/bold]")

        # 1. Spawn Swarm
        neighbors = swarm.hamming_neighbors(current_rule)
        probes = []

        # 2. Probe Neighbors
        with console.status("[bold green]Swarm Probing...[/bold green]"):
            for r in neighbors:
                # Run lightweight simulation
                engine = ECAEngine(r)
                st = engine.simulate(200, 300, "random")
                analyzer = TelemetryAnalyzer()
                tel = analyzer.analyze(st)

                # Determine interestingness
                score = gradient.compute_interestingness(tel)
                w_class = RuleClassifier.classify(tel)

                probes.append(ProbeResult(r, tel, w_class, score))

        # 3. Calculate Gradient
        best_rule, magnitude = gradient.calculate_gradient(current_rule, probes)

        # Display Swarm Status
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Rule")
        table.add_column("Class")
        table.add_column("Interest")
        table.add_column("Compression")

        for p in probes:
            style = "white"
            if p.rule == best_rule:
                style = "bold green"
            if p.wolfram_class == 4:
                style = "bold gold1"

            table.add_row(
                str(p.rule),
                str(p.wolfram_class),
                f"{p.interestingness:.4f}",
                f"{p.telemetry.rigid_ratio_lzma:.2f}",
                style=style,
            )

        console.print(table)

        if best_rule == current_rule:
            console.print("[yellow]Local optimum reached. Swarm staying put.[/yellow]")
        else:
            console.print(
                f"[cyan]Gradient found! Moving to Rule {best_rule} (Mag: {magnitude:.4f})[/cyan]"
            )
        if best_rule == current_rule:
            console.print("[yellow]Local optimum reached. Swarm staying put.[/yellow]")
        else:
            console.print(
                f"[cyan]Gradient found! Moving to Rule {best_rule} (Mag: {magnitude:.4f})[/cyan]"
            )
            current_rule = best_rule

        time.sleep(1)


@app.command()
def probe_2d(
    width: int = typer.Option(64, help="Grid width"),
    height: int = typer.Option(64, help="Grid height"),
    steps: int = typer.Option(100, help="Simulation steps per epoch"),
    seed: int = typer.Option(
        224,
        help="Initial Rule Code (Default: Game of Life 224/std is actually complex mapping, try simple ints)",
    ),
    epochs: int = typer.Option(1000, help="Max epochs to run"),
    window: int = typer.Option(
        12,
        help="Observer Window Size (Quantum Analysis). Warning: Complexity scales exponentially.",
    ),
):
    """
    Launch the Rulial Titans autonomous agent in 2D Rule Space.
    """
    # Import locally to avoid circular imports or heavy load
    from rulial.runners.probe_2d import RulialProbe2D

    typer.echo(f"Initializing Titans... Target: 2D Totalistic Space. Seed Rule: {seed}")
    runner = RulialProbe2D(
        width=width, height=height, steps=steps, seed_rule=seed, obs_window=window
    )
    runner.run_loop(max_epochs=epochs)


@app.command()
def pipeline(
    mode: str = typer.Option("analyze", help="Mode: explore, catalog, analyze, query"),
    rule: str = typer.Option("B3/S23", help="Rule to analyze"),
    steps: int = typer.Option(20, help="Exploration steps"),
    query: str = typer.Option("", help="Query string for query mode"),
):
    """
    Unified Ruliad Pipeline: Titans + Atlas + Mining + Query.
    """
    from rulial.pipeline import UnifiedPipeline

    pipe = UnifiedPipeline()

    if mode == "explore":
        console.print(
            f"[bold cyan]Starting Titans exploration from {rule}...[/bold cyan]"
        )
        results = pipe.explore(steps=steps, start_rule=rule)
        console.print(
            f"\n[green]Exploration complete. Analyzed {len(results)} rules.[/green]"
        )
        logic_capable = sum(1 for r in results if r.is_logic_capable)
        console.print(f"[gold1]Logic-capable rules found: {logic_capable}[/gold1]")

    elif mode == "catalog":
        console.print("[bold cyan]Cataloging Class 4 rules from atlas...[/bold cyan]")
        results = pipe.catalog_atlas()
        console.print(
            f"\n[green]Cataloging complete. Analyzed {len(results)} rules.[/green]"
        )

    elif mode == "query":
        if query:
            console.print(f"[bold cyan]Query: {query}[/bold cyan]")
            result = pipe.query(query)
            console.print(result)
        else:
            console.print(
                "[yellow]Usage: pipeline --mode query --query 'your question'[/yellow]"
            )

    else:  # analyze
        console.print(f"[bold cyan]Analyzing {rule}...[/bold cyan]")
        result = pipe.analyze_rule(rule)
        console.print(result.summary())


@app.command()
def entropy_flow(
    rule: str = typer.Option("B3/S23", help="Rule to analyze"),
):
    """
    Analyze compression flow for a rule (Maxwell's Demon for complexity).

    Uses bifurcated architecture:
    - Layer 1: Rigid (LZMA) for exact patterns
    - Layer 2: Neural for soft patterns

    Outputs: FRUSTRATION (chaos), BOREDOM (frozen), or CURIOSITY (complexity)
    """
    from rulial.compression.flow import CompressionFlowAnalyzer

    console.print(f"[bold cyan]Analyzing compression flow for {rule}...[/bold cyan]")
    analyzer = CompressionFlowAnalyzer()
    result = analyzer.analyze(rule)
    console.print(result.summary())


@app.command()
def tpe(
    rule: str = typer.Option("B3/S23", help="Rule to analyze"),
):
    """
    T-P+E Analysis: Toroidal-Poloidal Emergence.

    Measures expansion (T) vs contraction (P) dialectic.
    E = (T·P) × |T-P| is maximized at balanced dynamics.
    """
    from rulial.mapper.tpe import TPEAnalyzer

    console.print(f"[bold cyan]T-P+E analysis for {rule}...[/bold cyan]")
    analyzer = TPEAnalyzer()
    result = analyzer.analyze(rule)
    console.print(result.summary())


@app.command()
def oligons(
    rule: str = typer.Option("B3/S23", help="Rule to analyze"),
):
    """
    Count oligons (small stable structures).

    Oligons are the "dark matter scaffolding" of the Ruliad:
    - Still lifes (period 1)
    - Oscillators (period 2-4)
    """
    from rulial.mining.oligon import OligonCounter

    console.print(f"[bold cyan]Counting oligons for {rule}...[/bold cyan]")
    counter = OligonCounter()
    result = counter.count(rule)
    console.print(result.summary())


if __name__ == "__main__":
    app()
