# Serve publication-readiness audit

**Experiment:** `research-serve-publication-readiness-v0.1`

**Status:** aggregate coverage and uncertainty audit; no player output

## Design boundary

The audit uses 22,661 collision-safe match-player
records from 11,336 matches. It creates trailing five-season histories for
as-of years 1974-2026 without requiring future player
participation. A history is one player-surface-as-of-year instance, so the same player may
contribute in multiple windows.

The final as-of year uses data only through the preceding season. The partial latest season in the
snapshot is excluded from the final history rather than treated as complete.

The stress-test intersection requires at least five matches, two seasons, three opponents, two
tournaments, no match above 50% of eligible events, and effective match count of at least three.
It is not a publication threshold.

## Aggregate results

| Target | Tour | Histories | Players | Median matches | Median effective matches | Stress-test share | Median clustered half-width | Median cluster/conditional SD |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `first_serve_in_rate` | All | 18,257 | 1,627 | 2.0 | 1.9 | 0.225 | 0.044 | 1.052 |
| `first_serve_in_rate` | ATP | 10,901 | 949 | 2.0 | 1.9 | 0.242 | 0.043 | 1.095 |
| `first_serve_in_rate` | WTA | 7,356 | 678 | 2.0 | 1.9 | 0.200 | 0.047 | 0.979 |
| `ace_per_service_point` | All | 18,257 | 1,627 | 2.0 | 1.9 | 0.225 | 0.022 | 1.179 |
| `ace_per_service_point` | ATP | 10,901 | 949 | 2.0 | 1.9 | 0.242 | 0.024 | 1.252 |
| `ace_per_service_point` | WTA | 7,356 | 678 | 2.0 | 1.9 | 0.200 | 0.019 | 1.081 |
| `double_fault_per_second_serve_attempt` | All | 18,257 | 1,627 | 2.0 | 1.9 | 0.225 | 0.040 | 0.954 |
| `double_fault_per_second_serve_attempt` | ATP | 10,901 | 949 | 2.0 | 1.8 | 0.242 | 0.035 | 0.959 |
| `double_fault_per_second_serve_attempt` | WTA | 7,356 | 678 | 2.0 | 1.9 | 0.200 | 0.049 | 0.945 |
| `first_serve_direction` | All | 18,257 | 1,627 | 2.0 | 1.9 | 0.225 | 0.149 | 1.798 |
| `first_serve_direction` | ATP | 10,901 | 949 | 2.0 | 1.8 | 0.242 | 0.133 | 1.775 |
| `first_serve_direction` | WTA | 7,356 | 678 | 2.0 | 1.9 | 0.200 | 0.172 | 1.828 |
| `second_serve_direction` | All | 18,256 | 1,627 | 2.0 | 1.9 | 0.225 | 0.221 | 2.097 |
| `second_serve_direction` | ATP | 10,900 | 949 | 2.0 | 1.8 | 0.242 | 0.213 | 2.196 |
| `second_serve_direction` | WTA | 7,356 | 678 | 2.0 | 1.9 | 0.200 | 0.234 | 1.946 |

The clustered half-width is `1.96` times a match-clustered ratio standard error. The comparison
standard deviation is the zero-strength conditional count-model diagnostic. Neither quantity
captures charted-match selection, parser error, or all forms of temporal and contextual change.

## Uncertainty by exposure

| Target | Minimum matches | Histories | Median clustered half-width | Median cluster/conditional SD |
|---|---:|---:|---:|---:|
| `first_serve_in_rate` | 10 | 2,018 | 0.028 | 1.152 |
| `first_serve_in_rate` | 2 | 10,028 | 0.044 | 1.052 |
| `first_serve_in_rate` | 20 | 857 | 0.021 | 1.164 |
| `first_serve_in_rate` | 5 | 4,339 | 0.036 | 1.134 |
| `ace_per_service_point` | 10 | 2,018 | 0.016 | 1.387 |
| `ace_per_service_point` | 2 | 10,028 | 0.022 | 1.179 |
| `ace_per_service_point` | 20 | 857 | 0.014 | 1.399 |
| `ace_per_service_point` | 5 | 4,339 | 0.019 | 1.321 |
| `double_fault_per_second_serve_attempt` | 10 | 2,018 | 0.025 | 1.052 |
| `double_fault_per_second_serve_attempt` | 2 | 10,028 | 0.040 | 0.954 |
| `double_fault_per_second_serve_attempt` | 20 | 857 | 0.019 | 1.063 |
| `double_fault_per_second_serve_attempt` | 5 | 4,339 | 0.032 | 1.026 |
| `first_serve_direction` | 10 | 2,018 | 0.068 | 1.679 |
| `first_serve_direction` | 2 | 10,028 | 0.149 | 1.798 |
| `first_serve_direction` | 20 | 857 | 0.049 | 1.658 |
| `first_serve_direction` | 5 | 4,339 | 0.096 | 1.728 |
| `second_serve_direction` | 10 | 2,018 | 0.110 | 1.992 |
| `second_serve_direction` | 2 | 10,022 | 0.221 | 2.097 |
| `second_serve_direction` | 20 | 857 | 0.081 | 1.958 |
| `second_serve_direction` | 5 | 4,338 | 0.153 | 2.054 |

These cohorts are nested rather than independent. The two-match cluster estimator is itself noisy;
the higher thresholds show whether the direction of the discrepancy persists with more clusters.

## Adversarial interpretation

The median history contains only two distinct matches and about 1.9 effective matches. The
diagnostic diversity/concentration intersection retains roughly one quarter of history instances,
so broad player availability and defensible coverage cannot both be assumed.

Direction is the clearest warning against point-count uncertainty. Its clustered uncertainty
remains materially larger than the conditional count-model diagnostic even at twenty matches.
Outcome rates show smaller discrepancies, but this does not address selected charting or incomplete
context adjustment. Grass coverage is especially sparse relative to hard-court coverage.

**DATA-QUALITY DECISION:** no public eligibility or confidence policy is supported yet. Continue
internal feature specification, but require match-clustered uncertainty and surface-specific
coverage in any future proposal. Conditional posterior precision must not be displayed as total
confidence.

## Interpretation boundary

**OPEN QUESTION:** surface and as-of-year results remain in the machine-readable artifact and must
be checked for reversals before any policy is proposed. Coverage, statistical precision, and
representativeness are different properties; a narrow conditional interval cannot repair a
selected sample.

No player estimate or identity is serialized. No sensitivity-grid value or stress-test rule is
approved by this audit.

## Reproduce

```powershell
python -m research.experiments.serve_publication_readiness
```
