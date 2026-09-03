# Complete MCP snapshot profile

**Generated:** 2026-09-03

**Snapshot ID:** `mcp-atp-wta-2026-09-03-2c59eef1`

**Official source commit:** `2c59eef194967e688b69e73df344184a06322cd8`

**Parser version:** `mcp-parser-v0.1-draft`

**Scope:** six point shards, two match metadata files, and twelve behavior-relevant aggregate files

## Counts

| Measure | ATP | WTA | Total |
|---|---:|---:|---:|
| Raw point rows | 1,284,276 | 568,839 | 1,853,115 |
| Usable logical point rows | 1,281,679 | 568,315 | 1,849,994 |
| Players in match metadata | 1,003 | 732 | 1,735 |
| Safely joined charted matches | 7,530 | 4,060 | 11,590 |
| Players in safely joined matches | 1,002 | 730 | 1,732 |

| Integrity check | Count |
|---|---:|
| Unique point keys | 1,850,490 |
| Duplicate point-key groups | 2,625 |
| Exact duplicate groups | 2,129 |
| Conflicting duplicate groups | 496 |
| Raw rows in conflicting groups | 992 |
| Unique metadata match IDs | 11,638 |
| Conflicting metadata IDs | 8 |
| Structurally anomalous metadata IDs | 47 |
| Safely joined charted matches | 11,590 |
| Point match IDs without safe metadata | 11 |
| Point match IDs absent from metadata | 0 |
| Point match IDs with conflicting metadata | 8 |
| Point match IDs with structurally anomalous metadata | 11 |
| Safe metadata IDs without points | 1 |

The usable-point policy collapses exact duplicate keys and excludes conflicting keys. It does
not repair or select among conflicting annotations.

## Point-field coverage after duplicate handling

| Point field | Rows | Non-empty | Completeness | Valid | Valid rate |
|---|---:|---:|---:|---:|---:|
| `match_id` | 1,849,994 | 1,849,994 | 100.0% | 1,849,994 | 100.0% |
| `Pt` | 1,849,994 | 1,849,994 | 100.0% | 1,849,994 | 100.0% |
| `Set1` | 1,849,994 | 1,849,994 | 100.0% | 1,849,994 | 100.0% |
| `Set2` | 1,849,994 | 1,849,994 | 100.0% | 1,849,994 | 100.0% |
| `Gm1` | 1,849,994 | 1,849,993 | 100.0% | 1,849,993 | 100.0% |
| `Gm2` | 1,849,994 | 1,849,992 | 100.0% | 1,849,992 | 100.0% |
| `Pts` | 1,849,994 | 1,849,994 | 100.0% | 1,849,994 | 100.0% |
| `Gm#` | 1,849,994 | 1,849,992 | 100.0% | 1,849,992 | 100.0% |
| `TbSet` | 1,849,994 | 1,849,993 | 100.0% | 1,849,993 | 100.0% |
| `Svr` | 1,849,994 | 1,849,994 | 100.0% | 1,849,994 | 100.0% |
| `1st` | 1,849,994 | 1,849,994 | 100.0% | 1,849,994 | 100.0% |
| `2nd` | 1,849,994 | 693,068 | 37.5% | 693,068 | 37.5% |
| `Notes` | 1,849,994 | 134,342 | 7.3% | 134,342 | 7.3% |
| `PtWinner` | 1,849,994 | 1,849,994 | 100.0% | 1,849,994 | 100.0% |

For `1st`, `2nd`, and `Notes`, “valid” means non-empty only. Shot-notation validity remains an
open parser question. A blank `2nd` value usually means no second serve and is not automatically
a data-quality failure; feature denominators must reflect tennis semantics.

## Notation preflight

| Check | Count |
|---|---:|
| Non-empty first-serve cells | 1,849,994 |
| Non-empty second-serve cells | 693,112 |
| First-serve cells containing undocumented characters | 337 |
| Second-serve cells containing undocumented characters | 62 |

### Undocumented characters

| Value | Count |
|---|---:|
| ` ` | 418 |
| `a` | 7 |
| `&` | 6 |
| `D` | 5 |
| `A` | 4 |
| `N` | 4 |
| `)` | 3 |
| `_` | 3 |
| `.` | 2 |
| `M` | 2 |
| `T` | 2 |
| `W` | 2 |
| ``` | 2 |
| `$` | 1 |
| `%` | 1 |
| `'` | 1 |
| `(` | 1 |
| `/` | 1 |
| `?` | 1 |
| `F` | 1 |

### Whole-point and exceptional codes

