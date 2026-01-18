"""
Compression Flow Analyzer: The Sextant of the Navigator.

Implements the Universal Compression Stack with bifurcated architecture:
- Layer 1: Rigid Compression (LZMA/GZIP) - detects exact repetition, periodicity
- Layer 2: Fluid Compression (Neural) - detects soft patterns via prediction error

The key metric is Compression Progress (dr_c/dt), the time derivative of
compressibility. This distinguishes:
- Zero Flow + High CR: Chaos (Class 3) → Frustration
- Zero Flow + Low CR: Frozen (Class 1) → Boredom
- Positive Flow: Complexity (Class 4) → Curiosity

This acts as "Maxwell's Demon" for complexity, filtering the Sea of Chaos
and Ice of Order to surf the Gold Filaments of the Ruliad.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple

import numpy as np
import scipy.stats

from rulial.compression.neural import NeuralCompressor
from rulial.compression.rigid import compress_ratio_lzma
from rulial.engine.totalistic import Totalistic2DEngine


class NavigatorSignal(Enum):
    """Decision signals for the Navigator."""

    FRUSTRATION = "frustration"  # High entropy, zero flow → Avoid/Heat Up
    BOREDOM = "boredom"  # Low entropy, zero flow → Avoid/Cool Down
    CURIOSITY = "curiosity"  # Intermediate entropy, positive flow → Approach


@dataclass
class CompressionFlowState:
    """Instantaneous state of the compression stack."""

    timestep: int
    rigid_ratio: float  # LZMA compression ratio
    neural_loss: float  # Prediction error (1 - neural_ratio)
    combined_ratio: float  # Weighted combination


@dataclass
class FlowAnalysis:
    """Complete flow analysis result."""

    rule_str: str

    # Static metrics
    mean_rigid_ratio: float
    mean_neural_loss: float
    final_rigid_ratio: float

    # Flow metrics (derivatives)
    rigid_flow: float  # dr_rigid/dt
    neural_flow: float  # dr_neural/dt
    combined_flow: float  # Weighted combination

    # Classification
    signal: NavigatorSignal
    wolfram_class: int
    intrinsic_reward: float  # Curiosity strength

    # Raw data for visualization
    rigid_curve: List[float]
    neural_curve: List[float]

    def summary(self) -> str:
        signal_icons = {
            NavigatorSignal.FRUSTRATION: "🔥 FRUSTRATION",
            NavigatorSignal.BOREDOM: "❄️ BOREDOM",
            NavigatorSignal.CURIOSITY: "✨ CURIOSITY",
        }

        return (
            f"═══ Compression Flow: {self.rule_str} ═══\n"
            f"  Rigid CR: {self.mean_rigid_ratio:.4f} (final: {self.final_rigid_ratio:.4f})\n"
            f"  Neural Loss: {self.mean_neural_loss:.4f}\n"
            f"  ─────────────────────────────\n"
            f"  Rigid Flow (dr/dt): {self.rigid_flow:+.6f}\n"
            f"  Neural Flow: {self.neural_flow:+.6f}\n"
            f"  Combined Flow: {self.combined_flow:+.6f}\n"
            f"  ─────────────────────────────\n"
            f"  Signal: {signal_icons[self.signal]}\n"
            f"  Wolfram Class: {self.wolfram_class}\n"
            f"  Intrinsic Reward: {self.intrinsic_reward:.4f}"
        )


class CompressionFlowAnalyzer:
    """
    The Universal Compression Stack.

    Bifurcated architecture:
    1. Rigid Layer: LZMA compression for exact patterns
    2. Fluid Layer: Neural prediction for soft patterns

    Outputs Compression Progress (flow) and Navigator Signals.
    """

    def __init__(
        self,
        window_size: int = 20,  # Frames per compression window
        neural_epochs: int = 3,  # Training epochs per window
        rigid_weight: float = 0.4,  # Weight for rigid in combined
        neural_weight: float = 0.6,  # Weight for neural in combined
    ):
        self.window_size = window_size
        self.neural_epochs = neural_epochs
        self.rigid_weight = rigid_weight
        self.neural_weight = neural_weight

        # Thresholds for classification
        self.chaos_threshold = 0.12  # CR > this = chaos
        self.frozen_threshold = 0.003  # CR < this = frozen
        self.flow_threshold = 0.0001  # |flow| > this = learning

    def _compress_window(
        self, frames: np.ndarray, neural: NeuralCompressor
    ) -> CompressionFlowState:
        """Compress a window of frames through both layers."""
        # Layer 1: Rigid compression
        flat_bytes = frames.tobytes()
        rigid_ratio = compress_ratio_lzma(flat_bytes)

        # Layer 2: Neural compression (prediction error)
        # Reshape 3D (time, h, w) to 2D (time, h*w) for neural compressor
        if frames.ndim == 3:
            frames_2d = frames.reshape(frames.shape[0], -1)
        else:
            frames_2d = frames

        losses = neural.compression_progress(frames_2d)
        neural_loss = np.mean(losses) if losses else 1.0

        # Combined ratio (weighted)
        combined = self.rigid_weight * rigid_ratio + self.neural_weight * neural_loss

        return CompressionFlowState(
            timestep=0,  # Will be set by caller
            rigid_ratio=rigid_ratio,
            neural_loss=neural_loss,
            combined_ratio=combined,
        )

    def analyze(
        self,
        rule_str: str,
        steps: int = 300,
        grid_size: int = 64,
        density: float = 0.3,
    ) -> FlowAnalysis:
        """
        Perform full compression flow analysis on a rule.

        Returns FlowAnalysis with static metrics, flow metrics, and signal.
        """
        # 1. Simulate
        engine = Totalistic2DEngine(rule_str)
        history = engine.simulate(
            grid_size, grid_size, steps, "random", density=density
        )
        spacetime = np.stack(history, axis=0)

        # 2. Process through compression stack in windows
        neural = NeuralCompressor()
        states: List[CompressionFlowState] = []

        num_windows = len(history) // self.window_size
        for i in range(num_windows):
            start = i * self.window_size
            end = start + self.window_size
            window = spacetime[start:end]

            state = self._compress_window(window, neural)
            state.timestep = i
            states.append(state)

        if len(states) < 3:
            # Not enough data for flow analysis
            return FlowAnalysis(
                rule_str=rule_str,
                mean_rigid_ratio=0.0,
                mean_neural_loss=1.0,
                final_rigid_ratio=0.0,
                rigid_flow=0.0,
                neural_flow=0.0,
                combined_flow=0.0,
                signal=NavigatorSignal.BOREDOM,
                wolfram_class=1,
                intrinsic_reward=0.0,
                rigid_curve=[],
                neural_curve=[],
            )

        # 3. Extract curves
        rigid_curve = [s.rigid_ratio for s in states]
        neural_curve = [s.neural_loss for s in states]
        combined_curve = [s.combined_ratio for s in states]

        # 4. Calculate static metrics
        mean_rigid = np.mean(rigid_curve)
        mean_neural = np.mean(neural_curve)
        final_rigid = rigid_curve[-1]

        # 5. Calculate flow (time derivative)
        # Use linear regression on second half (post-warmup)
        half = len(rigid_curve) // 2
        t = np.arange(len(rigid_curve[half:]))

        rigid_slope, _, _, _, _ = scipy.stats.linregress(t, rigid_curve[half:])
        neural_slope, _, _, _, _ = scipy.stats.linregress(t, neural_curve[half:])
        combined_slope, _, _, _, _ = scipy.stats.linregress(t, combined_curve[half:])

        # 6. Classify signal
        signal, wolfram_class = self._classify(mean_rigid, final_rigid, combined_slope)

        # 7. Calculate intrinsic reward
        # Positive flow (negative slope = compression improving) = reward
        # Scale by distance from extremes
        intrinsic_reward = self._calculate_reward(mean_rigid, combined_slope, signal)

        return FlowAnalysis(
            rule_str=rule_str,
            mean_rigid_ratio=float(mean_rigid),
            mean_neural_loss=float(mean_neural),
            final_rigid_ratio=float(final_rigid),
            rigid_flow=float(rigid_slope),
            neural_flow=float(neural_slope),
            combined_flow=float(combined_slope),
            signal=signal,
            wolfram_class=wolfram_class,
            intrinsic_reward=float(intrinsic_reward),
            rigid_curve=rigid_curve,
            neural_curve=neural_curve,
        )

    def _classify(
        self,
        mean_cr: float,
        final_cr: float,
        flow: float,
    ) -> Tuple[NavigatorSignal, int]:
        """
        Classify based on compression ratio and flow.

        Returns (NavigatorSignal, WolframClass)
        """
        # Zero flow detection
        has_flow = abs(flow) > self.flow_threshold

        # High CR = Chaos
        if final_cr > self.chaos_threshold:
            if has_flow:
                # Still learning in chaos - potential Class 4
                return NavigatorSignal.CURIOSITY, 4
            else:
                # Stuck in chaos
                return NavigatorSignal.FRUSTRATION, 3

        # Low CR = Frozen
        if final_cr < self.frozen_threshold:
            return NavigatorSignal.BOREDOM, 1

        # Intermediate CR
        if has_flow:
            # Actively learning = Complexity
            # Negative slope means CR is decreasing = getting more compressible
            # But for interesting patterns, we want structured incompressibility
            if flow < 0:
                return NavigatorSignal.CURIOSITY, 4  # Learning structure
            else:
                return NavigatorSignal.CURIOSITY, 4  # Complexity emerging
        else:
            # Static intermediate = periodic
            return NavigatorSignal.BOREDOM, 2

    def _calculate_reward(
        self,
        mean_cr: float,
        flow: float,
        signal: NavigatorSignal,
    ) -> float:
        """
        Calculate intrinsic reward for the Navigator.

        Reward = Curiosity strength
        - Maximized when in Goldilocks zone with active flow
        - Zero when in Frustration or Boredom
        """
        if signal == NavigatorSignal.CURIOSITY:
            # Reward proportional to flow magnitude
            # and distance from extremes
            distance_from_chaos = abs(self.chaos_threshold - mean_cr)
            distance_from_frozen = abs(mean_cr - self.frozen_threshold)
            goldilocks = min(distance_from_chaos, distance_from_frozen)

            # Flow contribution (absolute value, both directions interesting)
            flow_magnitude = abs(flow) * 1000  # Scale up

            return goldilocks * (1 + flow_magnitude)

        elif signal == NavigatorSignal.FRUSTRATION:
            # Small negative reward to encourage escape
            return -0.1

        else:  # BOREDOM
            # Moderate negative reward
            return -0.05

    def compute_gradient(
        self,
        current_rule: str,
        neighbor_analyses: Dict[str, FlowAnalysis],
    ) -> Tuple[str, float]:
        """
        Compute the Gradient of Interest across neighbors.

        Returns (best_neighbor_rule, gradient_magnitude)
        """
        if not neighbor_analyses:
            return current_rule, 0.0

        # Find neighbor that maximizes intrinsic reward
        best_rule = current_rule
        best_reward = float("-inf")

        for rule, analysis in neighbor_analyses.items():
            if analysis.intrinsic_reward > best_reward:
                best_reward = analysis.intrinsic_reward
                best_rule = rule

        # Get current reward for magnitude calculation
        current_reward = neighbor_analyses.get(
            current_rule,
            FlowAnalysis(
                rule_str=current_rule,
                mean_rigid_ratio=0,
                mean_neural_loss=0,
                final_rigid_ratio=0,
                rigid_flow=0,
                neural_flow=0,
                combined_flow=0,
                signal=NavigatorSignal.BOREDOM,
                wolfram_class=1,
                intrinsic_reward=0,
                rigid_curve=[],
                neural_curve=[],
            ),
        ).intrinsic_reward

        gradient_magnitude = best_reward - current_reward

        return best_rule, gradient_magnitude


# Convenience function
def analyze_compression_flow(rule_str: str) -> FlowAnalysis:
    """Quick analysis of a single rule."""
    analyzer = CompressionFlowAnalyzer()
    return analyzer.analyze(rule_str)


if __name__ == "__main__":
    # Test with known rules
    analyzer = CompressionFlowAnalyzer()

    test_rules = [
        ("B3/S23", "Game of Life - expected Class 4/Curiosity"),
        ("B/S", "Empty rule - expected Class 1/Boredom"),
        ("B12345678/S12345678", "Dense rule - expected Class 3/Frustration"),
        ("B36/S23", "HighLife - expected Class 4/Curiosity"),
    ]

    for rule, description in test_rules:
        print(f"\n{'='*60}")
        print(f"Testing: {description}")
        print("=" * 60)
        result = analyzer.analyze(rule)
        print(result.summary())
