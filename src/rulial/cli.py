import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def explore(
    db: str = typer.Option("data/atlas_full_v6_gpu.db", help="Path to Atlas DB"),
    steps: int = typer.Option(1000000, help="Number of steps to explore"),
    start_rule: str = typer.Option("B3/S23", help="Starting rule"),
):
    """
    Start the Discovery Engine (Titans Only).
    """
    from rulial.pipeline import UnifiedPipeline

    console.print(
        "[bold green]Initializing Unified Pipeline (Mode: Explorer)...[/bold green]"
    )
    pipe = UnifiedPipeline(db_path=db)

    console.print(f"[bold cyan]Bootstrapping Titans from {db}...[/bold cyan]")
    pipe.bootstrap_titans()

    console.print("[bold green]Starting Exploration Loop...[/bold green]")
    try:
        pipe.run_continuously(steps=steps, start_rule=start_rule)
    except KeyboardInterrupt:
        console.print("\n[yellow]Exploration paused.[/yellow]")
        if hasattr(pipe, "titans_path") and pipe.titans_path:
            pipe.titans.save(str(pipe.titans_path))


@app.command()
def science(
    db: str = typer.Option("data/atlas_full_v6_gpu.db", help="Path to Atlas DB"),
    steps: int = typer.Option(1000000, help="Number of steps to explore"),
    start_rule: str = typer.Option("B3/S23", help="Starting rule"),
):
    """
    Start the AIR Protocol (Advanced Scientific Mining).

    1. Titans Navigation
    2. Compression Compass
    3. Sheaf/Fractal Physics
    4. Active Mining (Particles, Colliders)
    """
    from rulial.pipeline import UnifiedPipeline

    console.print(
        "[bold green]Initializing Unified Pipeline (Mode: AIR Protocol)...[/bold green]"
    )
    pipe = UnifiedPipeline(db_path=db)

    # Ensure bootstrap
    pipe.bootstrap_titans()

    console.print("[bold purple]Starting Scientific Discovery Loop...[/bold purple]")
    console.print("   [dim]Targeting: Gliders, Vortex Knots, Logic Gates[/dim]")

    try:
        pipe.run_continuously(steps=steps, start_rule=start_rule)
    except KeyboardInterrupt:
        console.print("\n[yellow]Science paused.[/yellow]")
        if hasattr(pipe, "titans_path") and pipe.titans_path:
            pipe.titans.save(str(pipe.titans_path))


@app.command(name="goal-search")
def goal_search(
    goal_type: str = typer.Option(
        "goldilocks", help="Search type: goldilocks, condensate, particle"
    ),
    limit: int = typer.Option(20, help="Max results"),
    db: str = typer.Option("data/atlas_full_v6_gpu.db", help="Path to Atlas DB"),
):
    """
    Search the Atlas for rules matching specific goals.
    """
    from rulial.navigator.goal_search import GoalDirectedSearch

    searcher = GoalDirectedSearch(db_path=db)

    if goal_type == "goldilocks":
        results = searcher.find_goldilocks(limit)
    elif goal_type == "condensate":
        results = searcher.find_condensates(limit)
    elif goal_type == "particle":
        results = searcher.find_particles(limit)
    else:
        console.print(f"[red]Unknown goal type: {goal_type}[/red]")
        return

    console.print(
        f"[bold cyan]Found {len(results)} candidates for '{goal_type}':[/bold cyan]"
    )
    for r in results[:10]:
        console.print(
            f"  {r['rule_str']}: H={r['harmonic_overlap']:.3f}, Phase={r.get('phase', 'N/A')}"
        )


# Analysis Sub-Commands
analyze_app = typer.Typer(help="Analyze the mapped Ruliad.")
app.add_typer(analyze_app, name="analyze")


@analyze_app.command("stats")
def analyze_stats(
    db: str = typer.Option("data/atlas_full_v6_gpu.db", help="Path to Atlas DB")
):
    """Show global statistics of the mapped Ruliad."""
    from rulial.analytics.analyzer import RuliadAnalyzer

    analyzer = RuliadAnalyzer(db)
    stats = analyzer.get_global_stats()

    console.print("[bold]Ruliad Mapping Status[/bold]")
    console.print(f" Total Rules Scanned:  [cyan]{stats.total_scanned:,}[/cyan]")
    console.print(
        f" Goldilocks (H~0.5):   [yellow]{stats.goldilocks_count:,}[/yellow] ({(stats.goldilocks_count/stats.total_scanned)*100:.1f}%)"
    )
    console.print(
        f" Class 4 Candidates:   [magenta]{stats.class_4_candidates:,}[/magenta]"
    )
    console.print(f" Average Entropy:      {stats.avg_entropy:.4f}")


