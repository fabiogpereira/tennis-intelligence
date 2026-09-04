# Context-controlled serve stability pilot

**Experiment:** `research-context-serve-stability-v0.1`

**Status:** internal falsification result; no player ranking or profile is produced

## Data boundary

- 23,180 source match-player serve records were considered.
- 22,672 had a collision-free safe match link before
  the player-ID check.
- 11 records from
  2 normalized player identities were excluded because
  they map to multiple context IDs.
- 22,661 match-player records across
  11,336 matches enter the experiment.
- Player rank is known for 22,546 eligible records; opponent rank is known
  for 22,541.

MCP supplies surface, tournament, round, and chart author. The context archive supplies only
match-specific ranks and namespaced IDs here. Missing rank remains explicit. All rejected join
classes remain excluded.

## Results

| Family | Context | Matches / half | Player-strata | Players | Within | Bootstrap range | Between | Ratio |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `first_serve_direction` | `surface` | 2 | 1,076 | 609 | 0.102 | 0.119-0.127 | 0.153 | 0.666 |
| `first_serve_direction` | `surface` | 5 | 516 | 329 | 0.075 | 0.089-0.097 | 0.130 | 0.574 |
| `first_serve_direction` | `era` | 2 | 912 | 666 | 0.097 | 0.114-0.122 | 0.157 | 0.615 |
| `first_serve_direction` | `era` | 5 | 511 | 390 | 0.072 | 0.087-0.094 | 0.137 | 0.530 |
| `first_serve_direction` | `player_rank_band` | 2 | 1,224 | 576 | 0.103 | 0.122-0.129 | 0.156 | 0.661 |
| `first_serve_direction` | `player_rank_band` | 5 | 509 | 291 | 0.074 | 0.091-0.100 | 0.131 | 0.569 |
| `first_serve_direction` | `opponent_rank_band` | 2 | 1,331 | 473 | 0.107 | 0.127-0.133 | 0.151 | 0.709 |
| `first_serve_direction` | `opponent_rank_band` | 5 | 534 | 217 | 0.079 | 0.095-0.103 | 0.128 | 0.616 |
| `first_serve_direction` | `tournament` | 2 | 1,319 | 279 | 0.113 | 0.133-0.140 | 0.157 | 0.717 |
| `first_serve_direction` | `tournament` | 5 | 269 | 69 | 0.076 | 0.094-0.106 | 0.122 | 0.622 |
| `first_serve_direction` | `chart_author` | 2 | 1,245 | 467 | 0.107 | 0.121-0.130 | 0.157 | 0.684 |
| `first_serve_direction` | `chart_author` | 5 | 461 | 234 | 0.077 | 0.090-0.100 | 0.131 | 0.589 |
| `first_serve_direction` | `joint_basic_context` | 2 | 1,413 | 350 | 0.110 | 0.130-0.138 | 0.152 | 0.726 |
| `first_serve_direction` | `joint_basic_context` | 5 | 372 | 123 | 0.077 | 0.092-0.100 | 0.115 | 0.669 |
| `second_serve_direction` | `surface` | 2 | 1,076 | 609 | 0.155 | 0.182-0.194 | 0.228 | 0.681 |
| `second_serve_direction` | `surface` | 5 | 516 | 329 | 0.126 | 0.143-0.154 | 0.193 | 0.653 |
| `second_serve_direction` | `era` | 2 | 912 | 666 | 0.146 | 0.169-0.181 | 0.221 | 0.659 |
| `second_serve_direction` | `era` | 5 | 511 | 390 | 0.120 | 0.138-0.150 | 0.195 | 0.618 |
| `second_serve_direction` | `player_rank_band` | 2 | 1,224 | 576 | 0.158 | 0.189-0.197 | 0.233 | 0.677 |
| `second_serve_direction` | `player_rank_band` | 5 | 509 | 291 | 0.126 | 0.146-0.159 | 0.197 | 0.641 |
| `second_serve_direction` | `opponent_rank_band` | 2 | 1,331 | 473 | 0.162 | 0.195-0.207 | 0.228 | 0.709 |
| `second_serve_direction` | `opponent_rank_band` | 5 | 534 | 217 | 0.132 | 0.152-0.163 | 0.194 | 0.682 |
| `second_serve_direction` | `tournament` | 2 | 1,319 | 279 | 0.185 | 0.215-0.227 | 0.251 | 0.740 |
| `second_serve_direction` | `tournament` | 5 | 269 | 69 | 0.132 | 0.157-0.179 | 0.211 | 0.626 |
| `second_serve_direction` | `chart_author` | 2 | 1,245 | 467 | 0.155 | 0.183-0.193 | 0.229 | 0.676 |
| `second_serve_direction` | `chart_author` | 5 | 461 | 234 | 0.122 | 0.143-0.157 | 0.201 | 0.605 |
| `second_serve_direction` | `joint_basic_context` | 2 | 1,413 | 350 | 0.174 | 0.208-0.220 | 0.243 | 0.717 |
| `second_serve_direction` | `joint_basic_context` | 5 | 372 | 123 | 0.130 | 0.153-0.171 | 0.208 | 0.625 |
| `serve_outcomes` | `surface` | 2 | 1,076 | 609 | 0.029 | 0.035-0.037 | 0.046 | 0.641 |
| `serve_outcomes` | `surface` | 5 | 516 | 329 | 0.023 | 0.026-0.029 | 0.042 | 0.554 |
| `serve_outcomes` | `era` | 2 | 912 | 666 | 0.028 | 0.033-0.035 | 0.045 | 0.623 |
| `serve_outcomes` | `era` | 5 | 511 | 390 | 0.020 | 0.025-0.027 | 0.041 | 0.495 |
| `serve_outcomes` | `player_rank_band` | 2 | 1,224 | 576 | 0.031 | 0.037-0.039 | 0.048 | 0.640 |
| `serve_outcomes` | `player_rank_band` | 5 | 509 | 291 | 0.023 | 0.027-0.030 | 0.042 | 0.547 |
| `serve_outcomes` | `opponent_rank_band` | 2 | 1,331 | 473 | 0.031 | 0.038-0.040 | 0.048 | 0.661 |
| `serve_outcomes` | `opponent_rank_band` | 5 | 534 | 217 | 0.024 | 0.028-0.031 | 0.042 | 0.569 |
| `serve_outcomes` | `tournament` | 2 | 1,319 | 279 | 0.034 | 0.041-0.043 | 0.049 | 0.704 |
| `serve_outcomes` | `tournament` | 5 | 269 | 69 | 0.024 | 0.029-0.032 | 0.042 | 0.574 |
| `serve_outcomes` | `chart_author` | 2 | 1,245 | 467 | 0.032 | 0.038-0.041 | 0.048 | 0.659 |
| `serve_outcomes` | `chart_author` | 5 | 461 | 234 | 0.023 | 0.027-0.031 | 0.043 | 0.538 |
| `serve_outcomes` | `joint_basic_context` | 2 | 1,413 | 350 | 0.034 | 0.041-0.043 | 0.049 | 0.696 |
| `serve_outcomes` | `joint_basic_context` | 5 | 372 | 123 | 0.024 | 0.029-0.032 | 0.040 | 0.599 |

