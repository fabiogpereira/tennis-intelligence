# ADR-014: Validation-estimated direction process variance

**Status:** Retained for internal uncertainty research; not approved for publication

**Date:** 2026-09-04

## Context

Match-clustered uncertainty for raw first-serve direction covers only approximately 77%-82% of
later-season component shares across pre-specified historical windows and exposure thresholds.
This indicates season-to-season process variation beyond point and match sampling uncertainty.

## Decision

**STATISTICAL DECISION:** retain a validation-estimated additive process variance as the next
internal uncertainty candidate. For each rolling fold, tour, and direction component, the model
uses training-to-validation residuals to estimate the extra variance required for the deterministic
finite-sample 95th-percentile calibration rule. Sparse tour-component estimates back off to pooled
component and then global estimates. Test seasons remain untouched.

Across the pre-specified grid, process-aware aggregate test coverage is approximately 95.0%-96.3%,
compared with 77.4%-82.4% for match-clustered sampling uncertainty alone.

## Consequences

- Temporal/process variation must be distinct from sampling uncertainty in future models.
- Calibration is achieved with mean radii roughly 1.5-1.8 times the base radii, so product utility
  and precision remain unresolved.
- Older strict-threshold folds use pooled/global fallbacks heavily; WTA high-exposure and grass
  results remain sparse.
- Evaluation radii include test-season sampling variance. They are not directly displayable future
  intervals.
- The model may proceed to joint center/uncertainty falsification, but no player output is allowed.

## Alternatives rejected

- Match clustering alone: later-season coverage is inadequate.
- One global fixed multiplier: hides component and tour variation.
- Tuning on test coverage: violates the temporal boundary.
- Automatic publication after reaching 95% aggregate coverage: ignores width, fallback, and sparse
  subgroup behavior.
