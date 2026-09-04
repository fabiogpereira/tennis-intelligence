# ADR-011: Serve shrinkage and temporal evaluation

**Status:** Accepted for Phase 2 falsification; not approved for player publication

**Date:** 2026-09-04

## Context

The aggregate and context-controlled stability pilots retain five serve targets, but raw
player-surface rates are noisy for sparse histories. Selecting a minimum exposure or pooling rule
after viewing recognizable players would create avoidable researcher flexibility. Point-level
random splits would also leak later behavior and overstate independent evidence.

## Decision

**ENGINEERING DECISION:** `research-serve-shrinkage-v0.1` uses rolling seasons. Five seasons train
the candidate estimates, the next season selects a prior strength from 0/25/100/400 eligible
events, and the following season is untouched test data. The test history is then refit on the five
immediately preceding seasons. Eligibility is reported on the pre-specified 2/5/10/20 distinct-
match grid rather than reduced to one cutoff.

Binary targets use stabilized Beta-style posterior means. Direction targets use stabilized
Dirichlet-style posterior means by court side. Player-surface histories shrink toward a tour,
surface, and opponent-rank-band baseline with documented backoff. The target player's contribution
is removed from its context comparator. Evaluation uses match-average log loss, Brier score,
binary calibration diagnostics, and deterministic paired bootstrap ranges over test matches.

No individual estimate, ranking, similarity, or profile is serialized by this experiment.

## Consequences

- Sparse estimates can be compared with raw player and context-only predictions out of time.
- Test outcomes cannot select prior strength, although requiring test-period presence conditions
  the evaluation cohort on future availability.
- The posterior standard deviation is conditional on a simplified count model. It does not cover
  match selection, charting error, unmeasured context, or within-match dependence.
- A maximum-grid selection signals an unresolved boundary; it does not license extrapolating to a
  stronger prior.
- Results remain specific to the selected MCP charted sample and the pinned context mirror.
- Feature approval remains a separate human decision. Tennis DNA construction stays blocked.

## Alternatives rejected

- One post-hoc exposure cutoff: too sensitive to the observed result.
- Random point or match splits: weaker protection against temporal leakage and drift.
- Raw rates only: needlessly unstable for low exposure.
- One global prior strength: hides target, period, and exposure heterogeneity.
- Publishing player intervals now: overstates what the conditional count model measures.
