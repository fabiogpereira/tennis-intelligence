# Methodology

## Current status
Phase 1 is complete and Phase 2 is active. The complete MCP snapshot is profiled, the field-aware
v0.2 parser preserves safe prefixes, and serve fields have been reconciled against MCP aggregates.
An aggregate serve pilot found provisional persistence across independent match splits, with weaker
chronological than alternating-match stability. Serve candidates are not approved for player
profiles. A precision-first ATP/WTA context join reaches 97.8% automated coverage but remains
unapproved until its deterministic sample is reviewed. Parser exceptions for other behavior
families and context-controlled stability remain unresolved. Tennis DNA is a project/research name,
not an established scientific construct.
Research #02 pressure work is preserved but not active.

## Proposed Tennis DNA analytical chain

```text
raw MCP source files
        -> source/schema audit
        -> validated shot-notation parsing
        -> canonical point and player records
        -> raw behavior features
        -> coverage and uncertainty audit
        -> split-sample stability tests
        -> similarity or clustering experiments
```

### Match and point state
The existing scoring engine and source adapters remain reusable infrastructure. A canonical record
must preserve source identity, player identity, match context, point state, notation provenance, and
missingness. Context IDs retain source namespaces. Join v0.1 uses exact normalized player pairs,
bounded date proximity, and supporting context; fuzzy names, ambiguities, source conflicts, and
target collisions are not silently repaired.

### Notation validity and attribute coverage
Parser success is not feature coverage. Shot direction and return depth are optional, `0` means
unknown, exceptional whole-point codes contain no ordinary shot sequence, and some observed strings
extend or contradict the simplified workbook grammar. The v0.2 parser may preserve a safe serve
prefix while rejecting a later suffix; this does not make the cell fully valid. Reports separate
observed, unknown, absent, partial, invalid, and not-applicable components. Published MCP aggregates
are comparison targets, not ground truth that overrides raw-source conflicts.

### Tennis DNA feature
A candidate feature is a defined behavioral quantity with source fields, denominator, transformation version, sample requirement, interpretation, and confounders. Raw behavior comes before surface/opponent/era adjustment.

### Representation
**PROJECT HYPOTHESIS:** A validated vector of behavioral features may represent meaningful and partially stable differences in how players play. A two-dimensional projection is a visualization, not proof that geometric distance equals real-world style distance.

### Stability
Player profiles must be calculated on independent match samples. The v0.1 pilot uses chronological
and alternating disjoint matches, match-level bootstrap diagnostics, and within-tour between-player
negative controls. Its aggregate result is necessary but not sufficient: context-controlled
persistence and player-level uncertainty must precede similarity or archetype claims.

### Research #02 pressure analysis
The preserved pressure study may later ask whether behavior changes as leverage rises. It must use Tennis DNA-compatible behavioral outcomes and retain the original leakage, calibration, persistence, and selection-bias safeguards.

## Interpretation boundary
An observed behavioral difference can describe the charted sample. It does not, by itself, prove intent, psychology, causality, or a universal player trait.

## Required reporting
Every result must state data snapshot, match inclusion rules, model version, temporal split, calibration, uncertainty, sensitivity analyses, missingness, and limitations. Metric versions belong in ADRs and experiment specifications.
