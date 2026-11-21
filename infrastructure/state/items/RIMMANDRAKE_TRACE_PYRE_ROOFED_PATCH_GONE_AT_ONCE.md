# RIMMANDRAKE_TRACE_PYRE_ROOFED_PATCH_GONE_AT_ONCE

Caused by RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO (Stage 6 visit 2, 2026-11-20). Class SITE (presumed,
unproven). sc_roof_withers decides no bar.

## spec

`roof_withers` (design/concepts/Pyrelands/version/in_game/visit_2/evidence/pv2_roof_withers.json):
- `roof_withers` (gate on) PASS: the roofed patch A lost HP every hour (700 -> 675 -> 650 ...) with the
  RM_WithersUnderRoof line shown; the open patch B kept every plant. That is the mod's mechanism, visibly.
- `gate_off_kills_nothing` FAIL: with pyrelandsEnabled off, patch A kept hpA 700 and no wither line every hour, then
  went from 25 plants to 0 between two hourly reads near hour 41; B kept 25 throughout; the row's fire count read 0.
A loss of every plant at once, with HP unchanged up to it and no line, is not the mod's wither. Candidates: the roof
(RoofConstructed set by jawa/set_roof_batch with no walls under it may collapse), heat in the roofed cells, or a
vanilla plant rule. The row does not record which.

## verify

Rerun the gate-off pair and read, the hour the plants go: the roof cells, the cell temperature, and what destroyed them.

## criteria

- The cause is named. If the scene caused it (an unsupported roof), the scene is repaired and the row is shown FAIL on a
  planted wither (gate on) and PASS on the gate-off build reading.

## Acceptance test

Live only. Red now: `... cli.py run ... --chains roof_withers` reads gate_off_kills_nothing FAIL "A [25, ... 25, 0, 0
...]" (seen 2026-11-20). Green: PASS, or a FAIL whose note names a mod cause.

## refs

file: src/RimMandrake/Pyrelands/validation.py
file: src/RimMandrake/Pyrelands/Source/CompWithersUnderRoof.cs
