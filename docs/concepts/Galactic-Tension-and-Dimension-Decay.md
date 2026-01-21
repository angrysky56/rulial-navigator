# Galactic Tension and Dimension Decay

This document explains how flat galaxy rotation curves emerge from **Oligon scaffolding** and **dimension decay** in the hypergraph, without requiring dark matter halos.

---

## The Mapping

| MSM Concept             | Wolfram Analog    | Meaning                                   |
| ----------------------- | ----------------- | ----------------------------------------- |
| **Tension Lines**       | Causal Flux       | Connectivity density deflects geodesics   |
| **Cosmic Scaffold**     | Oligon Network    | Light defects form gravitational skeleton |
| **Membrane Elasticity** | Dimension Decay   | Fractional dimension at galactic scales   |
| **Tully-Fisher**        | Spacetime Texture | $v^4 \propto M_b$ from geometry           |

---

## 1. The Scaffold: Oligon Networks

**Cosmic Web** = Baryonic matter tracing the Oligon scaffold

```
Oligons (small defects)  →  Omnipresent background texture
              ↓
    Gravitational skeleton of universe
              ↓
    Galaxies cluster along these lines
```

The "invisible scaffolding" is not a halo of particles but the **connectivity structure** of the hypergraph itself.

---

## 2. Tension Lines as Causal Flux

**Gravity is not a force pulling objects—it is geodesic deflection.**

$$F_{gravity} = \nabla \cdot \Phi_{causal}$$

Where:

- $\Phi_{causal}$ = Causal flux density
- High flux = High connectivity = Mass concentration
- Geodesics curve toward dense regions

The "tension" is the network's resistance to deformation.

---

## 3. Flat Rotation Curves via Dimension Decay

**The Problem:** Stars at galaxy edges move too fast for $1/r^2$ gravity.

**Standard Solution:** Dark matter halos (invisible heavy particles).

**Wolfram Solution:** The effective dimension of space drops below 3 at galactic scales.

| Scale         | Effective Dimension | Gravity Falloff      |
| ------------- | ------------------: | -------------------- |
| Solar system  |                 3.0 | $1/r^2$ (normal)     |
| Galactic disk |                 2.8 | $1/r^{1.6}$ (slower) |
| Intergalactic |                3.0+ | $1/r^2$ (normal)     |

**Result:** Gravity falls off slower → Flat rotation curves → No dark matter needed.

---

## 4. The Tully-Fisher Relation

$$v^4 = \alpha G M_b$$

| Variable | Physical Meaning  | Hypergraph Meaning               |
| -------- | ----------------- | -------------------------------- |
| $v$      | Rotation velocity | Geodesic curvature rate          |
| $M_b$    | Baryonic mass     | Causal flux of particle knots    |
| $\alpha$ | Tension constant  | Oligon density at galactic scale |

The **vacuum energy itself** (via Oligons) provides the missing gravitational potential.

---

## Implementation Analogy in Navigator

| Galactic Concept | CA Analog                                  |
| ---------------- | ------------------------------------------ |
| Galaxy           | Dense region of Class 4 structures         |
| Rotation curve   | Particle velocity vs. distance from center |
| Dark Matter halo | β₁ topology in surrounding space           |
| Dimension decay  | Compression ratio gradient                 |

### Measuring "Galactic" Structure

```python
# Compression ratio as function of distance from active region
def galactic_tension_profile(spacetime, center):
    """Measure how 'tension' (CR) varies with distance from center."""
    profiles = []
    for radius in range(1, 30):
        ring = extract_ring(spacetime, center, radius)
        cr = compress_ratio_lzma(ring.tobytes())
        profiles.append((radius, cr))
    return profiles
# Flat profile = constant tension = "dark matter" equivalent
```

---

## The Complete Cosmological Picture

```
┌──────────────────────────────────────────────────────────────┐
│                HYPERGRAPH COSMOLOGY                          │
│                                                              │
│  Emes ─── Oligons ─── Particles ─── Galaxies ─── Cosmos     │
│   │         │           │             │           │          │
│   ▼         ▼           ▼             ▼           ▼          │
│  Space   Dark Matter  Baryons    Clusters   Expansion       │
│ fabric   scaffold    (knots)    (web)      (Λ pressure)     │
│                                                              │
│  All from ONE hypergraph with tension and dimension decay   │
└──────────────────────────────────────────────────────────────┘
```

---

## References

- Tully, R.B. & Fisher, J.R. (1977) "A New Method of Determining Distances to Galaxies"
- Milgrom, M. (1983) "Modified Dynamics as an Alternative to Dark Matter"
- Wolfram, S. "A New Kind of Science" (2002)
- [The Metastable Superfluid Membrane](The-Metastable-Superfluid-Membrane.md)
- [Dark Matter as Oligons](Dark-Matter-as-Oligons.md)