| Value | Count |
|---|---:|
| `S` | 12,069 |
| `R` | 4,256 |
| `Q` | 83 |
| `P` | 50 |
| `V` | 44 |

### Parser foundation result

| Cell | Parsed | Rejected | Parse success |
|---|---:|---:|---:|
| First serve | 1,682,148 | 167,846 | 90.9% |
| Second serve | 595,020 | 98,092 | 85.8% |

| Parsed attribute | Observed | Eligible parsed denominator | Coverage |
|---|---:|---:|---:|
| Known serve direction | 2,258,581 | 2,260,666 | 99.9% |
| Known shot direction | 5,221,335 | 5,335,724 | 97.9% |
| Known return direction | 1,297,842 | 1,339,375 | 96.9% |
| Known return depth | 931,906 | 1,339,375 | 69.6% |

Most common parser rejection classes:

| Value | Count |
|---|---:|
| `1st:expected_shot_type` | 161,651 |
| `2nd:expected_shot_type` | 96,691 |
| `1st:trailing_after_serve_fault` | 3,448 |
| `1st:expected_serve_direction` | 1,871 |
| `1st:trailing_after_rally_outcome` | 786 |
| `2nd:trailing_after_serve_fault` | 622 |
| `2nd:trailing_after_rally_outcome` | 437 |
| `2nd:expected_serve_direction` | 285 |
| `1st:missing_point_ending` | 85 |
| `2nd:missing_point_ending` | 55 |
| `1st:duplicate_modifier` | 4 |
| `2nd:duplicate_modifier` | 2 |
| `1st:trailing_after_serve_outcome` | 1 |

Most common rejection classes with the character found at the failing position:

| Value | Count |
|---|---:|
| `1st:expected_shot_type:8` | 71,786 |
| `1st:expected_shot_type:9` | 52,856 |
| `2nd:expected_shot_type:8` | 43,059 |
| `2nd:expected_shot_type:9` | 33,272 |
| `1st:expected_shot_type:7` | 24,980 |
| `2nd:expected_shot_type:7` | 14,485 |
| `1st:expected_shot_type:!` | 4,455 |
| `1st:trailing_after_serve_fault:;` | 2,809 |
| `1st:expected_shot_type:2` | 2,677 |
| `2nd:expected_shot_type:!` | 1,479 |
| `2nd:expected_shot_type:2` | 1,326 |
| `1st:expected_shot_type:+` | 1,276 |
| `1st:expected_shot_type:1` | 945 |
| `1st:expected_shot_type:3` | 900 |
| `2nd:expected_shot_type:+` | 818 |
| `1st:expected_serve_direction:g` | 798 |
| `2nd:expected_shot_type:3` | 729 |
| `1st:expected_serve_direction:n` | 654 |
| `1st:expected_shot_type:;` | 578 |
| `2nd:expected_shot_type:1` | 536 |

### Parser coverage by tour

| Tour | Cells | Parsed | Success |
|---|---:|---:|---:|
| ATP | 1,763,229 | 1,606,614 | 91.1% |
| WTA | 777,673 | 669,249 | 86.1% |

### Parser coverage by season

