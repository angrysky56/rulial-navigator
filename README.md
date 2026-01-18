# Rulial Navigator

**Autonomous Exploration of Computational Universes**

---

## What Is This?

Imagine every possible set of rules that could govern a universe—every way particles could interact, every law of physics that *could* exist. The **Ruliad** is the mathematical space containing *all* of these possible rule systems.

This project is a **navigator** that explores this space, searching for rules that produce complexity, structure, and the conditions for computation—the same conditions that allow matter, life, and minds to exist.

### The Simple Version

- **We simulate tiny universes** using cellular automata (like Conway's Game of Life)
- **We measure what happens**: Does it freeze? Explode into chaos? Or create interesting patterns?
- **We found something surprising**: Rules divide into two fundamentally different "phases"—like ice and water

> *Think of it like exploring an endless library of physics textbooks, each describing a different universe, and discovering that all the "interesting" ones fall into just two categories.*

---

## Key Discovery: Two Phases of Reality

Just as water can exist as ice (solid) or liquid, computational rules exist in two distinct **phases**:

| Phase | What It Looks Like | Everyday Analogy | Example |
|-------|-------------------|------------------|---------|
| **Particle** | Things move through empty space | Planets orbiting in a vacuum | Game of Life |
| **Condensate** | Space itself is "full"—no emptiness | Sound waves in water | B078/S012478 |

**Both phases can compute.** Both can support "gliders" (moving patterns that transmit information). They just do it differently:
- **Particles:** Information travels as discrete objects
- **Condensates:** Information travels as waves

---

## For Specialists

<details>
<summary><strong>Physics Connection</strong></summary>

The particle/condensate distinction maps to QFT vacuum states:
- **Particle phase** → Perturbative vacuum with localized excitations
- **Condensate phase** → Symmetry-broken vacuum (BCS-like)

The **Harmonic Overlap (H)** metric corresponds to the projection onto ker(L) where L is the sheaf Laplacian—effectively measuring distance from equilibrium.

</details>

<details>
<summary><strong>Mathematics</strong></summary>

We use **cellular sheaf theory** to analyze CA dynamics:
- **Coboundary operator δ₀**: maps 0-cochains (cell values) → 1-cochains (edge differences)
- **Sheaf Laplacian L = δ₀ᵀδ₀**: governs diffusion
- **H¹ = coker(δ₀)**: irreducible topological structures (≈ Betti-1)
- **Monodromy Φ**: +1 = resonant (condensate), -1 = tense (particle)

</details>

<details>
<summary><strong>Computational Complexity</strong></summary>

The **Goldilocks Zone** (H = 0.3-0.6) corresponds to the edge of chaos:
- Too frozen (H > 0.9): No information processing
- Too chaotic (H < 0.3): Information destroyed
- Just right: Persistent mobile structures (gliders) can exist

This is the **spectral signature of Turing-completeness**.

</details>

---

## The Method

### Maxwell's Demon for Complexity

The navigator measures information flow in each rule:

| Signal | Meaning | Action |
|--------|---------|--------|
| 🔥 **FRUSTRATION** | Chaos—nothing persists | Move away |
| ❄️ **BOREDOM** | Frozen—nothing happens | Move away |
| ✨ **CURIOSITY** | Structure + dynamics | Explore! |

### T-P+E: Expansion vs Contraction

Every rule system balances:
- **Toroidal (T):** Expansion, spreading out
- **Poloidal (P):** Contraction, coming together
- **Emergence:** How much interesting structure appears

Maximum complexity occurs when these forces balance.

---

## The Theory

This project builds on the **Metastable Superfluid Membrane** hypothesis:

| What We See | What It Might Mean |
|-------------|-------------------|
| **Particles** | Knots in spacetime |
| **Speed of light** | Rigidity of the vacuum "membrane" |
| **Time** | Direction toward equilibrium |
| **Dark matter** | Scaffolding of stable micro-structures |

See the [theoretical documentation](docs/The-Metastable-Superfluid-Membrane.md) for deep dives.

---

## Research Highlights

### Key Discoveries (2026)

| Discovery | Evidence |
|-----------|----------|
| **B0/B1 → Condensate** | 99.4% of B0/B1 rules exhibit condensate behavior |
| **Universality** | Proven in 512-bit non-totalistic rules |
| **Goldilocks Zone** | H = 0.3-0.6 predicts computational capacity |
| **Both Phases Compute** | Gliders found in particles AND condensates |

### The Goldilocks Zone

Computation emerges where **Harmonic Overlap** H = 0.3-0.6:

| Rule | Phase | H | Structures |
|------|-------|---|------------|
| B6/S123467 | Particle | 0.503 | 11 Gliders, 45 Still Lifes |
| B0467/S0568 | Condensate | 0.479 | 6 Solitons, 25 Oscillators |

### Core Theorem

> A totalistic 2D CA exhibits condensate behavior iff **(0 ∈ B) OR (1 ∈ B)**

This was proven universal across all 2^512 possible 2D Moore-neighborhood rules.

### Visualizations

All figures are in [`docs/visualizations/`](docs/visualizations/):

| Figure | Description |
|--------|-------------|
| `fig_goldilocks_zone.png` | Phase diagram showing computational sweet spot |
| `fig_monodromy_histogram.png` | Bimodal phase separation |
| `fig_s_sum_correlation.png` | Vacuum energy prediction (r = 0.632) |
| `fig_tpe_modes.png` | T-P+E dynamics distribution |

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
- [x] **Sheaf-theoretic framework** ← NEW
- [x] **Universality proof** ← NEW
- [x] **Goldilocks zone discovery** ← NEW
- [ ] Gate hunting (collision logic)
- [ ] Multi-rule circuit synthesis

---

## License

MIT
