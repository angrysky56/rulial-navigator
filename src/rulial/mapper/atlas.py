from typing import Dict, List, Optional
from ..compression.metrics import CompressionTelemetry
from ..navigator.gradient import ProbeResult
from .topology import TopologicalSignature

class Atlas:
    """
     The Atlas of Ignorance.
     Maps the explored Rulial Space.
    """
    
    def __init__(self):
        # In-memory storage for MVP
        self.rules: Dict[int, Dict] = {}
        
    def record(self, 
               rule: int, 
               telemetry: CompressionTelemetry,
               wolfram_class: int,
               topology: Optional[TopologicalSignature] = None):
        """
        Record a visit to a rule.
        """
        self.rules[rule] = {
            "class": wolfram_class,
            "rigid_ratio": telemetry.rigid_ratio_lzma,
            "loss_slope": telemetry.loss_derivative,
            "betti_1": topology.betti_1 if topology else 0,
            "persistence_max": topology.max_persistence if topology else 0.0
        }
        
    def get_color(self, rule: int) -> str:
        """
        Return the map color for a rule.
        """
        if rule not in self.rules:
            return "black" # Terra Incognita
            
        data = self.rules[rule]
        c = data["class"]
        
        if c == 1 or c == 2:
            return "blue" # Ice
        elif c == 3:
            return "red" # Fire/Chaos
        elif c == 4:
            return "gold" # The Filament
            
        return "grey"
        
    def get_gold_filaments(self) -> List[int]:
        """Return all Class 4 rules found."""
        return [r for r, d in self.rules.items() if d["class"] == 4]
        
    def get_map_status(self) -> Dict[str, int]:
        """Return counts of explored types."""
        counts = {"black": 256 - len(self.rules), "blue": 0, "red": 0, "gold": 0}
        for r in self.rules:
            color = self.get_color(r)
            if color in counts:
                counts[color] += 1
        return counts