| Season | Cells | Parsed | Success |
|---|---:|---:|---:|
| 1960 | 661 | 659 | 99.7% |
| 1969 | 1,020 | 1,015 | 99.5% |
| 1970 | 428 | 426 | 99.5% |
| 1971 | 671 | 669 | 99.7% |
| 1972 | 350 | 350 | 100.0% |
| 1973 | 438 | 437 | 99.8% |
| 1974 | 733 | 733 | 100.0% |
| 1975 | 1,195 | 1,192 | 99.7% |
| 1976 | 642 | 642 | 100.0% |
| 1977 | 580 | 577 | 99.5% |
| 1978 | 742 | 741 | 99.9% |
| 1979 | 1,183 | 1,172 | 99.1% |
| 1980 | 3,926 | 3,901 | 99.4% |
| 1981 | 4,382 | 4,369 | 99.7% |
| 1982 | 3,954 | 3,947 | 99.8% |
| 1983 | 3,714 | 3,698 | 99.6% |
| 1984 | 5,376 | 5,364 | 99.8% |
| 1985 | 11,381 | 11,341 | 99.6% |
| 1986 | 7,255 | 7,234 | 99.7% |
| 1987 | 12,690 | 12,659 | 99.8% |
| 1988 | 11,003 | 10,963 | 99.6% |
| 1989 | 12,669 | 12,613 | 99.6% |
| 1990 | 21,295 | 21,207 | 99.6% |
| 1991 | 24,626 | 24,535 | 99.6% |
| 1992 | 23,753 | 23,681 | 99.7% |
| 1993 | 22,278 | 22,116 | 99.3% |
| 1994 | 22,026 | 21,965 | 99.7% |
| 1995 | 24,490 | 24,388 | 99.6% |
| 1996 | 25,712 | 25,629 | 99.7% |
| 1997 | 19,711 | 19,638 | 99.6% |
| 1998 | 20,958 | 20,900 | 99.7% |
| 1999 | 21,215 | 21,143 | 99.7% |
| 2000 | 24,270 | 24,001 | 98.9% |
| 2001 | 26,313 | 26,205 | 99.6% |
| 2002 | 26,326 | 26,199 | 99.5% |
| 2003 | 26,885 | 26,688 | 99.3% |
| 2004 | 30,420 | 30,255 | 99.5% |
| 2005 | 31,501 | 31,384 | 99.6% |
| 2006 | 37,156 | 37,038 | 99.7% |
| 2007 | 26,001 | 25,464 | 97.9% |
| 2008 | 29,294 | 29,027 | 99.1% |
| 2009 | 33,344 | 32,093 | 96.2% |
| 2010 | 29,855 | 29,656 | 99.3% |
| 2011 | 33,560 | 32,782 | 97.7% |
| 2012 | 43,098 | 41,770 | 96.9% |
| 2013 | 40,105 | 38,974 | 97.2% |
| 2014 | 64,297 | 57,042 | 88.7% |
| 2015 | 105,343 | 104,104 | 98.8% |
| 2016 | 55,569 | 53,699 | 96.6% |
| 2017 | 72,071 | 69,284 | 96.1% |
| 2018 | 79,922 | 75,137 | 94.0% |
| 2019 | 211,785 | 188,498 | 89.0% |
| 2020 | 73,664 | 54,683 | 74.2% |
| 2021 | 146,749 | 111,507 | 76.0% |
| 2022 | 213,912 | 166,230 | 77.7% |
| 2023 | 207,486 | 168,887 | 81.4% |
| 2024 | 252,748 | 218,872 | 86.6% |
| 2025 | 231,053 | 198,261 | 85.8% |
| 2026 | 77,118 | 68,219 | 88.5% |

### Parser coverage for the most-charted players

| Player | Matches | Cells | Parsed | Success |
|---|---:|---:|---:|---:|
| `Roger Federer` | 722 | 172,765 | 169,954 | 98.4% |
| `Novak Djokovic` | 552 | 127,288 | 118,619 | 93.2% |
| `Rafael Nadal` | 423 | 95,133 | 85,379 | 89.7% |
| `Hubert Hurkacz` | 320 | 73,486 | 47,163 | 64.2% |
| `Jannik Sinner` | 297 | 66,029 | 56,844 | 86.1% |
| `Daniil Medvedev` | 284 | 62,229 | 51,450 | 82.7% |
| `Andy Murray` | 256 | 61,452 | 57,537 | 93.6% |
| `Pete Sampras` | 237 | 63,052 | 62,817 | 99.6% |
| `Iga Swiatek` | 226 | 38,966 | 28,708 | 73.7% |
| `Carlos Alcaraz` | 221 | 50,249 | 45,886 | 91.3% |
| `Andre Agassi` | 215 | 57,407 | 57,263 | 99.7% |
| `Stefanos Tsitsipas` | 200 | 45,273 | 42,115 | 93.0% |
| `Alexander Zverev` | 195 | 42,601 | 39,605 | 93.0% |
| `Stefan Edberg` | 190 | 50,659 | 50,295 | 99.3% |
| `Bianca Andreescu` | 185 | 37,442 | 25,070 | 67.0% |
| `Dominic Thiem` | 183 | 41,167 | 38,240 | 92.9% |
| `Andrey Rublev` | 176 | 36,881 | 34,792 | 94.3% |
| `Grigor Dimitrov` | 173 | 37,751 | 35,228 | 93.3% |
| `Casper Ruud` | 170 | 35,413 | 33,160 | 93.6% |
| `Caroline Wozniacki` | 155 | 28,368 | 27,042 | 95.3% |

The parser result is a conservative foundation, not a final validity claim. Rejection classes must
be manually reviewed against the workbook before any normalization rule is added. Attribute rates
condition on currently parsed cells and can change as parser coverage improves.

## Charted-match coverage

### Surface

| Value | Count |
|---|---:|
| `Hard` | 7,563 |
| `Clay` | 2,749 |
| `Grass` | 1,278 |

### Tournament

