# Quantum Mechanics from Branchial Space

This document explains how the wavefunction emerges as a **geodesic bundle** in the multiway graph, and probability as **path density**.

---

## The Mapping

| MSM Concept           | Wolfram Analog      | Meaning                             |
| --------------------- | ------------------- | ----------------------------------- |
| **Phonon Envelope**   | Geodesic Bundle     | Spread of possible histories        |
| **Path Density**      | Multiway Measure    | Number of paths to state            |
| **Vacuum Graininess** | Branchial Structure | Discrete quantum branching          |
| **Wavefunction**      | Bundle Evolution    | Propagation through Branchial Space |

---

## 1. The Wavefunction as Geodesic Bundle

**Standard QM:** $\psi(x,t)$ is a probability amplitude field.

**Wolfram View:** $\psi$ describes a **bundle of geodesics** in the multiway graph.

```
Particle (topological defect)
      ↓
Updates create branching histories
      ↓
Bundle of paths through Branchial Space
      ↓
This bundle IS the wavefunction
```

### Phase from Action

$$\psi \sim e^{iS/\hbar}$$

Where S = "turning" accumulated as paths evolve through multiway space.

---

## 2. Born Rule from Path Counting

$$|\psi|^2 = \rho_{paths}$$

| Quantity       | Physical Meaning | Wolfram Meaning           |
| -------------- | ---------------- | ------------------------- | ------------------- | ------------ |
| $              | \psi             | ^2$                       | Probability density | Path measure |
| $\rho_{paths}$ | Phonon density   | Causal edge flux          |
| High density   | High probability | Many paths converge there |

**The Born Rule emerges from counting paths, not from postulation.**

---

## 3. Uncertainty from Branchial Spread

**Why Heisenberg Uncertainty?**

We are "spread out" across branches:

- Position = Location in spatial hypergraph
- Momentum = Direction in branchial graph
- These are **orthogonal directions** in the full state space

$$\Delta x \cdot \Delta p \geq \frac{\hbar}{2}$$

The limit is set by:

- **Maximum entanglement speed** ($\zeta$)
- **Discrete update rate** of the hypergraph

---

## 4. Wave-Particle Duality

| Aspect       | MSM Term        | Wolfram Term               |
| ------------ | --------------- | -------------------------- |
| **Particle** | Vortex knot     | Topological obstruction    |
| **Wave**     | Phonon envelope | Geodesic bundle            |
| **Dual**     | Same object     | Spatial vs. branchial view |

The particle IS the wave:

- Viewed in **space**: Localized knot
- Viewed in **multiway**: Extended bundle

---

## Implementation in Navigator

| Quantum Concept | CA Analog                            |
| --------------- | ------------------------------------ |
| Wavefunction    | Probability map of particle location |
| Measurement     | Sampling one trajectory              |
| Superposition   | Multiple glider positions            |
| Entanglement    | Correlated particle pairs            |

### The TensorBridge Already Measures This

```python
from rulial.quantum.bridge import TensorBridge

bridge = TensorBridge(height=16, width=16)
psi = bridge.grid_to_tensor_state(grid)
result = bridge.compute_bipartition_entropy(psi)

# Entropy = spread of geodesic bundle
# High entropy = highly branched = quantum superposition
```

---

## The Three Spaces

```
┌──────────────────────────────────────────────────────────────┐
│                    THE TRINITY OF SPACES                     │
│                                                              │
│  PHYSICAL SPACE    BRANCHIAL SPACE    RULIAL SPACE          │
│  (where things     (where quantum      (where rules          │
│   are located)      states live)        are defined)         │
│                                                              │
│  Position x   ←→   Momentum p    ←→   Rule r                │
│  Speed c      ←→   Speed ζ       ←→   Speed ρ               │
│  Particles    ←→   Wavefunctions ←→   Observers             │
│                                                              │
│  All embedded in the same Ruliad                            │
└──────────────────────────────────────────────────────────────┘
```

---

## The Deep Insight

> _"The phonon is the vibration of the Ruliad itself; we perceive its density as probability because we are woven into the same lattice we are measuring."_

**We don't observe the wavefunction collapse—we ARE the collapse.**

Each measurement is our thread of observation slicing through the bundle of histories.

---

## References

- Feynman, R.P. "Path Integrals and Quantum Mechanics"
- Gorard, J. "Some Quantum Mechanical Properties of the Wolfram Model"
- [The Metastable Superfluid Membrane](The-Metastable-Superfluid-Membrane.md)
- [Particles as Vortex Knots](Particles-as-Vortex-Knots.md)
