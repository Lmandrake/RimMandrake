# SOLAR_HEAT_EXPOSURE_1 — tranche 1 report

Status: LANDED, tranche 1 of several. The item stays open. 2026-09-29.
Nothing was deployed or live-tested.

## What it builds on
- **`RM_MapComponent_ShadeGrid`** (Creature Behaviors) is extended in place, and its `ShadeAt` contract is unchanged, so every existing consumer still works.
- **`RM_MapComponent_PinnedSun`**: its `ShadowDirection`, `ShadowLengthPerHeight` and `SunGeometry` supply the direction and length of the cast shadows.
- **Harmony**: Creature Behaviors already references it (`RM_SightBlockPatches`, `RM_PinnedSunPatches`), so this adds no new dependency.
- **Engine, checked in RimSage (decompiled 1.6):**
  - `HediffGiver_Heat.OnIntervalPassed` reads `pawn.AmbientTemperature` and compares it with `SafeTemperatureRange`.
  - `Pawn_PathFollower.GenerateNewPathRequest` passes no `IPathGridCustomizer`.
  - `PathGridJob` adds `custom[index]` to each cell's path cost. A value of 10000 or more makes the cell impassable.
  - `PathFinder` caches its cost grids by the customizer object.

## §2 Heat kinds per biome
There is a new `RM_SunHeatExtension` on the BiomeDef, which sets `heatKind` (overhead / lowSun / ambient), a heat offset, a body-size exponent, a path cost, and a fallback sun geometry. A biome's kind was chosen by reading its def and its sheet, not its name.

| BiomeDef | kind | evidence |
|---|---|---|
| `RM_LongShade` | overhead | owner ruling, ideation doc: "overhead sun here, so parasols and tents work" |
| `RM_Stillsand` (the Deep Desert; the def merges deep_desert + dune_sea) | lowSun | "a low sun in the deep desert, so a shield you stand behind works" |
| `RM_FloodedCanyon` (the Cracked Lands) | lowSun | the_cracked_lands.md: "the open flats lethal by exposure", "Shade is in the cuts", sun at about 21° |
| `RM_TheScald` | ambient | the_scald.md: "A crater sea that boils. Volcanic heat rises under it" |
| `RM_TheForge` | ambient | the_forge.md: "one volcanic massif", "lava … in scalding bursts" |
| `RM_Greentide` | ambient | the_greentide.md: "roiling, ground-hugging, HOT fog" |

**Excluded**, because their heat is not extreme or the hazard is something else:
- `RM_Pyrelands`: its danger is fire ecology.
- `RM_Contagion`: its danger is UV and toxin, not heat.
- `RM_Wasteland`: runs from -35 to 30°C.
- `RM_TheSump`: cold.

**Needs a ruling:**
- `RM_RustCathedral`: it has the highest sun on the planet, but its heat also comes from a Scald coolant loop. That fits none of the three kinds cleanly.
- **RUT_ twins are not wired.** Only the RM_ tier ships. `RUT_Desert` and `RUT_ExtremeDesert` are frozen shells.

## §3 Directional shade grid
The grid now has a roof layer and a cast layer.
- **Where the sun direction comes from**, in order:
  1. the pinned sun, so the shade you see is the shade that counts;
  2. the heat biome's own substellar geometry;
  3. the old radius-2 ring, for biomes that have no sun direction at all.
- **Shadow length** is the caster's `staticSunShadowHeight` (or its fillPercent, or 0.5 × a big plant's visual size) × cot(elevation). It is capped at 16 cells, and the far tip is 0.6 shade.
- **Setting:** "Shadows fall one way".

## §1 Sun exposure feeds vanilla heat
- **How it works:** a postfix on the `Thing.AmbientTemperature` getter, for pawns only, adds `exposure × heatOffsetC × strength × (1/bodySize)^0.5`, clamped. Because vanilla's comfort, Heatstroke and burn checks all read that number, the sun reaches them without a new hediff.
- **Exposure by kind:**
  - overhead: 1 − max(roof, cast)
  - lowSun: 1 − max(thick rock roof, cast), so a built roof does not protect
  - ambient: 1
  - an enclosed room (one that does not use the outdoor temperature) is 0 for every kind.
- **The heat offsets per biome are invented first values** (30 / 35 / 25 / 15 / 15 / 8°C).

## §7 Mod Settings (Creature Behaviors, entry 39)
- **Sun heat**: the master toggle, with a strength slider from 0 to 300%.
- **Shadows fall one way**, **Walk shade to shade** (with its own avoidance slider) and **Sun load bar**: one toggle for each feature.

## §4 Sun-cost pathing
- **The one path patch** is a postfix on `Pawn_PathFollower.GenerateNewPathRequest`. It attaches a shared per-map `RM_SunPathCustomizer` (a NativeArray of ushort, cost = exposure × 20 × dial) to requests from undrafted pawns. Drafted pawns and ambient maps are not affected.
- **The cost grid is rebuilt as a new object on every grid recompute**, because the path finder caches by object identity and worker threads read the array. The old one is disposed one rebuild later.

## §6 Sun-load bar
`RM_Gizmo_SunLoad` appears for a single selected pawn on a sun-heat map. The bar shows the pawn's Heatstroke severity, and the line under it reads "In sun: +N°C" or "In shade". The tooltip explains the biome's heat kind.

## Verification
- The Creature Behaviors build succeeds with 0 errors and 0 warnings. The DLL is committed with its `.srchash`.
- All six edited biome XML files parse.
- `selftest_sun_heat.py` passes 11/11. It covers sun vs shade vs roofed for each kind, scored against vanilla's own HediffGiver_Heat curve, plus body size, path cost (a Dijkstra route that hugs the shade), and the directional cast.
- `run_selftests.py`: 77/79. The only failure is the known `selftest_deployed_biome_refs`, and one test is unmeasured (`bridgetools/selftest_tool_metadata`).

## Remaining
- **§5 rest-dash-rest animal AI:** the shade-patch graph (`RM_MapComponent_ShadePatches`), the Rest and Dash job givers, and the pause at the rim. When built, the dash giver should read `RM_ShadePerception.PerceivedShadeAt`, so the mirrak counts.
- **§6 drafted-pawn ring:** the dash-radius ring around a drafted pawn. It needs the patch graph first.
- **Moving casters:** the gloomcast's `RM_Comp_ShadowCaster` is not in the directional grid yet.
- **Rulings owed:** the heat kind for `RM_RustCathedral`, and whether the RUT_ twins get the extension.
- **Quicktests:** a Long Shade map, a steam or volcanic map with no relief from shade, and a low-sun map where a roof does not protect. Then an owner-watched session to rule on how strict it should be (the offsets and the path cost).
- **Watch in a quicktest:** undrafted pawns routed round the sun could fall into a seek-safe-temperature loop outdoors. And a sun-heat biome without a pinned sun still has a vanilla night, while the heat itself does not follow the day/night cycle.
