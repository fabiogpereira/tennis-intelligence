# First-serve direction temporal robustness

**Experiment:** `research-first-serve-direction-robustness-v0.1`

**Status:** aggregate falsification; no player output

## Input checks

The collision-safe input contains
22,661 match-player records.
Among records with any known successful first-serve direction, 22,658 contain both
court sides and 1 contain only one. The both-side eligibility rate is
100.00%.

Canonical side-aware reconciliation is 98.59% across
22,528 comparable records:

| Surface | Comparable | Mismatches | Mismatch rate |
|---|---:|---:|---:|
| `hard` | 14,743 | 205 | 1.39% |
| `clay` | 5,307 | 62 | 1.17% |
| `grass` | 2,478 | 51 | 2.06% |

## Temporal results

Each row aggregates player-surface-period results over complete test seasons. Coverage is the share
of six component comparisons whose later-season raw share falls inside the diagnostic combined
history/test radius.

| Window | History matches | Periods | Players | Mean error | Conditional coverage | Clustered coverage | Median smaller-side share |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 2 | 2,247 | 418 | 0.074 | 0.781 | 0.815 | 0.472 |
| 2 | 5 | 1,315 | 267 | 0.062 | 0.768 | 0.824 | 0.472 |
| 2 | 10 | 675 | 158 | 0.053 | 0.759 | 0.821 | 0.471 |
| 2 | 20 | 231 | 57 | 0.044 | 0.727 | 0.807 | 0.469 |
| 3 | 2 | 2,479 | 458 | 0.074 | 0.771 | 0.812 | 0.473 |
| 3 | 5 | 1,578 | 293 | 0.064 | 0.756 | 0.819 | 0.473 |
| 3 | 10 | 928 | 184 | 0.055 | 0.748 | 0.815 | 0.472 |
| 3 | 20 | 386 | 79 | 0.048 | 0.723 | 0.801 | 0.471 |
| 5 | 2 | 2,639 | 484 | 0.075 | 0.760 | 0.805 | 0.474 |
| 5 | 5 | 1,822 | 334 | 0.065 | 0.749 | 0.808 | 0.473 |
| 5 | 10 | 1,144 | 215 | 0.058 | 0.735 | 0.799 | 0.473 |
| 5 | 20 | 581 | 117 | 0.051 | 0.720 | 0.787 | 0.472 |
| 8 | 2 | 2,692 | 491 | 0.075 | 0.750 | 0.796 | 0.474 |
| 8 | 5 | 1,952 | 358 | 0.066 | 0.739 | 0.796 | 0.474 |
| 8 | 10 | 1,275 | 227 | 0.060 | 0.728 | 0.784 | 0.473 |
| 8 | 20 | 718 | 141 | 0.053 | 0.715 | 0.774 | 0.472 |

## Adversarial review

Clustered component coverage ranges from 77.4% to
82.4% across the pre-specified grid, well below the 95% diagnostic
reference. Coverage generally falls as the history window and minimum match count increase, even
while mean absolute error falls with exposure. Narrower sampling intervals are not absorbing
season-to-season process variation.

At the five-year/five-match reference, ATP mean component error is
0.060 and WTA error is
0.075. The component breakdown is:

| Component | Mean error | Conditional coverage | Clustered coverage |
|---|---:|---:|---:|
| `deuce_wide` | 0.067 | 0.790 | 0.829 |
| `deuce_middle` | 0.056 | 0.682 | 0.786 |
| `deuce_t` | 0.068 | 0.766 | 0.805 |
| `ad_wide` | 0.072 | 0.780 | 0.828 |
| `ad_middle` | 0.055 | 0.698 | 0.788 |
| `ad_t` | 0.071 | 0.777 | 0.808 |

No component reaches adequate diagnostic coverage. Match clustering improves coverage over the
conditional count model but does not close the gap. Both court sides are present in essentially
every record with observed direction, and the median smaller-side event share is near 47%, so
court-side availability does not explain the temporal miss.

**STATISTICAL DECISION:** retain first-serve direction as an internal descriptive measurement, but
reject the current conditional or match-cluster-only interval as a player-stability model. Do not
expand the shrinkage grid yet. The next model must estimate temporal/process variation on
validation seasons and demonstrate later-season calibration without player output.

## Interpretation boundary

Conditional and clustered coverage are empirical diagnostics, not calibrated interval guarantees.
They average correlated direction components and repeated player histories. Requiring two test
matches conditions the evaluation cohort on later participation, while the latest partial season
is excluded completely.

**OPEN QUESTION:** window, exposure, tour, surface, component, and period consistency must be
reviewed together. No favorable aggregate row selects a reporting period or eligibility rule.

No player identity or estimate is serialized. Expanded shrinkage-prior analysis remains blocked
until this raw-measurement result is reviewed.

## Reproduce

```powershell
python -m research.experiments.first_serve_direction_robustness
```
