# Tennis Intelligence

> A data-driven exploration of what separates elite tennis players from the rest.

**Status: Phase 2 | MCP data foundation and stability falsification**

Tennis Intelligence is a research-led product about performance in tennis. The first investigation now asks:

## Can we quantify playing style?

The provisional public-facing concept is **Tennis DNA**: a multidimensional representation of how a player plays, built from validated serve, return, shot, rally, error, and net-behavior features. Tennis DNA is a **PROJECT HYPOTHESIS**, not an established scientific construct.

The first step is feasibility. We will not define the feature vector, player thresholds, similarity map, or clusters until the Match Charting Project data has been profiled and its notation has been parsed and validated.

## Why this project

I played competitive tennis in national and international tournaments. That experience left me with a persistent question: what is actually different about the way elite players play? Tennis Intelligence is an attempt to investigate that question with public data, explicit uncertainty, and software that can be inspected.

## How the research evolved

The project began with a question about clutch performance. Data feasibility work showed that broad historical sources do not provide enough representative shot-level detail, while the Match Charting Project provides unusually rich behavioral data but is selected rather than representative. Instead of forcing a pressure claim onto a weak data foundation, Research #01 changed to **Can we quantify playing style?** The original pressure question is preserved as Research #02: **Does pressure change how players play?**

## What Phase 1 establishes

- A pivot analysis and decision record explaining why Research #01 changed.
- A research question and feasibility criteria for Tennis DNA.
- A conservative literature and dataset baseline in [research/literature_review.md](research/literature_review.md) and [research/datasets.md](research/datasets.md).
- The original pressure approaches and objections, preserved for Research #02 in [research/statistical_risks.md](research/statistical_risks.md).
- A minimum point-level data model and validation framework.
- An MCP data profiler with actual counts, completeness, feasibility, and sampling-bias reports.
- Project skills for research review, data-quality auditing, statistical skepticism, engineering quality, product design, and portfolio communication.
- Architecture decisions that keep notebooks exploratory and avoid premature infrastructure.

## Current evidence

The pinned complete MCP snapshot contains 1,853,115 raw point rows. After the conservative duplicate policy, 1,849,994 logical points remain. They cover 11,590 matches with unambiguous, structurally valid metadata and 1,732 represented players. This scale supports continued feasibility work; it does not remove the source's crowdsourced selection bias or validate any Tennis DNA feature.

Parser v0.2 preserves independently safe serve prefixes even when a later rally token is
unsupported. Across comparable match-player records, basic serve outcomes agree with MCP aggregates
at 99.9%-100.0%; side-aware direction vectors agree at 98.6% for first serves and 96.8% for second
serves. A first split-sample pilot then found lower median distance within players than between
players across all tested exposure levels, but chronological splits were consistently less stable
than alternating-match splits. These results keep serve features under study; they do not approve
publication or a Tennis DNA vector.

A conservative context audit now links 11,336 of 11,590 point-bearing MCP matches (97.8%) to a
pinned ATP/WTA archival mirror. Ranking is present for 99.5% of linked player-match sides, but the
human review confirmed all 25 sampled safe links. One different-match candidate was already
excluded by the collision rule. The safe links are cleared only for internal contextual
falsification; the mirror provenance gap and non-commercial/share-alike license remain explicit
product blockers.

See the [Phase 2 progress report](docs/phase-2-progress.md), [complete dataset profile](research/dataset_profile.md), [machine-readable audit](research/mcp_snapshot_profile.json), [MCP snapshot contract](data/mcp_snapshot.md), [context snapshot contract](data/sackmann_context_snapshot.md), [notation parser specification](research/mcp_notation_spec.md), [parser baseline](research/mcp_notation_parser_baseline.md), [serve reconciliation](research/mcp_serve_reconciliation.md), [serve stability pilot](research/serve_stability.md), [context join audit](research/mcp_context_join.md), [serve candidates](research/serve_feature_candidates.md), and [feature gate](research/tennis_dna_feature_gate.md).

## What we do not know yet

Serve candidates show aggregate split-sample persistence, but we do not yet know whether it
survives surface, opponent, era, tournament, and chart-author controls. We also do not know whether
the remaining notation supports return, rally, error, or net features. No result should be
presented as a universal description of a player.

## Product direction

The eventual product will let visitors explore player behavior, sample confidence, style similarity, and surface differences, with methodology and sampling limitations visible beside results. Research #02 may later use Tennis DNA to ask whether pressure changes behavior. The final application is not being built in this phase.

## Technical direction

The proposed architecture is Next.js and TypeScript for the web experience, FastAPI for an API boundary, and Python modeling/pipelines using Parquet and DuckDB for analytical work. These are planned choices, not installed dependencies. See [docs/architecture.md](docs/architecture.md) and [docs/decisions](docs/decisions).

## AI-assisted development

AI agents help with research discovery, drafts, test ideas, implementation, and review prompts. Human ownership remains with the problem definition, source acceptance, estimand, methodology approval, interpretation, architecture, product direction, and final conclusions. The workflow is documented in [docs/ai-assisted-development.md](docs/ai-assisted-development.md).

## Repository map

- `research/`: questions, literature, datasets, risks, experiments, and notebooks.
- `skills/`: reusable project-specific AI review workflows.
- `docs/`: methodology, architecture, AI transparency, and ADRs.
- `apps/`, `pipelines/`, `models/`, `packages/`, `tests/`: implementation areas, with only source adapters, scoring, profiling, and tests built so far.
- `data/`: schemas and handling guidance; raw source data is not committed.

## Local checks

The repository currently has no third-party runtime dependencies. From the repository root,
inspect Markdown links and run:

```powershell
python -m unittest discover -s tests -v
python -m research.experiments.profile_mcp_snapshot
python -m research.experiments.serve_stability
python -m research.experiments.audit_context_join
python -m research.experiments.summarize_context_join_review
git diff --check  # when the directory is inside a Git worktree
```

## Limitations

Public point data is incomplete and selected. Match-state reconstruction can fail on missing points, retirements, format changes, or source corrections. Observational pressure estimates cannot establish causality or psychology on their own. These limitations are part of the product, not footnotes.

## Roadmap

See [ROADMAP.md](ROADMAP.md). The next step is surface, opponent, era, tournament, ranking, and
chart-author sensitivity for the serve candidates, using only the reviewed safe context links.
Tennis DNA v0.1 is not yet approved.
