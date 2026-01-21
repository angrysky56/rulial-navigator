import sqlite3

import torch
import torch.nn.functional as F
from torch.optim import Adam

from rulial.learning.hypercube import generate_hypercube_graph
from rulial.learning.sheaf_learner import SheafLearner


def rule_str_to_index(rule_str: str) -> int:
    """Convert 'B.../S...' string to 18-bit integer index."""
    # Format B{born}/S{survive}
    # Bits 0-8: Born mask, Bits 9-17: Survive mask
    b_part, s_part = rule_str.split("/")
    b_digits = [int(c) for c in b_part[1:]]
    s_digits = [int(c) for c in s_part[1:]]

    idx = 0
    for d in b_digits:
        idx |= 1 << d
    for d in s_digits:
        idx |= 1 << (d + 9)
    return idx


def load_data(db_path="data/atlas_full_v6_gpu.db"):
    print(f"Loading data from {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Simple query
    rows = cur.execute("SELECT rule_str, wolfram_class FROM explorations").fetchall()
    conn.close()

    # Create label tensor (Class 4 = 1, Others = 0)
    # 0 = Unlabeled, 1 = Not Class 4, 2 = Class 4
    num_nodes = 2**18
    labels = torch.zeros(num_nodes, dtype=torch.long)
    mask = torch.zeros(num_nodes, dtype=torch.bool)

    count_c4 = 0
    for r_str, wc in rows:
        idx = rule_str_to_index(r_str)
        if wc == 4:
            labels[idx] = 1  # Positive class
            count_c4 += 1
        else:
            labels[idx] = 0  # Negative class
        mask[idx] = True

    print(f"Loaded {len(rows)} scanned rules.")
    print(f"Class 4: {count_c4}, Other: {len(rows) - count_c4}")
    return labels, mask


def train():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # 1. Build Graph
    print("Generating hypercube graph...")
    edge_index, x = generate_hypercube_graph(18)
    edge_index = edge_index.to(device)
    x = x.to(device)

    # 2. Load Labels
    labels, mask = load_data()
    labels = labels.to(device)
    mask = mask.to(device)

    # 3. Model
    model = SheafLearner(hidden_dim=32).to(device)
    optimizer = Adam(model.parameters(), lr=0.01)

    print("Training Sheaf Learner...")
    model.train()

    for epoch in range(200):
        optimizer.zero_grad()
        out = model(x, edge_index)

        # Loss only on masked (scanned) nodes
        loss = F.cross_entropy(out[mask], labels[mask])

        loss.backward()
        optimizer.step()

        if epoch % 20 == 0:
            pred = out.argmax(dim=1)
            acc = (pred[mask] == labels[mask]).float().mean()
            print(
                f"Epoch {epoch:03d}: Loss {loss.item():.4f}, Accuracy {acc.item():.4f}"
            )

    # 4. Predict on Unscanned
    print("\nPredicting on unscanned universe...")
    model.eval()
    with torch.no_grad():
        out = model(x, edge_index)
        probs = F.softmax(out, dim=1)
        c4_prob = probs[:, 1]

    # Find high probability unscanned rules
    unscanned_mask = ~mask
    c4_prob_unscanned = c4_prob * unscanned_mask.float()

    top_vals, top_indices = torch.topk(c4_prob_unscanned, 10)

    print("\nTop 10 Predicted Class 4 Rules (Unscanned):")
    for i in range(10):
        idx = top_indices[i].item()
        prob = top_vals[i].item()

        # Decode index to rule string
        # Inverse of rule_str_to_index
        b_set = []
        s_set = []
        for b in range(9):
            if (idx >> b) & 1:
                b_set.append(str(b))
        for s in range(9):
            if (idx >> (s + 9)) & 1:
                s_set.append(str(s))

        rule_str = f"B{''.join(b_set)}/S{''.join(s_set)}"
        print(f"  {rule_str}: {prob:.4f}")

    # Save model
    torch.save(model.state_dict(), "data/sheaf_model.pt")
    print("Model saved to data/sheaf_model.pt")


if __name__ == "__main__":
    train()
