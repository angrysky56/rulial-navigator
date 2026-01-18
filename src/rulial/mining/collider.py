"""
The Collider: Automated Discovery of Particle Interaction Rules (The Algebra of a Universe).

Given a set of Particles extracted by the Miner, this module systematically
collides them to discover the interaction algebra of the rule.

Output: A Reaction Table that can be used to determine if a rule supports
specific logical operations (e.g., signal transmission, annihilation, logic gates).

Example Reactions:
  - Glider + Nothing -> Glider (Wire/Transmission)
  - Glider + Block -> 0 (Absorption/Eater)
  - Glider A + Glider B -> Block (Memory Write)
  - Glider A + Glider B (at angle) -> Glider C (Reflection/OR Gate Candidate)
"""

from dataclasses import dataclass, field
from typing import List

import numpy as np
from scipy.ndimage import label

from rulial.engine.totalistic import Totalistic2DEngine
from rulial.mining.extractor import Particle, ParticleMiner


@dataclass
class Reaction:
    """Result of a collision experiment."""

    reactant_a: str  # Name of first particle
    reactant_b: str  # Name of second particle (or "Nothing")
    product_count: int  # Number of particles after collision
    product_names: List[str]  # Names of resulting particles
    outcome_type: (
        str  # 'transmission', 'annihilation', 'creation', 'reflection', 'unknown'
    )

    def __repr__(self):
        products = " + ".join(self.product_names) if self.product_names else "0"
        return (
            f"{self.reactant_a} + {self.reactant_b} -> {products} ({self.outcome_type})"
        )


@dataclass
class ReactionTable:
    """The Algebra of a Rule."""

    rule_str: str
    reactions: List[Reaction] = field(default_factory=list)

    def supports_transmission(self) -> bool:
        """Can signals propagate?"""
        return any(r.outcome_type == "transmission" for r in self.reactions)

    def supports_annihilation(self) -> bool:
        """Can signals cancel?"""
        return any(r.outcome_type == "annihilation" for r in self.reactions)

    def supports_creation(self) -> bool:
        """Can collisions create more particles?"""
        return any(r.outcome_type == "creation" for r in self.reactions)

    def is_logic_capable(self) -> bool:
        """Minimum requirement for logic: transmission + some interaction."""
        return self.supports_transmission() and (
            self.supports_annihilation() or self.supports_creation()
        )

    def summary(self) -> str:
        lines = [f"Reaction Table for {self.rule_str}:"]
        for r in self.reactions:
            lines.append(f"  {r}")
        lines.append("\nCapabilities:")
        lines.append(f"  Transmission: {self.supports_transmission()}")
        lines.append(f"  Annihilation: {self.supports_annihilation()}")
        lines.append(f"  Creation: {self.supports_creation()}")
        lines.append(f"  LOGIC CAPABLE: {self.is_logic_capable()}")
        return "\n".join(lines)


