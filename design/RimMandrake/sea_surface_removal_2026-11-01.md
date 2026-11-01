# Sea surface removal, 2026-11-01: the owner's list

Owner ruling, 2026-11-01, verbatim: *"Please perform the same modification to The Chill, the Twilight Sea, and the Grey Sea. You are either on their sea floor, or you are on their beach. There is no 'on their surface' location."* Precedent: commit 66c228ef46 (the Scald).

## What was done

Every statement in the three seas' design sheets, their shared law sheet (`terminator_sea.md`) and the comments under `src/RimMandrake/TerminalBiomes` that gave the sea's SURFACE as a place now says the shore (beach) or the sea floor. Uses that are not a place were left alone: the surface of a material or a brine pool, the surface world and its people, 'engine surface', 'surface sunlight' (an engine term), land rivers (`SURFACE_RIVER_WEIRS_1`), and every verbatim owner quote. No def's behaviour was changed.

**The Chill's biome sheet** is `design/Jawa/worldbuilding/biomes/the_propane_lakes.md` (`RUT_PropaneLake`, shipped as `RM_TheChill`); it had no 'surface and shore' scoping of its own.

**An engine fact that already matches the ruling:** `RM_GreySea`, `RM_TwilightSea` and `RM_TheChill` are all `impassable` + `isBackgroundBiome`. So the only map that carries each sea biome is its floor pocket map, and the beach is the neighbouring land tile. Vanilla `Rain` was already removed from `RM_GreySea` (GREYSEA_SALT_SNOW_WEATHER_1) and from `RM_TwilightSea` (TWILIGHT_SEA_FIX_IT_RAINS_UNDERWATER).

## Judgement calls: 17 (each needs your word)

