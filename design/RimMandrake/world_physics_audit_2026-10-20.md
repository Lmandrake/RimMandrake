# World physics audit — tidal lock, sun per tile, temperatures, Rings (2026-10-20)

Item `WORLD_PHYSICS_AUDIT_LOCKED_SUN_TEMPS_RINGS`. Owner (2026-10-20, AFK): *"Finally, ensure we are
in fact Tidally Locked. There was a ritual before that had to be followed to ensure that. Check the
solar angle per tile is correct and does not change day/night. I would also like to add back the
Rings when we bring back the larger mod list. Ensure the temperatures are correct as well."*

Offline numbers: `python3 src/RimMandrake/Utils/remake/world_physics_audit.py <save.rws>` (port of
the tidal-lock sun code; method in its docstring). Live reads: `Transient/world_physics_2026-10-20/`
(`live_probe.py read|clock|fix|tiles`, one JSON per phase).

## 1. The ritual, and why the dev save is NOT locked on the full list

Read from source (`…\294100\3626210061\Source\PlanetTypeManager.cs`, `…\3631364335\Source\PlanetTypeDef.cs`,
Worldbuilder `…\3522102833\1.6\Source\WorldPresetManager.cs` + `HarmonyPatches\World_ExposeData_Patch.cs`):

- The tidal lock is not data. It is a set of Harmony patches (sun pinned, glow by tile, no daily
  temperature swing) that `7f.alienworlds.tidallylocked` applies **only while its PlanetTypeDef is
  the active planet type** (`OnActivate => harmony.PatchAll()`, `OnDeactivate => UnpatchAll`).
- On every save load, `PostSaveLoadHook` calls `PlanetTypeManager.UpdateActive(Current)`.
  `Current` depends on the backend:
  - **Standalone (Worldbuilder NOT loaded — PAINT):** `Current` is the save's
    `<alienWorldsFrameworkPlanetType>`. The dev save reads `TidallyLocked`, so PAINT loads it locked.
    (New worlds on PAINT need `set_planet_type.py --apply` first — the 2026-10-20 lesson.)
  - **Worldbuilder loaded (the full list: FULL.LATEST / Wave 4 324 has `ferny.worldbuilder`):**
    `Current` IGNORES the save's planet type and reads Worldbuilder's `CurrentlyLoadedPreset`,
    which comes from the save's `<worldPresetName>`. No preset name ⇒ `"Default"` ⇒ the
    tidal-lock patches are never applied ⇒ **the sun rises and sets**, and the getter also
    overwrites the stored value, so the next save writes `alienWorldsFrameworkPlanetType = Default`.
- **The ritual** (old route, `skills/rimworld-world-editing/references/tidally-locked.md`): create
  the world from Worldbuilder's shipped *"tidally locked world"* preset, which stamps
  `<worldPresetName>TidallyLocked</worldPresetName>` into the save. Measured:
  `CANONICAL_ASHKARR_START_2026-09-12.rws` carries it; **`ASHKARR_DEV_START_2026-10-20.rws` does
  not** (made on PAINT, no Worldbuilder). Autosave-1/2 and `XENO_HEADS_REVIEW_2026-10-20.rws` already
  read `alienWorldsFrameworkPlanetType = Default`.
- **Fix, live (no offline save write):** `jawa/static_call Worldbuilder.World_ExposeData_Patch
  set_WorldPresetName TidallyLocked`, then `jawa/static_call AlienWorlds.PlanetTypeManager
  UpdateActive`, read back `get_Current` and `HarmonyLib.Harmony HasAnyPatches
  7f.alienworlds.tidallylocked`, then save in game — the save then carries both fields and loads
  locked on either backend.

## 2. Sun per tile

Our Direct Sun is geometry alone: elevation = 90 − arc from (lat 0, long 0)
(`RM_MapComponent_ShadeGrid` → `RM_MapComponent_PinnedSun.SunGeometry`), independent of the tidal-lock
mod and of the clock. The GAME's light (`GenCelestial.CelestialSunGlow`, what decides day/night,
plant light, solar power) comes from the tidal-lock `SunGlowPatch`, which feeds LONGITUDE into
vanilla's latitude-shaped sun fudges ("sun peeks around", polar-winter offset at dayOfYear 0). So
it is fixed in time but not a clean function of arc.

