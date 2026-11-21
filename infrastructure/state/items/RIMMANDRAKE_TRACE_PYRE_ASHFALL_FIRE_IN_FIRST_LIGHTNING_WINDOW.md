# RIMMANDRAKE_TRACE_PYRE_ASHFALL_FIRE_IN_FIRST_LIGHTNING_WINDOW

Caused by RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO (Stage 6 visit 2, 2026-11-20). Class HARNESS (presumed).

## spec

`cinderfall_lightning` (sc_three_skies, bar three_skies "lightning strikes under cinderfall and none under ash fall")
FAILED: new fires per 1000 ticks, cinderfall [1, 12, 0, 9, 0, 0, 31, 13, 1, 24] (91), ash fall [1, 0, 0, 0, 0, 0, 0, 0,
0, 0] (1) (`design/concepts/Pyrelands/version/in_game/visit_2/evidence/pv2_cinderfall+blackrain.json`). The row's own def leg PASSED: RM_FE_Weather_AshFall carries no
lightning event maker. Visit 1 read the same pattern ("none under ash fall after its first window"). So the one fire is
presumed not lightning: the instrument counts every new Fire. The row runs AshFall first, after SKY_SETTLE_TICKS and an
extinguish, under `_isolate`. The source is not traced.

Trace it: read the first window's new Fire (position, the thing it burns, the tick) and what lit it. If it is a strike,
the def or the weather blend is wrong (MOD). If it is a re-ignition or another mod's fire, the row must count strikes
(WeatherEvent_LightningStrike) or exclude what it did not cause (HARNESS).

## verify

The first window's fire is named, and the row rerun reads a verdict that the cause supports.

## criteria

- The fire's cause is recorded.
- The repaired row FAILs on a planted strike under ash fall and PASSes on the real build.

## Acceptance test

Live only. Red now: `... cli.py run ... --chains cinderfall` reads cinderfall_lightning FAIL, ash fall total 1
(seen 2026-11-20). Green: the row PASS with the cause of any ash-fall fire named in its note.

## refs

file: src/RimMandrake/Pyrelands/validation.py
def: WeatherDef/RM_FE_Weather_AshFall
def: WeatherDef/RM_FE_Weather_Cinderfall
