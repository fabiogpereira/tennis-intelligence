# ADR-013: First-serve direction needs temporal process uncertainty

**Status:** Accepted; current interval model rejected for player stability

**Date:** 2026-09-04

## Context

First-serve direction has strong parser coverage, 98.6% side-aware aggregate reconciliation,
context-stratified persistence, and later-season predictive signal. The publication-readiness audit
showed that match clustering produces materially wider uncertainty than a conditional Dirichlet
count model. It remained unknown whether either diagnostic covers later-season variation.

## Decision

**STATISTICAL DECISION:** retain `first-serve-in-direction-share-v0.1-candidate` as an internal
descriptive measurement, but reject conditional Dirichlet or match-cluster-only intervals as a
player-stability uncertainty model.

Across pre-specified 2/3/5/8-season windows and 2/5/10/20 historical-match thresholds, empirical
clustered component coverage is approximately 77%-82%, below the 95% diagnostic reference. Higher
exposure narrows sampling uncertainty but does not remove the history-to-test difference. The next
candidate must estimate temporal/process variation using validation seasons and evaluate it on
untouched later seasons.

Do not expand the shrinkage-prior grid until this temporal uncertainty problem is addressed.

## Consequences

- First-serve direction remains useful for internal descriptive research, not player publication.
- Match clustering is necessary but insufficient for a stability claim.
- A future model must separate sampling uncertainty from season-to-season process variation.
- ATP/WTA, surface, component, and period calibration remain visible; no global correction is
  assumed.
- No player estimate, ranking, similarity, profile, or confidence badge is authorized.

## Alternatives rejected

- Treating conditional count intervals as confidence: empirically undercovers later seasons.
- Treating match clustering as the complete fix: coverage remains materially low.
- Selecting the shortest or best-looking window: the grid is sensitivity evidence, not a contest.
- Increasing pooling immediately: it could hide temporal misspecification without calibrating
  uncertainty.
