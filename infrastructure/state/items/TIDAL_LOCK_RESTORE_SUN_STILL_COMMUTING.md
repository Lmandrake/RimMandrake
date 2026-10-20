# TIDAL_LOCK_RESTORE_SUN_STILL_COMMUTING

Found by FOUNDRY 2026-10-20 during WORLDMAP_BIOME_APPEARANCE_1 (owner: *"Let's get it looking great again. Right now it's barely recognizable."*).

## Measured (live, 324 list, ASHKARR_DEV_START_2026-10-20 loaded)
- The globe's sun moves with the game clock. Same camera (tile 17011, altitude 1100), only the clock changed (play_for 15,000 ticks):
  map clock 6 AM: the substellar desert is dark, the nightside Umbra is evenly lit (`wtx_v2_start2.png`, `wtx_v2_t11000.png`);
  12 PM: the dayside is lit (`wtx_v2_start_noon.png`). All in
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\`.
- Vanilla `GenCelestial.CurSunPositionInWorldSpace` turns the sun with `GenDate.DayPercent` (RimSage source).
  `7f.alienworlds.tidallylocked` (workshop 3631364335, `Source/PlanetTypeDef.cs`) fixes it with a Harmony prefix on
  `SunPositionUnmodified` (dayOfYear 0, dayPercent 0.5), a postfix on `CurSunPositionInWorldSpace`, and a prefix on
  `CelestialSunGlow(PlanetTile,int)`. **None of these is applied in this session.** `jawa/harmony_patches typeName=RimWorld.GenCelestial`
  lists one patched method, `CurCelestialSunGlow` (PerformanceOptimizer, VEE, our EnvironmentalHazards).
  The patches are applied only from `PlanetTypeDef.OnActivate`, and the save does say `<alienWorldsFrameworkPlanetType>TidallyLocked`.
- Consequence (INFERRED): the map day/night cycle and sun glow are vanilla, not tidally locked, and the globe looks dark whenever the clock puts the sun on the nightside.

## spec
1. Find why the Alien Worlds framework does not call `OnActivate` on this save (framework `AlienWorlds.PlanetTypeManager`; try the 374 backup list `infrastructure/state/modlists/ModsConfig.LIVE_BACKUP_2026-10-20_pre_wave4.xml` to see if Wave 4 caused it; read the framework source).
2. Fix the activation, or have a small RimMandrake patch call it. Do not re-implement the sun.

## verify
- `jawa/harmony_patches typeName=RimWorld.GenCelestial` lists `SunPositionUnmodified`, `CurSunPositionInWorldSpace` and `CelestialSunGlow` patched by `7f.alienworlds.tidallylocked`.
- Two globe shots of the same camera 6 game hours apart have the same lighting.
