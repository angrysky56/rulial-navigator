"""
Vacuum Condensate Phases - Analysis Scripts

This module provides scripts to replicate the results from:
"Vacuum Condensate Phases in the Ruliad: A Classification of Complex Rules by Membrane Structure"

Usage:
    # Run all analyses
    uv run python -m scripts.analysis

    # Individual analyses
    uv run python -m scripts.analysis condensate_summary
    uv run python -m scripts.analysis control_test
    uv run python -m scripts.analysis s_correlation
    uv run python -m scripts.analysis tpe_analysis
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


def load_atlas(filename: str = "atlas_v4_condensate.json") -> list:
    """Load atlas data from JSON file."""
    path = Path(filename)
    if not path.exists():
        print(f"Error: {filename} not found. Run the atlas scan first.")
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def condensate_summary():
    """
    Section 3.1: B0 Rules Are Universally Condensate
    
    Summarizes the condensate scan results.
    """
    print("═══ CONDENSATE SCAN SUMMARY ═══")
    print("Section 3.1: B0 Rules Are Universally Condensate\n")
    
    data = load_atlas("atlas_v4_condensate.json")
    
    print(f"Total rules analyzed: {len(data)}")
    
    # Count by class
    classes = Counter(r['wolfram_class'] for r in data)
    print(f"\nWolfram Classes: {dict(sorted(classes.items()))}")
    
    # Count by phase
    phases = Counter(r['phase'] for r in data)
    print(f"Phases: {dict(phases)}")
    
    # Condensate stats
    condensates = [r for r in data if r['is_condensate']]
    print(f"\nCondensates: {len(condensates)}/{len(data)} ({100*len(condensates)/len(data):.1f}%)")
    
    if condensates:
        eq_densities = [r['equilibrium_density'] for r in condensates]
        print(f"Equilibrium density range: {min(eq_densities):.1%} - {max(eq_densities):.1%}")
        
        expansions = [r['expansion_factor'] for r in condensates]
        print(f"Expansion factor range: {min(expansions):.0f} - {max(expansions):.0f}")


def control_test():
    """
    Section 3.6: Control Test - Non-B0 Rules
    
    Verifies that non-B0 rules are particle-phase.
    """
    print("═══ CONTROL TEST: NON-B0 RULES ═══")
    print("Section 3.6: Non-B0 Rules Are Particle-Phase\n")
    
    from rulial.mapper.condensate import VacuumCondensateAnalyzer
    
    test_rules = [
        ('B3/S23', 'Game of Life'),
        ('B36/S23', 'HighLife'),
        ('B2/S', 'Seeds'),
        ('B1/S1', 'Gnarl'),
        ('B3/S12', 'Maze'),
        ('B34/S34', '34 Life'),
        ('B35678/S5678', 'Diamoeba'),
        ('B378/S235678', 'Day & Night'),
        ('B2345/S45678', 'Coral'),
        ('B4678/S35678', 'Anneal'),
    ]
    
    analyzer = VacuumCondensateAnalyzer(grid_size=32, steps=80)
    
    condensates = 0
    particles = 0
    
    for rule, name in test_rules:
        result = analyzer.analyze(rule)
        phase = '🌊 CONDENSATE' if result.is_condensate else '⚛️ PARTICLE'
        if result.is_condensate:
            condensates += 1
        else:
            particles += 1
        print(f'{rule:20s} ({name:15s}) {phase} eq={result.equilibrium_density:.1%}')
    
    print('\n═══ SUMMARY ═══')
    print(f'Particles: {particles}/{len(test_rules)} ({100*particles/len(test_rules):.0f}%)')
    print(f'Condensates: {condensates}/{len(test_rules)} ({100*condensates/len(test_rules):.0f}%)')
    
    if particles == len(test_rules):
        print('\n✅ HYPOTHESIS CONFIRMED: Non-B0 rules are particle-phase')
    else:
        print('\n❌ HYPOTHESIS NOT FULLY CONFIRMED')


def s_correlation():
    """
    Section 3.7: S-Parameter Correlation with Vacuum Energy
    
    Analyzes how S-set parameters predict equilibrium density.
    """
    print("═══ S-PARAMETER CORRELATION ANALYSIS ═══")
    print("Section 3.7: S-Set Predicts Vacuum Energy\n")
    
    data = load_atlas("atlas_v4_condensate.json")
    
    records = []
    for r in data:
        s_set = r['s_set']
        s_digits = [int(c) for c in s_set] if s_set else []
        s_count = len(s_digits)
        s_sum = sum(s_digits) if s_digits else 0
        s_mean = np.mean(s_digits) if s_digits else 0
        
        records.append({
            'rule': r['rule_str'],
            'eq_density': r['equilibrium_density'],
            's_count': s_count,
            's_sum': s_sum,
            's_mean': s_mean,
        })
    
    eq_densities = [r['eq_density'] for r in records]
    s_counts = [r['s_count'] for r in records]
    s_sums = [r['s_sum'] for r in records]
    s_means = [r['s_mean'] for r in records]
    
    print("CORRELATIONS:")
    print(f'  S-count vs eq_density: r = {np.corrcoef(s_counts, eq_densities)[0,1]:.3f}')
    print(f'  S-sum vs eq_density:   r = {np.corrcoef(s_sums, eq_densities)[0,1]:.3f} ← STRONGEST')
    print(f'  S-mean vs eq_density:  r = {np.corrcoef(s_means, eq_densities)[0,1]:.3f}')
    
    # Group by S-count
    print('\nEQUILIBRIUM DENSITY BY S-COUNT:')
    by_count = defaultdict(list)
    for r in records:
        by_count[r['s_count']].append(r['eq_density'])
    
    for count in sorted(by_count.keys()):
        densities = by_count[count]
        print(f'  S-count={count}: mean={np.mean(densities):.1%} (n={len(densities)})')
    
    # Extremes
    print('\nEXTREMES:')
    sorted_records = sorted(records, key=lambda x: x['eq_density'])
    print('Lowest density:')
    for r in sorted_records[:3]:
        print(f"  {r['rule']:25s} S-sum={r['s_sum']:2d} eq={r['eq_density']:.1%}")
    print('Highest density:')
    for r in sorted_records[-3:]:
        print(f"  {r['rule']:25s} S-sum={r['s_sum']:2d} eq={r['eq_density']:.1%}")


def tpe_analysis():
    """
    Section 3.3: T-P+E Dynamics Analysis
    
    Analyzes toroidal-poloidal dynamics of condensate rules.
    """
    print("═══ T-P+E DYNAMICS ANALYSIS ═══")
    print("Section 3.3: Toroidal-Poloidal Dynamics\n")
    
    data = load_atlas("atlas_v4_condensate.json")
    
    # T-P+E modes
    tpe_modes = Counter(r['tpe_mode'] for r in data)
    print("T-P+E MODE DISTRIBUTION:")
    for mode, count in sorted(tpe_modes.items(), key=lambda x: -x[1]):
        print(f'  {mode:15s}: {count:3d} ({100*count/len(data):.1f}%)')
    
    # Check for T-dominant
    t_dominant = [r for r in data if r['tpe_mode'] == 'T-dominant']
    print(f'\nT-dominant rules: {len(t_dominant)} (condensates never fragment)')
    
    # Top by emergence
    print('\nTOP 5 BY EMERGENCE (E = T·P × |T-P|):')
    sorted_by_e = sorted(data, key=lambda x: x['emergence'], reverse=True)[:5]
    for r in sorted_by_e:
        print(f"  {r['rule_str']:20s} E={r['emergence']:.4f} T={r['toroidal']:.2f} P={r['poloidal']:.2f}")
    
    # P distribution for condensates
    p_values = [r['poloidal'] for r in data]
    print('\nP (Poloidal) Statistics:')
    print(f'  Mean: {np.mean(p_values):.3f}')
    print(f'  Min:  {np.min(p_values):.3f}')
    print(f'  Max:  {np.max(p_values):.3f}')


def full_analysis():
    """
    Run all analyses for the whitepaper.
    """
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  VACUUM CONDENSATE PHASES IN THE RULIAD                      ║")
    print("║  Full Analysis Results                                       ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    
    condensate_summary()
    print("\n" + "="*60 + "\n")
    
    tpe_analysis()
    print("\n" + "="*60 + "\n")
    
    s_correlation()
    print("\n" + "="*60 + "\n")
    
    print("═══ CONTROL TEST ═══")
    print("(Running control test requires simulation, use 'control_test' command)")


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        full_analysis()
        return
    
    command = sys.argv[1]
    
    commands = {
        'condensate_summary': condensate_summary,
        'control_test': control_test,
        's_correlation': s_correlation,
        'tpe_analysis': tpe_analysis,
        'full': full_analysis,
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        print(f"Available: {', '.join(commands.keys())}")


if __name__ == "__main__":
    main()