@analyze_app.command("goldilocks")
def analyze_goldilocks(
    db: str = typer.Option("data/atlas_full_v6_gpu.db", help="Path to Atlas DB"),
    limit: int = typer.Option(20, help="Number of rules to show"),
):
    """List out top 'Goldilocks' rules with high complexity."""
    from rich.table import Table

    from rulial.analytics.analyzer import RuliadAnalyzer

    analyzer = RuliadAnalyzer(db)
    rules = analyzer.find_goldilocks_rules(limit)

    table = Table(title=f"Top {limit} Goldilocks Candidates")
    table.add_column("Rule", style="cyan")
    table.add_column("Harmonic Overlap", justify="right")
    table.add_column("Fractal Dim", justify="right")
    table.add_column("Class", justify="right")

    for r in rules:
        table.add_row(
            r["rule_str"],
            f"{r['harmonic_overlap']:.4f}",
            f"{r['fractal_dimension']:.4f}",
            str(r["wolfram_class"]),
        )

    console.print(table)


@analyze_app.command("export")
def analyze_export(
    output: str = typer.Option("data/rule_space.nq.gz", help="Output path for N-Quads"),
    db: str = typer.Option("data/atlas_full_v6_gpu.db", help="Path to Atlas DB"),
):
    """Export the graph connectivity to N-Quads for visualization."""
    from rulial.analytics.analyzer import RuliadAnalyzer

    analyzer = RuliadAnalyzer(db)
    analyzer.export_cayley_nquads(output)
    console.print(f"[green]Exported graph to {output}[/green]")


@app.command()
def inspect(
    rule: str = typer.Argument(..., help="Rule string to analyze (e.g. B3/S23)"),
    db: str = typer.Option("data/atlas_full_v6_gpu.db", help="Path to Atlas DB"),
):
    """Analyze a single rule using the full V5 stack (Sheaf, Fractal, Condensate, Oligon)."""
    from rulial.engine.totalistic import Totalistic2DEngine
    from rulial.mapper.condensate import analyze_condensate
    from rulial.mapper.fractal import compute_fractal_dimension
    from rulial.mapper.sheaf_gpu import analyze_rule_gpu
    from rulial.mining.oligon import count_oligons

    console.print(f"[bold cyan]Analyzing {rule} with FULL PHYSICS SUITE...[/bold cyan]")

    # 1. Physics & Sheaf
    try:
        console.print("\n[bold]1. Topological Analysis (Sheaf)[/bold]")
        sheaf_res = analyze_rule_gpu(rule, grid_size=48, steps=100, device="cuda")

        console.print(f" Harmonic Overlap: {sheaf_res.harmonic_overlap:.4f}")
        console.print(f" Monodromy Index:  {sheaf_res.monodromy_index:.4f}")
        console.print(f" Spectral Gap:     {sheaf_res.spectral_gap:.4f}")

        if 0.3 <= sheaf_res.harmonic_overlap <= 0.6:
            console.print(
                "[bold gold1]🌟 GOLDILOCKS CANDIDATE (Topologically Complex)[/bold gold1]"
            )

    except Exception as e:
        console.print(f"[red]Sheaf analysis failed: {e}[/red]")

    # 2. Fractal
    try:
        engine = Totalistic2DEngine(rule)
        h = engine.simulate(48, 48, 100, "random")
        dim = compute_fractal_dimension(h[-1])
        console.print(f" Fractal Dim:      {dim:.4f}")
    except Exception as e:
        console.print(f"[red]Fractal analysis failed: {e}[/red]")

    # 3. Vacuum Condensate (Cosmology)
    try:
        console.print("\n[bold]2. Cosmological Analysis (Vacuum)[/bold]")
        condensate = analyze_condensate(rule)
        if condensate.is_condensate:
            console.print(" Phase:            [cyan]🌊 VACUUM CONDENSATE[/cyan]")
            console.print(f" Equilibrium:      {condensate.equilibrium_density:.1%}")
            console.print(f" Expansion Factor: {condensate.expansion_factor:.0f}x")
        else:
            console.print(" Phase:            [green]⚛️ PARTICLE-BASED[/green]")
    except Exception as e:
        console.print(f"[red]Condensate analysis failed: {e}[/red]")

    # 4. Oligons (Particle Physics)
    try:
        console.print("\n[bold]3. Particle Analysis (Oligons)[/bold]")
        oligons = count_oligons(rule)
        console.print(f" Total Oligons:    {oligons.total_oligons}")
        console.print(f" Still Lifes (P1): {oligons.still_lifes}")
        console.print(f" Oscillators (P2): {oligons.oscillators_p2}")
        console.print(f" Oscillators (P3+):{oligons.oscillators_p3_plus}")
        console.print(f" Unique Species:   {oligons.unique_patterns}")

        if oligons.unique_patterns > 5 and oligons.oscillators_p3_plus > 0:
            console.print("[bold gold1]🧪 RICH PARTICLE ZOO DETECTED[/bold gold1]")

    except Exception as e:
        console.print(f"[red]Oligon analysis failed: {e}[/red]")


