# ADR-002: DuckDB and Parquet for analytical workflows

## Context
Point-level research needs scans, joins, and repeatable local experiments before an API exists.

## Options considered
Pandas-only files, a managed warehouse, or Parquet queried by DuckDB.

## Decision
Use Pandas or Polars where they make a transformation clearer, write stable analytical outputs as Parquet, and query them with DuckDB.

## Why
This keeps experiments portable and avoids infrastructure that does not yet improve the research.

## Trade-offs
Users must manage data snapshots locally, and database-style permissions are out of scope. Query performance and schema contracts need explicit tests.

## Consequences
Notebooks remain consumers of modules and data products, never the source of production behavior.
