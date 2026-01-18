# Rulial Navigator - Project Structure

A comprehensive map of the codebase for the Rulial Navigator system.

---

## Directory Tree

```
rulial-navigator/
│
├── src/rulial/
│   ├── cli.py                    # Main CLI entry point
│   ├── pipeline.py               # Unified analysis pipeline
│   │
│   ├── compression/              # Complexity Measurement
│   │   ├── flow.py               # Universal Compression Stack ★
│   │   ├── metrics.py            # Telemetry analyzer
│   │   ├── neural.py             # LSTM predictor
│   │   └── rigid.py              # LZMA compression
│   │
│   ├── engine/                   # Simulation Engines
│   │   ├── eca.py                # 1D Elementary CA
│   │   ├── totalistic.py         # 2D Outer-Totalistic CA
│   │   └── spacetime.py          # Causal graphs, point clouds
│   │
│   ├── mapper/                   # Topological Analysis
│   │   ├── topology.py           # Persistent homology (GUDHI)
│   │   ├── tpe.py                # T-P+E Framework ★
│   │   ├── condensate.py         # Vacuum phase detection ★
│   │   ├── atlas.py              # Rule space navigation
│   │   └── entailment.py         # Causal structure
│   │
│   ├── mining/                   # Physics Extraction
│   │   ├── extractor.py          # Particle miner
│   │   ├── collider.py           # Reaction tables
│   │   ├── synthesizer.py        # Logic gadgets (WIRE, EATER, NOT)
│   │   ├── oligon.py             # Oligon counter ★
│   │   └── query.py              # Natural language API
│   │
│   ├── navigator/                # AI Exploration
│   │   ├── titans.py             # Test-time learning ★
│   │   ├── swarm.py              # Swarm navigation
│   │   ├── gradient.py           # Gradient descent
│   │   ├── annealing.py          # Simulated annealing
│   │   └── classifier.py         # Wolfram classifier
│   │
│   ├── quantum/                  # Quantum Bridge
│   │   ├── bridge.py             # PEPS tensor network
│   │   ├── kernel.py             # Quantum kernel navigator
│   │   ├── superfluid.py         # Topological phase detection
│   │   └── zx_reducer.py         # ZX-calculus simplification
│   │
│   ├── runners/                  # Atlas Scanners
│   │   ├── probe_2d.py           # Original (Titans + TensorBridge)
│   │   ├── probe_2d_v2.py        # Simplified probe
│   │   ├── probe_2d_v3.py        # Grid scanner
│   │   └── probe_2d_v4.py        # Modern V4 scanner ★
│   │
│   └── server/                   # Web Interface
│       ├── rpc.py                # FastAPI endpoints
│       └── static/
│           └── observatory.html  # Three.js visualization
│
├── docs/                         # Documentation
│   ├── USAGE_GUIDE.md            # CLI & API reference ★
│   ├── The-Metastable-Superfluid-Membrane.md
│   ├── Emes-and-the-Glass-Floor.md
│   ├── Particles-as-Vortex-Knots.md
│   ├── Dark-Matter-as-Oligons.md
│   ├── Galactic-Tension-and-Dimension-Decay.md
│   ├── Dark-Energy-and-Hubble-Tension.md
│   ├── Quantum-Mechanics-from-Branchial-Space.md
│   ├── Vacuum-Condensate-Discovery.md
│   └── Whitepaper-Vacuum-Condensate-Phases.md
│
├── data/                         # Generated Data
│   ├── atlas_grid.json           # V1-V3 Atlas data
│   ├── atlas_v4.json             # V4 Atlas with phases
│   ├── golden_filaments.json     # Class 4 discoveries
│   └── titans_history.json       # Learning history
│
└── *.py                          # Root scripts (testing)
```

★ = Key modules

---

## Module Purposes

### compression/ — Measuring Complexity

| File         | Purpose                                                              |
| ------------ | -------------------------------------------------------------------- |
| `flow.py`    | **Universal Compression Stack** — Rigid (LZMA) + Fluid (LSTM) layers |
| `metrics.py` | Telemetry analyzer, compression ratios                               |
| `neural.py`  | LSTM-based prediction for neural compression                         |
| `rigid.py`   | LZMA-based rigid compression                                         |

### engine/ — Simulating Universes

