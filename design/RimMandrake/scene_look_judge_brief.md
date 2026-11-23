# Scene look judge brief: a fresh player's eyes on a staged in-game scene

This brief is for a judge that did NOT build the work. The judge looks at a staged RimWorld scene (a screenshot or
crops), not at a sprite sheet. Sprite and art sheets use `design/RimMandrake/art_judge_brief.md`.

Why this brief exists:

- `standing_rulings.md` §Nothing reaches the owner unread.
- The per-station zoomed stare in `skills/rimworld-live-review/SKILL.md` (walkthrough section). That stare is a zoomed
  capture of every station, with a close look at each capture.

The owner's words (2026-11-12): *"You are human player looking at this test from a game playing point of
view... first, does anything look odd? Then, look specifically at (whatever the test required)."* and *"front-back
ordering is always to be checked against expectations, as are appropriate relative sizes and recognizable appearance
wrt what the objects are supposed to be (e.g. a ladder that suddenly looks like a waffle fails no matter its size,
layer, and behavior)."*

## The owner's method: a matrix, pre-looked by a fresh open-question judge
The owner looks at MATRIX scenes. In a matrix scene, one prepared cell (every fitting and facing, goods inside) is
replicated over the variables that matter (e.g. pit depth x water fill). A grid key goes with the scene. Lesson:
`infrastructure/state/lessons/20261112T184403Z-CONDUCTOR-owner-looks-are-matrix-not-one.md`.

Before he sees a matrix scene, two judges look at it:

- Pass 1: a fresh judge, asked an open question, looks at the scene first (the pre-look).
- Pass 2: a different judge then runs the checklist.

Use two judges, never one judge doing both. The reason: once a judge has a checklist, that judge looks only where the
checklist points.

## What the presenter gives each judge
The presenter is the agent that gives the images to the judges. The presenter also stages each frame (see the reset
rule below).

- The image(s): the uncropped frame AND zoomed crops of every cell. Give one crop per cell, labelled. Put a pawn or a
  known vanilla object in or beside at least one crop, for scale.
