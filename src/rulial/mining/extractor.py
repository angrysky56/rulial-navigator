"""
The Miner: Automated Extraction of Physics from Rules.

This module automates the discovery of "particles" (gliders, oscillators, still lifes)
within a given Cellular Automaton rule.

Algorithm:
1. Primordial Soup: Run random grids.
2. Settlement: Wait for high-entropy chaos to die down (Ash formation).
3. Segmentation: Identify connected components (blobs) in the sparse grid.
4. Tracking: Track blobs over time to determine:
   - Periodicity (Does it repeat?)
   - Displacement (Does it move?)
   - Velocity (Displacement / Period)
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from scipy.ndimage import label

from rulial.engine.totalistic import Totalistic2DEngine


@dataclass
class Particle:
    rule_str: str
    pattern: np.ndarray  # The cropped minimal bounding box of the particle
    period: int
    dx: int
    dy: int
    name: str = "Unknown"

    @property
    def is_spaceship(self) -> bool:
        return self.dx != 0 or self.dy != 0

    @property
    def velocity(self) -> float:
        if self.period == 0:
            return 0.0
        dist = np.sqrt(self.dx**2 + self.dy**2)
        return dist / self.period

    def fingerprint(self) -> str:
        """Hash of the canonical pattern for deduplication."""
        return str(hash(self.pattern.tobytes()))


class ParticleMiner:
    def __init__(self, rule_str: str):
        self.rule_str = rule_str
        self.engine = Totalistic2DEngine(rule_str)
        self.found_particles: Dict[str, Particle] = {}

    def mine(
        self,
        attempts: int = 10,
        grid_size: int = 64,
        steps: int = 500,
        density: float = 0.5,
    ) -> List[Particle]:
        """
        Run multiple soup experiments to find particles.
        """
        for _ in range(attempts):
            self._run_experiment(grid_size, steps, density)
        return list(self.found_particles.values())

    def mine_grid(self, grid: np.ndarray, steps: int = 500) -> List[Particle]:
        """Mine from a specific grid state."""
        h, w = grid.shape
        history = self.engine.simulate(
            h, w, steps, init_condition="custom", custom_grid=grid
        )
        self._analyze_history(history, steps)
        return list(self.found_particles.values())

    def _run_experiment(self, size: int, steps: int, density: float):
        # 1. Run Soup
        if density != 0.5:
            seed = (np.random.random((size, size)) < density).astype(np.uint8)
            history = self.engine.simulate(
                size, size, steps, init_condition="custom", custom_grid=seed
            )
        else:
            history = self.engine.simulate(size, size, steps, init_condition="random")
        self._analyze_history(history, steps)

    def _analyze_history(self, history, steps):

        # 2. Analyze the 'Ash' (last few frames)
        # We look for separate connected components
        last_frame = history[-1]
        # Use 8-connectivity (diagonals count) to keep gliders as one object
        structure = np.ones((3, 3), dtype=np.int8)
        labeled_array, num_features = label(last_frame, structure=structure)

        if num_features == 0 or num_features > 50:
            # Too empty or too chaotic/dense to segment cleanly
            return

        # 3. For each blob, trace it BACKWARDS or check periodicity
        # Simplified: Check if this blob exists in previous frames with offset

        # Optimization: Just check the last 20 frames for cycles
        check_depth = 20
        for component_id in range(1, num_features + 1):
            mask = labeled_array == component_id
            blob = last_frame * mask

            # Crop to bounding box
            rows = np.any(blob, axis=1)
            cols = np.any(blob, axis=0)
            if not np.any(rows):
                continue

            rmin, rmax = np.where(rows)[0][[0, -1]]
            cmin, cmax = np.where(cols)[0][[0, -1]]

            pattern_t0 = blob[rmin : rmax + 1, cmin : cmax + 1]
            h, w = pattern_t0.shape

            if h * w > 100:
                continue  # Ignore huge blobs (like debris)

            # Check for this pattern in previous frames
            for p in range(1, check_depth):
                current_idx = steps - 1
                prev_idx = current_idx - p

                if prev_idx < 0:
                    break
                prev_frame = history[prev_idx]

                # Search for pattern_t0 in prev_frame
                # This is a template match.
                # For efficiency, we just assume it's isolated and check if we can find it.
                # Heuristic: Check center of mass shift?

                # Proper way: Cross Correlate? Too slow.
                # Heuristic: Scan neighborhood of current position
                # (Assuming speed <= c aka 1 cell/tick)

                # Let's simplify:
                # 1. Is it a Still Life? (Period 1, dx=0, dy=0)
                # 2. Is it a Period P oscillator?
                # 3. Is it a Spaceship?

                # Rigorous check:
                # Can we find pattern_t0 in prev_frame (shifted)?
                # If yes, we found a candidate.

                match_found, dx, dy = self._find_pattern_in_grid(
                    pattern_t0, prev_frame, rmin, cmin, p
                )
                if match_found:
                    # Found a cycle!
                    self._register_particle(pattern_t0, p, dx, dy)
                    break

    def _find_pattern_in_grid(
        self, pattern, grid, r_orig, c_orig, dt
    ) -> Tuple[bool, int, int]:
        """
        Check if pattern exists in grid within light-cone of (r_orig, c_orig).
        Light cone radius = dt (since speed limit = 1).
        """
        ph, pw = pattern.shape
        gh, gw = grid.shape

        # Search window
        r_start = max(0, r_orig - dt)
        r_end = min(gh - ph, r_orig + dt)
        c_start = max(0, c_orig - dt)
        c_end = min(gw - pw, c_orig + dt)

        for r in range(r_start, r_end + 1):
            for c in range(c_start, c_end + 1):
                subgrid = grid[r : r + ph, c : c + pw]
                if np.array_equal(subgrid, pattern):
                    # Check if it is isolated (surrounded by 0s) - skipped for MVP
                    # Calculate displacement from PAST to PRESENT
                    # (r,c) is 'past' pos. (r_orig, c_orig) is 'present' pos.
                    # displacement = present - past
                    dx = c_orig - c
                    dy = r_orig - r
                    print(
                        f"DEBUG: Found match p={dt} at past({r},{c}) vs present({r_orig},{c_orig}) -> dx={dx}, dy={dy}"
                    )
                    return True, dx, dy

        return False, 0, 0

    def _register_particle(self, pattern, period, dx, dy):
        """Save particle if new."""
        # Simple dedupe
        key = hash(pattern.tobytes())
        if key not in self.found_particles:
            name = "Still Life"
            if period > 1:
                name = f"Oscillator (P{period})"
            if dx != 0 or dy != 0:
                name = f"Spaceship (P{period}, v=({dx},{dy}))"
                if period == 4 and abs(dx) == 1 and abs(dy) == 1:
                    name = "Glider"  # Famous one

            self.found_particles[key] = Particle(
                rule_str=self.rule_str,
                pattern=pattern,
                period=period,
                dx=dx,
                dy=dy,
                name=name,
            )