| Value | Count |
|---|---:|
| `Australian Open` | 1,033 |
| `US Open` | 894 |
| `Wimbledon` | 762 |
| `Roland Garros` | 690 |
| `Indian Wells Masters` | 337 |
| `Miami Masters` | 280 |
| `Monte Carlo Masters` | 237 |
| `Tour Finals` | 234 |
| `Rome Masters` | 230 |
| `Paris Masters` | 229 |
| `Canada Masters` | 211 |
| `Madrid Masters` | 210 |
| `Indian Wells` | 208 |
| `Miami` | 193 |
| `Cincinnati Masters` | 188 |

### Round

| Value | Count |
|---|---:|
| `R32` | 2,123 |
| `R16` | 1,681 |
| `F` | 1,648 |
| `SF` | 1,569 |
| `QF` | 1,530 |
| `R64` | 1,313 |
| `R128` | 969 |
| `RR` | 600 |
| `Q1` | 67 |
| `Q2` | 44 |
| `Q3` | 33 |
| `BR` | 10 |
| `PO` | 1 |
| `PQ` | 1 |
| `R64 ` | 1 |

### Most-charted players

| Player | Matches |
|---|---:|
| `Roger Federer` | 722 |
| `Novak Djokovic` | 552 |
| `Rafael Nadal` | 423 |
| `Hubert Hurkacz` | 320 |
| `Jannik Sinner` | 297 |
| `Daniil Medvedev` | 284 |
| `Andy Murray` | 256 |
| `Pete Sampras` | 237 |
| `Iga Swiatek` | 226 |
| `Carlos Alcaraz` | 221 |
| `Andre Agassi` | 215 |
| `Stefanos Tsitsipas` | 200 |
| `Alexander Zverev` | 195 |
| `Stefan Edberg` | 190 |
| `Bianca Andreescu` | 185 |
| `Dominic Thiem` | 183 |
| `Andrey Rublev` | 176 |
| `Grigor Dimitrov` | 173 |
| `Casper Ruud` | 170 |
| `Caroline Wozniacki` | 155 |

These are exposure counts within a crowdsourced sample, not population rankings.

### Exposure distribution

| Exposure per player | Minimum | P25 | Median | P75 | Maximum |
|---|---:|---:|---:|---:|---:|
| Matches Per Player | 1 | 1 | 2 | 10 | 722 |
| Points Per Player | 56 | 140 | 359 | 1,538 | 125,338 |
| Opponents Per Player | 1 | 1 | 2 | 9 | 208 |
| Surfaces Per Player | 1 | 1 | 1 | 2 | 3 |
| Tournaments Per Player | 1 | 1 | 2 | 8 | 50 |

## Published aggregate-file coverage

| Aggregate | Tour | Rows | Charted matches covered | Coverage | Players | Orphan IDs | Conflicting grain groups | Invalid numeric values |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `charting-m-stats-NetPoints.csv` | ATP | 59,396 | 7,523 | 99.9% | 1,000 | 17 | 30 | 0 |
| `charting-m-stats-Overview.csv` | ATP | 56,850 | 7,527 | 100.0% | 1,002 | 17 | 46 | 0 |
| `charting-m-stats-Rally.csv` | ATP | 96,706 | 7,527 | 100.0% | 1,002 | 17 | 55 | 0 |
| `charting-m-stats-ReturnDepth.csv` | ATP | 270,002 | 7,527 | 100.0% | 1,002 | 17 | 138 | 0 |
| `charting-m-stats-ServeDirection.csv` | ATP | 45,341 | 7,526 | 99.9% | 1,002 | 17 | 31 | 0 |
| `charting-m-stats-ShotTypes.csv` | ATP | 352,384 | 7,529 | 100.0% | 1,002 | 17 | 161 | 0 |
| `charting-w-stats-NetPoints.csv` | WTA | 31,120 | 4,054 | 99.9% | 726 | 12 | 0 | 0 |
| `charting-w-stats-Overview.csv` | WTA | 26,820 | 4,058 | 100.0% | 730 | 12 | 0 | 0 |
| `charting-w-stats-Rally.csv` | WTA | 52,313 | 4,058 | 100.0% | 730 | 12 | 0 | 0 |
| `charting-w-stats-ReturnDepth.csv` | WTA | 145,235 | 4,060 | 100.0% | 730 | 12 | 0 | 0 |
| `charting-w-stats-ServeDirection.csv` | WTA | 24,432 | 4,060 | 100.0% | 730 | 12 | 0 | 0 |
| `charting-w-stats-ShotTypes.csv` | WTA | 177,717 | 4,059 | 100.0% | 730 | 12 | 0 | 0 |

