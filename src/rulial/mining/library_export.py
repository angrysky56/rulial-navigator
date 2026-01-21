"""
Pattern Library Export: Convert discovered patterns to reusable formats.

Takes Oligon data (Still Lifes, Oscillators, Gliders) and exports to:
- RLE (Run-Length Encoded) format for Golly/LifeViewer
- JSON catalog for programmatic use
"""
from dataclasses import dataclass
from typing import List, Dict, Tuple
from pathlib import Path
import json

@dataclass
class Pattern:
    """A single CA pattern."""
    name: str
    rule: str
    period: int  # 1 = still life, 2+ = oscillator
    cells: List[Tuple[int, int]]  # (x, y) coordinates of live cells
    bounding_box: Tuple[int, int, int, int]  # min_x, min_y, max_x, max_y
    
    def to_rle(self) -> str:
        """Convert to RLE format."""
        if not self.cells:
            return ""
        
        min_x = min(c[0] for c in self.cells)
        min_y = min(c[1] for c in self.cells)
        max_x = max(c[0] for c in self.cells)
        max_y = max(c[1] for c in self.cells)
        
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        
        # Normalize coordinates
        normalized = {(x - min_x, y - min_y) for (x, y) in self.cells}
        
        # Build RLE
        header = f"x = {width}, y = {height}, rule = {self.rule}\n"
        
        rle_data = ""
        for row in range(height):
            run_count = 0
            last_char = None
            row_data = ""
            
            for col in range(width):
                char = 'o' if (col, row) in normalized else 'b'
                if char == last_char:
                    run_count += 1
                else:
                    if last_char:
                        row_data += f"{run_count if run_count > 1 else ''}{last_char}"
                    run_count = 1
                    last_char = char
            
            if last_char:
                row_data += f"{run_count if run_count > 1 else ''}{last_char}"
            
            # Remove trailing 'b's
            row_data = row_data.rstrip('b').rstrip('1234567890')
            
            rle_data += row_data + ("$" if row < height - 1 else "!")
        
        return header + rle_data

    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict."""
        return {
            "name": self.name,
            "rule": self.rule,
            "period": self.period,
            "cells": self.cells,
            "bounding_box": self.bounding_box
        }

class PatternLibrary:
    """Manages a collection of patterns."""
    
    def __init__(self):
        self.patterns: List[Pattern] = []
    
    def add(self, pattern: Pattern):
        self.patterns.append(pattern)
    
    def export_rle(self, output_dir: str = "data/patterns"):
        """Export all patterns to individual RLE files."""
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        
        for i, p in enumerate(self.patterns):
            filename = f"{p.rule.replace('/', '_')}_{p.name}_{i}.rle"
            (path / filename).write_text(p.to_rle())
        
        print(f"Exported {len(self.patterns)} patterns to {output_dir}/")
    
    def export_json(self, output_path: str = "data/pattern_catalog.json"):
        """Export catalog as JSON."""
        catalog = {
            "count": len(self.patterns),
            "patterns": [p.to_dict() for p in self.patterns]
        }
        Path(output_path).write_text(json.dumps(catalog, indent=2))
        print(f"Exported catalog to {output_path}")
    
    @staticmethod
    def from_oligon_analysis(rule: str, oligon_result: Dict) -> 'PatternLibrary':
        """
        Build library from OligonCounter results.
        Note: This requires the OligonCounter to store cell positions,
        which may need enhancement.
        """
        lib = PatternLibrary()
        # Placeholder: Real integration would extract cells from oligon analysis
        # For now, we create a stub
        print(f"[PatternLibrary] Would extract patterns from {rule}")
        return lib
