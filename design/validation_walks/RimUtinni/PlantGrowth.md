# PlantGrowth — validation walk
subject: src/RimUtinni/PlantGrowth  (packageId mandrake.rut.plantgrowth)
deps: brrainz.harmony (Harmony, modDependencies + loadAfter), Ludeon.RimWorld (modDependencies + loadAfter, vanilla)
list: minimal     # Harmony is a baseline dependency already carried by the minimal list; no other third-party mod is required
status-hint: one Harmony postfix on Plant.GrowthRate (getter) that multiplies every plant's composite growth rate planet-wide — wild/crops x4.0, trees x2.5, terminator/poison-forest biomes x0.4 — tunable at runtime from Defs/JawaPlantGrowthSettings.xml with compiled fallback defaults, and a short exempt list (anima tree, Gauranlen, ambrosia, anything already under 1 grow-day).

## must be true
- PlantGrowthSettingsDef RUT_JawaPlantGrowth_Settings loads with defaultMultiplier=4.0, treeMultiplier=2.5, terminatorMultiplier=0.4, minGrowDaysToBoost=1.0, terminatorBiomes=[PoisonForest], exemptPlants=[Plant_TreeAnima, Plant_TreeGauranlen, Plant_Ambrosia].
- On startup, JawaPlantGrowthMod's static constructor calls PlantGrowthConfig.Rebuild() then Harmony("mandrake.rut.plantgrowth").PatchAll(), and logs "[RimMandrake.Utinni.PlantGrowth] scaling {N} plant defs (default x4, tree x2.5), {N} exempt, {N} terminator biome(s) at x0.4." with real substituted counts.
- A non-exempt wild/crop plant's Plant.GrowthRate getter returns vanilla-composite x4.0; a tree-type plant returns vanilla-composite x2.5; a plant standing in a PoisonForest-biome map returns vanilla-composite x0.4 — all BEFORE the terminator/default multiplier choice, meaning environmental penalties (light/temp/fertility) are still folded into the pre-multiply base.
- Plant_TreeAnima, Plant_TreeGauranlen and Plant_Ambrosia are never scaled, in any biome including PoisonForest.
- If PoisonForest is not a loaded BiomeDef (mod absent), Rebuild() logs "[RimMandrake.Utinni.PlantGrowth] terminator biome 'PoisonForest' is not loaded; skipping it." and does not throw.
- A plant's in-game inspect string reflects the boosted growth rate, since it reads from the same Plant.GrowthRate getter the postfix patches.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rut.plantgrowth" and no XML error naming JawaPlantGrowthSettings.xml
2. [L] Player.log after load contains "[RimMandrake.Utinni.PlantGrowth] scaling" with nonzero ScaledCount, confirming Rebuild()+PatchAll() ran without hitting the catch block's "failed to build the growth tables, leaving growth vanilla" fallback
3. [D] def read-back: defType=RimMandrake.Utinni.PlantGrowth.PlantGrowthSettingsDef defName=RUT_JawaPlantGrowth_Settings; defaultMultiplier=4.0, treeMultiplier=2.5, terminatorMultiplier=0.4, terminatorBiomes contains PoisonForest
4. [B] jawa/set_plants {growth stage/values on a spawned test plant} then jawa/inspect_string {the plant} → the reported growth rate/days-to-maturity is faster than the plant ThingDef's own vanilla growDays would predict (default band) or slower (if the map's biome is PoisonForest)
5. [B] jawa/inspect_string on a spawned Plant_TreeAnima, Plant_TreeGauranlen, or Plant_Ambrosia → growth rate matches vanilla (unscaled), confirming the exempt list held
