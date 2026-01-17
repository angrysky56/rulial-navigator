import numpy as np

from rulial.navigator.titans import TitansNavigator


def mock_entropy_function(rule_vector):
    """
    Simulate physics: High entropy if rule has > 5 '1's.
    This mimics finding "dense" rules.
    """
    s = np.sum(rule_vector)
    # Smooth sigmoid-like mapping or binary
    if s > 5:
        return 0.8 + (s / 10) * 0.2
    else:
        return 0.1


def verify_titans():
    print("=== Testing Rulial Titans (Cognitive Layer) ===")

    rule_size = 10  # 10 bits
    titans = TitansNavigator(rule_size_bits=rule_size)

    print("\n[Phase 1] Training on Random Probes...")

    losses = []

    for i in range(50):
        # 1. Random Rule interaction
        rule = np.random.randint(0, 2, rule_size)

        # 2. Physics (Ground Truth)
        true_entropy = mock_entropy_function(rule)

        # 3. Learn
        loss = titans.probe_and_learn(rule, true_entropy)
        losses.append(loss)

        if i % 10 == 0:
            print(f"Step {i}: Loss (Surprise) = {loss:.4f}")

    avg_loss_start = np.mean(losses[:10])
    avg_loss_end = np.mean(losses[-10:])
    print(
        f"\nLearning Check: First 10 Avg={avg_loss_start:.4f} -> Last 10 Avg={avg_loss_end:.4f}"
    )

    if avg_loss_end < avg_loss_start:
        print("SUCCESS: Titans learned the pattern!")
    else:
        print("WARNING: Learning curve stagnated (might need more steps or simpler fn)")

    print("\n[Phase 2] Hallucination Test (Intuition)...")

    # Start with a low-complexity rule (all zeros)
    current = np.zeros(rule_size, dtype=int)
    print(f"Current Rule (Sum={np.sum(current)}). Predicting neighbors...")

    # We expect it to prefer neighbors that flip 0 -> 1 (closer to sum > 5)
    # But wait, it only sees 1-step neighbors. Sum will go 0 -> 1.
    # The GT function is: sum > 5 is High(0.8), sum <= 5 is Low(0.1).
    # If network learned "More 1s = Better", it should predict higher entropy for sum=1 than sum=0?
    # Or maybe it learned 0, 1, 2, 3, 4, 5 ALL map to 0.1.
    # So gradient is flat locally?
    # Actually, Neural Nets generalize. It might learn linear trend.

    best_rule, pred_ent = titans.hallucinate_neighbors(current, num_neighbors=10)
    print(
        f"Titans Suggests Neighbor with Sum={np.sum(best_rule)}, Predicted Entropy={pred_ent:.4f}"
    )

    # Let's force-feed a High Entropy rule and see if it hallucinates keeping it high
    print("\nTesting near High Entropy peak:")
    high_rule = np.ones(rule_size, dtype=int)  # Sum 10
    best_rule, pred_ent = titans.hallucinate_neighbors(high_rule, num_neighbors=10)
    # The neighbor will have sum 9. It should still predict high entropy.
    print(
        f"From Sum=10, Titans Suggests Neighbor (Sum={np.sum(best_rule)}), Pred={pred_ent:.4f}"
    )


if __name__ == "__main__":
    verify_titans()
