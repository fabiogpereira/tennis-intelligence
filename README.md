# Tennis Intelligence

> A data-driven exploration of what separates elite tennis players from the rest.

**Status: Phase 1 | Tennis DNA feasibility audit**

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

See the [complete dataset profile](research/dataset_profile.md), [machine-readable audit](research/mcp_snapshot_profile.json), [snapshot contract](data/mcp_snapshot.md), [notation parser specification](research/mcp_notation_spec.md), [parser baseline](research/mcp_notation_parser_baseline.md), and [feature gate](research/tennis_dna_feature_gate.md).

## What we do not know yet

We do not yet know whether charted shot notation is complete and parseable enough to support stable player-style profiles. No result should be presented as a universal description of a player until coverage and split-sample stability support that interpretation.

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

Phase 1 has no runtime dependencies. From the repository root, inspect Markdown links and run:

```powershell
python -m unittest discover -s tests -v
python -m research.experiments.profile_mcp_snapshot
git diff --check  # when the directory is inside a Git worktree
```

## Limitations

Public point data is incomplete and selected. Match-state reconstruction can fail on missing points, retirements, format changes, or source corrections. Observational pressure estimates cannot establish causality or psychology on their own. These limitations are part of the product, not footnotes.

## Roadmap

See [ROADMAP.md](ROADMAP.md). The next step is to validate the MCP notation parser and aggregate denominators before defining Tennis DNA v0.1.