Ratios below one favor same-player repeatability within a context stratum; ratios at or above one
fail that check. Sparse or missing ratios are negative coverage evidence, not omitted successes.
Player-strata can exceed distinct players because one player may contribute to several contexts.

## Falsification summary

All 42 aggregate evaluations produced a ratio below one; 0
failed or lacked the aggregate ratio check. Across the 84 ATP/WTA cells,
0 failed or lacked that check. In 0 aggregate evaluations, the
upper endpoint of the within-player bootstrap range reached the between-player median.

Observed aggregate ratio ranges:

- `first_serve_direction`: 0.530-0.726.
- `second_serve_direction`: 0.605-0.740.
- `serve_outcomes`: 0.495-0.704.

Coverage still narrows materially under stronger controls. At five matches per half, exact
tournament strata retain only 69 distinct players and joint surface/era/opponent-rank strata retain
123. The four largest chart authors account for 52.9% of eligible match-player
records. These are selection and precision warnings even though the ratios remain below one.

**PROJECT HYPOTHESIS:** the three serve families retain aggregate repeatability under these simple
observed-context checks. `second_serve_direction` remains the weakest family because it has the
largest within-player distances, the weakest prior reconciliation, and the highest controlled
ratios in several cells.

**DATA-QUALITY DECISION:** retain all three families for shrinkage and player-level uncertainty
experiments. This is not approval for a feature vector. Tournament-specific and joint-context
results at five matches per half are exploratory because their player coverage is narrow.

## Interpretation boundary

This is one-factor stratification plus a pre-specified joint basic context, not a causal adjustment
model. It cannot remove selection into charted matches, unmeasured opponent style, score state,
match format, or dependence across repeated player-strata. The bootstrap range resamples matches
within halves and is a diagnostic range, not a confidence interval.

No predictive model is fitted, so calibration and discrimination are not applicable. Rankings are
treated as source-reported match context; their historical timing semantics were not independently
validated and remain a possible measurement limitation.

**OPEN QUESTION:** whether retained families justify shrinkage and player-level uncertainty work.
No individual player estimate is emitted, and no ratio alone approves a Tennis DNA feature.

## Reproduce

```powershell
python -m research.experiments.context_serve_stability
```