Mechanism (read from `…\3631364335\Source\PlanetTypeDef.cs` `SunGlowPatch` + RimSage `GenCelestial`):
the prefix calls vanilla `SurfaceNormal(long)` and `SunPosition(long, 0, 0)` with LONGITUDE in the
latitude slot, then rotates the sun about the up axis by latitude. Inside `SunPosition`, two vanilla
fudges written for latitude act on longitude: (a) `SunOffsetFractionFromLatitudeCurve` at dayOfYear 0
(vanilla's "polar winter" tilt, 0.2 ⇒ the sun dropped 11.3° along −y) — in this frame −y lies toward
negative longitude, so the WEST rim is lit further round and the EAST rim darker; (b) "sun peeks
around" bends the sun 19° toward the tile (fading out at |long| 70–75°) plus 17°·(1−|long|/60) inside
|long| < 60°. Then `clamp01(dot/0.7)` saturates everything with dot ≥ 0.7. It is the mod's own
shortcut (its comment: *"hacky prefix … meh. it works"*), not our data, and nothing we ship touches it.
Direct Sun (heat) does NOT supersede it: glow drives `IsDaytime`, plant growth light, solar power,
darkness mood/accuracy and shadows.

| probe | tile | arc | geometric sun ° | game glow (predicted) | reads as |
|---|---:|---:|---:|---:|---|
| substellar | 19337 | 0.8 | 89.2 | 1.00 | day |
| arc 30 E | 2391 | 30 | 60 | 1.00 | day |
| arc 60 E | 2475 | 60 | 30 | 0.87 | day |
| arc 80 E | 7724 | 80 | 9.8 | **0.00** | **night on the day side** |
| terminator E | 20791 | 90 | 0 | 0.00 | night |
| terminator W | 18631 | 90 | 0 | **0.72** | **day at the terminator** |
| arc 100 W | 7821 | 100 | −9.8 | 0.50 | dusk on the night side |
| arc 120 W/E | 2489/2480 | 120 | −30 | 0.01/0.00 | night |
| antistellar | 18991 | 179 | −89 | 0.00 | night |
| start | 17011 | 54.6 | 35.4 | 1.00 | day |

Planet-wide: 448 night-side tiles read as daytime (glow > 0.6) and 1,796 day-side tiles read as
night. Live confirmation of this table is in §5.

## 5. Live reads, 2026-10-20 15:28–15:31Z (Wave 4 324 list, dev save loaded, bridge held by FOUNDRY)

- **Readback on load:** `PlanetTypeManager.Current` = **`Default`**, `WorldPresetName` = null,
  `Harmony.HasAnyPatches("7f.alienworlds.tidallylocked")` = **False**. Not locked.
- **Clock scrub before the fix** (home tile 17011; +6 h/+12 h/+18 h/+15 d, restored to tick 3):
  celestial glow 0.68 → 1.00 → 0.68 → **0.00** → 0.75 — the sun sets. Direct Sun elevation stayed
  35.40° throughout (geometry: 35.4°).
- **Fix applied live** (the two static calls in §1): `Current` = `TidallyLocked`, patches present =
  True. **Same scrub after:** glow 0.7535 at all five times, Direct Sun 35.40°. 🔴 That constant
  glow is a FROZEN CACHE, not the lock: 0.7535 is exactly vanilla's glow at the before-fix +15 d
  sample (2nd Jugust; recomputed offline to 4 digits, as are the other four before-fix values), and
  every read after the clock was set BACK to tick 3 returned it. The home map is read through
  `CurCelestialSunGlow(map)`, which PerformanceOptimizer caches (`Optimization_GenCelestial_CurCelestialSunGlow`,
  a `refreshTick` cache); rewinding the clock leaves the refresh tick in the future (cause of the
  freeze INFERRED from the DLL's names; the symptom MEASURED). The lock itself is proven by the patches
  being present and by the scratch maps below, whose fresh maps match the time-independent formula.
  The home tile under the lock reads 1.00 (port).
- **Scratch maps** (generated, read, dropped, their world objects 156–159 removed):

  | tile | arc | predicted glow | live glow | Direct Sun ° (live) | outdoor °C live / stored |
  |---:|---:|---:|---:|---:|---|
  | 18631 terminator W | 90 | 0.72 | **0.721** | (no sun-heat biome) | 12.7 / 14.0 |
  | 7724 arc 80 E | 80 | 0.00 | **0.000** | (no sun-heat biome) | 23.0 / 21.8 |
  | 7821 arc 100 W | 100 | 0.50 | **0.500** | (no sun-heat biome) | 3.4 / 2.2 |
  | 2475 arc 60 E | 60 | 0.87 | **0.873** | 29.97 (geometry 30.0) | 33.6 / 34.8 |

  The port matches the game on every scratch tile. The home map's 0.7535 is the stale cache above,
  not a glow scaler (`RUT_ExtremeDesert` carries no `BiomeGlowMultiplierExtension`). The ±1.25 °C live-vs-stored offsets
  flip sign by hemisphere: that is the seasonal term of §3 at this date.
- **Saved:** `Saves\ASHKARR_DEV_START_2026-10-20_LOCKED.rws` (in-game save, new name), which reads
  `alienWorldsFrameworkPlanetType = TidallyLocked` and `worldPresetName = TidallyLocked`. The
  original `ASHKARR_DEV_START_2026-10-20.rws` is untouched and still loads unlocked on the full list.

## 3. Temperatures

Stored tile temperatures in the dev save equal the painted record (`world/ASHKARR_WORLDMAP_tiles.csv`)
on all 21,872 tiles (max |Δ| ≤ 1 °C: none), and track the ruled curve
`[70,58,38,14,−22,−58,−80]` on arc minus 5.5 °C/km (biome medians within ±1 °C of it). Mismatches:

- **The Scald** (`RM_TheScald`, 312 tiles): sheet `design/Jawa/worldbuilding/biomes/the_scald.md` §0
  puts it at arc 0–30, air +58..+70 °C; the planet has it at arc 23–51 (median 36), 36..53 °C
  (median 46), and 7.8 °C under the curve on every tile.
- Smaller local departures (|Δ| > 5 °C): RM_TwilightSea 83, RM_TheRot 61, RM_Abyss 45, RUT_Umbra 19,
  RM_FloodedCanyon 17 tiles — authored in the record, not drift.
- 🔴 **Seasons still swing.** Under the tidal lock the daily swing is off, but vanilla
  `GenTemperature.OffsetFromSeasonCycle` still runs with `SeasonalShiftAmplitudeAt(tile)`. Which curve feeds that
  amplitude depends on the backend: standalone, Alien Worlds' transpiler reads the TidallyLocked def's
  `seasonalTempVariationCurve` (0:15, 1:15, 2:5 → 15 °C on every tile); **with Worldbuilder loaded (the full list),
  Worldbuilder replaces the method and uses its axial-tilt curve (Normal = 3/4/28, by sin(latitude))**, measured
  8.649 °C at the home tile (§8). A tidally locked planet with no axial tilt has no seasons; owner ruled "Remove the
  swing" (§6).
- Under the `Default` planet (§1) vanilla's latitude seasonality and a ±7 °C day/night swing apply.

## 4. The Rings

The Rings are **RW - Planet Atmosphere** (`RWNodeTree.RWPlanetAtmosphere`, workshop 3272330410,
needs only Harmony) with our settings: `Config\Mod_3272330410_AtmosphereMod.xml` = the owner-verified
`deployed/config/Mod_3272330410_AtmosphereMod.TRUE-GLORIOUS-RING.xml` (md5 ac1e8fa4; ringMapPath
`Ring/ring_debris`, ringFromTo 14e6–20e6) and the war-debris strip `deployed/atmosphere_ring/ring_debris.png`
(md5 df22cd50), hand-copied into the WORKSHOP folder `…\3272330410\Textures\Ring\` (a Steam update
can wipe it). It was on every full list through Wave 1 (498) and dropped in Wave 2 as "05 SAFE drop"
(`infrastructure/state/modlists/wave2_removed_118.txt`); absent from FULL.LATEST/Wave 4 324, SHIP,
DEV, PAINT. Registry: KEEP-TEMPORARILY-THEN-PHASE-OUT, owner C18 "measure real memory cost first".
Restore steps: item `PLANET_RINGS_RESTORE_DEBRIS_STILL_IN_ORBIT`.

## 6. Owner decisions by card, 2026-10-20, and what was built (offline)

- **Light** ("Lopsided tidal-lock daylight" → "Light follows the sun"): `RM_TidalSunGlowPatch` +
  `RM_TidalSunGlowMath` (CreatureBehaviors) postfix `CelestialSunGlow(PlanetTile,int)` only while
  `7f.alienworlds.tidallylocked` has its patch on it: glow = 0.6 + 0.4·min(1, sin e / sin 30°) for sun
  elevation e > 0, a 12° dusk band (owner by card 2026-10-20; was 6°) (smoothstep to 0.6) below the horizon, 0 beyond; constant in time, symmetric.
  Setting `tidalSunGlowByGeometry` (on) + dusk-band slider. Offline (`world_physics_audit.py`, selftest
  `remake/selftest_tidal_sun_glow.py`): 0 night-side tiles read day and 0 day-side tiles read night (mod: 450 /
  1,794 unrounded; 448 / 1,796 rounded, §2); home 17011 = 1.00. Live check + deploy: `TIDAL_GLOW_DEPLOY_FOLLOWS_THE_SUN`.
- **Seasons** ("Every tile swings ~15 C" → "Remove the swing"): `CreatureBehaviors/Patches/RM_TidalLock_NoSeasons.xml`
  flattens the TidallyLocked def's `seasonalTempVariationCurve` to 0 (FindMod + Conditional guarded; validate_patch
  `--live --defs`: 1 match, 0 errors). Stored tile temperatures are untouched: both dev saves equal the painted
  record on all 21,872 tiles (max |Δ| 0.0). The Scald line stays on `BIOME_PAINT_ONCE_AT_THE_END_1`. Live check:
  `LOCKED_SEASONS_DEPLOY_CALENDAR_GOES_FLAT`.
- **Home map size** ("250x250 vs 325x325" → "Back to 325"): the size every later home map (gravship landing,
  settling) is generated at is the scribed `WorldInfo.initialMapSize`. `CANONICAL_ASHKARR_START_2026-09-12.rws`
  reads 325; every `ASHKARR_DEV_*_2026-10-20` save reads 250 (made through a new game, `GameInitData.mapSize`
  default 250). No def or scenario sets it; the route is the live world: `jawa/world_info_set initialMapSize=325`
  (parameter added, companion not yet deployed), then save. Runbook: `HOME_MAP_SIZE_RESTORE_ROOM_TO_STRETCH`.

## 7. Owed (as of the morning; see sections 8 and 9 for the evening)

- `TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING` — pick the dev save; a load-time guard so the full list cannot load unlocked.
- `PLANET_RINGS_RESTORE_DEBRIS_STILL_IN_ORBIT` — ride the next larger-list cold load.
- The Scald's arc/temperature vs its sheet (§3) goes on the end-of-build paint list, not a repaint now:
  filed as a line in `infrastructure/state/items/BIOME_PAINT_ONCE_AT_THE_END_1.md`.

## 9. Live check, 2026-10-20 evening (FOUNDRY, 325-mod list)

Evidence: `D:\ClaudeWork\rimmandrake\scratch\live5\` (`clock.json`, `live_tiles_after_glow.json`, `seasons.json`, `verify2.json`).
- **Lock on load:** `ASHKARR_DEV_START_2026-10-20_PARITY` loads `TidallyLocked`, preset name `TidallyLocked`, and the tidal patches are present.
  `SunPositionUnmodified`, `CurSunPositionInWorldSpace` and `CelestialSunGlow` are owned by `7f.alienworlds.tidallylocked`.
- **Uncached clock (forward steps only, before the light patch was deployed):** home glow 1.00 and Direct Sun 35.40° at
  ticks 2243, 17395, 32986, 47995 and 63582 (one game day). The sun does not commute.
- **Light follows the sun (CreatureBehaviors built at 3742c2b6b):** `mandrake.rm.creaturebehaviors.tidalsunglow` sits beside the lock on
  `CelestialSunGlow`. Fresh scratch maps read 18631 0.60, 7724 0.74, 7821 0.00 and 2475 1.00 (0.9996). Home 17011 reads 1.00, as predicted.
  ⚠️ The scratch maps on Blackstar settlement tiles log pawn-generation NREs (`Error while resolving symbol "pawn"`, PostMapInit for
  Orwell/Sliverwar, then a draw-error run). They stop when the map drops.
- 🔴 **Seasons are NOT flat after the NoSeasons patch.** Home 17011 `seasonalTemp` went 36.951 → 37.170 over +15,705 ticks forward.
  That is the same +0.22 °C per 6 h as before the deploy. Either the patch did not reach the curve Alien Worlds installs,
  or the save restores it. `GenTemperature.SeasonalShiftAmplitudeAt` cannot be read: `jawa/static_call` refuses
  `PlanetTile` arguments.
- **Rings:** ring drawn with the debris texture, clear of the surface. With Rings on, the process ran WS 6.5 GB, private 17.9 GB,
  peak WS 9.8 GB (first load) and WS 7.7 GB, private 17.7 GB (second load). No Rings-off load ran this session, so the delta is UNMEASURED.
  `RW_PlanetAtmosphere` logs no errors. 12 benign "shader not supported" lines come from the Metal bundle.
- **Atmosphere shell A/B** (`ATMO_pair_limb.png`, `ATMO_pair_globe.png`, left original and right LIMB-TEST minh/maxh 100/108):
  - **Gains with LIMB-TEST:** a real blue limb and night-side shading east of the terminator.
  - **Costs with LIMB-TEST:** haze dulls the surface colours and labels, and 🔴 the near side of the ring disappears where it
    crosses the globe (the shell draws over it), plus a thin white arc on the right limb.
  - **Kept:** the original `TRUE-GLORIOUS-RING` config (md5 ac1e8fa4). The owner picks; the LIMB file stays in `deployed/config/`.
- **Map size:** `jawa/world_info_set initialMapSize=325`, saved as `ASHKARR_DEV_START_2026-10-20_PARITY_QUIET.rws`
  (file reads `(325, 1, 325)`). The same save ignores VFE's Junkers, Mercenaries and Roaming monstrosities. "Do nothing" does not persist, and
  "Don't ask for this faction again" writes `NewFactionSpawningState.ignoredFactions` (63 entries). A reload showed no dialog.

## 8. Why seasons stayed after the NoSeasons patch, and the fix (FOUNDRY, 2026-10-20 night)

Evidence: `D:\ClaudeWork\rimmandrake\scratch\seasonsdusk\samples.json` (`sample.py`), PARITY_QUIET save, 325-mod list.
- **Measurement:** the clock was jumped forward (`jawa/time_set_ticks`, then 2 stepped ticks so the tile-temperature cache
  refreshes) to 25 hourly points across one day and then once a day for 15 days; at each point `outdoorTemp` and
  `seasonalTemp` were read at a home-map cell.
  - Daily term and noise: **none.** `outdoor == seasonal` at all 39 points (the lock drops `OffsetFromSunCycle` and the
    Perlin daily noise).
  - Seasonal term: **all of it.** Solving `seasonal = 40.4 − A·cos(2π(day/60 − 10/12))` gives A = **8.649 °C at every
    point** (36.96 °C on day 1 → 48.33 °C on day 15). The +0.22 °C per 6 h was this term.
- **Mechanism** (`jawa/harmony_patches Verse.GenTemperature`; Worldbuilder source
  `…\3522102833\1.6\Source\HarmonyPatches\GenTemperature_SeasonalShiftAmplitudeAt_Patch.cs`): `SeasonalShiftAmplitudeAt`
  has Worldbuilder's prefix, which returns false, so the original body never runs, and Alien Worlds' transpiler, which
  lives in that body, never runs either. Worldbuilder's priority-MaxValue postfix then sets the amplitude from its
  axial-tilt table. Normal tilt = vanilla's 3/4/28 curve at `DistanceFromEquatorNormalized` = sin(15.92°) = 0.274 → 8.649.
  BiomesCore adds a priority-400 postfix after it. `RM_TidalLock_NoSeasons.xml` applied (the def curve), but nothing read it.
  ⚠️ The ±15 °C in §3 was the standalone-backend figure; on the full list the swing is the tilt curve (3 °C at the
  equator, 28 °C at the poles).
- **Fix:** `RM_TidalNoSeasonsPatch` (CreatureBehaviors) adds a `Priority.Last` postfix on `SeasonalShiftAmplitudeAt`
  that returns 0 while the tidal lock is active. Setting `tidalLockNoSeasons` (default on). The XML patch stays for the
  standalone backend.
- **Readback owed after deploy:** the same sampler gives `seasonal` = 40.4 at every point (A = 0).

