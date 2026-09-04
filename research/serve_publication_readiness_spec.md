# Serve publication-readiness audit specification

**Experiment ID:** `research-serve-publication-readiness-v0.1`

**Status:** pre-specified aggregate coverage and uncertainty audit; no player output

## Question

**OPEN QUESTION:** how much of the MCP player-surface sample has diversified match coverage and
match-clustered precision compatible with a future bounded profile?

This audit does not decide that a profile is publishable. It measures the consequences of possible
coverage rules before a human chooses any rule and before recognizable player estimates are
inspected.

## Inputs and time boundary

- Use the collision-free 22,661 contextual match-player records from the pinned MCP and context
  snapshots.
- For every observed as-of season with five preceding seasons, form player-surface histories using
  only those preceding five seasons. Do not create a cutoff after the latest observed season,
  because that would treat the latest partial season as complete.
- Do not require a player to appear after the as-of date. This is a coverage audit, not a predictive
  cohort, and must not condition inclusion on future participation.
- Keep ATP and WTA separate in every reported breakdown.
- Emit counts and distribution summaries only; never serialize player identities or estimates.

## Target-specific exposure

Audit the same five targets as `research-serve-shrinkage-v0.1`. A match contributes only when the
target's own denominator is valid. First- and second-serve direction continue to require observed
wide/body/T counts on both court sides.

For every player-surface history, calculate:

- distinct eligible matches;
- distinct seasons, opponents, tournaments, and chart authors;
- eligible-event total;
- largest single-match share of eligible events; and
- Kish-style effective match count, `1 / sum(match_event_share^2)`.

Event totals are the binary denominator or, for direction, the combined deuce/ad denominator.
Effective match count describes concentration; it is not a replacement for distinct matches.

## Fixed sensitivity grids

Report coverage without selecting a cutoff over these fixed marginal grids:

- distinct matches: 2, 5, 10, and 20;
- distinct seasons: 1, 2, and 3;
- distinct opponents: 2, 3, and 5;
- distinct tournaments: 1, 2, and 3;
- distinct chart authors: 1 and 2;
- largest-match event share at most 0.75, 0.50, and 0.33; and
- effective match count at least 2, 5, 10, and 20.

Also report one explicitly labeled diagnostic intersection: at least five matches, two seasons,
three opponents, two tournaments, no match above 50% of events, and effective match count at least
three. It is a stress test, not an approved publication policy.

## Match-clustered uncertainty

For histories with at least two eligible matches, estimate the raw ratio of summed target events.
Use the match as the independent cluster. For a binary component with match counts `(success_i,
trial_i)`, use the ratio-estimator cluster variance based on `success_i - rate * trial_i`, with the
finite-cluster correction `m / (m - 1)`. For direction, calculate the same diagnostic separately
for wide/body/T and report the largest component standard error across both court sides.

Report aggregate quantiles of the approximate 95% half-width (`1.96 * standard error`) and the
ratio between cluster-robust standard error and the zero-strength conditional Beta/Dirichlet
count-model standard deviation. This reuses the shrinkage-pilot implementation without selecting
a prior strength for this audit. These are diagnostics, not calibrated confidence or credible
intervals. Do not truncate widths to the probability boundary before summarizing.

## Breakdowns

Report all-player-surface summaries overall and by target, tour, surface, and as-of season. To keep
the human-readable report bounded, it may show overall target/tour summaries while retaining
surface and season aggregates in machine-readable output. Empty cells remain explicit.

## Falsification and stopping criteria

Publication readiness is weakened when:

- coverage collapses under modest diversity or concentration safeguards;
- nominal match counts substantially exceed effective match counts;
- cluster-robust uncertainty materially exceeds the conditional posterior diagnostic;
- conclusions reverse by tour, surface, or period; or
- apparently precise cohorts are dominated by one tournament, opponent, or chart author.

No threshold is selected by this experiment. A subsequent human decision must name the product
claim first, then justify any eligibility and uncertainty policy against the full sensitivity
output. Tennis DNA, similarity, rankings, confidence badges, and the final application remain
blocked.