class Collider:
    """Particle Accelerator for Cellular Automata."""

    def __init__(self, rule_str: str, particles: List[Particle]):
        self.rule_str = rule_str
        self.engine = Totalistic2DEngine(rule_str)
        self.particles = {p.name: p for p in particles}
        self.miner = ParticleMiner(rule_str)  # For identifying products

    def run_all_experiments(self) -> ReactionTable:
        """Run standard collision experiments."""
        table = ReactionTable(rule_str=self.rule_str)

        # 1. Test each particle alone (transmission test)
        for _, particle in self.particles.items():
            if particle.is_spaceship:
                reaction = self._test_transmission(particle)
                table.reactions.append(reaction)

        # 2. Test pairs (head-on collisions)
        spaceships = [p for p in self.particles.values() if p.is_spaceship]
        for i, p1 in enumerate(spaceships):
            for p2 in spaceships[i:]:  # Include self-collisions
                reaction = self._test_head_on(p1, p2)
                table.reactions.append(reaction)

        # 3. Test spaceship vs still life (eater test)
        still_lifes = [p for p in self.particles.values() if not p.is_spaceship]
        for ship in spaceships:
            for block in still_lifes:
                reaction = self._test_eater(ship, block)
                table.reactions.append(reaction)

        return table

    def _test_transmission(self, particle: Particle) -> Reaction:
        """Does a spaceship survive on its own?"""
        size = 64
        steps = 100

        grid = np.zeros((size, size), dtype=np.uint8)
        ph, pw = particle.pattern.shape

        # Place in center
        r, c = size // 2, size // 2
        grid[r : r + ph, c : c + pw] = particle.pattern

        # Simulate
        history = self.engine.simulate(
            size, size, steps, init_condition="custom", custom_grid=grid
        )

        # Analyze end state
        structure = np.ones((3, 3), dtype=np.int8)
        final = history[-1]
        labeled, num = label(final, structure=structure)

        if num == 1:
            return Reaction(
                reactant_a=particle.name,
                reactant_b="Nothing",
                product_count=1,
                product_names=[particle.name],
                outcome_type="transmission",
            )
        elif num == 0:
            return Reaction(
                reactant_a=particle.name,
                reactant_b="Nothing",
                product_count=0,
                product_names=[],
                outcome_type="decay",
            )
        else:
            return Reaction(
                reactant_a=particle.name,
                reactant_b="Nothing",
                product_count=num,
                product_names=["unknown"] * num,
                outcome_type="fission",
            )

    def _test_head_on(self, p1: Particle, p2: Particle) -> Reaction:
        """Collide two spaceships head-on."""
        size = 64
        steps = 200

        grid = np.zeros((size, size), dtype=np.uint8)

        # Place p1 on left, moving right (+dx)
        # Place p2 on right, moving left (-dx) - need to flip it
        # Assume standard glider moves (+1, +1).
        # For head-on, we need opposite velocities.

        ph1, pw1 = p1.pattern.shape
        ph2, pw2 = p2.pattern.shape

        # Place p1 at left
        r1, c1 = size // 2, 10
        grid[r1 : r1 + ph1, c1 : c1 + pw1] = p1.pattern

        # Place p2 at right (flipped to face left if possible)
        # Simple flip: horizontal flip
        p2_flipped = np.fliplr(p2.pattern)
        r2, c2 = size // 2, size - 10 - pw2
        grid[r2 : r2 + ph2, c2 : c2 + pw2] = p2_flipped

        # Simulate
        history = self.engine.simulate(
            size, size, steps, init_condition="custom", custom_grid=grid
        )

        # Analyze
        structure = np.ones((3, 3), dtype=np.int8)
        final = history[-1]
        labeled, num = label(final, structure=structure)

        if num == 0:
            outcome = "annihilation"
        elif num == 1:
            outcome = "merge"
        elif num == 2:
            # Check if they passed through each other
            outcome = "reflection"  # or "passthrough"
        elif num > 2:
            outcome = "creation"
        else:
            outcome = "unknown"

        return Reaction(
            reactant_a=p1.name,
            reactant_b=p2.name,
            product_count=num,
            product_names=["debris"] * num if num > 0 else [],
            outcome_type=outcome,
        )

    def _test_eater(self, ship: Particle, block: Particle) -> Reaction:
        """Does a still life 'eat' a spaceship?"""
        size = 64
        steps = 200

        grid = np.zeros((size, size), dtype=np.uint8)

        sh, sw = ship.pattern.shape
        bh, bw = block.pattern.shape

        # Place ship on left
        r1, c1 = size // 2, 10
        grid[r1 : r1 + sh, c1 : c1 + sw] = ship.pattern

        # Place block in its path
        r2, c2 = size // 2, size // 2
        grid[r2 : r2 + bh, c2 : c2 + bw] = block.pattern

        # Simulate
        history = self.engine.simulate(
            size, size, steps, init_condition="custom", custom_grid=grid
        )

        # Analyze
        structure = np.ones((3, 3), dtype=np.int8)
        final = history[-1]
        labeled, num = label(final, structure=structure)

        # Check if block survived alone
        if num == 1:
            # The block ate the glider (or glider passed)
            # Need more sophisticated check
            outcome = "absorption"  # Eater behavior
        elif num == 0:
            outcome = "mutual_annihilation"
        elif num == 2:
            outcome = "passthrough"  # Both survived
        else:
            outcome = "unknown"

        return Reaction(
            reactant_a=ship.name,
            reactant_b=block.name,
            product_count=num,
            product_names=["debris"] * num if num > 0 else [],
            outcome_type=outcome,
        )


def analyze_rule(rule_str: str) -> ReactionTable:
    """
    High-level API: Given a rule string, extract its physics and interaction algebra.
    """
    print(f"Analyzing Rule: {rule_str}")

    # 1. Mine for particles
    miner = ParticleMiner(rule_str)
    particles = miner.mine(attempts=20, steps=500, density=0.1)

    if not particles:
        print("  No particles found. Rule may be too chaotic or static.")
        return ReactionTable(rule_str=rule_str)

    print(f"  Found {len(particles)} unique particles.")
    for p in particles:
        print(f"    - {p.name}")

    # 2. Collide them
    collider = Collider(rule_str, particles)
    table = collider.run_all_experiments()

    return table


if __name__ == "__main__":
    # Test with Game of Life
    table = analyze_rule("B3/S23")
    print(table.summary())
