# LiveTennisAPI sample baseline

**Status:** Engineering/data-contract validation, not statistical validation.

## Snapshot

- Zenodo record: 22058943, version 1.0.1
- Retrieved: 2026-09-03
- Adapter: `pipelines/processing/livetennis.py`
- Match metadata rows: 173,571
- Player metadata rows: 32,678
- Point-state rows: 951,064
- Matches with point-state rows: 5,380

## Parse result

All 951,064 point-state rows parse successfully through the source adapter.

Observed missingness:

- Missing server: 39,848 states
- Missing point labels: 5,710 states
- Literal 0-0 tape starts: 212 matches

The first observed tape begins with match ID 8568 and empty game arrays, no server, and `0-0` point labels. The final observed row in the file is match ID 16296 with no server. These are valid examples of why the source documentation warns that tapes may start mid-match or end before the final point.

## Important semantics

Each row is a scoreboard state, not a point event. A point outcome must be inferred from the transition between adjacent rows in capture order. This inference is only valid when the two states are consecutive and sufficiently complete. Missing server or point labels can prevent a directional inference even when the score transition is otherwise usable.

`games_p1` and `games_p2` are JSON arrays whose last values represent the current set. The source `is_tiebreak` flag is retained as provided, but the sample contains rows where it is inconsistent with the point label; the adapter preserves the raw value rather than silently correcting it.

## Current decision

Use this sample to build and test a state-transition adapter. Do not claim that all 5,380 tapes provide complete match histories, and do not infer missing outcomes. Keep observed data separate from any reconstructed full corpus later supplied by the provider because their provenance and timestamp semantics differ.

## Next checks

1. Infer outcomes only for adjacent, complete state transitions.
2. Classify transitions as point, game, set, tiebreak, missing, or invalid.
3. Measure complete-transition coverage by match, tour, surface, and format.
4. Compare a validated subset against the existing scoring engine.
5. Request full research access only after the public sample contract is understood.
