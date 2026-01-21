import gzip
import sqlite3
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class RuleStats:
    total_scanned: int
    goldilocks_count: int
    class_4_candidates: int
    avg_entropy: float


class RuliadAnalyzer:
    def __init__(self, db_path: str = "data/atlas_full_v6_gpu.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_global_stats(self) -> RuleStats:
        """Fetch high-level statistics about the mapped Ruliad."""
        cursor = self.conn.cursor()

        # Total scanned
        cursor.execute("SELECT count(*) FROM explorations")
        total = cursor.fetchone()[0]

        # Goldilocks (0.3 <= H <= 0.6)
        cursor.execute(
            "SELECT count(*) FROM explorations WHERE harmonic_overlap BETWEEN 0.3 AND 0.6"
        )
        goldilocks = cursor.fetchone()[0]

        # Wolfram Class 4 (approximate based on saved class)
        cursor.execute("SELECT count(*) FROM explorations WHERE wolfram_class = 4")
        class_4 = cursor.fetchone()[0]

        # Avg Entropy
        cursor.execute(
            "SELECT avg(harmonic_overlap) FROM explorations WHERE harmonic_overlap > 0"
        )
        avg_h = cursor.fetchone()[0] or 0.0

        return RuleStats(total, goldilocks, class_4, avg_h)

    def find_goldilocks_rules(self, limit: int = 50) -> List[Dict]:
        """Find the most interesting 'Class 4' candidates."""
        cursor = self.conn.cursor()
        query = """
            SELECT rule_str, harmonic_overlap, fractal_dimension, wolfram_class
            FROM explorations 
            WHERE harmonic_overlap BETWEEN 0.3 AND 0.6
            ORDER BY harmonic_overlap DESC
            LIMIT ?
        """
        cursor.execute(query, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def export_cayley_nquads(self, output_path: str = "data/rule_space.nq.gz"):
        """
        Export the connectivity graph to N-Quads format for Cayley.
        Nodes: Rules
        Edges: <RuleA> <connected_to> <RuleB> .
        """
        print(f"Exporting N-Quads to {output_path}...")

        # Get all vectors/rules to build graph
        # For simplicity, we define neighbors as rules with Hamming distance 1
        # BUT calculating that for 158k rules is O(N^2) - too slow.
        # Instead, we just export the properties we know.

        # If we really want the graph, we need to know WHO connects to WHO.
        # Since we don't store edges explicitly, we can generate them for the known set.
        # For 158k rules, we can iterate and generate neighbors, check if neighbor exists.

        cursor = self.conn.cursor()
        cursor.execute("SELECT rule_str, harmonic_overlap FROM explorations")
        rules = {row["rule_str"]: row["harmonic_overlap"] for row in cursor.fetchall()}

        known_set = set(rules.keys())

        with gzip.open(output_path, "wt") as f:
            for rule, h in rules.items():
                # 1. Node properties
                # <rule:B3/S23> <pred:type> <obj:Rule>
                f.write(f"<rule:{rule}> <pred:type> <obj:Rule> .\n")

                # <rule:B3/S23> <pred:harmonic_overlap> "0.5000"
                f.write(f'<rule:{rule}> <pred:harmonic_overlap> "{h:.4f}" .\n')

                # 2. Edges (Hamming neighbors)
                neighbors = self._generate_neighbors(rule)
                for n in neighbors:
                    if n in known_set:
                        # <rule:A> <pred:connected_to> <rule:B>
                        f.write(f"<rule:{rule}> <pred:connected_to> <rule:{n}> .\n")

    def _generate_neighbors(self, rule_str: str) -> List[str]:
        """Generate 18 Hamming neighbors for a rule string."""
        # This duplicates logic in pipeline but is pure string manipul for safety
        # Or reuse pipeline logic if imported?
        # Let's implement a lightweight converter here to avoid heavy imports

        # Parse B/S
        try:
            b_part, s_part = rule_str.split("/")
            b_nums = set(int(c) for c in b_part[1:] if c.isdigit())
            s_nums = set(int(c) for c in s_part[1:] if c.isdigit())

            neighbors = []

            # Flip B bits (0-8)
            for i in range(9):
                new_b = b_nums.copy()
                if i in new_b:
                    new_b.remove(i)
                else:
                    new_b.add(i)
                neighbors.append(self._fmt(new_b, s_nums))

            # Flip S bits (0-8)
            for i in range(9):
                new_s = s_nums.copy()
                if i in new_s:
                    new_s.remove(i)
                else:
                    new_s.add(i)
                neighbors.append(self._fmt(b_nums, new_s))

            return neighbors
        except ValueError:
            return []

    def _fmt(self, b_set, s_set) -> str:
        b = "".join(str(x) for x in sorted(list(b_set)))
        s = "".join(str(x) for x in sorted(list(s_set)))
        return f"B{b}/S{s}"
