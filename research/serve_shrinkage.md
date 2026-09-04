# Serve shrinkage and temporal uncertainty pilot

**Experiment:** `research-serve-shrinkage-v0.1`

**Status:** temporal predictive falsification; no player ranking or profile is produced

## Design boundary

The experiment uses 22,661 collision-safe
match-player records from 11,336 matches. Five historical seasons train
each fold, the following season selects one of the fixed prior strengths
`[0, 25, 100, 400]`, and the next season is untouched test data.
Eligibility uses only pre-validation match counts on the 2/5/10/20 grid.

Context baselines use tour, surface, and opponent-rank band with documented backoff. The target
player is removed from every context baseline. Binary targets use stabilized Beta-style means;
direction targets use stabilized Dirichlet-style means by court side. Scores average within match
before averaging across matches.

## Results

| Target | Training matches | Folds | Players | Test matches | Context loss | Raw loss | Shrunk loss | Shrunk-context bootstrap | Shrunk-raw bootstrap | Posterior SD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `first_serve_in_rate` | 2 | 46 | 448 | 8,553 | 0.6610 | 0.6591 | 0.6589 | -0.0024 to -0.0019 | -0.0004 to -0.0002 | 0.0113 |
| `first_serve_in_rate` | 5 | 43 | 307 | 7,345 | 0.6602 | 0.6585 | 0.6582 | -0.0022 to -0.0018 | -0.0003 to -0.0002 | 0.0100 |
| `first_serve_in_rate` | 10 | 40 | 204 | 5,908 | 0.6589 | 0.6571 | 0.6570 | -0.0022 to -0.0017 | -0.0002 to -0.0001 | 0.0086 |
| `first_serve_in_rate` | 20 | 37 | 111 | 4,166 | 0.6569 | 0.6550 | 0.6550 | -0.0022 to -0.0017 | -0.0001 to -0.0000 | 0.0074 |
| `ace_per_service_point` | 2 | 46 | 448 | 8,553 | 0.2734 | 0.2672 | 0.2667 | -0.0072 to -0.0063 | -0.0006 to -0.0003 | 0.0056 |
| `ace_per_service_point` | 5 | 43 | 307 | 7,345 | 0.2821 | 0.2752 | 0.2751 | -0.0075 to -0.0064 | -0.0002 to 0.0000 | 0.0051 |
| `ace_per_service_point` | 10 | 40 | 204 | 5,908 | 0.2917 | 0.2846 | 0.2845 | -0.0079 to -0.0066 | -0.0003 to -0.0001 | 0.0045 |
| `ace_per_service_point` | 20 | 37 | 111 | 4,166 | 0.3023 | 0.2960 | 0.2958 | -0.0072 to -0.0057 | -0.0002 to -0.0001 | 0.0039 |
| `double_fault_per_second_serve_attempt` | 2 | 46 | 448 | 8,553 | 0.3234 | 0.3199 | 0.3194 | -0.0044 to -0.0036 | -0.0007 to -0.0003 | 0.0107 |
| `double_fault_per_second_serve_attempt` | 5 | 43 | 307 | 7,345 | 0.3188 | 0.3149 | 0.3147 | -0.0046 to -0.0037 | -0.0003 to -0.0000 | 0.0094 |
| `double_fault_per_second_serve_attempt` | 10 | 40 | 204 | 5,908 | 0.3147 | 0.3103 | 0.3103 | -0.0049 to -0.0037 | -0.0001 to 0.0002 | 0.0081 |
| `double_fault_per_second_serve_attempt` | 20 | 37 | 111 | 4,165 | 0.3033 | 0.2987 | 0.2988 | -0.0051 to -0.0039 | -0.0000 to 0.0002 | 0.0069 |
| `first_serve_direction` | 2 | 46 | 448 | 8,551 | 0.9827 | 0.9627 | 0.9602 | -0.0236 to -0.0213 | -0.0029 to -0.0020 | 0.0184 |
| `first_serve_direction` | 5 | 43 | 307 | 7,343 | 0.9761 | 0.9547 | 0.9536 | -0.0236 to -0.0214 | -0.0015 to -0.0009 | 0.0161 |
| `first_serve_direction` | 10 | 40 | 204 | 5,906 | 0.9715 | 0.9497 | 0.9491 | -0.0237 to -0.0210 | -0.0009 to -0.0003 | 0.0137 |
| `first_serve_direction` | 20 | 37 | 111 | 4,165 | 0.9637 | 0.9414 | 0.9414 | -0.0241 to -0.0206 | -0.0003 to 0.0003 | 0.0115 |
| `second_serve_direction` | 2 | 46 | 448 | 8,548 | 1.0662 | 1.0307 | 1.0242 | -0.0444 to -0.0401 | -0.0076 to -0.0054 | 0.0235 |
| `second_serve_direction` | 5 | 43 | 307 | 7,343 | 1.0674 | 1.0264 | 1.0229 | -0.0470 to -0.0422 | -0.0044 to -0.0027 | 0.0207 |
| `second_serve_direction` | 10 | 40 | 204 | 5,906 | 1.0693 | 1.0231 | 1.0221 | -0.0500 to -0.0444 | -0.0018 to -0.0002 | 0.0181 |
| `second_serve_direction` | 20 | 37 | 111 | 4,164 | 1.0727 | 1.0247 | 1.0242 | -0.0515 to -0.0454 | -0.0013 to 0.0003 | 0.0153 |

