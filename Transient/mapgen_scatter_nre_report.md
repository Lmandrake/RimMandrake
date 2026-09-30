# MAPGEN_SCATTER_NRE_1 report (2026-09-30)

## Root cause

- **The step that throws is `RUT_Jawa_ScatterScrapfields`** (order 960, `ChunkSlagSteel`, `filthDef Filth_MachineBits`, clusterSize 10), in `src/RimUtinni/UtinniPatches/Defs/MapGeneration/JawaScrapfields.xml`, registered on Base_Player for every biome. It is the only item scatter with a filthDef between the NRE and the order-965 Scald wreck lines in Player.log. I checked every `GenStep_ScatterThings` GenStepDef in the deployed Mods folder, Data/ and the workshop tree. Core's only other order-960 filth scatter spawns buildings, which always spawn.
- **The mechanism, from the decompiled `Verse.GenStep_ScatterThings.ScatterAt` (RimSage):** an Item is placed with `GenPlace.TryPlaceThing(..., Near, ...)` and the result is ignored. `TryFindPlaceSpotNear` fails **silently** when no radial cell is usable. For example, chunks are `saveCompressible`, so they refuse a cell that already holds a chunk or rock, and a 10-chunk cluster can fill a small walkable pocket. When that happens the chunk never spawns. The filth block still runs `item2.InBounds(thing.Map)` with `thing.Map == null`, which is the NRE at IL 0x13f.
- **Why it hits some biomes and not others:** no "Failed to place" line appears anywhere in the log. That rules out the other failure branch, which does log. Which of the five biomes' terrain produces the full-pocket case is UNMEASURED offline.
- **Not involved:**
  - `BiomesCore.IslandGeysers` is only a prefix on the call stack.
  - No DEPLOY_HOLD'd or renamed def is involved; `ChunkSlagSteel` is Core.
- ⚠️ **Correction to the brief:** a GenStep exception does **not** abort later steps. `MapGenerator.GenerateContentsIntoMap` wraps each step in its own try/catch. The NRE only loses the rest of the scrap chunks on that map. **RM_BlueDesert's zero plants has a different cause.**

## Fix

- New class `RimMandrake.Utinni.UtinniPatches.RUT_GenStep_ScatterThingsPlacedFilth` in `src/RimUtinni/UtinniPatches/Source/RUT_GenStep_ScatterThingsPlacedFilth.cs`, also added to the csproj.
  - It calls the stock `ScatterAt` with the filth turned off.
  - It then lays filth, with the same `filthExpandBy`/`filthChance`, only around a chunk that actually spawned. It detects that chunk through `ListerThings` growth.
- `JawaScrapfields.xml` now uses this class. All other fields are unchanged. The DLL and `.srchash` were rebuilt.

## Biome-gating of scatters

Each scatter was moved off the global `Base_Player` genSteps. Verse.MapGenerator appends `extraGenSteps` only for that biome or mutator:

| scatter | now on |
|---|---|
| RUT_Jawa_ScatterScaldWreck{Hull,Tank,Frame} | BiomeDef RM_TheScald + RUT_TheScald `.extraGenSteps` |
| RM_ScatterWastelandBrine{Tekk,Drazz,Plate} | BiomeDef RM_Wasteland `.extraGenSteps` |
| RUT_Jawa_ScatterWastelandBrine{Tekk,Drazz,Plate} | BiomeDef RUT_Wasteland `.extraGenSteps` |
| RUT_ContagionRingScatter | BiomeDef RUT_TheForge `.extraGenSteps` (the class's own `<biomes>`) |
| RM_GreySeaScatterShoreDomes | TileMutatorDef RM_SeaCoast `.extraGenSteps` (a land map beside the sea, so the biome cannot gate it). `warnOnFail false` for coasts of the other 3 modded seas |

- The patches are nested Conditionals: the target def must exist, then the patch appends to `extraGenSteps` or creates it.
- Scope change: `extraGenSteps` applies to every map generator on that biome, not only Base_Player. The terrain-tag validators still confine where things land.
- `RUT_Jawa_ScatterScrapfields` stays planet-wide on Base_Player. That is deliberate per its own header: the Jawa world is littered.

## Verification

- XML parse passes on all touched files.
- `validate_patch.py` gives 0 errors. Its 2 warnings are the intentional add-if-missing pattern.
- The UtinniPatches build succeeded with 0 warnings.
- `run_selftests.py`: 77/79 passed. The one FAIL is `selftest_deployed_biome_refs.py`: 19 dangling wildPlants refs (RotSporeKit / RUT_Dewshrooms). It predates this change and is unrelated.

## Live checks for coordinator

1. Deploy UtinniPatches (the DLL plus JawaScrapfields.xml) and RimMandrake.Biomes (TerminalBiomes + Wasteland patches).
2. Regenerate the debug map as RM_Contagion, RM_LongShade, RM_Cauldron, RM_Wasteland and RM_BlueDesert. Expect:
   - **no** `Error in GenStep: NullReferenceException … GenStep_ScatterThings.ScatterAt [0x0013f]`;
   - no Scald-wreck / GreySea shore-dome / RUT_Wasteland-brine "could not find cell" lines, and no "RUT_ContagionRingScatter has no filthDef configured" line, on those maps.
3. On an RM_Wasteland map, the RM_ brine scatters should still run, and warn only if the map has no brine shallows.
4. On a Scald map, the wreck steps should run.
5. Slag chunks with machine-bit filth should still appear on desert maps.
6. RM_BlueDesert zero plants: investigate separately. It is **not** explained by this NRE.
