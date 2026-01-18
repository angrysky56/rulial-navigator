"""
Generate Visualizations from Atlas Data

Creates figures for the whitepaper:
1. Phase diagram (equilibrium density vs B/S parameters)
2. T-P+E mode distribution
3. S-sum correlation plot
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not installed. Install with: uv pip install matplotlib")


def load_atlas(filename: str) -> list:
    """Load atlas data."""
    path = Path(filename)
    if not path.exists():
        print(f"Error: {filename} not found")
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def plot_equilibrium_by_s_count(data: list, output: str = "fig_equilibrium_by_s_count.png"):
    """
    Figure: Equilibrium Density by S-Count
    Bar chart showing how S-count affects vacuum energy.
    """
    if not HAS_MATPLOTLIB:
        return
    
    # Group by S-count
    by_count = defaultdict(list)
    for r in data:
        s_count = len(r['s_set']) if r['s_set'] else 0
        by_count[s_count].append(r['equilibrium_density'])
    
    counts = sorted(by_count.keys())
    means = [np.mean(by_count[c]) for c in counts]
    stds = [np.std(by_count[c]) for c in counts]
    ns = [len(by_count[c]) for c in counts]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(counts, means, yerr=stds, capsize=5, color='steelblue', alpha=0.8)
    
    # Add count labels
    for bar, n in zip(bars, ns, strict=True):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
                f'n={n}', ha='center', va='bottom', fontsize=9)
    
    ax.set_xlabel('S-count (number of survival conditions)', fontsize=12)
    ax.set_ylabel('Mean Equilibrium Density', fontsize=12)
    ax.set_title('Vacuum Energy Increases with Survival Conditions', fontsize=14)
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))
    
    plt.tight_layout()
    plt.savefig(output, dpi=150)
    print(f"Saved: {output}")
    plt.close()


def plot_s_sum_correlation(data: list, output: str = "fig_s_sum_correlation.png"):
    """
    Figure: S-Sum vs Equilibrium Density Scatter
    Shows the r=0.621 correlation.
    """
    if not HAS_MATPLOTLIB:
        return
    
    s_sums = []
    eq_densities = []
    
    for r in data:
        s_set = r['s_set']
        s_digits = [int(c) for c in s_set] if s_set else []
        s_sum = sum(s_digits)
        s_sums.append(s_sum)
        eq_densities.append(r['equilibrium_density'])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(s_sums, eq_densities, alpha=0.6, s=50, c='steelblue')
    
    # Regression line
    z = np.polyfit(s_sums, eq_densities, 1)
    p = np.poly1d(z)
    x_line = np.linspace(min(s_sums), max(s_sums), 100)
    ax.plot(x_line, p(x_line), 'r-', linewidth=2, label=f'r = {np.corrcoef(s_sums, eq_densities)[0,1]:.3f}')
    
    ax.set_xlabel('S-sum (sum of survival condition digits)', fontsize=12)
    ax.set_ylabel('Equilibrium Density', fontsize=12)
    ax.set_title('S-Sum Predicts Vacuum Energy', fontsize=14)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))
    ax.legend(fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output, dpi=150)
    print(f"Saved: {output}")
    plt.close()


def plot_tpe_modes(data: list, output: str = "fig_tpe_modes.png"):
    """
    Figure: T-P+E Mode Distribution
    Pie chart showing balanced vs P-dominant.
    """
    if not HAS_MATPLOTLIB:
        return
    
    from collections import Counter
    modes = Counter(r['tpe_mode'] for r in data)
    
    labels = list(modes.keys())
    sizes = list(modes.values())
    colors = {'balanced': 'steelblue', 'P-dominant': 'coral', 'T-dominant': 'gold', 'dead': 'gray'}
    c = [colors.get(label, 'gray') for label in labels]
    
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                       colors=c, startangle=90, textprops={'fontsize': 12})
    ax.set_title('T-P+E Mode Distribution in Condensate Rules', fontsize=14)
    
    plt.tight_layout()
    plt.savefig(output, dpi=150)
    print(f"Saved: {output}")
    plt.close()


def plot_phase_comparison(output: str = "fig_phase_comparison.png"):
    """
    Figure: Particle vs Condensate Phase Comparison
    Side-by-side comparison of key metrics.
    """
    if not HAS_MATPLOTLIB:
        return
    
    # Data from analysis
    metrics = ['Single Cell\nExpansion', 'Equilibrium\nDensity', 'Oligon\nCount']
    particle = [0, 0.05, 36]  # B3/S23
    condensate = [220, 0.25, 0]  # B078/S012478
    
    x = np.arange(len(metrics))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, particle, width, label='B3/S23 (Particle)', color='steelblue')
    bars2 = ax.bar(x + width/2, condensate, width, label='B078/S012478 (Condensate)', color='coral')
    
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title('Particle vs Condensate Phase Comparison', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=11)
    ax.legend(fontsize=11)
    
    # Add value labels
    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
                f'{bar.get_height():.0f}' if bar.get_height() >= 1 else f'{bar.get_height():.0%}',
                ha='center', va='bottom', fontsize=10)
    for bar in bars2:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                f'{bar.get_height():.0f}' if bar.get_height() >= 1 else f'{bar.get_height():.0%}',
                ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output, dpi=150)
    print(f"Saved: {output}")
    plt.close()


def plot_goldilocks_zone(output: str = "fig_goldilocks_zone.png"):
    """
    Figure: The Goldilocks Zone
    Scatter plot showing harmonic overlap vs monodromy, highlighting
    the computational zone (H = 0.3-0.6) where gliders exist.
    """
    if not HAS_MATPLOTLIB:
        return
    
    from rulial.mapper.sheaf import SheafAnalyzer
    
    # Key rules to analyze
    rules = [
        ("B3/S23", "Life"),
        ("B36/S23", "HighLife"),
        ("B6/S123467", "Goldilocks-P"),
        ("B0467/S0568", "Goldilocks-C"),
        ("B268/S0367", "Goldilocks-P2"),
        ("B078/S012478", "Condensate"),
        ("B01/S23", "Active-C"),
        ("B0/S8", "Minimal"),
    ]
    
    print("Computing sheaf metrics for Goldilocks plot...")
    analyzer = SheafAnalyzer(grid_size=24, steps=40)
    
    h_values = []
    mono_values = []
    names = []
    is_goldilocks = []
    
    for rule, name in rules:
        try:
            result = analyzer.analyze(rule)
            h_values.append(result.harmonic_overlap)
            mono_values.append(result.monodromy_index)
            names.append(name)
            is_goldilocks.append(0.3 < result.harmonic_overlap < 0.6)
        except Exception as e:
            print(f"  Skipping {rule}: {e}")
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot Goldilocks zone background
    ax.axhspan(-1.5, 1.5, xmin=0, xmax=1, alpha=0.1, color='gray')
    ax.axvspan(0.3, 0.6, alpha=0.2, color='gold', label='Goldilocks Zone')
    
    # Scatter points
    colors = ['gold' if g else ('coral' if m > 0 else 'steelblue') 
              for g, m in zip(is_goldilocks, mono_values, strict=True)]
    sizes = [200 if g else 100 for g in is_goldilocks]
    
    ax.scatter(h_values, mono_values, c=colors, s=sizes, edgecolors='black', linewidths=1.5, zorder=5)
    
    # Labels
    for h, m, name in zip(h_values, mono_values, names, strict=True):
        offset = 0.02 if h < 0.5 else -0.02
        ax.annotate(name, (h, m), textcoords="offset points", 
                    xytext=(10, 5), fontsize=10, fontweight='bold' if 0.3 < h < 0.6 else 'normal')
    
    # Axis labels
    ax.set_xlabel('Harmonic Overlap (H)', fontsize=14)
    ax.set_ylabel('Monodromy (Φ)', fontsize=14)
    ax.set_title('The Goldilocks Zone: Computation Emerges at H = 0.3-0.6', fontsize=16)
    
    # Grid and limits
    ax.set_xlim(0, 1)
    ax.set_ylim(-1.2, 1.2)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(y=0.5, color='gray', linestyle=':', alpha=0.3)
    ax.axhline(y=-0.5, color='gray', linestyle=':', alpha=0.3)
    ax.grid(True, alpha=0.3)
    
    # Phase annotations
    ax.text(0.95, 1.0, 'Resonant\n(Condensate)', ha='right', va='top', fontsize=11, color='coral')
    ax.text(0.95, -1.0, 'Tense\n(Particle)', ha='right', va='bottom', fontsize=11, color='steelblue')
    ax.text(0.45, -1.15, '← GOLDILOCKS →', ha='center', fontsize=12, fontweight='bold', color='goldenrod')
    
    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='gold', markersize=12, label='Goldilocks (Gliders)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='coral', markersize=10, label='Resonant'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='steelblue', markersize=10, label='Tense'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11)
    
    plt.tight_layout()
    plt.savefig(output, dpi=150)
    print(f"Saved: {output}")
    plt.close()


def plot_monodromy_histogram(output: str = "fig_monodromy_histogram.png"):
    """
    Figure: Monodromy Distribution
    Shows clear separation between condensate (+1) and particle (-1) phases.
    """
    if not HAS_MATPLOTLIB:
        return
    
    from rulial.mapper.sheaf import SheafAnalyzer
    import random
    
    print("Computing monodromy for histogram...")
    analyzer = SheafAnalyzer(grid_size=20, steps=30)
    
    monos = []
    for i in range(30):
        # Generate random rule
        b_digits = ''.join(str(d) for d in range(9) if random.random() < 0.4)
        s_digits = ''.join(str(d) for d in range(9) if random.random() < 0.5)
        if not b_digits:
            b_digits = str(random.randint(0, 8))
        rule = f"B{b_digits}/S{s_digits}"
        
        try:
            result = analyzer.analyze(rule)
            monos.append(result.monodromy_index)
        except Exception:
            pass
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(monos, bins=20, range=(-1.2, 1.2), color='steelblue', edgecolor='black', alpha=0.7)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=2)
    ax.axvline(x=0.5, color='coral', linestyle=':', linewidth=2, label='Condensate threshold')
    ax.axvline(x=-0.5, color='blue', linestyle=':', linewidth=2, label='Particle threshold')
    
    ax.set_xlabel('Monodromy (Φ)', fontsize=14)
    ax.set_ylabel('Count', fontsize=14)
    ax.set_title('Monodromy Distribution: Phase Separation', fontsize=16)
    ax.legend(fontsize=11)
    
    plt.tight_layout()
    plt.savefig(output, dpi=150)
    print(f"Saved: {output}")
    plt.close()


def generate_all(atlas_file: str = "atlas_v4_condensate.json"):
    """Generate all figures."""
    print("═══ GENERATING VISUALIZATIONS ═══\n")
    
    if not HAS_MATPLOTLIB:
        print("Error: matplotlib required. Install with: uv pip install matplotlib")
        return
    
    data = load_atlas(atlas_file)
    
    # Original plots
    plot_equilibrium_by_s_count(data)
    plot_s_sum_correlation(data)
    plot_tpe_modes(data)
    plot_phase_comparison()
    
    # New Goldilocks plots
    plot_goldilocks_zone()
    plot_monodromy_histogram()
    
    print("\nAll figures generated!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_all(sys.argv[1])
    else:
        generate_all()
