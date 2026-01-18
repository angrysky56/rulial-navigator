"""
Unit test for Miner detection logic.
Injects a known Glider to verify it is detected as a spaceship.
"""

import sys

import numpy as np

from rulial.mining.extractor import ParticleMiner


def test_glider_detection():
    print("Testing Glider Detection...")

    # Glider pattern
    # .O.
    # ..O
    # OOO
    glider = np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]], dtype=np.uint8)

    size = 32
    # Place glider in top left
    grid = np.zeros((size, size), dtype=np.uint8)
    grid[5:8, 5:8] = glider

    miner = ParticleMiner("B3/S23")
    print(f"Engine Rules: Born={miner.engine.born}, Survive={miner.engine.survive}")

    # Run mining (Short duration to avoid wall collision)
    particles = miner.mine_grid(grid, steps=20)

    print(f"Found {len(particles)} particles.")

    glider_found = False
    for p in particles:
        print(
            f"Name: {p.name}, Period: {p.period}, Velocity: {p.velocity:.2f}, Vector: ({p.dx}, {p.dy})"
        )
        print("Pattern (cropped):")
        print(p.pattern)
        if "Spaceship" in p.name or "Glider" in p.name:
            glider_found = True

    if glider_found:
        print("SUCCESS: Glider detected!")
    else:
        print("FAILURE: Glider NOT detected.")
        sys.exit(1)


if __name__ == "__main__":
    test_glider_detection()
