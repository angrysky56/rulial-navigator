import numpy as np
from typing import Literal, Optional

class ECAEngine:
    """
    1D Elementary Cellular Automata (ECA) simulation engine.
    Optimized for batch processing using NumPy vectorization.
    """
    
    def __init__(self, rule: int):
        """
        Initialize ECA engine with a specific rule.
        
        Args:
            rule: Integer between 0-255 representing the Wolfgang rule number.
        """
        if not (0 <= rule <= 255):
            raise ValueError("Rule must be between 0 and 255")
        
        self.rule = rule
        # Convert rule to 8-bit lookup table (binary representation)
        # We start from bit 0 (000) to bit 7 (111)
        # np.unpackbits is big-endian by default, so we reverse or manage indices carefully.
        # Let's map explicit neighborhood indices 0-7 to output bits.
        self.lookup_table = np.array([int(x) for x in f"{rule:08b}"[::-1]], dtype=np.uint8)

    def simulate(self, 
                 width: int, 
                 steps: int, 
                 init_condition: Literal["random", "single_seed"] = "single_seed",
                 custom_init: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Simulate the ECA for a given number of steps.
        
        Args:
            width: Width of the grid (number of cells).
            steps: Number of time steps to evolve.
            init_condition: 'random' for random 0/1, 'single_seed' for single 1 in center.
            custom_init: Optional 1D numpy array for custom initial state.
            
        Returns:
            np.ndarray: Space-time diagram of shape (steps, width).
                        Row 0 is the initial condition.
        """
        spacetime = np.zeros((steps, width), dtype=np.uint8)
        
        # Set initial condition
        if custom_init is not None:
            if len(custom_init) != width:
                raise ValueError(f"Custom init length {len(custom_init)} must match width {width}")
            spacetime[0] = custom_init.astype(np.uint8)
        elif init_condition == "single_seed":
            spacetime[0, width // 2] = 1
        elif init_condition == "random":
            spacetime[0] = np.random.randint(0, 2, size=width, dtype=np.uint8)
            
        # Evolution loop
        # We use numpy roll to get left and right neighbors efficiently
        current_state = spacetime[0]
        
        for t in range(1, steps):
            # Left neighbor (shift right)
            left = np.roll(current_state, 1)
            # Center (no shift)
            center = current_state
            # Right neighbor (shift left)
            right = np.roll(current_state, -1)
            
            # Calculate neighborhood index (0-7): 4*L + 2*C + 1*R
            neighborhood_idx = (left << 2) | (center << 1) | right
            
            # Apply rule lookup
            next_state = self.lookup_table[neighborhood_idx]
            
            spacetime[t] = next_state
            current_state = next_state
            
        return spacetime
