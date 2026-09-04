# Public datasets and data strategy

## Candidate sources

| Source | Granularity | Strength | Constraint | Phase 1 decision |
|---|---|---|---|---|
| Jeff Sackmann ATP/WTA repositories | Match-level results, rankings, and statistics | Broad historical context, stable public repositories, familiar CSV structure | No shot sequences; licensing and entity/match resolution still require explicit review | Use later as the broader match universe and contextual layer |
| Match Charting Project | Point-level rows with raw shot-by-shot notation plus derived match aggregates | 11,590 safely joined point-bearing matches and 1.85M usable logical points in the pinned snapshot | Non-random sample, uneven player/era coverage, notation must be validated; CC BY-NC-SA 4.0 is non-commercial/share-alike | Primary behavioral source for Research #01, subject to quality gates |
| Sackmann archive mirror | Grand Slam point-by-point files for 2011–2024, plus ATP/WTA match-level archives | Directly downloadable historical point data and preserved upstream provenance | Point-level coverage is Grand Slam-only; CC BY-NC-SA 4.0; mirror is not the original maintainer | Evaluate as a historical expansion, with source attribution and license review |
| Colin Parker Kaggle dataset | Match-level rows containing encoded point sequences for ATP main draw, qualifiers, Challengers, and Futures from 2011–2017 | Potentially broader tour coverage; compact match-row format; CC BY-NC-SA 4.0 | Derived from Jeff Sackmann's `tennis_pointbypoint`; not exhaustive; exact coverage and provenance need verification | Evaluate as a candidate adapter, not yet a canonical source |
| LiveTennisAPI dataset | Full index claims 173,571 completed matches from 2023–2026 and point sequences for 170,527; public sample has 951,064 observed point states | Largest apparent modern coverage, ATP/WTA/Challenger/ITF, stable IDs and a Sackmann crosswalk | Full corpus requires application; public sample is June 2026 observed data; reconstructed and observed provenance differ; no pre-2023 points; CC BY-NC 4.0 and no raw redistribution | Request access and evaluate as a separate recent-era cohort |
| ATP/WTA official statistics | Official match and tournament reporting | Authoritative event metadata | Access, historical completeness, and terms may limit automated use | Consult as validation/reference source |

Canonical entry points: [Jeff Sackmann's public repositories](https://github.com/JeffSackmann), [Sackmann archive mirror](https://github.com/Aneeshers/tennis-sackmann-archive), [Match Charting Project repository](https://github.com/JeffSackmann/tennis_MatchChartingProject), [Colin Parker point-by-point dataset](https://www.kaggle.com/datasets/colinparker/pointbypoint-bo3-tennis-data-2011-2017), [LiveTennisAPI documentation](https://github.com/livetennisapi/livetennisapi-data), [LiveTennisAPI Zenodo record](https://doi.org/10.5281/zenodo.22048731), and [ITF Rules](https://www.itftennis.com/en/about-us/tennis-tech/itf-rules-of-tennis/).

## Source review conclusion

**OPEN QUESTION:** We have not found a large, historical, fully downloadable, shot-level dataset with permissive commercial reuse terms that covers the whole professional game. The available sources are complementary:

- The Sackmann archive and Colin Parker dataset improve historical/tour coverage but retain CC BY-NC-SA 4.0 constraints and inherited provenance questions.
- LiveTennisAPI is the most promising volume increase, but its full dataset is application-only, its public sample is recent and observed-only, and its terms prohibit raw redistribution.
- MCP is large enough to justify Tennis DNA feasibility work but remains selected and cannot establish population representativeness on its own.

**ENGINEERING DECISION:** Use MCP for behavior and keep match-level or scoreboard-state sources separate until their definitions, temporal coverage, licensing, and entity resolution are validated. Do not concatenate sources merely because rows can be parsed.

## Current recommendation

**ENGINEERING DECISION:** Use the pinned Match Charting Project snapshot as the primary Research #01 source, subject to its CC BY-NC-SA 4.0 license and visible attribution. Do not assume it can power a commercial product or unrestricted redistribution. The original Jeff Sackmann `tennis_atp` and `tennis_wta` repositories became unavailable before the context audit. The pinned [`tennis-sackmann-archive`](https://github.com/Aneeshers/tennis-sackmann-archive) mirror is therefore the reproducible feasibility source, with its missing exact upstream commit hashes recorded as a provenance limitation.

## Pivoted data role

**ENGINEERING DECISION:** MCP is now the primary behavioral source for Research #01. Broader ATP/WTA match datasets remain useful for player identity, rankings, opponent context, surface context, and the broader match universe, but joins must be validated and must not be treated as automatic.

The pinned MCP profile now covers all six upstream ATP/WTA point shards at commit `2c59eef194967e688b69e73df344184a06322cd8`. The conservative context audit links 97.8% of its point-bearing matches to mirror commit `83733587353df8a41f2fd4f516147d5aa83f5a8d`. Human review confirmed all 25 sampled safe links; the links are cleared for internal contextual falsification, while exceptions and production identity use remain gated. MCP remains a selected charted sample, not enough for tour-wide Tennis DNA claims. See [dataset_profile.md](dataset_profile.md), [data_feasibility.md](data_feasibility.md), [sampling_bias.md](sampling_bias.md), [mcp_context_join.md](mcp_context_join.md), [mcp_context_join_human_review.md](mcp_context_join_human_review.md), and the [source contracts](../data/README.md).

## Minimum point-level data model

One immutable row per point, with a stable `match_id` and `point_number`:

- match identity: `match_id`, date, tournament, round, best_of, surface
- participants: `server_id`, `receiver_id`, player-side identifiers, handedness where available
- pre-point state: set number, game number, points in game, games in set, sets won, tiebreak flag, server/receiver score labels
- point event: winner (`server` or `receiver`), point-ending reason, ace/double-fault flag where available
- derived state: canonical state key, next state key, match completion flag, current player-to-serve
- provenance: source file/version, row hash, parser version, missingness flags

A point row is insufficient without the match format and server rotation rules. Reconstructors must reject impossible transitions rather than silently repair them.

## Storage proposal
**ENGINEERING DECISION:** Keep raw source files outside version control, store normalized analytical data as Parquet, and use DuckDB for local analytical queries. Add PostgreSQL only when an application workload demonstrates the need for durable serving or collaboration. This avoids infrastructure before product requirements exist.

## Dataset risks
- Point coverage is not necessarily random; charted matches may overrepresent notable players and events.
- Public collections can change or be corrected; record retrieval date and source revision.
- Match-level data cannot reconstruct point leverage.
- Missing points, retirements, walkovers, format changes, and super tiebreaks require explicit rules.
- Player identifiers must be reconciled without merging distinct people.
- Data availability may induce survivorship and selection bias.

## Initial reconstruction result

The first strict adapter reconstructed 311 of 391 sampled matches to completion. It rejected 77 matches: 45 set/game score mismatches, 19 point-number gaps, 9 server mismatches, and 4 point-score mismatches; 3 additional matches were incomplete. The snapshot contains 260 duplicate `(match_id, Pt)` groups: 250 exact repeats and 10 annotation conflicts. See [the reconstruction baseline](experiments/mcp_reconstruction_baseline.md). These are engineering/data-quality findings, not evidence about pressure performance.
