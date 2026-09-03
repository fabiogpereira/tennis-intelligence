# MCP sampling bias and eligibility risks

## Established limitation

The Match Charting Project is crowdsourced. Its 11,590 safely
joined point-bearing matches are not a random sample of professional tennis. Dataset size does not
remove famous-player, event, round, era, surface, or contributor selection effects.

## Observed dimensions

- Players represented in point-bearing matches: 1,732.
- Median matches per represented player: 2; maximum: 722.
- Median usable point exposure per represented player: 359; maximum: 125,338.
- Median distinct opponents per represented player: 2; maximum: 208.
- Median represented surfaces per player: 1 of at most four source labels.
- Surface, tournament, round, player, and opponent exposure are recorded in the machine-readable profile.
- Ranking-band coverage is unavailable until the MCP-to-ATP/WTA match join is implemented and validated.

## Eligibility remains an open question

No minimum-match threshold or HIGH/MEDIUM/LOW confidence label is approved. A future eligibility
analysis must jointly evaluate usable matches, field-specific point/shot denominators, opponent and
surface diversity, temporal coverage, and split-sample stability. Threshold sensitivity must be
reported rather than selecting a convenient cutoff.

## Claim boundary

Use “in the charted MCP sample” for player descriptions. Do not infer that a profile represents all
matches played by that player, an entire tour, or causal playing-style traits.
