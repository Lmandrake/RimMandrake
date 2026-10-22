# Who reads the sky glow — consequences of "Light follows the sun" (2026-10-20)

Owner, by card 2026-10-20: *"Lopsided tidal-lock daylight: what should light do?" → "Light follows the sun"*.
Built: `src/RimMandrake/CreatureBehaviors/Source/RM_TidalSunGlowPatch.cs` + `RM_TidalSunGlowMath.cs` (postfix on
`GenCelestial.CelestialSunGlow(PlanetTile,int)`, active only while the tidal lock is). Day side: glow 0.6 at the
horizon → 1.0 from 30° elevation, never ≤ 0.6, so `IsDaytime` is always true. Dusk band: 12° below the horizon (owner, by card 2026-10-20 → "12 degrees"; was 6°),
smoothstep 0.6 → 0. Beyond: **0, forever**. Constant in time, symmetric west/east. Deploy + live check:
`TIDAL_GLOW_DEPLOY_FOLLOWS_THE_SUN`. Context: `design/RimMandrake/world_physics_audit_2026-10-20.md`.

Method: OFFLINE. Vanilla 1.6 symbols read through RimSage (call sites of `CurCelestialSunGlow`, `CelestialSunGlow`,
`IsDaytime`, `CurSkyGlow`, `GroundGlowAt`, `PsychGlowAt`, `InSunlight`, `GetLightSourceInfo`, `AverageGlow`,
`Plant`, `WildPlantSpawner`, `JobGiver_GetRest`); our mods by grep of `src/`. The tidal-lock mod's patch list read from
its source (`…\workshop\content\294100\3631364335\Source\PlanetTypeDef.cs`). Per-biome numbers are from the RECORD
`world/ASHKARR_WORLDMAP_tiles.csv` (where things sit; not a claim about what is built) through the Python port in
`src/RimMandrake/Utils/remake/world_physics_audit.py` (`glow_geo` new, `glow_tidal` the mod's old value). Scripts and
raw output: `D:\ClaudeWork\rimmandrake\scratch\glowconsumers\`. Donor-mod comps other than the tidal-lock mod were
**not** searched (UNMEASURED); `src/` has no nocturnal/diurnal mechanic, only description text.

## How the number reaches each consumer

- `CelestialSunGlow(PlanetTile,int)` ← **our postfix**. Read directly by `MapPlantGrowthRateCalculator` (world
  grazing/plant-rate tables) and by `GameCondition_EnvironmentalWeather` (day/night temperature lerp).
- `CurCelestialSunGlow(Map)` = the above × our `BiomeGlowPatches` postfix (`BiomeGlowMultiplierExtension`: Miasma 0.85,
  Greentide 0.75, Sump 0.55; Breaklight-style override conditions). Feeds `IsDaytime`, shadows, sky colour, auroras.
- `SkyManager.CurSkyGlow` = weather's `CurSkyTarget` (min(celestial, weather.maxGlow)) lerped with sky events (our
  pinned sun, auroras, eclipses). Feeds `GlowGrid.GroundGlowAt` (sky + lamps; lamps cap at 0.5 unless overlit) →
  `PsychGlow` (Dark ≤ 0.3 < Lit ≤ 0.9 < Overlit), plants, sight, mood.
- Not glow at all (unchanged by this patch): the **clock**. `GenLocalDate.HourOfDay/DayPercent` keep ticking; the
  tidal-lock mod only pins the sun's world position and, inside `GetLightSourceInfo`, swaps `DayPercent` for a
  per-tile constant (shadow direction fixed by arc).

## Consumer table

Constant 0 = night side (and dusk band past −12°); constant 0.6–1.0 = day side.

| consumer (vanilla unless `RM`) | what reads glow | night side, glow 0 forever | day side, 0.6–1.0 forever | intended? | breaks? |
|---|---|---|---|---|---|
| Plant growth `Plant.GrowthRateFactor_Light` (`GroundGlowAt`, `InverseLerp(growMinGlow 0.51, 1)`) | sky+lamps | 0 unless lit by a sun lamp (lamps alone cap 0.5 < 0.51) | factor 0.18 at the horizon → 1.0 from 30°; arc 60–90 farms grow slower than under the mod (Desert mean 0.61 vs 0.56 old, Arid Shrubland 0.60 vs 0.77, Weeping Stones 0.82 vs 0.97) | yes (geometry) | no |
| Plant death `Plant.unlitTicks > 450000` (7.5 d) with `dieIfNoSunlight` (default **true**) | `HasEnoughLightToGrow` | **every plant without `growMinGlow 0` / `dieIfNoSunlight false` dies in 7.5 days** and `WildPlantSpawner` re-spawns it (no light check) → stunted churn | n/a | **no** for the nightside/terminator flora the sheets call chemotrophic | **YES** — see §A |
| Plant resting (`Plant.Resting`, clock) | clock | growth 0 anyway | `RM_Patch_Plant_Resting_TidalLock` (ExplosiveGrowth, OQ-7 "always lit means always growing") lifts rest when lit | yes | no |
| World plant-rate tables `MapPlantGrowthRateCalculator` (pasture/grazing info) | `CelestialSunGlow(tile)` (no biome multiplier) | 0 → no grazing growth listed | constant | yes | no |
| Fall colours `PlantFallColors` (`AverageGlow`) | vanilla latitude math, sun pinned by the mod | constant | constant | yes (seasons removed: `RM_TidalLock_NoSeasons.xml`) | no |
| Solar generator `CompPowerPlantSolar` = lerp(0, max, `CurSkyGlow`) | sky | **0 forever** | 0.6–1.0 × max, 24 h a day (vanilla averages ~half that over a day) | yes (physics) | no — balance note: day-side solar is ~2× vanilla daily energy, batteries optional; night-side colonies need fuel/geothermal |
| Our sun machines: `RM_SunPower` (Stillsand, non-pinned branch), `RM_MapComponent_MirrorLight` (`Daylight`: 0 ≤ 0.1, full ≥ 0.6), FlowWorks `CompLiquidConverter` (`SunFactor(CurSkyGlow)`) | celestial / sky | off | on, constant | yes | no |
| `IsDaytime` (glow > 0.6): sky colour set, lightsource shine, shadow branch | `CurCelestialSunGlow` | night | day — **unless a biome multiplier pushes it under 0.6**: Sump ×0.55 never "day" (designed dusk); Miasma ×0.85 drops under at elevation < 7.6°, Greentide ×0.75 under 14.5° — both biomes' record arcs (≤75, ≤58) stay above | yes | no |
| Shadows: strength `CurShadowStrength` = \|glow−0.6\|/0.15; direction by arc (mod) | celestial | strong "moon" shadows | **faint near the terminator** (glow 0.6–0.75 = elevation 0–11°), full only above ~11° — the long low-sun shadows read weakest exactly where they are longest | cosmetic | no — pinned-sun biomes (LongShade, Stillsand, Leaning Scrub) already set their own opacity; see §C |
| Darkness mood `ThoughtWorker_Dark` (no Lit for > 240 ticks while awake) / `PawnRecentMemory` | `PsychGlowAt` | outdoors always Dark → mood debuff unless lamps | never | yes (permanent night; lamps are the answer) | no |
| Ideology light precepts (`IndoorLight`, `OutdoorBlindingLight` = Overlit, Darklight) | `PsychGlowAt` | dark | outdoors Overlit only above glow 0.9 (elevation ≳ 22°) | yes | no |
| Combat in darkness `DarknessCombatUtility` (outdoors lit when `CurSkyGlow` > 0.35) | sky | dark combat rules always | lit always | yes | no |
| Sunlight `SanguophageUtility.InSunlight` (`CurSkyGlow` > 0.1, unroofed): sanguophage burn, deathrest, `ConditionalStatAffecter_InSunlight`, `ThoughtWorker_InSunlight`; our `RM_HediffComp_SunlightScald`, `RM_Hediff_SunScald` | sky | never | **always** outdoors | yes (and the Direct Sun / tree-shade work is the shade answer) | no — sanguophages cannot stand outdoors on the day side at any hour; physics, worth one line in the player notes |
| Dusk band `InSunlight` edge | sky | glow > 0.1 only to ~4.5° below the horizon | — | yes | no |
| Sleep, schedules, animal rest (`JobGiver_GetRest`: non-scheduled pawns sleep 22–6 by `HourOfDay`), our `LordToil_InhabitedRoutine`, `FeralSurvivors`, `RM_QuestPart_EggHatch` | **clock** | unchanged: 24 h body clock | unchanged | yes | no — vanilla has no light-sleep thought and no nocturnal mechanic; none in `src/` |
| Clock / date UI (`DateReadout`, time-of-day) | clock | keeps showing hours | same | acceptable | no — the hour is a body clock, not a sun |
| Auroras: `IncidentWorker_Aurora` needs glow ≤ 0.5 now and +5000 ticks; `GameCondition_Aurora` ends when > 0.5; our `AuroraLight` `Nightness` | celestial | can fire any time, never ends early | never fires | yes | no |
| Skygaze `JobDriver_Skygaze` | celestial | always the night-sky thought | always the day-sky thought | yes | no |
| Darkness overlay `SectionLayer_Darkness`, `GenUI` winter text shadow, sand/blizzard overlay tint | sky / celestial | vanilla midnight look forever | daylight | yes | no |
| Infestation cell weight, `CompSightstealer`, Anomaly darkness, noctoliths, edge-walk-in-darkness | `GroundGlowAt`/`PsychGlow` | favoured outdoors | disfavoured | yes | no |
| `GameCondition_EnvironmentalWeather` day/night temp lerp | `CelestialSunGlow` | night offset | 0.6–1.0 of the day offset | moot | no — no def in `src/` sets `dayTempOffset`/`nightTempOffset` (grep: 0) |
| Food spoilage `CompRottable`, outdoor temperature | temperature only | — | — | — | no glow input (daily swing already off under the lock; seasons flattened) |
| Direct Sun heat, tree shade (`RM_MapComponent_ShadeGrid`, `RM_MapComponent_PinnedSun.SunGeometry`) | **geometry, not glow** | none (sun below horizon) | per elevation | yes | no — glow and heat now share one geometry |
| `RM_WatcherCues` shade reading, Deepfire paint (glows when sky ≤ 0.35), `RM_TwilightFloraBehaviour` (wilts on *artificial* glow > 0.35, `ignoreSky`) , `RM_Comp_VaeuliskLure` (seeks darkest cell) | sky / ground | dark → paint glows, lures work | lit | yes | no |
| PerformanceOptimizer's `CurCelestialSunGlow` cache (audit §5) | cache | constant value ⇒ harmless | same | — | no — only a live toggle of the setting or a clock rewind shows a stale value until its refresh tick |

## A. BREAKS — night and terminator flora that needs a sun (not caused by this patch; exposed by the lock)

Vanilla kills any wild plant whose cell glow stays below its `growMinGlow` for 7.5 days unless it sets
`dieIfNoSunlight false` (`Plant.CurrentDyingDamagePerTick`, RimSage), and `WildPlantSpawner` keeps re-seeding it, so
a sunless biome becomes a churn of tiny plants that never reach full size. The old tidal-lock glow was 0 on most of
these tiles too, but the full list was loading UNLOCKED (audit §1), so the day/night cycle hid it.

🔴 **The trap:** `growMinGlow 0` alone does NOT make a sunless plant. `PlantUtility.GrowthRateFactorFor_Light` is
`InverseLerp(growMinGlow, growOptimalGlow, glow)`, which is **0 at glow 0** when optimal stays at the default 1.0, so the
plant is "unlit", never grows and dies at 7.5 days. Vanilla's own cave plants (`Glowstool`, RimSage) set BOTH
`growMinGlow 0` and `growOptimalGlow 0` (then the factor is 1 at any glow, `GenMath.InverseLerp` a == b branch).

Static parse of `src/` BiomeDefs + patch-added `wildPlants`, inheritance resolved inside `src/`, factor computed at
glow 0 exactly as vanilla does (script `D:\ClaudeWork\rimmandrake\scratch\glowconsumers\nightplants2.py`, output
`nightplants2.txt`): GROWS = factor > 0 at glow 0; DIES = factor 0 and `dieIfNoSunlight` true.

| biome | where (sheet / record) | wild plants | grows in the dark | dies in the dark | note |
|---|---|---:|---:|---:|---|
| `RM_TheSump` | dusk, median −10.6° | 10 | 0 | **10** | sheet: *"every native plant here is chemotrophic on the tar"*; all set `growMinGlow 0` but leave optimal 1.0 (`RM_Brindeth`, `RM_Dorvel`, …) — the trap |
| `RM_TheRot` | nightside, record arc median 114 | 39 | 19 | **19** | the donor ports (`RM_TheRotPortedCavePlantBase` children: `RM_Bryolux`, `RM_AgariluxPrime`, …) inherit vanilla 0.51/1.0; the spore-kit plants are already right |
| `RM_Cauldron` (Poison Forest) | terminator, arc core 82–106, median −1.3° | 16 | 0 | **16** | sheet: *"Chemosynthesis wins, and photosynthesis survives as an underclass"* — no plant encodes the chemotroph half |
| `RM_Abyss` | nightside | 10 | 2 | **8** | `RM_GiantFibreStalk`, `RM_GiantGlowGlobe` set min 0 only — the trap |
| `RM_GelatinousSlime` | terminator, arc 81–103 | 4 | 0 | **4** | min 0.31 → dies wherever the sun is more than ~2.9° below the horizon |
| `RM_Wastes` | ~+3° sheet; record 37–118 | 9 | 0 | **9** | lit tiles fine; nightside tail dies |
| `RM_LanternDeeps` | nightside | 11 | 10 | 1 | |
| `RM_BlueDesert`, `RM_TwilightSea`, `RM_GreySea` | night / terminator seas | 9 / 8 / 17 | all | 0 | already right |

Share of record tiles where a default plant (`growMinGlow` 0.51) cannot grow, new vs mod: The Rot 85% vs 91%,
Poison Forest 47% vs 44%, Slime 34% vs 59%, Wasteland 66% vs 76%, Sump 80% vs 71%, Twilight Sea 45% vs 33%.

**Proposed fix (offline, per plant, in the mods we own):** for each listed plant whose sheet makes it sunless
(chemotroph, nightside-lush, glower), set `<growMinGlow>0</growMinGlow>` AND `<growOptimalGlow>0</growOptimalGlow>`
(vanilla Glowstool's pattern, and the Rot spore kit's); never add `diesToLight` (that kills them on the day side and in
lamplight). Leave the Cauldron's named photosynthetic underclass as is. A selftest should refuse any plant with
`growMinGlow 0` and `growOptimalGlow > 0` (the trap). Item: `DARK_FLORA_FIX_WILTS_WITHOUT_A_SUN`.

## B. DECISION — how far does dusk reach?

**Decided 2026-10-20, owner by card: "How far below the horizon should dusk light reach?" → "12 degrees (Recommended)".** At 12° the Sump is 39% dark tiles (was 61%), median glow 0.02; the Crags 84% (was 98%), median 0. Still 0 night-side-reads-day / 0 day-side-reads-night tiles (selftest). The table below is the evidence the card was put on:

The sheets name a twilight the 6° band does not give:

| biome | sheet says | median sun elevation | glow 0 on tiles, band 6° / 12° / 18° | median glow, 6° / 12° / 18° |
|---|---|---:|---|---|
| The Sump | *"permanent deep twilight … the sun a glow below the horizon"* | −10.6° | 61% / 39% / 0% | 0.00 / 0.02 / 0.22 (×0.55 biome multiplier) |
| Wasteland | — | −7.6° | 59% / 28% / 12% | 0.00 / 0.18 / 0.37 |
| Forsaken/"Twilight" Crags | *"the crags are twilight (arc 100–116)"* | −18.2° | 98% / 84% / 51% | 0.00 |
| Poison Forest / Cauldron | *"permanent scattered twilight"* | −1.3° | 21% / 16% / 6% | 0.53 / 0.58 / 0.59 |
| Slime | *"the terminator's permanent low amber"* | 0.0° | 15% / 1% / 0% | 0.60 |

Real twilight runs to 18° below the horizon (civil 6°, nautical 12°, astronomical 18°). The slider
`tidalTwilightBandDegrees` already exists; only its default was at stake (now 12°). Any band keeps every lit-side and night-side
rule above; a wider band lifts the Sump and the Crags out of pitch black (still psychologically Dark < 0.3, still too
dim for sun plants). Item: `TWILIGHT_BAND_DECIDE_HOW_FAR_DUSK_REACHES` (owner card).

## C. Cosmetic, noted only (his permission needed before any change)

Shadow opacity follows vanilla's |glow−0.6|/0.15, so day-side tiles with the sun under ~11° (record arc 79–90:
Slime, Grey Sea, Twilight Sea, half of Desert) draw faint shadows even though their shadows are the longest. Pinned-sun
biomes already override it. Not filed.
