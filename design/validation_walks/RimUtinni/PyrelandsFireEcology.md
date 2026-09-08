# PyrelandsFireEcology — validation walk
subject: src/RimUtinni/PyrelandsFireEcology  (packageId `mandrake.rut.fireecology`)
deps: mandrake.rsw.fireecology (own tier), zylle.morevanillabiomes (third-party, "More Vanilla Biomes")
list: minimal+zylle.morevanillabiomes+mandrake.rsw.fireecology
status-hint: wires the RSW fire-ecology engine onto ZBiome_Grasslands (More Vanilla Biomes' Pyrelands stand-in) — strips rain, cranks DryThunderstorm, adds Black Rain, swaps ground terrain for the scorchable/ash-ladder family.

## must be true
- ZBiome_Grasslands' `terrainsByFertility` li[1..4] resolve to RSW_FE_Ground_Sand/Gravel/Soil/SoilRich, not the donor mod's stock Sand/Gravel/Soil/SoilRich.
- ZBiome_Grasslands' `terrainPatchMakers/li[1]/thresholds/li[1]` resolves to RSW_FE_Ground_SoilRich (Mud/WaterShallow/WaterDeep thresholds stay vanilla — untouched by this mod).
- ZBiome_Grasslands' `baseWeatherCommonalities` has no Rain, RainyThunderstorm, FoggyRain, or TorrentialRain entries.
- ZBiome_Grasslands' `baseWeatherCommonalities/DryThunderstorm` = 35 and `/Clear` = 55.
- ZBiome_Grasslands' `baseWeatherCommonalities/RSW_FE_BlackRain` = 1 (added, not replacing anything).
- Three PatchOperationFindMod blocks are all gated on "More Vanilla Biomes" being active — with it absent, patches apply to nothing and log nothing (never assert on log silence for this).

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rut.fireecology" and no XML error naming PyrelandsGround_ScorchableTerrain.xml, PyrelandsWeather_BlackRain.xml, or PyrelandsWeather_Stage0.xml
2. [B] jawa/get_def {defName: "ZBiome_Grasslands", defType: "BiomeDef"} → terrainsByFertility li[1..4] read RSW_FE_Ground_Sand/Gravel/Soil/SoilRich (resolved post-patch, not the raw donor XML)
3. [B] jawa/get_def {defName: "ZBiome_Grasslands", defType: "BiomeDef"} → terrainPatchMakers li[1]/thresholds li[1] terrain reads RSW_FE_Ground_SoilRich
4. [D] def read-back: BiomeDef ZBiome_Grasslands baseWeatherCommonalities has no Rain/RainyThunderstorm/FoggyRain/TorrentialRain keys; DryThunderstorm = 35; Clear = 55; RSW_FE_BlackRain = 1
5. [D] def read-back: RSW_FE_Ground_Sand/Gravel/Soil/SoilRich (from mandrake.rsw.fireecology) exist as TerrainDefs — the four defNames this mod repoints onto, confirming the dependency actually shipped them
X. [S] (human pass) generate a fresh Pyrelands map tile and look at the ground texture — scorchable/ash-ladder terrain, not stock sand
