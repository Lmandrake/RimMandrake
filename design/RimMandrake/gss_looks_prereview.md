# Gimme Some Slack: looks pre-review recipe (2026-10-06)

This is the GSS instance of the contact-board method in `rich_screenshot_art_prereview.md`. The board is staged in game,
captured off screen in one frame, cut into one crop per subject, and passed through the cheap checks and then one
batched image read. After that, the owner's policy decides what happens to each finding.

**Status:** built and selftested offline. **Never run live.** The companion DLL has to be deployed with the game down first.

## Owner policy (2026-10-06, typed)

> *"(1) plus regen the art if you already know how, only go to human if you need judgement to fix it"*

`src/RimMandrake/Utils/artboard/autofix.py` puts every finding into exactly one class:

| class | what it covers | what happens |
|---|---|---|
| STAGING | a refused op, `OFF_CELL`, `OUT_OF_FRAME`, `BAD_BOARD` | Fixed silently: re-stage (nudge the origin, try another rotation, or fix the recipe) and re-capture. A staging fault hides the art, so it always comes first. |
| ART_FIX | `MISSING_TEXTURE`, `HOLE`, `TRUNCATED`, or a catalogued draw-code defect | Fixed without asking. Search the art ledger first (`artpipe_state.py find`), then regenerate or patch, then re-run the board. |
| JUDGEMENT | `WRONG_COLOUR`, `IDENTICAL`, `REF_DRIFT`, `OVERFLOW`, `EMPTY`, any vision FAIL or UNSURE, a catalogued design question, any check it does not know | Sent to the owner board, and nothing else is. |

The catalogue (`autofix.KNOWN`) currently holds two entries:
- `cord_unpowered` is **ART_FIX**. GPT A19 confirmed that the dark power strip is drawn at aspect 1. The fix is to draw it at 0.5.
- `hose_behind_uturn` is **JUDGEMENT**. This is the G2 outlet-blend kink, and the fix is a design call.

## The board: `gss_states` (18 subjects, 46×45 cells, 2208×2160 px at 48 px/cell)

| group | subjects | what each must show |
|---|---|---|
| cords (7×5) | `cord_powered`, `cord_unpowered`, `cord_wall_end`, `cord_tee`, `cord_cut_live` | lit vs dead ends, a wall stub (never on top of the wall), a junction, a live frayed tip |
| reels (3×3) | `reel_stored_{Scrapper,Industrial,Modern,Futuristic}` | each style reads as itself, with the hose stored |
| hoses (12×6) | `hose_ahead_flat`, `hose_ahead_flowing`, `hose_behind_uturn`, `hose_end_{open,nozzle,cap}` | leaves through the outlet; plump when flowing; no kink on the U-turn; the three ends |
| spans (12×4) | `span_up`, `span_cut`, `span_bracket` | a sag with a shadow; fallen halves; landing on the bracket's insulator |

Things are spawned by `jawa/artboard_stage` (kind=thing). The GSS state comes after that, from `gss_*` ops run by the new
`jawa/gss_stage` (in `JawaBenchGssPlaytest.cs`): charge, lay, flow, end, look, link, cut and ticks.
`artboard/recipes.py plan()` sends `gss_*` ops to `gss_ops`. `artboard/live.py` runs them after the subjects phase and
merges any refusals, so a refused subject is dropped as STAGE_REFUSED and is never captured on the wrong cell.

**Unverified staging:** the wall bracket's rotation and cell (`span_bracket`). If the stager refuses it, autofix sends it
to STAGING as designed.

## Run (live, game up on a GSS tier, bridge held, scratch map)

```
cd src/RimMandrake/Utils
python3 -m artboard.live gss_states --origin <x,z> --dry-run       # the 46x45 rect must be open ground
python3 -m artboard.live gss_states --origin <x,z>                 # stage, plate, board, crops, tier a
# one image read of <out>/vision_mosaic.png with <out>/vision_prompt.md -> answers.txt
python3 -m artboard.autofix <out> --vision answers.txt             # triage.md: staging / art fix / owner
```

Afterwards, save the board as a keeper so the owner can walk it in game (visuals are reviewed in game, not in browser sheets).
