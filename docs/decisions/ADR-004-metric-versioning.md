# ADR-004: Metric versioning strategy

## Context
Tennis DNA features and future pressure metrics depend on source snapshots, parser rules, feature definitions, scoring rules, estimands, and model versions. Silent changes would make results incomparable.

## Options considered
Unversioned notebook outputs, Git commit references only, or explicit metric/model/data versions.

## Decision
Every published result will identify a research track, data snapshot, parser version, feature/metric definition version, model version when applicable, scoring-rule version when applicable, and experiment specification.

Use a small explicit convention:

- Data snapshot: `<source>-<scope>-<retrieval-date>-<sha256-prefix>`, for example `mcp-w-to-2009-2026-09-03-00d8b86b`.
- Parser: `<source>-parser-v<major>.<minor>`, created only when a parser exists.
- Feature set: `tennis-dna-v<major>.<minor>`, with `draft` appended until the feature set passes review.
- Pressure metric: a separately named and versioned Research #02 artifact; it must not inherit a Tennis DNA version implicitly.

A definition or denominator change increments the feature/metric version. A source refresh changes the snapshot identifier even when code is unchanged. Exploratory notebooks may use `draft`, but public outputs may not omit these identifiers.

## Why
A user must be able to understand what changed and reproduce the result without relying on hidden notebook state.

## Trade-offs
Metadata takes effort and may make early experiments feel slower. That cost is justified by research integrity.

## Consequences
Methodology changes require an ADR or experiment note and may invalidate prior outputs. The convention records provenance without introducing a model registry or ML platform during Phase 1.
