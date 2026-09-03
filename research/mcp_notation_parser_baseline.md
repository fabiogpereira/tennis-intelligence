# MCP notation parser baseline

**Snapshot:** `mcp-atp-wta-2026-09-03-2c59eef1`

**Parser:** `mcp-parser-v0.2-draft`

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

## Field-aware component states

| Cell | Component | Observed | Unknown | Absent | Partial | Invalid | N/A |
|---|---|---:|---:|---:|---:|---:|---:|
| 1st | serve direction | 1,829,626 | 1,996 | 0 | 0 | 1,871 | 16,501 |
| 1st | serve and volley | 111,096 | 0 | 1,720,526 | 0 | 1,871 | 16,501 |
| 1st | rally | 824,610 | 0 | 0 | 161,309 | 2,217 | 861,858 |
| 1st | outcome | 1,669,882 | 0 | 85 | 0 | 163,526 | 16,501 |
| 2nd | serve direction | 692,523 | 303 | 0 | 0 | 285 | 1 |
| 2nd | serve and volley | 37,051 | 0 | 655,775 | 0 | 285 | 1 |
| 2nd | rally | 516,128 | 0 | 2 | 96,578 | 400 | 80,004 |
| 2nd | outcome | 596,076 | 0 | 57 | 0 | 96,978 | 1 |

A cell with any issue remains rejected as a whole. The v0.2 component states retain only fields
decoded before the issue; they do not reinterpret or normalize the unsupported suffix.

## Attribute coverage among currently parsed cells

| Attribute | Observed | Parsed denominator | Coverage |
|---|---:|---:|---:|
| Known serve direction | 2,522,149 | 2,524,448 | 99.9% |
| Known shot direction | 5,732,155 | 5,862,279 | 97.8% |
| Known return direction | 1,545,907 | 1,598,625 | 96.7% |
| Known return depth | 1,177,458 | 1,598,625 | 73.7% |

These are field-level diagnostic rates over safely decoded prefixes. Each feature still needs its
own eligibility and denominator audit.

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
65.8% for Bianca Andreescu (185 matches) to
99.8% for Andre Agassi (215 matches). Consequently,
parser-derived player or era comparisons would currently mix tennis behavior with notation-version
and charting-practice effects.

## Serve-direction extraction despite whole-cell rejection

| Match era | All notation cells | Extractable direction | Known direction | Known / extractable |
|---|---:|---:|---:|---:|
| through 2009 | 602,567 | 589,345 | 588,536 | 99.9% |
| 2010-2018 | 523,820 | 521,556 | 521,066 | 99.9% |
| 2019 | 211,785 | 211,252 | 211,094 | 99.9% |
| 2020-2023 | 641,811 | 640,413 | 639,885 | 99.9% |
| 2024-2026 | 560,919 | 559,679 | 559,365 | 99.9% |

**ESTABLISHED FOR THIS PARSER AND SNAPSHOT:** safely extracting the serve prefix removes most of the
era variation affecting whole-cell parsing. Among the twenty most-charted players, known direction
coverage within extractable serve prefixes ranges from 99.6% for
Caroline Wozniacki (155 matches) to
100.0% for Casper Ruud
(170 matches). This is necessary but not sufficient for feature
approval; court-side, serve-number, and aggregate agreement remain separate gates.

## Coverage by chart author

| Chart author | Cells | Whole-cell success | Extractable serve directions | Known / extractable |
|---|---:|---:|---:|---:|
| `Edo` | 453,519 | 99.7% | 445,301 | 99.9% |
| `Zindaras` | 426,345 | 61.0% | 425,327 | 99.9% |
| `BG` | 278,935 | 99.8% | 275,635 | 100.0% |
| `Isaac` | 256,408 | 92.7% | 255,416 | 99.9% |
| `Ludo` | 152,931 | 99.9% | 152,855 | 100.0% |
| `Carrie` | 150,922 | 62.3% | 150,613 | 100.0% |
| `Lowell` | 117,568 | 99.9% | 117,482 | 99.9% |
| `chsv` | 101,784 | 99.7% | 100,369 | 99.7% |
| `KleineBiere` | 54,984 | 100.0% | 54,941 | 99.9% |
| `tsitsi` | 44,252 | 99.9% | 44,114 | 100.0% |
| `Edged` | 40,971 | 99.7% | 40,924 | 100.0% |
| `1HandBH` | 36,102 | 100.0% | 35,959 | 99.6% |
| `Amy` | 35,316 | 98.4% | 35,163 | 99.9% |
| `Palaver` | 34,755 | 100.0% | 34,505 | 99.7% |
| `ChapelHeel66` | 28,307 | 99.5% | 28,229 | 99.9% |
| `stard54` | 27,115 | 98.1% | 26,866 | 100.0% |
| `ojustino` | 26,230 | 97.1% | 25,905 | 99.8% |
| `MaGav` | 25,517 | 99.6% | 25,430 | 100.0% |
| `Angel Moreno` | 25,463 | 99.8% | 25,433 | 100.0% |
| `Salvo` | 24,377 | 100.0% | 24,316 | 99.9% |

The table shows the twenty authors with the most notation cells; all authors remain in the
machine-readable profile. Author differences describe data-production patterns and must not be
interpreted as player behavior.

## Gate decision

**PROCEED WITH A SERVE-ONLY STABILITY PILOT:** field-aware serve prefixes have strong aggregate
agreement and explicit missingness. No player feature is approved for publication. Continue parser
revision for return/rally/net families and investigate serve exceptions, context dependence, and
split-sample persistence before constructing Tennis DNA profiles.
