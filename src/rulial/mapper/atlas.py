"""
Atlas of Ignorance - Persistent Rulial Map

Maps explored Rulial Space with compression, topological, and sheaf metrics.
Uses SQLite for persistence, allowing systematic scans and visualizations.
"""

import sqlite3
import json
from typing import Any, Dict, List, Optional
from dataclasses import asdict

from ..compression.metrics import CompressionTelemetry
from .topology import TopologicalSignature


class Atlas:
    """
    The Atlas of Ignorance (Persistent).
    Maps explored Rulial Space with Sheaf & Topological metrics.
    
    Supports both 1D ECA (by rule number) and 2D Totalistic (by rule string).
    """

    def __init__(self, db_path: str = "atlas.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        """Initialize database schema with sheaf metrics."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS explorations (
                rule_str TEXT PRIMARY KEY,
                wolfram_class INTEGER,
                
                -- Phase Classification
                phase TEXT,
                is_condensate INTEGER,
                
                -- Compression Metrics
                compression_ratio REAL,
                loss_slope REAL,
                
                -- Topological Metrics
                betti_1 INTEGER,
                persistence_max REAL,
                
                -- Condensate Metrics
                equilibrium_density REAL,
                expansion_factor REAL,
                
                -- Sheaf Metrics (The New Physics)
                monodromy REAL,
                harmonic_overlap REAL,
                spectral_gap REAL,
                sheaf_phase TEXT,
                
                -- T-P+E Metrics
                toroidal REAL,
                poloidal REAL,
                emergence REAL,
                tpe_mode TEXT,
                
                -- B/S set parsing
                b_set TEXT,
                s_set TEXT,
                
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def record(
        self,
        rule_str: str,
        wolfram_class: int,
        telemetry: Optional[CompressionTelemetry] = None,
        topology: Optional[TopologicalSignature] = None,
        sheaf: Optional[Any] = None,  # SheafAnalysis
        condensate: Optional[Any] = None,  # CondensateAnalysis
        tpe: Optional[Any] = None,  # TPEResult
        phase: str = "unknown",
        b_set: str = "",
        s_set: str = "",
    ):
        """
        Record a complete exploration result.
        """
        query = """
            INSERT OR REPLACE INTO explorations (
                rule_str, wolfram_class, phase, is_condensate,
                compression_ratio, loss_slope,
                betti_1, persistence_max,
                equilibrium_density, expansion_factor,
                monodromy, harmonic_overlap, spectral_gap, sheaf_phase,
                toroidal, poloidal, emergence, tpe_mode,
                b_set, s_set
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Safe extraction with defaults
        cr = telemetry.rigid_ratio_lzma if telemetry else 0.0
        ls = telemetry.loss_derivative if telemetry else 0.0
        
        betti = topology.betti_1 if topology else 0
        p_max = topology.max_persistence if topology else 0.0
        
        eq_d = condensate.equilibrium_density if condensate else 0.0
        exp_f = condensate.expansion_factor if condensate else 0.0
        is_cond = 1 if (condensate and condensate.is_condensate) else 0
        
        mono = sheaf.monodromy_index if sheaf else 0.0
        overlap = sheaf.harmonic_overlap if sheaf else 0.0
        gap = sheaf.spectral_gap if sheaf else 0.0
        s_phase = sheaf.sheaf_type if sheaf else "unknown"
        
        t_val = tpe.toroidal if tpe else 0.0
        p_val = tpe.poloidal if tpe else 0.0
        e_val = tpe.emergence if tpe else 0.0
        tpe_m = tpe.mode if tpe else "unknown"

        self.conn.execute(query, (
            rule_str, wolfram_class, phase, is_cond,
            cr, ls,
            betti, p_max,
            eq_d, exp_f,
            mono, overlap, gap, s_phase,
            t_val, p_val, e_val, tpe_m,
            b_set, s_set
        ))
        self.conn.commit()

    def record_from_dict(self, data: Dict[str, Any]):
        """Record from a dictionary (useful for JSON import)."""
        self.conn.execute("""
            INSERT OR REPLACE INTO explorations (
                rule_str, wolfram_class, phase, is_condensate,
                compression_ratio, betti_1,
                equilibrium_density, expansion_factor,
                monodromy, harmonic_overlap, spectral_gap, sheaf_phase,
                toroidal, poloidal, emergence, tpe_mode,
                b_set, s_set
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('rule_str', ''),
            data.get('wolfram_class', 0),
            data.get('phase', 'unknown'),
            1 if data.get('is_condensate', False) else 0,
            data.get('compression_ratio', 0.0),
            data.get('betti_1', 0),
            data.get('equilibrium_density', 0.0),
            data.get('expansion_factor', 0.0),
            data.get('monodromy', 0.0),
            data.get('harmonic_overlap', 0.0),
            data.get('spectral_gap', 0.0),
            data.get('sheaf_phase', 'unknown'),
            data.get('toroidal', 0.0),
            data.get('poloidal', 0.0),
            data.get('emergence', 0.0),
            data.get('tpe_mode', 'unknown'),
            data.get('b_set', ''),
            data.get('s_set', ''),
        ))
        self.conn.commit()

    def import_from_json(self, json_path: str):
        """Import existing atlas JSON data into SQLite."""
        import json as json_module
        with open(json_path) as f:
            data = json_module.load(f)
        
        for record in data:
            self.record_from_dict(record)
        
        return len(data)

    def get_all_rules(self) -> List[Dict[str, Any]]:
        """Retrieve full dataset for visualization."""
        cursor = self.conn.execute("SELECT * FROM explorations")
        return [dict(row) for row in cursor.fetchall()]

    def get_by_phase(self, phase: str) -> List[Dict[str, Any]]:
        """Get rules by phase (condensate, particle, hybrid)."""
        cursor = self.conn.execute(
            "SELECT * FROM explorations WHERE phase = ?", (phase,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_by_sheaf_type(self, sheaf_type: str) -> List[Dict[str, Any]]:
        """Get rules by sheaf classification."""
        cursor = self.conn.execute(
            "SELECT * FROM explorations WHERE sheaf_phase = ?", (sheaf_type,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_gold_filaments(self) -> List[str]:
        """Return rule strings of Class 4 / Life-like rules."""
        cursor = self.conn.execute(
            "SELECT rule_str FROM explorations WHERE wolfram_class = 4"
        )
        return [row[0] for row in cursor.fetchall()]

    def get_condensates(self) -> List[str]:
        """Return all condensate rules."""
        cursor = self.conn.execute(
            "SELECT rule_str FROM explorations WHERE is_condensate = 1"
        )
        return [row[0] for row in cursor.fetchall()]

    def get_computational_candidates(self, min_overlap: float = 0.3, max_overlap: float = 0.7) -> List[Dict[str, Any]]:
        """
        Get rules in the 'Goldilocks zone' for computation.
        High harmonic overlap = near equilibrium (frozen)
        Low harmonic overlap = far from equilibrium (chaotic)
        Middle = potential for structured computation
        """
        cursor = self.conn.execute("""
            SELECT * FROM explorations 
            WHERE harmonic_overlap BETWEEN ? AND ?
            ORDER BY harmonic_overlap
        """, (min_overlap, max_overlap))
        return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict[str, Any]:
        """Get summary statistics."""
        cursor = self.conn.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN wolfram_class = 4 THEN 1 ELSE 0 END) as class_4,
                SUM(CASE WHEN is_condensate = 1 THEN 1 ELSE 0 END) as condensates,
                AVG(harmonic_overlap) as avg_overlap,
                AVG(monodromy) as avg_monodromy
            FROM explorations
        """)
        row = cursor.fetchone()
        return dict(row) if row else {}

    def get_color(self, rule_str: str) -> str:
        """Return the map color for a rule."""
        cursor = self.conn.execute(
            "SELECT wolfram_class, is_condensate FROM explorations WHERE rule_str = ?",
            (rule_str,)
        )
        row = cursor.fetchone()
        
        if not row:
            return "black"  # Terra Incognita
        
        c, is_cond = row['wolfram_class'], row['is_condensate']
        
        if c == 1 or c == 2:
            return "blue"  # Ice
        elif c == 3:
            return "red"  # Fire/Chaos
        elif c == 4:
            if is_cond:
                return "cyan"  # Condensate
            return "gold"  # Particle (The Filament)
        
        return "grey"

    def close(self):
        """Close database connection."""
        self.conn.close()
