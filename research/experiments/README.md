# Experiments

Experiment specifications and reports belong here. Each experiment should state its question, estimand, data snapshot, feature provenance, split strategy, baselines, metrics, uncertainty, and stopping/falsification criteria.

Notebooks are exploratory artifacts. Reusable scoring, feature, and modeling logic belongs in tested modules under `pipelines/` or `models/` once implementation begins.

## Current reproducible audits

```powershell
python -m research.experiments.profile_mcp_snapshot
python -m research.experiments.serve_stability
python -m research.experiments.audit_context_join
python -m research.experiments.summarize_context_join_review
python -m research.experiments.context_serve_stability
python -m research.experiments.serve_shrinkage
python -m research.experiments.serve_publication_readiness
python -m research.experiments.first_serve_direction_robustness
python -m research.experiments.first_serve_direction_process_uncertainty
python -m research.experiments.profile_mcp  # focused legacy/single-shard fixture
```

The complete-snapshot profiler is the canonical MCP audit. It writes the human-readable dataset,
feasibility, sampling-bias, parser-baseline, and serve-reconciliation reports plus
`research/mcp_snapshot_profile.json`.

The context-join audit pins a separate ATP/WTA archive, produces aggregate precision/coverage
evidence, and writes a deterministic human-review queue. It does not approve the crosswalk by
itself.

The review summarizer validates that the project-owner CSV preserves every generated evidence
field, accepts documented Excel localization of dates and booleans, and produces a bounded review
result. It does not fill blank labels or convert reviewed exceptions into aliases.

The context-controlled serve pilot uses only collision-free safe links, keeps three candidate
families separate, and repeats chronological stability inside pre-specified surface, era, ranking,
tournament, chart-author, and joint-context strata. It emits no player estimates.

The temporal shrinkage pilot evaluates five serve targets with rolling training, validation, and
test seasons over four pre-specified exposure thresholds. It compares context-only, raw player,
and partially pooled player predictions and emits aggregate diagnostics only.

The publication-readiness audit measures trailing five-season exposure diversity, match
concentration, effective match count, and match-clustered uncertainty. It reports only aggregate
target/tour/surface/period summaries and does not choose a public threshold.

The first-serve direction robustness audit tests raw later-season error and conditional versus
match-clustered coverage across fixed windows and exposure levels. The process-uncertainty follow-up
uses validation-only residuals to calibrate additive temporal variance before untouched test years.
