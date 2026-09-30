# SEA_DIVE_FLOOR_TERRAIN_1 — per-sea habitat bands on the dive floor

Status: built offline, DLL rebuilt clean, XML parses, NOT live-verified (proof script written, not run).

## Defect
`GenStep_SeaFloorTerrain` (the only terrain step in every `RM_SeaDiveGenerator_*`) painted ONE
constant terrain on every cell, so no terrain carrying a floor-flora `wildTerrainTags` tag ever
existed on the map a player dives to. Also: the Scald and Chill generators had no vanilla `Plants`
GenStep at all, so their `wildPlants` could not generate even with habitat present.

## Mechanism
- `RM_SeaFloorBandsExtension` (new, `src\RimMandrake\DivingInteraction\Source\RM_SeaFloorBandsExtension.cs`),
  a DefModExtension on the **MapGeneratorDef** — so it is gated on the dive map by construction
  (a surface / quicktest map of the same biome never reads it). Fields: `baseTerrain`, nested
  `bands` (terrain + exact share of cells), `noiseFrequency`, `minConnectedShare`.
  Terrains named by string, resolved `GetNamedSilentFail` (absent mod = band skipped, one warning).
- `GenStep_SeaFloorTerrain` reads `map.generatorDef` (RimSage: `Verse.Map.generatorDef`), paints the
  base, then ranks all cells by one Perlin field and hands out bands top-down, so band 0 is each
  patch's core and later bands ring it.
- Walkability pass: if a band is Impassable, flood-fill walkable cells; stranded pockets are filled
  into the pool; if the main region is < 90% of walkable cells, every impassable band cell reverts
  to the next walkable band outward.
- Mod setting `seaFloorBandsEnabled` (default ON, labelled "map generation") in `RM_DivingSettings`.
- `Plants` added to the Scald and Chill generators (vanilla `Plants` order 900; RimSage).

Engine facts checked via RimSage: `PlantUtility.CanEverPlantAt` refuses a wild plant whose
`WildTerrainTags` don't overlap the cell terrain's tags, and does NOT require a standable cell;
`GenStep_Plants` -> `WildPlantSpawner.CheckSpawnWildPlantAt` has no standability gate, and every
flora def here is `completelyIgnoreFertility`, so fertility-0 floors pass.

## Per-sea floor
| Sea | base | bands (core -> ring) | serves |
|---|---|---|---|
| Scald | RM_SeaFloorGround | RUT_ScaldWaterOceanShallow 5% (boiling, burns, RM_CrowncarpetBed) -> RUT_ScaldMargin 12% (cool mat ring, RUT_ScaldMarginMat) | RM_Crowncarpet; both walkable |
| Chill | RM_ChillIceBedrock | RM_TheChillDeep 5% (liquid, Impassable, RM_TheChillBed) -> RM_SolidPropane 15% (crust, standable, RM_TheChillShelf) | all 10 Chill flora |
| Grey Sea | RM_SeaFloorGround | none — its tag-gated flora (RM_GreyBrineChannel / RM_GreyChimneySeep) is already painted by GenStep_GreySeaFloorDressing | unchanged |
| Twilight Sea | RM_SeaFloorGround | none | its 3 flora carry no terrain tags |

## Gaps reported, not invented
- **The Chill has no WALKABLE bed-tagged terrain in src.** `RM_TheChillBed` exists only on
  `RM_TheChillDeep` / `RM_PropaneDeep` (both Impassable). So the six bed species grow in liquid
  pools the crew walks around but cannot stand in to harvest. If bed flora must be reachable,
  that needs a standable bed terrain (a design call, not made here).
- **The Twilight Sea has no seabed terrain of its own** (and no tag-gated flora), so its floor
  stays one plain terrain.
- The rime terraces (order 920) paint over whatever is under them, including bands — by design.

## Proof (not run)
`python.exe src/RimMandrake/bridgetools/prove_sea_dive_floor.py [TheScald GreySea TwilightSea TheChill]`
on a throwaway quicktest: re-biomes the current tile per sea, sets `requireGravEngine=false` for the
run, spawns an `RM_SeaDiveHatch`, orders a colonist `EnterPortal` (the real
`MapPortal.GetOtherMap -> GeneratePocketMap` path), then censuses the new pocket map's terrain and
plants and prints PASS/FAIL/UNMEASURED per sea. Settings and tile biome restored at the end.
Needs the rebuilt DLL deployed first.

## Verify
- `dotnet build` RM_DivingInteraction.csproj: 0 warnings, 0 errors.
- RM_SeaDiveGenerators.xml parses.
- run_selftests.py: 77/79; the one FAIL is `selftest_deployed_biome_refs.py` (19 dangling refs in
  the DEPLOYED RUT_TheRot / RUT_WeepingStones folders), unrelated to this change.
