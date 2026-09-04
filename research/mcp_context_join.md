# MCP to Sackmann context join audit

**Experiment:** `research-mcp-context-join-v0.1`

**Behavior snapshot:** `mcp-atp-wta-2026-09-03-2c59eef1`

**Context snapshot:** `sackmann-archive-2026-06-25-8373358`

**Status:** automated precision-first join audit; safe-link precision was reviewed separately

## Source decision

The original `JeffSackmann/tennis_atp` and `tennis_wta` repositories returned `Repository not
found` on 2026-09-03. This audit therefore uses the already identified
`Aneeshers/tennis-sackmann-archive` mirror pinned at commit
`83733587353df8a41f2fd4f516147d5aa83f5a8d`. The mirror preserves the upstream READMEs and states that its
ATP/WTA snapshots came from June 2026, but does not provide their exact upstream commit hashes.

**ENGINEERING DECISION:** the mirror is acceptable for a feasibility audit, not silently equivalent
to the unavailable upstream. Its provenance gap and CC BY-NC-SA 4.0 license remain product blockers.

## Context source profile

- 262 ATP/WTA singles files and
  1,749,872 raw match rows were read.
- 1,737,809 canonical match keys were structurally safe.
- 0 rows lacked a required identity/date value;
  60 canonical keys conflicted and were excluded.
- Raw context files remain under `data/raw/` and are not committed.

## Resolution contract

`research-mcp-context-join-v0.1` requires the same tour, an exact unordered pair after conservative
case/diacritic/separator normalization, and a tournament-date window of -7/+20 days. A unique
candidate also needs either exact normalized tournament or joint round/surface/best-of agreement.
Multiple candidates are accepted only when exact normalized tournament and round produce one
candidate. Fuzzy names and hand-authored aliases are not used.

Canonical IDs are namespaced as `sackmann:<tour>:<player_id>` and
`sackmann:<tour>:<file-family>:<tourney_id>:<match_num>`. The file-family segment prevents
main-draw, qualifying/challenger, and futures keys from being treated as the same namespace. MCP
source IDs remain preserved separately.

## Join result

| Status | Matches |
|---|---:|
| Safely matched | 11,336 |
| Exact normalized pair absent | 60 |
| Exact pair outside date window | 61 |
| Pair/date found but supporting context conflicts | 77 |
| Ambiguous candidates | 48 |
| Canonical target collision | 8 |

Overall safe match rate: **97.8%**.

| Tour | MCP matches | Safely matched | Rate |
|---|---:|---:|---:|
| ATP | 7,530 | 7,365 | 97.8% |
| WTA | 4,060 | 3,971 | 97.8% |

## Independent agreement checks among matched records

| Field | Comparable | Agrees | Agreement |
|---|---:|---:|---:|
| `surface` | 11,336 | 11,056 | 97.5% |
| `round` | 11,336 | 11,291 | 99.6% |
| `tournament` | 11,336 | 10,600 | 93.5% |
| `best_of` | 11,336 | 11,287 | 99.6% |

These fields do not participate in the unique-pair rule, except tournament and round when multiple
candidates remain. Agreement therefore helps detect false joins and source-definition differences;
it is not independent proof of identity.

Ranking is present for 22,552 of
22,672 safely matched player-match sides
(99.5%).

## Date-window sensitivity

| Window before / after tournament date | Matched before collision check | Ambiguous | Pair absent | Outside window | Context conflict |
|---|---:|---:|---:|---:|---:|
| -1 / +14 days | 11,218 | 29 | 60 | 206 | 77 |
| -7 / +20 days | 11,344 | 48 | 60 | 61 | 77 |
| -14 / +28 days | 11,325 | 80 | 60 | 51 | 74 |

The selected window follows the upstream documentation that `tourney_date` is usually the Monday at
or near the start of an event, while MCP records the match date. No window is interpreted as a
validated threshold until the deterministic review sample is checked by a human.

## Automated identity prescreen

**OPEN QUESTION:** `martin landaluce` maps to source player IDs `211776` and `126205`. ID `126205`
appears on one 2022 Gijon record while `211776` is used by the later records inspected. This may be
a source correction or reassignment, but the audit does not merge the IDs.

**OPEN QUESTION:** `tiantsoa sarah rakotomanga rajaonah` maps to source player IDs `239456` and
`266531`; the latter appears at W50+H Macon in 2025 in the inspected records. This source
inconsistency is retained for human review rather than converted into an alias.

The canonical-collision examples also include duplicate MCP aliases and contradictory MCP
date/round/tournament metadata. All 8 affected MCP rows,
covering 4 context targets, remain excluded from the safe
matched set. These observations reduce the review search space; they are not human approval.

## Remaining blockers

- Safe-link precision review is complete in `research/mcp_context_join_human_review.md`; 15 exception
  rows without selected side-by-side context remain unreviewed and excluded.
- 2 matched normalized player names
  map to multiple source player IDs and require identity review before a player crosswalk is approved.
- Context coverage varies by season and unresolved names have not been given fuzzy aliases.
- The mirror provenance gap and non-commercial/share-alike license remain explicit.
- Surface, opponent, era, and ranking-controlled stability has not yet been run.

**DATA-QUALITY DECISION:** the separately reviewed safe links may be used for the next internal
sensitivity experiment. Do not publish canonical player profiles or ranking-band claims yet.

## Reproduce

```powershell
powershell -NoProfile -File pipelines/ingestion/fetch_sackmann_context_snapshot.ps1
python -m research.experiments.audit_context_join
```
