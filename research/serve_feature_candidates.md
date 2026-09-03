# Tennis DNA serve feature candidates

**Definition version:** `tennis-dna-serve-v0.1-candidate`

**Data snapshot:** `mcp-atp-wta-2026-09-03-2c59eef1`

**Parser:** `mcp-parser-v0.2-draft`

**Status:** nominated for stability experiments; not approved for player profiles

## Estimand boundary

**PROJECT HYPOTHESIS:** these rates may describe reproducible serve behavior for a player within the
charted MCP sample. They do not measure serve quality, intent, talent, or causal player effects.

The unit of analysis is an observed service point. Player-level estimates must aggregate at the
match level for uncertainty and must not treat points as independent observations.

## Candidate definitions

| Candidate | Numerator | Eligible denominator | Missing / excluded |
|---|---|---|---|
| `first_serve_in_rate` | Service points with a safely classified first serve in play | Service points with resolvable first-serve status | Unobserved/penalty points; malformed or ambiguous first-serve prefix |
| `ace_per_service_point` | Safely observed first- or second-serve aces | Service points whose terminal serve state rules an ace in or out | Exceptional points; terminal serve state unresolved |
| `double_fault_per_second_serve_attempt` | Safely observed second-serve faults after a first-serve fault | Resolvable second-serve attempts | Missing or malformed second-serve notation |
| `first_serve_in_direction_share` | First serves in play for one known wide/body/T direction | First serves in play with known direction, separately by deuce/ad court | Direction `0`; unresolved court side or first-serve status; faults |
| `second_serve_direction_share` | Second-serve attempts for one known wide/body/T direction | Second-serve attempts with known direction, separately by deuce/ad court | Direction `0`; unresolved court side or serve number |

**ENGINEERING DECISION:** the initial first-serve direction candidate is conditional on the first
serve landing in. This matches the MCP `ServeDirection` row `1` denominator and must be named
explicitly; it is not equivalent to intended direction across all first-serve attempts.

The aggregate column `second_in` behaves as a second-serve-attempt count, including double faults,
in the current reconciliation. The source name is retained only for comparison and is not adopted
as the public feature name.

## Current software-consistency evidence

Across comparable match-player records, raw-notation agreement with MCP `Overview` is 99.9% for
service points, aces, first serves in, and second-serve attempts, and effectively 100.0% for double
faults. Mean absolute differences are below 0.01 per match-player record.

For `ServeDirection`, the exact side-aware six-cell vector agrees for 98.6% of first-serve records,
96.8% of second-serve records, and 95.7% of total records. Marginal wide/body/T agreement is 99.0%,
97.0%, and 96.2%, respectively. See the
[serve reconciliation report](mcp_serve_reconciliation.md) for denominators and source conflicts.

**Interpretation:** this supports nomination for falsification and stability tests. It does not make
the aggregates independent ground truth, explain every mismatch, or approve player-level output.

## Ranked remaining threats

1. MCP match selection may make a player's charted serve mix unlike their full career or season.
2. Surface, opponent, era, tournament, score state, and match format can explain raw differences.
3. Direction is conditional on recorded/known direction and, for first serves, on the serve landing
   in; those mechanisms may differ by player and chart author.
4. Repeated points within matches reduce effective sample size.
5. Unexplained reconciliation exceptions may be concentrated in particular source periods or
   contributors.
6. Inspecting recognizable players before fixing eligibility rules can bias feature selection.

## Required stability experiment

For each candidate, before approval:

1. publish field-specific coverage by player, season, surface, tournament, and chart author;
2. characterize every reconciliation mismatch class rather than selecting a convenient tolerance;
3. split each player's matches into earlier/later and alternating-match samples;
4. calculate match-level uncertainty and shrink sparse estimates toward an explicit baseline;
5. compare within-player persistence with between-player differences;
6. repeat with surface and opponent-strength stratification after the contextual join exists; and
7. report threshold sensitivity, null results, reversals, and unstable players.

## Falsification criteria

Reject or revise a candidate if apparent player differences disappear under basic context controls,
do not persist across independent match samples, are dominated by match-level uncertainty, or track
chart-author/missingness patterns more strongly than player identity.

## Recommendation

**PROCEED TO A SERVE-ONLY STABILITY PILOT.** Do not combine these candidates into a Tennis DNA
vector, assign weights, rank players, or expose them in a product yet. Second-serve direction should
receive particular scrutiny because its reconciliation is weaker than first-serve direction.
