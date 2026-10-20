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
- 🔴 **Seasons still swing ±15 °C everywhere.** Under the tidal lock the daily swing is off
  (`includeDailyVariations = false`) but vanilla `GenTemperature.OffsetFromSeasonCycle` still runs,
  with the planet def's `seasonalTempVariationCurve` (0:15, 1:15, 2:5) evaluated at |lat|/90 —
  i.e. 15 °C amplitude on every tile, opposite sign per hemisphere. A tidally locked planet with no
  axial tilt has no seasons; this is an owner question, not a silent fix.
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

## 6. Owed

- `TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING` — pick the dev save; a load-time guard so the full list cannot load unlocked.
- `SUN_GLOW_DECIDE_WEST_TERMINATOR_SUNBATHING` — owner card: light by geometry or the mod's skew.
- `LOCKED_SEASONS_DECIDE_FIFTEEN_DEGREE_WOBBLE` — owner card: the ±15 °C seasons.
- `PLANET_RINGS_RESTORE_DEBRIS_STILL_IN_ORBIT` — ride the next larger-list cold load.
- The Scald's arc/temperature vs its sheet (§3) goes on the end-of-build paint list, not a repaint now:
  filed as a line in `infrastructure/state/items/BIOME_PAINT_ONCE_AT_THE_END_1.md`.
