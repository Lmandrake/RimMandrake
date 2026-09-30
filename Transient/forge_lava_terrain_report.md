# FORGE_LAVA_TERRAIN_1: open lava at RM_TheForge map generation

Status: BUILT OFFLINE (XML only). Not deployed or live-tested; the coordinator does that.

## Problem (measured)
A freshly generated RM_TheForge map had zero lava cells (`Transient/quicktest_forge_cycle_2026-09-30.json`: AB_BlackPebbles 40,916 of 62,500). The six-phase Forge cycle's freeze, crust, cracks and melt phases act only on lava, so they changed no terrain across ~400k ticks.

## Which terrain the cycle treats as lava
`RM_ForgePulse.xml` → `RM_ForgeCycleExtension.freezableTerrains` = `[LavaDeep]`. `IsFreezable` checks the natural terrain layer, with no temp terrain and no foundation. The crust is `RM_BasaltShingle`/`RM_PumiceRubble` on the temp layer, so natural `CooledLava` banks do not collide with `IsOurCrust`. `maxFrozenCells` is 6000.

## Mechanism chosen
This uses vanilla Odyssey's own mechanism: `BiomeDef.terrainPatchMakers`, the same shape as `Data/Odyssey/Defs/BiomeDefs/LavaField.xml` (LavaDeep above Perlin 0.9, VolcanicRock rim). I checked it in RimSage:
- `GenStep_Terrain` → `MapGenUtility.TerrainFrom` applies patch makers before the gravel, rock and fertility bands. It destroys a rock edifice wherever the terrain has `supportsRock=false`, so the lava cuts through the massif.
- Lava behaviour needs no GenStep or MapComponent. It comes from the TerrainDef itself:
  - `SteadyEnvironmentEffects` reads `heatPerTick`.
  - `HediffGiver_Terrain` reads `burnDamage` and `ignitePawnsIntervalTicks`.
  - `LavaBase` also sets `dangerous`, `avoidWander` and `Impassable`.
- There is no C#, so no DLL and no Mod Settings toggle were added.

There are two patch makers, both with `isPond=false` so that a `preventsPondGeneration` mutator cannot erase the lava:
1. **Fields:** Perlin 0.035/1.5/6. LavaDeep at ≥0.7, with CooledLava shores at 0.55–0.7.
2. **Seams (rivers):** Perlin 0.012/2/4. LavaDeep at |v| ≤ 0.025, with CooledLava banks at |v| ≤ 0.045. This band is contour lines, so it forms winding rivers. It is gated to `maxFertility 0.65`, which breaks the seams over the fertile ground so impassable lava cannot seal the map into pieces. The gaps are the crossings, and the freeze phase opens more.

## Coverage target
The coverage figures are **estimates**. They come from an offline libnoise-style Perlin approximation over 12 seeds on 250×250, not the engine's own noise:
- LavaDeep: about **9%** (range 5.5–14%), roughly 5,400 cells on 62,500, which is close to `maxFrozenCells` 6000.
- Walkable CooledLava banks: about 5% more.
- For comparison, vanilla LavaField's 0.9 threshold gives about 2% in the same approximation.

## Verification
- XML parses, and both patch makers read back correctly.
- `run_selftests.py`: 77/79 passed. The one FAIL is `selftest_deployed_biome_refs.py`. It fails on 21 dangling references that already existed in the deployed game folder. None of them touches this file; the only Forge hit is `RUT_Sagecrust <- RUT_TheForge.xml`, which is the RUT twin.
- There is no C# build, because nothing was compiled.

## Coordinator: check live
1. On a fresh RM_TheForge quicktest map, the LavaDeep cell count should be about 3–15% of cells, and CooledLava should be present.
2. The map edge should reach the map centre and each edge. If the seams seal off regions, raise `maxFertility` gaps (lower it to 0.55) or narrow the band.
3. The cycle's freeze phase should now crust cells ("Crusted cells: N" > 0), and the melt should restore LavaDeep.
4. Watch for plant and fire churn at start from lava ignition (`igniteRadius` 1.9). Vanilla LavaField has the same behaviour.
5. Check whether the composed Baroque Biomes build picks up this file unchanged.
