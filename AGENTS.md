# Tennis Intelligence Agent Guidance

## Product philosophy
Tennis Intelligence is a research-led public product, not a generic dashboard. Optimize for useful questions, honest uncertainty, clear storytelling, and a polished experience. Research #01 is an investigation, not proof that clutch performance exists. Do not build future research tracks until their question and evidence justify them.

## Research integrity
- Label claims as **ESTABLISHED RESEARCH**, **PROJECT HYPOTHESIS**, **ENGINEERING DECISION**, or **OPEN QUESTION**.
- Cite primary sources, official documentation, or reputable academic work. Never fabricate a reference.
- Separate software correctness from statistical validity. Passing tests does not validate a metric.
- Report null, negative, conflicting, and inconclusive results.
- Do not change a metric definition, dataset, split, or interpretation without documenting the decision and its rationale.

## Engineering standards
- Prefer the simplest architecture that meets a demonstrated need.
- Do not silently introduce dependencies, services, infrastructure, or data sources.
- Keep production modeling logic in tested modules; notebooks are for exploration only.
- Prefer deterministic transformations, explicit schemas, temporal splits, reproducible experiments, typing, and focused tests.
- Avoid speculative abstractions for hypothetical research tracks.

## Project structure
- `apps/`: user-facing web and API applications.
- `research/`: questions, literature, datasets, risks, experiments, and notebooks.
- `pipelines/`: ingestion, processing, and feature transformations.
- `models/`: reusable win-probability and pressure modeling logic.
- `packages/`: shared contracts and utilities.
- `skills/`: portable AI workflow definitions.
- `docs/`: architecture, methodology, decisions, and AI transparency.
- `data/`: schemas and data handling guidance; raw data is not committed.
- `tests/`: domain, pipeline, and model tests.

## Naming conventions
Use lowercase snake_case for Python modules and data fields, kebab-case for web routes, and descriptive versioned names for metrics and experiments. Use `research-` or `model-` prefixes in experiment identifiers where useful. Preserve source dataset names in ingestion metadata.

## Validation before completion
Run the narrowest relevant tests first, then typing/linting and reproducibility checks. For research changes, verify every factual claim has a source, assumptions are labeled, and the statistical-skeptic review has considered leakage, confounding, calibration, uncertainty, and temporal out-of-sample persistence. For UI work, inspect responsive screenshots when browser tooling is available.

## Skills workflow
Use `research-reviewer` for literature and bibliography work, `statistical-skeptic` for metric proposals and results, `engineering-quality-gate` before implementation is considered complete, `product-design-reviewer` for product/UI work, and `portfolio-storyteller` for public-facing narrative. Recommendations are inputs to human judgment, not automatic approvals.

## Current phase
Phase 1 is pivot, data feasibility, and research only. Research #01 is Tennis DNA; the original pressure work is preserved as Research #02. Do not implement Tennis DNA modeling, PPI, or the final application until the MCP profile, notation parser, feature coverage, and stability questions have been reviewed. Record significant disagreements and methodology changes in the relevant document or an ADR.

## How to run checks
The repository currently has no third-party runtime dependencies. From the repository root, run the narrow checks with `python -m unittest discover -s tests -v`, regenerate feasibility reports with `python -m research.experiments.profile_mcp_snapshot`, then perform Markdown link/path review and `git diff --check` when the directory is inside a Git worktree.
