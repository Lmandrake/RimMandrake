# TIDAL_LOCK_RESTORE_SUN_STILL_COMMUTING

Found by FOUNDRY 2026-10-20 during WORLDMAP_BIOME_APPEARANCE_1 (owner: *"Let's get it looking great again. Right now it's barely recognizable."*).
Owner 2026-10-20: *"ensure we are in fact Tidally Locked ... Check the solar angle per tile is correct and does not change day/night. Ensure the temperatures are correct as well."*

## State (2026-10-20, offline source read)
- Cause MEASURED: the dev save had no `<worldPresetName>`; with `ferny.worldbuilder` loaded, AlienWorlds reads the
  Default planet type and `7f.alienworlds.tidallylocked`'s patches (applied only in `PlanetTypeDef.OnActivate`) never
  run, so the sun commutes. Live-fixed and saved as `Saves\ASHKARR_DEV_START_2026-10-20_LOCKED.rws`; the durable fix
  (load-time guard + which save is canonical) is `TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING` — not duplicated here.
- How the lock works when active (source, `…\3631364335\Source\PlanetTypeDef.cs`): `SunPositionUnmodified` prefix pins
  dayOfYear 0 / dayPercent 0.5; `CelestialSunGlow(PlanetTile,int)` prefix computes glow from tile position only (no
  ticks read); `CalculateOutdoorTemperatureAtTile` prefix forces `includeDailyVariations = false`. Time independence is
  by construction. Seasons are NOT pinned (`LOCKED_SEASONS_DECIDE_FIFTEEN_DEGREE_WOBBLE`); light is skewed against
  geometry (`SUN_GLOW_DECIDE_WEST_TERMINATOR_SUNBATHING`).
- 🔴 Correction: the audit's "glow 0.7535 at all five clock times after the fix" was a frozen PerformanceOptimizer cache
  of `CurCelestialSunGlow(map)` after `jawa/time_set_ticks` rewound the clock (0.7535 = vanilla glow at the +15 d
  sample, recomputed offline: `D:\ClaudeWork\rimmandrake\scratch\sunglow\vanilla_glow.py`). It is not lock evidence.
  The lock IS evidenced by `HasAnyPatches` True and fresh scratch maps matching the formula to 3 decimals.

## verify (owed, needs the bridge)
- On a fresh load of the LOCKED save: `jawa/harmony_patches typeName=RimWorld.GenCelestial` lists `SunPositionUnmodified`,
  `CurSunPositionInWorldSpace`, `CelestialSunGlow` by `7f.alienworlds.tidallylocked`.
- Clock test that cannot be cached: call `GenCelestial.CelestialSunGlow(PlanetTile,int)` with explicit ticksAbs
  (now, +6 h, +12 h, +18 h, +15 d), or let the game run FORWARD 6 h between reads; never rewind before a
  `CurCelestialSunGlow(map)` read. Home tile 17011 should read 1.00 at every time.
- Two globe shots of the same camera 6 game hours apart have the same lighting.

NEXT: after `TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING` lands, run the uncached clock test above on the bridge and close this item with that read.
