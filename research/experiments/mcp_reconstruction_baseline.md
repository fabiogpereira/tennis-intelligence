# MCP reconstruction baseline

**Status:** Engineering validation, not statistical validation.

## Snapshot
- Source: `charting-w-points-to-2009.csv`
- Retrieved: 2026-09-03
- Point rows: 57,913
- Unique matches: 391
- Duplicate `(match_id, Pt)` groups observed: 260; 250 are exact repeats and 10 have conflicting chart annotations.
- Adapter: `pipelines/processing/mcp.py`

## Result

| Outcome | Matches |
|---|---:|
| Strictly reconstructed to completed match | 311 |
| Strict validation failure | 77 |
| Parsed but incomplete | 3 |

The normalized run collapses exact duplicate rows and excludes the 10 conflicting annotation groups. It still produces 311 completed matches, 3 incomplete matches, and 77 strict-validation failures. Therefore duplicate rows do not explain the broad reconstruction failure rate.

Failure categories:

- Set/game score mismatch: 45
- Point-number gap: 19
- Server mismatch: 9
- Point-score mismatch: 4

The first real match reconstructed successfully through completion. The full sample does not, so the adapter is not yet ready to claim broad MCP compatibility.

The duplicate-key count is an additional source-quality warning. Field-level comparison found that the 250 exact-repeat groups can be safely collapsed for state-level analysis. The 10 conflicting groups affect only `1st`, `2nd`, and/or `Notes`, while score, server, and point-winner fields agree. They remain flagged and are excluded from shot-level analyses until their provenance is understood.

## Interpretation

**ENGINEERING FINDING:** The source contains enough information for deterministic reconstruction on a substantial subset, but source conventions, gaps, incomplete records, or exceptional match handling require investigation. Strict rejection is currently preferable to silently repairing rows.

This result says nothing about the validity of a pressure metric. It is only a software/data contract check.

## Next checks

1. Inspect representative failures by category and match format.
2. Identify whether the 10 annotation conflicts are revised or segmented observations.
3. Compare MCP-derived score fields with the raw `1st`/`2nd` charting codes where needed.
4. Identify whether rows are duplicated, segmented, or intentionally omitted.
5. Add exact-duplicate normalization for state-level analysis, with provenance counts.
6. Add explicit handling only for documented source conventions.
7. Add a fixture for each accepted exception and retain rejection tests for ambiguous cases.
