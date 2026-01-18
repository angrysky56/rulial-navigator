# Rulial Navigator - Project Structure

A comprehensive map of the codebase for the Rulial Navigator system.

**Last Updated:** 2026-01-18

---

## Directory Tree

```
rulial-navigator/
│
├── README.md                     # Project overview & research highlights
├── PROJECT_STRUCTURE.md          # This file
├── pyproject.toml               # Dependencies & metadata
├── uv.lock                      # Dependency lock file
│
├── atlas_v4.json                # Primary atlas data (200 rules)
├── atlas_v4_condensate.json     # B0-focused condensate data (50 rules)
├── atlas_v4.db                  # SQLite database (persistent)
│
├── src/rulial/
│   ├── cli.py                   # Main CLI entry point
│   ├── pipeline.py              # Unified analysis pipeline
│   │
│   ├── compression/             # Complexity Measurement
│   │   ├── flow.py              # Universal Compression Stack ★
│   │   ├── metrics.py           # Telemetry analyzer
│   │   ├── neural.py            # LSTM predictor
│   │   └── rigid.py             # LZMA compression
│   │
│   ├── engine/                  # Simulation Engines
│   │   ├── eca.py               # 1D Elementary CA
│   │   ├── totalistic.py        # 2D Outer-Totalistic CA
│   │   └── spacetime.py         # Causal graphs, point clouds
│   │
│   ├── mapper/                  # Topological & Sheaf Analysis
│   │   ├── topology.py          # Persistent homology (GUDHI)
│   │   ├── tpe.py               # T-P+E Framework ★
│   │   ├── condensate.py        # Vacuum phase detection ★
│   │   ├── sheaf.py             # Cellular Sheaf Theory ★ NEW
│   │   ├── atlas.py             # SQLite atlas (persistent) ★
│   │   └── entailment.py        # Causal structure
│   │
│   ├── mining/                  # Physics Extraction
│   │   ├── extractor.py         # Particle miner
│   │   ├── collider.py          # Reaction tables
│   │   ├── synthesizer.py       # Logic gadgets (WIRE, EATER, NOT)
│   │   ├── oligon.py            # Oligon counter ★
│   │   └── query.py             # Natural language API
│   │
│   ├── navigator/               # AI Exploration
│   │   ├── titans.py            # Test-time learning ★
│   │   ├── swarm.py             # Swarm navigation
│   │   ├── gradient.py          # Gradient descent
│   │   ├── annealing.py         # Simulated annealing
│   │   └── classifier.py        # Wolfram classifier
│   │
│   ├── quantum/                 # Quantum Bridge
│   │   ├── bridge.py            # PEPS tensor network
│   │   ├── kernel.py            # Quantum kernel navigator
│   │   ├── superfluid.py        # Topological phase detection
│   │   └── zx_reducer.py        # ZX-calculus simplification
│   │
│   ├── runners/                 # Atlas Scanners
│   │   ├── probe_2d.py          # Original (Titans + TensorBridge)
│   │   ├── probe_2d_v2.py       # Simplified probe
│   │   ├── probe_2d_v3.py       # Grid scanner
│   │   ├── probe_2d_v4.py       # Modern V4 scanner ★
│   │   ├── scan_v4.py           # Full pipeline + SQLite ★ NEW
│   │   ├── universality_test.py # Non-totalistic proof ★ NEW
│   │   └── investigate_particle.py # Glider detection ★ NEW
│   │
│   └── server/                  # Web Interface
│       ├── rpc.py               # FastAPI endpoints
│       └── static/
│           └── observatory.html # Three.js visualization
│
├── scripts/                     # Replication Scripts
│   ├── replicate_all.py         # Full replication suite ★
│   ├── analysis.py              # Condensate/S-parameter stats
│   ├── analyze_rule.py          # Single rule analysis
│   ├── visualize.py             # Figure generation
│   └── README.md                # Scripts documentation
│
├── docs/                        # Documentation
│   ├── USAGE_GUIDE.md           # CLI & API reference ★
│   ├── RESEARCH_STATUS.md       # Gap tracking ★
│   ├── Whitepaper-Vacuum-Condensate-Phases.md ★
│   ├── Sheaf-Theory-Connection.md ★ NEW
│   ├── visualizations/          # Generated figures ★ NEW
│   │   ├── fig_goldilocks_zone.png
│   │   ├── fig_monodromy_histogram.png
│   │   └── ...
│   ├── development_tests_archived/  # Archived dev scripts
│   │   └── data_archived/           # Archived JSON data
│   └── [theoretical docs...]
│
├── data/                        # Runtime data
└── cli/                         # CLI tools
```

