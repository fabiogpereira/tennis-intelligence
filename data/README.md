# Data

Raw and licensed source data is not committed to this repository. Store local data outside Git and record source URL, retrieval date, revision/hash, license/terms, parser version, and schema version in a manifest.

Normalized analytical outputs should use versioned Parquet. See [research/datasets.md](../research/datasets.md) and [docs/decisions/ADR-001-data-storage-strategy.md](../docs/decisions/ADR-001-data-storage-strategy.md).

Pinned local source contracts:

- [Match Charting Project behavior snapshot](mcp_snapshot.md)
- [Sackmann ATP/WTA context mirror](sackmann_context_snapshot.md)
