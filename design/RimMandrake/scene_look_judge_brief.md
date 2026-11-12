# Scene look judge brief: a fresh player's eyes on a staged in-game scene

For a judge that did NOT build the work, looking at a staged RimWorld scene (screenshot or crops), not a sprite sheet.
Sprite and art sheets use `design/RimMandrake/art_judge_brief.md`. Why this exists: `standing_rulings.md` §Nothing
reaches the owner unread; the per-station zoomed stare in `skills/rimworld-live-review/SKILL.md` (walkthrough
section). The owner's words (2026-11-12): *"You are human player looking at this test from a game playing point of
view... first, does anything look odd? Then, look specifically at (whatever the test required)."* and *"front-back
ordering is always to be checked against expectations, as are appropriate relative sizes and recognizable appearance
wrt what the objects are supposed to be (e.g. a ladder that suddenly looks like a waffle fails no matter its size,
layer, and behavior)."*

## What the presenter gives you (and must not give you)
- The image(s): the uncropped frame AND zoomed crops of every cell (one crop per cell, labelled, a pawn or a known
  vanilla object in or beside at least one crop for scale). If a matrix, a grid key (which cell is which variable).
- ONE sentence of expectation: what a player should see. Never what was changed, fixed, measured or passed. A judge
  told "the hose was fixed" checks the hose and stops looking. The sentence and grid key must cover EVERY cell,
  including dry, empty or brim-full reference cells, or the judge files the references as WRONG (calibration 2026-11-12).

## Role
You are a RimWorld player who has just walked up to this part of the map. You know the game, not the code.

## Pass 1: open (before any checklist)
For each cell or crop, first DESCRIBE in plain words what you see, object by object, including how each object sits
against the ones around it (on top of, behind, under, cut off by). Only then answer: does anything look odd?

## Pass 2: comparison
Put cells side by side. Which cell is the odd one out against its neighbours, or against the known-good reference
(the same object in a dry or vanilla cell)? An object that is drawn differently in one cell from the others with no
reason in the expectation is a finding.

## Pass 3: checklist (only after passes 1 and 2)
1. Front-back ordering vs expectation: what should be in front (a fitting over the wall it hangs on, water over the
   submerged part, a pawn over the floor) and is it?
2. Relative size vs a human pawn.
3. Recognisable as what it is meant to be (a ladder that looks like a waffle fails whatever its size, layer, behaviour).
4. Liquid and waterline: does the liquid meet each object at a believable level?
5. Clipping, cut-off, or floating parts. Where an object stops at an edge (waterline, wall band, rim), say which
   thing is in front and whether the object should carry on past it; check against the same object in the reference
   cell. A naive judge read a ladder cut off at the waterline as "submerged, fine" (calibration 2026-11-12).
6. Consistency across N/S/E/W facings of the same object.
7. Anything missing or duplicated.
8. UI on screen: dialogs, red letters, error text, dev palettes covering the subject.
9. Dead or downed pawns, fires, filth with no cause in the scene.

## Output, per cell
`cell: EXPECTED | ODD | WRONG | COULD NOT SEE` plus the object named and where (e.g. "left cell, east reel,
the part between rim and water"). COULD NOT SEE is an allowed answer: too small, too zoomed out or covered is a
refusal, never a pass. Then one line: the single thing a player would notice first.

## Missed by the judge, caught by the owner (add a line each time)
| date | scene | what he saw | what our proof said |
|---|---|---|---|
| 2026-11-12 | FlowWorks pit submerge matrix, 2 m water (`RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL`) | north ladder drawn behind the pit wall art (south ladder and 1 m correct) | 21/21 live rows PASS; no look at ordering. Calibration (n=1): naive judges missed it; this brief got PARTIAL, `D:\ClaudeWork\rimmandrake\conductor\scene_judge_20261112\RESULT.md` |

## Keep the exact image judged (owner, 2026-11-12)

*"Please save that precise ingested image ... Asking me to judge on precisely the images they took for their own judgements is the very best comparison."* Every judge pass saves, beside its verdict, the exact file(s) it was given (same pixels, no re-encode), and its verdict names each file with its pixel size and how it was made from the source (crop box, scale factor). A showing to the owner lists those files first. A crop that was only enlarged holds no more detail than its source: say the source pixel size of the object judged.
