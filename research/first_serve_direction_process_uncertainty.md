# First-serve direction process uncertainty

**Experiment:** `research-first-serve-direction-process-uncertainty-v0.1`

**Status:** temporal calibration falsification; no player output

## Design boundary

Validation seasons estimate an additional process variance separately by tour and direction
component. Each test season is untouched by that estimate. The grid retains 2/3/5/8-year histories
and 2/5/10/20 historical-match thresholds, with at least two validation or test matches for a
clustered seasonal share. The latest partial season is excluded.

## Results

| Window | History matches | Periods | Players | Base coverage | Process coverage | Base radius | Process radius | Process SD |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 2 | 2,244 | 417 | 0.815 | 0.956 | 0.143 | 0.216 | 0.073 |
| 2 | 5 | 1,308 | 267 | 0.824 | 0.961 | 0.118 | 0.183 | 0.061 |
| 2 | 10 | 666 | 154 | 0.822 | 0.958 | 0.098 | 0.154 | 0.049 |
| 2 | 20 | 227 | 57 | 0.805 | 0.950 | 0.080 | 0.141 | 0.054 |
| 3 | 2 | 2,477 | 458 | 0.812 | 0.957 | 0.142 | 0.218 | 0.074 |
| 3 | 5 | 1,575 | 293 | 0.819 | 0.955 | 0.119 | 0.182 | 0.061 |
| 3 | 10 | 921 | 184 | 0.815 | 0.963 | 0.101 | 0.167 | 0.059 |
| 3 | 20 | 384 | 79 | 0.800 | 0.955 | 0.085 | 0.147 | 0.052 |
| 5 | 2 | 2,636 | 484 | 0.805 | 0.958 | 0.140 | 0.221 | 0.076 |
| 5 | 5 | 1,818 | 333 | 0.807 | 0.956 | 0.120 | 0.188 | 0.065 |
| 5 | 10 | 1,141 | 215 | 0.799 | 0.962 | 0.104 | 0.172 | 0.064 |
| 5 | 20 | 577 | 116 | 0.787 | 0.959 | 0.088 | 0.152 | 0.056 |
| 8 | 2 | 2,689 | 491 | 0.796 | 0.958 | 0.138 | 0.222 | 0.075 |
| 8 | 5 | 1,949 | 357 | 0.795 | 0.959 | 0.120 | 0.194 | 0.067 |
| 8 | 10 | 1,271 | 227 | 0.784 | 0.958 | 0.105 | 0.176 | 0.065 |
| 8 | 20 | 712 | 139 | 0.774 | 0.958 | 0.090 | 0.162 | 0.061 |

Base and process radii compare two noisy seasonal shares and include both history and test sampling
variance. A future displayed interval would not know test sampling variance and is not authorized
by this result.

## Adversarial review

Base clustered coverage ranges from 77.4% to 82.4%. Adding
validation-estimated process variance raises aggregate test coverage to
95.0%-96.3%, but mean radii become
1.52-1.79 times the base radii. Calibration is recovered at
a material precision cost.

Fallback use ranges from 31.4% to 100.0% across the grid
and is highest for strict exposure thresholds in older sparse folds. Recent well-populated folds
more often support tour-component estimates, but this does not repair historical or grass
coverage. Small WTA high-exposure and grass cells remain the clearest adverse cases.

At the five-year/five-match reference, component results are:

| Component | Base coverage | Process coverage | Base radius | Process radius |
|---|---:|---:|---:|---:|
| `deuce_wide` | 0.829 | 0.956 | 0.127 | 0.188 |
| `deuce_middle` | 0.785 | 0.965 | 0.101 | 0.174 |
| `deuce_t` | 0.805 | 0.960 | 0.128 | 0.196 |
| `ad_wide` | 0.828 | 0.947 | 0.136 | 0.206 |
| `ad_middle` | 0.788 | 0.958 | 0.098 | 0.165 |
| `ad_t` | 0.808 | 0.953 | 0.130 | 0.198 |

**STATISTICAL DECISION:** retain validation-estimated process variance as an internal uncertainty
candidate because it meets the aggregate test-coverage criterion across the grid. Do not approve
it for publication: interval width, fallback dependence, sparse surface/tour cells, and the
difference between evaluation and future display intervals remain unresolved.

## Interpretation boundary

**OPEN QUESTION:** acceptable calibration requires coverage, width, fallback frequency, tour,
surface, component, and period consistency to agree. Validation-targeted process variance can
overcover or fail under drift; neither outcome proves a stable player trait.

No player identity, estimate, or interval is serialized. No window, threshold, or publication
policy is approved automatically.

## Reproduce

```powershell
python -m research.experiments.first_serve_direction_process_uncertainty
```
