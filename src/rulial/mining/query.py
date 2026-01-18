"""
The Query Interface: Semantic Search for Computational Universes.

This module provides a high-level API for AI agents to query the Ruliad
for rules that satisfy specific functional requirements.

Example Queries:
  - find_logic_capable(): Find all rules that can perform computation.
  - find_with_gadgets(["WIRE", "EATER"]): Find rules with specific building blocks.
  - analyze_rule(rule_str): Full analysis of a single rule.
  - search(query_str): Natural language search (e.g., "I need a NOT gate").
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from rulial.mining.collider import Collider
from rulial.mining.extractor import ParticleMiner
from rulial.mining.synthesizer import Synthesizer

logger = logging.getLogger(__name__)


@dataclass
class RuleProfile:
    """Complete analysis of a rule's computational capabilities."""

    rule_str: str
    wolfram_class: int = 0
    particle_count: int = 0
    spaceship_count: int = 0
    is_logic_capable: bool = False
    supports_transmission: bool = False
    supports_annihilation: bool = False
    supports_creation: bool = False
    available_gadgets: List[str] = field(default_factory=list)

    def matches_requirements(self, required_gadgets: List[str]) -> bool:
        """Check if this rule satisfies a set of requirements."""
        return all(g in self.available_gadgets for g in required_gadgets)

    def as_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        lines = [
            f"Rule: {self.rule_str}",
            f"  Wolfram Class: {self.wolfram_class}",
            f"  Particles: {self.particle_count} ({self.spaceship_count} spaceships)",
            f"  Logic Capable: {self.is_logic_capable}",
            f"  Gadgets: {', '.join(self.available_gadgets) or 'None'}",
        ]
        return "\n".join(lines)


class RuliadQuery:
    """
    Query interface for the Ruliad Navigator.

    Usage:
        query = RuliadQuery()

        # Analyze a specific rule
        profile = query.analyze("B3/S23")
        print(profile.summary())

        # Search for rules with specific capabilities
        matches = query.find_with_gadgets(["WIRE", "NOT_GATE_TEMPLATE"])

        # Natural language query (simple pattern matching)
        matches = query.search("signal transmission")
    """

    def __init__(self, atlas_path: Optional[str] = None):
        """Initialize with optional path to atlas data."""
        self.atlas_path = atlas_path or "atlas_grid.json"
        self.cache: Dict[str, RuleProfile] = {}
        self._load_atlas()

    def _load_atlas(self):
        """Load pre-computed atlas data if available."""
        path = Path(self.atlas_path)
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                    # Pre-populate cache with class info
                    for entry in data:
                        rule = entry.get("rule_str", "")
                        if rule and rule not in self.cache:
                            self.cache[rule] = RuleProfile(
                                rule_str=rule,
                                wolfram_class=entry.get("wolfram_class", 0),
                            )
            except Exception as e:
                logger.debug(f"Could not load atlas file: {e}")

    def analyze(self, rule_str: str, force: bool = False) -> RuleProfile:
        """
        Perform full analysis of a rule.

        Args:
            rule_str: The rule to analyze (e.g., "B3/S23")
            force: If True, recompute even if cached
        """
        if rule_str in self.cache and not force:
            profile = self.cache[rule_str]
            if profile.particle_count > 0:  # Already fully analyzed
                return profile

        print(f"Analyzing {rule_str}...")

        # 1. Mine for particles
        miner = ParticleMiner(rule_str)
        particles = miner.mine(attempts=10, steps=300, density=0.1)

        particle_count = len(particles)
        spaceship_count = sum(1 for p in particles if p.is_spaceship)

        if not particles:
            profile = RuleProfile(
                rule_str=rule_str, particle_count=0, spaceship_count=0
            )
            self.cache[rule_str] = profile
            return profile

        # 2. Collide
        collider = Collider(rule_str, particles)
        table = collider.run_all_experiments()

        # 3. Synthesize
        particles_dict = {p.name: p for p in particles}
        synth = Synthesizer(rule_str, table, particles_dict)
        gadgets = synth.synthesize_all()

        profile = RuleProfile(
            rule_str=rule_str,
            particle_count=particle_count,
            spaceship_count=spaceship_count,
            is_logic_capable=table.is_logic_capable(),
            supports_transmission=table.supports_transmission(),
            supports_annihilation=table.supports_annihilation(),
            supports_creation=table.supports_creation(),
            available_gadgets=[g.name for g in gadgets],
        )

        self.cache[rule_str] = profile
        return profile

    def find_logic_capable(self, limit: int = 10) -> List[RuleProfile]:
        """Find rules that are logic capable from the atlas."""
        results = []
        for rule_str in list(self.cache.keys())[: limit * 2]:
            profile = self.analyze(rule_str)
            if profile.is_logic_capable:
                results.append(profile)
                if len(results) >= limit:
                    break
        return results

    def find_with_gadgets(
        self, required: List[str], limit: int = 10
    ) -> List[RuleProfile]:
        """Find rules that have specific gadgets available."""
        results = []
        for rule_str in list(self.cache.keys()):
            profile = self.analyze(rule_str)
            if profile.matches_requirements(required):
                results.append(profile)
                if len(results) >= limit:
                    break
        return results

    def search(self, query: str) -> List[RuleProfile]:
        """
        Simple semantic search for rules.

        Supports keywords: "logic", "wire", "eater", "not gate", "transmission"
        """
        query_lower = query.lower()

        # Map keywords to requirements
        requirements = []

        if (
            "wire" in query_lower
            or "transmission" in query_lower
            or "signal" in query_lower
        ):
            requirements.append("WIRE")
        if "eater" in query_lower or "absorb" in query_lower:
            requirements.append("EATER")
        if "not" in query_lower or "invert" in query_lower:
            requirements.append("NOT_GATE_TEMPLATE")
        if "delay" in query_lower:
            requirements.append("DELAY_LINE_10")

        if not requirements:
            # Default to logic-capable search
            return self.find_logic_capable()

        return self.find_with_gadgets(requirements)


def query_ruliad(request: str) -> str:
    """
    Main entry point for AI agents.

    Example:
        result = query_ruliad("I need a universe with signal transmission and absorption")
        print(result)
    """
    query = RuliadQuery()

    # Parse and execute query
    if "analyze" in request.lower() and (
        "b" in request.lower() or "s" in request.lower()
    ):
        # Extract rule string (e.g., "B3/S23")
        import re

        match = re.search(r"B\d+/S\d+", request, re.IGNORECASE)
        if match:
            rule_str = match.group().upper()
            profile = query.analyze(rule_str)
            return profile.summary()

    # Otherwise treat as semantic search
    results = query.search(request)

    if not results:
        return "No matching rules found in atlas. Try running a scan first."

    output = [f"Found {len(results)} matching rule(s):"]
    for profile in results:
        output.append(profile.summary())

    return "\n\n".join(output)


if __name__ == "__main__":
    # Demo query
    print("=" * 60)
    print("RULIAD QUERY INTERFACE")
    print("=" * 60)

    result = query_ruliad("Analyze B3/S23")
    print(result)
