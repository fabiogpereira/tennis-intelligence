# MCP data feasibility

**Status:** complete-snapshot audit; no Tennis DNA feature has been approved.

## Established for this snapshot

- Six ATP/WTA point shards were profiled at official commit `2c59eef194967e688b69e73df344184a06322cd8`.
- 1,853,115 raw point rows produce 1,849,994 usable logical points under the conservative duplicate policy.
- 11,590 point-bearing matches join to unambiguous MCP metadata.
- Behavior-relevant aggregate files cover as many as 7,529 matches, depending on the aggregate and its row semantics.
- Draft parser success is 90.9% for non-empty first-serve cells and 85.8% for non-empty second-serve cells.

## Data-quality decision

**EXPLORATORY ONLY:** the complete snapshot and draft parser are strong enough to justify
parser-revision and feature-coverage work. They are not sufficient to publish Tennis DNA profiles.

**BLOCKED:** population-level claims, player rankings, similarity scores, clusters, and confidence
tiers remain blocked by selected charting coverage, unresolved aggregate grains, parser validity,
and untested profile stability.

## Candidate families for the next audit

| Family | Evidence now available | Next gate |
|---|---|---|
| Serve outcomes and direction | Raw notation plus Overview/ServeDirection aggregates | Parser agreement and denominator audit |
| Return behavior and depth | Raw notation plus ReturnDepth aggregates | Missingness semantics and player-side validation |
| Shot selection and direction | Raw notation plus ShotTypes aggregates | Shot-code parser and redundancy review |
| Rally behavior | Raw notation plus Rally aggregates | Row-category and rally-denominator validation |
| Winners and errors | Overview/ShotTypes/Rally aggregates | Cross-file agreement and point-ending semantics |
| Net usage | NetPoints aggregates and notation | Approach definition and sparse-denominator audit |

No family should enter Tennis DNA merely because an aggregate CSV exists.

## Reproduce

```powershell
python -m research.experiments.profile_mcp_snapshot
```