- If the scene is a matrix, give a grid key: the variable values of each cell (e.g. "bottom: depth 4, water at the
  brim"), nothing more.
- Never tell a judge what was changed, fixed, measured or passed. A judge told "the hose was fixed" checks the hose and
  stops looking.
- Resetting a scene is harness housekeeping (owner, 2026-11-17: *"We shouldn't be judging Test Reset as a mod
  deliverable."*). Stage each frame from the save taken before the scene. A judge can call a leftover of an earlier
  scene ODD or WRONG (its filth, fire, scar or staged object). That answer is the presenter's reset to redo. It is
  never a finding against the mod, a Problem or a Polish entry.

## Pass 1: ONE fresh judge, open question, no checklist
Give the images, the grid key and this question only: *"You are a RimWorld player who has just walked up to this part
of the map. Does anything look odd?"* Give no checklist, no expectation sentence and no list of things to check.

The judge describes what it sees in each cell in plain words. The judge names anything odd, and where it is.

In the 2026-11-12 calibration, both naive judges (no checklist, no expectation) caught the owner's fault. The fault
was the north ladder drawn behind the wall art in the brim pit
(`D:\ClaudeWork\rimmandrake\conductor\scene_judge_20261112\RESULT.md`).

## Pass 2: a DIFFERENT fresh judge, checklist, after pass 1
The pass-2 judge did not run pass 1 and does not see the pass-1 answer. The pass-2 judge gets the same images and
grid key, plus ONE sentence of expectation: what a player should see.

The sentence and the grid key must cover EVERY cell, including dry, empty or brim-full reference cells. If they do not,
the judge files the reference cells as WRONG (calibration 2026-11-12).

1. Comparison first: which cell is the odd one out against its neighbours or the known-good reference (the same
   object in a dry or vanilla cell)? An object drawn differently in one cell, with no reason in the expectation, is a
   finding.
2. Front-back ordering vs expectation: what should be in front (a fitting over the wall it hangs on, water over the
   submerged part, a pawn over the floor), and is it in front?
3. Relative size vs a human pawn.
4. Recognisable as what it is meant to be (a ladder that looks like a waffle fails whatever its size, layer, behaviour).
5. Liquid and waterline: does the liquid meet each object at a believable level?
6. Clipping, cut-off, or floating parts. Where an object stops at an edge (waterline, wall band, rim), say which
   thing is in front. Say whether the object should carry on past the edge. Check against the same object in the
   reference cell.
7. Consistency across N/S/E/W facings of the same object.
8. Anything missing or duplicated.
9. UI on screen: dialogs, red letters, error text, dev palettes covering the subject.
10. Dead or downed pawns, fires, filth with no cause in the scene.

## When the look is enough, and when to stop (owner, 2026-11-19)
`standing_rulings.md` §Touching code has a cost; if you see it, do it: every judging brief states its stopping level.

- Enough: every cell has one answer (EXPECTED, ODD, WRONG or COULD NOT SEE), with the object and the place. Then the
  judge stops. The judge does not look for more.
- Each pass is one look. A look after a repair re-judges only the cells that were ODD, WRONG or COULD NOT SEE. That
  look raises something new only where the repair itself changed what the cell shows.
- There is no third look. What is still open goes to the owner as a short list (§The judge refuses flaws, not
  polish, Rule 2).
- The danger that this count of looks guards: a judge that is asked again never stops (Pyrelands stage 5 took nine
  recorded looks, 2026-11-17).
- Polish route: the judge can call a detail minor (not odd, and not the thing a player would notice first). A minor
  detail is one line in the output, marked polish. A polish line is not a refusal, files no ticket and blocks nothing.
- This stop rule is UNTESTED until a calibration run checks it (`RIMMANDRAKE_CALIBRATE_JUDGE_STOP_RULES_WORDS_UNTIL_RUN`).

## North-star must-show bars: the same two passes, one entry point
Owner pick 11 (2026-11-12; OWNER.jsonl tsn 1794524114165680240): one item, one judge
(`RIMMANDRAKE_FOLD_FRAME_JUDGE_INTO_PRELOOK`). THIS brief judges the frames of a north-star run, through ONE entry
point: `src/RimMandrake/Utils/northstar_driver/judge_cli.py`. cli.py and `src/RimMandrake/Graffiti/northstar_full.py`
call `judge_cli.py` after a run. `judge_cli.py` is not a second judge.

- Pass 1: before anyone asks about a bar, one fresh judge per capture gets the open question above.
  That judge gets nothing else (no bar id, no bar text, no checklist).
  - A pass-1 ODD or WRONG is a doubt. `judge_cli.py` lists the doubt on every bar row judged on that capture (`doubts`, and
    "pass-1 doubt" in the row's evidence).
  - Like every doubt here, a pass-1 doubt stands until the owner rules on it or a state read settles it.
  - A pass-1 doubt does not change the bar's status, because a bar passes or fails on its own promise
    (`standing_rulings.md` §The judge refuses flaws, not polish).
  - `judge_cli.py` counts COULD NOT SEE, an unreadable answer or a judge that could not run as "could not look",
    with its cause. A "could not look" is never a doubt and never a verdict.
- Pass 2: a different fresh judge that never sees pass 1. Its one sentence of expectation is the must-show bar's text,
  verbatim (`src/RimMandrake/Utils/modcheck/judge.py`'s statement prompt: YES, NO or UNJUDGEABLE; UNJUDGEABLE is never
  a pass). That verdict is the bar's verdict.
- The bar's state result still gates first: a state FAIL stays FAIL whatever the frame shows.
- Input, narrower than a matrix look: the judge judges each claim on ONE capture, the component's last shot. When the
  component has a framed `__cell_rect` crop, the judge gets that crop. The capture tool writes that crop. The judge does not get the uncropped frame, the labelled crops or the grid key that a presenter gives
  for a matrix scene. A north-star component frames one subject. A matrix scene still goes through the presenter route
  above.
- Output, also narrower: pass 1 answers one look per capture, and pass 2 answers YES / NO / UNJUDGEABLE per bar. Neither
  pass gives per-cell lines.
- Nothing on this route has its own place to judge recognisability (checklist item 4). So on this route, a "looks like
  a waffle" answer is a pass-1 doubt, unless the bar itself promises the look.
- The refusal-contract record for a north-star frame FAIL is not written yet
  (`RIMMANDRAKE_EMIT_REFUSAL_RECORDS_FROM_NORTHSTAR_FRAME_FAILS`).
- The exact image judged is the run's own capture file. The judge record names the file with its sha256, pixel size and
  crop note. `judge_cli.py` judges a byte copy and deletes only the copy.
- On this route the crop is the capture tool's own `__cell_rect` file, and the judge never enlarges it. So its
  provenance is that file and the source that it names. The judge record holds no crop box or scale factor. (The section "Keep
  the exact image judged" below asks a presenter who crops for them.)
- Calibration: the fold did not change pass 2's prompt. Pass 1 is new and has no consequence beyond the doubts that
  it lists. This brief stays UNTESTED in `infrastructure/state/judge_calibration.json` until its planted cases run
  (`RIMMANDRAKE_SEED_SCENE_LOOK_CALIBRATION_BRIM_PIT_PAIR`).

## Output, per cell (both passes)
`cell: EXPECTED | ODD | WRONG | COULD NOT SEE` plus the object named and where it is (e.g. "left cell, east reel,
the part between rim and water").

COULD NOT SEE is an allowed answer. Too small, too zoomed out or covered is a refusal, never a pass.

Then write one line: the single thing a player would notice first.

### Refusal record: every ODD, WRONG or COULD NOT SEE is one (owner, 2026-11-12)

*"ANY refusals must be as detailed as the evidence they are rejecting and include the fixes and paths towards passing
that are attainable and reasonable. It also MUST include assessment of the acceptance criteria themselves."*

Beside the lines above, return a `contract` block in the form of the refusal contract
(`design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md` section 1):

- `clause` is the cell (pass 1), or `<cell>/<checklist number>` (pass 2).
- `evidence` is the crop that you looked at.
- Every EXPECTED cell goes in `passed`.

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

COULD NOT SEE is a refusal whose `smallest_fix` is the re-shot crop (cost `rerun`).

Before any refusal sends a builder back, the presenter does two things:

- The presenter writes `given`: the crops and the cell lines that the presenter gave you.
- The presenter runs `python3 src/RimMandrake/rimflow/refusal_contract.py submit <file> --given <given.json>`.

A malformed record is itself refused and re-asked once. A second malformed record marks this
brief FAILED and raises `REFUSAL_NOTHING_COULD_EVER_PASS`. If you judge a cell line `flawed` or `unattainable`, a
neutral criteria fixer gets that cell line. The cell line never goes back to the builder.

## A builder's "by design" never overrules a judge's doubt
Every ODD or WRONG from either pass stands until one of two things answers it:

- the owner rules on it; or
- a read of the game state settles it (the cell's true fill, the fitting's drawn cut line, the def), with the reading
  written beside the doubt.

The builder saying "that is by design", and the presenter agreeing, is not an answer. In the 2026-11-12 calibration,
the briefed judge said "pit6: WRONG ... the ladder is hidden except for its hooks". That answer was first scored a
false alarm, because the builder's staging note said "at brim nothing shows". That pit held the owner's fault.

## Missed by the judge, caught by the owner (add a line each time)
| date | scene | what he saw | what our proof said |
|---|---|---|---|
| 2026-11-12 | FlowWorks pit submerge scene, 2 m water (`RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL`) | north ladder drawn behind the pit wall art (south ladder and 1 m correct) | 21/21 live rows PASS; no look at ordering. Calibration afterwards (n=1): both naive judges and the briefed judge flagged the brim pit's ladder; the briefed judge's doubt was then dismissed as "by design". `D:\ClaudeWork\rimmandrake\conductor\scene_judge_20261112\RESULT.md` |

## Keep the exact image judged (owner, 2026-11-12)

*"Please save that precise ingested image ... Asking me to judge on precisely the images they took for their own judgements is the very best comparison."*

- Every judge pass saves, beside its verdict, the exact file(s) that it was given (same pixels, no re-encode).
- The verdict names each file, with its pixel size.
- The verdict also says how each file was made from the source (crop box, scale factor).
- A showing to the owner lists those files first.
- A crop that was only enlarged holds no more detail than its source. So say the source pixel size of the object
  judged.
