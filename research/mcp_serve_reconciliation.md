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

## Interpretation boundary

Agreement shows software consistency with MCP's convenience aggregates; it does not independently
validate the source charting, remove sample-selection bias, or prove temporal player-style stability.
Mismatch examples and metric-specific missingness remain available in the machine-readable profile.

## Reproduce

```powershell
python -m research.experiments.profile_mcp_snapshot
```
