# RIMMANDRAKE_MEASURE_PYRE_ASHFALL_DIMMING_BY_SKY_NOT_GLOW

Caused by RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO (Stage 6 visit 2, 2026-11-20).

## spec

`sc_ash_ground` (bar `ash_ground_and_blowing_ash`: "during ash fall the map dims") has the row
`ash_fall_vs_clear_by_hour` in `src/RimMandrake/Pyrelands/validation.py` (`_ten_ground_deep_ash`). It compares
`jawa/glow_at` `skyGlow` (SkyManager.CurSkyGlow) under ash fall and under Clear at matched hours. Visit 2 measured
`1.0` against `1.0` at 13.6h (evidence `design/concepts/Pyrelands/version/in_game/visit_2/evidence/pv2_b.json`).

CurSkyGlow is `Math.Min(sunGlow, WeatherDef.maxGlow)` (WeatherWorker.CurSkyTarget). `RM_FE_Weather_AshFall` sets no
`maxGlow` (default 1). It dims the map through `skyColorsDay` (sky 0.62,0.58,0.54). SkyManagerUpdate puts that colour on
`MatBases.LightOverlay.color`, which multiplies the whole rendered map. So the row reads a channel that the mod does not
use. Class HARNESS (the instrument). No bridge tool reads the sky colour today, so the repair was not made in the sitting.

Decide one of two:
- HARNESS repair: add a JawaBench read of `map.skyManager.CurSky.colors.sky` (or `MatBases.LightOverlay.color`) and
  compare its luminance (times skyGlow) by hour. This is the obvious answer: weathers dim through the sky colour in vanilla.
- MOD: if the design wants ash fall to lower gameplay light (work speed, mood), set `maxGlow` on the WeatherDef. That is a
  Divergent change for the next version, not this one.

## verify

The repaired row runs on the real build and on a planted fault, in one sitting.

## criteria

- Real build: ash-fall sky luminance is below Clear's at every matched hour (10h to 14h).
- Planted fault: AshFall's `skyColorsDay` set to vanilla Clear's makes the row FAIL.

## Acceptance test

Live only (needs the game), so no offline oracle. Red now:
`python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains ground_deep_ash`
reads `ash_fall_vs_clear_by_hour` FAIL ("ash-fall light 1.0 is not below clear 1.0"), seen 2026-11-20 on mod_sha 01853a05a6.
Green on a fix: the same row PASS, and FAIL with the planted sky colour.

## refs

file: src/RimMandrake/Pyrelands/validation.py
file: src/RimMandrake/Pyrelands/Defs/WeatherDefs/AshFall.xml
def: WeatherDef/RM_FE_Weather_AshFall
