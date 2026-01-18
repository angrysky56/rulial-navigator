# Rulial Navigator: Complete Usage Guide

A comprehensive guide for AI agents and code-savvy users.

---

## Table of Contents

1. [Installation](#installation)
2. [CLI Reference](#cli-reference)
3. [Python API](#python-api)
4. [Core Concepts](#core-concepts)
5. [Workflows](#workflows)
6. [Data Formats](#data-formats)

---

## Installation

```bash
git clone https://github.com/yourusername/rulial-navigator.git
cd rulial-navigator
uv sync
```

**Requirements:** Python 3.11+, CUDA recommended for Titans

**Optional dependencies:**

- `qiskit` + `qiskit-machine-learning` for quantum kernel
- `gudhi` for persistent homology

---

## CLI Reference

### Core Commands

```bash
# View all commands
uv run rulial --help
```

### Analysis Commands

| Command        | Description                 | Example                                          |
| -------------- | --------------------------- | ------------------------------------------------ |
| `entropy-flow` | Compression flow analysis   | `uv run rulial entropy-flow --rule "B3/S23"`     |
| `tpe`          | T-P+E dynamics analysis     | `uv run rulial tpe --rule "B36/S23"`             |
| `oligons`      | Count stable structures     | `uv run rulial oligons --rule "B3/S23"`          |
| `condensate`   | Vacuum condensate detection | `uv run rulial condensate --rule "B078/S012478"` |

### Pipeline Commands

```bash
# Analyze a single rule (full pipeline)
uv run rulial pipeline --mode analyze --rule "B3/S23"

# Explore with Titans agent
uv run rulial pipeline --mode explore --steps 50 --rule "B3/S23"

# Catalog Class 4 rules from atlas
uv run rulial pipeline --mode catalog

# Natural language query
uv run rulial pipeline --mode query --query "logic capable"
```

### Atlas Scanning

```bash
# V4 Scanner (recommended)
uv run python -m rulial.runners.probe_2d_v4 --mode quick --samples 200

# Modes:
#   quick     - Random sampling (fast)
#   full      - Systematic grid (comprehensive)
#   region    - Targeted B/S range
#   condensate - Focus on B0 rules

# Options:
#   --samples N      Number of rules to scan
#   --output FILE    Output JSON file
#   --grid-size N    Simulation grid size
#   --steps N        Simulation steps
```

### Web Observatory

```bash
uv run rulial serve
# Open http://localhost:8000
```

---

## Python API

### Quick Start

```python
from rulial.engine.totalistic import Totalistic2DEngine

# Simulate Game of Life
engine = Totalistic2DEngine("B3/S23")
history = engine.simulate(64, 64, 100, "random", density=0.3)
print(f"Final population: {history[-1].sum()}")
```

### Compression Flow Analysis

```python
from rulial.compression.flow import CompressionFlowAnalyzer

analyzer = CompressionFlowAnalyzer()
result = analyzer.analyze("B36/S23")

print(f"Signal: {result.signal.name}")
print(f"Wolfram Class: {result.wolfram_class}")
print(f"Compression Ratio: {result.mean_rigid_ratio:.4f}")
```

### T-P+E Framework

```python
from rulial.mapper.tpe import TPEAnalyzer

tpe = TPEAnalyzer()
result = tpe.analyze("B3/S23")

print(f"Toroidal (T): {result.toroidal:.3f}")
print(f"Poloidal (P): {result.poloidal:.3f}")
print(f"Emergence (E): {result.emergence:.4f}")
print(f"Mode: {result.dominant_mode}")
```

### Vacuum Condensate Detection

```python
from rulial.mapper.condensate import VacuumCondensateAnalyzer

analyzer = VacuumCondensateAnalyzer()
result = analyzer.analyze("B078/S012478")

print(f"Is Condensate: {result.is_condensate}")
print(f"Equilibrium Density: {result.equilibrium_density:.1%}")
print(f"Single Cell → {result.expansion_factor:.0f} cells")
```

### Oligon Census

```python
from rulial.mining.oligon import OligonCounter

counter = OligonCounter()
result = counter.count("B3/S23")

print(f"Still Lifes: {result.still_lifes}")
print(f"Total Oligons: {result.total_oligons}")
print(f"Density: {result.density:.2f} per 100 cells")
```

### Particle Mining

```python
from rulial.mining.extractor import ParticleMiner

miner = ParticleMiner("B3/S23")
particles = miner.mine()

for p in particles:
    print(f"{p.name}: period={p.period}, velocity={p.velocity}")
```

### Topology (Persistent Homology)

```python
import numpy as np
from rulial.mapper.topology import TopologyMapper

mapper = TopologyMapper()
# Needs spacetime array (T, H, W)
spacetime = np.stack(history, axis=0)
result = mapper.compute_persistence(spacetime)

print(f"β₀ (components): {result.betti_0}")
print(f"β₁ (loops): {result.betti_1}")
print(f"Persistence entropy: {result.persistence_entropy:.4f}")
```

### Unified Pipeline

```python
from rulial.pipeline import UnifiedPipeline

pipe = UnifiedPipeline()

# Analyze single rule
result = pipe.analyze_rule("B3/S23")
print(result.summary())

# Natural language query
response = pipe.query("find logic capable rules")
print(response)
```

### Titans Navigation (Online Learning)

```python
from rulial.navigator.titans import TitansNavigator
import numpy as np

nav = TitansNavigator(rule_size_bits=18)

# Convert rule to vector
rule_vec = np.array([0,0,0,1,0,0,0,0,0, 0,0,1,1,0,0,0,0,0], dtype=np.float32)

# Probe and learn
entropy = 0.5
surprise = nav.probe_and_learn(rule_vec, entropy)

# Hallucinate promising neighbors
next_vec, predicted_entropy = nav.hallucinate_neighbors(rule_vec)
```

---

## Core Concepts

### Wolfram Classes

| Class | Behavior        | Example |
| ----- | --------------- | ------- |
| 1     | Dies out        | B/S     |
| 2     | Periodic/stable | B2/S    |
| 3     | Chaotic         | B1/S1   |
| 4     | Complex         | B3/S23  |

### Navigator Signals

| Signal         | Meaning              | Action   |
| -------------- | -------------------- | -------- |
| 🔥 FRUSTRATION | High entropy, chaos  | Escape   |
| ❄️ BOREDOM     | Low entropy, frozen  | Escape   |
| ✨ CURIOSITY   | Active flow, complex | Approach |

### T-P+E Framework

- **Toroidal (T):** Expansion, divergence, fragmentation
- **Poloidal (P):** Contraction, convergence, mass formation
- **Emergence (E):** E = (T·P) × |T-P|

Maximum emergence occurs when T ≈ P ≈ 0.5.

### Phase Classification

| Phase        | Description                  | Signature                   |
| ------------ | ---------------------------- | --------------------------- |
| `particle`   | Isolated gliders/oscillators | has_oligons, not condensate |
| `condensate` | Coherent membrane            | is_condensate               |
| `hybrid`     | Both properties              | rare                        |

---

## Workflows

### 1. Discover Interesting Rules

```bash
# Scan for Class 4 rules
uv run python -m rulial.runners.probe_2d_v4 --mode quick --samples 500 --output discovery.json

# Check results
cat discovery.json | jq '.[] | select(.wolfram_class == 4) | .rule_str'
```

### 2. Deep Analysis of a Rule

```python
from rulial.compression.flow import CompressionFlowAnalyzer
from rulial.mapper.tpe import TPEAnalyzer
from rulial.mapper.condensate import VacuumCondensateAnalyzer
from rulial.mining.oligon import OligonCounter

rule = "B078/S012478"

# Full analysis
flow = CompressionFlowAnalyzer().analyze(rule)
tpe = TPEAnalyzer().analyze(rule)
cond = VacuumCondensateAnalyzer().analyze(rule)
olig = OligonCounter().count(rule)

print(flow.summary())
print(tpe.summary())
print(cond.summary())
print(olig.summary())
```

### 3. Find Condensate Rules

```bash
# Focus on B0 rules (likely condensates)
uv run python -m rulial.runners.probe_2d_v4 --mode condensate --samples 200

# Filter results
cat atlas_v4.json | jq '.[] | select(.is_condensate == true)'
```

### 4. Query for Specific Properties

```python
from rulial.mining.query import query_ruliad

# Natural language query
result = query_ruliad("I need signal transmission and absorption")
print(result)
```

---

## Data Formats

### Atlas V4 JSON

```json
{
  "rule_str": "B3/S23",
  "b_set": "3",
  "s_set": "23",
  "x": 8,
  "y": 12,
  "compression_ratio": 0.0581,
  "signal": "CURIOSITY",
  "toroidal": 0.609,
  "poloidal": 0.531,
  "emergence": 0.0251,
  "tpe_mode": "balanced",
  "is_condensate": false,
  "equilibrium_density": 0.039,
  "expansion_factor": 0,
  "betti_1": 15,
  "final_population": 1024,
  "wolfram_class": 4,
  "phase": "particle"
}
```

### Rule String Format

```
B{born}/S{survive}
```

- `B`: Digits 0-8 specifying birth conditions
- `S`: Digits 0-8 specifying survival conditions

Examples:

- `B3/S23`: Game of Life
- `B36/S23`: HighLife
- `B078/S012478`: Condensate example

---

## Key Files

| Path                                | Description                |
| ----------------------------------- | -------------------------- |
| `src/rulial/cli.py`                 | CLI entry point            |
| `src/rulial/pipeline.py`            | Unified analysis pipeline  |
| `src/rulial/compression/flow.py`    | Compression flow analyzer  |
| `src/rulial/mapper/tpe.py`          | T-P+E framework            |
| `src/rulial/mapper/condensate.py`   | Vacuum condensate analyzer |
| `src/rulial/mining/oligon.py`       | Oligon counter             |
| `src/rulial/mining/extractor.py`    | Particle miner             |
| `src/rulial/runners/probe_2d_v4.py` | Atlas scanner              |
| `src/rulial/navigator/titans.py`    | Online learning agent      |

---

## Theoretical Documentation

| Document                                      | Topic                    |
| --------------------------------------------- | ------------------------ |
| `docs/The-Metastable-Superfluid-Membrane.md`  | Core MSM theory          |
| `docs/Emes-and-the-Glass-Floor.md`            | Speed of light emergence |
| `docs/Particles-as-Vortex-Knots.md`           | Mass as causal flux      |
| `docs/Dark-Matter-as-Oligons.md`              | Tension network          |
| `docs/Vacuum-Condensate-Discovery.md`         | Condensate phases        |
| `docs/Whitepaper-Vacuum-Condensate-Phases.md` | Research paper           |

---

## For AI Agents

### Recommended Analysis Sequence

1. **Quick classification:** `entropy-flow --rule "RULE"`
2. **Dynamics check:** `tpe --rule "RULE"`
3. **Phase determination:** `condensate --rule "RULE"`
4. **Structure inventory:** `oligons --rule "RULE"`

### Key Decision Points

- **is_condensate = True**: Rule forms coherent membrane, no isolated particles
- **tpe_mode = balanced**: Complex dynamics, likely Class 4
- **betti_1 > 20**: Rich topological structure
- **signal = CURIOSITY**: Active information flow
