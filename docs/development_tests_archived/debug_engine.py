"""
Debug CA Engine.
Prints frames of a glider simulation to see if it moves.
"""

import numpy as np

from rulial.engine.totalistic import Totalistic2DEngine


def debug_print(grid):
    rows, cols = grid.shape
    for r in range(rows):
        line = ""
        for c in range(cols):
            line += "O" if grid[r, c] else "."
        print(line)
    print("-" * cols)


def test_engine():
    print("Testing Engine Dynamics...")
    glider = np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]], dtype=np.uint8)

    size = 10
    grid = np.zeros((size, size), dtype=np.uint8)
    grid[1:4, 1:4] = glider

    engine = Totalistic2DEngine("B3/S23")

    print("Frame 0:")
    debug_print(grid)

    # Step manually
    for i in range(1, 6):
        grid = engine.step(grid)
        print(f"Frame {i}:")
        debug_print(grid)


if __name__ == "__main__":
    test_engine()
