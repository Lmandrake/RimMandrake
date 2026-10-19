# TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE: offline proof of the tree crown shade model

Design: `design/RimMandrake/tree_shade_model_2026-10-19.md` §6 (T1–T6 are the adopt-or-fall-back
test). **Needs:** offline. **Model: sonnet.** It is written alongside `TREE_SHADE_BUILD_CROWNS_ON_STILTS`,
and the build cannot close without it.

## spec

1. **Census, which replaces the UNMEASURED column in design §2.2.**
   - Generate one quicktest map per tree-heavy biome: `RM_Greentide`, `RUT_Greentide`, `RM_Miasma`,
     `RUT_Miasma`, `RM_FeverWood`, `RUT_FeverWood`, `RM_Webwork`, `RUT_Webwork`, `RM_Contagion` and
     `RUT_Contagion`. Saves of maps already generated are fine.
   - Count the caster-plant cells over passable non-water cells with
     `src/RimMandrake/Utils/rimbench/savemap.py`. Use the def dump of the same mod set.
   - Record them as MEASURED, with the save path and the dump fingerprint.
   - This step needs the bridge to make the maps. If no bridge window is free, it may be split off as
     its own item. The rest of this item is offline.
2. **T1, geometry.** Call `RM_SunHeatMath.CrownFootprint` in the C# SelfTest
   (`src/RimMandrake/CreatureBehaviors/Source/SelfTest/Program.cs`):
   - The same tree at the same E gives an identical footprint whatever biome is named.
   - At E = 90°, the disc lies under the trunk.
   - At E = 14°, the offset is `hc × cot 14°`, capped at 16.
   - A seedling's disc scales with growth.
3. **T2, offline half.** On synthetic grids at the census densities, at least 60% of open cells are
   covered in the Greentide and the Miasma. A cut 7×7 clearing is sunlit at its centre for E ≥ 30°.
   The result agrees with `design/RimMandrake/tree_shade_model_2026-10-19_estimate.py` within ±10
   points.
4. **T4.** Removing a caster and recomputing clears its footprint. Raising growth widens it.
5. **T5, benchmark.** `Recompute`'s raster on a 275×275 grid at `RM_Greentide` density takes at most
   15 ms. Report the measured number, never a bare pass.
6. **T6.** A rebuilt grid from the same thing set is bit-identical, because nothing is saved.
7. **Lint.** No BiomeDef or patch under `src/` carries a crown or canopy field (XML parsed as
   elements).
8. Add the new tests to `run_selftests.py` under the CreatureBehaviors group.
