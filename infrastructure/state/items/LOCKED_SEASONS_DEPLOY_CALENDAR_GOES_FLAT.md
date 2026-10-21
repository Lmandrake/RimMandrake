# LOCKED_SEASONS_DEPLOY_CALENDAR_GOES_FLAT

Owner, by card 2026-10-20: "Every tile swings ~15 C with the seasons: what should seasons do?" -> "Remove the swing".
Built offline in 3742c2b6bc29 (closes `LOCKED_SEASONS_DECIDE_FIFTEEN_DEGREE_WOBBLE`). Design: `design/RimMandrake/world_physics_audit_2026-10-20.md` §3, §6.

## What shipped (repo only, NOT deployed)
- `src/RimMandrake/CreatureBehaviors/Patches/RM_TidalLock_NoSeasons.xml` — FindMod("Alien Worlds - Tidally Locked") +
  Conditional, replaces the TidallyLocked PlanetTypeDef's `seasonalTempVariationCurve` with 0:0 / 2:0 (non-null, so
  Alien Worlds' FieldPatcher still installs it). `validate_patch.py --live --defs`: 1 match, 0 errors.
- Stored tile temperatures unchanged: LOCKED and original dev saves equal `world/ASHKARR_WORLDMAP_tiles.csv` on all
  21,872 tiles (max |Δ| 0.0). The Scald note stays on `BIOME_PAINT_ONCE_AT_THE_END_1` (line present).

## verify (rides the same deploy as TIDAL_GLOW_DEPLOY_FOLLOWS_THE_SUN; takes effect at load/activation)
- After a load of the LOCKED dev save: `jawa/static_call RimWorld.GenTemperature SeasonalShiftAmplitudeAt 17011` = 0, and
  `AverageTemperatureAtTileForTwelfth` is the same for all 12 twelfths on 17011 and one southern tile.

## 2026-10-20 night: why the patch did nothing on the full list (audit §8)
Measured live: no daily term (outdoor == seasonal at 39 points), seasonal amplitude 8.649 C at 17011 on every sample.
Worldbuilder's prefix on `GenTemperature.SeasonalShiftAmplitudeAt` skips the body (and with it Alien Worlds' curve
transpiler); its postfix applies the axial-tilt curve (Normal). Fix: `RM_TidalNoSeasonsPatch` (Priority.Last postfix,
0 while locked; setting `tidalLockNoSeasons`, default on).

## verify (replaces the one above)
- After deploy + load of `ASHKARR_DEV_START_2026-10-20_PARITY_QUIET`: `jawa/harmony_patches Verse.GenTemperature` lists
  `mandrake.rm.creaturebehaviors.tidalnoseasons` on SeasonalShiftAmplitudeAt; run
  `D:\ClaudeWork\rimmandrake\scratch\seasonsdusk\sample.py`: `seasonal` = 40.4 at every point.

NEXT: deploy CreatureBehaviors (compose biomes) with the game down, load PARITY_QUIET, run sample.py and confirm seasonal = 40.4 flat.
