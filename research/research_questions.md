# Research questions

## Research #01: Can we quantify playing style?

**Public-facing concept:** Tennis DNA

**PROJECT HYPOTHESIS:** A multidimensional representation built from validated charted behavior may capture meaningful and partially stable differences in how professional tennis players play.

### Research questions

1. Which serve, return, shot, rally, error, and net features have sufficient coverage and parser validity?
2. Are player profiles stable across independent match samples?
3. Are players more similar to themselves than to randomly selected players?
4. Do natural style groups emerge without imposing traditional archetypes?
5. How much does style change across surfaces?

### Boundaries

MCP is a selected charted sample, not a random professional-tennis population. Initial claims must be phrased as claims about the charted sample. Tennis DNA is a project/research name and is not established research.

Feature selection is deferred until the dataset profile and notation parser establish coverage.

## Research #02: Does pressure change how players play?

The original pressure question is preserved as a future study. It may later use Tennis DNA behavioral features to ask whether serve direction, rally length, aggression, errors, or net usage change as leverage increases.

### Evidence labels
- **PROJECT HYPOTHESIS:** Point leverage based on the change in match-win probability may be more informative than fixed break-point or match-point labels.
- **PROJECT HYPOTHESIS:** Pressure behavior should be evaluated against expected behavior, not raw rates in selected situations.
- **OPEN QUESTION:** Whether a player-level pressure behavior effect persists out of sample.
- **OPEN QUESTION:** Whether a psychologically meaningful "clutch" construct is identifiable from public point data.

### Falsification criteria
The hypothesis is weakened or rejected if a pressure residual does not beat a player-quality baseline out of sample, fails calibration/sensitivity checks, or shows no persistence beyond sampling noise.

## Questions before implementation
1. Which win-probability model is sufficiently calibrated without leaking future information?
2. Should leverage be signed, absolute, or decomposed by serving/returning player?
3. How should expected point probability account for server, returner, surface, era, and match format?
4. How much point-level coverage is required for stable player estimates?
5. Does pressure performance persist across time, or does it regress fully toward the mean?
6. Can the design distinguish pressure response from strategic choice, fatigue, injury, or scoreboard-induced tactics?

## Future tracks, deliberately deferred
Serve versus return contribution, surface adaptability, career evolution, matchups, and performance persistence are possible future studies, not current deliverables.
