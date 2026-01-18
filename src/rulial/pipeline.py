"""
Unified Ruliad Pipeline: Integrating All Components.

This module connects:
1. Titans (Exploration) → Finds promising rules via test-time learning
2. Atlas (Mapping) → Records findings and classifications
3. Mining (Extraction) → Analyzes particles and reactions
4. Query (Interface) → Answers questions about discovered physics

The pipeline can run in different modes:
- EXPLORE: Use Titans to actively search for Class 4 rules
- CATALOG: Batch analyze rules from an existing atlas
- QUERY: Answer questions about discovered physics
"""

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np

from rulial.compression.metrics import TelemetryAnalyzer
from rulial.engine.totalistic import Totalistic2DEngine
from rulial.mapper.atlas import Atlas
from rulial.mapper.topology import TopologyMapper
from rulial.mining.collider import Collider
from rulial.mining.extractor import ParticleMiner
from rulial.mining.synthesizer import Synthesizer
from rulial.navigator.titans import TitansNavigator
from rulial.quantum.bridge import TensorBridge

logger = logging.getLogger(__name__)


@dataclass
class UnifiedResult:
    """Complete analysis of a rule through the full pipeline."""

    rule_str: str
    wolfram_class: int
    compression_ratio: float
    betti_1: int
    entanglement_entropy: float
    particle_count: int
    spaceship_count: int
    is_logic_capable: bool
    available_gadgets: List[str]
    titans_surprise: float = 0.0

    def as_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        lines = [
            f"═══ {self.rule_str} ═══",
            f"  Wolfram Class: {self.wolfram_class}",
            f"  Compression: {self.compression_ratio:.5f}",
            f"  Topology: β₁={self.betti_1}",
            f"  Entanglement: {self.entanglement_entropy:.3f}",
            f"  Particles: {self.particle_count} ({self.spaceship_count} spaceships)",
            f"  Logic Capable: {'✅' if self.is_logic_capable else '❌'}",
            f"  Gadgets: {', '.join(self.available_gadgets) or 'None'}",
        ]
        if self.titans_surprise > 0.05:
            lines.append(f"  ⚡ Titans Surprise: {self.titans_surprise:.3f}")
        return "\n".join(lines)


