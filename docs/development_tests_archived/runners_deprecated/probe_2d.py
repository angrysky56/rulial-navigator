import time

import numpy as np
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from rulial.engine.totalistic import Totalistic2DEngine
from rulial.navigator.titans import TitansNavigator
from rulial.quantum.bridge import TensorBridge


def int_to_bits(n: int, num_bits: int) -> np.ndarray:
    # Ensure binary string is padded
    bin_str = format(n, f"0{num_bits}b")
    # If n exceeds num_bits, it might be longer, handle optional truncation or strictness
    # For now assume n fits
    return np.array([int(x) for x in bin_str], dtype=np.float32)


def bits_to_int(bits: np.ndarray) -> int:
    return int("".join(str(int(b)) for b in bits), 2)


class RulialProbe2D:
    def __init__(self, width=64, height=64, steps=100, seed_rule=224, obs_window=12):
        # 1. Physics (The Universe)
        self.width = width
        self.height = height
        self.steps = steps

        # 2. Observer (The Quantum Bridge)
        # Optimized Default: 12x12
        # Contraction complexity scales as 2^N_active.
        # 12x12 = 144 sites. If 20% active -> ~28 qubits. Feasible.
        # 24x24 -> Likely OOM.
        self.obs_size = obs_window

        # Initialize Bridge with actual window size
        self.bridge = TensorBridge(
            max(self.obs_size, min(height, self.obs_size)),
            max(self.obs_size, min(width, self.obs_size)),
        )
        # Note: We will crop the grid to this size.

        # 3. Cognition (The Brain)
        # Input dim is 18 bits for the rule code
        self.navigator = TitansNavigator(rule_size_bits=18)

        self.current_rule = seed_rule
        self.history = []

        # Camera State (Active Observer)
        self.camera_x = float(width) / 2.0
        self.camera_y = float(height) / 2.0

        # Golden Cache
        self.filaments = []

    def run_loop(self, max_epochs=1000):
        layout = self._create_layout()

        # Using rich Live context
        with Live(layout, refresh_per_second=4, screen=True):
            for epoch in range(max_epochs):
                # --- Step A: Action (Simulate) ---

                rule_bits = int_to_bits(self.current_rule, 18)
                # Parse bits: B (0-8) -> S (9-17)
                b_indices = [i for i, b in enumerate(rule_bits[0:9]) if b == 1]
                s_indices = [i for i, b in enumerate(rule_bits[9:18]) if b == 1]

                b_str = "".join(map(str, b_indices))
                s_str = "".join(map(str, s_indices))
                rule_str = f"B{b_str}/S{s_str}"

                # Instantiate engine with current rule
                engine = Totalistic2DEngine(rule_str)

                # Run Simulation
                grid_history = engine.simulate(
                    self.height, self.width, self.steps, "random"
                )

                # Use the last frame for observation
                full_grid = grid_history[-1]

                # --- CROP GRID FOR OBSERVER (Active Born-Maxwell Focus) ---

                # 1. Measure "Born Probability" (Center of Mass of Activity)
                # We want to focus on where the information IS.
                active_rows, active_cols = np.nonzero(full_grid)

                target_y, target_x = self.camera_y, self.camera_x

                if len(active_rows) > 0:
                    # Calculate CoM
                    com_y = np.mean(active_rows)
                    com_x = np.mean(active_cols)

                    # 2. Maxwell's Demon (Camera Movement)
                    # Apply momentum/smoothing to avoid jitter
                    # alpha = 0.2 (20% move towards target per frame)
                    self.camera_y = (1 - 0.2) * self.camera_y + 0.2 * com_y
                    self.camera_x = (1 - 0.2) * self.camera_x + 0.2 * com_x

                    target_y, target_x = int(self.camera_y), int(self.camera_x)

                else:
                    # Universe is dead. Drift back to center.
                    target_y, target_x = self.height // 2, self.width // 2
                    self.camera_y, self.camera_x = target_y, target_x

                # 3. Crop Window (Clamping to bounds for now, todo: toroidal crop)
                # We limit the camera so the window stays inside the "Linear Memory"
                # Even though the universe is Toroidal, the Tensor Bridge is Linear/Fixed-Boundary for V1.

                half_obs = self.bridge.H // 2

                # Clamp center so window doesn't go out of bounds
                # min_y = half_obs, max_y = height - half_obs

                safe_cy = max(half_obs, min(self.height - half_obs, target_y))
                safe_cx = max(half_obs, min(self.width - half_obs, target_x))

                y1 = int(safe_cy - half_obs)
                y2 = int(y1 + self.bridge.H)
                x1 = int(safe_cx - half_obs)
                x2 = int(x1 + self.bridge.W)

                # Adjust if strictly smaller
                grid_crop = full_grid[y1:y2, x1:x2]

                # --- Step B: Observation (Collapse) ---
                # Convert to Tensor Network and measure Entropy
                tn = self.bridge.grid_to_tensor_state(grid_crop)

                # Explicit garbage collection for previous steps if needed
                # But Python scopes should handle it.

                entropy_data = self.bridge.compute_bipartition_entropy(tn)
                entropy = entropy_data["entropy"]

                # --- Step C: Cognition (Learn) ---
                # Teach Titans Memory

                # Handle Sentinel: -1.0 means Volume Law (Max Entropy / Chaos)
                # We interpret this as 1.0 (Maximum normalized complexity) for the neural net.

                # Normalization:
                # Max Entropy ~ Number of Qubits in Cut = self.obs_size
                # We want a [0, 1] scalar for the Sigmoid output.
                max_possible_ent = float(self.obs_size) * 0.7  # ln(2) approx 0.693

                learning_entropy = entropy
                if entropy < 0.0:
                    learning_entropy = 1.0  # Saturation
                else:
                    learning_entropy = min(1.0, entropy / max_possible_ent)

                # rule_bits is already np array
                surprise = self.navigator.probe_and_learn(rule_bits, learning_entropy)

                # --- Step D: Decision (Hallucinate) ---
                # Titans imagines neighbor rules and picks the most complex one
                next_rule_vec, pred_entropy = self.navigator.hallucinate_neighbors(
                    rule_bits
                )
                next_rule = bits_to_int(next_rule_vec)

                # --- Derived Metrics for Classification ---
                # 1. Dynamism (Pixel Delta) derived from last 2 frames
                # We need the second to last frame.
                if len(grid_history) > 1:
                    last_frame = grid_history[-1].astype(int)
                    prev_frame = grid_history[-2].astype(int)
                    dynamism = np.sum(np.abs(last_frame - prev_frame))
                else:
                    dynamism = 0

                # 2. Population (Active Cells)
                active_cells = np.sum(full_grid)

                # 3. Compression Ratio (Quick check using LZMA)
                import lzma

                # Pack grid to bytes for compression
                grid_bytes = full_grid.tobytes()
                compressed = lzma.compress(grid_bytes)
                compression_ratio = len(compressed) / len(grid_bytes)

                # 4. Wolfram Class Inference (Heuristic)
                wolfram_class = 0
                if entropy < 0.0:
                    wolfram_class = 3  # Chaos/Volume Law
                elif dynamism == 0:
                    wolfram_class = 1  # Frozen / Still Life (Class 1 or 2 depending on if it has structure, but mostly 1/2)
                elif dynamism < 20 and active_cells > 0:
                    # Low dynamism but not zero -> Simple Oscillator?
                    wolfram_class = 2  # Periodic
                elif entropy > 3.0:
                    wolfram_class = 3  # High entropy fire
                elif 0.1 <= entropy <= 3.0:
                    wolfram_class = 4  # Complex / Liquid

                # Refine Class 2 vs 4 based on "Boring Oscillation" vs "Walking"
                # If compression is extremely high (<0.05) it's likely Class 2/1
                if compression_ratio < 0.05 and wolfram_class == 4:
                    wolfram_class = 2  # Downgrade to Periodic if too simple

                # --- Visualization Update ---
                record = {
                    "rule": int(self.current_rule),
                    "rule_bits": [int(x) for x in rule_bits],
                    "entropy": float(entropy),
                    "surprise": float(surprise),
                    "pred": float(pred_entropy),
                    "epoch": epoch,
                    "cam": (int(target_y), int(target_x)),  # Log camera pos
                    # NEW METADATA
                    "wolfram_class": int(wolfram_class),
                    "dynamism": int(dynamism),
                    "active_cells": int(active_cells),
                    "compression_ratio": float(compression_ratio),
                }
                self.history.append(record)

                # --- Capture Golden Filaments ---
                # Criteria: Not Chaos (-1 / <0), Not Ice (<0.1)
                # Range: 0.1 <= entropy <= 3.0
                is_stable_liquid = 0.1 <= entropy <= 3.0
                if is_stable_liquid:
                    # Check if recently added to avoid duplicates from immediate neighbors?
                    # For now just log all unique rule ints
                    if not any(
                        f["rule"] == int(self.current_rule) for f in self.filaments
                    ):
                        self.filaments.append(record)

                self._update_display(
                    layout,
                    full_grid,
                    epoch,
                    rule_str,
                    entropy,
                    surprise,
                    (target_y, target_x),
                    len(self.filaments),
                )

                # Periodic Save (every 50 epochs)
                if epoch % 50 == 0:
                    self.save_results()

                # Move to next rule
                self.current_rule = next_rule

                # Explicit Garbage Collection to prevent OOM
                import gc

                gc.collect()

                time.sleep(0.5)  # Pause for visual stability and CPU cooling

        # Final Save
        self.save_results()

    def save_results(self):
        import json

        filename = "titans_history.json"

        # Basic serialization
        try:
            with open(filename, "w") as f:
                json.dump(self.history, f, indent=2)

            # Save Filaments
            if self.filaments:
                with open("golden_filaments.json", "w") as f:
                    json.dump(self.filaments, f, indent=2)
            # Update footer to show saved status logic would need access to layout, but skipping for simplicity
        except Exception as e:
            import sys

            print(
                f"Failed to save results to {filename}: {e}", file=sys.stderr
            )  # Don't crash UI on save fail

    def _create_layout(self):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3),
        )
        layout["main"].split_row(
            Layout(name="universe", ratio=2), Layout(name="brain", ratio=1)
        )
        return layout

    def _update_display(
        self,
        layout,
        grid,
        epoch,
        rule_str,
        entropy,
        surprise,
        cam_pos,
        filament_count=0,
    ):
        # Header
        cy, cx = cam_pos
        layout["header"].update(
            Panel(
                f"RULIAL NAVIGATOR v2.2 | Epoch: {epoch} | Rule: {rule_str} | Cam: ({cy},{cx}) | Filaments: {filament_count}",
                style="bold white on blue",
            )
        )

        # Universe (ASCII Grid)
        # Downsample grid for CLI viewing if huge
        view_h, view_w = grid.shape
        viz_str = ""
        # Limit view
        for r in range(min(view_h, 30)):
            row_str = ""
            for c in range(min(view_w, 60)):
                row_str += "█" if grid[r, c] else " "
            viz_str += row_str + "\n"

        layout["universe"].update(
            Panel(viz_str, title="Spacetime Projection", border_style="green")
        )

        # Brain (Metrics)
        table = Table(title="Titans Cognition")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Entanglement Entropy", f"{entropy:.6f}")
        table.add_row("Surprise (Loss)", f"{surprise:.6f}")
        table.add_row("History Length", f"{len(self.history)}")

        # Add classification based on entropy
        cls = "Unknown"
        if entropy < 0.0:
            cls = "Class 3 (Chaos/Volume Law) 🔥"
        elif entropy < 0.1:
            cls = "Class 1/2 (Ice)"
        elif entropy > 3.0:
            cls = "Class 3 (Fire)"
        else:
            cls = "Class 4 (Liquid/Life) 🌊"

        table.add_row("Topological Phase", cls)

        layout["brain"].update(
            Panel(table, title="Neural Memory", border_style="yellow")
        )
        layout["footer"].update(
            Panel("Press Ctrl+C to exit autonomous mode.", style="dim")
        )