★ = Key modules    NEW = Added 2026-01-18

---

## New Modules (2026)

### mapper/sheaf.py — Cellular Sheaf Analysis

| Component | Purpose |
|-----------|---------|
| `SheafAnalyzer` | Sparse matrix sheaf Laplacian |
| `_compute_monodromy()` | Phase classification (Φ = ±1) |
| `_compute_hodge_decomposition()` | Harmonic overlap (H) |
| `analyze()` | Returns `SheafAnalysis` dataclass |

### runners/ — New Scanners

| File | Purpose |
|------|---------|
| `scan_v4.py` | Full pipeline → SQLite database |
| `universality_test.py` | Proves B0→Condensate in non-totalistic rules |
| `investigate_particle.py` | Finds gliders, oscillators, still lifes |

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

### mapper/ — Topological & Sheaf Analysis

| File            | Purpose                                                 |
| --------------- | ------------------------------------------------------- |
| `topology.py`   | **TopologyMapper** — Persistent homology, Betti numbers |
| `tpe.py`        | **T-P+E Framework** — Toroidal/Poloidal dynamics        |
| `condensate.py` | **VacuumCondensateAnalyzer** — Phase detection          |
| `sheaf.py`      | **SheafAnalyzer** — Monodromy, harmonic overlap ★ NEW   |
| `atlas.py`      | **Atlas** — SQLite persistence ★ UPDATED                |
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

| File                     | Purpose                                                  |
| ------------------------ | -------------------------------------------------------- |
| `probe_2d.py`            | Original (Titans + TensorBridge + Rich UI)               |
| `probe_2d_v2.py`         | Simplified classification probe                          |
| `probe_2d_v3.py`         | Grid scanner (Born × Survive)                            |
| `probe_2d_v4.py`         | **Modern V4** — T-P+E + Condensate + Multi-signal voting |
| `scan_v4.py`             | **Full pipeline** → SQLite ★ NEW                         |
| `universality_test.py`   | **Non-totalistic proof** ★ NEW                           |
| `investigate_particle.py`| **Glider detection** ★ NEW                               |

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
│  Compression │ T-P+E │ Condensate │ Topology │ Sheaf ★      │
└─────────────────────────────┼───────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────┐
│                   EXTRACTION LAYER                          │
│  Particles → Reactions → Gadgets │ Oligons │ Gliders ★      │
└─────────────────────────────┼───────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────┐
│                   PERSISTENCE LAYER              ★ NEW      │
│  SQLite Atlas │ JSON Export │ Figures                       │
└─────────────────────────────┼───────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────┐
│                   INTERFACE LAYER                           │
│  CLI │ Query API │ Web Observatory                          │
└─────────────────────────────────────────────────────────────┘
```

---

## CLI Commands

| Command                                        | Purpose                   |
| ---------------------------------------------- | ------------------------- |
| `uv run rulial --help`                         | Show all commands         |
| `uv run rulial entropy-flow --rule "RULE"`     | Compression flow analysis |
| `uv run rulial tpe --rule "RULE"`              | T-P+E dynamics            |
| `uv run rulial condensate --rule "RULE"`       | Vacuum phase detection    |
| `uv run rulial oligons --rule "RULE"`          | Oligon count              |
| `uv run rulial serve`                          | Start web observatory     |
| `uv run python -m rulial.runners.probe_2d_v4`  | Run V4 atlas scan         |
| `uv run python -m rulial.runners.scan_v4 scan` | Full pipeline scan ★ NEW  |
| `uv run python scripts/replicate_all.py`       | Replicate all findings    |
| `uv run python scripts/visualize.py`           | Generate figures          |

---

## Key Research Outputs

| File | Description |
|------|-------------|
| `atlas_v4.db` | SQLite database with sheaf metrics |
| `atlas_v4.json` | 200-rule atlas (JSON) |
| `atlas_v4_condensate.json` | 50 B0-focused rules |
| `docs/visualizations/fig_goldilocks_zone.png` | Computation phase diagram |

---

## Full Documentation

See [`docs/USAGE_GUIDE.md`](docs/USAGE_GUIDE.md) for complete reference.
