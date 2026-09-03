# Pivot analysis: from pressure to playing style

## Current components

The repository currently contains:

- Research framing, evidence labels, literature notes, dataset assessments, and statistical-risk reviews.
- A deterministic tennis scoring engine in `models/scoring.py`.
- An MCP CSV adapter with strict validation and exact-duplicate normalization in `pipelines/processing/mcp.py`.
- A LiveTennisAPI scoreboard-state adapter in `pipelines/processing/livetennis.py`.
- A pinned complete MCP snapshot contract, reproducible acquisition script, and sample/full-snapshot profiling experiments.
- Standard-library tests for scoring, source parsing, normalization, and edge cases.
- Six reusable AI skills, including an adversarial data-quality gate.

## What was built for the original pressure research

The original work focused on point leverage, expected performance, match-state reconstruction, and persistence of a possible Pressure Performance Index. It established useful state-transition, provenance, calibration, leakage, and temporal-validation concerns, but did not implement PPI or publish a pressure result.

## Fully reusable

- Scoring transitions and domain tests.
- Source manifests, raw-data exclusion, checksums, and provenance conventions.
- MCP normalization and strict rejection of ambiguous records.
- LiveTennisAPI and MCP adapters as source-specific ingestion boundaries.
- Research experiment conventions and the adversarial statistical review process.
- Architecture principles separating raw ingestion, normalized data, research experiments, and future applications.
- Existing AI skills and AI ownership documentation.

### Reuse by repository area

| Area | Decision | Rationale |
|---|---|---|
| Match ingestion | Reuse and extend | MCP and LiveTennisAPI adapters preserve source-specific semantics and reject ambiguous rows |
| Point reconstruction | Preserve for Research #02 and validation | Stateful scoring and reconstruction tests remain useful, but do not parse shot notation |
| Player models | Not built | No player representation or PPI exists to migrate |
| APIs | Preserve boundary only | `apps/api` documents the intended boundary; no endpoints exist yet |
| Frontend | Preserve boundary only | `apps/web` is a placeholder; product UI remains intentionally deferred |
| Data structures | Reuse scoring records; extend later | Canonical player/match identity and notation records are still missing |
| Tests | Reuse and extend | Domain/source tests pass; profiler contract tests now cover duplicate and orphan behavior |
| Documentation | Reclassify incrementally | Pressure material remains Research #02; pivot and feasibility documents become the active entry points |
| Research tooling | Reuse | Experiments remain reproducible consumers of tested modules rather than production logic |
| AI Skills | Reuse plus one gate | Existing review Skills remain; `data-quality-auditor` adds source/feature rejection authority |

## Needs modification

- README, roadmap, methodology, and research question documents must identify Tennis DNA as Research #01.
- Dataset documentation must distinguish raw MCP point notation from derived aggregate fields and their denominators.
- The data layer needs a canonical player/match representation and validated entity-resolution work before joining MCP to broader match data.
- Snapshot profiling is complete; parser-validity and field-denominator audits must still precede feature selection.
- The current MCP adapter is sufficient for event/state validation, but shot-code parsing and feature extraction do not yet exist.

## Preserve as Research #02

The pressure literature review, PPI candidate approaches, statistical objections, validation framework, and source-quality findings remain valuable. They become Research #02: **Does pressure change how players play?** Tennis DNA can later provide the behavioral outcomes for that question.

No pressure code or documentation is deleted. Its interpretation changes from the first product study to a future research track.

## Now obsolete or insufficient

- Treating MCP as a representative professional-tennis universe is obsolete and explicitly rejected.
- Treating a single pressure score as the immediate product objective is obsolete.
- Assuming 11,590 selected charted matches are representative enough for general player rankings is insufficient.
- Treating published aggregate columns as validated Tennis DNA features is unsafe until their grains and denominators agree with parsed notation.
- The existing `models/README.md` description as pressure-first should be broadened to reusable research models.

## Proposed migration plan

1. Reclassify the pressure work as Research #02 and record this pivot.
2. Profile the actual MCP files and publish completeness, coverage, and sampling-bias reports.
3. Audit entity resolution between MCP match metadata and the broader match universe; do not assume joins are exact.
4. Define a Tennis DNA v0.1 feature ontology from fields that survive the feasibility audit.
5. Implement only a small, well-covered feature pipeline with denominator and missingness tests.
6. Run `data-quality-auditor` and `statistical-skeptic` before profile generation at scale.
7. Test within-player profile stability on split matches before similarity, clustering, or UI work.
8. Keep Research #02 and future surface/career/matchup tracks documented but unimplemented.

## Data-feasibility implementation

The standard-library full-snapshot profiler discovers all six MCP point shards, verifies schemas, records the upstream commit and file SHA-256 hashes, applies the documented duplicate policy, rejects structurally invalid metadata from safe joins, and audits twelve behavior-relevant aggregate files. It writes human-readable feasibility reports and a machine-readable JSON artifact.

Re-run from the repository root:

```powershell
python -m research.experiments.profile_mcp_snapshot
```

Optional `--source` and `--output` arguments support alternate pinned snapshots without editing source code. The earlier single-file profiler remains available for focused fixtures. The foundation intentionally stops before shot-notation parsing.

## Pivot risks

- MCP selection bias can make Tennis DNA descriptive of the charted sample rather than professional tennis generally.
- Shot notation may be more complex or incomplete than the convenience fields suggest.
- Player sample sizes can be highly unequal, making profiles and similarity rankings unstable.
- Entity-resolution errors can falsely attribute behavior to the wrong player or duplicate a match.
- Combining MCP with broader match data can introduce temporal, tournament, or population mismatch.
- A visually compelling low-dimensional map can overstate what distance means.

## Assumptions requiring approval

- **ENGINEERING DECISION:** MCP is the primary behavioral source; broader match data supplies context and a join universe.
- **ENGINEERING DECISION:** The reproducible baseline is pinned to MCP commit `2c59eef194967e688b69e73df344184a06322cd8` and all six point shards.
- **ENGINEERING DECISION proposed:** Initial Tennis DNA features will be raw, interpretable rates with coverage and uncertainty, not adjusted causal effects.
- **OPEN QUESTION:** Minimum player eligibility thresholds will be selected from observed distributions, not chosen in advance.
- **ENGINEERING DECISION proposed:** No player-facing profiles, similarity claims, or clusters will be published before split-sample stability is tested.
