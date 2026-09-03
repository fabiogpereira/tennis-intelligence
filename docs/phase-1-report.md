# Phase 1 pivot and feasibility report

**Historical milestone:** this report records the Phase 1 exit state under parser v0.1. Current
Phase 2 evidence is in the [parser baseline](../research/mcp_notation_parser_baseline.md),
[serve reconciliation](../research/mcp_serve_reconciliation.md), and
[serve candidate specification](../research/serve_feature_candidates.md).

## Decision

**ENGINEERING DECISION:** Research #01 is now **Can we quantify playing style?** The provisional product name is Tennis DNA. It is not an established scientific construct.

The earlier clutch-performance investigation is preserved as Research #02: **Does pressure change how players play?** No PPI or Tennis DNA model has been implemented.

## What was preserved

- The deterministic tennis scoring engine and its domain tests.
- MCP and LiveTennisAPI source adapters, manifests, checksums, and raw-data policy.
- Pressure literature, estimand questions, calibration concerns, and falsification tests for Research #02.
- Architecture boundaries between ingestion, normalization, feature logic, experiments, APIs, and UI.
- Project review Skills for research, statistics, engineering, product, and portfolio work.

## What changed

- README, roadmap, methodology, architecture, and ADR-007 now make Tennis DNA Research #01.
- The MCP profiler reports field coverage, charted-sample exposure, duplicate conflicts, metadata integrity, source hashes, and blocked analyses.
- `data-quality-auditor` can reject weak fields, joins, thresholds, and claims before they enter Tennis DNA.
- Pressure work is deferred rather than removed.

## What data we actually have

The current MCP snapshot pins all six upstream ATP/WTA point shards and both match metadata files at commit `2c59eef194967e688b69e73df344184a06322cd8`. The generated [dataset profile](../research/dataset_profile.md) is authoritative for counts and hashes.

At the current snapshot it contains:

- 1,853,115 raw point rows and 1,849,994 usable logical points.
- 11,590 point-bearing matches with unambiguous, structurally valid metadata.
- 7,530 ATP matches, 4,060 WTA matches, and 1,732 represented players.
- 2,625 duplicate point-key groups: 2,129 exact and 496 conflicting.
- Match context, raw `1st`/`2nd` notation, and twelve behavior-relevant aggregate files.
- A draft parser that passes official examples but currently accepts 90.9% of non-empty first-serve cells and 85.8% of non-empty second-serve cells.
- Parser acceptance varies materially by circuit, era, and player; recent-season acceptance is only 74.2%-88.5% for 2020-2026.
- No ranking fields and no reliable total-shot count.

The audit excludes eight conflicting metadata IDs and 47 structurally anomalous IDs from safe joins. Eleven point-bearing match IDs therefore lack safe metadata. These records remain visible rather than being silently repaired.

## What we can reliably measure now

**ESTABLISHED FOR THIS SNAPSHOT:** source row counts, hashes, raw field completeness, exact/conflicting duplicate groups, metadata-match coverage, season/surface/tournament/round distributions, and player match/point exposure.

**SUPPORTED WITH EXCLUSIONS:** score state, server, and point winner for rows that survive duplicate handling. Strict match reconstruction still exposes source gaps and state disagreements; those failures are not silently repaired.

## What we cannot reliably measure now

**EXPLORATORY ONLY:** serve direction, shot direction/type, rally length, return depth, winners, forced/unforced errors, and net usage have published aggregate files. Their grains and denominators require validation against raw notation before feature use.

**BLOCKED BY SOURCE QUALITY:** reliable full-corpus shot totals and parser-derived behavior metrics. The draft parser rejects recurring grammar extensions, and its accepted-cell denominators may be selective.

**BLOCKED BY COVERAGE:** representative ATP/WTA comparisons, ranking-band coverage, and general claims about how a player always plays.

**OPEN QUESTION:** player eligibility and HIGH/MEDIUM/LOW confidence thresholds. They require observed denominator distributions, diversity checks, and split-sample stability rather than an arbitrary match cutoff.

## Recommendation for Tennis DNA v0.1

Do not approve a feature vector yet. The [feature gate](../research/tennis_dna_feature_gate.md) finds critical parser-selection and charted-sample bias. The full snapshot and core parser are now reproducible; next, review observed grammar extensions, improve parser coverage through versioned decisions, and compare parser-derived totals with published aggregates. Only raw, interpretable features that pass `data-quality-auditor` and `statistical-skeptic` should become v0.1 candidates.

Similarity, clustering, surface profiles, and player-facing UI remain out of scope until profile stability is demonstrated.

## Required human approvals

- Confirm MCP as the primary behavioral source and broader match data as contextual/join data.
- Confirm the pinned commit and the conservative policy of collapsing exact duplicate point rows and excluding conflicting groups.
- Approve raw, interpretable features as the first candidate layer before contextual adjustment models.