Aggregate rows are generated from MCP notation. Their presence is useful for feasibility and
cross-checking, but it does not replace parser validation or prove that every denominator is
complete. The reported grain uses the available match/player-or-server/row-or-set keys. Conflicts
are excluded from feature consideration until they can be reconciled with raw point annotations.

## Snapshot files

| File | Bytes | SHA-256 |
|---|---:|---|
| `charting-m-matches.csv` | 1,149,384 | `3CAE52BCD4880606155DD449057B3856725C2362C4473ED452CEAF3AF4AD1313` |
| `charting-m-points-2010s.csv` | 36,832,932 | `65C44AC350915896253729B50E9A3B57880ADD588865763580F9D300C564E5FE` |
| `charting-m-points-2020s.csv` | 57,137,962 | `8350EB0D963974E45C79FF2EEFDCA1788131CC49C4F2B61FDF3DF1AFF3BBA78F` |
| `charting-m-points-to-2009.csv` | 38,404,877 | `EC4C83640ED15045F8B0983B074DF17A870094555541949B37FB60D862EE17F5` |
| `charting-m-stats-NetPoints.csv` | 6,243,659 | `183D4B6F0652E116BE794601C7659BFEA5B54916213A91D058BC73027EC890C1` |
| `charting-m-stats-Overview.csv` | 6,708,656 | `42EC479A9C5068E6699EC04B9556836D2E58DCDA456B5B2CC89FD95D12F8A273` |
| `charting-m-stats-Rally.csv` | 11,070,837 | `3AC1D647018FB426CA3AFD7223E22668BFD895A9E0283B06D1B55EA56F070242` |
| `charting-m-stats-ReturnDepth.csv` | 25,896,588 | `42DC9F95485282150031EAEB1F725C2766400E665EB6137C165F78FB67FCBC82` |
| `charting-m-stats-ServeDirection.csv` | 4,708,555 | `9780B92A6B20602EDE21F32B8C45667F9EB57867BE6A3766AA25B5D84C4924FB` |
| `charting-m-stats-ShotTypes.csv` | 33,709,827 | `D71CBD9471256BA8ED8C2CD3C1867D1581DE78FF65FE45473981B59A72098A16` |
| `charting-w-matches.csv` | 613,918 | `B3B39331F11D09DB45C4CB969904CDE30EF08F0CD0ADCAF91D96FAA9975F9B27` |
| `charting-w-points-2010s.csv` | 18,272,331 | `659A827430A37191D5C5CA2E5FCD4377504800539008ACFEBE942C42FC41D3BD` |
| `charting-w-points-2020s.csv` | 33,914,653 | `E81E2A93F7F929A37E45FB4BBF425809C451AC1AA8A21CB2D6DCBE2D26D8A542` |
| `charting-w-points-to-2009.csv` | 5,916,186 | `387BABFF76D23B781564F90000AEAEF28A44C9CBD83C346B969ADE9F1ABF93F7` |
| `charting-w-stats-NetPoints.csv` | 3,228,885 | `F2895A77E892A056F2FDEEF8EBD8D7186DC009EC9E5CB7A16AD0FA41D3E277BC` |
| `charting-w-stats-Overview.csv` | 3,160,936 | `418519777875F84E0D3C42CD182B32760024D5612910C9B0362353CC5E1F4B2F` |
| `charting-w-stats-Rally.csv` | 5,974,643 | `C4F12307C118C935D4DA4F53F8416B089F466250CD79DCAAD1C627F7544C7462` |
| `charting-w-stats-ReturnDepth.csv` | 13,876,912 | `731735823FC3CDC074CC096B01D26C346F3991E8EC878C4A619C26D0561D46E6` |
| `charting-w-stats-ServeDirection.csv` | 2,512,489 | `3272AF24668F2B44F91B49C4143A9321BD00EC48CFE5738ABC95E96B8C440BF4` |
| `charting-w-stats-ShotTypes.csv` | 16,932,556 | `5D8B91F0BCBB1F8952A854E0B82BEF8830A7A4A9D55C9E09C37E07BDE24BB5E3` |
| `data_dictionary.txt` | 2,707 | `7381EEAAEE020D42906D99E9ADF67215D0011B05C40BACB431E995E87538F293` |
| `MatchChart 0.3.2.xlsm` | 482,316 | `46E2349EEE512296A86170449F6E463A6BE91BE9261A0C7B6B5D5A25C006729F` |
| `README.md` | 4,849 | `750F0E043F59AB74941D2A71E175527FE0B3F694AC0177D781838F3C190DDB34` |

The machine-readable companion is `research/mcp_snapshot_profile.json`.
