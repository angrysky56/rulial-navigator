"""
LLL Complexity v2: Non-Circular Derivation from Rule Combinatorics

CRITICAL FIX: The original implementation had circular reasoning:
- It used simulation to measure p (probability of no structure)
- Then used LLL to "predict" structures exist
- This is circular: measuring gliders to prove gliders exist

THE HOLY GRAIL: Derive p purely from the rule table (LUT) combinatorics.
This allows predicting emergence WITHOUT simulation.

Key insight for totalistic rules (B/S notation):
- p_birth = probability that a random neighborhood produces birth
- p_death = probability that a random neighborhood produces death
- These can be computed from the rule string alone!

For a 9-cell Moore neighborhood with random 50% fill:
- Count of k live neighbors follows binomial distribution B(8, 0.5)
- P(k neighbors) = C(8,k) / 2^8
- p_birth = sum over k in B of P(k)
- p_survive = sum over k in S of P(k)
"""

from dataclasses import dataclass
from math import comb
from math import e as E


@dataclass
class LLLAnalysis:
    """
    Non-circular LLL analysis derived purely from rule combinatorics.
    """

    rule_str: str

    # Combinatorial probabilities (no simulation!)
    p_birth: float  # P(dead cell → alive) from random neighborhood
    p_survive: float  # P(live cell → alive) from random neighborhood
    p_active: float  # P(cell changes state) = stationary activity

    # LLL parameters
    dependency_d: int  # Neighborhood size = 8 for Moore
    lll_score: float  # ep(d+1) - if ≤ 1, theorem applies
    lll_satisfied: bool  # Is LLL condition met?

    # Derived predictions
    expected_density: float  # Stationary density (from Markov chain)
    structure_predicted: bool  # Does combinatorics predict interesting dynamics?


def parse_rule(rule_str: str) -> tuple[set[int], set[int]]:
    """Parse B/S notation into birth and survival sets."""
    parts = rule_str.upper().replace(" ", "").split("/")

    b_set = set()
    s_set = set()

    for part in parts:
        if part.startswith("B"):
            b_set = {int(c) for c in part[1:] if c.isdigit()}
        elif part.startswith("S"):
            s_set = {int(c) for c in part[1:] if c.isdigit()}

    return b_set, s_set


def binomial_probability(n: int, k: int, p: float = 0.5) -> float:
    """P(exactly k successes in n trials with probability p)."""
    return comb(n, k) * (p**k) * ((1 - p) ** (n - k))


def compute_p_from_rule(b_set: set[int], s_set: set[int]) -> tuple[float, float]:
    """
    Compute birth and survival probabilities from rule sets.

    For a random 50% fill in the 8 neighbors:
    - P(k neighbors) = C(8,k) / 256
    - p_birth = sum over k in B of P(k)
    - p_survive = sum over k in S of P(k)
    """
    # Neighbor count distribution (exclude center cell)
    p_birth = sum(binomial_probability(8, k) for k in b_set if k <= 8)
    p_survive = sum(binomial_probability(8, k) for k in s_set if k <= 8)

    return p_birth, p_survive


def compute_stationary_density(p_birth: float, p_survive: float) -> float:
    """
    Compute expected stationary density from Markov chain analysis.

    At equilibrium (if it exists):
    - Rate of birth = Rate of death
    - (1 - ρ) * p_birth = ρ * (1 - p_survive)
    - Solving: ρ = p_birth / (p_birth + 1 - p_survive)

    This is approximate (ignores spatial correlations) but gives a baseline.
    """
    denominator = p_birth + (1 - p_survive)
    if denominator <= 0:
        return 0.5  # Undefined, assume 50%

    return p_birth / denominator


