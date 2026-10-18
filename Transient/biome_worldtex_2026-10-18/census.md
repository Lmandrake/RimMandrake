# Biome world-texture census 2026-10-18

Item BIOME_WORLDTEX_BUILD_EVERY_BIOME_A_FACE. MEASURED: 65 BiomeDefs prefixed RM_/RSW_/RUT_ in src/ (XML-parsed), minus 3 selftest fixtures (`src/RimMandrake/Utils/selftest_fixtures/density_classes/*.xml`) = **62 real defs**, all given a new texture. No RSW_ BiomeDefs exist.
Twin defs (RM_ vs RUT_ of the same biome, FuelSnows/Umbra) share one picture under each owner's own filename. 36 distinct pictures (generator `Transient/biome_worldtex_2026-10-18/gen.py`, procedural seamless 512x512 opaque RGB, matching existing `RM_TheRot.png`/`Jawa_HorrorWastes.png`). PLACEHOLDERS for worldmap painting; owner to refine.
Previously: 5 RM defs already had own near-flat textures (FeverWood, GelatinousSlime, Pyrelands, ChillCrater, TheRot) and were replaced; all others pointed at donor/vanilla paths (World/Biomes/Ocean, IceSheet, ExtremeDesert, AB_* ...) so many biomes shared one face.

