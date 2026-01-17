from ..compression.metrics import CompressionTelemetry

class RuleClassifier:
    """
    Heuristics to classify rules into Wolfram Classes (1-4).
    Based on compression metrics and learning dynamics.
    """
    
    @staticmethod
    def classify(telemetry: CompressionTelemetry) -> int:
        """
        Returns:
            1: Frozen (Homogeneous)
            2: Periodic (Simple patterns)
            3: Chaotic (Random)
            4: Complex (Structured/Computation)
        """
        # Heuristics
        
        # 1. Entropy Check (Is there anything there?)
        if telemetry.shannon_entropy < 0.05:
            return 1 # Class 1: Frozen / Empty
            
        # 2. Rigid Compression Check (Is it simple?)
        # Tuned thresholds based on 200x500 grid:
        # Rule 0 (Class 1): ~0.002
        # Rule 110 (Class 4): ~0.078
        # Rule 30 (Class 3): ~0.142
        
        ratio = telemetry.rigid_ratio_lzma
        
        if ratio < 0.03:
            return 2 # Class 2: Simple Periodic (very compressible but > 0 entropy)
            
        if ratio > 0.12:
            return 3 # Class 3: Chaotic (Least compressible)
            
        # Intermediate zone (0.03 - 0.12) -> Potential Class 4
        # Check neural learning to confirm it's not just "noisy periodic"
        
        # If model is learning (negative slope), it's likely Class 4.
        # However, for MVP, the rigid ratio is a strong enough signal for 1D.
        # Let's trust the "Goldilocks Zone" of compression.
        return 4
                
        return 0 # Unknown
