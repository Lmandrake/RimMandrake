## spec
Contagion's `legacy_placement_worker` is scoped out by the standing no-worldgen ruling, but it still scores tiles:
`RM_BiomeWorker_Contagion.GetScore` returns `r.baseScore` at the shipped `biomeRarityFactor` of 1
(`src/RimMandrake/Contagion/Source/RM_ContagionBiome.cs:62-103`, read 2026-11-16), and the setting lives in a
"Biome rarity (WORLDGEN-AFFECTING)" group (`RM_ContagionMod.cs:137`). Retire it: the BiomeDef's workerClass scores every
tile at or below -100, and `biomeRarityFactor` and its group are removed (Scribe key dropped). Owed by Contagion coverage
gap g14 (`rm-coverage-judge-1794821839`); `coverage_rest` covers the entry by this item plus the absence arm of the offline
leaf `biome_def_declared`.

## verify
The acceptance test below passes; `selftest_contagion.py` still passes; the Contagion DLL builds.

## criteria
Acceptance test: absence arm of the offline leaf `biome_def_declared` (design/concepts/Contagion/tree.json): the workerClass named in
RM_Contagion.xml scores -100 or less for any tile (source read of GetScore), and `biomeRarityFactor` appears in no
Contagion .cs file: 2 passes. Fails on the base (GetScore returns r.baseScore; biomeRarityFactor at RM_ContagionMod.cs:22).
