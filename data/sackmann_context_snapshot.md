# Sackmann ATP/WTA context snapshot

## Role

**ENGINEERING DECISION:** this source is a contextual match universe for internal MCP entity
resolution, ranking coverage, and sensitivity analysis. It does not replace MCP behavior data.

## Pinned mirror

- Mirror: [Aneeshers/tennis-sackmann-archive](https://github.com/Aneeshers/tennis-sackmann-archive)
- Mirror commit: `83733587353df8a41f2fd4f516147d5aa83f5a8d`
- Snapshot ID: `sackmann-archive-2026-06-25-8373358`
- Mirror commit date: 2026-06-25
- Retrieved: 2026-09-03
- Upstream attribution: Jeff Sackmann / Tennis Abstract
- License: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International

The mirror README states that ATP and WTA snapshots came from upstream commits made in June 2026,
but it does not record their exact hashes. On the retrieval date, the original
`JeffSackmann/tennis_atp` and `JeffSackmann/tennis_wta` Git remotes returned `Repository not found`.

**OPEN QUESTION:** whether the original repositories will return or publish verifiable successor
snapshots. The mirror commit is the reproducible source identity for this audit; it is not presented
as an original upstream commit.

## Consumed scope

The join audit reads yearly ATP tour, qualifying/challenger, and futures singles files and yearly
WTA tour and qualifying/ITF singles files. Doubles, rankings history files, player master files, and
Grand Slam point-by-point files are not inputs to join v0.1.

Tournament dates are usually event-start dates rather than match dates. Rankings embedded in match
rows are described by the upstream documentation as the ranking on, or most recently before, the
tournament date.

## Reproduce locally

```powershell
powershell -NoProfile -File pipelines/ingestion/fetch_sackmann_context_snapshot.ps1
python -m research.experiments.audit_context_join
```

The fetch script refuses to overwrite an existing directory. Raw files stay under `data/raw/` and
are excluded from Git.

## Product boundary

Both MCP and this context archive use CC BY-NC-SA 4.0. Commercial use and redistribution require a
separate source/licensing decision before production.
