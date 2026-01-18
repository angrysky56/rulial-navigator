# Vacuum Condensate Phases - Replication Scripts

Scripts to replicate the results from _"Vacuum Condensate Phases in the Ruliad"_.

## Quick Start

```bash
# Full analysis from pre-computed atlas data
uv run python -m scripts.analysis

# Analyze a specific rule
uv run python scripts/analyze_rule.py "B078/S012478"
uv run python scripts/analyze_rule.py "B3/S23"

# Generate visualizations (requires matplotlib)
uv pip install matplotlib
uv run python scripts/visualize.py
```

## Scripts

| Script            | Purpose                             |
| ----------------- | ----------------------------------- |
| `replicate_all.py` | **Full replication of all findings** (Sections 3-5) |
| `analysis.py`     | Condensate/S-parameter stats (Section 3) |
| `analyze_rule.py` | Full analysis of any single rule |
| `visualize.py`    | Generates `figure_*.png` for the paper |

## New Scripts (2026)

Run via the `rulial.runners` module:

| Script | Purpose |
|--------|---------|
| `universality_test.py` | Prove B0→Condensate in non-totalistic rules (Section 4) |
| `investigate_particle.py` | Find gliders/oscillators → Turing completeness (Section 5) |
| `scan_v4.py` | Full pipeline scanner with sheaf metrics (SQLite output) |

## Individual Analyses

```bash
# Section 3.1: Condensate Summary
uv run python -m scripts.analysis condensate_summary

# Section 3.3: T-P+E Dynamics
uv run python -m scripts.analysis tpe_analysis

# Section 3.6: Control Test (non-B0 rules are particle-phase)
uv run python -m scripts.analysis control_test

# Section 3.7: S-Parameter Correlation
uv run python -m scripts.analysis s_correlation
```

## Required Data Files

The following pre-computed atlas files are included:

| File                       | Description                 | Rules |
| -------------------------- | --------------------------- | ----- |
| `atlas_v4_condensate.json` | B0 rules (condensate focus) | 50+   |
| `atlas_v4.json`            | Random sample               | 200+  |

## Regenerating Atlas Data

If you want to regenerate the atlas from scratch:

```bash
# Random sample (quick)
uv run python -m rulial.runners.probe_2d_v4 --mode quick --samples 200 --output atlas_v4.json

# B0-focused (condensate)
uv run python -m rulial.runners.probe_2d_v4 --mode condensate --samples 100 --output atlas_v4_condensate.json

# Full systematic scan (slow, comprehensive)
uv run python -m rulial.runners.probe_2d_v4 --mode full --samples 1000 --output atlas_v4_full.json
```

## Expected Output

### Condensate Summary

```
═══ CONDENSATE SCAN SUMMARY ═══
Total rules analyzed: 50
Wolfram Classes: {4: 50}
Phases: {'condensate': 50}
Condensates: 50/50 (100.0%)
Equilibrium density range: 29.1% - 99.7%
```

### S-Parameter Correlation

```
CORRELATIONS:
  S-count vs eq_density: r = 0.487
  S-sum vs eq_density:   r = 0.621 ← STRONGEST
  S-mean vs eq_density:  r = 0.303
```

### Control Test

```
═══ CONTROL TEST: NON-B0 RULES ═══
B3/S23               (Game of Life    ) ⚛️ PARTICLE eq=5.1%
B36/S23              (HighLife        ) ⚛️ PARTICLE eq=5.0%
...
Particles: 10/10 (100%)
✅ HYPOTHESIS CONFIRMED: Non-B0 rules are particle-phase
```

### Sheaf Spectral Analysis (Goldilocks Zone)

Output from `replicate_all.py` verifying computation in the 0.3 < H < 0.6 range:

```
═══ MAPPING THE GOLDILOCKS ZONE ═══
Hypothesis: Computation occurs when 0.3 < Harmonic Overlap < 0.6

Rule                 | Phase        | Overlap (H)  | Monodromy
-----------------------------------------------------------------
B3/S23 (Life)        | tense        | 0.400 🌟     | -1.00
B0467/S0568          | resonant     | 0.479 🌟     | +1.00
B6/S123467           | tense        | 0.503 🌟     | -1.00
B01/S23              | resonant     | 0.907        | +1.00 (Frozen)
B/S012345678         | tense        | 0.050        | -1.00 (Chaos)

✅ HYPOTHESIS CONFIRMED: 
   - Class 4 / Computation rules cluster in 0.3 < H < 0.6
   - Both phases (Resonant/Tense) appear in the Goldilocks Zone
```

### Glider Census (Computational Structures)

```
═══ STRUCTURE CENSUS ═══
Rule: B6/S123467

  Still Lifes:  45
  Oscillators:  0
  Gliders:      11 🚀

🚀 GLIDER CANDIDATES:
  Size: 3 cells, Movement: 70.0 cells
    █·█
    ·█·

✅ GLIDERS FOUND - Potential for signal transmission!
```

---

## Visualization Outputs

The `visualize.py` script generates:

| Figure | Description |
|--------|-------------|
| `figure_density_by_s.png` | Equilibrium density vs S-count |
| `figure_s_correlation.png` | S-sum correlation with vacuum energy |
| `figure_tpe_modes.png` | T-P+E phase diagram |
| `figure_goldilocks.png` | Harmonic overlap distribution |

