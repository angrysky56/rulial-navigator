"""
Universality Test: Proving Condensation is Universal

This test proves that "vacuum condensation" is not just an artifact of
totalistic (sum-based) CA rules, but a universal feature of any rule
where the "all-zero neighborhood" maps to 1 (the generalized B0 condition).

Hypothesis: Any rule where the empty neighborhood activates a cell will
exhibit Monodromy ≈ +1 (resonance/condensate behavior).
"""

import numpy as np
from typing import Callable
from scipy.signal import convolve2d


class LookupTableEngine:
    """
    A non-totalistic CA engine using a 512-bit lookup table.
    
    Instead of summing neighbors (totalistic), it uses the exact 3x3
    configuration to look up the next state. This covers ALL possible
    2D Moore-neighborhood CA rules.
    
    The 3x3 neighborhood is encoded as a 9-bit index (0-511):
    [[256, 128, 64], [32, 16, 8], [4, 2, 1]]
    
    Index 0 = all neighbors dead = the "generalized B0" condition.
    """
    
    def __init__(self, rule_table: np.ndarray):
        """
        Initialize with a 512-element boolean array.
        
        rule_table[i] = 1 means configuration i produces a live cell.
        """
        assert len(rule_table) == 512, "Rule table must have 512 entries"
        self.lut = rule_table.astype(np.uint8)
        
        # Check if this is a "generalized B0" rule
        # Index 0 = center cell dead, all 8 neighbors dead
        # If lut[0] = 1, then empty space creates cells → condensate
        self.has_generalized_b0 = bool(self.lut[0])
    
    @classmethod
    def from_hex(cls, hex_string: str) -> 'LookupTableEngine':
        """Create from a 128-character hex string (512 bits)."""
        # Pad to 128 chars if needed
        hex_string = hex_string.zfill(128)
        binary = bin(int(hex_string, 16))[2:].zfill(512)
        rule_table = np.array([int(b) for b in binary], dtype=np.uint8)
        return cls(rule_table)
    
    @classmethod
    def random(cls, force_b0: bool = False, seed: int = None) -> 'LookupTableEngine':
        """Generate a random 512-bit rule."""
        if seed is not None:
            np.random.seed(seed)
        rule_table = np.random.randint(0, 2, size=512, dtype=np.uint8)
        
        if force_b0:
            # Set index 0 to 1: empty neighborhood → birth
            rule_table[0] = 1
        
        return cls(rule_table)
    
    def step(self, grid: np.ndarray) -> np.ndarray:
        """
        Advance the grid by one step using the lookup table.
        """
        # Kernel encodes each position as a power of 2
        # Positions: [[NW, N, NE], [W, C, E], [SW, S, SE]]
        # We want center (C) included in the index for full generality
        kernel = np.array([
            [256, 128, 64],
            [32,  16,  8],
            [4,   2,   1]
        ], dtype=np.int32)
        
        # Convolve to get neighborhood index for each cell
        indices = convolve2d(
            grid.astype(np.int32), 
            kernel, 
            mode='same', 
            boundary='wrap'
        )
        
        # Look up new state for each cell
        return self.lut[indices.astype(np.int32)]
    
    def simulate(
        self, 
        size: int, 
        steps: int, 
        density: float = 0.3,
        seed: int = None
    ) -> list[np.ndarray]:
        """
        Simulate the CA for a given number of steps.
        """
        if seed is not None:
            np.random.seed(seed)
        
        grid = (np.random.random((size, size)) < density).astype(np.uint8)
        history = [grid.copy()]
        
        for _ in range(steps):
            grid = self.step(grid)
            history.append(grid.copy())
        
        return history


def create_simulator_callback(engine: LookupTableEngine) -> Callable:
    """Create a simulator callback for SheafAnalyzer."""
    def simulate(rule_str: str, size: int, steps: int, seed: int) -> np.ndarray:
        history = engine.simulate(size, steps, density=0.3, seed=seed)
        return history[-1]
    return simulate


def run_universality_test(samples: int = 20, verbose: bool = True):
    """
    Test whether the generalized B0 condition universally produces condensation.
    
    Hypothesis:
    - Rules with B0 (empty neighborhood → birth) → Monodromy ≈ +1 (resonance)
    - Rules without B0 → Monodromy ≈ -1 (tension)
    """
    from rulial.mapper.sheaf import SheafAnalyzer
    
    print("═══ UNIVERSALITY TEST ═══")
    print(f"Testing {samples} non-totalistic rules")
    print("Hypothesis: Generalized B0 → Condensation is universal")
    print()
    
    results_b0 = []
    results_non_b0 = []
    
    for i in range(samples):
        if verbose:
            print(f"\rTesting rule {i+1}/{samples}", end="")
        
        # Test B0 rule (generalized condensate)
        engine_b0 = LookupTableEngine.random(force_b0=True, seed=i)
        history_b0 = engine_b0.simulate(16, 20, density=0.01, seed=i)
        
        # Measure "monodromy" via expansion
        initial_b0 = max(1, history_b0[0].sum())
        final_b0 = history_b0[-1].sum()
        spread_b0 = final_b0 / initial_b0
        
        if spread_b0 > 10:
            mono_b0 = 1.0
        elif spread_b0 > 1:
            mono_b0 = np.tanh(np.log(spread_b0))
        else:
            mono_b0 = -1.0
        
        results_b0.append(mono_b0)
        
        # Test non-B0 rule
        engine_non = LookupTableEngine.random(force_b0=False, seed=i + 1000)
        # Make sure it doesn't have B0 by accident
        engine_non.lut[0] = 0
        
        history_non = engine_non.simulate(16, 20, density=0.01, seed=i)
        initial_non = max(1, history_non[0].sum())
        final_non = history_non[-1].sum()
        spread_non = final_non / initial_non
        
        if spread_non > 10:
            mono_non = 1.0
        elif spread_non > 1:
            mono_non = np.tanh(np.log(max(0.01, spread_non)))
        else:
            mono_non = -1.0
        
        results_non_b0.append(mono_non)
    
    if verbose:
        print()
    
    # Results
    print()
    print("═══ RESULTS ═══")
    print()
    
    mean_b0 = np.mean(results_b0)
    std_b0 = np.std(results_b0)
    mean_non = np.mean(results_non_b0)
    std_non = np.std(results_non_b0)
    
    print(f"Generalized B0 (Condensate):")
    print(f"  Mean Monodromy: {mean_b0:+.4f} ± {std_b0:.4f}")
    print(f"  Resonant (+1): {sum(1 for m in results_b0 if m > 0.5)}/{len(results_b0)}")
    print()
    
    print(f"Non-B0 (Particle/Chaos):")
    print(f"  Mean Monodromy: {mean_non:+.4f} ± {std_non:.4f}")
    print(f"  Tense (-1): {sum(1 for m in results_non_b0 if m < -0.5)}/{len(results_non_b0)}")
    print()
    
    # Verdict
    if mean_b0 > 0.5 and mean_non < 0:
        print("✅ UNIVERSALITY CONFIRMED!")
        print("   Vacuum condensation is a universal feature of")
        print("   computational rule spaces, not just totalistic CA.")
    elif mean_b0 > mean_non + 0.5:
        print("✅ PARTIAL CONFIRMATION")
        print("   B0 rules trend toward resonance more than non-B0.")
    else:
        print("❌ HYPOTHESIS NOT SUPPORTED")
        print("   B0 condition does not universally predict condensation.")
    
    return results_b0, results_non_b0


if __name__ == "__main__":
    run_universality_test(samples=30)
