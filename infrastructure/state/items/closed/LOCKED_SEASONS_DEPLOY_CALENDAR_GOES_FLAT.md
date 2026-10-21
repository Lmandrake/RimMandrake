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

## Deploy state (2026-10-20 night, FOUNDRY)
`deploy_custom_mods.py --compose biomes --apply` ran with the game down: 22 files incl. CreatureBehaviors DLL at
0f76174bd (no-seasons postfix + 12-degree dusk), RM_TidalLock_NoSeasons.xml, the Biomes DLL (river blend e7adc75e3),
the dark-flora plant defs and Gale dust A. VERIFIED in sync. The relaunch did not reach the bridge; the bridge was handed to
the live agent. No load has run on these files yet.

## Measurement design (for the live agent; scripts in D:\ClaudeWork\rimmandrake\scratch\seasonsdusk\)
- `verify.py` (python.exe, RM_DATA_ROOT set): loads PARITY_QUIET, lists patches on SeasonalShiftAmplitudeAt (expect
  `mandrake.rm.creaturebehaviors.tidalnoseasons` priority 0 after WorldbuilderMod MaxValue and rimworld.biomes.core 400),
  confirms the lock (HasAnyPatches 7f.alienworlds.tidallylocked), then jumps the clock FORWARD only
  (time_set_ticks + 2 stepped ticks so TileTemperaturesComp refreshes its 60-tick cache) to 9 points across a day
  (every 7,500 ticks) and days 3/8/15/30.
- Separation: daily + noise = outdoor − seasonal (was 0.000 at all 39 points before the fix: the lock already drops
  OffsetFromSunCycle and the Perlin noise). Seasonal amplitude A = −(seasonal − 40.4)/cos(2π(ticksAbs/60000 mod 60 /60 − 10/12));
  before the fix A = 8.649 at every point (Worldbuilder Normal tilt at sin(lat)). Pass: seasonal = 40.4 at every point (A = 0).
- If A is still non-zero: candidates in order — (1) our postfix missing from the list (deploy/load did not take: check
  Player.log for "[RM CreatureBehaviors] tidal no-seasons"); (2) TidalLockActive() false (CelestialSunGlow lacks the
  7f owner: the planet loaded as Default, see audit §1); (3) a mod caching the amplitude elsewhere (harmony_patches
  on RimWorld.Planet.TileTemperaturesComp and Verse.GenTemperature OffsetFromSeasonCycle).
- Dusk (DUSK_BAND_DEPLOY_TWELVE_DEGREES_OF_GLOAMING) and rivers (RIVER_BLEND_DEPLOY_UNDER_THE_WATERLINE) ride the same load.

NEXT: load PARITY_QUIET on the deployed files, run seasonsdusk\verify.py, confirm seasonal = 40.4 at every point, then close with the verify.json path.
