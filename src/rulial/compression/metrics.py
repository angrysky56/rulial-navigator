import numpy as np
import scipy.stats
from dataclasses import dataclass
from typing import List
from .rigid import compress_ratio_lzma, compress_ratio_gzip
from .neural import NeuralCompressor
from ..engine.spacetime import SpacetimeUtil

@dataclass
class CompressionTelemetry:
    rigid_ratio_lzma: float
    rigid_ratio_gzip: float
    neural_losses: List[float]
    mean_loss: float
    loss_derivative: float  # Slope of loss curve (learning rate)
    shannon_entropy: float

class TelemetryAnalyzer:
    def __init__(self):
        self.neural = NeuralCompressor()
        
    def analyze(self, spacetime: np.ndarray) -> CompressionTelemetry:
        """
        Perform full compression analysis on a spacetime diagram.
        """
        # 1. Rigid Compression
        data_bytes = SpacetimeUtil.to_bytes(spacetime)
        lzma_ratio = compress_ratio_lzma(data_bytes)
        gzip_ratio = compress_ratio_gzip(data_bytes)
        
        # 2. Entropy
        # Flatten and compute Shannon entropy of the bit distribution
        flat = spacetime.flatten()
        counts = np.bincount(flat, minlength=2)
        probs = counts / np.sum(counts)
        entropy = scipy.stats.entropy(probs, base=2)
        
        # 3. Neural Compression Progress
        losses = self.neural.compression_progress(spacetime)
        mean_loss = np.mean(losses) if losses else 0.0
        
        # Calculate approximate derivative (slope of last 50% of learning curve)
        if len(losses) > 10:
            half = len(losses) // 2
            # Simple linear regression slope
            indices = np.arange(len(losses[half:]))
            slope, _, _, _, _ = scipy.stats.linregress(indices, losses[half:])
        else:
            slope = 0.0
            
        return CompressionTelemetry(
            rigid_ratio_lzma=lzma_ratio,
            rigid_ratio_gzip=gzip_ratio,
            neural_losses=losses,
            mean_loss=mean_loss,
            loss_derivative=slope, # Negative slope = Learning = Good
            shannon_entropy=entropy
        )
