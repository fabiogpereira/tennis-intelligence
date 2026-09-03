# MCP failure analysis

**Status:** Engineering/data-quality investigation. This is not statistical validation.

## Scope
The analysis uses the normalized local snapshot `charting-w-points-to-2009.csv`. Exact duplicate rows are collapsed. Conflicting annotation groups are excluded explicitly for state-level analysis and remain unavailable for shot-level analysis.

## Findings

- Duplicate groups: 260
- Exact-repeat groups: 250
- Conflicting annotation groups: 10
- Conflicts affect only `1st`, `2nd`, and/or `Notes`.
- Score, server, and point-winner fields agree within those conflicts.
- After normalization, 311 of 391 matches reconstruct completely.
- 3 matches are incomplete.
- 77 matches still fail strict validation.

Failure categories:

| Category | Count | Interpretation |
|---|---:|---|
| Set/game score mismatch | 45 | The engine and source state diverge before a later point; needs local trace and source-code comparison |
| Point-number gap | 19 | A source segment omits one or more point numbers; outcomes must not be invented |
| Server mismatch | 9 | Source and inferred rotation disagree, possibly after an omitted segment or source convention |
| Point-score mismatch | 4 | At least one source segment begins after an omitted point; the displayed score reflects an unseen prior outcome |
| Incomplete | 3 | The available chart does not represent a finished match |

The normalized run has the same 311/3/77 outcome as the pre-normalization run. Duplicate rows therefore do not explain the broad failure rate.

## Representative observations

- `20090603-W-Roland_Garros-QF-Serena_Williams-Svetlana_Kuznetsova` jumps from point 159 to 211. The next source row begins a new set, so this is an omitted block, not a tiebreak rule issue.
- `20090124-W-Australian_Open-R32-Samantha_Stosur-Elena_Dementieva` begins its available sequence at point 2 with `15-0`; point 1 is not available in the source sequence. The adapter correctly refuses to infer that missing outcome.
- `20090908-W-US_Open-QF-Na_Li-Kim_Clijsters` diverges at a later game boundary even though its metadata is best-of-three with no final-set tiebreak. This requires a row-by-row trace, not a scoring-rule exception.
- The ten conflicting duplicate keys are concentrated in the 2001 US Open final and 1996 Wimbledon final. Their visible state fields agree; only chart annotations differ.

## Current data policy

For state-level experiments, use only matches that pass strict reconstruction after exact deduplication and explicit exclusion of conflicting annotation keys. Keep source match IDs and normalization decisions in the experiment manifest.

For shot-level experiments, exclude all conflicting annotation keys until their provenance is understood. Do not select one annotation by recency or convenience.

Do not repair point gaps, server changes, or score mismatches by interpolation. A repaired state can create artificial leverage and would directly contaminate Research #01.

## Next investigation

1. Add a trace mode that reports the last matching state and first divergence for each failed match.
2. Compare divergence rows against raw `1st`/`2nd` codes and the MCP data dictionary.
3. Determine whether score/game mismatches arise from parser assumptions, omitted segments, or source revisions.
4. Validate completed-match final scores against metadata before accepting the 311-match cohort.
5. Freeze the accepted cohort as a versioned fixture before baseline modeling.
