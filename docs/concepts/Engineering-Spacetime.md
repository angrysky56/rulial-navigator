# Engineering Spacetime: Foliation and Causal Flux

This document explains how to **induce Lorentz contraction** and **create anisotropy** within the spatial hypergraph through active observer manipulation.

---

## Core Insight

> Effects are not physical deformations of a rigid material, but **computational consequences** of how an observer samples the updating network.

---

## 1. Lorentz Contraction via Foliation

**Objects don't move through the grid—they ARE persistent patterns OF the grid.**

### The Mechanism

```
Static Observer:          Moving Observer:
┌───────────────┐        ┌───────────────┐
│ ━━━━━━━━━━━━━ │        │    ╲          │
│ ━━━━━━━━━━━━━ │   →    │     ╲         │  Tilted
│ ━━━━━━━━━━━━━ │        │      ╲        │  Slices
│ ━━━━━━━━━━━━━ │        │       ╲       │
└───────────────┘        └───────────────┘
  Flat foliation           Angled foliation
  (at rest)                (in motion)
```

| Concept             | Meaning                                                 |
| ------------------- | ------------------------------------------------------- |
| **Reference Frame** | Choice of foliation (how you slice the causal graph)    |
| **Motion**          | Hypergraph rewriting to propagate a topological feature |
| **Contraction**     | Steeper angle → fewer nodes in spatial slice            |
| **Trade-off**       | Space extension → Time extension (dilation)             |

**Result:** Contraction emerges from **changing your computational reference frame**.

---

## 2. Anisotropy via Causal Flux

**Inject energy to curve the grid.**

### The Mechanism

| Action                  | Hypergraph Effect   |
| ----------------------- | ------------------- |
| Increase update density | Higher causal flux  |
| Higher causal flux      | Geodesic deflection |
| Deflected geodesics     | Curved spacetime    |
| Curved spacetime        | **Anisotropy**      |

The "distance" (edges to traverse) now differs by direction.

### Gravity as Anisotropy

$$\text{Mass} = \text{Dense Causal Flux} \implies \text{Curved Geodesics}$$

The "tension" of the vacuum increases where flux is highest.

---

## 3. Rulial Motion: Changing the Laws

**The most fundamental manipulation: move in Rulial Space.**

| Space      | Variable      | Speed Limit | What Changes         |
| ---------- | ------------- | ----------- | -------------------- |
| Physical   | Position      | c           | Where you are        |
| Branchial  | Quantum state | ζ           | What you can measure |
| **Rulial** | **Rule set**  | **ρ**       | **Laws of physics**  |

### Navigating to Anisotropic Rules

You could theoretically find a rule-set where:

- Updates preferentially occur in one direction
- The hypergraph has built-in asymmetry
- Geometry is inherently non-isotropic

**This is what the Navigator does**: explores Rulial Space to find rules with specific properties.

---

## Implementation in Navigator

| Theoretical Concept | Navigator Implementation             |
| ------------------- | ------------------------------------ |
| Foliation choice    | Initial condition selection          |
| Causal flux         | Compression ratio (activity density) |
| Geodesic deflection | Particle velocity measurement        |
| Rulial motion       | Titans exploration jumps             |
| Anisotropic rules   | Atlas scan for unusual CRs           |

### Measuring Anisotropy

```python
def measure_anisotropy(rule_str, steps=100):
    """
    Check if a rule has directional preference in particle motion.
    """
    from rulial.mining.extractor import ParticleMiner

    miner = ParticleMiner(rule_str)
    particles = miner.mine()
    spaceships = [p for p in particles if p.is_spaceship]

    if not spaceships:
        return 0.0  # No motion to measure

    # Velocity distribution
    velocities = [p.velocity for p in spaceships]
    v_x = [v[0] for v in velocities]
    v_y = [v[1] for v in velocities]

    # Anisotropy = difference in average speeds
    anisotropy = abs(np.mean(np.abs(v_x)) - np.mean(np.abs(v_y)))
    return anisotropy
```

---

## The Active Observer

To "cause" these effects, **you must act as an active observer**:

| Effect              | Action                               |
| ------------------- | ------------------------------------ |
| Lorentz Contraction | Change foliation (velocity)          |
| Local Anisotropy    | Inject causal flux (mass/energy)     |
| Global Anisotropy   | Navigate Rulial Space (change rules) |

---

## Connection to Titans

The Titans agent is an **active observer** in Rulial Space:

1. **Current Position**: The rule being analyzed
2. **Foliation**: The specific initial condition
3. **Causal Flux**: Measured via compression ratio
4. **Movement**: Hallucinating promising neighbors
5. **Goal**: Find rules with desired flux patterns (Class 4)

**Titans doesn't just observe the Ruliad—it navigates it.**

---

## References

- Gorard, J. "Some Relativistic and Gravitational Properties of the Wolfram Model"
- [The Metastable Superfluid Membrane](The-Metastable-Superfluid-Membrane.md)
- [Emes and the Glass Floor](Emes-and-the-Glass-Floor.md)