Negative bootstrap ranges favor shrinkage. Ranges crossing zero are inconclusive. Posterior
standard deviation is a model-based diagnostic, not a confidence interval; it does not capture MCP
selection, charting error, or all within-match dependence.

## Adversarial review

Every target beats the context-only comparator overall and within ATP and WTA at all four exposure
thresholds. That is evidence that historical player-surface behavior contains some later-season
predictive information beyond these coarse context fields. It is not evidence that the current
context model is complete or that the effect is causal.

The comparison with the raw player estimate is less uniform. The table below shows the least and
most restrictive exposure endpoints; the machine-readable artifact retains all thresholds and
folds.

| Target | Matches | Overall vs raw | ATP vs raw | WTA vs raw | Folds favoring context | Folds favoring raw | Selected strengths |
|---|---:|---|---|---|---:|---:|---|
| `first_serve_in_rate` | 2 | favors shrinkage | favors shrinkage | favors shrinkage | 42/46 | 30/46 | 0:4, 25:4, 100:11, 400:27 |
| `first_serve_in_rate` | 20 | favors shrinkage | favors shrinkage | favors shrinkage | 31/37 | 20/37 | 0:7, 100:4, 400:26 |
| `ace_per_service_point` | 2 | favors shrinkage | favors shrinkage | favors shrinkage | 45/46 | 30/46 | 0:6, 25:3, 100:22, 400:15 |
| `ace_per_service_point` | 20 | favors shrinkage | favors shrinkage | inconclusive | 36/37 | 20/37 | 0:12, 25:1, 100:5, 400:19 |
| `double_fault_per_second_serve_attempt` | 2 | favors shrinkage | favors shrinkage | favors shrinkage | 42/46 | 32/46 | 0:4, 25:8, 100:20, 400:14 |
| `double_fault_per_second_serve_attempt` | 20 | inconclusive | inconclusive | inconclusive | 32/37 | 12/37 | 0:16, 25:3, 100:5, 400:13 |
| `first_serve_direction` | 2 | favors shrinkage | favors shrinkage | favors shrinkage | 46/46 | 35/46 | 0:2, 25:18, 100:24, 400:2 |
| `first_serve_direction` | 20 | inconclusive | inconclusive | inconclusive | 36/37 | 16/37 | 0:10, 25:5, 100:11, 400:11 |
| `second_serve_direction` | 2 | favors shrinkage | favors shrinkage | favors shrinkage | 46/46 | 37/46 | 0:1, 25:24, 100:18, 400:3 |
| `second_serve_direction` | 20 | inconclusive | inconclusive | inconclusive | 37/37 | 11/37 | 0:12, 25:4, 100:14, 400:7 |

At two training matches, shrinkage beats raw estimates for all targets overall and in both tours.
At twenty matches, the advantage remains clear for first-serve-in rate, remains clear overall and
for ATP aces, and is inconclusive for the remaining tour/target comparisons. This is compatible
with shrinkage helping sparse histories and converging toward raw estimates as exposure grows.
It also means the experiment does not justify one universal shrinkage strength.

Validation selected both zero and the maximum strength. Maximum-strength selections are frequent
for the binary outcomes, especially first-serve-in rate, so the upper grid boundary remains a model
adequacy question. Fold-level wins are less uniform than aggregate wins, especially against the
raw player comparator. Binary calibration scores are descriptive because no acceptance cutoff was
pre-specified.

**DATA-QUALITY DECISION:** retain all five serve targets for a bounded feature-definition review;
do not approve a composite vector or player output. Preserve raw and shrunk estimates as competing
candidates until the estimand, reporting period, exposure policy, and uncertainty display are
chosen explicitly.

## Interpretation boundary

This experiment tests prediction in later charted seasons, not causality or universal player
identity. Validation chooses shrinkage strength separately for each target, exposure threshold, and
fold. Test data never select a strength. No player estimate is serialized.

**OPEN QUESTION:** feature-by-feature decisions require reviewing aggregate, ATP/WTA, exposure,
calibration, strength-boundary, and period consistency together. A favorable overall score cannot
override a tour reversal or sparse low-exposure result.

## Reproduce

```powershell
python -m research.experiments.serve_shrinkage
```
