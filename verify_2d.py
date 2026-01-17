import numpy as np
from rulial.engine.totalistic import Totalistic2DEngine

def print_grid(grid):
    rows, cols = grid.shape
    for r in range(rows):
        line = ""
        for c in range(cols):
            line += "■" if grid[r, c] else "·"
        print(line)
    print("-" * cols)



def test_glider():
    print("Testing Game of Life (B3/S23) - Glider")
    engine = Totalistic2DEngine("B3/S23")
    
    # Custom Init: Glider
    # .1.
    # ..1
    # 111
    h, w = 10, 10
    grid = np.zeros((h, w), dtype=np.uint8)
    # Start at top left (shifted slightly)
    # 0 1 0
    # 0 0 1
    # 1 1 1
    grid[1, 2] = 1
    grid[2, 3] = 1
    grid[3, 1] = 1
    grid[3, 2] = 1
    grid[3, 3] = 1
    
    hist = engine.simulate(h, w, 5, "custom", custom_grid=grid)
    
    for t in range(5):
        print(f"Frame {t}")
        print_grid(hist[t])

if __name__ == "__main__":
    test_glider()
