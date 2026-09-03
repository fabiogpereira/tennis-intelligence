# Match Charting Project snapshot

## Role

**ENGINEERING DECISION:** The Match Charting Project (MCP) is the primary behavioral source for Research #01. ATP/WTA match datasets will later provide rankings, broader match-universe context, and validated entity resolution; they do not replace MCP shot-level information.

## Pinned source

- Upstream: [JeffSackmann/tennis_MatchChartingProject](https://github.com/JeffSackmann/tennis_MatchChartingProject)
- Commit: `2c59eef194967e688b69e73df344184a06322cd8`
- Snapshot ID: `mcp-atp-wta-2026-09-03-2c59eef1`
- Retrieved: 2026-09-03
- License: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
- Attribution: The Tennis Abstract Match Charting Project

The upstream README states that the data is crowdsourced, shot-by-shot, and non-commercial. Raw files are excluded from this repository and must not be redistributed as project assets.

## Reproduce the local snapshot

Requirements: Git and PowerShell. From the repository root:

```powershell
powershell -NoProfile -File pipelines/ingestion/fetch_mcp_snapshot.ps1
python -m research.experiments.profile_mcp_snapshot
```

The fetch script refuses to overwrite an existing destination. This prevents a source refresh from silently changing an analysis snapshot. Use a different `-Destination` for another commit and document the change before comparing outputs.

## Profiled scope

The complete-snapshot profile consumes:

- Three ATP and three WTA point shards: through 2009, the 2010s, and the 2020s.
- ATP and WTA match metadata.
- ATP and WTA aggregates for Overview, ServeDirection, ShotTypes, Rally, ReturnDepth, and NetPoints.

The generated [dataset profile](../research/dataset_profile.md) records row counts and SHA-256 hashes. The machine-readable [snapshot profile](../research/mcp_snapshot_profile.json) preserves schemas, field coverage, integrity counts, exposure summaries, and aggregate row categories.

## Boundaries

- **ESTABLISHED RESEARCH:** MCP is a crowdsourced charting project, not a random sample of professional tennis.
- **ENGINEERING DECISION:** Exact duplicate point keys are collapsed; conflicting point keys are excluded rather than guessed.
- **ENGINEERING DECISION:** Conflicting or structurally invalid metadata records are excluded from safe joins and remain counted in the audit.
- **OPEN QUESTION:** Aggregate files are derived from notation and require grain, denominator, and parser agreement checks before their fields become Tennis DNA features.
- **OPEN QUESTION:** Commercial product use would require a source/licensing decision because the MCP license is non-commercial and share-alike.
