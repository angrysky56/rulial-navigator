import json
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

def analyze_titans():
    console = Console()
    console.print("[bold blue]Rulial Titans: Mission Analysis[/bold blue]")
    
    try:
        with open("titans_history.json", "r") as f:
            history = json.load(f)
    except FileNotFoundError:
        console.print("[red]Error: titans_history.json not found. Run 'probe-2d' first.[/red]")
        return

    total_epochs = len(history)
    console.print(f"Loaded [bold]{total_epochs}[/bold] epochs of exploration data.")
    
    # Metrics extraction
    entropies = [h['entropy'] for h in history]
    surprises = [h['surprise'] for h in history]
    
    # 1. Finding 'The Titans' (Class 4 Candidates)
    # Heuristic: Entropy in [0.6, 2.5] (Neither Ice nor Fire)
    # Rule 110 is ~0.94. Game of Life Glider ~1.0. 
    # Let's look for this "Sweet Spot".
    
    candidates = []
    for h in history:
        ent = h['entropy']
        if 0.6 < ent < 2.5:
           candidates.append(h)
           
    # Sort candidates by Surprise (Novelty)
    # High surprise means the Neural Net didn't expect this complexity.
    top_novel = sorted(candidates, key=lambda x: x['surprise'], reverse=True)[:10]
    
    table = Table(title="💎 Discovered Class 4 Candidates (Ranked by Surprise)")
    table.add_column("Rule ID", style="cyan")
    table.add_column("Entropy", style="magenta")
    table.add_column("Surprise", style="yellow")
    table.add_column("Bits (B/S)", style="green")
    
    for c in top_novel:
        # Decode rule bits
        bits = c['rule_bits']
        b_bits = bits[:9]
        s_bits = bits[9:]
        b_str = "".join([str(i) for i, b in enumerate(b_bits) if b])
        s_str = "".join([str(i) for i, b in enumerate(s_bits) if b])
        bs_code = f"B{b_str}/S{s_str}"
        
        table.add_row(
            str(c['rule']),
            f"{c['entropy']:.4f}",
            f"{c['surprise']:.4f}",
            bs_code
        )
        
    console.print(table)
    
    # 2. Global Stats
    avg_ent = np.mean(entropies)
    max_ent = np.max(entropies)
    
    msg = f"""
    [bold]Global Statistics:[/bold]
    Average Entropy: {avg_ent:.4f}
    Max Entropy:     {max_ent:.4f} (Volume Law / Chaos)
    Candidates Found: {len(candidates)} / {total_epochs}
    """
    console.print(Panel(msg, title="Mission Report", border_style="white"))

if __name__ == "__main__":
    analyze_titans()