| # | file:line | old | new | open question |
|---|---|---|---|---|
| 1 | `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\terminator_sea.md`:12 | governs the seas' **SURFACE and SHORE**, | governs the seas' **SHORE (the beach)**, | The solitary / no-schools / sparse-roster law was 'surface and shore'. With no surface it binds the beach only; on a beach 'no schools' is nearly vacuous. Should it also bind what is FISHED from the beach (catch tables), or the Grey floor (which already inherits it by the_grey_deep.md §0)? |
| 2 | `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\terminator_sea.md`:226 | - ⛔ **No rain, no thunderstorms, no snow, no ice.** | (unchanged) | UNCHANGED wording. With no surface this is beach weather. But the beach is the neighbouring LAND tile, whose weather comes from its own land biome, not from the sea BiomeDef (which only reaches the floor). Does the ban bind the shore tiles' land-biome weather, the floor's weather, both, or neither? |
| 3 | `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_twilight_deep.md`:125 | **No crowding above the roof** — the surface/shore biome keeps every | **No crowding on the shore** — the beach keeps every | Ban 1 forbade crowding 'above the roof' (on top of the waveglass / open water). That place no longer exists, so the ban now forbids crowding on the beach only. Is anything still forbidden for the open water between the beach and the waveglass edge (e.g. what the beach can SEE or fish)? |
| 4 | `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep.md`:284 | that ban is about WATER weather on the SURFACE, and gives its | that ban is about WATER weather on the SHORE (beach), and gives its | The salt-snow ruling rested on 'the ban is surface weather; this is floor weather'. Re-scoped to beach weather the floor salt-snow stays outside it. Open: is water weather on the FLOOR (rain underwater) banned by this sheet too, or only by the owner's separate 2026-10-16 'sea floor... no rain' ruling on the Twilight? |
| 5 | `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep_content_2026-09-26.md`:399 | SURFACE. This weather is on the floor, | SHORE (beach). This weather is on the floor, | Same as the_grey_deep.md:284 (no-rain ban re-scoped from surface to beach). |
| 6 | `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep_content_2026-09-26.md`:691 | ban is about water weather on the surface | ban is about water weather on the shore (beach) | Same as the_grey_deep.md:284. |
| 7 | `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep_content_2026-09-26.md`:694 | "No snow" stands for the surface; salt | "No snow" stands for the shore; salt | This is the text of a 2026-09-26 RULING ('No snow stands for the surface'). Re-scoped to the shore; confirm the ruling is meant to read that way. |
| 8 | `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_propane_lakes.md`:287 | **"Aurora curtains over a black mirror sea, with blue flame running on the ice."** | (unchanged) | UNCHANGED (no 'surface' word). The Chill's image, the Burners 'killer on the ice' (§4) and the hoolen 'runs the frozen sheets between the pools' all place life ON the lake's ice. Is the ice a beach (a place a pawn can stand), part of the floor world, or a surface place that no longer exists? |
| 9 | `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_propane_lakes.md`:148 | - **Fuel snow** — hydrocarbon and ammonia precipitation; the crystal flora's feed. | (unchanged) | UNCHANGED. §4b weather is unscoped. `RM_TheChill` is impassable + background, so its BiomeDef weather only ever reaches the floor pocket map. Is §4b beach weather (then it needs a carrier on the shore tiles), floor weather, or both? |
| 10 | `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_chill_warlab_routes_spec_2026-09-27.md`:406 | the lake and surface unchanged, | the lake and its shore unchanged, | 'the lake and surface unchanged' after Route 2: read as the shore (beach). If it meant the lake's top/ice, say so. |
| 11 | `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_chill_warlab_routes_spec_2026-09-27.md`:513 | A surface-side hot-source story may still exist above the crust, | A shore-side hot-source story may still exist on the beach, | 'above the crust, where the atmosphere is' implied a place on top of the lake. Re-scoped to the beach. Is a hot-source story on the lake's ice/crust still possible, or is the beach the only air-side place? |
| 12 | `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_propane_lake_flora_pass_2026-09-27.md`:472 | bells catch the fall at the surface; | bells catch the fall high in the column; | The oovu's habitat was 'at the surface' of the fuel. Moved to 'high in the fuel column' (the floor agenda already said it 'lives in the fuel column — fine on the floor'). The player-facing descriptions still say 'rides at the surface of the fuel' (RM_TheChillCatch.xml:141, RM_TheChillFloorLife.xml:370) — filed for FOUNDRY, not changed. |
| 13 | `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_propane_lake_floor_sitting_agenda_2026-10-02.md`:250 | The floor and the lake's surface share one biome | The floor and the lake's world tile share one biome | Q1 (ruled, CHILL_FLOOR_CAST_TRIM_1 done) moved hoolen and vaunoom off the floor to wait for 'a surface home'. That home is now the beach, or nowhere: the vaunoom is by its own description a hunter of the lake's surface wake (V-wake). Does the vaunoom get a beach home, a floor home, or is it cut? The Q1 option text below line 250 is left as asked (historical); the banner at the top says how to read it. |
| 14 | `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\ThingDefs_Races\RM_TheChillFauna.xml`:223 | ice-sheet rim skimmer, the SURFACE face. | ice-sheet rim skimmer, the SHORE face (owner 2026-11-01: no surface place). | See the_propane_lakes.md:287 (is the ice sheet a beach?). |
| 15 | `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\ThingDefs_Races\RM_TheChillFloorLife.xml`:364 | jelly riding the fuel's surface, catching | jelly riding high in the fuel column, catching | See the_propane_lake_flora_pass:472. |
| 16 | `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\WeatherDefs\RM_GreySaltSnow.xml`:50 | about WATER weather on the SURFACE and gives | about WATER weather on the SHORE (beach) and gives | Same as the_grey_deep.md:284. |
| 17 | `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\BiomeDefs\RM_TheChill.xml`:56 | they wait for a surface home at the surface sitting. | they wait for a shore home at the shore sitting (CHILL_SURFACE_SITTING_1). | See the floor agenda:250 (vaunoom's home). |

## Plain re-wordings: 58 (no change to what anything forbids)

| file:line | old | new |
|---|---|---|
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\terminator_sea.md`:16 | by the owner's ruling). Neither world leaks into the other. | by the owner's ruling). Neither world leaks into the other.  🔴 **Amended 2026-11-01 — there is no sea surface** (owner, 2026-11-01: *"You are either on their sea floor, or you are on their beach. Ther… |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_twilight_deep.md`:23 | surface and shore stay with `terminator_sea.md`). | the shore (beach) stays with `terminator_sea.md`; there is no surface location, owner 2026-11-01). |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_twilight_deep.md`:31 | govern the SURFACE and SHORE, where they | govern the SHORE (the beach), where they |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_twilight_deep.md`:95 | (the surface ban broken below the roof, | (the shore's no-schools ban broken below the roof, |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_twilight_deep.md`:115 | the surface above stays solitary and | the shore stays solitary and |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_twilight_deep.md`:126 | nothing schools, herds, or thickens up there. | nothing schools, herds, or thickens there. |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_twilight_deep.md`:212 | `terminator_sea.md` (surface law, scoped); | `terminator_sea.md` (shore law, scoped); |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_twilight_deep_content_2026-09-26.md`:258 | `terminator_sea.md`'s surface bans | `terminator_sea.md`'s shore bans |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_twilight_deep_content_2026-09-26.md`:857 | on **tile 2919, a surface | on **tile 2919, an |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_twilight_deep_content_2026-09-26.md`:858 | the Hold is a *surface* seat and stays one. | the Hold is a *shore* (beach) seat and stays one. |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_twilight_deep_content_2026-09-26.md`:959 | (surface and shore only, | (shore only, |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_twilight_deep_content_2026-09-26.md`:968 | the surface bans on lush/open-close flora | the shore bans on lush/open-close flora |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_twilight_deep_content_2026-09-26.md`:973 | that was against the surface ban anyway | that was against the no-rain ban anyway |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_twilight_deep_content_2026-09-26.md`:1022 | the Hold is a surface | the Hold is a shore |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_twilight_deep_content_2026-09-26.md`:1023 | seat and its cast has surface hooks). | seat and its cast has shore hooks). |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_twilight_deep_content_2026-09-26.md`:1059 | (the surface biome's catch, | (the shore's catch, |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_twilight_deep_content_2026-09-26.md`:1094 | **Fix the surface defect** | **Fix the rain defect** |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep.md`:20 | plus its ice fringe; surface and shore canon | plus its ice fringe; shore (beach) canon |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep.md`:264 | the surface sea is `allowRivers false`) | `RM_GreySea` itself is `allowRivers false`) |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep.md`:268 | a flat pan. Surface-and-shore, so it lands | a flat pan. A shore feature, so it lands |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep.md`:290 | which IS against the surface ban — fix it alongside. | which IS against that ban — fix it alongside (done: removed, see `RM_GreySea.xml`). |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep.md`:494 | surface canon's vigil. | shore canon's vigil. |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep.md`:575 | (surface and shore, inherited | (shore, inherited |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep_content_2026-09-26.md`:91 | this is the SURFACE shore, | this is the shore (beach), |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep_content_2026-09-26.md`:201 | This is a surface-and-shore statement | This is a shore statement |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep_content_2026-09-26.md`:383 | a pocket-map weather, not a surface one. | a pocket-map weather, not a beach one. |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep_content_2026-09-26.md`:402 | which IS against the surface ban and | which IS against that ban and |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep_content_2026-09-26.md`:522 | the surface sea. In engine terms | the sea above. In engine terms |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep_content_2026-09-26.md`:753 | the surface sea has `allowRivers false`. | `RM_GreySea` has `allowRivers false`. |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep_content_2026-09-26.md`:835 | **Fix the pre-existing surface defect** | **Fix the pre-existing rain defect** |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep_content_2026-09-26.md`:839 | the surface reads as the Grey | the shore reads as the Grey |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_grey_deep_content_2026-09-26.md`:864 | step 5, surface-side, and Q4. | step 5, shore-side, and Q4. |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\grey_deep_sitting_agenda_2026-09-27.md`:676 | is not the banned surface weather | is not the banned shore weather |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\grey_deep_sitting_agenda_2026-09-27.md`:725 | impassable-surface with a walkable pocket floor | impassable on the world map, with a walkable pocket floor |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\grey_deep_pool_sentinel_2026-09-27.md`:58 | fishable from the surface shore | fishable from the shore |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_propane_lakes.md`:101 | The lab beneath the surface has survived | The lab beneath the lake has survived |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_propane_lakes.md`:201 | lake's surface, directly over the Impact Site | lake, directly over the Impact Site |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_propane_lake_floor_sitting_agenda_2026-10-02.md`:47 | the **surface** gets its own separate sitting | the **shore** (beach) gets its own separate sitting |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_propane_lake_floor_sitting_agenda_2026-10-02.md`:122 | ### 1.6 Surface-side mechanics | ### 1.6 Shore-side mechanics |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_propane_lake_floor_sitting_agenda_2026-10-02.md`:144 | no (surface sitting) | no (shore sitting) |
| `D:\Luke\dev\RimMandrake\design\Jawa\worldbuilding\biomes\the_propane_lake_floor_sitting_agenda_2026-10-02.md`:151 | the same BiomeDef as the surface tile | the same BiomeDef as the sea's world tile |
| `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Source\RM_PlaceWorker_ChillFloorOnly.cs`:8 | never the surface/shore map that carries the same biome) | never any non-pocket map carrying the same biome; there is no surface place, owner 2026-11-01) |
| `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\ThingDefs_Items\RUT_TwilightFish_Niim.xml`:12 | shared by the ruled no-fish SURFACE | shared by the ruled no-fish non-floor side ("surface" in 2026-09; owner 2026-11-01: no surface place) |
| `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\ThingDefs_Items\RUT_TwilightFish_Niim.xml`:14 | would make the surface fishable too | would make that side fishable too |
| `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\ThingDefs_Items\RUT_TwilightFish_Niim.xml`:19 | no surface/deep split exists on disk | no non-floor/floor split exists on disk |
| `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\BiomeDefs\RM_ChillCrater.xml`:42 | under a live surface map, | under a live non-pocket map, |
| `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\ThingDefs_Races\RM_TheChillFloorLife.xml`:615 | surface-spawned Tarnn. | non-pocket-map Tarnn. |
| `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\ThingDefs_Items\RM_TheChillCatch.xml`:8 | (surface wildAnimals only, verdict 4) | (verdict 4; off the floor roster since CHILL_FLOOR_CAST_TRIM_1, awaiting a shore home) |
| `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\WeatherDefs\RM_GreySaltSnow.xml`:61 | It is not a surface weather by the back door. | It is not a beach weather by the back door. |
| `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\ThingDefs_Races\RM_GreySeaShoreLife.xml`:23 | this is a surface/near-surface glider, built plain. | this is a shore-shallows glider, built plain. |
| `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\ThingDefs_Items\RM_TwilightSeaCatch.xml`:6 | ten-species surface catch | ten-species catch |
| `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Source\RM_MapComponent_WellLedger.cs`:23 | the surface tile) | the sea's world tile) |
| `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\ThingDefs_Plants\RM_GreySeaSaltBlade.xml`:26 | SHORE/SURFACE feature | SHORE feature |
| `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\BiomeDefs\RM_TheChill.xml`:54 | (surface animals) | (shore animals by their descriptions) |
| `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\TerrainDefs\RM_GreySeaTerrains.xml`:9 | GREYSEA_SHORE_MUTATOR_SPECIFICS_1  (surface) | GREYSEA_SHORE_MUTATOR_SPECIFICS_1  (shore) |
| `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\TerrainDefs\RM_GreySeaTerrains.xml`:80 | SURFACE — the crusted white shoreline. | SHORE — the crusted white shoreline. |
| `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\TerrainDefs\RM_GreySeaTerrains.xml`:115 | the surface sea is | RM_GreySea itself is |
| `D:\Luke\dev\RimMandrake\src\RimMandrake\TerminalBiomes\Defs\IncidentDefs\RM_SuulkArrival.xml`:11 | world-surface tile AND | world-map tile AND |

## Not changed, filed for FOUNDRY

- Player-facing description text still placing life at the surface: the oovu "rides at the surface of the fuel" (`RM_TheChillCatch.xml:141`, `RM_TheChillFloorLife.xml:370`). Def text, not a comment, so it was left for FOUNDRY.
- The ledger item `CHILL_SURFACE_SITTING_1` keeps its id (ids are permanent); a note on it says its scope is now the shore (beach).
- Leftovers of the Scald precedent that 66c228ef46 did not reach: comments citing the withdrawn ban 4 (`RUT_ScaldWater.xml:349`, `RUT_ScaldMargin.xml:46`, `RM_ScaldFloorFauna.xml:75`) and the player-facing `RUT_ScaldWater` descriptions "dead calm on the surface ... nothing swims here". Outside this brief; filed for FOUNDRY.
