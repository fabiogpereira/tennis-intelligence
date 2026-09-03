# ADR-007: Pivot Research #01 to Tennis DNA

## Context
The original Research #01 asked whether clutch performance is real and considered a pressure metric. Public data investigation showed that MCP has unusually rich shot-level detail but selected, non-representative coverage. The available data is better suited to describing how charted players play than to making broad claims about persistent clutch ability.

## Options considered
- Continue with pressure as Research #01 using MCP alone.
- Wait for a larger point-level source before any research product.
- Make playing style the first study and preserve pressure as a later study.

## Decision
Research #01 becomes **Can we quantify playing style?**, with the provisional product name **Tennis DNA**. The pressure study becomes Research #02: **Does pressure change how players play?**

## Why
This aligns the first question with the strongest available source characteristic: detailed behavioral charting. It is an intentional scope correction, not evidence that Tennis DNA is scientifically established.

## Trade-offs
MCP selection bias limits population claims. The first product may describe the charted sample rather than professional tennis generally. A larger match universe can provide context but does not automatically make shot behavior representative.

## Consequences
MCP becomes the primary behavioral source. Broader ATP/WTA match datasets are context and potential join universes. All entity resolution must be validated. Feature selection follows a reproducible feasibility profile. No player profile, similarity map, archetype, or cluster is published before stability and coverage checks pass.