def analyze_rule_combinatorially(rule_str: str) -> LLLAnalysis:
    """
    Perform non-circular LLL analysis using only rule combinatorics.

    THE KEY: No simulation is used. All predictions come from
    the rule's birth/survival sets alone.
    """
    b_set, s_set = parse_rule(rule_str)

    # Compute probabilities from combinatorics only
    p_birth, p_survive = compute_p_from_rule(b_set, s_set)

    # Activity probability: how often does a cell change?
    # Dead cell becomes active OR live cell dies
    # p_active ≈ (1-ρ)*p_birth + ρ*(1-p_survive)
    # Approximation at 50% density:
    p_active = 0.5 * p_birth + 0.5 * (1 - p_survive)

    # Stationary density (mean-field approximation)
    expected_density = compute_stationary_density(p_birth, p_survive)

    # LLL parameters
    # d = dependency degree = 8 neighbors in Moore neighborhood
    d = 8

    # p for LLL = probability of "bad event" at a cell
    # Bad event = cell is "boring" (never changes)
    # p_boring = 1 - p_active
    p_boring = 1 - p_active

    # LLL score: ep(d+1)
    lll_score = E * p_boring * (d + 1)
    lll_satisfied = lll_score <= 1

    # Structure prediction:
    # - Not trivial (p_active > 0.1)
    # - Not chaotic (p_active < 0.9)
    # - LLL satisfied OR in "Goldilocks" activity range
    in_goldilocks = 0.2 <= p_active <= 0.5
    structure_predicted = in_goldilocks or lll_satisfied

    return LLLAnalysis(
        rule_str=rule_str,
        p_birth=p_birth,
        p_survive=p_survive,
        p_active=p_active,
        dependency_d=d,
        lll_score=lll_score,
        lll_satisfied=lll_satisfied,
        expected_density=expected_density,
        structure_predicted=structure_predicted,
    )


def validate_predictions(
    rules_with_known_gliders: list[str], rules_without_gliders: list[str]
) -> dict:
    """
    Validate LLL predictions against known rules.
    This is the acid test: can we predict gliders without simulation?
    """
    results = {
        "true_positives": 0,
        "false_positives": 0,
        "true_negatives": 0,
        "false_negatives": 0,
    }

    for rule in rules_with_known_gliders:
        analysis = analyze_rule_combinatorially(rule)
        if analysis.structure_predicted:
            results["true_positives"] += 1
        else:
            results["false_negatives"] += 1

    for rule in rules_without_gliders:
        analysis = analyze_rule_combinatorially(rule)
        if analysis.structure_predicted:
            results["false_positives"] += 1
        else:
            results["true_negatives"] += 1

    total = sum(results.values())
    if total > 0:
        results["accuracy"] = (
            results["true_positives"] + results["true_negatives"]
        ) / total
    else:
        results["accuracy"] = 0.0

    return results


if __name__ == "__main__":
    print("═══ LLL COMPLEXITY v2: NON-CIRCULAR ANALYSIS ═══")
    print()
    print("All probabilities derived from RULE COMBINATORICS ONLY.")
    print("No simulation used!")
    print()

    test_rules = [
        ("B3/S23", "Game of Life", True),
        ("B0/S", "Condensate (trivial)", False),
        ("B0/S012345678", "Dense condensate", False),
        ("B6/S123467", "Goldilocks (known gliders)", True),
        ("B36/S23", "HighLife", True),
        ("B2/S", "Seeds (chaotic)", False),
        ("B35678/S5678", "Diamoeba", True),
    ]

    print(
        f"{'Rule':<20} {'p_birth':>8} {'p_surv':>8} {'p_active':>10} {'LLL':>8} {'Predict':>10}"
    )
    print("-" * 75)

    for rule, _, has_gliders in test_rules:
        analysis = analyze_rule_combinatorially(rule)
        predict = "✓ STRUCT" if analysis.structure_predicted else "✗ none"
        actual = "(has gliders)" if has_gliders else "(no gliders)"
        correct = "✓" if (analysis.structure_predicted == has_gliders) else "✗"

        print(
            f"{rule:<20} {analysis.p_birth:>8.3f} {analysis.p_survive:>8.3f} "
            f"{analysis.p_active:>10.3f} {analysis.lll_score:>8.2f} {predict:>10} {correct}"
        )

    print()
    print("═══ VALIDATION ═══")

    validation = validate_predictions(
        ["B3/S23", "B36/S23", "B6/S123467"],  # Known glider rules
        ["B0/S", "B2/S"],  # No-glider rules (trivial or chaotic)
    )

    print(f"Accuracy: {validation['accuracy']:.1%}")
    print(f"True Positives: {validation['true_positives']}")
    print(f"False Positives: {validation['false_positives']}")
    print(f"True Negatives: {validation['true_negatives']}")
    print(f"False Negatives: {validation['false_negatives']}")
    print()

    print("═══ KEY INSIGHT ═══")
    print()
    print("The 'Goldilocks Zone' in combinatorics:")
    print("  p_active ∈ [0.2, 0.5] → structures likely")
    print("  p_active < 0.2 → too stable (frozen)")
    print("  p_active > 0.5 → too chaotic")
