# Scene look judge brief: a fresh player's eyes on a staged in-game scene

For judges that did NOT build the work, looking at a staged RimWorld scene (screenshot or crops), not a sprite sheet.
Sprite and art sheets use `design/RimMandrake/art_judge_brief.md`. Why this exists: `standing_rulings.md` §Nothing
reaches the owner unread; the per-station zoomed stare in `skills/rimworld-live-review/SKILL.md` (walkthrough
section). The owner's words (2026-11-12): *"You are human player looking at this test from a game playing point of
view... first, does anything look odd? Then, look specifically at (whatever the test required)."* and *"front-back
ordering is always to be checked against expectations, as are appropriate relative sizes and recognizable appearance
wrt what the objects are supposed to be (e.g. a ladder that suddenly looks like a waffle fails no matter its size,
layer, and behavior)."*

## The owner's method: a matrix, pre-looked by a fresh open-question judge
The owner looks at MATRIX scenes: one prepared cell (every fitting and facing, goods inside) replicated over the
variables that matter (e.g. pit depth x water fill), with a grid key. Lesson
`infrastructure/state/lessons/20261112T184403Z-CONDUCTOR-owner-looks-are-matrix-not-one.md`. Before he sees it, a
fresh judge asked an open question pre-looks it (pass 1). A different judge then runs the checklist (pass 2). Two
judges, never one judge doing both: once a judge has a checklist, it looks only where the checklist points.

## What the presenter gives each judge
- The image(s): the uncropped frame AND zoomed crops of every cell (one crop per cell, labelled, a pawn or a known
  vanilla object in or beside at least one crop for scale). If a matrix, a grid key: the variable values of each cell
  (e.g. "bottom: depth 4, water at the brim"), nothing more.
- Never what was changed, fixed, measured or passed. A judge told "the hose was fixed" checks the hose and stops looking.

## Pass 1: ONE fresh judge, open question, no checklist
Give the images, the grid key and this question only: *"You are a RimWorld player who has just walked up to this part
of the map. Does anything look odd?"* No checklist, no expectation sentence, no list of things to check. The judge
describes what it sees in each cell in plain words and names anything odd, and where. In the 2026-11-12 calibration
both naive judges (no checklist, no expectation) caught the owner's fault, the north ladder drawn behind the wall art in the
brim pit (`D:\ClaudeWork\rimmandrake\conductor\scene_judge_20261112\RESULT.md`).

## Pass 2: a DIFFERENT fresh judge, checklist, after pass 1
A judge that did not run pass 1 and does not see its answer. It gets the same images and grid key plus ONE sentence
of expectation: what a player should see. The sentence and grid key must cover EVERY cell, including dry, empty or
brim-full reference cells, or the judge files the references as WRONG (calibration 2026-11-12).
1. Comparison first: which cell is the odd one out against its neighbours or the known-good reference (the same
   object in a dry or vanilla cell)? An object drawn differently in one cell, with no reason in the expectation, is a finding.
2. Front-back ordering vs expectation: what should be in front (a fitting over the wall it hangs on, water over the
   submerged part, a pawn over the floor) and is it?
3. Relative size vs a human pawn.
4. Recognisable as what it is meant to be (a ladder that looks like a waffle fails whatever its size, layer, behaviour).
5. Liquid and waterline: does the liquid meet each object at a believable level?
6. Clipping, cut-off, or floating parts. Where an object stops at an edge (waterline, wall band, rim), say which
   thing is in front and whether the object should carry on past it; check against the same object in the reference cell.
7. Consistency across N/S/E/W facings of the same object.
8. Anything missing or duplicated.
9. UI on screen: dialogs, red letters, error text, dev palettes covering the subject.
10. Dead or downed pawns, fires, filth with no cause in the scene.

## Output, per cell (both passes)
`cell: EXPECTED | ODD | WRONG | COULD NOT SEE` plus the object named and where (e.g. "left cell, east reel,
the part between rim and water"). COULD NOT SEE is an allowed answer: too small, too zoomed out or covered is a
refusal, never a pass. Then one line: the single thing a player would notice first.

### Refusal record: every ODD, WRONG or COULD NOT SEE is one (owner, 2026-11-12)

*"ANY refusals must be as detailed as the evidence they are rejecting and include the fixes and paths towards passing
that are attainable and reasonable. It also MUST include assessment of the acceptance criteria themselves."* Beside
the lines above, return a `contract` block in the refusal contract's form
(`design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md` section 1): `clause` is the cell (pass 1) or
`<cell>/<checklist number>` (pass 2), `evidence` the crop you looked at, and every EXPECTED cell goes in `passed`.

```json
{"contract": {"item": "<ledger item>", "family": "scene_look_judge_brief", "sha": "<save or capture sha>",
  "passed": [{"clause": "B2", "evidence": ["crop_B2.png"]}],
  "refusals": [{"clause": "B3", "criterion_hash": "<refusal_contract.criterion_hash of the cell's line>",
    "evidence": ["crop_B3.png"], "observed": "the east reel's lower half is cut off above the water line",
    "would_pass": "the whole reel, rim to water, is drawn above the water surface in a crop at zoom 1",
    "smallest_fix": {"what": "re-shoot cell B3 at zoom 1 with the camera centred on the east reel",
                     "attainable": "yes", "cost": "rerun"},
    "criterion_verdict": "sound",
    "criterion_why": "A player looking at this cell expects to see the whole reel, and the scene can show it.",
    "new_since": "first"}]}}
```

COULD NOT SEE is a refusal whose `smallest_fix` is the re-shot crop (cost `rerun`). The presenter writes `given` (the
crops and the cell lines it gave you) and runs `python3 src/RimMandrake/rimflow/refusal_contract.py submit <file>
--given <given.json>` before any refusal sends a builder back. A malformed record is itself refused and re-asked once; a
second marks this brief FAILED and raises `REFUSAL_NOTHING_COULD_EVER_PASS`. A cell line you judge `flawed` or
`unattainable` goes to a neutral criteria fixer, never back to the builder.

## A builder's "by design" never overrules a judge's doubt
Every ODD or WRONG from either pass stands until one of two things answers it: the owner rules on it, or a read of the
game state settles it (the cell's true fill, the fitting's drawn cut line, the def), with the reading written beside
the doubt. The builder saying "that is by design", and the presenter agreeing, is not an answer. In the 2026-11-12
calibration the briefed judge's "pit6: WRONG ... the ladder is hidden except for its hooks" was first scored a false
alarm because the builder's staging note said "at brim nothing shows". That pit held the owner's fault.

## Missed by the judge, caught by the owner (add a line each time)
| date | scene | what he saw | what our proof said |
|---|---|---|---|
| 2026-11-12 | FlowWorks pit submerge scene, 2 m water (`RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL`) | north ladder drawn behind the pit wall art (south ladder and 1 m correct) | 21/21 live rows PASS; no look at ordering. Calibration afterwards (n=1): both naive judges and the briefed judge flagged the brim pit's ladder; the briefed judge's doubt was then dismissed as "by design". `D:\ClaudeWork\rimmandrake\conductor\scene_judge_20261112\RESULT.md` |

## Keep the exact image judged (owner, 2026-11-12)

*"Please save that precise ingested image ... Asking me to judge on precisely the images they took for their own judgements is the very best comparison."* Every judge pass saves, beside its verdict, the exact file(s) it was given (same pixels, no re-encode), and its verdict names each file with its pixel size and how it was made from the source (crop box, scale factor). A showing to the owner lists those files first. A crop that was only enlarged holds no more detail than its source: say the source pixel size of the object judged.
