# Rulial Navigator - Project Structure

A comprehensive map of the codebase for the Rulial Navigator system.

## Directory Tree

```
rulial-navigator/
├── src/rulial/
│   ├── cli.py                    # Main CLI entry point
│   │
│   ├── compression/              # Kolmogorov Complexity & Metrics
│   │   ├── metrics.py            # TelemetryAnalyzer (compression ratios)
│   │   ├── neural.py             # Neural compression baseline
│   │   └── rigid.py              # LZMA rigid compression
│   │
│   ├── engine/                   # CA Simulation Engines
│   │   ├── eca.py                # 1D Elementary Cellular Automata
│   │   ├── spacetime.py          # SpacetimeUtil (causal graphs, point clouds)
│   │   └── totalistic.py         # 2D Totalistic CA (B.../S... rules)
│   │
│   ├── mapper/                   # Topological Analysis
│   │   ├── atlas.py              # AtlasMapper (rule space navigation)
│   │   ├── entailment.py         # EntailmentCone (causal structure)
│   │   └── topology.py           # TopologyMapper (TDA, Betti numbers)
│   │
│   ├── mining/                   # Physics Extraction (Phases 12-15)
│   │   ├── extractor.py          # ParticleMiner (gliders, blocks, oscillators)
│   │   ├── collider.py           # Collider (interaction algebra, reactions)
│   │   ├── synthesizer.py        # Synthesizer (logic gadget construction)
│   │   └── query.py              # RuliadQuery (natural language API)
│   │
│   ├── navigator/                # AI Agents
│   │   ├── titans.py             # TitansMemory (test-time learning)
│   │   ├── swarm.py              # Swarm navigation
│   │   ├── gradient.py           # Gradient-based exploration
│   │   ├── annealing.py          # Simulated annealing
│   │   └── classifier.py         # Wolfram class classifier
│   │
│   ├── quantum/                  # Quantum Bridge
│   │   ├── bridge.py             # TensorBridge (PEPS, entanglement entropy)
│   │   ├── kernel.py             # Quantum kernel methods
│   │   ├── superfluid.py         # Topological phase detection
│   │   └── zx_reducer.py         # ZX-calculus simplification
│   │
│   ├── runners/                  # Execution Runners
│   │   ├── probe_2d.py           # Original 2D probe (Titans + TensorBridge)
│   │   ├── probe_2d_v2.py        # Simplified probe
│   │   └── probe_2d_v3.py        # Atlas mapper (Born/Survive grid scan)
│   │
│   └── server/                   # Web Server
│       ├── rpc.py                # FastAPI endpoints
│       └── static/
│           └── observatory.html  # 3D/2D visualization (Three.js)
│
├── docs/                         # Documentation & Theory
│   ├── Mapping-Infinite-Rulial-Space.md    # Core specification
│   ├── The_Ruliad.md                       # Ruliad theory survey
│   ├── Geometry-of-the-Quantum-Branchial-Graph.md
│   ├── Causal-Invariance-and-the-Convergence-of-Multiway-Systems.md
│   └── topological_maps_of_computational_evolution.md
│
├── *.py                          # Root scripts
│   ├── mine_life.py              # Miner test (Game of Life)
│   ├── test_miner.py             # Glider detection unit test
│   ├── debug_engine.py           # Engine dynamics debugger
│   ├── verify_ground_truth.py    # Classification calibration
│   ├── verify_rule_behavior.py   # Engine behavior verification
│   ├── merge_atlas.py            # Combine partial atlas scans
│   └── replay_filaments.py       # Golden filament replay
│
└── data/
    ├── atlas_grid.json           # 2D Atlas data (Born/Survive grid)
    ├── golden_filaments.json     # Discovered Class 4 rules
    └── titans_history.json       # Titans learning history
```

---

## Module Purposes

### 1. `compression/` - Measuring Complexity

| File         | Purpose                                                    |
| ------------ | ---------------------------------------------------------- |
| `metrics.py` | `TelemetryAnalyzer` - computes compression ratio, progress |
| `neural.py`  | Neural network-based compression baseline                  |
| `rigid.py`   | LZMA-based rigid compression for Kolmogorov proxy          |

### 2. `engine/` - Simulating Universes

| File            | Purpose                                                  |
| --------------- | -------------------------------------------------------- |
| `eca.py`        | 1D Elementary Cellular Automata (Wolfram rules 0-255)    |
| `totalistic.py` | 2D Totalistic CA engine (B.../S... format, e.g., B3/S23) |
| `spacetime.py`  | Utilities for causal graphs, point clouds, ASCII output  |

### 3. `mapper/` - Analyzing Topology

| File            | Purpose                                               |
| --------------- | ----------------------------------------------------- |
| `topology.py`   | `TopologyMapper` - Persistent Homology, Betti numbers |
| `entailment.py` | `EntailmentCone` - Causal structure and logical depth |
| `atlas.py`      | `AtlasMapper` - Rule space navigation and caching     |

### 4. `mining/` - Extracting Physics (NEW: Phases 12-15)

| File             | Purpose                                                     |
| ---------------- | ----------------------------------------------------------- |
| `extractor.py`   | `ParticleMiner` - Finds gliders, blocks, oscillators        |
| `collider.py`    | `Collider` - Tests particle interactions, reaction tables   |
| `synthesizer.py` | `Synthesizer` - Identifies logic gadgets (WIRE, EATER, NOT) |
| `query.py`       | `RuliadQuery` - Natural language API for AI agents          |

