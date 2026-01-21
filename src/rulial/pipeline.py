"""
Unified Ruliad Pipeline: The Discovery Engine.

Integrates:
1. Titans (Exploration) - Learned navigation
2. LLL (Filter) - Combinatorial complexity filter
3. Sheaf (Physics) - GPU-accelerated cohomology
4. Atlas (Persistence) - SQLite storage

This pipeline replaces all standalone runners.
"""

import logging
import time
from pathlib import Path

import numpy as np

from rulial.engine.totalistic import Totalistic2DEngine
from rulial.mapper.atlas import Atlas
from rulial.mapper.fractal import compute_fractal_dimension
from rulial.mapper.lll_complexity import analyze_rule_combinatorially
from rulial.mapper.sheaf_gpu import analyze_rule_gpu
from rulial.mining.collider import Collider
from rulial.mining.extractor import ParticleMiner
from rulial.navigator.compass import CompressionCompass
from rulial.navigator.titans import TitansNavigator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rulial")


class UnifiedPipeline:
    def __init__(self, db_path: str = "data/atlas_full_v6_gpu.db"):
        self.db_path = db_path
        self.atlas = Atlas(db_path)

        # Initialize Titans
        self.titans = TitansNavigator(rule_size_bits=18)
        self.titans_path = Path("data/titans_memory.pt")

        # AIR Protocol Components
        self.compass = CompressionCompass()
        # Miners are instantiated per rule, but we can keep refs if needed

        # Load persistent state if available
        if self.titans_path.exists():
            self.titans.load(str(self.titans_path))

        self.known_rules = set()

    def bootstrap_titans(self):
        """
        Train Titans on the entire history of the Atlas.
        This allows the agent to 'wake up' with knowledge of the 36h scan.
        """
        print(f"🧠 Bootstrapping Titans from {self.db_path}...")

        # Fetch all rules with harmonic_overlap (our target metric)
        cursor = self.atlas.conn.execute(
            "SELECT rule_str, harmonic_overlap FROM explorations WHERE harmonic_overlap IS NOT NULL AND harmonic_overlap != 0"
        )
        rows = cursor.fetchall()

        if not rows:
            print("No training data found in Atlas.")
            return

        print(f"Found {len(rows)} training examples.")

        # Populate known rules set for fast skipping
        self.known_rules = set()

        vectors = []
        targets = []

        for row in rows:
            rule_str = row[0]
            overlap = row[1]
            vec = self._rule_to_vector(rule_str)
            vectors.append(vec)
            targets.append(overlap)

            # Canonicalize key for cache
            # This ensures "B3/S23" matches exactly what _vector_to_rule produces
            canonical_rule = self._vector_to_rule(vec)
            self.known_rules.add(canonical_rule)

        vectors = np.array(vectors)
        targets = np.array(targets)

        # Train
        print("Training Titans neural memory...")
        self.titans.train_batch(vectors, targets, epochs=3)  # Quick epochs
        self.titans.save(str(self.titans_path))
        print("✅ Titans bootstrapped and saved.")

    def run_continuously(self, steps: int = 1000000, start_rule: str = "B3/S23"):
        """
        The Main Loop.
        1. Hallucinate next rule (Titans)
        2. LLL Filter (Reject boring)
        3. Physics (Sheaf + Fractal)
        4. Learn (Titans update)
        5. Persist
        """
        print("🚀 Starting Continuous Exploration Engine")
        print(f"   Database: {self.db_path}")
        print("   Titans: Active")

        # Start vector
        current_vec = self._rule_to_vector(start_rule)

        # Stats
        start_time = time.time()
        scanned = 0
        goldilocks = 0

        consecutive_skips = 0

        for step in range(steps):
            # 1. Titans suggests next rule
            # Hallucinate 20 neighbors, pick best
            next_vec, predicted_h = self.titans.hallucinate_neighbors(
                current_vec, num_neighbors=20
            )
            rule_str = self._vector_to_rule(next_vec)

            # 2. LLL Combinatorial Filter
            # Fast check before simulation
            try:
                # SKIP CHECK: If we already know this rule, don't simulate it again.
                if rule_str in self.known_rules:
                    consecutive_skips += 1

                    # STUCK DETECTION: If we skip too many, JUMP.
                    if consecutive_skips > 50:
                        if consecutive_skips % 50 == 0:
                            print(
                                f"\r[{step}] 🌀 STUCK in known space ({consecutive_skips} skips). Teleporting to random rule...",
                                end="",
                                flush=True,
                            )

                        # Generate completely random rule
                        current_vec = np.random.randint(0, 2, 18).astype(np.float32)
                        # Or verify it's not known?
                        while self._vector_to_rule(current_vec) in self.known_rules:
                            current_vec = np.random.randint(0, 2, 18).astype(np.float32)
                        continue

                    # Metric for user
                    sys_print = f"\r[{step}] {rule_str:<18} ♻️  Known In DB. Skipping... (Seq: {consecutive_skips})"
                    print(sys_print, end="", flush=True)
                    current_vec = next_vec
                    continue

                # Reset counter if found new
                consecutive_skips = 0

                lll = analyze_rule_combinatorially(rule_str)
                # Keep if p_active is in "Goldilocks Zone" ~[0.15, 0.55]
                if not (0.15 <= lll.p_active <= 0.55):
                    # Reject without simulation
                    current_vec = next_vec
                    continue
            except Exception:
                current_vec = next_vec
                continue

            # 3. Physics & Sheaf (GPU)
            try:
                # GPU Sheaf Analysis
                sheaf_res = analyze_rule_gpu(
                    rule_str, grid_size=48, steps=100, device="cuda"
                )

                # Fractal Dimension
                engine = Totalistic2DEngine(rule_str)
                history = engine.simulate(48, 48, 100, "random", density=0.3)
                final_grid = history[-1]
                fractal_dim = compute_fractal_dimension(final_grid)
                equilibrium_density = final_grid.sum() / (48 * 48)

            except Exception:
                # logger.error(f"Physics error on {rule_str}: {e}")
                current_vec = next_vec
                continue

            # 4. Titans Learn
            # Use Harmonic Overlap as the learning signal
            surprise = self.titans.probe_and_learn(next_vec, sheaf_res.harmonic_overlap)

            # 5. Mining & Validation (The "Scientific" Phase)
            # Only mine if Physics or LLL suggests it's worth it
            particle_count = 0
            interaction_count = 0
            avg_mass = 0.0
            max_vel = 0.0
            is_logic = False
            betti_1 = 0  # GPU Sheaf doesn't return betti? It returns h1_dim?
            # Reviewing sheaf_gpu. analyze_rule_gpu returns a named tuple/dataclass?
            # It returns SheafAnalysis which has h1_dim.
            betti_1 = getattr(sheaf_res, "h1_dim", 0)

            # Trigger Mining if:
            # - Goldilocks (harmonic overlap)
            # - OR LLL promising
            # - OR Compass says Interesting (Class 4 Candidate) - WAIT, we didn't run Compass yet!

            # Run Compass on History
            compass_reading = self.compass.measure(rule_str, history)

            should_mine = (
                (0.2 <= sheaf_res.harmonic_overlap <= 0.7)
                or (0.15 <= lll.p_active <= 0.55)
                or compass_reading.is_interesting
            )

            if should_mine:
                try:
                    # A. Particles
                    miner = ParticleMiner(rule_str)
                    particles = miner.mine(attempts=5, steps=200)  # Quick mine
                    particle_count = len(particles)

                    if particles:
                        avg_mass = np.mean([np.sum(p.pattern) for p in particles])
                        max_vel = max([np.linalg.norm(p.velocity) for p in particles])

                        # B. Collisions
                        collider = Collider(rule_str)
                        # Pre-inject found particles to avoid re-mining?
                        collider.particles = {p.uuid: p for p in particles}
                        # Run experiments
                        table = collider.run_all_experiments()
                        interaction_count = len(table.reactions)

                        # Logic check: Do we have gliders interacting?
                        # Simple proxy: if we have interactions, we have logic potential
                        is_logic = interaction_count > 0
                except Exception as e:
                    logger.error(f"Mining error on {rule_str}: {e}")

            # 6. Persist
            is_goldilocks = 0.3 <= sheaf_res.harmonic_overlap <= 0.6
            w_class = (
                4
                if (is_goldilocks or particle_count > 0)
                else (2 if equilibrium_density > 0.0 else 1)
            )
            if equilibrium_density > 0.0 and not is_goldilocks and particle_count == 0:
                w_class = 3  # Chaos/Periodic generic

            # Simple manual insertion to avoid circular dependency or old Atlas code issues
            try:
                # Basic Explorations Table
                self.atlas.record_from_dict(
                    {
                        "rule_str": rule_str,
                        "wolfram_class": w_class,
                        "harmonic_overlap": sheaf_res.harmonic_overlap,
                        "monodromy": sheaf_res.monodromy_index,
                        "spectral_gap": sheaf_res.spectral_gap,
                        "sheaf_phase": sheaf_res.sheaf_type,
                        "equilibrium_density": equilibrium_density,
                        "fractal_dimension": fractal_dim,
                        "is_condensate": False,
                    }
                )

                # Scientific Metrics Table (AIR)
                self.atlas.conn.execute(
                    """
                    INSERT OR REPLACE INTO scientific_metrics (
                        rule_str,
                        compression_ratio_start, compression_ratio_end, compression_progress, logical_depth,
                        betti_1, lll_score,
                        particle_count, avg_particle_mass, max_particle_velocity,
                        interaction_count, is_logic_capable, oligon_density
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        rule_str,
                        compass_reading.compression_ratio_start,
                        compass_reading.compression_ratio_end,
                        compass_reading.compression_progress,
                        compass_reading.logical_depth_proxy,
                        betti_1,
                        lll.lll_score,
                        particle_count,
                        avg_mass,
                        max_vel,
                        interaction_count,
                        is_logic,
                        equilibrium_density,  # Proxy for oligon density if no detailed count
                    ),
                )

                # Add to local cache to prevent re-scanning in this session
                self.known_rules.add(self._vector_to_rule(next_vec))

                # Periodically save weights
                if step % 50 == 0:
                    self.titans.save(str(self.titans_path))

            except Exception as e:
                logger.error(f"DB Error: {e}")

            # Update loop state
            current_vec = next_vec
            scanned += 1
            if is_goldilocks:
                goldilocks += 1

            # Console output
            elapsed = time.time() - start_time
            rate = scanned / elapsed

            status_icon = (
                "🌟" if is_goldilocks else ("🧪" if particle_count > 0 else "•")
            )
            print(
                f"\r[{step}] {rule_str:<18} {status_icon} H={sheaf_res.harmonic_overlap:.2f} S={surprise:.3f} P={particle_count} Rate={rate:.1f}/s {compass_reading.status_msg[:15]}...",
                end="",
                flush=True,
            )

    def _rule_to_vector(self, rule_str: str) -> np.ndarray:
        """Convert B/S rule string to 18-bit binary vector."""
        digits = "012345678"
        vector = np.zeros(18, dtype=np.float32)
        parts = rule_str.upper().replace(" ", "").split("/")
        for part in parts:
            if part.startswith("B"):
                for i, d in enumerate(digits):
                    if d in part:
                        vector[i] = 1.0
            elif part.startswith("S"):
                for i, d in enumerate(digits):
                    if d in part:
                        vector[9 + i] = 1.0
        return vector

    def _vector_to_rule(self, vector: np.ndarray) -> str:
        """Convert 18-bit binary vector to B/S rule string."""
        digits = "012345678"
        b = "".join(digits[i] for i in range(9) if vector[i] > 0.5)
        s = "".join(digits[i] for i in range(9) if vector[9 + i] > 0.5)
        return f"B{b}/S{s}"
