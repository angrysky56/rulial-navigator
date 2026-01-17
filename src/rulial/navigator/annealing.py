class AnnealingController:
    """
    Adiabatic Annealing Controller.
    Manages the 'Temperature' of the search.
    
    - High Temp: High probability of long-distance jumps (Exploration).
    - Low Temp: Local hill climbing (Exploitation).
    """
    
    def __init__(self, 
                 initial_temp: float = 1.0,
                 min_temp: float = 0.1,
                 max_temp: float = 5.0,
                 cooling_rate: float = 0.9,
                 heating_rate: float = 1.1):
        self.temperature = initial_temp
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.cooling_rate = cooling_rate
        self.heating_rate = heating_rate
        self.stagnation_counter = 0

    def update(self, gradient_magnitude: float) -> float:
        """
        Update temperature based on recent progress (gradient magnitude).
        """
        threshold = 0.01 # What counts as "progress"
        
        if gradient_magnitude > threshold:
            # We are climbing a hill! Cool down to focus.
            self.temperature *= self.cooling_rate
            self.stagnation_counter = 0
        else:
            # Flat landscape / Local optimum. Heat up to escape.
            self.temperature *= self.heating_rate
            self.stagnation_counter += 1
            
        # Clamp
        self.temperature = max(self.min_temp, min(self.max_temp, self.temperature))
        
        return self.temperature
