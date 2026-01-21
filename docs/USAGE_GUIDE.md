# Rulial Navigator: The Field Manual

**A Guide to Mapping the Computational Universe**

---

## Part I: Project Context

### 1. What is the Ruliad?
The **Ruliad** is the abstract space of *all possible computational rules*. Imagine a library containing every possible universe's laws of physics. Most of these "books" describe empty universes or chaotic static, but a rare few describe universes rich with structure, logic, and complexity.

This project, the **Rulial Navigator**, is an autonomous agent designed to explore this infinite library. Its mission is to find the "interesting" books—the rules that support complex structures akin to life and matter.

### 2. The Goal: Finding "Class 4"
Wolfram classified cellular automata into 4 classes:
1.  **Class 1**: Dies out (Boring).
2.  **Class 2**: Periodic/Stable (Boring).
3.  **Class 3**: Chaotic (Too unpredictable).
4.  **Class 4**: **Complex** (The "Goldilocks" zone).

**Class 4** rules are capable of universal computation. They support "gliders" (particles that move and interact) and stable structures. Our goal is to map the distribution of these Class 4 rules in the Ruliad.

### 3. The Physics of Rule Space
We use advanced mathematical tools to identify these rules without running them for eternity:

*   **Topological Analysis (Sheaf Theory)**: We measure "Harmonic Overlap" ($H$). Rules with $0.3 \le H \le 0.6$ are in the "Goldilocks Zone"—balanced between order and chaos.
*   **Cosmological Analysis (Condensates)**: Some rules behave like a "Big Bang," expanding from a single cell to fill space. We call these **Vacuum Condensates**.
*   **Particle Physics (Oligons)**: Other rules support stable, isolated particles called **Oligons**. These are the building blocks of "matter" in these toy universes.

---

## Part II: The Unified Pipeline

We have consolidated all tools into a single command-line interface: `rulial`.

### 1. Launching the Discovery Engine
To start the autonomous exploration agent:

```bash
uv run rulial explore
```

**What this does:**
1.  **Bootstraps Titans**: Loads the Neural Memory (Titans) from your existing database.
2.  **Continuous Exploration**:
    *   **Hallucinate**: The AI predicts a new rule vector that might be interesting.
    *   **Filter**: Quick combinatorial check (LLL) to discard obviously boring rules.
    *   **Simulate & Analyze**: Runs the rule on GPU to measure its Physics (Sheaf, Fractal).
    *   **Learn**: Updates the Titans memory based on how "surprising" the result was.
    *   **Save**: Persists findings to `data/atlas_full_v6_gpu.db`.

**Options:**
*   `--steps N`: Run for N steps (default: infinite).
*   `--db PATH`: Use a different database file.

---

## Part III: Analysis Tools

Once you have mapped parts of the Ruliad, you need to understand what you've found.

### 1. Global Status
See how much of the universe you have mapped and what you have found:

```bash
uv run rulial analyze stats
```
*   **Goldilocks Count**: Number of complex candidate rules found.
*   **Coverage**: Total unique rules explored.

### 2. Finding Candidates
List the top "Class 4" candidates (highest complexity scores):

```bash
uv run rulial analyze goldilocks --limit 20
```

### 3. Deep Dive Inspection
When you find a specific rule of interest (e.g., `B07/S457`), run a full physics simulation:

```bash
uv run rulial inspect B07/S457
```

**Output Explanation:**
*   **Harmonic Overlap ($H$)**: Complexity score. ~0.5 is ideal.
*   **Fractal Dimension ($D$)**: Structure complexity. ~1.6 suggests rich texture.
*   **Cosmological Phase**:
    *   `VACUUM CONDENSATE`: Expands to fill space (a "Universe").
    *   `PARTICLE-BASED`: Empty space with distinct objects.
*   **Particle Zoo (Oligons)**: Counts the number of stable species (Still lifes, Oscillators) this rule supports.

---

## Part IV: Visualization

To see the "Highways of Complexity" in the rule space, we use **Cayley**, a graph database visualization tool.

### 1. Export the Map
Convert your SQLite atlas into a Graph format (N-Quads):

```bash
uv run rulial analyze export --output data/rule_space.nq.gz
```

### 2. Load in Cayley
(Assuming you have Cayley installed or running via Docker):

```bash
# Example Docker command
docker run -d -p 64210:64210 \
  -v $(pwd)/data:/data \
  cayleygraph/cayley:latest \
  -c /data/cayley.yml \
  --load=/data/rule_space.nq.gz
```

Open `http://localhost:64210` in your browser.

### 3. Visual Queries (Gizmo)
Paste these into the **Visualize** tab to see connections:

**Show "Life-Like" Neighbors:**
```javascript
g.V("<rule:B3/S23>").Both("<pred:connected_to>").All()
```

**Show the Goldilocks Highway:**
```javascript
// Find connections between complex rules
g.V().Has("<pred:harmonic_overlap>", gt("0.4")).Tag("source").Both("<pred:connected_to>").Has("<pred:harmonic_overlap>", gt("0.4")).Tag("target").All()
```

---

## Part V: The Turing Machine Corps
*Mapping the computational paths of Non-Deterministic Machines.*

While 2D Cellular Automata explore the **landscape**, Turing Machines explore the **paths**.
We use Non-Deterministic Turing Machines (NDTMs) to map all possible timelines of a computation.

### 1. Explore a Rule's Multiway Graph
Visualize the branching timelines of a Turing Machine rule.

```bash
# Explore Rule 2507 (Deterministic but active)
uv run rulial tm-explore --rule-code 2507 --steps 10

# Explore Rule 2506 (Simple)
uv run rulial tm-explore --rule-code 2506
```

### 2. Understanding the Output
- **States**: The non-deterministic states at each time step.
- **Red Digit**: The current position of the machine's head.
- **Branching**: As steps increase, the number of parallel states may grow (for NDTMs).

> [!TIP]
> This engine supports full Non-Deterministic branching, allowing you to trace the "Actual Paths" of computation across the Rulial Multiway Graph.


---

## Part VI: Rulial Function Mining
*Extracting useful algorithms from the infinite rule space.*

Don't just watch the machines—put them to work.
The **Function Miner** searches the Rulial Multiway Graph to find specific rules and paths that solve a problem you define.

### 1. Define Your Problem
You provide an **Input** and a Desired **Target**.
*   Input: `01` (Binary 1)
*   Target: `11` (binary 3? or just bit flipping?)
*   Goal: Find a machine that performs this transformation.

### 2. Run the Miner
```bash
# Find a rule that transforms "01" into "11" (Bit Flipper)
# Check the first 200 rules, searching up to 5 steps deep.
uv run rulial tm-mine --input-tape "01" --target-tape "11" --rule-limit 200 --max-steps 5
```

### 3. Interpret Results
```text
FOUND 102 SOLUTIONS!
Rule 1 found in 1 steps.
Rule 106 found in 3 steps.
```
*   **Fast solutions (1 step)**: Likely simple lookup-table behavior.
*   **Deep solutions (3+ steps)**: Indicate an algorithmic process (moving head, rewriting).

> [!TIP]
> This is **Program Synthesis**. You are discovering algorithms that exist naturally in the Ruliad.

---

## Appendix: Key Files
*   `src/rulial/pipeline.py`: The brain of the autonomous agent.
*   `src/rulial/navigator/titans.py`: The Neural Memory architecture.
*   `src/rulial/mapper/sheaf_gpu.py`: The GPU-accelerated Physics engine.
*   `src/rulial/analytics/analyzer.py`: The Data Analysis engine.
