# Vacuum Condensate Phases in the Ruliad

**A Classification of Complex Rules by Membrane Structure**

_Draft Whitepaper - Rulial Navigator Project_

---

## Abstract

We demonstrate that Class 4 rules in the Ruliad exhibit at least two distinct phases: **particle-based** rules where isolated structures (gliders, oscillators) propagate through a sparse background, and **condensate** rules where any perturbation spontaneously expands to fill space at a characteristic equilibrium density. Using the `VacuumCondensateAnalyzer`, we identify B078/S012478 as an exemplar of the condensate phase, exhibiting 24.6% equilibrium density and 220× single-cell expansion. This classification has implications for the Metastable Superfluid Membrane theory of vacuum structure.

---

## 1. Introduction

### 1.1 The Wolfram Classification Problem

Wolfram's four-class system for cellular automata identifies Class 4 as rules exhibiting complex, computation-capable behavior. However, this classification treats all Class 4 rules equivalently. Our investigation reveals that Class 4 contains at least two fundamentally distinct phases:

| Phase              | Example       | Signature                                  |
| ------------------ | ------------- | ------------------------------------------ |
| **Particle-based** | B3/S23 (Life) | Isolated gliders, oscillators, still lifes |
| **Condensate**     | B078/S012478  | No isolated structures; coherent membrane  |

### 1.2 Theoretical Motivation

The Metastable Superfluid Membrane (MSM) theory posits that the vacuum is a quantum condensate with micropolar elasticity. This framework predicts:

1. **Particles as topological defects** — isolated "knots" in the vacuum order parameter
2. **Vacuum phases** — different rules represent different vacuum states
3. **Spontaneous condensation** — perturbations can nucleate phase transitions

We propose that condensate-phase rules model a vacuum state below the "superfluid λ-point" where individual excitations cannot exist.

---

## 2. Methods

### 2.1 VacuumCondensateAnalyzer

We implement a systematic detector for condensate behavior:

```python
@dataclass
class CondensateAnalysis:
    is_condensate: bool           # Single cell expands?
    equilibrium_density: float    # Characteristic density (0-1)
    critical_density: float       # Phase transition point
    expansion_factor: float       # How much single cell grows
    stability_variance: float     # Variance at equilibrium
```

**Detection criteria:**

- `is_condensate = True` if a single cell expands to >10 cells
- Equilibrium measured from both sparse (5%) and dense (40%) initial conditions
- Critical density found via binary search

### 2.2 Test Rules

| Rule         | Class | Known Behavior                            |
| ------------ | ----- | ----------------------------------------- |
| B3/S23       | 4     | Game of Life — gliders, stable structures |
| B36/S23      | 4     | HighLife — replicators                    |
| B078/S012478 | 4     | Discovered in Atlas scan                  |

---

## 3. Results

### 3.1 Phase Classification

| Rule             | Phase         | Eq. Density | Single Cell → | σ²   |
| ---------------- | ------------- | ----------- | ------------- | ---- |
| **B078/S012478** | 🌊 CONDENSATE | 24.6%       | 220           | 0.00 |
| **B3/S23**       | ⚛️ PARTICLE   | 3.9%        | 0             | 0.00 |

### 3.2 B078/S012478 Behavior

**Spontaneous expansion from minimal seed:**

| Initial       | After 50 steps | Growth |
| ------------- | -------------- | ------ |
| 1 cell        | 220 cells      | 220×   |
| 4 cells       | 204 cells      | 51×    |
| 41 cells (1%) | 980 cells      | 24×    |

**Convergence to equilibrium:**

Starting from 30% density, the system contracts to 24.6%.
Starting from 1% density, the system expands to 24.6%.

This demonstrates a **characteristic ground state density** independent of initial conditions.

### 3.3 T-P+E Analysis

| Rule         | T    | P    |      | T-P         |     | Mode |
| ------------ | ---- | ---- | ---- | ----------- | --- | ---- |
| B078/S012478 | 0.61 | 0.63 | 0.02 | ✨ BALANCED |
| B3/S23       | 0.61 | 0.53 | 0.08 | ✨ BALANCED |

Both rules show balanced T-P dynamics, but only B078/S012478 exhibits condensate behavior. This suggests T-P+E captures dynamics but not phase.

### 3.4 Oligon Census

| Rule         | Still Lifes | Oscillators | Total |
| ------------ | ----------- | ----------- | ----- |
| B078/S012478 | 0           | 0           | 0     |
| B3/S23       | 36          | 0           | 36    |

**Key finding:** Condensate rules have zero oligons — no isolated stable structures exist.

---

## 4. Discussion

### 4.1 Physical Interpretation

In MSM framework:

| CA Phenomenon        | Physical Analog          |
| -------------------- | ------------------------ |
| Condensate phase     | Superfluid below λ-point |
| Equilibrium density  | Vacuum energy            |
| No particles         | Coherent ground state    |
| Any seed → expansion | Nucleation of condensate |

B078/S012478 models a vacuum where **the vacuum itself is the structure**. There are no particles because any perturbation becomes part of the coherent whole.

### 4.2 Implications for Ruliad Navigation

The Titans agent should navigate differently in condensate vs particle phases:

| Phase      | Strategy                                        |
| ---------- | ----------------------------------------------- |
| Particle   | Look for gliders, oscillators, logic gates      |
| Condensate | Measure equilibrium density, correlation length |

### 4.3 Open Questions

1. **What determines equilibrium density?**
   - Can it be predicted from B/S rule parameters?

2. **Are there higher-order condensates?**
   - Multiple equilibrium states?
   - Phase transitions between densities?

3. **What is the "critical temperature"?**
   - At what point does particle behavior emerge?

---

## 5. Conclusion

We introduce the vacuum condensate phase as a subclass of Class 4 rules characterized by:

1. **Spontaneous expansion** of minimal seeds
2. **Characteristic equilibrium density** independent of initial conditions
3. **Absence of isolated structures** (zero oligons, zero particles)
4. **Near-zero stability variance** (frozen membrane)

Rule B078/S012478 exemplifies this phase, modeling a coherent vacuum state that challenges particle-based intuitions about complex cellular automata.

---

## Appendix A: CLI Commands

```bash
# Condensate analysis
uv run rulial condensate --rule "B078/S012478"

# Compare with traditional metrics
uv run rulial entropy-flow --rule "B078/S012478"
uv run rulial tpe --rule "B078/S012478"
uv run rulial oligons --rule "B078/S012478"
```

---

## References

1. Wolfram, S. "A New Kind of Science" (2002)
2. [The Metastable Superfluid Membrane](The-Metastable-Superfluid-Membrane.md)
3. [Particles as Vortex Knots](Particles-as-Vortex-Knots.md)
4. [Vacuum Condensate Discovery](Vacuum-Condensate-Discovery.md)
