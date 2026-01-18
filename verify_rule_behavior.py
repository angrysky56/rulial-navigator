import numpy as np

from rulial.engine.totalistic import Totalistic2DEngine


def int_to_rule_str(n: int) -> str:
    bin_str = format(int(n), "018b")
    b_bits = bin_str[0:9]
    s_bits = bin_str[9:18]
    born = [i for i, bit in enumerate(b_bits) if bit == "1"]
    survive = [i for i, bit in enumerate(s_bits) if bit == "1"]
    return f"B{''.join(map(str, born))}/S{''.join(map(str, survive))}"


def test_rule(rule_id: int):
    rule_str = int_to_rule_str(rule_id)
    print(f"--- Testing Rule {rule_id} -> {rule_str} ---")

    engine = Totalistic2DEngine(rule_str)

    # Run multiple seeds to be sure
    total_alive_trace = np.zeros(100)

    for i in range(5):
        # Explicit seed
        np.random.seed(42 + i)
        grid = engine.init_grid(64, 64, "random", density=0.5)

        counts = []
        for _ in range(100):
            counts.append(np.sum(grid))
            grid = engine.step(grid)

        total_alive_trace += np.array(counts)

    avg_trace = total_alive_trace / 5.0
    print(
        f"Avg Alive Count (Steps 0, 10, 50, 99): {avg_trace[0]:.1f}, {avg_trace[10]:.1f}, {avg_trace[50]:.1f}, {avg_trace[99]:.1f}"
    )

    # Check for Dynamism
    # Run one last step to compare
    next_grid = engine.step(grid)
    diff = np.sum(np.abs(grid.astype(int) - next_grid.astype(int)))
    print(f"Dynamism (Delta at step 100): {diff} pixel changes")

    # Check for death
    if avg_trace[-1] < 10:
        print("Outcome: DEATH (Ash)")
    elif avg_trace[-1] > 3000:
        print("Outcome: EXPLOSION (Chaos)")
    elif diff == 0:
        print("Outcome: STILL LIFE (Frozen)")
    else:
        print("Outcome: SUSTAINED DYNAMIC ACTIVITY (True Life)")
    print("")


if __name__ == "__main__":
    test_rule(224)  # Game of Life (Reference)
    test_rule(14449)  # The "Inverter"
    test_rule(222)  # Another Gold Filament

    # User Requested Rule: B45/S236
    # We need to test the string directly since we don't have its int ID handy
    print("--- Testing User Rule B45/S236 ---")
    engine = Totalistic2DEngine("B45/S236")
    total_alive_trace = np.zeros(100)

    # Must declare grid for scope
    grid = None

    for i in range(5):
        np.random.seed(42 + i)
        grid = engine.init_grid(64, 64, "random", density=0.5)
        counts = []
        for _ in range(100):
            counts.append(np.sum(grid))
            grid = engine.step(grid)
        total_alive_trace += np.array(counts)

    avg_trace = total_alive_trace / 5.0
    print(f"Avg Alive Count: {avg_trace[0]:.1f}, {avg_trace[-1]:.1f}")

    next_grid = engine.step(grid)
    diff = np.sum(np.abs(grid.astype(int) - next_grid.astype(int)))
    print(f"Dynamism: {diff} pixel changes")
    print("")

    # Standard Game of Life (Baseline)
    print("--- Testing Standard Life B3/S23 ---")
    engine = Totalistic2DEngine("B3/S23")
    total_alive_trace = np.zeros(100)

    grid = None

    for i in range(5):
        np.random.seed(42 + i)
        grid = engine.init_grid(64, 64, "random", density=0.5)
        counts = []
        for _ in range(100):
            counts.append(np.sum(grid))
            grid = engine.step(grid)
        total_alive_trace += np.array(counts)

    avg_trace = total_alive_trace / 5.0
    print(f"Avg Alive Count: {avg_trace[0]:.1f}, {avg_trace[-1]:.1f}")

    next_grid = engine.step(grid)
    diff = np.sum(np.abs(grid.astype(int) - next_grid.astype(int)))
    print(f"Dynamism: {diff} pixel changes")
    print("")