| File            | Purpose                                       |
| --------------- | --------------------------------------------- |
| `eca.py`        | 1D Elementary Cellular Automata (rules 0-255) |
| `totalistic.py` | 2D Outer-Totalistic CA (B.../S... format)     |
| `spacetime.py`  | Causal graphs, point clouds, ASCII output     |

### mapper/ — Topological Analysis

| File            | Purpose                                                 |
| --------------- | ------------------------------------------------------- |
| `topology.py`   | **TopologyMapper** — Persistent homology, Betti numbers |
| `tpe.py`        | **T-P+E Framework** — Toroidal/Poloidal dynamics        |
| `condensate.py` | **VacuumCondensateAnalyzer** — Phase detection          |
| `atlas.py`      | AtlasMapper — Rule space navigation                     |
| `entailment.py` | EntailmentCone — Causal structure                       |

### mining/ — Physics Extraction

| File             | Purpose                                                     |
| ---------------- | ----------------------------------------------------------- |
| `extractor.py`   | **ParticleMiner** — Finds gliders, oscillators, still lifes |
| `collider.py`    | **Collider** — Tests particle interactions                  |
| `synthesizer.py` | **Synthesizer** — Identifies WIRE, EATER, NOT gates         |
| `oligon.py`      | **OligonCounter** — Counts small stable structures          |
| `query.py`       | Natural language API for AI agents                          |

### navigator/ — AI Exploration

| File            | Purpose                                              |
| --------------- | ---------------------------------------------------- |
| `titans.py`     | **TitansNavigator** — Online learning, hallucination |
| `swarm.py`      | Swarm-based parallel exploration                     |
| `gradient.py`   | Gradient descent in entropy landscape                |
| `annealing.py`  | Simulated annealing explorer                         |
| `classifier.py` | Wolfram class 1/2/3/4 classifier                     |

### quantum/ — Quantum Bridge

| File            | Purpose                                           |
| --------------- | ------------------------------------------------- |
| `bridge.py`     | **TensorBridge** — Maps CA → PEPS tensor networks |
| `kernel.py`     | Quantum kernel navigator (Qiskit)                 |
| `superfluid.py` | Topological phase detection                       |
| `zx_reducer.py` | ZX-calculus circuit simplification                |

### runners/ — Atlas Scanners

| File             | Purpose                                                  |
| ---------------- | -------------------------------------------------------- |
| `probe_2d.py`    | Original (Titans + TensorBridge + Rich UI)               |
| `probe_2d_v2.py` | Simplified classification probe                          |
| `probe_2d_v3.py` | Grid scanner (Born × Survive)                            |
| `probe_2d_v4.py` | **Modern V4** — T-P+E + Condensate + Multi-signal voting |

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     EXPLORATION LAYER                       │
│  Titans Memory ◄── Online Learning ◄── Hallucination        │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────┐
│                   SIMULATION LAYER                          │
│  ECA (1D) │ Totalistic (2D) │ Spacetime Utils               │
└─────────────────────────────┼───────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────┐
│                   ANALYSIS LAYER                            │
│  Compression Flow │ T-P+E │ Condensate │ Topology │ Quantum │
└─────────────────────────────┼───────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────┐
│                   EXTRACTION LAYER                          │
│  Particles → Reactions → Gadgets │ Oligons                  │
└─────────────────────────────┼───────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────┐
│                   INTERFACE LAYER                           │
│  CLI │ Query API │ Web Observatory                          │
└─────────────────────────────────────────────────────────────┘
```

---

## CLI Commands

| Command                                       | Purpose                   |
| --------------------------------------------- | ------------------------- |
| `uv run rulial --help`                        | Show all commands         |
| `uv run rulial entropy-flow --rule "RULE"`    | Compression flow analysis |
| `uv run rulial tpe --rule "RULE"`             | T-P+E dynamics            |
| `uv run rulial condensate --rule "RULE"`      | Vacuum phase detection    |
| `uv run rulial oligons --rule "RULE"`         | Oligon count              |
| `uv run rulial serve`                         | Start web observatory     |
| `uv run python -m rulial.runners.probe_2d_v4` | Run V4 atlas scan         |

---

## Full Documentation

See [`docs/USAGE_GUIDE.md`](docs/USAGE_GUIDE.md) for complete reference.
