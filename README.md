# Rulial Navigator

**Autonomous Exploration of Computational Universes**

---

## The Journey

The **Ruliad** is the infinite space of all possible computational rules. Somewhere in this vast landscape lie the rules that give rise to physics, to particles, to minds, to us.

This project is a navigator—an autonomous agent that explores this space, measuring each rule's capacity for complexity, structure, and emergence.

> _"We are in a single membrane and this is all just unresolved knots, virtual particles, solitons, dissolving in entropy towards the resolving void."_

---

## The Question

**What makes a rule interesting?**

Not all rules are created equal. Most either freeze into static patterns or dissolve into chaos. But some—like Conway's Game of Life—exist on a knife's edge, generating persistent structures that resist entropy.

We call these rules **Class 4**: the computational edge of chaos.

But even within Class 4, we've discovered two fundamentally different phases:

| Phase          | Description                                                         | Example               |
| -------------- | ------------------------------------------------------------------- | --------------------- |
| **Particle**   | Isolated structures (gliders, oscillators) move through empty space | B3/S23 (Game of Life) |
| **Condensate** | The vacuum itself is structure—any seed expands to fill space       | B078/S012478          |

This mirrors theoretical physics: some vacua support localized excitations (particles), while others are coherent wholes (condensates).

---

## The Method

### Maxwell's Demon for Complexity

The navigator acts as **Maxwell's Demon**, measuring information flow:

| Signal             | Interpretation         | Action        |
| ------------------ | ---------------------- | ------------- |
| 🔥 **FRUSTRATION** | High entropy, no flow  | Escape chaos  |
| ❄️ **BOREDOM**     | Low entropy, no flow   | Escape frozen |
| ✨ **CURIOSITY**   | Active flow, structure | Approach!     |

### T-P+E: The Dialectic of Dynamics

Every rule balances two forces:

- **Toroidal (T):** Expansion, divergence, fragmentation
- **Poloidal (P):** Contraction, convergence, mass formation
- **Emergence:** $E = (T \cdot P) \times |T-P|$

Maximum emergence occurs at the balance point: T ≈ P ≈ 0.5.

### Oligons: Dark Matter Scaffolding

Small stable structures (still lifes, blinkers) form a **tension network** that shapes larger dynamics. Rules with many oligons support particle physics. Rules with zero oligons are condensates.

---

## The Theory

This project is grounded in the **Metastable Superfluid Membrane** hypothesis:

| Physical Concept        | Ruliad Mapping                                      |
| ----------------------- | --------------------------------------------------- |
| **Matter as Knots**     | Particles are topological defects in the hypergraph |
| **Superfluid Rigidity** | The speed of light emerges from vacuum elasticity   |
| **Entropy Flow**        | Time is the direction toward/away from equilibrium  |
| **Tension Network**     | Dark matter as oligon scaffolding                   |
| **Vacuum Phases**       | Class 4 splits into particle vs condensate phases   |

See the [theoretical documentation](#theoretical-documentation) for deep dives.

---

## Quick Start

```bash
git clone https://github.com/angrysky56/rulial-navigator.git
cd rulial-navigator
uv sync
```

```bash
# Quick analysis of a rule
uv run rulial entropy-flow --rule "B3/S23"
uv run rulial tpe --rule "B3/S23"
uv run rulial condensate --rule "B078/S012478"

# Scan the rule space
uv run python -m rulial.runners.probe_2d_v4 --mode quick --samples 200
```

**Full usage guide:** [`docs/USAGE_GUIDE.md`](docs/USAGE_GUIDE.md)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     EXPLORATION LAYER                       │
│  Titans Memory ◄── Online Learning ◄── Hallucination        │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────┐
│                   ANALYSIS LAYER                            │
│  Compression Flow │ T-P+E │ Condensate │ Topology (TDA)     │
└─────────────────────────────┼───────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────┐
│                   EXTRACTION LAYER                          │
│  Particles → Reactions → Logic Gates → Oligons              │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
src/rulial/
├── compression/          # Complexity measurement
│   ├── flow.py           # Universal Compression Stack
│   └── neural.py         # LSTM predictor
├── engine/               # Simulation
│   ├── eca.py            # 1D Elementary CA
│   └── totalistic.py     # 2D Outer-Totalistic CA
├── mapper/               # Analysis
│   ├── topology.py       # Persistent homology (GUDHI)
│   ├── tpe.py            # T-P+E Framework
│   └── condensate.py     # Vacuum phase detection
├── mining/               # Physics extraction
│   ├── extractor.py      # Particle miner
│   ├── collider.py       # Reaction tables
│   ├── synthesizer.py    # Logic gadgets
│   ├── oligon.py         # Oligon counter
│   └── query.py          # Natural language interface
├── navigator/            # AI exploration
│   └── titans.py         # Test-time learning
├── quantum/              # Quantum bridge
│   ├── bridge.py         # PEPS tensor network
│   └── kernel.py         # Quantum kernel navigator
├── runners/              # Atlas scanners
│   └── probe_2d_v4.py    # Modern V4 scanner
├── pipeline.py           # Unified analysis pipeline
└── cli.py                # Command line interface
```

---

## Documentation

### Usage & Reference

- [`docs/USAGE_GUIDE.md`](docs/USAGE_GUIDE.md) — Complete CLI and API reference

### Theoretical Framework

- [`docs/The-Metastable-Superfluid-Membrane.md`](docs/The-Metastable-Superfluid-Membrane.md) — Core theory
- [`docs/Emes-and-the-Glass-Floor.md`](docs/Emes-and-the-Glass-Floor.md) — Speed of light emergence
- [`docs/Particles-as-Vortex-Knots.md`](docs/Particles-as-Vortex-Knots.md) — Mass as causal flux
- [`docs/Dark-Matter-as-Oligons.md`](docs/Dark-Matter-as-Oligons.md) — Oligon tension networks
- [`docs/Galactic-Tension-and-Dimension-Decay.md`](docs/Galactic-Tension-and-Dimension-Decay.md) — Galaxy rotation curves
- [`docs/Dark-Energy-and-Hubble-Tension.md`](docs/Dark-Energy-and-Hubble-Tension.md) — Cosmological implications
- [`docs/Quantum-Mechanics-from-Branchial-Space.md`](docs/Quantum-Mechanics-from-Branchial-Space.md) — Path integral connection

### Research

- [`docs/Vacuum-Condensate-Discovery.md`](docs/Vacuum-Condensate-Discovery.md) — B078/S012478 discovery
- [`docs/Whitepaper-Vacuum-Condensate-Phases.md`](docs/Whitepaper-Vacuum-Condensate-Phases.md) — Draft whitepaper

---

## Roadmap

- [x] Core engines (1D/2D CA)
- [x] Quantum tensor bridge
- [x] Physics mining pipeline
- [x] Universal Compression Stack
- [x] T-P+E Framework
- [x] Vacuum condensate detection
- [x] V4 Atlas scanner
- [ ] Geodesic proof paths
- [ ] Multi-rule circuit synthesis

---

## License

MIT
