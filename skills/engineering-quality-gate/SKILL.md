# engineering-quality-gate

## Purpose
Act as a senior engineering gate for reproducibility, maintainability, and proportionate complexity.

## Use when
A feature, pipeline, model, schema, dependency, or release is proposed as complete.

## Required inputs
- Changed files and intended behavior.
- Architecture and dependency impact.
- Tests, data contracts, and reproducibility instructions.
- Relevant validation output.

## Workflow
1. Trace the owning abstraction and public contract.
2. Check tests for domain edge cases and failure behavior.
3. Check typing, linting, deterministic transformations, and clear errors.
4. Inspect for duplication, unnecessary infrastructure, hidden state, and undocumented dependencies.
5. Check data/version provenance and reproducible commands.
6. Confirm documentation, limitations, and migration implications.
7. Report blockers separately from optional improvements.

## Expected outputs
A release decision with blockers, risks, test gaps, and a minimal remediation list.

## Validation checks
The narrowest relevant test runs first, followed by type/lint checks and reproducibility checks. New dependencies and architecture changes have explicit justification.

## Challenge or reject when
Reject a completion claim with missing tests, untyped public behavior, non-deterministic transformations, silent dependency additions, or infrastructure added only for appearance.
