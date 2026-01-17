from typing import List

import numpy as np
import torch
import torch.nn as nn


class SimplePredictor(nn.Module):
    """
    Lightweight GRU-based predictor for 1D sequences.
    Predicts next cell state based on context window.
    """

    def __init__(self, input_dim: int = 1, hidden_dim: int = 32, num_layers: int = 1):
        super().__init__()
        self.rnn = nn.GRU(input_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        """
        x: (batch, seq_len, 1)
        Returns: (batch, seq_len, 1) predictions
        """
        out, _ = self.rnn(x)
        out = self.fc(out)
        return self.sigmoid(out)


class NeuralCompressor:
    """
    Estimates 'Compression Progress' via prediction error dynamics.
    Instead of full file compression, we measure how well a model *learns* the rule over time.
    """

    def __init__(self, learning_rate: float = 0.01):
        self.model = SimplePredictor()
        self.criterion = nn.BCELoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        # We re-initialize for every new rule to measure *intrinsic* learnability from scratch

    def reset_model(self):
        """Reset model weights to untrained state."""
        for layer in self.model.children():
            if hasattr(layer, "reset_parameters"):
                layer.reset_parameters()
        self.model = SimplePredictor()  # Fresh init
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)

    def compression_progress(
        self, spacetime: np.ndarray, window: int = 50
    ) -> List[float]:
        """
        Walks through the spacetime diagram, training online.
        Returns the loss curve (prediction error over time).

        Interpretation:
        - Rapid drop to 0: Trivial (Class 1/2)
        - Flat high line: Random (Class 3)
        - Slow, jerky decline: Complexity (Class 4) - model is fighting to extract patterns

        Returns:
            List of loss values per row (or batched window).
        """
        self.reset_model()
        self.model.train()
        losses = []

        # We treat each row as a sequence to be learned
        # For 1D CA, time direction is the learning axis.
        # We can also feed sliding windows of the previous row to predict the next row.
        # Simplest proxy: Can we predict row T from T-1?
        # Actually, for CA, row T is deterministically row T-1 + Rule.
        # If the model learns the Rule, loss goes to 0.
        # Class 4 is harder to learn than Class 1, but easier than Class 3.

        # Let's train on (Row -> Next Row) pairs.

        rows, cols = spacetime.shape
        # Prepare tensor: (rows-1, cols, 1)
        data = torch.from_numpy(spacetime).float().unsqueeze(-1)

        # Online learning loop
        # We update the model row by row and record the loss *before* optimization step (surprisal)

        for t in range(rows - 1):
            input_row = data[t].unsqueeze(0)  # (1, width, 1)
            target_row = data[t + 1].unsqueeze(0)  # (1, width, 1)

            # Predict
            output = self.model(
                input_row
            )  # We use RNN to predict next *token* in sequence or next *row*?
            # Wait, RNN usually predicts T+1 from 0..T.
            # Here we are mapping Spatial Row T -> Spatial Row T+1.
            # This is effectively learning the CA rule function.

            # Calculate Surprisal (Loss before update)
            loss = self.criterion(output, target_row)
            losses.append(loss.item())

            # Learn
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        return losses
