# Serve shrinkage and uncertainty specification

**Experiment ID:** `research-serve-shrinkage-v0.1`

**Status:** pre-specified temporal prediction experiment; no player output

## Question

**PROJECT HYPOTHESIS:** a partially pooled player-surface estimate may predict the player's future
charted serve behavior better than a tour/context baseline or an unpooled player rate.

Prediction is used as a falsification device. Better held-out prediction would support, but not
prove, a persistent player characteristic. It does not establish causality, talent, intention, or
representativeness beyond the charted MCP sample.

## Inputs and identity boundary

- Use the 22,661 contextual match-player records accepted by
  `research-context-serve-stability-v0.1`.
- Preserve the same collision, join, parsing, denominator, and missing-rank treatment.
- Group player history by normalized MCP player identity and normalized surface.
- Use source-reported opponent rank only through the fixed bands already defined.
- Emit aggregate scores and uncertainty diagnostics only; never serialize player estimates.

## Targets

Evaluate five targets separately:

1. `first_serve_in_rate`;
2. `ace_per_service_point`;
3. `double_fault_per_second_serve_attempt`;
4. `first_serve_direction`; and
5. `second_serve_direction`.

The binary targets retain their versioned feature-specific denominators. Direction remains a
wide/body/T categorical distribution evaluated separately on deuce and ad courts.

## Temporal design

For every possible test season with six preceding seasons in the snapshot:

- training history: test year minus six through test year minus two (five seasons);
- validation: test year minus one;
- test: the test season;
- select shrinkage strength on validation only;
- refit player and context counts on the five seasons immediately preceding test, including the
  validation season and dropping the oldest training season;
- evaluate once on the untouched test season.

All points from a match stay together. Eligibility is determined before validation from distinct
training matches, using the fixed grid 2/5/10/20. A player-surface must also appear in validation
and test. Empty folds and sparse cohorts are reported, not silently omitted.

## Predictors

| Predictor | Definition |
|---|---|
| Tour baseline | Tour-level training counts |
| Context baseline | Tour + surface + opponent-rank-band counts, backing off to tour + surface and then tour only when a denominator is absent |
| Raw player | Player-surface training counts with only boundary stabilization |
| Shrunk player | Player-surface counts partially pooled toward the match-specific context baseline |

Binary rates use a Beta-style posterior mean with a Jeffreys `0.5/0.5` stabilizer. Direction uses a
Dirichlet-style mean with `0.5` per category. Candidate prior strengths are fixed at 0, 25, 100,
and 400 eligible events. Ties select the smaller strength. These are engineering estimators for
prediction, not claims that observations are independent Bernoulli or multinomial trials.

Every tour and context baseline removes the target player's own contribution before prediction,
then backs off when no other eligible event remains. This prevents the comparator from partially
encoding the same player history that the player-specific predictors are meant to test.

## Evaluation and uncertainty

- Primary score: match-average negative log loss; direction averages deuce/ad observations.
- Secondary score: match-average Brier score (positive-class squared error for binary targets and
  summed component squared error for direction targets).
- Binary calibration: ten fixed probability bins and expected calibration error.
- Report selected-strength frequencies rather than presenting one universal optimum.
- Report results overall, by tour, exposure threshold, target, and test season coverage.
- Use a deterministic 200-replicate paired bootstrap over test matches for score differences
  between shrunk versus context and shrunk versus raw predictors.
- Report the median approximate posterior standard deviation of shrunk estimates as an uncertainty
  diagnostic. It is not a frequentist confidence interval and does not account for source
  selection or within-match dependence.

Point-weighted likelihood is intentionally not the primary score because longer matches should not
masquerade as independent replication. Calibration and prediction are evaluated only out of time.

## Falsification criteria

A target is weakened or rejected when shrinkage fails to improve held-out match-average log loss
over the context baseline, fails to improve over the raw player estimate, has paired-bootstrap
ranges materially crossing zero, is miscalibrated, reverses by tour or period, or works only in the
highest-exposure cohort. A selected strength of zero is valid negative evidence against pooling;
selection of the maximum grid value is evidence that the grid boundary requires review, not proof
that stronger pooling is optimal.

No target is approved automatically. Null, adverse, sparse, and contradictory results remain in
the report. Tennis DNA construction, similarity, rankings, and public player confidence labels stay
blocked after this experiment pending a feature-by-feature human gate.
