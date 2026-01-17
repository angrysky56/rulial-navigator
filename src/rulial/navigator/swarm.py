import random
import numpy as np
from typing import List

class SwarmNavigator:
    """
    Manages the swarm of probes exploring rule space.
    """
    
    @staticmethod
    def hamming_neighbors(rule: int, distance: int = 1) -> List[int]:
        """
        Get all rules within Hamming distance D of the current rule.
        For D=1, flips 1 bit (8 neighbors).
        """
        neighbors = []
        # ECA rules are 8 bits (0-255)
        num_bits = 8
        
        # Simple recursion for distance > 1 could be added,
        # but for now let's just do distance=1 explicitly
        if distance == 1:
            for i in range(num_bits):
                # Flip bit i
                neighbor = rule ^ (1 << i)
                neighbors.append(neighbor)
        else:
            # Monte Carlo sampling for larger distances/temperature
            # Or exhaustive if D is small
            pass
            
        return neighbors

    @staticmethod
    def spawn_probes(center: int, count: int, temperature: float) -> List[int]:
        """
        Spawn probes around a center rule.
        
        Temperature T dictates mutation probability:
        - Low T (< 1.0): Mostly nearest neighbors (Hamming=1)
        - High T (> 2.0): Jumps to further rules (Hamming > 1)
        
        We can model this as Boltzmann distribution or simple mutation rate.
        Let's use mutation rate P = sigmoid(T) - 0.5?
        Or just: Distance = Poisson(T)?
        """
        probes = set()
        probes.add(center) # Always include self
        
        # 1. Always include all immediate neighbors (Isotropy)
        neighbors_d1 = SwarmNavigator.hamming_neighbors(center, 1)
        probes.update(neighbors_d1)
        
        # 2. If count > 9, sample others based on temperature
        needed = count - len(probes)
        if needed > 0:
            for _ in range(needed):
                # Mutation logic
                # Randomly flip bits with probability scaled by T
                # Base mutation rate per bit
                p_flip = min(0.5, 0.05 * temperature)
                
                mutation = 0
                for i in range(8):
                    if random.random() < p_flip:
                        mutation |= (1 << i)
                
                new_rule = center ^ mutation
                probes.add(new_rule)
                
        return list(probes)