| defName | label | old texture | new texture (installed) | picture | mean RGB |
|---|---|---|---|---|---|
| RUT_Desert | the Desert | World/Biomes/Desert | World/Biomes/RUT_LongShade (`RimUtinni/UtinniPatches`) | LongShade | [211, 182, 137] |
| RUT_Greentide | the Greentide | World/Biomes/Biome_CypreJungle | World/Biomes/RUT_Greentide (`RimUtinni/UtinniPatches`) | Greentide | [30, 117, 66] |
| RUT_FuelSnows | the Fuel Snows | Biomes/AB_PropaneLakes | World/Biomes/RUT_Umbra (`RimUtinni/UtinniPatches`) | Umbra | [12, 22, 37] |
| RUT_Jawa_BackgroundWater | mineral water | World/Biomes/Jawa_SickWater | World/Biomes/RUT_MineralWater (`RimUtinni/UtinniPatches`) | MineralWater | [95, 128, 106] |
| RUT_PropaneLake | the Chill | World/Biomes/Jawa_SickWater | World/Biomes/RUT_Chill (`RimUtinni/UtinniPatches`) | Chill | [37, 77, 113] |
| RUT_Cauldron | the Cauldron | Biomes/PoisonForest | World/Biomes/RUT_Cauldron (`RimUtinni/UtinniPatches`) | Cauldron | [40, 45, 32] |
| RUT_Scarlands | the Warscar | World/Biomes/Scarlands | World/Biomes/RUT_Warscar (`RimUtinni/UtinniPatches`) | Warscar | [93, 73, 59] |
| RUT_Webwork | the Webwork | Biomes/AB_FeraliskInfestedJungle | World/Biomes/RUT_Webwork (`RimUtinni/UtinniPatches`) | Webwork | [51, 63, 74] |
| RUT_TheRot | the Rot | Biomes/AB_MycoticJungle | World/Biomes/RUT_TheRot (`RimUtinni/UtinniPatches`) | TheRot | [182, 162, 196] |
| RUT_Umbra | Umbra | Biomes/AB_PropaneLakes | World/Biomes/RUT_Umbra (`RimUtinni/UtinniPatches`) | Umbra | [12, 22, 37] |
| RUT_FeverWood | the Fever Wood | World/Biomes/GreaterTropicalSwamp | World/Biomes/RUT_FeverWood (`RimUtinni/UtinniPatches`) | FeverWood | [65, 78, 36] |
| RUT_NightsideIce | the Sleeping Ice | World/Biomes/IceSheet | World/Biomes/RUT_SleepingIce (`RimUtinni/UtinniPatches`) | SleepingIce | [179, 188, 197] |
| RUT_TheScald | the Scald | World/Biomes/Ocean | World/Biomes/RUT_Scald (`RimUtinni/UtinniPatches`) | Scald | [72, 158, 165] |
| RUT_RustCathedral | the Rust Cathedral | Biomes/AB_MechanoidBiome | World/Biomes/RUT_RustCathedral (`RimUtinni/UtinniPatches`) | RustCathedral | [135, 55, 24] |
| RUT_BlueDesert | the Blue Desert | World/Biomes/IceSheet | World/Biomes/RUT_BlueDesert (`RimUtinni/UtinniPatches`) | BlueDesert | [209, 233, 247] |
| RUT_Slime | the Slime | Biomes/AB_GelatinousSuperorganism | World/Biomes/RUT_Slime (`RimUtinni/UtinniPatches`) | Slime | [148, 188, 32] |
| RUT_CrackedLands | the Cracked Lands | World/Biomes/ZBiome_Badlands | World/Biomes/RUT_CrackedLands (`RimUtinni/UtinniPatches`) | CrackedLands | [147, 67, 43] |
| RUT_TwilightSea | the Twilight Sea | World/Biomes/Ocean | World/Biomes/RUT_TwilightSea (`RimUtinni/UtinniPatches`) | TwilightSea | [43, 97, 133] |
| RUT_TheForge | the Forge | Biomes/AB_PyroclasticConflagration | World/Biomes/RUT_Forge (`RimUtinni/UtinniPatches`) | Forge | [74, 32, 14] |
| RUT_Sump | the Sump | Biomes/AB_TarPits | World/Biomes/RUT_Sump (`RimUtinni/UtinniPatches`) | Sump | [31, 28, 18] |
| RUT_Wasteland | the Wastes | Biomes/Wasteland | World/Biomes/RUT_Wasteland (`RimUtinni/UtinniPatches`) | Wasteland | [172, 164, 140] |
| RUT_Abyss | the Abyss | Biomes/AB_RockyCrags | World/Biomes/RUT_Abyss (`RimUtinni/UtinniPatches`) | Abyss | [55, 21, 89] |
| RUT_GreySea | the Grey Sea | World/Biomes/Ocean | World/Biomes/RUT_GreySea (`RimUtinni/UtinniPatches`) | GreySea | [127, 140, 141] |
| RUT_ExtremeDesert | the Extreme Desert | World/Biomes/ExtremeDesert | World/Biomes/RUT_Stillsand (`RimUtinni/UtinniPatches`) | Stillsand | [200, 165, 65] |
| RUT_Contagion | the Contagion | Biomes/AB_OcularForest | World/Biomes/RUT_Contagion (`RimUtinni/UtinniPatches`) | Contagion | [108, 19, 27] |
| RUT_AridShrubland | the arid shrubland | World/Biomes/AridShrubland1 | World/Biomes/RUT_LeaningScrub (`RimUtinni/UtinniPatches`) | LeaningScrub | [142, 159, 140] |
| RUT_WeepingStones | the Weeping Stones | World/Biomes/ZBiome_Oasis | World/Biomes/RUT_WeepingStones (`RimUtinni/UtinniPatches`) | WeepingStones | [188, 184, 173] |
| RUT_Miasma | the Miasma | Biomes/AB_MiasmicMangrove | World/Biomes/RUT_Miasma (`RimUtinni/UtinniPatches`) | Miasma | [119, 117, 30] |
| RM_Warscar | Warscar | World/Biomes/Scarlands | World/Biomes/RM_Warscar (`RimMandrake/Scarlands`) | Warscar | [93, 73, 59] |
| RM_RustCathedral | the Rust Cathedral | Biomes/AB_MechanoidBiome | World/Biomes/RM_RustCathedral (`RimMandrake/RustCathedral`) | RustCathedral | [135, 55, 24] |
| RM_TheScald | the Scald | World/Biomes/Ocean | World/Biomes/RM_Scald (`RimMandrake/TerminalBiomes`) | Scald | [72, 158, 165] |
| RM_GreySea | the Grey Sea | World/Biomes/Ocean | World/Biomes/RM_GreySea (`RimMandrake/TerminalBiomes`) | GreySea | [127, 140, 141] |
| RM_TheChill | the Chill | World/Biomes/Jawa_SickWater | World/Biomes/RM_Chill (`RimMandrake/TerminalBiomes`) | Chill | [37, 77, 113] |
| RM_ChillCrater | the Chill crater | World/Biomes/RM_ChillCrater | World/Biomes/RM_ChillCrater (`RimMandrake/TerminalBiomes`) | ChillCrater | [8, 9, 21] |
| RM_TwilightSea | the Twilight Sea | World/Biomes/Ocean | World/Biomes/RM_TwilightSea (`RimMandrake/TerminalBiomes`) | TwilightSea | [43, 97, 133] |
| RM_Webwork | the Webwork | World/Biomes/TropicalRainforest | World/Biomes/RM_Webwork (`RimMandrake/Webwork`) | Webwork | [51, 63, 74] |
| RM_TheRot | the Rot | World/Biomes/RM_TheRot | World/Biomes/RM_TheRot (`RimMandrake/TheRot`) | TheRot | [182, 162, 196] |
| RM_BlueDesert | the Blue Desert | World/Biomes/IceSheet | World/Biomes/RM_BlueDesert (`RimMandrake/BlueDesert`) | BlueDesert | [209, 233, 247] |
| RM_Miasma | the Miasma | Biomes/AB_MiasmicMangrove | World/Biomes/RM_Miasma (`RimMandrake/Miasma`) | Miasma | [119, 117, 30] |
| RM_TheForge | the Forge | World/Biomes/ExtremeDesert | World/Biomes/RM_Forge (`RimMandrake/TheForge`) | Forge | [74, 32, 14] |
| RM_FloodedCanyon | the Cracked Lands | World/Biomes/ExtremeDesert | World/Biomes/RM_CrackedLands (`RimMandrake/FloodedCanyon`) | CrackedLands | [147, 67, 43] |
| RM_TheSump | the Sump | Biomes/AB_TarPits | World/Biomes/RM_Sump (`RimMandrake/TheSump`) | Sump | [31, 28, 18] |
| RM_NightsideIce | the Sleeping Ice | World/Biomes/IceSheet | World/Biomes/RM_SleepingIce (`RimMandrake/NightsideIce`) | SleepingIce | [179, 188, 197] |
| RM_GelatinousSlime | the Slime | World/Biomes/RM_GelatinousSlime | World/Biomes/RM_Slime (`RimMandrake/GelatinousSlime`) | Slime | [148, 188, 32] |
| RM_LongShade | the Long Shade | World/Biomes/Desert | World/Biomes/RM_LongShade (`RimMandrake/LongShade`) | LongShade | [211, 182, 137] |
| RM_WeepingStones | the Weeping Stones | World/Biomes/ZBiome_Oasis | World/Biomes/RM_WeepingStones (`RimMandrake/WeepingStones`) | WeepingStones | [188, 184, 173] |
| RM_Contagion | the Contagion | Biomes/AB_OcularForest | World/Biomes/RM_Contagion (`RimMandrake/Contagion`) | Contagion | [108, 19, 27] |
| RM_LeaningScrub | the Leaning Scrub | World/Biomes/AridShrubland | World/Biomes/RM_LeaningScrub (`RimMandrake/LeaningScrub`) | LeaningScrub | [142, 159, 140] |
| RM_Pyrelands | the Pyrelands | World/Biomes/RM_Pyrelands | World/Biomes/RM_Pyrelands (`RimMandrake/Pyrelands`) | Pyrelands | [103, 92, 37] |
| RM_Wasteland | the Wastes | Biomes/Wasteland | World/Biomes/RM_Wasteland (`RimMandrake/Wasteland`) | Wasteland | [172, 164, 140] |
| RM_FeverWood | the Fever Wood | World/Biomes/RM_FeverWood | World/Biomes/RM_FeverWood (`RimMandrake/FeverWood`) | FeverWood | [65, 78, 36] |
| RM_LanternDeeps | the Lantern Deeps | World/Biomes/IceSheet | World/Biomes/RM_LanternDeeps (`RimMandrake/LanternDeeps`) | LanternDeeps | [12, 36, 73] |
| RM_Stillsand | the Stillsand | World/Biomes/ExtremeDesert | World/Biomes/RM_Stillsand (`RimMandrake/Stillsand`) | Stillsand | [200, 165, 65] |
| RM_Cauldron | the Cauldron | Biomes/PoisonForest | World/Biomes/RM_Cauldron (`RimMandrake/Cauldron`) | Cauldron | [40, 45, 32] |
| RM_SeabedFloor_TheScald | the Scald floor | World/Biomes/Ocean | World/Biomes/RM_SeabedScald (`RimMandrake/DivingInteraction`) | SeabedScald | [93, 31, 15] |
| RM_SeabedFloor_GreySea | Grey Sea floor | World/Biomes/Ocean | World/Biomes/RM_SeabedGrey (`RimMandrake/DivingInteraction`) | SeabedGrey | [195, 151, 158] |
| RM_SeabedFloor_TwilightSea | Twilight Sea floor | World/Biomes/Ocean | World/Biomes/RM_SeabedTwilight (`RimMandrake/DivingInteraction`) | SeabedTwilight | [79, 38, 61] |
| RM_SeabedFloor_TheChill | Chill floor | World/Biomes/Ocean | World/Biomes/RM_SeabedChill (`RimMandrake/DivingInteraction`) | SeabedChill | [27, 88, 79] |
| RM_SeabedUnavailable | bedrock | World/Biomes/ExtremeDesert | World/Biomes/RM_SeabedBedrock (`RimMandrake/DivingInteraction`) | SeabedBedrock | [70, 70, 75] |
| RM_SeabedFloor | sea floor | World/Biomes/Ocean | World/Biomes/RM_SeabedFloor (`RimMandrake/DivingInteraction`) | SeabedFloor | [135, 135, 106] |
| RM_Greentide | the Greentide | World/Biomes/TropicalRainforest | World/Biomes/RM_Greentide (`RimMandrake/Greentide`) | Greentide | [30, 117, 66] |
| RM_Abyss | the Abyss | Biomes/AB_RockyCrags | World/Biomes/RM_Abyss (`RimMandrake/Abyss`) | Abyss | [55, 21, 89] |

