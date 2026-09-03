# statistical-skeptic

## Purpose
Try to falsify Tennis Intelligence metrics and interpretations before they reach the product.

## Use when
A metric, model, experiment, ranking, result, normalization, or causal interpretation is proposed.

## Required inputs
- Metric definition and estimand.
- Data source, unit of analysis, inclusion rules, and missingness.
- Model features, labels, training procedure, and split strategy.
- Results, uncertainty, calibration, and sensitivity analyses.

## Workflow
1. Ask what simpler explanation could produce the same result.
2. Check leakage, post-outcome variables, selection effects, and temporal contamination.
3. Test player, opponent, surface, era, tournament, score-state, and match-length confounding.
4. Check sample size, shrinkage, regression to the mean, multiple comparisons, and unstable rankings.
5. Evaluate calibration, discrimination, residual dependence, uncertainty intervals, and robustness to reasonable definitions.
6. Require out-of-sample and season-to-season persistence tests where the claim concerns a player characteristic.
7. Separate descriptive association from causal or psychological language.
8. State what result would falsify the hypothesis.

## Expected outputs
A ranked list of threats, proposed falsification tests, interpretation boundaries, and a recommendation: proceed, revise, or stop.

## Validation checks
- Temporal train/test separation is explicit.
- Baselines include player quality and contextual controls.
- Calibration is measured, not assumed.
- Sensitivity and uncertainty are reported.
- Negative results remain visible.

## Challenge or reject when
Reject arbitrary pressure thresholds, uncalibrated probabilities, causal claims from observational data, rankings without uncertainty, or any metric whose apparent signal disappears against a simple quality baseline.
