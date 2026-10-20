# World parity: canonical Ash'karr start vs new dev world (2026-10-20)

**Old:** `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\CANONICAL_ASHKARR_START_2026-09-12.rws` (edited in place to 2026-10-09)
**New:** `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\ASHKARR_DEV_START_2026-10-20_RECORDLINKS.rws`
Both copied read-only to `D:\ClaudeWork\rimmandrake\scratch\parity\` (`canon.rws`, `dev.rws`, reader `load.py`). Decoded with
`worldview.PlanetView` (per-tile arrays, links, objects), `worldmap.mutator_entries`, and `feature_drawcenter_audit.py`.
Nothing written, no game, no bridge. `world/ASHKARR_WORLDMAP_tiles.csv` used only as a RECORD to name the 3 biome hashes the dump cannot resolve.

## Instrument probes (done first; the earlier renderer read 0% water and 0 mutated tiles)
- **Water.** `worldview` reports 0 water on the OLD save: `water_biomes()` reads the NEW dump, which lacks the old water biome names. Not zero. Truth: record `water=1` is 1,448 tiles; the old save's GreySea 472 + TwilightSea 607 + TheScald 312 + PropaneLake 57 = 1,448; the new save reads 1,448 directly. The 0% was an instrument miss.
- **Biome hashes.** 3 hashes in the old save (59367, 65189, 58457) resolve to nothing in the current dump; the record names them RUT_ForsakenCrags 1,135 / RUT_PoisonForest 546 / ZBiome_Grasslands 222, and the new save puts RM_Abyss / RM_Cauldron / RM_Pyrelands on exactly those tiles. The old save also reads 44 tiles as `RM_FloodedCanyon` where the record says RUT_TheForge (new save: RM_TheForge 44): a hash read against the wrong mod set, the exact trap `worldmap.py` warns of. Per-tile biome parity below uses the record to name them.
- **Mutators.** Old 27,856 entries over 14,421 tiles, 26 retired hashes (2,142 entries) unresolved; both arrays are length-checked by `mutator_entries`. New 56,070 over 19,642 tiles. Not zero, not a query bug.
- **Rivers/roads** decoded with full `unresolved`/`broken` lists empty on both saves.

## Parity table

Verdict: **SAME** identical, **INTENT** intentionally different (cited), **UNEXPL** unexplained.

| family | old (canon) | new (dev) | verdict | evidence / citation |
|---|---|---|---|---|
| tile count, geometry | 21,872; subdivisions 7, radius 100 | same | SAME | `PlanetView` |
| planet type, preset | AW TidallyLocked, preset TidallyLocked | same | SAME | world XML |
| coverage, rainfall, temp, axial tilt, pollution setting | 1 / Normal / Normal / Normal / 0.05 | same | SAME | `<info>` |
| game version | 1.6.4871 rev591 | same | SAME | |
| temperature per tile | | | SAME | 0 of 21,872 differ (1,473 distinct values, so the probe sees) |
| rainfall per tile | | | SAME | 0 differ (285 distinct) |
| swampiness per tile | | | SAME | 0 differ (84 distinct) |
| biome per tile | 27 biomes | 27 biomes | INTENT | 21,872 of 21,872 tiles map old to new through one clean 1:1 rename (no tile splits); counts identical per biome; owner's biome remake `design/RimMandrake/world_remake_2026-10-19/` and `donor_retirement_plan_2026-10-02.md`. RUT_Umbra 2,531 stays RUT_Umbra: an open owner call (runbook G7). Zero-tile biomes are not defects. |
| hilliness | | 3,699 tiles differ | INTENT | The set equals `world/ASHKARR_MOUNTAINS_2026-10-20_plan.json` exactly (3,699). `design/Jawa/worldbuilding/mountain_system_2026-10-20.md`. Pass 2 (805 tiles) is plan only and not applied (0 of 805 at target). |
| elevation | | 34 tiles differ (max +187 m) | INTENT | equals the same plan's 34 elevation entries |
| river links | 326 (Creek 170, River 62, HugeRiver 51, LargeRiver 43) | identical edge set and defs | SAME | 0 edges differ; the 2026-10-20 "record links restored" fix |
| road links | 1,242 (DirtRoad 527, DirtPath 321, StoneRoad 287, AncientAsphaltHighway 107) | identical edge set and defs | SAME | 0 differ |
| river flow numbers (`tileRiverDistances`) | nonzero on 1,127 tiles, max 95 | nonzero on 277 tiles, max 5 | **UNEXPL** | 1,117 tiles differ; see U4 |
| water tiles | 1,448 (4 sea biomes) | 1,448 (RM_GreySea, TwilightSea, TheScald, TheChill) | SAME | probe above |
| world features: names, count, per-tile membership | 71 | 71, identical names, 0 tiles differ | SAME | |
| world features: def | `WB_MapLabelFeature` | `Desert` | INTENT | Worldbuilder absent from the PAINT list (`Transient/world_remake_run_2026-10-20/RESULTS.md` S3) |
| world features: `drawCenter` (where the label sits) | 61 of 63 single-piece correct (2 wrong: Deadstone, Dune Sea) | 11 correct, **52 wrong** | **UNEXPL** | `feature_drawcenter_audit.py`; see U1 |
| world features: size | integer hierarchy (Fall Line 26) | engine-computed (Fall Line 16.8) | **UNEXPL** | 5 features differ by more than 1 (Fall Line 26 to 16.81, Salt Gate 10 to 6, Abandoned Mines 10 to 7.9, Hollow Verge 10 to 8.5, Quiet Ground 10 to 8.9); the rest within 0.5; see U1 |
| settlements, NPC | 95 | 95, same tile, name and faction def for all 95 | SAME | |
| settlement, player | "Zeddo's Salvage Yard" tile 17007 | "Colony" tile 17011 | INTENT | RESULTS.md morning call 2 (17007 refused: adjacent to a stamped NPC settlement) |
| settlement, orbital | none | `Luminary Dock` (TradersGuild) tile 421 | **UNEXPL** | see U6 |
| settlements per faction | Outlander 27, Hutt 12, Wildsteam 9, Tribe 9, FreeDroid 7, Helix 7, Deepwater 6, Geonosian 5, Pirate 4, Junkers 4, Empire 3, Moot 2 | same | SAME | |
| faction roster | 21 in `<info>`; AM_EnemyPirate, TribalHostile, DP_GenericHostile, CASacrilegHunters | RM_Faction_CombHolds, RM_Thozziks, RSW_PustuleHornets, RUT_GreentideAntFaction; donor four gone | INTENT | donor retirement; runbook S7; Greentide made by tool (RESULTS morning call 6) |
| faction display names | Mechanoid "Totharth Mechhive", Insect "Hive", Guild "Voidborn Bazaar", Salvagers "The Comet Party" | "Slinox Mechhive", "Sorne Geneline", "Space Exchange", "The Celestial Rogues" | UNEXPL (cosmetic) | rolled names; U8 |
| landmarks: count, tile, def | 3,008 | 3,008, identical except 26 | INTENT | the 26 are the retired-donor ports (sw_Sarlacc 8 to RSW_Sarlacc, AB_TarLakes 7 to RM_TarLakes, sw_DeadSarlacc 7, AB_MagmaticQuagmire 3, AB_QuicksandPits 1): `retired_mutators_port_2026-10-19.md` |
| landmark names | 3,008 names | 0 of 3,008 match | **UNEXPL** | the record CSV carries no name column; see U5 |
| tile mutators: retired donor ones | 26 hashes, 2,142 entries | ported 1:1 to RM_/RSW_ (RM_AmbientRadiation, RM_DerelictClusters, RM_OllathrixNest, RM_AncientFreezingVent, RSW_WildTattooinePlants 1,403 ...) | INTENT | `retired_mutators_port_map.json` |
| tile mutators: everything else | 27,856 entries total, 14,421 tiles, 162 defs | 56,070 entries, 19,642 tiles, 210 defs | **UNEXPL** | about 28,400 extra entries, 75 defs the old world never had (VEE_* about 400 each); see U2 |
| world objects: infestation sites | 20 `BI_InfestationWorldObject` | 0 | UNEXPL | see U7 |
| world objects: big asteroids | 40 `DeepOrbit.BigAsteroidMapParent` | 0 | UNEXPL | see U7 |
| world objects: basic and ice asteroids | 37 + 3 | 37 + 3 | SAME | |
| world objects: furnace herds | none | 2 `WorldObject_RM_FurnaceHerd` | INTENT | new Pyrelands content |
| layers | Surface, Orbit, Orbit2 (radius 260, DeepOrbit) | Surface, Orbit, `RM_SeabedLayer` (radius 100) | INTENT | Diving Interaction 2026-09-26; `worldmap_in_game_audit_2026-10-20.md`; DeepOrbit "until fixtures retire" (`11_ruled_keepcut.md`) |
| pollution per tile | 1,658 tiles nonzero | 1,199 nonzero; 2,716 tiles differ | UNEXPL (seed-random) | U9 |
| seed | `raven` | `safety` | INTENT | generation #2 of the remake run; the world is stamped, the seed no longer shapes content |
| initial map size | 325 x 325 | 250 x 250 | **UNEXPL** | see U3 |
| mods in save | 616 | 324 | INTENT | donor retirement; saves load on the PAINT list (RESULTS End state) |
| `worldGenerationData` block | present | absent | UNEXPL (inert) | engine-written at generation; no consumer found |
| difficulty | Hard | Medium | not world | game setting |

Counts (table rows): SAME 14, INTENT 12, UNEXPL 12 (7 player-visible, 5 cosmetic or inert), not-world 1.

## UNEXPLAINED, ranked by how visible they are to a player

**U1. Region labels hang over the wrong ground, and the size hierarchy is gone.** On the new world 52 of 63 single-piece region labels sit on ground belonging to a different region (worst: Scald 154 degrees away, Cratercrown 148, Fuelmere 134, Dew Horn 124). The old world had 2 wrong (Deadstone, Dune Sea). Region names are the player's map; this is visible on the first glance at the globe. Fall Line label size 26 became 16.8 and four 10-size labels shrank (Salt Gate 6). Likely cause: features were re-created on the new world by the stamp without Worldbuilder (def is now `Desert`), so drawCenter and size are engine defaults, not the ruled values. **Next measurement:** read how `w9_run.py` creates features (does it set `drawCenter`/`size`), then `feature_drawcenter_audit.py dev.rws --out <NEW copy>` as a dry fix and re-audit to 0 WRONG; restore sizes from the old save by name (71 names match).

**U2. About 28,400 engine-rolled tile mutators that were never authored.** 56,070 entries against the old 27,856; 75 mutator defs the old world never held, VEE_LargerRegion 1,154, VEE_SmallerRegion 1,061, a dozen VEE_* wildlife/vent ones at 380-480 each, Mountain +2,062 and Caves +1,092 (the extra Mountain follows the new hilliness). RESULTS.md S8 shows the stamp wrote 27,645 placements over 14,397 tiles, close to the old 27,856, and cleared only stale Coast (640) and 49 marine ones, so the rest is what world generation rolled for seed `safety` before the stamp. This contradicts the frozen-world rule (nothing rolled, one hand-made world). Visible as tile tooltips and as map content on landing. **Next measurement:** stamp-minus-save diff: take `ASHKARR_WORLDMAP_mutators.csv` through `retired_mutators_port_map.json`, subtract from the dev entries, confirm the remainder (about 28.4K) and which defs; then decide a strip step in `w9_run.py` (owner call: strip, or accept).

**U3. Starting map is 250 x 250, was 325 x 325.** `<initialMapSize>` in the new world info. Player-visible on the first map. No ruling found either way. **Next measurement:** search `standing_rulings.md` and the owner card log for a map-size ruling; if none, ask the owner (one question). The scenario page sets it, so a re-run is not needed if it is a game setting.

**U4. River flow numbers collapsed.** `tileRiverDistances` is the riverDist that orders which end of a river link is downstream (memory `river-direction-is-riverdist`). Old: 1,127 tiles nonzero, up to 95 hops. New: 277 nonzero, max 5. 1,113 of the 1,117 differing tiles are lower in the new world, 854 are zero. Same edges, so rivers render, but any river code that reads downstream direction (river mutators, TileMutatorWorker_River ordering) sees a flattened network. Mouth-first stamping in the remake (stage 2, "rivers mouth-first") should have set it. **Next measurement:** per river, walk mouth to head in both saves and compare monotonic riverDist; check whether the 2026-10-20 "record links restored live" step re-wrote links without distances.

**U5. Landmark labels renamed.** 0 of 3,008 landmark names survive (old "Prime Dove Village", "Orangeneedle Wastes"; new "Fort Aninum", "Cristina's Base"). The record has no name column, so the old names were never captured; the stamp lets the game name them. Settlements kept their names. Visible when hovering landmarks. **Next measurement:** confirm `w9_run.py` landmark stage never passes a name; decide whether the old names (in the old save) are a requirement, then carry them by tile.

**U6. A new orbital settlement, "Luminary Dock" (TradersGuild, tile 421).** Not in the old world; the engine adds the guild at worldgen. Visible as an extra orbital contact. **Next measurement:** read its layer from the world-object XML; check if the old world's TradersGuild had none on purpose (faction hidden / `requiredCountAtGameStart`).

**U7. Missing: 20 infestation sites and 40 DeepOrbit big asteroids.** The infestation sites are random Better Infestations content (Better Infestations stays loaded, its events silenced, `RETIREMENT_WAVE_1.md` C09). The 40 asteroids lived on the old Orbit2 layer that is now the seabed layer. Low player visibility (orbit and quest-site content). **Next measurement:** confirm DeepOrbit is on the PAINT list and whether big asteroids should exist.

**U8/U9. Cosmetic or inert:** four rolled faction names differ; per-tile pollution differs on 2,716 tiles (seed-rolled; setting is 5% in both); `worldGenerationData` absent.

## Not an issue (read this before re-filing)
Biomes on 0 tiles are expected until the single paint. The dev world's biome distribution equals the old one tile-for-tile under the rename. Temperature, rainfall, swampiness, rivers, roads, water, the 95 NPC settlements, feature membership and landmark placement are identical.
