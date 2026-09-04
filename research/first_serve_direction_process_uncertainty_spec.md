# First-serve direction process-uncertainty specification

**Experiment ID:** `research-first-serve-direction-process-uncertainty-v0.1`

**Status:** pre-specified temporal calibration experiment; no player output

## Question

**PROJECT HYPOTHESIS:** adding validation-estimated season-to-season process variation to
match-clustered sampling uncertainty can improve later-season coverage for first-serve direction.

This experiment calibrates uncertainty, not the player estimate. It does not change the raw
direction-share center, choose a shrinkage prior, or establish that temporal residuals are random
or stationary.

## Inputs and target

- Use the same collision-safe records, parser, identity exclusions, and six-component
  `first-serve-in-direction-share-v0.1-candidate` definition as the temporal robustness audit.
- Require observed wide/body/T direction on both deuce and ad court for each contributing match.
- Exclude the latest partial observed season from validation and test roles.
- Emit aggregate calibration diagnostics only; never serialize player identities, estimates, or
  interval endpoints.

## Rolling temporal design

For each test season and each pre-specified 2/3/5/8-season window:

1. training history ends before the validation season;
2. validation is test year minus one;
3. use training-to-validation residuals to estimate process variation;
4. refit the raw history window immediately before test, including validation and dropping the
   oldest season; and
5. evaluate interval coverage on the untouched test season.

Use the fixed 2/5/10/20 minimum historical-match grid and require at least two matches in validation
or test when that season supplies a clustered share. Eligibility for process calibration uses only
training plus validation. Test eligibility uses only the refit history plus test availability.

## Process-variance estimator

For each tour and direction component, calculate validation cases with:

- absolute training-to-validation raw-share residual `r`; and
- base comparison variance `v`, the sum of training and validation match-clustered variances.

For each case, the additional variance required for nominal 95% coverage is
`max(0, (r / 1.96)^2 - v)`. Select the deterministic finite-sample 95th percentile of these required
variances. This value is the component/tour process variance for the fold.

Require at least 30 validation cases for a tour-component estimate. Otherwise back off to the
pooled component estimate across tours; if that also has fewer than 30 cases, use the pooled value
across every component. Report every backoff. The count is a pre-specified estimation safeguard,
not a player eligibility threshold.

## Test comparison

For each test component, compare:

- base clustered radius: `1.96 * sqrt(history_variance + test_variance)`; and
- process-aware radius: `1.96 * sqrt(history_variance + test_variance + process_variance)`.

Report component coverage, mean radius, process-standard-deviation quantiles, and changes from the
base interval. Average components within player-surface before aggregate averaging. Preserve
overall, ATP/WTA, surface, component, window, exposure, and test-year results.

The test-season sampling variance is used only to evaluate whether two noisy seasonal shares are
compatible. A future displayed interval would omit unavailable future sampling variance and use
history plus process variance. This experiment does not authorize such a display.

## Falsification criteria

Revise or reject the process model when:

- test coverage remains materially below 90% across well-populated configurations;
- nominal improvement appears only through extremely wide radii;
- coverage reverses by tour, surface, component, or period;
- process estimates repeatedly require fallback or are unstable across folds; or
- the calibration works only at one convenient window or exposure threshold.

Coverage above 95% is not automatically good: excessive width and overcoverage remain visible.
No target coverage is used to tune the estimator after test results are observed.

No window, match threshold, process variance, shrinkage strength, or publication policy is approved
automatically. Tennis DNA, player profiles, similarity, rankings, and confidence badges remain
blocked.
