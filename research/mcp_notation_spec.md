# MCP notation parser specification

**Status:** field-aware draft parser contract (`mcp-parser-v0.2-draft`); corpus failures remain under review

**Source:** `MatchChart 0.3.2.xlsm`, Instructions sheet, from snapshot `mcp-atp-wta-2026-09-03-2c59eef1`

## Research boundary

**ESTABLISHED RESEARCH:** The Match Charting Project records every observed shot in either the `1st` cell or, after a first-serve fault, the `2nd` cell. The source instructions explicitly make shot direction, return depth, and several position modifiers optional.

**ENGINEERING DECISION:** Parser success and attribute coverage are separate quantities. A validly parsed forehand without a direction code contributes to forehand usage but not to a directional denominator.

**OPEN QUESTION:** How often chart-specific exceptions, undocumented symbols, and internally inconsistent sequences prevent safe extraction on the complete snapshot.

## Point-cell structure

The following is a descriptive grammar derived from the official Instructions sheet. It is not yet an executable grammar.

```text
point_cell        := exceptional_point | let* serve rally* terminal?
exceptional_point := "S" | "R" | "P" | "Q" | "V"
let               := "c"
serve             := serve_direction serve_modifier? serve_fault?
serve_direction   := "0" | "4" | "5" | "6"
serve_modifier    := "+"
serve_fault       := "n" | "w" | "d" | "x" | "g" | "e" | "!"
rally             := shot_type shot_modifier* shot_direction? return_depth?
shot_type         := "f" | "b" | "r" | "s" | "v" | "z" | "o" | "p"
                   | "u" | "y" | "l" | "m" | "h" | "i" | "j" | "k"
                   | "t" | "q"
shot_modifier     := "+" | "-" | "=" | ";" | "^"
shot_direction    := "0" | "1" | "2" | "3"
return_depth      := "0" | "7" | "8" | "9"
terminal          := "*" | error_detail? ("@" | "#") | "C"
error_detail      := "n" | "w" | "d" | "x" | "e" | "!"
```

The executable parser must not assume this simplified production resolves every ordering ambiguity. It must preserve the original string and return explicit errors or warnings for unsupported sequences.

## Semantic codes

### Serve

| Code | Meaning |
|---|---|
| `4` | Wide serve |
| `5` | Body serve |
| `6` | Serve down the T |
| `0` | Unknown serve direction |
| `c` | Let; may repeat before the serve |
| `+` | Serve-and-volley attempt when attached to the serve |

### Rally shot types

| Family | Forehand | Backhand |
|---|---|---|
| Groundstroke | `f` | `b` |
| Slice/chip | `r` | `s` |
| Volley | `v` | `z` |
| Overhead | `o` | `p` |
| Drop shot | `u` | `y` |
| Lob | `l` | `m` |
| Half-volley | `h` | `i` |
| Swinging volley | `j` | `k` |

`t` represents a trick shot and `q` an unknown shot type.

### Direction and depth

| Code | Context | Meaning |
|---|---|---|
| `1` | Rally direction | Toward a right-hander's forehand / left-hander's backhand side |
| `2` | Rally direction | Middle |
| `3` | Rally direction | Toward a right-hander's backhand / left-hander's forehand side |
| `0` | Direction/depth | Unknown |
| `7` | Return depth | Service boxes |
| `8` | Return depth | Between service line and baseline, nearer service line |
| `9` | Return depth | Nearer baseline |

Direction is destination-relative, not an intrinsic crosscourt/down-the-line label. Deriving crosscourt or down-the-line requires the hitter's side, opponent handedness, and shot sequence; the parser must preserve the source direction before any such transformation.

### Endings and modifiers

| Code | Meaning |
|---|---|
| `*` | Winner; on a bare serve, ace |
| `#` | Forced error; on a bare serve, unreturnable |
| `@` | Unforced error |
| `n`, `w`, `d`, `x`, `e`, `!` | Net, wide, deep, wide-and-deep, unknown, or shank error detail |
| `+` | Approach shot when attached to a rally shot |
| `-` / `=` | Shot taken at net / baseline contrary to the default inferred from shot type |
| `;` | Net cord |
| `^` | Stop/drop volley |
| `C` | Player incorrectly stopped play for a challenge |

### Exceptional whole-point codes

| Code | Meaning |
|---|---|
| `S` | Unobserved point awarded to server |
| `R` | Unobserved point awarded to returner |
| `P` | Point penalty against server |
| `Q` | Point penalty against returner |
| `V` | Time violation causing loss of first serve |

`S`, `R`, `P`, and `Q` preserve scoring continuity but do not support ordinary shot-behavior
denominators. When `V` appears in the first-serve cell and the second-serve cell contains notation,
the second serve remains an observed attempt; parser v0.2 preserves it while treating the first
serve as lost to the time violation.

## Parser contract

Each parsed cell should retain:

- Raw notation and source position (`1st` or `2nd`).
- Serve direction, fault detail, let count, and serve-and-volley flag where observed.
- Ordered shots with type, direction, return depth, position modifiers, and point-ending annotations.
- Whether every requested attribute was observed, unknown, optional-but-absent, or invalid.
- Exceptional whole-point status.
- Structured warnings and a fatal parse error when safe tokenization is impossible.
- Parser version and source snapshot identifier.

### Field-aware partial validity

**ENGINEERING DECISION:** `mcp-parser-v0.2-draft` preserves only the successfully decoded prefix when
a later token is unsupported. The cell remains invalid as a whole. Component states distinguish
`observed`, `unknown`, `absent`, `partial`, `invalid`, and `not_applicable` values for serve
direction, serve-and-volley, rally, and outcome.

An unsupported rally extension may therefore leave serve direction `observed` while marking rally
`partial` and outcome `invalid`. A malformed serve prefix leaves every downstream component
`invalid`. This contract permits family-specific coverage measurement without silently accepting
undocumented grammar.

The parser must be deterministic, side-effect free, and tested independently from feature calculations.

## Observed deviations requiring review

The initial full-corpus pass found recurring strings outside the simplified workbook grammar:

- Depth-like `7`/`8`/`9` codes after shots other than the return, despite the Instructions sheet documenting return depth specifically.
- Position/net-cord modifiers placed after direction or depth as well as immediately after shot type.
- Error-detail codes placed after `@`/`#` in some charts instead of before the terminal marker.
- Bare fault/error symbols without a serve-direction prefix.
- A small number of spaces, uppercase letters, punctuation, and annotations outside the documented alphabet.

**ENGINEERING DECISION:** `mcp-parser-v0.2-draft` rejects these forms and reports their exact failure position while retaining independently safe prefix fields. They must not be normalized until examples are reconciled with source history, aggregate output, or an explicit parser decision. A later parser version may accept a well-supported extension while preserving a warning that distinguishes it from the workbook grammar.

## Validation plan

1. Build hand-authored fixtures from examples in the official Instructions sheet.
2. Add real fixtures covering lets, faults, serve-and-volley, optional directions, return depth, modifiers, winners, forced/unforced errors, and exceptional points.
3. Lexically profile undocumented characters and whitespace before deciding normalization rules.
4. Compare parser-derived match totals with MCP Overview, ServeDirection, ShotTypes, Rally, ReturnDepth, and NetPoints aggregates.
5. Manually inspect disagreements; do not optimize agreement by silently discarding records.
6. Report parse success separately from coverage of direction, depth, error detail, and net-position attributes.

## Stop conditions

Block a candidate feature when its denominator cannot distinguish absent, unknown, invalid, and not-applicable notation; when parser/aggregate disagreement is unexplained; or when coverage varies enough by player/era to make comparison misleading.
