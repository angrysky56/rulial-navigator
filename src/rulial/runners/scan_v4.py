"""
V4 Atlas Scanner with Sheaf Metrics

Systematic scan of Rulial Space capturing:
- Compression flow metrics
- Topological signatures (β₁)
- Condensate analysis
- Sheaf metrics (monodromy, harmonic overlap)
- T-P+E dynamics

Outputs to SQLite atlas for persistence and analysis.
"""

import json
import argparse
from pathlib import Path

from rulial.mapper.atlas import Atlas
from rulial.mapper.sheaf import SheafAnalyzer
from rulial.mapper.condensate import VacuumCondensateAnalyzer
from rulial.mapper.tpe import TPEAnalyzer
from rulial.compression.flow import CompressionFlowAnalyzer
from rulial.engine.totalistic import Totalistic2DEngine


def generate_random_totalistic(seed: int = None) -> str:
    """Generate a random totalistic 2D rule string."""
    import numpy as np
    if seed is not None:
        np.random.seed(seed)
    
    # Random B and S sets
    b_digits = [str(d) for d in range(9) if np.random.random() < 0.4]
    s_digits = [str(d) for d in range(9) if np.random.random() < 0.5]
    
    # Ensure at least one birth condition
    if not b_digits:
        b_digits = [str(np.random.randint(0, 9))]
    
    return f"B{''.join(b_digits)}/S{''.join(s_digits)}"


def parse_rule(rule_str: str) -> tuple[str, str]:
    """Parse B/S sets from rule string."""
    parts = rule_str.split('/')
    b_set = parts[0].replace('B', '') if len(parts) > 0 else ''
    s_set = parts[1].replace('S', '') if len(parts) > 1 else ''
    return b_set, s_set


def classify_wolfram(
    sheaf_result, 
    condensate_result,
    compression_result
) -> int:
    """
    Classify rule into Wolfram class based on multiple signals.
    """
    # Use existing classification logic
    if compression_result.wolfram_class:
        return compression_result.wolfram_class
    
    # Fallback heuristics
    if sheaf_result.monodromy_index < -0.5:
        # Tense = particle behavior
        if sheaf_result.harmonic_overlap > 0.8:
            return 2  # Settled
        else:
            return 4  # Complex
    else:
        # Resonant = condensate
        if sheaf_result.harmonic_overlap > 0.9:
            return 2  # Frozen
        else:
            return 4  # Active condensate
    
    return 3  # Chaos fallback


def scan_batch(
    count: int = 200, 
    db_path: str = "atlas.db",
    mode: str = "random"
):
    """
    Scan a batch of rules with full metrics pipeline.
    """
    atlas = Atlas(db_path=db_path)
    
    sheaf = SheafAnalyzer(grid_size=32, steps=50)
    condensate = VacuumCondensateAnalyzer(grid_size=32, steps=80)
    tpe = TPEAnalyzer()
    compression = CompressionFlowAnalyzer()
    
    print(f"🚀 V4 Scan: {count} rules → {db_path}")
    print(f"Mode: {mode}")
    print()
    
    for i in range(count):
        # Generate rule
        if mode == "random":
            rule_str = generate_random_totalistic(seed=i)
        elif mode == "condensate":
            # Force B0/B1 for condensate focus
            rule_str = generate_random_totalistic(seed=i)
            b_set, s_set = parse_rule(rule_str)
            if '0' not in b_set and '1' not in b_set:
                b_set = '0' + b_set
            rule_str = f"B{b_set}/S{s_set}"
        else:
            rule_str = generate_random_totalistic(seed=i)
        
        b_set, s_set = parse_rule(rule_str)
        
        try:
            # Run analyzers
            sheaf_res = sheaf.analyze(rule_str)
            cond_res = condensate.analyze(rule_str)
            tpe_res = tpe.analyze(rule_str)
            comp_res = compression.analyze(rule_str)
            
            # Classify
            w_class = classify_wolfram(sheaf_res, cond_res, comp_res)
            
            # Determine phase
            if cond_res.is_condensate:
                phase = "condensate"
            elif sheaf_res.monodromy_index < -0.5:
                phase = "particle"
            else:
                phase = "hybrid"
            
            # Record to atlas
            atlas.record(
                rule_str=rule_str,
                wolfram_class=w_class,
                telemetry=comp_res,
                sheaf=sheaf_res,
                condensate=cond_res,
                tpe=tpe_res,
                phase=phase,
                b_set=b_set,
                s_set=s_set,
            )
            
            # Progress
            mono_str = f"{sheaf_res.monodromy_index:+.2f}"
            phase_icon = "🌊" if cond_res.is_condensate else "⚛️"
            print(f"[{i+1:3d}/{count}] {rule_str:20s} {phase_icon} Φ={mono_str} H={sheaf_res.harmonic_overlap:.2f}")
            
        except Exception as e:
            print(f"[{i+1:3d}/{count}] {rule_str:20s} ❌ Error: {e}")
    
    # Summary
    stats = atlas.get_statistics()
    print()
    print("═══ SCAN COMPLETE ═══")
    print(f"Total rules: {stats.get('total', 0)}")
    print(f"Class 4: {stats.get('class_4', 0)}")
    print(f"Condensates: {stats.get('condensates', 0)}")
    print(f"Avg monodromy: {stats.get('avg_monodromy', 0):.3f}")
    print(f"Avg harmonic overlap: {stats.get('avg_overlap', 0):.3f}")
    
    atlas.close()


def import_json(json_path: str, db_path: str = "atlas.db"):
    """Import existing JSON atlas into SQLite."""
    atlas = Atlas(db_path=db_path)
    count = atlas.import_from_json(json_path)
    print(f"✅ Imported {count} records from {json_path} → {db_path}")
    atlas.close()


def main():
    parser = argparse.ArgumentParser(description="V4 Atlas Scanner")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Run a new scan")
    scan_parser.add_argument("--count", type=int, default=200, help="Number of rules")
    scan_parser.add_argument("--mode", choices=["random", "condensate"], default="random")
    scan_parser.add_argument("--db", default="atlas.db", help="Database path")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import JSON data")
    import_parser.add_argument("json_file", help="JSON file to import")
    import_parser.add_argument("--db", default="atlas.db", help="Database path")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.add_argument("--db", default="atlas.db", help="Database path")
    
    args = parser.parse_args()
    
    if args.command == "scan":
        scan_batch(count=args.count, db_path=args.db, mode=args.mode)
    elif args.command == "import":
        import_json(args.json_file, db_path=args.db)
    elif args.command == "stats":
        atlas = Atlas(db_path=args.db)
        stats = atlas.get_statistics()
        print("═══ ATLAS STATISTICS ═══")
        for k, v in stats.items():
            print(f"  {k}: {v}")
        atlas.close()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
