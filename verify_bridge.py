import numpy as np
from rulial.engine.totalistic import Totalistic2DEngine
from rulial.quantum.bridge import TensorBridge
import warnings

# Suppress warnings for clean output
warnings.filterwarnings("ignore")

def print_grid(grid):
    rows, cols = grid.shape
    for r in range(rows):
        line = ""
        for c in range(cols):
            line += "■" if grid[r, c] else "·"
        print(line)
    print("-" * cols)

def test_bridge():
    print("=== Testing Tensor Bridge (Quantum V3) ===")
    
    # 1. Physics: Stimulate Glider
    h, w = 10, 10
    engine = Totalistic2DEngine("B3/S23")
    grid = np.zeros((h, w), dtype=np.uint8)
    # Shift Glider closer to the middle (Col 5 is boundary)
    # Start at Col 3
    # 0 1 2 [3] 4 | 5 6 7.
    # Pattern width 3. So occupies 3,4,5. Immediately straddles?
    # Glider:
    # ..1  (col 3,4,5) -> (1,5) is 1.
    # 1.1
    # .11
    
    # Let's put top-left at (1, 3)
    grid[1, 3] = 0 # Clear previous
    grid[2, 3] = 0
    grid[3, 3] = 0
    grid[3, 2] = 0 
    grid[3, 1] = 0 
    
    # Glider shape at (row 1, col 3)
    # 0 1 0
    # 0 0 1
    # 1 1 1
    
    # Relative to (1,3):
    # (0, 1) -> (1, 4)
    # (1, 2) -> (2, 5)  <- On boundary at start!
    # (2, 0) -> (3, 3)
    # (2, 1) -> (3, 4)
    # (2, 2) -> (3, 5)  <- On boundary
    
    grid = np.zeros((h, w), dtype=np.uint8)
    grid[1, 4] = 1
    grid[2, 5] = 1
    grid[3, 3] = 1
    grid[3, 4] = 1
    grid[3, 5] = 1
    
    hist = engine.simulate(h, w, 15, "custom", custom_grid=grid)
    
    # 2. Transduction: Tensor Bridge
    bridge = TensorBridge(h, w)
    
    for t in range(15):
        frame = hist[t]
        print(f"\nTime {t}:")
        print_grid(frame)
        
        # Convert to PEPS and measure Entropy
        psi = bridge.grid_to_tensor_state(frame)
        res = bridge.compute_bipartition_entropy(psi)
        
        if res['status'] == 'error':
             print(f"Entanglement Entropy: Error: {res.get('message', 'Unknown')}")
        else:
             print(f"Entanglement Entropy: {res['entropy']:.6f} ({res['status']})")
        
        # Checking consistency
        if t > 0 and res['entropy'] < 0.001:
             print("WARNING: Zero entropy for active pattern?")

if __name__ == "__main__":
    test_bridge()
