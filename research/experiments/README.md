# Experiments

Experiment specifications and reports belong here. Each experiment should state its question, estimand, data snapshot, feature provenance, split strategy, baselines, metrics, uncertainty, and stopping/falsification criteria.

Notebooks are exploratory artifacts. Reusable scoring, feature, and modeling logic belongs in tested modules under `pipelines/` or `models/` once implementation begins.

## Current reproducible audits

```powershell
python -m research.experiments.profile_mcp_snapshot
python -m research.experiments.serve_stability
python -m research.experiments.audit_context_join
python -m research.experiments.summarize_context_join_review
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
