"""
Goal-Directed Search: Find rules that satisfy specific functional objectives.

Instead of passive exploration, this module allows active search:
- User defines a Goal (e.g., "Find a rule with gliders that can create AND gates").
- System queries the Atlas for candidates matching criteria.
- System simulates candidates to verify they meet the goal.
"""

import sqlite3
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional


@dataclass
class SearchGoal:
    """Defines a goal for the search."""

    name: str
    description: str
    # Filter criteria for Atlas query
    min_harmonic_overlap: float = 0.3
    max_harmonic_overlap: float = 0.6
    phase: Optional[str] = None  # "Particle", "Condensate", or None for both
    requires_gliders: bool = False
    min_oligons: int = 0
    # Verification function (optional, runs simulation to verify)
    verifier: Optional[Callable] = None


class GoalDirectedSearch:
    """
    Searches the Atlas for rules matching specific goals.
    """

    def __init__(self, db_path: str = "data/atlas_full_v6_gpu.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def search(self, goal: SearchGoal, limit: int = 50) -> List[Dict]:
        """
        Search for rules matching the goal criteria.
        Returns a list of candidate rules with their metrics.
        """
        cursor = self.conn.cursor()

        # Build query dynamically
        conditions = ["harmonic_overlap BETWEEN ? AND ?"]
        params = [goal.min_harmonic_overlap, goal.max_harmonic_overlap]

        if goal.phase:
            conditions.append("phase = ?")
            params.append(goal.phase)

        if goal.requires_gliders:
            conditions.append("scientific_metrics.particle_count > 0")

        # trunk-ignore(bandit/B608)
        query = f"""
            SELECT explorations.rule_str, harmonic_overlap, fractal_dimension, 
                   monodromy, phase, wolfram_class, equilibrium_density,
                   particle_count, lll_score
            FROM explorations
            LEFT JOIN scientific_metrics ON explorations.rule_str = scientific_metrics.rule_str
            WHERE {' AND '.join(conditions)}
            ORDER BY harmonic_overlap DESC
            LIMIT ?
        """
        params.append(limit)

        cursor.execute(query, params)
        candidates = [dict(row) for row in cursor.fetchall()]

        # Apply verifier if provided
        if goal.verifier:
            verified = []
            for cand in candidates:
                if goal.verifier(cand["rule_str"]):
                    cand["verified"] = True
                    verified.append(cand)
            return verified

        return candidates

    def find_goldilocks(self, limit: int = 20) -> List[Dict]:
        """Shortcut: Find rules in the Goldilocks Zone."""
        goal = SearchGoal(
            name="Goldilocks",
            description="Rules with balanced complexity (H=0.3-0.6)",
            min_harmonic_overlap=0.3,
            max_harmonic_overlap=0.6,
        )
        return self.search(goal, limit)

    def find_condensates(self, limit: int = 20) -> List[Dict]:
        """Shortcut: Find high-complexity Condensate rules."""
        goal = SearchGoal(
            name="Complex Condensates",
            description="Condensate rules in Goldilocks Zone",
            min_harmonic_overlap=0.3,
            max_harmonic_overlap=0.6,
            phase="resonant",  # Condensates have positive monodromy
        )
        return self.search(goal, limit)

    def find_particles(self, limit: int = 20) -> List[Dict]:
        """Shortcut: Find high-complexity Particle rules."""
        goal = SearchGoal(
            name="Complex Particles",
            description="Particle rules in Goldilocks Zone",
            min_harmonic_overlap=0.3,
            max_harmonic_overlap=0.6,
            phase="tense",  # Particles have negative monodromy
        )
        return self.search(goal, limit)
