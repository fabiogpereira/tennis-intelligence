# MCP notation parser baseline

**Snapshot:** `mcp-atp-wta-2026-09-03-2c59eef1`

**Parser:** `mcp-parser-v0.1-draft`

**Status:** draft engineering result; no behavioral feature is approved

## Parse result

| Cell | Non-empty cells | Parsed | Rejected | Success |
|---|---:|---:|---:|---:|
| First serve | 1,849,994 | 1,682,148 | 167,846 | 90.9% |
| Second serve | 693,112 | 595,020 | 98,092 | 85.8% |

## Rejection classes

| Rejection | Cells |
|---|---:|
| `1st:expected_shot_type` | 161,651 |
| `2nd:expected_shot_type` | 96,691 |
| `1st:trailing_after_serve_fault` | 3,448 |
| `1st:expected_serve_direction` | 1,871 |
| `1st:trailing_after_rally_outcome` | 786 |
| `2nd:trailing_after_serve_fault` | 622 |
| `2nd:trailing_after_rally_outcome` | 437 |
| `2nd:expected_serve_direction` | 285 |
| `1st:missing_point_ending` | 85 |
| `2nd:missing_point_ending` | 55 |
| `1st:duplicate_modifier` | 4 |
| `2nd:duplicate_modifier` | 2 |
| `1st:trailing_after_serve_outcome` | 1 |

The largest class is a valid serve/shot prefix followed by a token that the simplified official
grammar does not permit at that position. Depth-like codes on non-return shots account for much of
this class. These forms remain rejected until their semantics are documented and tested.

## Attribute coverage among currently parsed cells

| Attribute | Observed | Parsed denominator | Coverage |
|---|---:|---:|---:|
| Known serve direction | 2,258,581 | 2,260,666 | 99.9% |
| Known shot direction | 5,221,335 | 5,335,724 | 97.9% |
| Known return direction | 1,297,842 | 1,339,375 | 96.9% |
| Known return depth | 931,906 | 1,339,375 | 69.6% |

These conditional rates are diagnostic only. They may be biased upward because rejected complex
cells are excluded from the denominator.

## Coverage shift by match era

| Match era | Cells | Parsed | Success |
|---|---:|---:|---:|
| through 2009 | 602,567 | 598,258 | 99.3% |
| 2010-2018 | 523,820 | 502,448 | 95.9% |
| 2019 | 211,785 | 188,498 | 89.0% |
| 2020-2023 | 641,811 | 501,307 | 78.1% |
| 2024-2026 | 560,919 | 485,352 | 86.5% |

**ESTABLISHED FOR THIS PARSER AND SNAPSHOT:** acceptance varies materially by match era. It is not
missing completely at random. Among the twenty most-charted players, acceptance ranges from
64.2% for Hubert Hurkacz (320 matches) to
99.7% for Andre Agassi (215 matches). Consequently,
parser-derived player or era comparisons would currently mix tennis behavior with notation-version
and charting-practice effects.

## Gate decision

**PROCEED WITH PARSER REVISION; STOP FEATURE GENERATION:** the parser handles the documented core and
official examples, but corpus acceptance is not high or exchangeable enough for player features.
Review observed grammar extensions, add versioned rules only when supported, and compare match totals
against MCP aggregates before generating Tennis DNA candidates.