class UnifiedPipeline:
    """
    The complete Ruliad Navigator pipeline.

    Integrates all components for automated discovery and analysis.
    """

    def __init__(
        self,
        atlas_path: str = "atlas_grid.json",
        catalog_path: str = "ruliad_catalog.json",
    ):
        self.atlas_path = Path(atlas_path)
        self.catalog_path = Path(catalog_path)

        # Initialize components
        self.analyzer = TelemetryAnalyzer()
        self.topo_mapper = TopologyMapper()

        # Titans (18-bit for 2D rules: 9 Born + 9 Survive)
        self.titans = TitansNavigator(rule_size_bits=18)

        # In-memory atlas and catalog
        self.atlas = Atlas()
        self.catalog: Dict[str, UnifiedResult] = {}

        # Load existing data if available
        self._load_atlas()
        self._load_catalog()

        print(
            f"Pipeline initialized. Atlas: {len(self.atlas.rules)} rules, Catalog: {len(self.catalog)} analyzed."
        )

    def _load_atlas(self):
        """Load pre-scanned atlas data."""
        if self.atlas_path.exists():
            try:
                with open(self.atlas_path) as f:
                    data = json.load(f)
                    for entry in data:
                        rule_str = entry.get("rule_str", "")
                        if rule_str:
                            # Create minimal telemetry for atlas recording
                            from rulial.compression.metrics import CompressionTelemetry

                            telemetry = CompressionTelemetry(
                                rigid_ratio_lzma=entry.get("compression_ratio", 0),
                                rigid_ratio_gzip=0,
                                neural_losses=[],
                                mean_loss=0,
                                loss_derivative=0,
                                shannon_entropy=0,
                            )
                            self.atlas.record(
                                rule=hash(rule_str) % 262144,  # 18-bit hash
                                telemetry=telemetry,
                                wolfram_class=entry.get("wolfram_class", 0),
                            )
                print(f"Loaded {len(data)} rules from atlas.")
            except Exception as e:
                logger.debug(f"Could not load atlas: {e}")

    def _load_catalog(self):
        """Load previously analyzed rules."""
        if self.catalog_path.exists():
            try:
                with open(self.catalog_path) as f:
                    data = json.load(f)
                    for entry in data:
                        rule_str = entry.get("rule_str", "")
                        if rule_str:
                            self.catalog[rule_str] = UnifiedResult(**entry)
                print(f"Loaded {len(self.catalog)} rules from catalog.")
            except Exception as e:
                logger.debug(f"Could not load catalog: {e}")

    def _save_catalog(self):
        """Save catalog to disk."""
        with open(self.catalog_path, "w") as f:
            data = [r.as_dict() for r in self.catalog.values()]
            json.dump(data, f, indent=2)

    def _rule_to_vector(self, rule_str: str) -> np.ndarray:
        """Convert B.../S... string to 18-bit binary vector for Titans."""
        born_bits = [0] * 9
        survive_bits = [0] * 9

        parts = rule_str.split("/")
        if len(parts) == 2:
            for c in parts[0]:
                if c.isdigit():
                    born_bits[int(c)] = 1
            for c in parts[1]:
                if c.isdigit():
                    survive_bits[int(c)] = 1

        return np.array(born_bits + survive_bits, dtype=np.float32)

    def analyze_rule(
        self, rule_str: str, use_titans: bool = True, deep_mining: bool = True
    ) -> UnifiedResult:
        """
        Full pipeline analysis of a single rule.

        Args:
            rule_str: The rule to analyze (e.g., "B3/S23")
            use_titans: Whether to update Titans memory
            deep_mining: Whether to run full particle mining
        """
        # Check cache first
        if rule_str in self.catalog:
            return self.catalog[rule_str]

        print(f"Analyzing {rule_str}...")

        # 1. Simulate
        engine = Totalistic2DEngine(rule_str)
        history = engine.simulate(64, 64, 200, "dense")
        spacetime = np.stack(history, axis=0)

        # 2. Compression Metrics
        flat = spacetime.reshape(spacetime.shape[0], -1)
        telemetry = self.analyzer.analyze(flat)

        # 3. Topology (TDA)
        topo = self.topo_mapper.compute_persistence(spacetime)
        betti_1 = topo.betti_1

        # 4. Classify
        cr = telemetry.rigid_ratio_lzma
        if cr < 0.0015:
            w_class = 1
        elif cr > 0.01:
            w_class = 3
        elif betti_1 > 50:
            w_class = 4
        else:
            w_class = 2

        # 5. Quantum Entanglement (if Class 4 candidate)
        entropy = 0.0
        if w_class >= 3:
            try:
                bridge = TensorBridge(height=16, width=16)
                # Sample middle frame
                mid_frame = history[len(history) // 2][:16, :16]
                psi = bridge.grid_to_tensor_state(mid_frame)
                result = bridge.compute_bipartition_entropy(psi)
                entropy = result.get("entropy", 0.0)
            except Exception as e:
                logger.debug(f"TensorBridge failed: {e}")

        # 6. Titans Learning (if enabled)
        surprise = 0.0
        if use_titans:
            rule_vec = self._rule_to_vector(rule_str)
            # Use normalized entropy as the target
            target = min(1.0, entropy) if entropy > 0 else cr * 10
            surprise = self.titans.probe_and_learn(rule_vec, target)

        # 7. Deep Mining (if enabled and Class 4)
        particle_count = 0
        spaceship_count = 0
        is_logic_capable = False
        gadgets = []

        if deep_mining and w_class == 4:
            try:
                miner = ParticleMiner(rule_str)
                particles = miner.mine(attempts=10, steps=300, density=0.1)
                particle_count = len(particles)
                spaceship_count = sum(1 for p in particles if p.is_spaceship)

                if particles:
                    collider = Collider(rule_str, particles)
                    table = collider.run_all_experiments()
                    is_logic_capable = table.is_logic_capable()

                    if is_logic_capable:
                        particles_dict = {p.name: p for p in particles}
                        synth = Synthesizer(rule_str, table, particles_dict)
                        gadget_list = synth.synthesize_all()
                        gadgets = [g.name for g in gadget_list]
            except Exception as e:
                logger.debug(f"Mining failed: {e}")

        # Build result
        result = UnifiedResult(
            rule_str=rule_str,
            wolfram_class=w_class,
            compression_ratio=cr,
            betti_1=betti_1,
            entanglement_entropy=entropy,
            particle_count=particle_count,
            spaceship_count=spaceship_count,
            is_logic_capable=is_logic_capable,
            available_gadgets=gadgets,
            titans_surprise=surprise,
        )

        # Cache
        self.catalog[rule_str] = result

        return result

    def explore(
        self, steps: int = 100, start_rule: str = "B3/S23"
    ) -> List[UnifiedResult]:
        """
        Use Titans to actively explore rule space.

        Returns a list of all analyzed rules.
        """
        results = []
        current_rule = start_rule
        current_vec = self._rule_to_vector(current_rule)

        print(f"Starting Titans exploration from {start_rule}...")

        for step in range(steps):
            # 1. Analyze current rule
            result = self.analyze_rule(current_rule, use_titans=True, deep_mining=True)
            results.append(result)
            print(f"[{step+1}/{steps}] {result.summary()}\n")

            # 2. Titans hallucinates next promising rule
            next_vec, predicted = self.titans.hallucinate_neighbors(
                current_vec, num_neighbors=10
            )

            # Convert back to rule string
            born_bits = next_vec[:9]
            survive_bits = next_vec[9:]
            b_str = "".join(str(i) for i, b in enumerate(born_bits) if b > 0.5)
            s_str = "".join(str(i) for i, b in enumerate(survive_bits) if b > 0.5)
            current_rule = f"B{b_str}/S{s_str}"
            current_vec = next_vec

            # Save periodically
            if (step + 1) % 10 == 0:
                self._save_catalog()

        self._save_catalog()
        return results

    def catalog_atlas(self, max_rules: int = 50) -> List[UnifiedResult]:
        """
        Analyze Class 4 candidates from the atlas.
        """
        results = []

        # Get Class 4 rules from atlas
        gold_rules = self.atlas.get_gold_filaments()
        print(f"Found {len(gold_rules)} Class 4 candidates in atlas.")

        # Also check the JSON directly for rule_str
        if self.atlas_path.exists():
            with open(self.atlas_path) as f:
                data = json.load(f)
                for entry in data:
                    if entry.get("wolfram_class", 0) == 4:
                        rule_str = entry.get("rule_str", "")
                        if rule_str and rule_str not in self.catalog:
                            print(f"Analyzing atlas candidate: {rule_str}")
                            result = self.analyze_rule(
                                rule_str, use_titans=True, deep_mining=True
                            )
                            results.append(result)
                            print(result.summary())
                            print()

                            if len(results) >= max_rules:
                                break

        self._save_catalog()
        return results

    def query(self, request: str) -> str:
        """
        Answer a natural language query about the catalog.
        """
        request_lower = request.lower()

        # Parse query type
        if "logic capable" in request_lower or "compute" in request_lower:
            matches = [r for r in self.catalog.values() if r.is_logic_capable]
            if matches:
                lines = [f"Found {len(matches)} logic-capable rule(s):"]
                for r in matches[:5]:
                    lines.append(r.summary())
                return "\n\n".join(lines)
            return "No logic-capable rules found in catalog."

        if (
            "gadget" in request_lower
            or "wire" in request_lower
            or "not gate" in request_lower
        ):
            gadget_name = None
            if "wire" in request_lower:
                gadget_name = "WIRE"
            elif "eater" in request_lower:
                gadget_name = "EATER"
            elif "not" in request_lower:
                gadget_name = "NOT_GATE_TEMPLATE"

            if gadget_name:
                matches = [
                    r
                    for r in self.catalog.values()
                    if gadget_name in r.available_gadgets
                ]
                if matches:
                    lines = [f"Found {len(matches)} rule(s) with {gadget_name}:"]
                    for r in matches[:5]:
                        lines.append(r.summary())
                    return "\n\n".join(lines)
                return f"No rules with {gadget_name} found in catalog."

        if "class 4" in request_lower or "complex" in request_lower:
            matches = [r for r in self.catalog.values() if r.wolfram_class == 4]
            if matches:
                lines = [f"Found {len(matches)} Class 4 rule(s):"]
                for r in matches[:5]:
                    lines.append(r.summary())
                return "\n\n".join(lines)
            return "No Class 4 rules found in catalog."

        if "analyze" in request_lower:
            # Extract rule string
            import re

            match = re.search(r"B\d*/S\d*", request, re.IGNORECASE)
            if match:
                rule_str = match.group().upper()
                result = self.analyze_rule(rule_str)
                return result.summary()

        return f"Catalog contains {len(self.catalog)} analyzed rules. Try: 'logic capable', 'class 4', 'analyze B3/S23'"


def main():
    """CLI interface for the unified pipeline."""
    import argparse

    parser = argparse.ArgumentParser(description="Unified Ruliad Pipeline")
    parser.add_argument(
        "--mode",
        choices=["explore", "catalog", "query", "analyze"],
        default="analyze",
        help="Operation mode",
    )
    parser.add_argument("--rule", type=str, default="B3/S23", help="Rule to analyze")
    parser.add_argument("--steps", type=int, default=20, help="Exploration steps")
    parser.add_argument("--query", type=str, default="", help="Query string")
    args = parser.parse_args()

    pipeline = UnifiedPipeline()

    if args.mode == "explore":
        results = pipeline.explore(steps=args.steps, start_rule=args.rule)
        print(f"\n{'='*60}")
        print(f"Exploration complete. Analyzed {len(results)} rules.")
        logic_capable = sum(1 for r in results if r.is_logic_capable)
        print(f"Logic-capable rules found: {logic_capable}")

    elif args.mode == "catalog":
        results = pipeline.catalog_atlas()
        print(f"\n{'='*60}")
        print(f"Cataloging complete. Analyzed {len(results)} Class 4 candidates.")

    elif args.mode == "query":
        if args.query:
            result = pipeline.query(args.query)
            print(result)
        else:
            print("Usage: --mode query --query 'your question'")

    else:  # analyze
        result = pipeline.analyze_rule(args.rule)
        print(result.summary())


if __name__ == "__main__":
    main()
