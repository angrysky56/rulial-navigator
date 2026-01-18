#!/usr/bin/env python
"""
Goldilocks Zone Stress Test

This script validates the "Goldilocks Zone" claim (H = 0.3-0.6) by:
1. Randomly generating rules until we find ones in the Goldilocks range
2. Testing each candidate for actual computational structures (gliders)
3. Computing a "Precision" metric: what fraction of Goldilocks rules actually compute?

This provides honest validation of the predictive power of the Harmonic Overlap metric.

Usage:
    uv run python scripts/stress_test_goldilocks.py
"""

import sys
import os
import random
from contextlib import redirect_stdout
import io

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def stress_test(target_samples: int = 20, verbose: bool = True):
    """
    Stress test the Goldilocks Zone hypothesis.
    
    For each rule in 0.3 < H < 0.6:
    - Check for gliders, oscillators, or still lifes
    - Compute precision (true positive rate)
    """
    from rulial.mapper.sheaf import SheafAnalyzer
    from rulial.runners.investigate_particle import investigate_rule
    
    print("🕵️ GOLDILOCKS ZONE STRESS TEST")
    print(f"Target: {target_samples} rules with 0.3 < H < 0.6")
    print("Verifying each for computational structures...")
    print()
    
    analyzer = SheafAnalyzer(grid_size=32, steps=50)
    
    found_goldilocks = 0
    verified_computational = 0
    partial_computational = 0
    false_positives = 0
    tested_rules = 0
    max_attempts = target_samples * 50  # Prevent infinite loop
    
    results = []
    
    while found_goldilocks < target_samples and tested_rules < max_attempts:
        tested_rules += 1
        
        # Generate random totalistic rule
        b = "".join([str(x) for x in sorted(random.sample(range(9), random.randint(1, 4)))])
        s = "".join([str(x) for x in sorted(random.sample(range(9), random.randint(1, 5)))])
        rule_str = f"B{b}/S{s}"
        
        # Sheaf analysis
        try:
            res = analyzer.analyze(rule_str)
        except Exception:
            continue
        
        h = res.harmonic_overlap
        phi = res.monodromy_index
        
        # Check if in Goldilocks Zone
        if 0.3 <= h <= 0.6:
            found_goldilocks += 1
            
            if verbose:
                print(f"[{found_goldilocks:2d}/{target_samples}] {rule_str:15s} H={h:.3f} Φ={phi:+.1f}", end=" ")
            
            # Glider verification (suppress output)
            f = io.StringIO()
            try:
                with redirect_stdout(f):
                    structs = investigate_rule(rule_str, steps=150, grid_size=48)
                
                gliders = structs.get('gliders', 0)
                oscillators = structs.get('oscillators', 0)
                still_lifes = structs.get('still_lifes', 0)
                
                result = {
                    'rule': rule_str,
                    'H': h,
                    'Phi': phi,
                    'gliders': gliders,
                    'oscillators': oscillators,
                    'still_lifes': still_lifes
                }
                results.append(result)
                
                if gliders > 0:
                    if verbose:
                        print(f"✅ {gliders} gliders")
                    verified_computational += 1
                elif oscillators > 0 or still_lifes > 5:
                    if verbose:
                        print(f"⚠️ {oscillators} osc, {still_lifes} still")
                    partial_computational += 1
                else:
                    if verbose:
                        print(f"❌ No structures")
                    false_positives += 1
                    
            except Exception as e:
                if verbose:
                    print(f"⚠️ Error: {e}")
                false_positives += 1
    
    # Summary
    print()
    print("═══ STRESS TEST RESULTS ═══")
    print()
    print(f"Rules tested:              {tested_rules}")
    print(f"Goldilocks candidates:     {found_goldilocks}")
    print()
    print(f"① Gliders found:          {verified_computational:3d} ({100*verified_computational/max(1,found_goldilocks):.1f}%)")
    print(f"② Oscillators/Still:      {partial_computational:3d} ({100*partial_computational/max(1,found_goldilocks):.1f}%)")
    print(f"③ No structures:          {false_positives:3d} ({100*false_positives/max(1,found_goldilocks):.1f}%)")
    print()
    
    # Compute precision
    strict_precision = verified_computational / max(1, found_goldilocks)
    relaxed_precision = (verified_computational + partial_computational) / max(1, found_goldilocks)
    
    print(f"STRICT PRECISION (gliders only):        {strict_precision:.1%}")
    print(f"RELAXED PRECISION (any structure):      {relaxed_precision:.1%}")
    print()
    
    # Interpretation
    if strict_precision >= 0.5:
        print("✅ GOLDILOCKS ZONE VALIDATED")
        print(f"   {strict_precision:.0%} of H=0.3-0.6 rules contain gliders.")
    elif relaxed_precision >= 0.6:
        print("✅ PARTIAL VALIDATION")
        print(f"   {relaxed_precision:.0%} of H=0.3-0.6 rules contain computational structures.")
    else:
        print("⚠️ WEAK VALIDATION")
        print(f"   Only {relaxed_precision:.0%} of Goldilocks rules show structure.")
        print("   The Goldilocks zone is suggestive but not strongly predictive.")
    
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Stress test the Goldilocks Zone hypothesis")
    parser.add_argument("--samples", type=int, default=20, help="Number of Goldilocks rules to test")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-rule output")
    args = parser.parse_args()
    
    stress_test(target_samples=args.samples, verbose=not args.quiet)


if __name__ == "__main__":
    main()
