# ADR-001: Data storage strategy

## Context
Phase 1 needs reproducible analytical data without committing large or licensed raw datasets.

## Options considered
- CSV-only workflows.
- A PostgreSQL-first application database.
- Parquet files queried with DuckDB.

## Decision
Use source manifests and normalized Parquet for analytical data, with DuckDB for local queries. Defer PostgreSQL until serving or collaboration needs are demonstrated.

## Why
Parquet is columnar and portable; DuckDB supports local analytical work with low operational overhead. This matches the current research-first phase.

## Trade-offs
This requires explicit schema/version manifests and does not solve multi-user serving. PostgreSQL may be added later for a demonstrated product need.

## Consequences
Raw data stays external and versioned by provenance. Pipelines must record source revision, retrieval date, and parser version.
