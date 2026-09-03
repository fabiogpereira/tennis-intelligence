# ADR-006: Use of Match Charting Project data

## Context
Tennis Intelligence needs point-level tennis data for a personal, publicly accessible, non-commercial research project. The Match Charting Project provides point-level professional match data, raw shot notation, derived aggregate files, and a data dictionary.

## Options considered
- Use the Match Charting Project for the research prototype.
- Find another point-level source before beginning any work.
- Request separate permission before using the data.

## Decision
Use the Match Charting Project for the personal research prototype, subject to the repository's CC BY-NC-SA 4.0 license. Credit the Tennis Abstract Match Charting Project, link to the original source, preserve the license for redistributed adaptations, and do not use the data for ads, paid features, sponsorship, or other commercial activity.

## Why
The source is directly relevant, transparent about its fields, and suitable for validating point reconstruction. The project owner has explicitly confirmed the intended use is public but non-commercial.

## Trade-offs
The license may not support a future commercial product or unrestricted redistribution. A later product direction, monetization, or hosting arrangement that creates commercial ambiguity requires a fresh license review or alternative dataset.

## Consequences
The source URL, retrieval date, revision/hash, attribution, license, and any transformations must be recorded in the data manifest. The reproducible Phase 1 baseline is `mcp-atp-wta-2026-09-03-2c59eef1` at commit `2c59eef194967e688b69e73df344184a06322cd8`; changing it requires a new snapshot identifier and regenerated reports. Adapted data must not be presented as an unrestricted original dataset. This decision does not remove the source's coverage, selection, or charting-quality limitations, and aggregate files do not bypass parser or denominator validation.
