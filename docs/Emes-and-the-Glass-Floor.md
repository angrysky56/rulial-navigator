# Emes and the Glass Floor: Speed of Light as Lattice Rigidity

This document explains how the speed of light ($c$) emerges from the discrete "atoms of space" (_emes_) and their causal connectivity.

---

## The Mapping

| MSM Concept         | Wolfram Analog      | Meaning                                            |
| ------------------- | ------------------- | -------------------------------------------------- |
| **Glass Floor**     | Spatial Hypergraph  | Discrete network appears continuous at large scale |
| **Vacuum Rigidity** | Causal Invariance   | Fixed rate of elementary updates                   |
| **Lattice Atoms**   | Emes                | Fundamental elements of space                      |
| **Shear Modulus**   | Causal Connectivity | How tightly emes are linked                        |

---

## 1. The Glass Floor: Emes and the Spatial Hypergraph

The universe is not a continuous fluid but composed of discrete elements:

**Emes** = Atoms of space

- Abstract relations forming a massive network (hypergraph)
- Connected by hyperedges that define spatial structure
- Too small to detect directly (~10⁻³⁵ m scale)

**The Illusion of Continuity:**

```
Discrete Emes → Hypergraph → Coarse-graining → Continuous Spacetime
```

Like seeing a gas as a smooth fluid—the molecular discreteness is invisible at our scale.

---

## 2. Speed of Light as "Lattice Rigidity"

$$c = \sqrt{\frac{\mu_{shear}}{\rho_{vacuum}}}$$

In the Wolfram model:

| MSM Variable    | Hypergraph Meaning                  |
| --------------- | ----------------------------------- |
| $\mu_{shear}$   | Causal connectivity (edges per eme) |
| $\rho_{vacuum}$ | Eme density                         |
| $c$             | Maximum causal propagation rate     |

**The Principle of Computational Equivalence** implies a universal "processor speed"—one fundamental update rate that defines $c$.

---

## 3. The "Freezing" is an Observer Effect

We perceive rigid, continuous space because we are **computationally bounded observers**.

| Perception Level   | What We See                            |
| ------------------ | -------------------------------------- |
| Slow observer (us) | Smooth manifold (General Relativity)   |
| Fast observer      | Discrete, chaotic eme updates (Ruliad) |

The "Glass Floor" would melt if our processing speed matched the hypergraph update rate.

---

## 4. Three Speed Limits in Three Spaces

The "elasticity" of the medium defines maximum speeds in different domains:

| Domain              | Speed Limit        | Symbol  | Meaning                        |
| ------------------- | ------------------ | ------- | ------------------------------ |
| **Physical Space**  | Speed of Light     | $c$     | Max causal propagation         |
| **Branchial Space** | Entanglement Speed | $\zeta$ | Max quantum correlation spread |
| **Rulial Space**    | Emulation Speed    | $\rho$  | Max rule translation rate      |

---

## Implementation in Rulial Navigator

| Physical Concept    | Code Implementation                |
| ------------------- | ---------------------------------- |
| Eme analogs         | Individual cells in CA grid        |
| Causal connectivity | `spacetime.extract_causal_graph()` |
| Propagation speed   | Spaceship velocity measurement     |
| Update rate         | Steps per simulation tick          |

### Measuring "c" for a Rule

```python
# The "speed of light" in a CA rule is the max spaceship velocity
from rulial.mining.extractor import ParticleMiner

miner = ParticleMiner("B3/S23")
particles = miner.mine()
spaceships = [p for p in particles if p.is_spaceship]

# c_rule = max velocity magnitude
c_rule = max(np.linalg.norm(s.velocity) for s in spaceships)
```

For Game of Life: $c_{GoL} = \sqrt{2}/4$ cells/step (diagonal glider)

---

## The Unified View

```
┌──────────────────────────────────────────────────────────┐
│                    THE RULIAD                            │
│                                                          │
│   Emes ─── Hyperedges ─── Causal Graph ─── Updates      │
│     │          │              │              │           │
│     ▼          ▼              ▼              ▼           │
│  "Atoms"   "Lattice"      "Light Cones"  "Processor"    │
│  of Space   Rigidity                       Speed         │
│                                                          │
│              Together define: c, ζ, ρ                    │
└──────────────────────────────────────────────────────────┘
```

---

## References

- Wolfram, S. "A New Kind of Science" (2002)
- Gorard, J. "Some Relativistic and Gravitational Properties of the Wolfram Model"
- [The Metastable Superfluid Membrane](The-Metastable-Superfluid-Membrane.md)
- [Dark Matter as Oligons](Dark-Matter-as-Oligons.md)