## Distinctness (nearest-neighbour mean-colour distance per picture; pattern in `gen.py` S table)

| picture | nearest | RGB dist |
|---|---|---|
| Abyss | SeabedTwilight | 41 |
| BlueDesert | SleepingIce | 74 |
| Cauldron | Sump | 24 |
| Chill | TwilightSea | 29 |
| ChillCrater | Umbra | 21 |
| Contagion | SeabedScald | 23 |
| CrackedLands | RustCathedral | 25 |
| FeverWood | Warscar | 37 |
| Forge | SeabedScald | 19 |
| Greentide | SeabedChill | 32 |
| GreySea | LeaningScrub | 24 |
| LanternDeeps | Umbra | 39 |
| LeaningScrub | GreySea | 24 |
| LongShade | SeabedGrey | 41 |
| Miasma | Pyrelands | 30 |
| MineralWater | SeabedFloor | 41 |
| Pyrelands | Miasma | 30 |
| RustCathedral | CrackedLands | 25 |
| Scald | GreySea | 63 |
| SeabedBedrock | Webwork | 20 |
| SeabedChill | Greentide | 32 |
| SeabedFloor | GreySea | 36 |
| SeabedGrey | Wasteland | 32 |
| SeabedScald | Forge | 19 |
| SeabedTwilight | SeabedBedrock | 36 |
| SleepingIce | WeepingStones | 26 |
| Slime | Stillsand | 66 |
| Stillsand | Slime | 66 |
| Sump | Cauldron | 24 |
| TheRot | SleepingIce | 26 |
| TwilightSea | Chill | 29 |
| Umbra | ChillCrater | 21 |
| Warscar | SeabedBedrock | 28 |
| Wasteland | LeaningScrub | 30 |
| Webwork | SeabedBedrock | 20 |
| WeepingStones | SleepingIce | 26 |

Closest pairs differ by pattern (e.g. Forge molten veins vs SeabedScald bubbles). Deploy: OWED (see report).
