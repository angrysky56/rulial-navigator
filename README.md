# Rulial Navigator: Autonomous Discovery Engine

The **Rulial Navigator** is a hybrid classical/quantum framework for autonomous exploration of computational universes. It maps the Ruliad—the infinite space of all possible rules—to discover rules capable of universal computation.

## 🌟 Key Features

### 🧠 Titans (Test-Time Learning)

- **Online Learning:** Neural memory updates during exploration, not just inference
- **Surprise-Driven:** Learns from prediction error (expected vs actual entropy)
- **Hallucination:** Predicts promising neighbors before expensive simulation

### 🔬 Universal Compression Stack

Maxwell's Demon for complexity detection:

| Layer     | Algorithm   | Detects                         |
| --------- | ----------- | ------------------------------- |
| **Rigid** | LZMA        | Exact patterns, periodicity     |
| **Fluid** | Neural LSTM | Soft patterns, prediction error |

**Navigator Signals:**

- 🔥 **FRUSTRATION** → High entropy, zero flow → Escape chaos
- ❄️ **BOREDOM** → Low entropy, zero flow → Avoid frozen
- ✨ **CURIOSITY** → Active flow → Approach complexity

### ⛏️ Physics Mining Pipeline

Automated discovery of computational physics:

```
Miner (Particles) → Collider (Reactions) → Synthesizer (Logic Gates)
```

- **Extractor:** Finds gliders, oscillators, still lifes
- **Collider:** Tests particle interactions (transmission, annihilation)
- **Synthesizer:** Identifies WIRE, EATER, NOT gates

### 🔮 Query Interface

Natural language API for AI agents:

```python
from rulial.mining.query import query_ruliad
result = query_ruliad("I need signal transmission and absorption")
```

### ⛩️ Tensor Bridge (Quantum)

- Maps 2D grids → Quantum Cluster States (PEPS)
- Computes bi-partition entanglement entropy
- Detects topological order

---

## 🚀 Installation

```bash
git clone https://github.com/yourusername/rulial-navigator.git
cd rulial-navigator
uv sync
```

**Requirements:** Python 3.11+, CUDA recommended for Titans

---

## 🕹️ Usage

### Unified Pipeline

```bash
# Analyze a single rule
uv run rulial pipeline --mode analyze --rule "B3/S23"

# Explore rule space with Titans
uv run rulial pipeline --mode explore --steps 50 --rule "B3/S23"

# Catalog Class 4 rules from atlas
uv run rulial pipeline --mode catalog

# Query the catalog
uv run rulial pipeline --mode query --query "logic capable"
```

### Compression Flow Analysis

```bash
uv run rulial entropy-flow --rule "B36/S23"
```

Output:

```
═══ Compression Flow: B36/S23 ═══
  Rigid CR: 0.0882 (final: 0.0614)
  Neural Loss: 0.4769
  Rigid Flow (dr/dt): -0.012524
  Signal: ✨ CURIOSITY
  Wolfram Class: 4
  Intrinsic Reward: 1.2955
```

### Atlas Scan

```bash
# Map the 2D rule space (Born × Survive grid)
uv run python -m rulial.runners.probe_2d_v3 --samples 200 --output atlas_grid.json
```

### Web Observatory

```bash
uv run rulial serve
# Open http://localhost:8000
```

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     EXPLORATION LAYER                       │
│  Titans Memory ◄── Swarm ◄── Gradient ◄── Annealing         │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────┐
│                   SIMULATION LAYER                          │
│  ECA (1D) │ Totalistic (2D) │ Spacetime Utils               │
└─────────────────────────────┼───────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────┐
│                   ANALYSIS LAYER                            │
│  Compression Flow │ Topology (TDA) │ Tensor Bridge (Quantum)│
└─────────────────────────────┼───────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────┐
│                   EXTRACTION LAYER                          │
│  Miner (Particles) → Collider (Reactions) → Synthesizer     │
└─────────────────────────────┼───────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────┐
│                   INTERFACE LAYER                           │
│  Query API │ Web Observatory │ CLI                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 Validation Results

