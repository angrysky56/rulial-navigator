"""
Quick Example: Analyze a Single Rule

Demonstrates the full analysis pipeline for any rule.
"""

from rulial.compression.flow import CompressionFlowAnalyzer
from rulial.mapper.condensate import VacuumCondensateAnalyzer
from rulial.mapper.tpe import TPEAnalyzer
from rulial.mining.oligon import OligonCounter


def analyze_rule(rule_str: str):
    """Perform full analysis on a single rule."""
    print(f"╔══════════════════════════════════════════════════════════════╗")
    print(f"║  FULL ANALYSIS: {rule_str:43s} ║")
    print(f"╚══════════════════════════════════════════════════════════════╝\n")
    
    # 1. Compression Flow
    print("📊 COMPRESSION FLOW")
    print("-" * 40)
    flow = CompressionFlowAnalyzer()
    flow_result = flow.analyze(rule_str)
    print(flow_result.summary())
    
    # 2. T-P+E Dynamics
    print("\n\n🌀 T-P+E DYNAMICS")
    print("-" * 40)
    tpe = TPEAnalyzer()
    tpe_result = tpe.analyze(rule_str)
    print(tpe_result.summary())
    
    # 3. Vacuum Condensate
    print("\n\n🌊 VACUUM CONDENSATE")
    print("-" * 40)
    cond = VacuumCondensateAnalyzer()
    cond_result = cond.analyze(rule_str)
    print(cond_result.summary())
    
    # 4. Oligon Census
    print("\n\n⚛️ OLIGON CENSUS")
    print("-" * 40)
    olig = OligonCounter()
    olig_result = olig.count(rule_str)
    print(olig_result.summary())
    
    # Summary
    print("\n\n" + "=" * 60)
    print("VERDICT:")
    if cond_result.is_condensate:
        print(f"  🌊 CONDENSATE PHASE")
        print(f"  Equilibrium density: {cond_result.equilibrium_density:.1%}")
        print(f"  Single cell expands to: {cond_result.expansion_factor:.0f} cells")
    else:
        print(f"  ⚛️ PARTICLE PHASE")
        print(f"  Oligons: {olig_result.total_oligons}")
        print(f"  Supports isolated structures: YES")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        rule = sys.argv[1]
    else:
        rule = "B3/S23"  # Default: Game of Life
    
    analyze_rule(rule)