### 5. `navigator/` - AI Exploration Agents

| File            | Purpose                                           |
| --------------- | ------------------------------------------------- |
| `titans.py`     | `TitansMemory` - Test-time learning neural memory |
| `swarm.py`      | Swarm-based parallel exploration                  |
| `gradient.py`   | Gradient descent in entropy landscape             |
| `annealing.py`  | Simulated annealing explorer                      |
| `classifier.py` | Wolfram class 1/2/3/4 classifier                  |

### 6. `quantum/` - Quantum Bridge

| File            | Purpose                                                |
| --------------- | ------------------------------------------------------ |
| `bridge.py`     | `TensorBridge` - Maps CA grids to PEPS tensor networks |
| `kernel.py`     | Quantum kernel methods for similarity                  |
| `superfluid.py` | Topological phase detection                            |
| `zx_reducer.py` | ZX-calculus circuit simplification                     |

### 7. `runners/` - Execution Runners

| File             | Purpose                                          |
| ---------------- | ------------------------------------------------ |
| `probe_2d.py`    | Full-featured probe (Titans + TensorBridge + UI) |
| `probe_2d_v2.py` | Simplified probe (classification metrics only)   |
| `probe_2d_v3.py` | Atlas mapper (2D Born/Survive grid scanner)      |

### 8. `server/` - Web Interface

| File               | Purpose                                                     |
| ------------------ | ----------------------------------------------------------- |
| `rpc.py`           | FastAPI server with `/atlas/history`, `/simulate` endpoints |
| `observatory.html` | Three.js visualization (2D heatmap + 3D voxel view)         |

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          EXPLORATION LAYER                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │  Titans  │    │  Swarm   │    │ Gradient │    │ Annealing│           │
│  │  Memory  │ ◄──│ Explorer │ ◄──│ Descent  │ ◄──│ Explorer │           │
│  └────┬─────┘    └──────────┘    └──────────┘    └──────────┘           │
│       │                                                                 │
│       ▼                                                                 │
│  ┌───────────────────────────────────────────────────────────┐          │
│  │                      SIMULATION LAYER                     │          │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │          │
│  │  │     ECA     │    │  Totalistic │    │  Spacetime  │    │          │
│  │  │  (1D Rules) │    │  (2D Rules) │    │   Utilities │    │          │
│  │  └─────────────┘    └──────┬──────┘    └─────────────┘    │          │
│  └────────────────────────────┼──────────────────────────────┘          │
│                               │                                         │
│       ┌───────────────────────┼─────────────────────────────┐           │
│       │                ANALYSIS LAYER                       │           │
│       │  ┌──────────┐    ┌──────────┐    ┌──────────┐       │           │
│       │  │Compression│   │ Topology │    │  Quantum │       │           │
│       │  │  Metrics │    │   TDA    │    │  Bridge  │       │           │
│       │  └──────────┘    └──────────┘    └──────────┘       │           │
│       └─────────────────────────┬───────────────────────────┘           │
│                                 │                                       │
│       ┌─────────────────────────┼────────────────────────────┐          │
│       │              EXTRACTION LAYER (NEW)                  │          │
│       │  ┌──────────┐    ┌──────────┐    ┌──────────┐        │          │
│       │  │  Miner   │───▶│ Collider │───▶│Synthesizer│       │          │
│       │  │(Particles)│   │(Reactions)│   │ (Gadgets) │       │          │
│       │  └──────────┘    └──────────┘    └────┬─────┘        │          │
│       └───────────────────────────────────────┼──────────────┘          │
│                                               │                         │
│       ┌───────────────────────────────────────┼───────────────┐         │
│       │                   QUERY LAYER                         │         │
│       │               ┌──────────────┐                        │         │
│       │               │ RuliadQuery  │◄── "I need a NOT gate" │         │
│       │               │   (NL API)   │                        │         │
│       │               └──────────────┘                        │         │
│       └───────────────────────────────────────────────────────┘         │
│                                                                         │
│       ┌───────────────────────────────────────────────────────┐         │
│       │                   OUTPUT LAYER                        │         │
│       │  ┌────────────┐    ┌────────────┐    ┌────────────┐   │         │
│       │  │ Atlas JSON │    │ Observatory│    │  Filaments │   │         │
│       │  │  (2D Map)  │    │   (WebUI)  │    │  (Catalog) │   │         │
│       │  └────────────┘    └────────────┘    └────────────┘   │         │
│       └───────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key Integrations Yet To Complete

| Integration             | Status           | Notes                                               |
| ----------------------- | ---------------- | --------------------------------------------------- |
| Titans → Miner/Collider | 🔴 Not Connected | Titans finds rules, Miner analyzes them             |
| probe_2d_v3 → Query     | 🔴 Not Connected | Atlas data should feed Query cache                  |
| TensorBridge → Mining   | 🔴 Not Connected | Entanglement entropy could guide particle detection |
| Observatory → Mining    | 🔴 Not Connected | Click a rule in UI → Show its particles             |

---

## Running Commands

```bash
# Start the Observatory Web Server
uv run rulial serve

# Run the 2D Atlas Scan
uv run python -m rulial.runners.probe_2d_v3 --samples 200 --output atlas_grid.json

# Run the full Titans-powered probe
uv run python -m rulial.runners.probe_2d --mode titans

# Analyze a specific rule
uv run python -c "from rulial.mining.query import query_ruliad; print(query_ruliad('Analyze B3/S23'))"

# Test the Miner
uv run python test_miner.py
```
