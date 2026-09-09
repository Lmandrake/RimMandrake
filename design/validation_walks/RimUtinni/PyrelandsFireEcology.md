# PyrelandsFireEcology — validation walk
subject: src/RimUtinni/PyrelandsFireEcology  (packageId `mandrake.rut.fireecology`)
deps: mandrake.rm.pyrelands (own tier — the self-contained "Pyrelands" biome mod, RM_FE_ prefix; renamed from mandrake.rsw.fireecology in the sprint global pass, 2026-09-08), zylle.morevanillabiomes (third-party, "More Vanilla Biomes")
list: minimal+zylle.morevanillabiomes+mandrake.rm.pyrelands
status-hint: wires mandrake.rm.pyrelands's fire-ecology defs onto ZBiome_Grasslands (More Vanilla Biomes' donor stand-in for the Pyrelands, still live pending PYRELANDS_WORLD_SWITCH_1) — strips rain, cranks DryThunderstorm, adds Black Rain, swaps ground terrain for the scorchable/ash-ladder family.

## must be true
- ZBiome_Grasslands' `terrainsByFertility` li[1..4] resolve to RM_FE_Ground_Sand/Gravel/Soil/SoilRich, not the donor mod's stock Sand/Gravel/Soil/SoilRich.
- ZBiome_Grasslands' `terrainPatchMakers/li[1]/thresholds/li[1]` resolves to RM_FE_Ground_SoilRich (Mud/WaterShallow/WaterDeep thresholds stay vanilla — untouched by this mod).
- ZBiome_Grasslands' `baseWeatherCommonalities` has no Rain, RainyThunderstorm, FoggyRain, or TorrentialRain entries.
- ZBiome_Grasslands' `baseWeatherCommonalities/DryThunderstorm` = 35 and `/Clear` = 55.
- ZBiome_Grasslands' `baseWeatherCommonalities/RM_FE_BlackRain` = 1 (added, not replacing anything).
- Three PatchOperationFindMod blocks are all gated on "More Vanilla Biomes" being active — with it absent, patches apply to nothing and log nothing (never assert on log silence for this).

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rut.fireecology" and no XML error naming PyrelandsGround_ScorchableTerrain.xml, PyrelandsWeather_BlackRain.xml, or PyrelandsWeather_Stage0.xml
2. [B] jawa/get_def {defName: "ZBiome_Grasslands", defType: "BiomeDef"} → terrainsByFertility li[1..4] read RM_FE_Ground_Sand/Gravel/Soil/SoilRich (resolved post-patch, not the raw donor XML)
3. [B] jawa/get_def {defName: "ZBiome_Grasslands", defType: "BiomeDef"} → terrainPatchMakers li[1]/thresholds li[1] terrain reads RM_FE_Ground_SoilRich
4. [D] def read-back: BiomeDef ZBiome_Grasslands baseWeatherCommonalities has no Rain/RainyThunderstorm/FoggyRain/TorrentialRain keys; DryThunderstorm = 35; Clear = 55; RM_FE_BlackRain = 1
5. [D] def read-back: RM_FE_Ground_Sand/Gravel/Soil/SoilRich (from mandrake.rm.pyrelands) exist as TerrainDefs — the four defNames this mod repoints onto, confirming the dependency actually shipped them
X. [S] (human pass) generate a fresh Pyrelands map tile and look at the ground texture — scorchable/ash-ladder terrain, not stock sand
