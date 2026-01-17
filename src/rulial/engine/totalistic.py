from typing import Tuple

import numpy as np
from scipy.signal import convolve2d


class Totalistic2DEngine:
    """
    Engine for 2D Outer Totalistic Cellular Automata (e.g., Game of Life).
    Uses convolution for efficient neighbor counting.
    """

    def __init__(self, rule_string: str = "B3/S23"):
        """
        Initialize with a rule string (Golly/RLE format).
        Format: "B3/S23" (Game of Life) or "B3678/S34678" (Day & Night).
        """
        self.born, self.survive = self._parse_rule(rule_string)

        # Moore Neighborhood Kernel
        self.kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])

    def _parse_rule(self, rule_str: str) -> Tuple[set, set]:
        """Parse Bx/Sy format."""
        # Normalize: ensure uppercase and standard order
        rule_str = rule_str.upper()
        parts = rule_str.split("/")

        born = set()
        survive = set()

        for p in parts:
            if p.startswith("B"):
                born.update(int(d) for d in p[1:])
            elif p.startswith("S"):
                survive.update(int(d) for d in p[1:])

        # Handle reverse format "23/3" -> S23/B3 if B/S missing?
        # Standard Golly is B.../S...
        return born, survive

    def init_grid(
        self,
        height: int,
        width: int,
        init_condition: str = "random",
        density: float = 0.5,
        custom_grid: np.ndarray = None,
    ) -> np.ndarray:
        """Initialize the grid."""
        if init_condition == "custom" and custom_grid is not None:
            grid = custom_grid.copy()
        elif init_condition == "random":
            grid = (np.random.random((height, width)) < density).astype(np.uint8)
        else:
            grid = np.zeros((height, width), dtype=np.uint8)
            # Center dot
            grid[height // 2, width // 2] = 1
        return grid

    def step(self, grid: np.ndarray) -> np.ndarray:
        """Advance the grid by one step."""
        # 1. Count neighbors via convolution
        # boundaries='wrap' for toroidal universe (standard for finite CA)
        neighbors = convolve2d(grid, self.kernel, mode="same", boundary="wrap")

        # 2. Apply Rule
        # Born: Cell is 0 and neighbors in B set
        # Survive: Cell is 1 and neighbors in S set
        # Dies: Otherwise

        # Vectorized rule application
        is_alive = grid == 1
        is_dead = grid == 0

        # Create masks
        born_mask = np.isin(neighbors, list(self.born)) & is_dead
        survive_mask = np.isin(neighbors, list(self.survive)) & is_alive

        next_grid = (born_mask | survive_mask).astype(np.uint8)
        return next_grid

    def simulate(
        self,
        height: int,
        width: int,
        steps: int,
        init_condition: str = "random",
        density: float = 0.5,
        custom_grid: np.ndarray = None,
    ) -> np.ndarray:
        """
        Simulate the CA.
        Returns: (steps, height, width) tensor.
        """
        grid = self.init_grid(height, width, init_condition, density, custom_grid)

        history = np.zeros((steps, height, width), dtype=np.uint8)
        history[0] = grid

        current_grid = grid

        for t in range(1, steps):
            next_grid = self.step(current_grid)
            history[t] = next_grid
            current_grid = next_grid

        return history