@app.command(name="tm-explore")
def tm_explore(
    rule_code: int = typer.Option(..., help="Wolfram code for the TM (e.g. 2506)"),
    steps: int = typer.Option(10, help="Steps to evolve"),
    initial_tape: str = typer.Option("0", help="Initial tape state (e.g. '010')"),
):
    """Explore the Multiway Graph of a Non-Deterministic Turing Machine."""
    from rulial.engine.turing import MultiwayTuringSystem, TMState, TuringMachineRule

    # 1. Setup Rule
    rule = TuringMachineRule.from_wolfram_code(rule_code)
    system = MultiwayTuringSystem(rule)

    # 2. Setup Initial State
    # Parse generic tape string "010" -> tuple, head at 0?
    # Let's assume head at index 0.
    tape_vals = tuple(int(c) for c in initial_tape)
    initial_state = TMState(tape=tape_vals, head_pos=0, state=0)

    # 3. Evolve
    history = system.evolve(initial_state, steps)

    # 4. Display
    console.print(f"[bold]Multiway Evolution of TM Rule {rule_code}[/bold]")
    for t, states in history.items():
        console.print(f"Step {t}: {len(states)} states")
        if len(states) < 10:
            for s in states:
                # Visualization logic
                tape_str = ""
                if not s.tape:
                    # Empty tape means all zeros. Show head on 0.
                    tape_str = "[bold red]0[/bold red]"
                else:
                    for i, cell in enumerate(s.tape):
                        if i == s.head_pos:
                            tape_str += f"[bold red]{cell}[/bold red]"
                        else:
                            tape_str += str(cell)
                console.print(f"  State {s.state}: {tape_str}")
        else:
            console.print("  (Too many to list)")


@app.command(name="tm-mine")
def tm_mine(
    input_tape: str = typer.Option(..., help="Input string (e.g. '010')"),
    target_tape: str = typer.Option(..., help="Target string (e.g. '01010')"),
    max_steps: int = typer.Option(10, help="Max steps to search"),
    rule_limit: int = typer.Option(
        100, help="Number of rules to check (starts from 0)"
    ),
):
    """
    Mine for a rule that transforms Input -> Target.
    Example: Find a doubler (01 -> 011).
    """
    from rulial.engine.turing import FunctionMiner

    # Parse inputs
    i_tuple = tuple(int(c) for c in input_tape)
    t_tuple = tuple(int(c) for c in target_tape)

    console.print(
        f"[bold cyan]Mining for Function:[/bold cyan] {input_tape} -> {target_tape}"
    )
    console.print(f"Scanning first {rule_limit} rules...")

    miner = FunctionMiner()
    solutions = miner.mine(
        i_tuple, t_tuple, max_steps=max_steps, rule_range=range(rule_limit)
    )

    if solutions:
        console.print(f"[bold green]FOUND {len(solutions)} SOLUTIONS![/bold green]")
        for sol in solutions:
            console.print(
                f"Rule [bold]{sol['rule']}[/bold] found in {sol['steps']} steps."
            )
            # Show path summary?
    else:
        console.print("[yellow]No solutions found in search range.[/yellow]")


@app.command()
def query(q: str):
    """Natural language query of the Ruliad."""
    console.print(f"Querying: {q}")


if __name__ == "__main__":
    app()
