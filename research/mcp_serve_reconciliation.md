# MCP serve reconciliation

**Snapshot:** `mcp-atp-wta-2026-09-03-2c59eef1`

**Parser:** `mcp-parser-v0.2-draft`

**Status:** raw-notation validation evidence; no player feature is approved by this report alone

## Question

Do independently parsed raw serve records reproduce the match-player totals published in MCP
`Overview` and `ServeDirection` aggregates?

## Source-grain integrity

| Source | Raw grain groups | Safe groups | Duplicate groups | Conflicting groups | Invalid rows |
|---|---:|---:|---:|---:|---:|
| Overview `Total` | 23,230 | 23,219 | 26 | 11 | 0 |
| ServeDirection `1`/`2`/`Total` | 69,695 | 69,664 | 78 | 31 | 0 |

Exact duplicate aggregate rows are collapsed. Conflicting grain groups are excluded rather than
selected. Raw notation uses the same point-key policy as the complete snapshot profile.

## Overview agreement

| Metric | Comparable match-player records | Exact | Exact rate | Mean absolute difference |
|---|---:|---:|---:|---:|
| `serve_pts` | 23,159 | 23,138 | 99.9% | 0.007 |
| `aces` | 21,950 | 21,938 | 99.9% | 0.001 |
| `dfs` | 21,950 | 21,946 | 100.0% | 0.000 |
| `first_in` | 22,116 | 22,099 | 99.9% | 0.004 |
| `second_in` | 22,103 | 22,087 | 99.9% | 0.003 |

The source column `second_in` is retained by name for reconciliation. In inspected MCP aggregates it
behaves as a second-serve-attempt count, including double faults; this empirical interpretation is
not silently renamed into a product feature.

## ServeDirection agreement

| Aggregate row | Comparable | Exact wide/body/T | Marginal exact rate | Exact deuce/ad vector | Side-aware exact rate |
|---|---:|---:|---:|---:|---:|
| `1` | 22,528 | 22,300 | 99.0% | 22,210 | 98.6% |
| `2` | 22,763 | 22,084 | 97.0% | 22,045 | 96.8% |
| `Total` | 22,183 | 21,348 | 96.2% | 21,238 | 95.7% |

A direction record is comparable only when every contributing raw serve has a known court side,
serve number, and direction. Marginal agreement compares wide/body/T after summing over court side;
side-aware agreement requires all six deuce/ad by wide/body/T cells to agree. This separation tests
whether discrepancies arise in notation direction or in court-side reconstruction.

## Mismatch context

| Comparison | Mismatches | ATP rate | WTA rate | Largest author count (rate) | Largest season count (rate) |
|---|---:|---:|---:|---|---|
| Overview `serve_pts` | 21 | 0.11% | 0.06% | `Edo`: 13 (0.36%) | `1993`: 2 (1.20%) |
| Overview `aces` | 12 | 0.08% | 0.01% | `BG`: 5 (0.25%) | `2013`: 2 (0.55%) |
| Overview `dfs` | 4 | 0.02% | 0.01% | `Amy`: 2 (0.56%) | `2013`: 2 (0.55%) |
| Overview `first_in` | 17 | 0.08% | 0.06% | `Edo`: 8 (0.24%) | `2015`: 4 (0.39%) |
| Overview `second_in` | 16 | 0.08% | 0.06% | `Edo`: 8 (0.24%) | `2015`: 4 (0.39%) |
| ServeDirection `1` | 318 | 1.69% | 0.90% | `Zindaras`: 112 (3.18%) | `2022`: 47 (2.38%) |
| ServeDirection `2` | 718 | 3.70% | 2.13% | `Edo`: 293 (8.20%) | `2025`: 57 (2.54%) |
| ServeDirection `Total` | 945 | 5.02% | 2.83% | `Edo`: 298 (8.44%) | `2025`: 85 (3.84%) |

Counts identify where mismatches accumulate; parenthetical values are stratum-specific rates using
only comparable records as denominators. The full, case-preserving author and season breakdown is
stored as record lists in the machine-readable profile. Concentration is a data-production warning,
not evidence that a contributor caused the discrepancy.

## Interpretation boundary

Agreement shows software consistency with MCP's convenience aggregates; it does not independently
validate the source charting, remove sample-selection bias, or prove temporal player-style stability.
Mismatch examples, context denominators, and metric-specific missingness remain available in the
machine-readable profile.

## Reproduce

```powershell
python -m research.experiments.profile_mcp_snapshot
```
