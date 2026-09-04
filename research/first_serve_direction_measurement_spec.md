# First-serve direction measurement specification

**Candidate ID:** `first-serve-in-direction-share-v0.1-candidate`

**Status:** internal descriptive measurement; process uncertainty retained but not publishable

## Intended claim

**PROJECT HYPOTHESIS:** within a documented player-surface-period charted sample, the distribution
of successful first serves across wide, body, and T directions may describe one component of serve
behavior.

The metric does not estimate intended direction across all attempts. It does not measure serve
quality, placement precision, tactics independent of context, or a timeless player characteristic.

## Unit and period

- Unit: player, normalized surface, and reporting period.
- Candidate period: the five complete seasons preceding an as-of season.
- Source unit: an eligible service point in the collision-safe MCP/context sample.
- Partial current seasons do not enter a completed five-season period.
- ATP and WTA remain separate analytical populations.

Five seasons is inherited from the temporal falsification design for comparability. It is not yet
an approved public recency rule.

## Components

Produce six candidate components, never one scalar:

- deuce court: wide, body, and T share;
- ad court: wide, body, and T share.

Each court-side vector sums to one independently. The numerator is the safely parsed direction
count for that side. The denominator is first serves that landed in with known direction and known
court side. Faults, direction `0`, exceptional points, unresolved scores, invalid serve prefixes,
and ambiguous match identities are excluded rather than imputed.

The public-facing word `body` is preferred even though the internal MCP direction code is named
`middle`. Any rename must be presentation-only and tested against this mapping.

## Estimator candidates

Two internal estimators remain visible:

1. the stabilized raw player-surface distribution; and
2. partial pooling toward a leave-player-out tour/surface/opponent-rank-band baseline.

No fixed prior strength is approved. The temporal pilot found sparse-history predictive gains but
also selected zero and boundary strengths in some folds. Estimator selection must not inspect
recognizable player profiles.

## Coverage and uncertainty contract

Every internal result must carry target-specific eligible events and these match-level diagnostics:

- distinct matches, seasons, opponents, tournaments, and chart authors;
- largest single-match event share;
- effective match count; and
- match-clustered uncertainty for all six components.

Conditional Dirichlet posterior deviation may be retained as a model diagnostic but must not be
named `confidence`. In the publication-readiness audit, median match-clustered uncertainty remains
about 1.66 times the conditional diagnostic even among histories with at least twenty matches.

No public minimum exposure or confidence category is defined. Surface-specific availability must
remain visible because grass histories are materially sparser than hard-court histories.

## Required next falsification

Before implementation as a player-facing feature:

1. resolve or bound the remaining first-serve direction reconciliation mismatches by period,
   surface, and chart author;
2. test sensitivity to reporting windows without using partial seasons;
3. retain validation-estimated temporal/process variance as an internal candidate and audit its
   width, fallback, and future-display interpretation;
4. jointly test raw/shrunk centers with process-aware uncertainty before revisiting publication;
5. define what happens when one court side is sparse while the other is not; and
6. obtain human approval for an exposure and uncertainty policy using aggregate outputs only.

## Product boundary

**ENGINEERING DECISION:** this specification may guide internal transformations and tests. It does
not authorize persistence of player estimates, a radar chart, rankings, similarity, clustering,
feature weighting, confidence badges, or the final application.

## Evidence

- [Candidate definitions](serve_feature_candidates.md)
- [Serve reconciliation](mcp_serve_reconciliation.md)
- [Context-controlled stability](context_serve_stability.md)
- [Temporal shrinkage](serve_shrinkage.md)
- [Publication-readiness audit](serve_publication_readiness.md)
- [Feature decision review](serve_feature_decision_review.md)
- [Coverage and uncertainty decision](../docs/decisions/ADR-012-serve-coverage-and-clustered-uncertainty.md)
- [Temporal robustness audit](first_serve_direction_robustness.md)
- [Process-uncertainty audit](first_serve_direction_process_uncertainty.md)
- [Temporal uncertainty decision](../docs/decisions/ADR-013-first-serve-direction-temporal-uncertainty.md)
- [Process-variance decision](../docs/decisions/ADR-014-validation-estimated-direction-process-variance.md)
