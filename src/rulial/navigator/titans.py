from typing import Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


class TitansMemory(nn.Module):
    """
    Rulial Titans: A Neural Memory module that learns at test-time.

    It predicts the 'Interestingness' (Entanglement Entropy) of a rule.
    High prediction error ('Surprise') triggers a weight update, encoding
    the topological features of the rule into the memory weights.
    """

    def __init__(
        self, input_dim: int, hidden_dim: int = 64, learning_rate: float = 0.01
    ):
        super().__init__()
        self.input_dim = input_dim

        # The "Memory" is these weights.
        # Unlike standard ML, we optimize these continuously during navigation.
        self.memory_core = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 1),  # Predicts Entropy scalar [0, 1]
            nn.Sigmoid(),
        )

        # Online Optimizer (Momentum-based SGD is standard for Titans)
        self.optimizer = optim.SGD(self.parameters(), lr=learning_rate, momentum=0.9)
        self.loss_fn = nn.MSELoss()

        # Metrics
        self.current_surprise = 0.0

        # Auto-Device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.to(self.device)
        print(f"Titans Memory loaded on: {self.device}")

    def forward(self, rule_vector: torch.Tensor) -> torch.Tensor:
        """
        Predicts the topological complexity of a rule vector.
        """
        return self.memory_core(rule_vector)

    def remember(self, rule_vector: np.ndarray, actual_entropy: float) -> float:
        """
        The 'Test-Time Training' step.

        1. Predicts entropy.
        2. Compares with actual (Tensor Bridge) entropy.
        3. Backpropagates the 'Surprise' to update memory.

        Returns:
            The magnitude of the Surprise (Loss).
        """
        # Convert inputs
        # Ensure rule_vector is float32
        x = (
            torch.tensor(rule_vector, dtype=torch.float32).unsqueeze(0).to(self.device)
        )  # Batch size 1
        y_true = (
            torch.tensor([actual_entropy], dtype=torch.float32)
            .unsqueeze(0)
            .to(self.device)
        )

        self.train()  # Ensure gradients are active
        self.optimizer.zero_grad()

        # 1. Forward (Prediction)
        y_pred = self(x)

        # 2. Compute Surprise (Loss)
        loss = self.loss_fn(y_pred, y_true)

        # 3. Backward (Memory Update)
        loss.backward()

        # 4. Commit to Memory
        self.optimizer.step()

        self.current_surprise = loss.item()
        return self.current_surprise


class TitansNavigator:
    """
    The Agent that uses the Memory to guide the Swarm.
    """

    def __init__(self, rule_size_bits: int):
        self.memory = TitansMemory(input_dim=rule_size_bits)
        self.input_dim = rule_size_bits
        self.device = self.memory.device

    def probe_and_learn(self, rule_code: np.ndarray, bridge_entropy: float):
        """
        Called after the Physics Engine & Bridge return a result.
        Updates the Titans Memory based on the finding.
        """
        surprise = self.memory.remember(rule_code, bridge_entropy)

        # If surprise was high, this rule is a "Landmark"
        # We can log this for the UI/User
        if surprise > 0.1:
            pass  # Keep UI clean
            # print(
            #    f"⚡ TITANS SURPRISE! Learned new complexity feature. Loss: {surprise:.4f}"
            # )

        return surprise

    def hallucinate_neighbors(
        self, current_rule: np.ndarray, num_neighbors: int = 10
    ) -> Tuple[np.ndarray, float]:
        """
        Uses the internal memory to 'imagine' which neighbors are promising
        without actually running the expensive Tensor Bridge on them.

        Returns:
            (best_neighbor_vector, predicted_entropy)
        """
        # Generate random bit-flip neighbors
        neighbors = []
        vectors = []

        # Always include the current rule? No, we want to move.

        for _ in range(num_neighbors):
            n_rule = current_rule.copy()
            # Flip random bit
            idx = np.random.randint(0, len(current_rule))
            n_rule[idx] = 1 - n_rule[idx]  # Bit flip for binary 0/1 rule
            neighbors.append(n_rule)
            vectors.append(n_rule)

        # Batch Predict
        self.memory.eval()  # Inference mode
        with torch.no_grad():
            batch_x = torch.tensor(np.array(vectors), dtype=torch.float32).to(
                self.device
            )
            predicted_tensor = self.memory(batch_x)
            predicted_entropies = predicted_tensor.cpu().numpy().flatten()

        # Return neighbor that minimizes distance to TARGET ENTROPY
        # Hypothesis: Class 4 "Life" lives on the Edge of Chaos.
        # Max Entropy (1.0) is Chaos/Volume Law.
        # Zero Entropy (0.0) is Ice/Area Law (Trivial).
        # We want "Complex Area Law" ~ 0.5 - 0.9.
        # User Selection: The Golden Ratio (Phi - 1)
        TARGET = 0.618

        # distance = abs(pred - TARGET)
        distances = np.abs(predicted_entropies - TARGET)
        best_idx = np.argmin(distances)

        return neighbors[best_idx], float(predicted_entropies[best_idx])
