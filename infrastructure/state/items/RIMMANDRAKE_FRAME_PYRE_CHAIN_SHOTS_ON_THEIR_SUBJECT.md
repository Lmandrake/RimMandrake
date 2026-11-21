# RIMMANDRAKE_FRAME_PYRE_CHAIN_SHOTS_ON_THEIR_SUBJECT

Caused by RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO (Stage 6 visit 2, 2026-11-20). Class HARNESS.

## spec

src/RimMandrake/Pyrelands/validation.py calls a bare `t.screenshot()` (no rect) 19 times. Those captures show whatever
the camera last framed. On visit 2, `giant_furnace_beast_1795234554.png` and `herd_follows_two_day_old_burn_1795234568.png`
are the same frame: a grass field and a concrete pad near the map's east edge (the right fifth of the image is off-map),
with no furnace-beast and no herd in it. The sky captures of cinderfall/three_skies were taken on that same frame too.
Small copies: design/concepts/Pyrelands/version/in_game/visit_2/screenshots/giant_furnace_beast_1795234554.jpg and
herd_follows_two_day_old_burn_1795234568.jpg. Suite bars marked visual read "state PASS, not yet judged": the judge
(northstar_driver/judge_cli.py) is shown these frames, so a visual verdict can be made on a picture without its subject.

Fix: each visual component frames its subject (`t.screenshot(rect=...)` on the pad, the pawn's cell, or the herd's
bounding box), as the captures that pass a rect already do (ashwallow_domed ..._cell_rect is framed right).

## verify

Each capture a visual bar names shows that bar's subject.

## criteria

- No visual component captures without a rect or a subject cell.

## Acceptance test

Offline: `grep -c "t.screenshot()" src/RimMandrake/Pyrelands/validation.py` prints 19 now (seen 2026-11-20 on
a7d25d9f33); green prints 0 (each call names a rect or a subject).

## refs

file: src/RimMandrake/Pyrelands/validation.py
file: src/RimMandrake/Utils/northstar_driver/judge_cli.py
