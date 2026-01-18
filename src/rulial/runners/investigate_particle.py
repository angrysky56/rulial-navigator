"""
Particle Investigator - Find Computational Structures

Analyzes particle-phase rules for:
- Oligons (isolated, persistent structures)
- Gliders (moving objects)
- Oscillators (cycling objects)
- Still lifes (stable objects)

This investigates the "Goldilocks zone" particles that may support computation.
"""

import numpy as np
from typing import List, Tuple
from rulial.engine.totalistic import Totalistic2DEngine


def label_components(grid: np.ndarray) -> Tuple[np.ndarray, int]:
    """
    Label connected components using a simple flood fill.
    Returns labeled grid and number of components.
    """
    h, w = grid.shape
    labels = np.zeros_like(grid, dtype=np.int32)
    label_num = 0
    
    def flood_fill(start_r, start_c, label):
        stack = [(start_r, start_c)]
        while stack:
            r, c = stack.pop()
            if r < 0 or r >= h or c < 0 or c >= w:
                continue
            if grid[r, c] == 0 or labels[r, c] != 0:
                continue
            labels[r, c] = label
            # 8-connectivity
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr != 0 or dc != 0:
                        stack.append((r + dr, c + dc))
    
    for r in range(h):
        for c in range(w):
            if grid[r, c] == 1 and labels[r, c] == 0:
                label_num += 1
                flood_fill(r, c, label_num)
    
    return labels, label_num


def get_component_properties(grid: np.ndarray, labels: np.ndarray, label_id: int) -> dict:
    """Get properties of a labeled component."""
    mask = labels == label_id
    coords = np.where(mask)
    
    if len(coords[0]) == 0:
        return None
    
    min_r, max_r = coords[0].min(), coords[0].max()
    min_c, max_c = coords[1].min(), coords[1].max()
    
    return {
        'label': label_id,
        'area': mask.sum(),
        'bbox': (min_r, min_c, max_r, max_c),
        'height': max_r - min_r + 1,
        'width': max_c - min_c + 1,
        'centroid': (coords[0].mean(), coords[1].mean()),
        'pattern': grid[min_r:max_r+1, min_c:max_c+1].copy()
    }


def pattern_hash(pattern: np.ndarray) -> str:
    """Create a hash of a pattern for comparison."""
    return ''.join(str(c) for c in pattern.flatten())


def investigate_rule(rule_str: str, steps: int = 200, grid_size: int = 64):
    """
    Investigate a rule for computational structures.
    """
    print(f"🕵️ Investigating: {rule_str}")
    print(f"   Grid: {grid_size}x{grid_size}, Steps: {steps}")
    print()
    
    engine = Totalistic2DEngine(rule_str)
    
    # Run simulation
    history = engine.simulate(grid_size, grid_size, steps, 'random', density=0.15)
    
    # Analyze last 20 frames for persistent structures
    frame_window = min(20, len(history))
    recent_frames = history[-frame_window:]
    
    # Track objects across frames
    all_patterns = {}
    pattern_occurrences = {}
    
    for frame_idx, frame in enumerate(recent_frames):
        labels, n_components = label_components(frame)
        
        for label_id in range(1, n_components + 1):
            props = get_component_properties(frame, labels, label_id)
            if props and 3 <= props['area'] <= 30:  # Filter interesting sizes
                h = pattern_hash(props['pattern'])
                
                if h not in all_patterns:
                    all_patterns[h] = props
                    pattern_occurrences[h] = []
                
                pattern_occurrences[h].append({
                    'frame': len(history) - frame_window + frame_idx,
                    'centroid': props['centroid']
                })
    
    # Classify patterns
    still_lifes = []
    oscillators = []
    gliders = []
    transients = []
    
    for h, occurrences in pattern_occurrences.items():
        pattern = all_patterns[h]
        n_occur = len(occurrences)
        
        if n_occur >= frame_window - 2:  # Appears in most frames
            # Check for movement
            centroids = [o['centroid'] for o in occurrences]
            if len(centroids) > 1:
                dr = abs(centroids[-1][0] - centroids[0][0])
                dc = abs(centroids[-1][1] - centroids[0][1])
                
                if dr > 3 or dc > 3:
                    gliders.append((pattern, dr + dc))
                else:
                    still_lifes.append(pattern)
        elif n_occur >= 5:
            oscillators.append(pattern)
        else:
            transients.append(pattern)
    
    # Report
    print("═══ STRUCTURE CENSUS ═══")
    print(f"  Still Lifes:  {len(still_lifes)}")
    print(f"  Oscillators:  {len(oscillators)}")  
    print(f"  Gliders:      {len(gliders)}")
    print(f"  Transients:   {len(transients)}")
    print()
    
    # Show interesting structures
    if gliders:
        print("🚀 GLIDER CANDIDATES:")
        for pattern, movement in gliders[:5]:
            print(f"  Size: {pattern['area']} cells, Movement: {movement:.1f} cells")
            _print_pattern(pattern['pattern'])
    
    if still_lifes:
        print("🗿 STILL LIFES (sample):")
        for pattern in still_lifes[:3]:
            print(f"  Size: {pattern['area']} cells")
            _print_pattern(pattern['pattern'])
    
    if oscillators:
        print("💫 OSCILLATOR CANDIDATES:")
        for pattern in oscillators[:3]:
            print(f"  Size: {pattern['area']} cells")
            _print_pattern(pattern['pattern'])
    
    # Verdict
    print()
    print("═══ VERDICT ═══")
    if gliders:
        print("✅ GLIDERS FOUND - Potential for signal transmission!")
    elif still_lifes and oscillators:
        print("⚡ Still lifes + Oscillators - Potential for memory/computation")
    elif still_lifes:
        print("🗿 Still lifes only - Limited computational capacity")
    else:
        print("💨 No persistent structures - Chaotic rule")
    
    return {
        'still_lifes': len(still_lifes),
        'oscillators': len(oscillators),
        'gliders': len(gliders),
        'transients': len(transients)
    }


def _print_pattern(pattern: np.ndarray):
    """Print a small pattern."""
    for row in pattern:
        print("    " + "".join("█" if c else "·" for c in row))
    print()


def compare_goldilocks(rules: List[str]):
    """Compare multiple Goldilocks candidates."""
    print("═══ GOLDILOCKS CANDIDATE COMPARISON ═══")
    print()
    
    results = {}
    for rule in rules:
        results[rule] = investigate_rule(rule)
        print("-" * 50)
    
    print()
    print("═══ SUMMARY ═══")
    print(f"{'Rule':20s} {'Gliders':>8s} {'Osc':>8s} {'Still':>8s}")
    print("-" * 50)
    for rule, res in results.items():
        print(f"{rule:20s} {res['gliders']:8d} {res['oscillators']:8d} {res['still_lifes']:8d}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        investigate_rule(sys.argv[1])
    else:
        # Investigate the Goldilocks candidates
        candidates = [
            "B6/S123467",     # Particle Goldilocks
            "B0467/S0568",    # Condensate Goldilocks  
            "B268/S0367",     # Particle Goldilocks
        ]
        compare_goldilocks(candidates)
