"""
The Synthesizer: Constructing Logic Gates from Particle Interactions.

Given a Rule's Reaction Table (from the Collider), this module attempts to
synthesize specific logical gadgets.

Approach:
1. Define abstract "gadget templates" (e.g., NOT Gate = Absorber + Emitter).
2. Match templates to discovered reactions.
3. Output concrete configurations (grid + particle placements).

Example Gadgets:
  - WIRE: A path where a Glider can travel unobstructed.
  - EATER: A Still Life that absorbs a Glider without changing.
  - NOT GATE: Signal In -> (No Signal Out) OR (No Signal In -> Signal Out).
    Typically implemented as Glider striking an Eater configuration.
  - AND GATE: Two Glider streams that only produce output if both arrive.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np

from rulial.engine.totalistic import Totalistic2DEngine
from rulial.mining.collider import ReactionTable
from rulial.mining.extractor import Particle


@dataclass
class Gadget:
    """A functional component in a cellular automaton."""

    name: str
    rule_str: str
    description: str
    particles_required: List[str]
    configuration: Optional[np.ndarray] = None  # The grid setup

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "rule": self.rule_str,
            "description": self.description,
            "particles": self.particles_required,
            "configuration_shape": (
                self.configuration.shape if self.configuration is not None else None
            ),
        }


class Synthesizer:
    """Logic Gate Constructor from Reaction Tables."""

    def __init__(
        self, rule_str: str, table: ReactionTable, particles: Dict[str, Particle]
    ):
        self.rule_str = rule_str
        self.table = table
        self.particles = particles
        self.engine = Totalistic2DEngine(rule_str)

    def synthesize_wire(self) -> Optional[Gadget]:
        """Find a particle that can transmit signals."""
        for r in self.table.reactions:
            if r.outcome_type == "transmission" and r.reactant_b == "Nothing":
                # Found a transmitter
                return Gadget(
                    name="WIRE",
                    rule_str=self.rule_str,
                    description=f"Signal carrier: {r.reactant_a}. Place in empty space to transmit.",
                    particles_required=[r.reactant_a],
                )
        return None

    def synthesize_eater(self) -> Optional[Gadget]:
        """Find a configuration that absorbs signals."""
        for r in self.table.reactions:
            if (
                r.outcome_type in ("absorption", "annihilation")
                and r.product_count <= 1
            ):
                # Still life or absorber
                return Gadget(
                    name="EATER",
                    rule_str=self.rule_str,
                    description=f"Signal absorber: {r.reactant_a} + {r.reactant_b} -> {r.product_count} debris.",
                    particles_required=[r.reactant_a, r.reactant_b],
                )
        return None

    def synthesize_not_gate(self) -> Optional[Gadget]:
        """
        NOT Gate Heuristic:
        Requires: A transmitter (Glider) and an Eater (Block that absorbs).
        Mechanism: A running "clock" Glider is blocked by an input Glider.
        If input is present, clock is absorbed -> No output.
        If input is absent, clock passes -> Output.

        This is complex to fully automate, so we provide a template.
        """
        wire = self.synthesize_wire()
        eater = self.synthesize_eater()

        if wire and eater:
            return Gadget(
                name="NOT_GATE_TEMPLATE",
                rule_str=self.rule_str,
                description=(
                    f"NOT Gate possible. Use {wire.particles_required[0]} as signal. "
                    f"Use {eater.particles_required[1]} as eater. "
                    "Configure so input Glider stream annihilates clock Glider stream."
                ),
                particles_required=wire.particles_required + eater.particles_required,
            )
        return None

    def synthesize_delay_line(self, delay_ticks: int = 10) -> Optional[Gadget]:
        """
        Delay Line: A signal that takes N ticks to traverse.
        Implementation: Just a long wire (empty space).
        """
        wire = self.synthesize_wire()
        if wire:
            return Gadget(
                name=f"DELAY_LINE_{delay_ticks}",
                rule_str=self.rule_str,
                description=f"Delay of ~{delay_ticks} ticks. Use {wire.particles_required[0]} over empty grid.",
                particles_required=wire.particles_required,
            )
        return None

    def synthesize_all(self) -> List[Gadget]:
        """Attempt to synthesize all known gadget types."""
        gadgets = []

        wire = self.synthesize_wire()
        if wire:
            gadgets.append(wire)

        eater = self.synthesize_eater()
        if eater:
            gadgets.append(eater)

        not_gate = self.synthesize_not_gate()
        if not_gate:
            gadgets.append(not_gate)

        delay = self.synthesize_delay_line(10)
        if delay:
            gadgets.append(delay)

        return gadgets

    def summary(self) -> str:
        gadgets = self.synthesize_all()
        lines = [f"Synthesizable Gadgets for {self.rule_str}:"]
        if not gadgets:
            lines.append("  No gadgets could be synthesized.")
        else:
            for g in gadgets:
                lines.append(f"  - {g.name}: {g.description}")
        return "\n".join(lines)


def synthesize_for_rule(rule_str: str) -> str:
    """
    High-level API: Analyze a rule and report what logic gadgets can be built.
    """
    from rulial.mining.collider import Collider
    from rulial.mining.extractor import ParticleMiner

    print(f"Synthesizing gadgets for {rule_str}...")

    # 1. Mine
    miner = ParticleMiner(rule_str)
    particles_list = miner.mine(attempts=10, steps=300, density=0.1)
    particles = {p.name: p for p in particles_list}

    if not particles:
        return f"No particles found for {rule_str}. Cannot synthesize."

    # 2. Collide
    collider = Collider(rule_str, particles_list)
    table = collider.run_all_experiments()

    # 3. Synthesize
    synth = Synthesizer(rule_str, table, particles)
    return synth.summary()


if __name__ == "__main__":
    result = synthesize_for_rule("B3/S23")
    print(result)
