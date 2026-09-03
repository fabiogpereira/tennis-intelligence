# Literature review baseline

Status: Phase 1 baseline. This is a map of relevant methods, not a completed systematic review. Claims below are deliberately bounded and each source is listed in the bibliography.

## Tennis scoring and state models
**ESTABLISHED RESEARCH:** Tennis has a recursive scoring structure: point outcomes determine games, games determine sets, and sets determine matches. This makes match-win probability computable from a sufficiently specified state and point-probability model.

**ESTABLISHED RESEARCH:** Klaassen and Magnus studied whether point outcomes can be treated as independent and identically distributed and found that tennis analysis needs to take dependence and player/context effects seriously. The exact implications depend on the model and data; this project must not assume iid points by default.

**PROJECT HYPOTHESIS:** A state-transition engine paired with a calibrated point model can estimate leverage at point resolution without relying on fixed pressure categories.

## Point importance and leverage
**ESTABLISHED RESEARCH:** The consequence of a point depends on score state and match format. A point's importance can therefore be represented through changes in a downstream win probability, provided that probability is defined and calibrated.

**OPEN QUESTION:** Whether absolute change in match-win probability is the best public-facing measure. Signed changes, expected absolute changes, and counterfactual value can answer different questions.

## Win probability and expected performance
**ESTABLISHED RESEARCH:** A probability forecast is useful only if it is both discriminative and calibrated. Evaluation must include calibration, proper scoring rules, temporal out-of-sample performance, and uncertainty.

**ENGINEERING DECISION:** Begin with transparent baselines before complex models: a score-state model, a player/opponent contextual point model, and a calibrated match-win model. Complexity must earn its place through validation.

## Elo and opponent strength
**ESTABLISHED RESEARCH:** Elo-style systems are recursive ratings based on outcomes and expected results. Tennis variants can incorporate surface and margin or point information, but each choice changes the estimand and introduces tuning decisions.

**PROJECT HYPOTHESIS:** Player strength should be a control or baseline, not an unexamined substitute for pressure performance. A pressure ranking that mainly reproduces Elo is not evidence of a distinct characteristic.

## Clutch performance and persistence
**ESTABLISHED RESEARCH:** High-leverage success rates are vulnerable to selection effects, low effective sample sizes, and regression to the mean. A player who looks exceptional in one period may not remain exceptional out of sample.

**OPEN QUESTION:** The tennis-specific persistence of a leverage-conditioned residual is unresolved for this project. It must be tested using time-forward splits, shrinkage, and reliability estimates rather than assumed from rankings.

## Similar approaches
The closest conceptual family is leverage-based sports analysis: define the value of an event by its effect on the probability of the eventual outcome, then study performance relative to expectation. Tennis-specific scoring models and point-by-point charting provide the state representation; Elo and contextual point models provide strength controls. The proposed Pressure Performance Index is a project hypothesis combining these families, not an established published metric.

## Research-reviewer note
The baseline supports investigating state-based leverage, but does not yet establish a validated player-level clutch statistic. A systematic search and source-by-source extraction should happen before metric selection.

## Bibliography
1. Klaassen, F. and Magnus, J. R. (2003). *Are points in tennis independent and identically distributed? Evidence from a dynamic binary panel data model.* Journal of the American Statistical Association. DOI: [10.1198/016214503388619456](https://doi.org/10.1198/016214503388619456)
2. Kovalchik, S. A. (2016). *Searching for the GOAT of tennis win prediction.* Journal of Quantitative Analysis in Sports. DOI: [10.1515/jqas-2015-0069](https://doi.org/10.1515/jqas-2015-0069)
3. Jeff Sackmann. *Tennis ATP point-by-point and match datasets.* Canonical repository: [github.com/JeffSackmann](https://github.com/JeffSackmann)
4. Match Charting Project. *Point-level tennis charting data and documentation.* [tennisabstract.com/charting](https://www.tennisabstract.com/charting/)
5. International Tennis Federation. *Rules of Tennis.* [itftennis.com/en/about-us/tennis-tech/itf-rules-of-tennis](https://www.itftennis.com/en/about-us/tennis-tech/itf-rules-of-tennis/)
6. FiveThirtyEight. *The Elo rating system.* Method overview: [fivethirtyeight.com/features/how-we-calculate-nba-elo-ratings](https://fivethirtyeight.com/features/how-we-calculate-nba-elo-ratings/)

Source-quality note: items 1–2 are academic references identified by DOI; items 3–6 are first-party or methodological reference points. Before publication, retrieve and archive exact metadata, access dates, and relevant passages in a formal bibliography file.
