import time
import numpy as np
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console
from rich import box

from rulial.engine.totalistic import Totalistic2DEngine
from rulial.quantum.bridge import TensorBridge
from rulial.navigator.titans import TitansNavigator

def int_to_bits(n: int, num_bits: int) -> np.ndarray:
    # Ensure binary string is padded
    bin_str = format(n, f'0{num_bits}b')
    # If n exceeds num_bits, it might be longer, handle optional truncation or strictness
    # For now assume n fits
    return np.array([int(x) for x in bin_str], dtype=np.float32)

def bits_to_int(bits: np.ndarray) -> int:
    return int("".join(str(int(b)) for b in bits), 2)

class RulialProbe2D:
    def __init__(self, width=64, height=64, steps=100, seed_rule=224, obs_window=24):
        # 1. Physics (The Universe)
        self.width = width
        self.height = height
        self.steps = steps
        
        # 2. Observer (The Quantum Bridge)
        # CRITICAL OPTIMIZATION:
        # We define an "Observer Window" to keep contraction tractable.
        # User requested aggressive RAM usage:
        # 16x16 = Low RAM (~6GB)
        # 24x24 = Medium/High
        # 32x32 = Extreme
        self.obs_size = obs_window 
        self.bridge = TensorBridge(max(self.obs_size, min(height, self.obs_size)), max(self.obs_size, min(width, self.obs_size)))
        # Actually 16x16 is 256 tensors. Contraction is still hard if dense.
        # But for Area Law states (Game of Life), it's trivial.
        # 12x12 might be safer if user is crashing on 64GB.
        # Let's stick to 16x16 but strict area law checks.
        self.bridge = TensorBridge(max(self.obs_size, min(height, 16)), max(self.obs_size, min(width, 16)))
        # Note: We will crop the grid to this size.
        
        # 3. Cognition (The Brain)
        # Input dim is 18 bits for the rule code
        self.navigator = TitansNavigator(rule_size_bits=18)
        
        self.current_rule = seed_rule
        self.history = []

    def run_loop(self, max_epochs=1000):
        layout = self._create_layout()
        
        # Using rich Live context
        with Live(layout, refresh_per_second=4, screen=True) as live:
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
                grid_history = engine.simulate(self.height, self.width, self.steps, "random") 
                
                # Use the last frame for observation
                full_grid = grid_history[-1]
                
                # --- CROP GRID FOR OBSERVER ---
                # Center crop
                cy, cx = self.height // 2, self.width // 2
                half_obs = self.bridge.H // 2 # Use bridge dims
                
                # Ensure bounds
                y1 = max(0, cy - half_obs)
                y2 = min(self.height, y1 + self.bridge.H)
                x1 = max(0, cx - half_obs)
                x2 = min(self.width, x1 + self.bridge.W)
                
                # Adjust if strictly smaller
                grid_crop = full_grid[y1:y2, x1:x2]
                
                # --- Step B: Observation (Collapse) ---
                # Convert to Tensor Network and measure Entropy
                tn = self.bridge.grid_to_tensor_state(grid_crop)
                
                # Explicit garbage collection for previous steps if needed
                # But Python scopes should handle it.
                
                entropy_data = self.bridge.compute_bipartition_entropy(tn)
                entropy = entropy_data['entropy']
                
                # --- Step C: Cognition (Learn) ---
                # Teach Titans Memory
                
                # Handle Sentinel: -1.0 means Volume Law (Max Entropy / Chaos)
                # We interpret this as 1.0 (Maximum normalized complexity) for the neural net.
                
                # Normalization:
                # Max Entropy ~ Number of Qubits in Cut = self.obs_size
                # We want a [0, 1] scalar for the Sigmoid output.
                max_possible_ent = float(self.obs_size) * 0.7 # ln(2) approx 0.693
                
                learning_entropy = entropy
                if entropy < 0.0:
                    learning_entropy = 1.0 # Saturation
                else:
                    learning_entropy = min(1.0, entropy / max_possible_ent)
                    
                # rule_bits is already np array
                surprise = self.navigator.probe_and_learn(rule_bits, learning_entropy)
                
                # --- Step D: Decision (Hallucinate) ---
                # Titans imagines neighbor rules and picks the most complex one
                next_rule_vec, pred_entropy = self.navigator.hallucinate_neighbors(rule_bits)
                next_rule = bits_to_int(next_rule_vec)
                
                # --- Visualization Update ---
                record = {
                    "rule": int(self.current_rule),
                    "rule_bits": [int(x) for x in rule_bits],
                    "entropy": float(entropy),
                    "surprise": float(surprise),
                    "pred": float(pred_entropy),
                    "epoch": epoch
                }
                self.history.append(record)
                
                self._update_display(layout, full_grid, epoch, rule_str, entropy, surprise)
                
                # Periodic Save (every 50 epochs)
                if epoch % 50 == 0:
                    self.save_results()
                
                # Move to next rule
                self.current_rule = next_rule
                time.sleep(0.1) # Brief pause for visual stability
        
        # Final Save
        self.save_results()

    def save_results(self):
        import json
        from datetime import datetime
        
        filename = "titans_history.json"
        
        # Basic serialization
        try:
            with open(filename, "w") as f:
                json.dump(self.history, f, indent=2)
            # Update footer to show saved status logic would need access to layout, but skipping for simplicity
        except Exception as e:
            pass # Don't crash UI on save fail

    def _create_layout(self):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        layout["main"].split_row(
            Layout(name="universe", ratio=2),
            Layout(name="brain", ratio=1)
        )
        return layout

    def _update_display(self, layout, grid, epoch, rule_str, entropy, surprise):
        # Header
        layout["header"].update(
            Panel(f"RULIAL NAVIGATOR v2.0 | Epoch: {epoch} | Active Rule: {rule_str}", 
                  style="bold white on blue")
        )
        
        # Universe (ASCII Grid)
        # Downsample grid for CLI viewing if huge
        view_h, view_w = grid.shape
        viz_str = ""
        # Limit view
        for r in range(min(view_h, 30)):
            row_str = ""
            for c in range(min(view_w, 60)):
                row_str += "█" if grid[r,c] else " "
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
        if entropy < 0.1: cls = "Class 1/2 (Ice)"
        elif entropy > 3.0: cls = "Class 3 (Fire)"
        else: cls = "Class 4 (Liquid/Life) 🌊"
        
        table.add_row("Topological Phase", cls)
        
        layout["brain"].update(Panel(table, title="Neural Memory", border_style="yellow"))
        layout["footer"].update(Panel("Press Ctrl+C to exit autonomous mode.", style="dim"))
