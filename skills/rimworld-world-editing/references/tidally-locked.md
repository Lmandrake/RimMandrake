# Tidally locked worlds

## 7. Tidally locked worlds — the geometry, solved

`7f.alienworlds.tidallylocked` (workshop **3631364335**, ACTIVE) on top of
`7f.alienworlds` (**3626210061**, ACTIVE). Both ship **full C# source**; everything below
was read out of `Source/PlanetTypeDef.cs` and `Defs/PlanetTypes.xml`, not inferred.

### 🔑 The substellar point is at latitude 0, longitude 0

The mod transpiles `WorldGenStep_Terrain.GenerateTileFor` so temperature stops being a
function of latitude and becomes a function of **great-circle distance from (0,0)**:

```csharp
effectiveLat = Acos( Cos(long) * Cos(lat) ) * Rad2Deg;   // pos.x = LONGitude, pos.y = lat
return AvgTempByLatitudeCurve.Evaluate(effectiveLat / 90f);
```

⚠️ `Find.WorldGrid.LongLatOf()` returns `Vector2(longitude, latitude)` — **x is longitude**.
Read that backwards and every calculation you build on it is wrong but plausible.

So the curve's x-axis is **(degrees from the substellar point) / 90**, and its published
0.0→2.0 range is exactly 0°→180°:

| x | angle from substellar | avg temp | what it is |
|---|---|---|---|
| 0.0 | 0° | **+70 °C** | substellar point — permanent noon, lethal |
| 0.44 | 40° | +21 °C | inner edge of the liveable ring |
| 0.5 | 45° | +14 °C | |
| 0.64 | 57° | **0 °C** | outer edge of the liveable ring |
| **1.0** | **90°** | **−37 °C** | 🔴 **THE TERMINATOR** |
| 1.33 | 120° | −70 °C | |
| 2.0 | 180° | −80 °C | antistellar point — permanent midnight |

### ⇒ Where the terminator actually is, in lat/lon

The terminator is the great circle **90° from (0,0)**, i.e. every tile where
`cos(long)·cos(lat) = 0`. In practice that means:

* **longitude = ±90°, at any latitude** — the two meridians that run pole to pole, and
* **the poles themselves** (latitude ±90°, any longitude).

**Day side = |longitude| < 90°. Night side = |longitude| > 90°.** It is a LONGITUDE
split, not the latitude split every other RimWorld world uses. Any tool that reasons
about "north is colder" is wrong on this planet.

🔑 **The liveable ring is a circle of radius ~40–57° around (0, 0)** — that is the
"habitable sliver" the mod's description promises, and it sits **well inside the day
side**, not at the terminator. The terminator itself is −37 °C.

Compute it per tile straight off `jawa/world_tile_export`:
```python
import math
d = math.degrees(math.acos(math.cos(math.radians(lon)) * math.cos(math.radians(lat))))
# d  <  40  scorched   |  40..57 liveable  |  57..90 cold  |  >90 night side
```

### 🔴 How you SELECT it — two backends, auto-detected

`AlienWorldsFramework.cs` picks its UI at `[StaticConstructorOnStartup]`:

* **If `ferny.Worldbuilder` is ACTIVE** — the framework writes a Worldbuilder preset
  folder at runtime and you choose *"tidally locked world"* on **Worldbuilder's world
  preset screen**. The mod-settings radio buttons are **disabled** in this mode.
  (This is almost certainly what created the empty `…\Worldbuilder\` folder on this
  machine — the framework expecting a companion that is switched off.)
* **If Worldbuilder is INACTIVE — our current state** — choose it at
  **Mod Settings → "Alien Worlds Framework" → "Planet type for new worlds"**, a radio
  button, **before you create the world**.

⛔ It is **not** a dropdown on the Create World page and **not** a scenario setting. If
you are looking for it at worldgen you will not find it. Framework + Harmony are hard
`modDependencies`.

### ⚠️ It applies NO biome restriction — this is the trap

The mod leaves the framework's `<biomes>` and `<biomeConfigs>` **empty**, and
`PlanetTypeManager.cs` treats an empty list as "no restriction". So **vanilla BiomeWorkers
run unchanged against the rewritten temperature field** — which produces jungle and
savanna at ~64 °C on the day side. That is the top complaint on its Workshop page, and it
is a real problem for any world meant to read as a desert.

⇒ The temperature model is excellent and the biome placement is not curated. If we want a
desert planet we constrain biomes ourselves — `Mlie.ChooseBiomeCommonality` (ACTIVE) is
the blunt lever, and per-tile repainting from `jawa/world_tile_export` is the precise one.

### What else the mod changes, from the patches

* **`SunPositionPatch`** pins `dayOfYear = 0`, `dayPercent = 0.5` — the sun never moves.
  **There is no day/night cycle anywhere on the planet.**
* **`SunGlowPatch`** rotates the sun vector by the tile's LONGITUDE, so in-map light
  level is set by longitude. Day-side maps are permanently lit, night-side permanently
  dark. Plan solar power and growing light accordingly.
* **`OutdoorTemperaturePatch`** forces `includeDailyVariations = false` — **no day/night
  temperature swing**, anywhere.
* **`NoIslandPatch` + `SeaIceEdgesPatch`** push sea ice right to the world edge, and
  `ungeneratedPlanetPartsTexture` is `World/Biomes/IceSheetOcean` — the unrendered
  remainder of the planet reads as ice ocean rather than blank.
* `seasonalTempVariationCurve` is 15 / 15 / 5 across the same axis — mild seasons on the
  day side, almost none on the night side.
* `difficulty: 3`. Ships an Alpha Biomes compat patch
  (`Mods/sarg.alphabiomes/Patches/UngeneratedPlanetParts.xml`).
* Ships `Textures/TidallyLockedWorld/Worldbuilder/{Thumbnail,Flavor}.png` — i.e. it is
  **built to be presented through Worldbuilder**, which is currently disabled here.

### ⭐ Coverage: the mod tells you itself

Its own description: *"Generating at least 50% of the planet is recommended."* That is an
independent confirmation of the **0.5 coverage** choice — and it is not arbitrary: below
that you clip away the latitude range that gives the liveable ring its land area.

⚠️ **Known issues.** `Realistic Planets` also rewrites `WorldGenStep_Terrain`
temperature and would collide — not installed here, keep it that way. The author's own
TODO warns the 15° sun-tilt correction may drift after ~half an in-game year. Caravan
travel is untouched (no patch). Solar panels run permanently on the day side and never on
the night side, because sun *glow* is permanent even though `sunlightFactor` is 1.0.

⚠️ **It defines NO biomes of its own.** `Defs/` holds one `PlanetTypeDef` and nothing
else. Biome placement is still vanilla + whatever biome mods are loaded, re-scored
against the new temperature field. So a "terminator biome" is not something this mod
provides — if we want one it is ours to author.

---
