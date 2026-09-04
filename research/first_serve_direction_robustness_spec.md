# First-serve direction temporal robustness specification

**Experiment ID:** `research-first-serve-direction-robustness-v0.1`

**Status:** pre-specified aggregate falsification; no player output

## Question

**PROJECT HYPOTHESIS:** a player's surface-specific distribution of successful first-serve
directions contains information that persists into a later complete season across reasonable
historical windows.

This experiment tests the raw measurement candidate before expanding the shrinkage-prior grid.
Failure of raw temporal coverage would weaken the case for solving that failure only by stronger
pooling.

## Inputs and feature definition

- Use the 22,661 collision-safe contextual match-player records from the pinned MCP and context
  snapshots.
- Use `first-serve-in-direction-share-v0.1-candidate` exactly as defined in
  `research/first_serve_direction_measurement_spec.md`.
- Keep deuce/ad and wide/body/T as six separate components.
- A match is eligible for vector estimation only when both court sides have at least one known
  successful first-serve direction. Audit records with direction on only one side separately.
- Keep ATP and WTA separate in reported breakdowns.
- Never serialize player identities or estimates.

## Reconciliation boundary

Read first-serve direction reconciliation from the canonical MCP profile. Report side-aware
mismatch rates by tour, surface, season, and chart author using comparable-record denominators.
Contributor concentration is a source-production diagnostic, not evidence of individual fault.

## Temporal design

Evaluate fixed historical windows of 2, 3, 5, and 8 complete seasons immediately before each test
season. The latest partial observed season is excluded as a test season. Player-surface eligibility
uses only the historical window and the fixed minimum-history-match grid 2/5/10/20. At least two
eligible matches in the test season are required to estimate test-season clustered uncertainty.

Requiring test observations defines an evaluation cohort but does not select a model or threshold.
Report empty folds and cohort size rather than silently dropping window/threshold combinations.

## Estimator and uncertainty diagnostics

For every eligible player-surface, estimate six raw direction shares by summing eligible events.
For each component calculate:

- historical raw share;
- historical zero-strength Dirichlet mean and conditional standard deviation;
- match-clustered ratio standard error in history;
- test-season raw share;
- test-season conditional and clustered standard errors; and
- absolute historical-to-test difference.

The component-level diagnostic interval covers the test-season share when the absolute difference
is no larger than `1.96 * sqrt(history_se^2 + test_se^2)`. Calculate this separately using
conditional count-model deviations and match-clustered standard errors. This is empirical
later-season component coverage, not a calibrated confidence interval: normal approximation,
temporal drift, sparse clusters, multiple correlated components, and selected charting all remain.

Average absolute error and component coverage within player-surface before aggregate averaging, so
players with more charted points do not dominate the result.

## Court-side support

For every historical estimate report the smaller court-side share of eligible direction events,
`min(deuce_events, ad_events) / total_events`. Preserve quantiles and sensitivity counts for at
least 10%, 20%, 30%, and 40% on the smaller side. These are diagnostics, not eligibility rules.

## Outputs

Report aggregate results overall and by window, minimum history matches, tour, surface, and test
season. Include the any-side versus both-side record audit and reconciliation context. The
human-readable report may summarize the window/threshold grid while the JSON preserves all
pre-specified breakdowns.

## Falsification criteria

Revise or stop the candidate when:

- later-season error or empirical coverage materially worsens for shorter or longer reasonable
  windows without a defensible period interpretation;
- clustered coverage remains substantially below its nominal diagnostic reference even at higher
  match exposure;
- conditional coverage looks adequate only because it ignores match dependence;
- results reverse by tour, surface, or period;
- one court side is routinely supported by very few events; or
- mismatch concentration aligns with the periods or surfaces driving the apparent signal.

No window, match threshold, coverage cutoff, or prior strength is approved automatically. Expanded
prior-boundary analysis follows only if the raw candidate survives this gate. Tennis DNA,
similarity, rankings, confidence badges, and the final application remain blocked.
