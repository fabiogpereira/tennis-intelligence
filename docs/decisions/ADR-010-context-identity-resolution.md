# ADR-010: Conservative MCP context identity resolution

**Status:** Accepted for internal context-controlled experiments; not a production crosswalk

**Date:** 2026-09-03

## Context

MCP supplies behavioral notation but no stable external player IDs or ranking fields. The broader
Sackmann ATP/WTA files supply player IDs, rankings, and match context, but their tournament date is
usually the event-start date rather than the individual match date. Names and tournament labels
also vary between sources.

The original `JeffSackmann/tennis_atp` and `tennis_wta` Git remotes were unavailable on the retrieval
date. The previously identified archival mirror is reproducible, but it does not preserve the exact
hashes of its June 2026 upstream ATP/WTA snapshots.

## Decision

Version `research-mcp-context-join-v0.1`:

- pins `Aneeshers/tennis-sackmann-archive` commit
  `83733587353df8a41f2fd4f516147d5aa83f5a8d`;
- keeps raw mirror files outside Git;
- normalizes case, diacritics, whitespace, and separators but performs no fuzzy matching;
- requires tour, unordered player pair, and a -7/+20-day tournament-date window;
- requires either exact normalized tournament or joint round/surface/best-of agreement for a
  unique pair/date candidate;
- resolves multiple candidates only when tournament and round identify one row;
- namespaces player IDs by tour and match IDs by tour, source-file family, tournament ID, and match
  number; and
- rejects missing pairs, date-window misses, context conflicts, ambiguities, and target collisions
  as separate classes.

## Evidence

The automated audit reads 1,749,872 context rows and safely links 11,336 of 11,590 point-bearing MCP
matches (97.8%). Ranking is populated for 99.5% of linked player-match sides. Among linked records,
surface agrees for 97.5%, round for 99.6%, tournament label for 93.5%, and best-of for 99.6%.

The deterministic 50-row sample contains 25 accepted links and five records from each exception
class. The project owner reviewed all 25 accepted links as the same match. None was reviewed as a
different match. A descriptive 95% Wilson interval for the observed 25/25 result is 86.7%-100.0%,
but it is not a design-based confidence interval because sample selection was deterministic rather
than recorded random sampling.

Among exception rows with selected context, nine were the same underlying match despite metadata
conflicts or duplicate MCP identities, while one Filderstadt record incorrectly pointed to a US
Open match between the same players. That row was already excluded as a canonical collision. The
15 exception rows without side-by-side context evidence remain unreviewed and excluded.

## Consequences

- The collision-free safe links may support internal context-controlled falsification.
- Exception recall remains partially reviewed; no relaxed rule or alias is approved.
- The two normalized names mapping to multiple player IDs require explicit investigation.
- Fuzzy aliases may only be introduced as reviewed, versioned records with provenance.
- The mirror's provenance gap and CC BY-NC-SA 4.0 terms remain visible product constraints.
- A source-family segment is mandatory because tournament ID plus match number collides across
  main-draw, qualifying/challenger, futures, and ITF files.

## Evidence artifacts

- [Context join audit](../../research/mcp_context_join.md)
- [Human review instructions](../../research/mcp_context_join_review.md)
- [Human review result](../../research/mcp_context_join_human_review.md)
- [Context snapshot contract](../../data/sackmann_context_snapshot.md)