| Rule                   | Compression Flow | Class | Signal       |
| ---------------------- | ---------------- | ----- | ------------ |
| B/S (empty)            | 0.0018           | 1     | ❄️ BOREDOM   |
| B12345678/S12345678    | 0.0018           | 1     | ❄️ BOREDOM   |
| **B3/S23** (Life)      | 0.0581           | 4     | ✨ CURIOSITY |
| **B36/S23** (HighLife) | 0.0614           | 4     | ✨ CURIOSITY |

---

## 📁 Project Structure

```
src/rulial/
├── compression/      # Kolmogorov complexity proxies
│   ├── flow.py       # Universal Compression Stack ★
│   ├── metrics.py    # Telemetry analyzer
│   └── neural.py     # LSTM predictor
├── engine/           # Simulation engines
│   ├── eca.py        # 1D Elementary CA
│   └── totalistic.py # 2D Totalistic CA
├── mapper/           # Topological analysis
│   └── topology.py   # Persistent homology (GUDHI)
├── mining/           # Physics extraction ★
│   ├── extractor.py  # Particle miner
│   ├── collider.py   # Reaction tables
│   ├── synthesizer.py# Logic gadgets
│   └── query.py      # NL interface
├── navigator/        # AI agents
│   └── titans.py     # Test-time learning ★
├── quantum/          # Quantum bridge
│   └── bridge.py     # PEPS tensor network
├── pipeline.py       # Unified pipeline ★
└── cli.py            # Command line interface
```

---

## 🔮 Roadmap

- [x] Phase 1-10: Core Engine + Quantum Layer
- [x] Phase 11: 2D Atlas of Ignorance
- [x] Phase 12: Particle Miner
- [x] Phase 13: Collider (Reaction Tables)
- [x] Phase 14: Synthesizer (Logic Gadgets)
- [x] Phase 15: Query Interface
- [x] Phase 16: Universal Compression Stack
- [ ] Phase 17: Geodesic Proof Paths
- [ ] Phase 18: Multi-Rule Circuit Synthesis

---

## 📜 Philosophy: The Metastable Superfluid Membrane

This project is grounded in the hypothesis that the vacuum is not empty but a **quantum condensate**—a Metastable Superfluid Membrane with elastic and topological properties.

> _"We are in a single membrane and this is all just unresolved knots, virtual particles, solitons, dissolving in entropy towards the resolving void."_

### Core Tenets

| Physical Concept        | Ruliad Mapping                               | Implementation                                   |
| ----------------------- | -------------------------------------------- | ------------------------------------------------ |
| **Matter as Knots**     | Particles are topological defects (solitons) | `mining/extractor.py` finds gliders, oscillators |
| **Superfluid Rigidity** | Lorentz invariance as emergent "glass floor" | `compression/flow.py` measures compressibility   |
| **Entropy Flow**        | Direction toward/away from void equilibrium  | Navigator signals: CURIOSITY vs BOREDOM          |
| **Tension Network**     | Dark Matter as cosmic string scaffolding     | Entailment cone coarse-graining                  |
| **Acoustic Metric**     | Gravity as effective geometry of fluid       | Tensor Bridge PEPS entropy                       |

### The Navigator's Role

The Universal Compression Stack acts as **Maxwell's Demon**:

- ❄️ **Ice** (low entropy, static) = Frozen vacuum = Class 1/2 = BOREDOM
- 🔥 **Fire** (high entropy, static) = Chaotic vacuum = Class 3 = FRUSTRATION
- ✨ **Gold** (flow, dynamic) = Metastable edge = Class 4 = CURIOSITY

Class 4 rules represent **structures that resist dissolution**—knots that persist in the entropy flow toward the void.

See: [`docs/The-Metastable-Superfluid-Membrane.md`](docs/The-Metastable-Superfluid-Membrane.md) for the full theoretical framework.

---

## License

MIT
