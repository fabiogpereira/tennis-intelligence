# Serve split-sample stability pilot

**Experiment:** `research-serve-stability-v0.1`

**Snapshot:** `mcp-atp-wta-2026-09-03-2c59eef1`

**Status:** aggregate falsification evidence; no player ranking or profile is produced

## Question

Are candidate serve descriptions more similar across independent match samples from the same
player than across different players in the same tour?

## Design

- The unit resampled for uncertainty is the match, not the point.
- Chronological halves test temporal persistence; alternating matches test sensitivity to the split.
- The 2/5/10/20 matches-per-half grid is a sensitivity analysis, not an approved eligibility rule.
- Outcome distance is the mean absolute difference across first-serve-in, ace, and double-fault
  rates, each using its field-specific resolved denominator.
- Direction distance is mean total-variation distance for wide/body/T distributions normalized
  separately on deuce and ad courts.
- Between-player negative controls compare the first split of one player with the second split of
  every other player in the same tour.
- The resampled range is the central 95% of a deterministic 100-replicate
  match-level bootstrap distribution of the median within-player distance. Because distances are
  non-negative, this range is not presented as a confidence interval and can be upward-biased. Its
  low replicate count is suitable for this feasibility pilot, not final inference.

## Results

| Family | Split | Matches / half | Players | Within median | Bootstrap resampled 95% range | Between median | Ratio |
|---|---|---:|---:|---:|---:|---:|---:|
| `serve_outcomes` | chronological | 2 | 717 | 0.027 | 0.031-0.034 | 0.044 | 0.620 |
| `serve_outcomes` | chronological | 5 | 444 | 0.021 | 0.025-0.028 | 0.040 | 0.510 |
| `serve_outcomes` | chronological | 10 | 262 | 0.018 | 0.020-0.024 | 0.039 | 0.461 |
| `serve_outcomes` | chronological | 20 | 146 | 0.015 | 0.017-0.021 | 0.039 | 0.389 |
| `serve_outcomes` | alternating | 2 | 717 | 0.022 | 0.027-0.029 | 0.043 | 0.504 |
| `serve_outcomes` | alternating | 5 | 444 | 0.016 | 0.021-0.023 | 0.039 | 0.404 |
| `serve_outcomes` | alternating | 10 | 262 | 0.012 | 0.016-0.018 | 0.038 | 0.306 |
| `serve_outcomes` | alternating | 20 | 146 | 0.009 | 0.012-0.015 | 0.037 | 0.253 |
| `first_serve_direction` | chronological | 2 | 717 | 0.092 | 0.107-0.117 | 0.153 | 0.604 |
| `first_serve_direction` | chronological | 5 | 444 | 0.073 | 0.085-0.094 | 0.134 | 0.542 |
| `first_serve_direction` | chronological | 10 | 262 | 0.060 | 0.069-0.077 | 0.123 | 0.489 |
| `first_serve_direction` | chronological | 20 | 146 | 0.055 | 0.060-0.070 | 0.115 | 0.480 |
| `first_serve_direction` | alternating | 2 | 717 | 0.075 | 0.095-0.104 | 0.149 | 0.500 |
| `first_serve_direction` | alternating | 5 | 444 | 0.057 | 0.072-0.080 | 0.130 | 0.440 |
| `first_serve_direction` | alternating | 10 | 262 | 0.044 | 0.054-0.062 | 0.118 | 0.377 |
| `first_serve_direction` | alternating | 20 | 146 | 0.034 | 0.042-0.050 | 0.110 | 0.309 |
| `second_serve_direction` | chronological | 2 | 717 | 0.139 | 0.164-0.175 | 0.218 | 0.636 |
| `second_serve_direction` | chronological | 5 | 444 | 0.115 | 0.132-0.145 | 0.191 | 0.606 |
| `second_serve_direction` | chronological | 10 | 262 | 0.103 | 0.114-0.128 | 0.178 | 0.578 |
| `second_serve_direction` | chronological | 20 | 146 | 0.092 | 0.100-0.114 | 0.167 | 0.550 |
| `second_serve_direction` | alternating | 2 | 717 | 0.111 | 0.140-0.152 | 0.211 | 0.526 |
| `second_serve_direction` | alternating | 5 | 444 | 0.078 | 0.103-0.114 | 0.182 | 0.428 |
| `second_serve_direction` | alternating | 10 | 262 | 0.060 | 0.081-0.092 | 0.168 | 0.355 |
| `second_serve_direction` | alternating | 20 | 146 | 0.049 | 0.064-0.076 | 0.158 | 0.312 |

Lower within-player distance than between-player distance is necessary, not sufficient, evidence
of persistence. A ratio below one favors player-specific repeatability; overlapping context,
selection, opponent, era, surface, and chart-author effects remain plausible explanations.

## Interpretation boundary

**OPEN QUESTION:** whether any family remains stable after surface, opponent strength, era, and
tournament controls. This snapshot does not yet contain validated canonical joins for those tests.

**ENGINEERING DECISION:** do not combine families, assign weights, rank players, cluster styles, or
publish Tennis DNA profiles from this pilot. Eligibility and shrinkage rules remain unresolved.

## Reproduce

```powershell
python -m research.experiments.serve_stability
```
