# Experiments

Experiment specifications and reports belong here. Each experiment should state its question, estimand, data snapshot, feature provenance, split strategy, baselines, metrics, uncertainty, and stopping/falsification criteria.

Notebooks are exploratory artifacts. Reusable scoring, feature, and modeling logic belongs in tested modules under `pipelines/` or `models/` once implementation begins.

## Current reproducible audits

```powershell
python -m research.experiments.profile_mcp_snapshot
python -m research.experiments.profile_mcp  # focused legacy/single-shard fixture
```

The complete-snapshot profiler is the canonical MCP audit. It writes the human-readable dataset,
feasibility, sampling-bias, parser-baseline, and serve-reconciliation reports plus
`research/mcp_snapshot_profile.json`.
