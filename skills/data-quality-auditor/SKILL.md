---
name: data-quality-auditor
description: Audit tennis datasets, joins, and candidate behavioral features for completeness, validity, representativeness, provenance, and publishability; use before Tennis DNA features or sample-confidence claims are approved.
---

# Data quality auditor

## Purpose
Audit whether a dataset and its derived fields are sufficiently complete, valid, representative, and reproducible for Tennis Intelligence research.

## Use when
A new source is added, datasets are joined, a feature is proposed for Tennis DNA, player eligibility is discussed, or a profile/result is prepared for publication.

## Required inputs
- Source files, schema/data dictionary, license, and snapshot manifest.
- Unit of analysis and expected grain.
- Field definitions, transformations, and feature denominators.
- Coverage target: players, matches, seasons, surfaces, tournaments, rounds, and ranking bands where available.
- Entity-resolution keys and validation sample.

## Workflow
1. Verify file identity, source revision, retrieval date, checksum, license, and raw-data handling.
2. Confirm the actual schema against the data dictionary; distinguish absent fields from null fields.
3. Measure row counts, unique matches, players, tournaments, seasons, and duplicate keys.
4. Measure completeness, null rate, valid-value rate, range violations, impossible transitions, and denominator counts for every candidate field.
5. Profile distributions and coverage by player, season, tournament, surface, round, tour, and ranking band when ranking exists.
6. Check duplicate matches, duplicate players, identifier collisions, and join precision/recall using manually reviewed examples.
7. Check temporal consistency, source mixing, selection mechanisms, survivorship, and uneven player exposure.
8. Challenge proposed thresholds using observed distributions and sensitivity analysis.
9. Classify each field or feature as supported, exploratory only, unsupported, or blocked by source quality.
10. Produce a reproducible report with exclusions, caveats, and a re-run command.

## Expected outputs
- Dataset profile with actual counts and distributions.
- Field-level completeness and validity table.
- Sampling-bias assessment.
- Eligibility analysis with no arbitrary threshold.
- Feature recommendation: include, defer, or reject.
- Reproducible commands and source snapshot identifiers.

## Validation checks
- Every reported number can be regenerated from the recorded snapshot.
- Schema and data dictionary disagreements are visible.
- Nulls, duplicates, invalid values, and missing coverage are not silently repaired.
- Features do not use unavailable or convenience-derived fields without checking their provenance.
- Player and match joins have measured error cases.
- Claims are bounded to the observed sample when sampling is non-random.

## Challenge or reject when
Reject a feature with weak denominator coverage, arbitrary eligibility thresholds, hidden missingness, impossible values, unresolved identity collisions, or a claim that generalizes beyond the sampled population. Reject a join based only on names without a validation set. Say "insufficient evidence" when the source cannot support the proposed interpretation.
