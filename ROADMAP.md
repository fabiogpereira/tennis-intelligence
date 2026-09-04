# Roadmap

This roadmap is phased to protect research quality. Dates are intentionally omitted until data access and scope are known.

## Phase 1: Foundation, pivot, and feasibility | complete
- Preserve the pressure research as Research #02.
- Establish Research #01: Can we quantify playing style?
- Profile the actual Match Charting Project files before selecting features.
- Audit raw-field completeness, player exposure, source integrity, and sampling bias.
- Pin and document the complete six-shard ATP/WTA MCP snapshot.
- Define entity-resolution requirements for MCP and broader match datasets.
- Create transparent AI workflows and architecture decisions.

**Exit criteria:** pivot reviewed, full MCP snapshot scope documented, profiling outputs reproducible, unsupported fields identified, and snapshot-level data-quality review completed.

## Phase 2: MCP data foundation | current
- Implement and validate the MCP shot-notation parser against official instructions.
- Add canonical match/player schemas and validated entity resolution.
- Add field completeness, parser-validity, missingness, and provenance reports.
- Build tests for feature denominators and source exceptions.
- Characterize serve-reconciliation exceptions and run an aggregate split-sample stability pilot.
- Pin an ATP/WTA archival context snapshot and audit a conservative cross-source match join.

**Exit criteria:** deterministic parsing on a documented fixture set, explicit handling of invalid/exceptional records, and enough coverage evidence to nominate candidate Tennis DNA fields.

## Phase 3: Tennis DNA definition and feature pipeline
- Define a feature ontology from fields that pass the feasibility audit.
- Start with raw interpretable behavior rates before adjustments.
- Add denominator, missing-data, and deterministic-transformation tests.
- Evaluate redundancy, coverage, uncertainty, and surface/context confounding.

**Exit criteria:** Tennis DNA v0.1 specification approved by data-quality-auditor and statistical-skeptic.

## Phase 4: Profile stability and style discovery
- Split eligible players’ charted matches into independent samples.
- Test whether within-player profiles are more similar than random-player profiles.
- Evaluate similarity metrics and clustering only after stability checks.
- Test surface-specific profiles with sample-size safeguards.

**Exit criteria:** reproducible stability results and bounded interpretation of any similarity or cluster output.

## Phase 5: Research #01 product
- Build the editorial web experience only around validated Tennis DNA evidence.
- Show charted-sample coverage, confidence, definitions, and sampling limitations.
- Explain raw versus adjusted behavior and what projected maps do not mean.
- Add accessible charts, responsive views, methodology links, and uncertainty.

**Exit criteria:** product and engineering quality gates pass; screenshots and public documentation match the analysis snapshot.

## Research #02: pressure and behavior | deferred
Only after Tennis DNA is stable, evaluate whether point leverage changes behavior such as serve direction, rally length, aggression, errors, or net usage. The preserved pressure literature and modeling work remain inputs, not an active implementation.

## Phase 6: Expansion
Only after Research #01 is stable, evaluate career evolution, matchups, or other questions. New tracks require their own question, data, methodology, and validation plan.
