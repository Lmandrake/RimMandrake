# Universal-mechanics conversion list, per mod (2026-11-21)

This file lists, per mod, the places that confine a mechanic to a biome. The rows come from two censuses: `design/specs/2026-11-21-guiding-principles/census_rulings.md` and `design/specs/2026-11-21-guiding-principles/census_code_gates.md`.
Rows of class WORLDGEN-SETTING come from item RIMMANDRAKE_CHECK_BIOME_RARITY_SLIDERS_AGAINST_NO_WORLDGEN_RULING, not from those censuses: each is a biome-rarity slider that the permanent no-worldgen ruling removes at the mod's next version (check: `python3 src/RimMandrake/Utils/worldgen_slider_check.py`).
A row is a pointer, not a ruling. Nothing here moves a current version's bars. The run that opens a mod's next version converts each row: a code gate becomes a physical condition, and a design or bar line is reworded as a condition.
In-game tests of a converted mechanic run on its home biome. No offline test and no foreign-map check is owed for the conversion (his words, 2026-11-21: "No offline testing, we test only where the mechanics matter").
A mechanic that is a heavy load even where it is not active may stay unloaded outside its parent biome. That is an exception: the design states it with its reason.
His cards of 2026-11-21 (`design/RimMandrake/standing_rulings.md` §Biome mechanics work by their conditions) settle most open rows. Each section has a line "Ruled 2026-11-21 (convert at the next version)" for those, and a line "Not ruled yet (wait for his card)" for the rest, which are not converted.

A program reads each section's `Version on 2026-11-21` line (`designer_stage.py` `conversion_owed`). The Designer's
packet names the section as owed input when the mod's version is newer than that line. `none` means the mod had no
version in design on 2026-11-21, so its first version is owed the conversion. A mod with no VERSION.json reads as
`0.1.0`.

## Abyss

- Version on 2026-11-21: `none`
- Folders: `design/concepts/Abyss/`, `src/RimMandrake/Abyss/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings R11 | `design/concepts/Abyss/design.md:195` | "Nothing outside the Abyss reads it" (cover). His cover card of 2026-11-19 made cover planet-wide. | REVERSED |
| code 53 | `src/RimMandrake/Abyss/Source/RM_MapComponentDark.cs:88`<br>`src/RimMandrake/Abyss/Source/RM_MapComponentDark.cs:258`<br>`src/RimMandrake/Abyss/Source/RM_AbyssSoundHook.cs:32`<br>`src/RimMandrake/Abyss/Source/RM_AbyssSoundscape.cs:48`<br>`src/RimMandrake/Abyss/Source/RM_AbyssSoundscape.cs:127`<br>`src/RimMandrake/Abyss/Source/RM_AbyssCryptid.cs:52`<br>`src/RimMandrake/Abyss/Source/RM_MapComponentShipCover.cs:58` | Darkness tick, sound, gust soundscape, cryptid signs and ship cover run only in the Abyss (defName). | MECHANIC-GATE |
| no-worldgen | `src/RimMandrake/Abyss/Source/RM_AbyssMod.cs:218`<br>`src/RimMandrake/Abyss/Source/RM_AbyssBiome.cs:58` | The biome-rarity slider (`biomeRarityFactor`, group "Biome rarity (WORLDGEN-AFFECTING)") changes how the BiomeWorker scores tiles, so it could roll a second world. Remove it: the slider, its group and its Scribe key go, and the worker scores every tile at -100 or less. The design already drops it. | WORLDGEN-SETTING (RULED 2026-08-15 and 2026-08-18: remove; no setting that could roll a second world) |

Not ruled yet (wait for his card): none.

## BlueDesert

- Version on 2026-11-21: `none`
- Folders: `design/concepts/BlueDesert/`, `src/RimMandrake/BlueDesert/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| code 52 | `src/RimMandrake/BlueDesert/Defs/IncidentDefs/RM_AblationSalvage.xml:58` | Ablation salvage is limited to its biome (allowedBiomes). (also in Miasma, TheSump) | UNCLEAR |

Not ruled yet (wait for his card): none.

## Cauldron

- Version on 2026-11-21: `0.1.0` (its first version was in design, with no VERSION.json yet: it keeps its scope)
- Folders: `design/concepts/Cauldron/`, `src/RimMandrake/Cauldron/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings A5 | `design/concepts/Cauldron/cleanse/bars.json` | R13: "Existing unsupported cross-biome switches stay off". Under the universal rule these switches have nothing to switch. (also in Contagion, CrackedLands, FeverWood, GelatinousSlime, LeaningScrub, LongShade, Miasma, RustCathedral, Stillsand, TerminalBiomes, TheRot, TheSump) | AMBIGUOUS |
| code 54 | `src/RimMandrake/Cauldron/Source/RM_AcidAir.cs:47` | Acid air burns pawns only on biomes with RM_AcidAirExtension. | MECHANIC-GATE |
| code 55 | `src/RimMandrake/Cauldron/Source/RM_VentBloomExposure.cs:75`<br>`src/RimMandrake/Cauldron/Source/RM_AcidAir.cs:64` | Animals native to the biome are exempt (read from the biome's animal list, CommonalityOfAnimal). | UNCLEAR |
| code 56 | `src/RimMandrake/Cauldron/Source/RM_CauldronRuinKit.cs:127`<br>`src/RimMandrake/Cauldron/Source/RM_CauldronVents.cs:320` | Ruin kit and vents are placed only in the Cauldron. | BIOME-DATA (map gen) |
| no-worldgen | `src/RimMandrake/Cauldron/Source/RM_CauldronMod.cs:159`<br>`src/RimMandrake/Cauldron/Source/RM_CauldronBiome.cs:59` | The biome-rarity slider (`biomeRarityFactor`, group "Biome rarity (WORLDGEN-AFFECTING)") changes how the BiomeWorker scores tiles, so it could roll a second world. Remove it: the slider, its group and its Scribe key go, and the worker scores every tile at -100 or less. The design already drops it. | WORLDGEN-SETTING (RULED 2026-08-15 and 2026-08-18: remove; no setting that could roll a second world) |

Ruled 2026-11-21 (convert at the next version): A5: the bar line becomes "each mechanic's switch is a plain on/off, default on, with no biome in it".
Not ruled yet (wait for his card): none.

## Contagion

- Version on 2026-11-21: `0.1.0`
- Folders: `design/concepts/Contagion/`, `src/RimMandrake/Contagion/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings R2 | `design/concepts/Contagion/design.md:153`<br>`design/concepts/Contagion/design.md:303` | Zhool haze turns plants to flesh plants "in our biomes only". | REVERSED |
| rulings R3 | `design/concepts/Contagion/tree.json` | Leaf flora_flesh: "owned biomes only"; haze on the temperate map counts as a false pass. | REVERSED |
| rulings A5 | `design/concepts/Contagion/cleanse/bars.json` | R13: "Existing unsupported cross-biome switches stay off". Under the universal rule these switches have nothing to switch. (also in Cauldron, CrackedLands, FeverWood, GelatinousSlime, LeaningScrub, LongShade, Miasma, RustCathedral, Stillsand, TerminalBiomes, TheRot, TheSump) | AMBIGUOUS |
| rulings A8 | `design/concepts/Contagion/cleanse/bars.json` | Bar 5: off-biome ambient exposure is unsupported; contact behaviour must not be redesigned to test other biomes. | AMBIGUOUS |
| rulings A9 | `design/concepts/Contagion/rewrite_choices.md:493`<br>`infrastructure/state/items/RIMMANDRAKE_BUILD_CONTAGION_REPULSOR_WARNING_NAMES_WHOLE_MAP.md:12` | "The Burn must never fire on another biome's map", kept as a build law. Fine if the cause is the Bloom cloud; wrong if it is the biome. | AMBIGUOUS |
| code 57 | `src/RimMandrake/Contagion/Source/CompZhoolHaze.cs:119-141` | Zhool haze converts only on a map whose biome comes from a mandrake.* mod (OurBiome, package-id prefix). | MECHANIC-GATE |
| code 58 | `src/RimMandrake/Contagion/Source/RM_ContagionSkyExtension.cs:77`<br>`src/RimMandrake/Contagion/Source/RM_GameCondition_ContagionBurn.cs:58` | Contagion sky and burn need the biome's extension; natives are exempt. | UNCLEAR |
| no-worldgen | `src/RimMandrake/Contagion/Source/RM_ContagionMod.cs:143`<br>`src/RimMandrake/Contagion/Source/RM_ContagionBiome.cs:62` | The biome-rarity slider (`biomeRarityFactor`, group "Biome rarity (WORLDGEN-AFFECTING)") changes how the BiomeWorker scores tiles, so it could roll a second world. Remove it: the slider, its group and its Scribe key go, and the worker scores every tile at -100 or less. The design already drops it. Contagion's own removal item is RIMMANDRAKE_RETIRE_CONTAGION_BIOME_SCORER_WORLD_IS_FROZEN. | WORLDGEN-SETTING (RULED 2026-08-15 and 2026-08-18: remove; no setting that could roll a second world) |

Ruled 2026-11-21 (convert at the next version): A5: the bar line becomes "each mechanic's switch is a plain on/off, default on, with no biome in it"; A8: the exposure reads its conditions on any map; in-game tests stay on the home biome; A9: the Burn reads its condition (the Bloom cloud), not the map, unless the design states the load exception.
Not ruled yet (wait for his card): none.

## CrackedLands

- Version on 2026-11-21: `none`
- Folders: `design/concepts/CrackedLands/`, `src/RimMandrake/CrackedLands/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings A5 | `design/concepts/CrackedLands/cleanse/bars.json` | bars 0/2/3/6/7 and check 1: "Existing unsupported cross-biome switches stay off". Under the universal rule these switches have nothing to switch. (also in Cauldron, Contagion, FeverWood, GelatinousSlime, LeaningScrub, LongShade, Miasma, RustCathedral, Stillsand, TerminalBiomes, TheRot, TheSump) | AMBIGUOUS |
| rulings A12 | `design/Jawa/worldbuilding/biomes/the_cracked_lands.md:273`<br>`infrastructure/state/items/EXPLOSIVE_PLANT_GROWTH_1.md:5-8` | Two growth rulings disagree: "the owner took it planet-wide" (2026-09-06) against "only natively apply to plants within the Baroque Biomes" (2026-10-16). (also in ExplosiveGrowth) | AMBIGUOUS |
| code 65 | `src/RimMandrake/CrackedLands/Source/RM_MercyLedges.cs:296`<br>`src/RimMandrake/CrackedLands/Source/RM_FossilStrata.cs:240`<br>`src/RimMandrake/CrackedLands/Source/RM_MapComponent_CanyonFlood.cs:126` | The flood cycle and mercy ledges run only in Flooded Canyon. (also in ExplosiveGrowth) | MECHANIC-GATE |
| switch | `src/RimMandrake/CrackedLands/Source/RM_CrackedLandsMod.cs:155`<br>`src/RimMandrake/CrackedLands/Source/RM_CrackedLandsMod.cs:227` | featureInOtherBiomes "Run the flood cycle in other biomes too" (default false). | SWITCH (ruled 2026-11-21) |
| switch | `src/RimMandrake/CrackedLands/Source/RM_CrackedLandsMod.cs:164`<br>`src/RimMandrake/CrackedLands/Source/RM_CrackedLandsMod.cs:282` | fossilSeamsInOtherBiomes "Fossil seams in other biomes too (worldgen)" (default false). | SWITCH (ruled 2026-11-21) |
| no-worldgen | `src/RimMandrake/CrackedLands/Source/RM_CrackedLandsMod.cs:218`<br>`src/RimMandrake/CrackedLands/Source/RM_BiomeWorker_CrackedLands.cs:40` | The biome-rarity slider (`biomeRarityFactor`, group "Biome rarity (WORLDGEN-AFFECTING)") changes how the BiomeWorker scores tiles, so it could roll a second world. Remove it: the slider, its group and its Scribe key go, and the worker scores every tile at -100 or less. The design already drops it. | WORLDGEN-SETTING (RULED 2026-08-15 and 2026-08-18: remove; no setting that could roll a second world) |

Ruled 2026-11-21 (convert at the next version): A5: the bar line becomes "each mechanic's switch is a plain on/off, default on, with no biome in it".
Ruled 2026-11-21 (convert at the next version): A12 (the Conductor's call under his cards of 2026-11-21): no conflict is left. Explosive growth belongs to the plant species and acts wherever those plants and water are. The Baroque biomes are where the plants are native (biome data). Switches featureInOtherBiomes and fossilSeamsInOtherBiomes: each becomes a plain on/off for its mechanic, default on, with no biome in it (the Conductor's call 2026-11-21: the same as the six-switch ruling).
Not ruled yet (wait for his card): none.

## FeverWood

- Version on 2026-11-21: `0.1.0` (its first version was in design, with no VERSION.json yet: it keeps its scope)
- Folders: `design/concepts/FeverWood/`, `src/RimMandrake/FeverWood/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings A5 | `design/concepts/FeverWood/cleanse/bars.json` | R13: "Existing unsupported cross-biome switches stay off". Under the universal rule these switches have nothing to switch. (also in Cauldron, Contagion, CrackedLands, GelatinousSlime, LeaningScrub, LongShade, Miasma, RustCathedral, Stillsand, TerminalBiomes, TheRot, TheSump) | AMBIGUOUS |
| code 59 | `src/RimMandrake/FeverWood/Source/RM_OilBoil.cs:82` | Oil boil needs the weather to be in the biome's weather table at its temperature (baseWeatherCommonalities). Census did not read the context. | UNCLEAR |

Ruled 2026-11-21 (convert at the next version): A5: the bar line becomes "each mechanic's switch is a plain on/off, default on, with no biome in it".
Not ruled yet (wait for his card): none.

## GelatinousSlime

- Version on 2026-11-21: `0.1.0` (its first version was in design, with no VERSION.json yet: it keeps its scope)
- Folders: `design/concepts/GelatinousSlime/`, `src/RimMandrake/GelatinousSlime/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings A5 | `design/concepts/GelatinousSlime/cleanse/bars.json` | bar 8: "Existing unsupported cross-biome switches stay off". Under the universal rule these switches have nothing to switch. (also in Cauldron, Contagion, CrackedLands, FeverWood, LeaningScrub, LongShade, Miasma, RustCathedral, Stillsand, TerminalBiomes, TheRot, TheSump) | AMBIGUOUS |
| rulings A16 | `design/concepts/GelatinousSlime/tree.json` | Leaf 11: "Arbitrary third-party biome retrofit is outside the adopted scope." Open: vanilla and third-party biomes. | AMBIGUOUS |
| code 62 | `src/RimMandrake/GelatinousSlime/Source/GeneSeeker.cs:112`<br>`src/RimMandrake/GelatinousSlime/Source/GeneSeeker.cs:279`<br>`src/RimMandrake/GelatinousSlime/Source/FarmRuins.cs:52`<br>`src/RimMandrake/GelatinousSlime/Source/SlimeVisitors.cs:55`<br>`src/RimMandrake/GelatinousSlime/Source/SlimeVisitors.cs:231` | Gene extraction ("Not on a gelatinous slime map."), farm ruins and slime visitors run only on the slime biome. | MECHANIC-GATE |
| code 63 | `src/RimMandrake/GelatinousSlime/Source/SlimeExposure.cs:114` | Slime exposure runs only if the biome lays slime grass (BiomeLaysSlimeGrass). Census did not read the context. | UNCLEAR |
| no-worldgen | `src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs:192`<br>`src/RimMandrake/GelatinousSlime/Source/SlimeBiome.cs:72` | The biome-rarity slider (`rarityFactor`, group "Biome rarity (WORLDGEN-AFFECTING)") changes how the BiomeWorker scores tiles, so it could roll a second world. Remove it: the slider, its group and its Scribe key go, and the worker scores every tile at -100 or less. The design already drops it. | WORLDGEN-SETTING (RULED 2026-08-15 and 2026-08-18: remove; no setting that could roll a second world) |

Ruled 2026-11-21 (convert at the next version): A5: the bar line becomes "each mechanic's switch is a plain on/off, default on, with no biome in it"; A16: vanilla and third-party biomes follow the same rule; no retrofit list is owed.
Not ruled yet (wait for his card): none.

## Greentide

- Version on 2026-11-21: `none`
- Folders: `design/concepts/Greentide/`, `src/RimMandrake/Greentide/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings R5 | `design/concepts/Greentide/cleanse/bars.json` | Rule R7: Direct Sun active "on Greentide maps only". Also breaks the Direct Sun ruling. | REVERSED |
| rulings C3 | `design/concepts/Greentide/design.md:468`<br>`design/RimMandrake/special_mechanics_review_2026-10-22.md:303` | Churnmud seeded on other biomes kept off and labelled unsupported. Terrain seeding is biome data. | WORDING |
| code 21 | `src/RimMandrake/EnvironmentalHazards/Source/RM_IncidentWorker_SteamDevil.cs:27`<br>`src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_RoilVortexSpawner.cs:75` | Steam devils and roil vortices appear only in Greentide (defName). (also in EnvironmentalHazards) | MECHANIC-GATE |
| code 64 | `src/RimMandrake/Greentide/Source/RM_MapComponent_CrossBiomeChurnmud.cs:59`<br>`src/RimMandrake/Greentide/Source/Kernel/RM_RulesKernel.cs:36-40`<br>`src/RimMandrake/Greentide/Source/RM_StellockLace.cs:53` | Churnmud conversion on foreign maps (setting-driven); Stellock lace branches drop only if felled in Greentide. | MECHANIC-GATE |
| switch | `src/RimMandrake/Greentide/Source/RM_GreentideMod.cs:177`<br>`src/RimMandrake/Greentide/Source/RM_GreentideMod.cs:325` | "Enable outside the Greentide biome" (default false) plus same three sub-settings: crossBiomeEverywhere, crossBiomeBiomeList, crossBiomeCoverage. | SWITCH (RULED 2026-11-21: plain on/off, default on) |

Ruled 2026-11-21 (convert at the next version): switch "Enable outside the Greentide biome": the six-switch ruling: this switch becomes a plain on/off for its mechanic, default on, with no biome in it.
Not ruled yet (wait for his card): none.

## LanternDeeps

- Version on 2026-11-21: `none`
- Folders: `design/concepts/LanternDeeps/`, `src/RimMandrake/LanternDeeps/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings R10 | `design/concepts/LanternDeeps/cleanse/bars.json` | Rules R0 and R8: custom host list is "unsupported outside shipped hosts". The temperature test alone should decide. | REVERSED |
| code extra | `src/RimMandrake/LanternDeeps/Source/RM_AuroraCollapse.cs:268-269`<br>`src/RimMandrake/LanternDeeps/Source/Patch_GateLanternstoneDeep.cs:29` | Collapse warnings only in the home biome; both are hard defName checks (outside the 66 numbered rows). | MECHANIC-GATE |
| switch | `src/RimMandrake/LanternDeeps/Source/LanternDeepsMod.cs:115-122` | entranceBiomes list (default BiomeGRimond, RM_SleepingIce, RM_TheChill). | SWITCH (ruled 2026-11-21) |

Ruled 2026-11-21 (convert at the next version): switch entranceBiomes list: each becomes a plain on/off for its mechanic, default on, with no biome in it (the Conductor's call 2026-11-21: the same as the six-switch ruling).
Not ruled yet (wait for his card): none.

## LeaningScrub

- Version on 2026-11-21: `0.1.0`
- Folders: `design/concepts/LeaningScrub/`, `src/RimMandrake/LeaningScrub/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings A5 | `design/concepts/LeaningScrub/cleanse/bars.json` | check 13: "Existing unsupported cross-biome switches stay off". Under the universal rule these switches have nothing to switch. (also in Cauldron, Contagion, CrackedLands, FeverWood, GelatinousSlime, LongShade, Miasma, RustCathedral, Stillsand, TerminalBiomes, TheRot, TheSump) | AMBIGUOUS |
| code 60 | `src/RimMandrake/LeaningScrub/Source/RM_TheLean.cs:114`<br>`src/RimMandrake/LeaningScrub/Source/RM_TheLean.cs:143`<br>`src/RimMandrake/LeaningScrub/Source/RM_PlantLean.cs:144`<br>`src/RimMandrake/LeaningScrub/Source/RM_PlantLean.cs:244-247` | Plants lean only if the biome carries RM_LeanExtension ("needs a Leaning Scrub map"). | MECHANIC-GATE |
| code 61 | `src/RimMandrake/LeaningScrub/Source/RM_VenomvineIslands.cs:57` | Venomvine islands need the extension. | UNCLEAR |

Ruled 2026-11-21 (convert at the next version): A5: the bar line becomes "each mechanic's switch is a plain on/off, default on, with no biome in it".
Not ruled yet (wait for his card): none.

## LongShade

- Version on 2026-11-21: `none`
- Folders: `design/concepts/LongShade/`, `src/RimMandrake/LongShade/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings A5 | `design/concepts/LongShade/cleanse/bars.json` | R5: "Existing unsupported cross-biome switches stay off". Under the universal rule these switches have nothing to switch. (also in Cauldron, Contagion, CrackedLands, FeverWood, GelatinousSlime, LeaningScrub, Miasma, RustCathedral, Stillsand, TerminalBiomes, TheRot, TheSump) | AMBIGUOUS |
| rulings (a) | `design/concepts/LongShade/design.md:42`<br>`design/concepts/LongShade/design.md:354` | "Every rock and scarp throws a shadow four times its own height"; line 354 already says the one sun runs on every day-side map. | TEXT-TO-REVIEW |
| code 29 | `src/RimMandrake/CreatureBehaviors/Source/RM_MapComponent_ShadeGrid.cs:172-175` | Every map-wide sun-heat effect needs the biome to carry RM_SunHeatExtension (the "Stillshade" sun-exposure mechanic; census could not tell Long Shade from Stillsand). (also in CreatureBehaviors, Stillsand) | MECHANIC-GATE |
| code 31 | `src/RimMandrake/LongShade/Source/RM_ShadeExtras.cs:46`<br>`src/RimMandrake/LongShade/Source/RM_ShadeExtras.cs:79`<br>`src/RimMandrake/LongShade/Source/RM_ShadeExtras.cs:290`<br>`src/RimMandrake/LongShade/Source/RM_ShadeExtras.cs:539`<br>`src/RimMandrake/LongShade/Source/RM_ShadeExtras.cs:596` | Tollok infestation, stampede and the other Stillshade extras run only on RM_LongShade (defName). | MECHANIC-GATE |
| code 32 | `src/RimMandrake/LongShade/Defs/IncidentDefs/RM_SmokeHaze.xml:48`<br>`src/RimMandrake/LongShade/Defs/IncidentDefs/RM_ShadeStampede.xml:13` | Smoke haze and shade stampede allowed only in RM_LongShade (allowedBiomes). | UNCLEAR |
| code 33 | `src/RimMandrake/LongShade/Source/RM_ShipfallCommons.cs:129` | Shipfall commons need the biome's extension. | UNCLEAR |

Ruled 2026-11-21 (convert at the next version): A5: the bar line becomes "each mechanic's switch is a plain on/off, default on, with no biome in it".
Not ruled yet (wait for his card): none.

## Miasma

- Version on 2026-11-21: `none`
- Folders: `design/concepts/Miasma/`, `src/RimMandrake/Miasma/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings A5 | `design/concepts/Miasma/cleanse/bars.json` | R9: "Existing unsupported cross-biome switches stay off". Under the universal rule these switches have nothing to switch. (also in Cauldron, Contagion, CrackedLands, FeverWood, GelatinousSlime, LeaningScrub, LongShade, RustCathedral, Stillsand, TerminalBiomes, TheRot, TheSump) | AMBIGUOUS |
| code 22 | `src/RimMandrake/EnvironmentalHazards/Source/RM_HediffComp_ForgeOnSurvival.cs:132-133`<br>`src/RimMandrake/Miasma/Patches/RM_Miasma_ForgeOnSurvival.xml:74-224` | The forge-on-survival hediff effect fires only in Miasma (7 onlyInBiomes entries). (also in EnvironmentalHazards) | MECHANIC-GATE |
| code 51 | `src/RimMandrake/Miasma/Source/RM_DecayCells.cs:128`<br>`src/RimMandrake/Miasma/Source/RM_MapComponent_FlotsamYard.cs:32`<br>`src/RimMandrake/Miasma/Source/RM_MapComponent_YoungCall.cs:27` | Decay cells, flotsam yard and young call run only in Miasma. | MECHANIC-GATE |
| code 52 | `src/RimMandrake/Miasma/Defs/IncidentDefs/RM_Surge.xml:71` | Surge is limited to its biome (allowedBiomes). (also in BlueDesert, TheSump) | UNCLEAR |
| no-worldgen | `src/RimMandrake/Miasma/Source/RM_MiasmaMod.cs:183`<br>`src/RimMandrake/Miasma/Source/RM_MiasmaBiome.cs:58` | The biome-rarity slider (`biomeRarityFactor`, group "Biome rarity (WORLDGEN-AFFECTING)") changes how the BiomeWorker scores tiles, so it could roll a second world. Remove it: the slider, its group and its Scribe key go, and the worker scores every tile at -100 or less. The design already drops it. | WORLDGEN-SETTING (RULED 2026-08-15 and 2026-08-18: remove; no setting that could roll a second world) |

Ruled 2026-11-21 (convert at the next version): A5: the bar line becomes "each mechanic's switch is a plain on/off, default on, with no biome in it".
Not ruled yet (wait for his card): none.

## Pyrelands

- Version on 2026-11-21: `0.1.0`
- Folders: `design/concepts/Pyrelands/`, `src/RimMandrake/Pyrelands/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings R14 | `commit 675ab57651` | Ashwallow dive: commit does not say Pyrelands-only; the gate is in code (code 2). Tree leaf ashwallow_dives_unharmed is not confined. | REVERSED |
| rulings A13 | `design/concepts/Pyrelands/tree.json` | Leaves 0-21 ("a running Pyrelands map with the biome's clocks") and the pyrelandsEnabled gates. Card 2026-10-15: Pyrelands cross-biome not picked. Open: mechanics that are dangerous everywhere. | AMBIGUOUS |
| rulings C7 | `design/concepts/Pyrelands/tree.json`<br>`design/concepts/Pyrelands/record.json` | populations_are_the_biomes_own, no foreign arrivals, "never sees ordinary rain". Roster and weather are biome data. | WORDING |
| code 2 | `src/RimMandrake/Pyrelands/Source/RM_JobGiver_BurrowOnFire.cs:76-80` | Ashwallow dive from fire runs only on a Pyrelands map (IsPyrelandsMap, a defName list). Commit 675ab57651. | MECHANIC-GATE |
| code 3 | `src/RimMandrake/Pyrelands/Source/MapComponent_BurnLine.cs:150-158` | The burn line is measured only on Pyrelands maps (PyrelandsBiomeDefNames). | MECHANIC-GATE |
| code 4 | `src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs:128-149`<br>`src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs:197` | Fire ecology (ash, scorch, fruit) runs per map: native biome or an opted-in map. | MECHANIC-GATE |
| code 5 | `src/RimMandrake/Pyrelands/Source/PyrelandsAshSand.cs:153` | Ash-sand build-up runs on the native biome, or on opted-in maps at the coverage percentage. | MECHANIC-GATE |
| code 6 | `src/RimMandrake/Pyrelands/Source/PyrelandsNoOrdinaryRain.cs:40` | Ordinary rain turns into black rain only in Pyrelands. | MECHANIC-GATE |
| code 7 | `src/RimMandrake/Pyrelands/Source/PyrelandsHerdThirst.cs:43` | Herd thirst runs only in Pyrelands (defName early return). | MECHANIC-GATE |
| code 8 | `src/RimMandrake/Pyrelands/Source/PyrelandsFireSense.cs:54` | Fire sense applies only in Pyrelands. | MECHANIC-GATE |
| code 9 | `src/RimMandrake/Pyrelands/Source/ThinkNode_ConditionalPyrelandsColonist.cs:19-20` | The colonist fire behaviour applies only in Pyrelands. | MECHANIC-GATE |
| code 10 | `src/RimMandrake/Pyrelands/Source/PyrelandsMechanicsGate.cs:28-47`<br>`src/RimMandrake/Pyrelands/Source/RM_PyrelandsMod.cs:46` | Every Pyrelands mechanic reads pyrelandsEnabled plus the shell's per-biome Enabled(key). | MECHANIC-GATE |
| code 11 | `src/RimMandrake/Pyrelands/Source/RM_PyrelandsMod.cs:209-210` | The cross-biome opt-in switch (see switch table). | MECHANIC-GATE |
| code 12 | `src/RimMandrake/Pyrelands/Source/PyrelandsAshField.cs:161` | Ash-field scan shortcuts to true on a Pyrelands biome; also detects by terrain extension. | UNCLEAR |
| code 13 | `src/RimMandrake/Pyrelands/Source/PyrelandsForeignArrivals.cs:43-53`<br>`src/RimMandrake/Pyrelands/Patches/RM_Pyrelands_NoForeignArrivals.xml:15-70` | Foreign herds and aggressive animals kept out of Pyrelands (6 incident patches with disallowedBiomes). | UNCLEAR |
| switch | `src/RimMandrake/Pyrelands/Source/RM_PyrelandsMod.cs:176`<br>`src/RimMandrake/Pyrelands/Source/RM_PyrelandsMod.cs:610` | crossBiomeEnabled "Enable outside the Pyrelands biome" (default false) plus same three sub-settings: crossBiomeEverywhere, crossBiomeBiomeList, crossBiomeCoverage (false, empty, 1.0). | SWITCH (RULED 2026-11-21: plain on/off, default on) |
| switch | `src/RimMandrake/Pyrelands/Source/RM_PyrelandsMod.cs:46` | pyrelandsEnabled "Mod enabled" (default true). | SWITCH (not ruled) |

Ruled 2026-11-21 (convert at the next version): switch crossBiomeEnabled "Enable outside the Pyrelands biome": the six-switch ruling: this switch becomes a plain on/off for its mechanic, default on, with no biome in it; A13: dangerous mechanics are on by default on every map; conditions decide.
Not ruled yet (wait for his card): switch: pyrelandsEnabled "Mod enabled".

## PyrelandsMechanics

- Version on 2026-11-21: `0.1.0`
- Folders: `design/concepts/PyrelandsMechanics/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings A14 | `design/concepts/PyrelandsMechanics/tree.json` | Leaf 8: the player who sets fires on a Pyrelands map never sees a raid. The question was whether the Tribes rite is biome data or a mechanic. | AMBIGUOUS |

Ruled 2026-11-21 (convert at the next version): A14 (the Conductor's call under his cards of 2026-11-21): the Tribes rite follows a burn front where the Tribes are present. The front's schedule is the biome's weather odds (data). The code names no biome.
Not ruled yet (wait for his card): none.

## RustCathedral

- Version on 2026-11-21: `none`
- Folders: `design/concepts/RustCathedral/`, `src/RimMandrake/RustCathedral/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings A5 | `design/concepts/RustCathedral/cleanse/bars.json` | R6: "Existing unsupported cross-biome switches stay off". Under the universal rule these switches have nothing to switch. (also in Cauldron, Contagion, CrackedLands, FeverWood, GelatinousSlime, LeaningScrub, LongShade, Miasma, Stillsand, TerminalBiomes, TheRot, TheSump) | AMBIGUOUS |
| rulings C8 | `infrastructure/state/items/RUST_CATHEDRAL_MECHANICS_1.md:360`<br>`infrastructure/state/items/RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1.md:70`<br>`infrastructure/state/items/FORGE_MECHANICS_1.md:449` | Infestation "on Cathedral maps only"; borehulk "on any other biome's map: none"; a hard-coded Forge biome check. Incident and placement odds are data. (also in TheForge) | WORDING |
| code 66 | `src/RimMandrake/RustCathedral/Source/Hum/RM_MapComponent_BiomeAttitude.cs:409-424`<br>`src/RimMandrake/RustCathedral/Source/Hum/RM_HumReading.cs:111`<br>`src/RimMandrake/RustCathedral/Source/Hum/RM_HumReading.cs:204`<br>`src/RimMandrake/RustCathedral/Source/Hum/RM_HullBolts.cs:83`<br>`src/RimMandrake/RustCathedral/Source/Hum/RM_HullBolts.cs:237`<br>`src/RimMandrake/RustCathedral/Source/Hum/RM_LineCycle.cs:60`<br>`src/RimMandrake/RustCathedral/Source/Hum/RM_LineCycle.cs:180`<br>`src/RimMandrake/RustCathedral/Source/Hum/RM_IncidentWorker_CathedralResponse.cs:96`<br>`src/RimMandrake/RustCathedral/Source/Walls/HarmonyPatch_GateLivePatternMetal.cs:46` | The whole Cathedral hum and attitude system, hull bolts, line cycle, Cathedral response, live-pattern metal (defName / targetBiome / ext). (also in Minerals, SleepingIce, Wastes, Webwork, WeepingStones) | MECHANIC-GATE |
| switch | `src/RimMandrake/RustCathedral/Source/RustCathedral/RM_RustCathedralMod.cs:151`<br>`src/RimMandrake/RustCathedral/Source/RustCathedral/RM_RustCathedralMod.cs:361` | "Allow this mod's mechanics on other biomes" (default false) plus same three sub-settings: crossBiomeEverywhere, crossBiomeBiomeList, crossBiomeCoverage. | SWITCH (RULED 2026-11-21: plain on/off, default on) |
| no-worldgen | `src/RimMandrake/RustCathedral/Source/RustCathedral/RM_RustCathedralMod.cs:265`<br>`src/RimMandrake/RustCathedral/Source/RustCathedral/RM_BiomeWorker_RustCathedral.cs:64` | The biome-rarity slider (`biomeRarityFactor`, group "Biome rarity (WORLDGEN-AFFECTING)") changes how the BiomeWorker scores tiles, so it could roll a second world. Remove it: the slider, its group and its Scribe key go, and the worker scores every tile at -100 or less. The design already drops it. | WORLDGEN-SETTING (RULED 2026-08-15 and 2026-08-18: remove; no setting that could roll a second world) |

Ruled 2026-11-21 (convert at the next version): switch "Allow this mod's mechanics on other biomes": the six-switch ruling: this switch becomes a plain on/off for its mechanic, default on, with no biome in it; A5: the bar line becomes "each mechanic's switch is a plain on/off, default on, with no biome in it".
Not ruled yet (wait for his card): none.

## SleepingIce

- Version on 2026-11-21: `none`
- Folders: `design/concepts/SleepingIce/`, `src/RimMandrake/SleepingIce/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings A15 | `design/concepts/SleepingIce/design.md:44` | "The law of the place ... which no other biome has: Sensing is thermal". Open: heat-sensing physics everywhere, with this biome as showcase? | AMBIGUOUS |
| code 66 | `src/RimMandrake/SleepingIce/Source/RM_HeatDial.cs:45` | The Sleeping Ice heat dial runs only on its biome. (also in Minerals, RustCathedral, Wastes, Webwork, WeepingStones) | MECHANIC-GATE |

Ruled 2026-11-21 (convert at the next version): A15: thermal sensing reads heat, on any map ("all of the biome specifics mechanics so far stated are per condition").
Not ruled yet (wait for his card): none.

## Stillsand

- Version on 2026-11-21: `0.1.0` (its first version was in design, with no VERSION.json yet: it keeps its scope)
- Folders: `design/concepts/Stillsand/`, `src/RimMandrake/Stillsand/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings A5 | `design/concepts/Stillsand/cleanse/bars.json` | R13: "Existing unsupported cross-biome switches stay off". Under the universal rule these switches have nothing to switch. (also in Cauldron, Contagion, CrackedLands, FeverWood, GelatinousSlime, LeaningScrub, LongShade, Miasma, RustCathedral, TerminalBiomes, TheRot, TheSump) | AMBIGUOUS |
| rulings C5 | `design/concepts/Stillsand/cleanse/bars.json` | Bar 1: tree-heavy other biomes are dependency scope, not new Stillsand promises. | WORDING |
| rulings (a) | `design/concepts/Stillsand/design.md:374` | "Every dayside biome uses the geometry; only here is there never anything else." | TEXT-TO-REVIEW |
| code 29 | `src/RimMandrake/CreatureBehaviors/Source/RM_MapComponent_ShadeGrid.cs:172-175` | Every map-wide sun-heat effect needs the biome to carry RM_SunHeatExtension (the "Stillshade" sun-exposure mechanic; census could not tell Long Shade from Stillsand). (also in CreatureBehaviors, LongShade) | MECHANIC-GATE |
| code 34 | `src/RimMandrake/Stillsand/Source/RM_MapComponent_Zuurrik.cs:84-87`<br>`src/RimMandrake/Stillsand/Source/RM_MapComponent_Zuurrik.cs:97` | The zuurrik swarm wakes only in RM_Stillsand (defName). | MECHANIC-GATE |
| code 35 | `src/RimMandrake/Stillsand/Source/RM_DuneTrackEraser.cs:124` | Dune wind erases tracks only in RM_Stillsand. | MECHANIC-GATE |
| code 36 | `src/RimMandrake/Stillsand/Source/RM_SandSwimRemainder.cs:131`<br>`src/RimMandrake/Stillsand/Source/RM_SandSwimRemainder.cs:136`<br>`src/RimMandrake/Stillsand/Source/RM_SandSwimRemainder.cs:167` | Sand-listening hiss runs on any biome whose name contains "Stillsand" (defName.Contains). | MECHANIC-GATE |
| code 37 | `src/RimMandrake/Stillsand/Source/RM_DuneGale.cs:115`<br>`src/RimMandrake/Stillsand/Source/RM_WaterLedger.cs:102`<br>`src/RimMandrake/Stillsand/Source/RM_SandLeviathan.cs:179` | Dune gale, water ledger and sand leviathan work only on listed biomes (biomes list on the def extension). | MECHANIC-GATE |
| code 38 | `src/RimMandrake/Stillsand/Source/RM_StillsandWater.cs:132`<br>`src/RimMandrake/Stillsand/Source/RM_GiantSkeletons.cs:320`<br>`src/RimMandrake/Stillsand/Source/RM_GiantSkeletons.cs:448`<br>`src/RimMandrake/Stillsand/Source/RM_HorizonWarning.cs:190`<br>`src/RimMandrake/Stillsand/Source/RM_PreciousCaves.cs:657` | Sand remembers water, giant skeletons, horizon warning and precious caves need the extension. | UNCLEAR |
| code 39 | `src/RimMandrake/Stillsand/Defs/IncidentDefs/RM_SandBusterEruption.xml:42`<br>`src/RimMandrake/Stillsand/Defs/IncidentDefs/RM_SandLeviathanIncidents.xml:34`<br>`src/RimMandrake/Stillsand/Defs/WeatherDefs/RM_DuneGale.xml:247` | Sand buster, leviathan and dune gale tied to biomes (allowedBiomes / biomes). | UNCLEAR |

Ruled 2026-11-21 (convert at the next version): A5: the bar line becomes "each mechanic's switch is a plain on/off, default on, with no biome in it".
Not ruled yet (wait for his card): none.

## TerminalBiomes

- Version on 2026-11-21: `none`
- Folders: `design/concepts/TerminalBiomes/`, `src/RimMandrake/TerminalBiomes/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings A4 | `CLAUDE.md:184`<br>`design/RimMandrake/standing_rulings.md:233`<br>`design/RimMandrake/biome_rulings.md:210` | "No biome has its own heat kind ... except the Scald" (card 2026-11-20). Open: biome exception, or physics of steam and hot water anywhere? (Scald lives in TerminalBiomes and DivingInteraction.) (also in DivingInteraction) | AMBIGUOUS |
| rulings A5 | `design/concepts/TerminalBiomes/cleanse/bars.json` | R8: "Existing unsupported cross-biome switches stay off". Under the universal rule these switches have nothing to switch. (also in Cauldron, Contagion, CrackedLands, FeverWood, GelatinousSlime, LeaningScrub, LongShade, Miasma, RustCathedral, Stillsand, TheRot, TheSump) | AMBIGUOUS |
| rulings A6 | `design/RimMandrake/unified_direct_sun_heat_2026-10-19.md:269`<br>`infrastructure/state/items/DIRECT_SUN_SETTINGS_WIRE_FEWER_KNOBS.md:24`<br>`design/concepts/TerminalBiomes/cleanse/tickets.md:317` | "No new cross-biome switch is built"; "Unsupported: may work outside our biomes, not tested" (2026-10-15). CreatureBehaviors holds the Direct Sun engine. (also in CreatureBehaviors) | AMBIGUOUS |
| rulings A7 | `design/concepts/TerminalBiomes/TheChill_design.md:566`<br>`design/concepts/TerminalBiomes/TwilightSea_design.md:508` | "Recommended for dropping, not yet his: the inert cross-biome switches". Ready for his word. | AMBIGUOUS |
| rulings C2 | `design/concepts/TerminalBiomes/TheChill_design.md:434` | "The same stove on any other map lights." Lack of oxygen is the real reason. | WORDING |
| rulings (a) | `design/Jawa/worldbuilding/biomes/the_twilight_deep_content_2026-09-26.md:757` | "Nowhere else on the planet do you rent light" (Twilight Deep). | TEXT-TO-REVIEW |
| code 24 | `src/RimMandrake/EnvironmentalHazards/Source/RM_IncidentWorker_WalkerSurfacing.cs:39`<br>`src/RimMandrake/TerminalBiomes/Defs/IncidentDefs/RM_WalkerSurfacing.xml:63` | The walker surfacing incident is limited to listed biomes (allowedBiomes). (also in EnvironmentalHazards) | UNCLEAR |
| code 40 | `src/RimMandrake/DivingInteraction/Source/RM_MapComponent_ScaldVentForecast.cs:43`<br>`src/RimMandrake/DivingInteraction/Source/RM_MapComponent_ScaldImmersionBerth.cs:32` | The vent forecast (steam clock) and the immersion berth run only on Scald floor maps (defName). (also in DivingInteraction) | MECHANIC-GATE |
| code 41 | `src/RimMandrake/DivingInteraction/Source/RM_ChillFireGate.cs:30`<br>`src/RimMandrake/DivingInteraction/Source/RM_MapComponent_ChillBoilShroud.cs:106` | The Chill boil shroud runs only on Chill seabed maps (defName plus pocket-map flag). (also in DivingInteraction) | MECHANIC-GATE |
| code 43 | `src/RimMandrake/TerminalBiomes/Source/RM_GreyHullCrust.cs:36` | Grey hull crust runs on Grey Sea maps. | MECHANIC-GATE |
| code 44 | `src/RimMandrake/TerminalBiomes/Source/RM_PlaceWorker_ChillFloorOnly.cs:17-19` | Chill-floor-only placement (defName plus pocket-map flag). | MECHANIC-GATE |
| code 45 | `src/RimMandrake/TerminalBiomes/Source/RM_MapComponent_VeilFall.cs:60`<br>`src/RimMandrake/TerminalBiomes/Source/RM_MapComponent_WellLedger.cs:130-131`<br>`src/RimMandrake/TerminalBiomes/Source/RM_TwilightFloraBehaviour.cs:50` | Veil fall, well ledger and twilight flora behaviour run only on Twilight Sea maps. | MECHANIC-GATE |
| code 46 | `src/RimMandrake/TerminalBiomes/Source/RM_JobGiver_SeekGlow.cs:36`<br>`src/RimMandrake/TerminalBiomes/Source/RM_GreyLampResponse.cs:484` | Seek-glow gated by ext.onlyBiome; the Grey lamp response refuses non-Grey maps. | MECHANIC-GATE |
| code 47 | `src/RimMandrake/TerminalBiomes/Defs/IncidentDefs/RM_SuulkArrival.xml:40`<br>`src/RimMandrake/TerminalBiomes/Defs/IncidentDefs/RM_VeilFallPaneStrike.xml:39`<br>`src/RimMandrake/TerminalBiomes/Source/RM_IncidentWorker_SuulkArrival.cs:36` | Suulk arrival and veil-fall pane strike limited to biomes (allowedBiomes). | UNCLEAR |
| switch | `src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs:276`<br>`src/RimMandrake/TerminalBiomes/Source/RM_TerminalBiomesMod.cs:687` | "Enable outside the Scald biome" (default false) plus same three sub-settings: crossBiomeEverywhere, crossBiomeBiomeList, crossBiomeCoverage. | SWITCH (RULED 2026-11-21: plain on/off, default on) |

Ruled 2026-11-21 (convert at the next version): switch "Enable outside the Scald biome": the six-switch ruling: this switch becomes a plain on/off for its mechanic, default on, with no biome in it; A4: hot water is physics, not a Scald exception; the Scald's clock is rewritten to read hot water and its steam on any map; A5: the bar line becomes "each mechanic's switch is a plain on/off, default on, with no biome in it"; A6: no switch reads a biome; each "Enable outside this biome" switch becomes a plain on/off, default on, and the "Unsupported" label goes; A7: the cross-biome switches are not dropped; each becomes a plain on/off, default on.
Not ruled yet (wait for his card): none.

## TheForge

- Version on 2026-11-21: `none`
- Folders: `design/concepts/TheForge/`, `src/RimMandrake/TheForge/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings R13 | `commit d07e03a938` | Vapour-column haze on Forge maps only (pale ring round every geyser). His words of 2026-11-21 reverse it. | REVERSED |
| rulings C8 | `infrastructure/state/items/RUST_CATHEDRAL_MECHANICS_1.md:360`<br>`infrastructure/state/items/RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1.md:70`<br>`infrastructure/state/items/FORGE_MECHANICS_1.md:449` | Infestation "on Cathedral maps only"; borehulk "on any other biome's map: none"; a hard-coded Forge biome check. Incident and placement odds are data. (also in RustCathedral) | WORDING |
| code 1 | `src/RimMandrake/TheForge/Source/RM_ForgeSkyPastures.cs:40`<br>`src/RimMandrake/TheForge/Source/RM_ForgeSkyPastures.cs:215`<br>`src/RimMandrake/TheForge/Source/Kernel/RM_SkyKernel.cs:51-59` | Geyser vapour-column haze and ash spirals drawn only on The Forge (commit d07e03a938). ColumnVisualsShow compares to HomeBiome RM_TheForge. | MECHANIC-GATE |
| code 23 | `src/RimMandrake/EnvironmentalHazards/Source/RM_IncidentWorker_ContagionProbe.cs:36` | The contagion probe incident fires only on The Forge (defName). (also in EnvironmentalHazards) | UNCLEAR |

Not ruled yet (wait for his card): none.

## TheRot

- Version on 2026-11-21: `none`
- Folders: `design/concepts/TheRot/`, `src/RimMandrake/TheRot/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings R9 | `design/RimMandrake/rot_warm_mat_portable_2026-10-22.md:143`<br>`design/RimMandrake/rot_warm_mat_portable_2026-10-22.md:26` | Mat food exemption decided by the map's biome (IsRotBiome). His outcome (no feeding in the Rot) may stay; the biome check may not. | REVERSED |
| rulings R12 | `design/RimMandrake/gpt_review_findings_2026-10-22.md:211` | Spore cloud slider governs nothing off the Rot; "cross-biome is unsupported by ruling". | REVERSED |
| rulings A5 | `design/concepts/TheRot/cleanse/bars.json` | R10: "Existing unsupported cross-biome switches stay off". Under the universal rule these switches have nothing to switch. (also in Cauldron, Contagion, CrackedLands, FeverWood, GelatinousSlime, LeaningScrub, LongShade, Miasma, RustCathedral, Stillsand, TerminalBiomes, TheSump) | AMBIGUOUS |
| rulings A17 | `design/concepts/TheRot/design.md:107`<br>`design/concepts/TheRot/design.md:353`<br>`design/RimMandrake/rot_warm_mat_portable_2026-10-22.md`<br>`design/RimMandrake/rot_northstar_bars_draft_2026-10-22.md:52` | His new ask of 2026-11-21: "make it die in direct Sun exposure". No file says it yet. | AMBIGUOUS |
| rulings C6 | `design/RimMandrake/rot_warm_mat_portable_2026-10-22.md:20-21` | No upkeep inside the Rot, needs food outside. Matches his 2026-11-21 words; the mechanism is R9. | WORDING |
| rulings (a) | `design/concepts/TheRot/design.md:107` | "The floor is the heater. Living mat warms a room built over it." Nothing says it dies in direct sun. | TEXT-TO-REVIEW |
| code 14 | `src/RimMandrake/TheRot/Source/RM_LivingMatRoot.cs:126`<br>`src/RimMandrake/TheRot/Source/RM_LivingMatRoot.cs:172`<br>`src/RimMandrake/TheRot/Source/RM_LivingMatRoot.cs:464` | The living mat eats food and dies back when food runs out; outside the Rot it is switched by InRot (IsRotBiome). | MECHANIC-GATE |
| code 15 | `src/RimMandrake/TheRot/Source/RM_LivingMatRoot.cs:305-306` | The mat heats rooms only when the biome carries RM_WarmGroundExtension and Enabled(warmGround). | MECHANIC-GATE |
| code 16 | `src/RimMandrake/TheRot/Source/RM_TheRotMod.cs:163-177`<br>`src/RimMandrake/TheRot/Source/RM_TheRotMod.cs:447`<br>`src/RimMandrake/TheRot/Source/RM_TheRotMod.cs:456-470`<br>`src/RimMandrake/TheRot/Source/RM_TheRotMod.cs:485-497` | The Rot's kit mechanics are on or off by Governs(biome); outside it the intensity is crossBiomeCoverage. | MECHANIC-GATE |
| code 17 | `src/RimMandrake/TheRot/Defs/GameConditionDefs/RM_RotSporeKit_SporeCloud.xml:80` | The spore-cloud condition names disallowedBiomes. | UNCLEAR |
| code 18 | `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_WarmGround.cs:93-94` | Warm ground (floor heat) runs only where the biome carries RM_WarmGroundExtension and Enabled. Serves The Rot. (also in EnvironmentalHazards) | MECHANIC-GATE |
| code 20 | `src/RimMandrake/EnvironmentalHazards/Source/RM_IncidentWorker_SporeCloud.cs:25`<br>`src/RimMandrake/EnvironmentalHazards/Source/RM_SporeAllergyIncidents.cs:11`<br>`src/RimMandrake/EnvironmentalHazards/Source/RM_SporeAllergyIncidents.cs:29`<br>`src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_LivingProduce.cs:35`<br>`src/RimMandrake/EnvironmentalHazards/Source/RM_Patch_LivePrepViability.cs:68`<br>`src/RimMandrake/EnvironmentalHazards/Source/RM_HediffComp_SheenExposure.cs:43` | Spore cloud, spore allergy, live-produce heat, strict live prep, sheen exposure: per-biome switch RM_KitFronts.Enabled(key, biome). Serves The Rot kit. (also in EnvironmentalHazards) | MECHANIC-GATE |
| switch | `src/RimMandrake/TheRot/Source/RM_TheRotMod.cs:158`<br>`src/RimMandrake/TheRot/Source/RM_TheRotMod.cs:417` | crossBiomeEnabled "Enable outside The Rot biome" (default false) plus same three sub-settings: crossBiomeEverywhere, crossBiomeBiomeList, crossBiomeCoverage. | SWITCH (RULED 2026-11-21: plain on/off, default on) |

Ruled 2026-11-21 (convert at the next version): switch crossBiomeEnabled "Enable outside The Rot biome": the six-switch ruling: this switch becomes a plain on/off for its mechanic, default on, with no biome in it; A5: the bar line becomes "each mechanic's switch is a plain on/off, default on, with no biome in it"; A17: the ticket is `RIMMANDRAKE_CONVERT_ROT_MAT_TO_CONDITIONS_AND_SUN_DEATH`.
Not ruled yet (wait for his card): none.

## TheSump

- Version on 2026-11-21: `none`
- Folders: `design/concepts/TheSump/`, `src/RimMandrake/TheSump/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings A5 | `design/concepts/TheSump/cleanse/bars.json` | bar 6: "Existing unsupported cross-biome switches stay off". Under the universal rule these switches have nothing to switch. (also in Cauldron, Contagion, CrackedLands, FeverWood, GelatinousSlime, LeaningScrub, LongShade, Miasma, RustCathedral, Stillsand, TerminalBiomes, TheRot) | AMBIGUOUS |
| code 28 | `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_SumpLivingMap.cs:87` | Sump living map (census did not read the context). Biome read. (also in EnvironmentalHazards) | UNCLEAR |
| code 52 | `src/RimMandrake/TheSump/Defs/IncidentDefs/RM_TarPitBelch.xml:51` | Tar-pit belch is limited to its biome (allowedBiomes). (also in BlueDesert, Miasma) | UNCLEAR |
| no-worldgen | `src/RimMandrake/TheSump/Source/RM_TheSumpMod.cs:181`<br>`src/RimMandrake/TheSump/Source/RM_TheSumpBiome.cs:59` | The biome-rarity slider (`biomeRarityFactor`, group "Biome rarity (WORLDGEN-AFFECTING)") changes how the BiomeWorker scores tiles, so it could roll a second world. Remove it: the slider, its group and its Scribe key go, and the worker scores every tile at -100 or less. The design already drops it. | WORLDGEN-SETTING (RULED 2026-08-15 and 2026-08-18: remove; no setting that could roll a second world) |

Ruled 2026-11-21 (convert at the next version): A5: the bar line becomes "each mechanic's switch is a plain on/off, default on, with no biome in it".
Not ruled yet (wait for his card): none.

## Warscar

- Version on 2026-11-21: `none`
- Folders: `design/concepts/Warscar/`, `src/RimMandrake/Scarlands/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings R4 | `design/concepts/Warscar/design.md:351` | Broken turrets follow movement and never fire, "on Warscar maps only"; check: other map's turrets do not turn. | REVERSED |
| rulings C1 | `design/concepts/Warscar/design.md:353`<br>`design/concepts/Warscar/design.md:400`<br>`design/concepts/Warscar/design.md:424` | "Gives nightmares only here" / "only while on this ground". Holds if the poisoned ground is the cause. | WORDING |
| rulings C4 | `design/concepts/Warscar/design.md:480`<br>`infrastructure/state/items/DEAD_OR_INERT_SETTINGS_1.md:11`<br>`infrastructure/state/items/DEAD_OR_INERT_SETTINGS_1.md:22`<br>`design/RimMandrake/fluff_cuts_2026-10-23.md:186` | Cross-biome spread and wreck-lichen seeding settings. Biome data. | WORDING |
| code 48 | `src/RimMandrake/Scarlands/Source/RM_WarscarMark.cs:193`<br>`src/RimMandrake/Scarlands/Source/RM_ChatrakSnap.cs:305` | Warscar mark and chatrak snap run only in the Warscar (map.Biome != Warscar). | MECHANIC-GATE |
| code 49 | `src/RimMandrake/Scarlands/Source/RM_Settling.cs:225`<br>`src/RimMandrake/Scarlands/Source/MapComponent_WreckLichen.cs:45`<br>`src/RimMandrake/Scarlands/Source/RM_WarscarMod.cs:183-196` | Settling and wreck lichen run on the Warscar or an opted-in map (lichen strength by slider). | MECHANIC-GATE |
| code 50 | `src/RimMandrake/Scarlands/Source/RM_WarscarPatches.cs:19` | The Warscar rarity patch applies only to RM_Warscar. | UNCLEAR |
| switch | `src/RimMandrake/Scarlands/Source/RM_WarscarMod.cs:292`<br>`src/RimMandrake/Scarlands/Source/RM_WarscarMod.cs:728` | "Enable outside the Warscar" (default false) plus same three sub-settings: crossBiomeEverywhere, crossBiomeBiomeList, crossBiomeCoverage. | SWITCH (RULED 2026-11-21: plain on/off, default on) |
| no-worldgen | `src/RimMandrake/Scarlands/Source/RM_WarscarMod.cs:374`<br>`src/RimMandrake/Scarlands/Source/RM_WarscarPatches.cs:20` | The biome-rarity slider (`biomeRarityFactor`, group "Biome rarity (WORLDGEN-AFFECTING)") changes how the BiomeWorker scores tiles, so it could roll a second world. Remove it: the slider, its group and its Scribe key go, and the worker scores every tile at -100 or less. The design already drops it. | WORLDGEN-SETTING (RULED 2026-08-15 and 2026-08-18: remove; no setting that could roll a second world) |

Ruled 2026-11-21 (convert at the next version): switch "Enable outside the Warscar": the six-switch ruling: this switch becomes a plain on/off for its mechanic, default on, with no biome in it.
Not ruled yet (wait for his card): none.

## Wastes

- Version on 2026-11-21: `none`
- Folders: `design/concepts/Wastes/`, `src/RimMandrake/Wastes/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings A10 | `design/concepts/Wastes/design.md:379` | "The same food on another biome's map at the same temperature rots." No physical reason is given. | AMBIGUOUS |
| code 66 | `src/RimMandrake/Wastes/Source/RM_Middenshell.cs:861`<br>`src/RimMandrake/Wastes/Source/RM_MapComponent_WastesStorms.cs:46` | Middenshell and Wastes storms run on their own biome (storms: UNCLEAR). (also in Minerals, RustCathedral, SleepingIce, Webwork, WeepingStones) | MECHANIC-GATE (UNCLEAR for Wastes storms and Minerals quarry) |

Ruled 2026-11-21 (convert at the next version): A10: food rots by its conditions (temperature and the like), the same on every map.
Not ruled yet (wait for his card): none.

## Webwork

- Version on 2026-11-21: `none`
- Folders: `design/concepts/Webwork/`, `src/RimMandrake/Webwork/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings C9 | `design/Jawa/worldbuilding/biomes/the_webwork.md:180`<br>`design/Jawa/worldbuilding/biomes/the_propane_lakes.md:180` | "No hyperweave from any source but the Webwork"; ban #8 binds the biome map only (the propane lakes file has no concept folder). The Webwork as source; a roster ban. | WORDING |
| rulings (a) | `design/Jawa/worldbuilding/biomes/the_webwork.md:206` | The light-moat is "the only base-defense of its kind on the planet". | TEXT-TO-REVIEW |
| code 66 | `src/RimMandrake/Webwork/Source/RM_WebworkSiege.cs:65` | Webwork siege runs only on its biome. (also in Minerals, RustCathedral, SleepingIce, Wastes, WeepingStones) | MECHANIC-GATE |

Not ruled yet (wait for his card): none.

## WeepingStones

- Version on 2026-11-21: `none`
- Folders: `design/concepts/WeepingStones/`, `src/RimMandrake/WeepingStones/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| code 66 | `src/RimMandrake/WeepingStones/Source/RM_WalkingCondenser.cs:63` | The walking condenser runs only on its biome. (also in Minerals, RustCathedral, SleepingIce, Wastes, Webwork) | MECHANIC-GATE |

Not ruled yet (wait for his card): none.

## Wreckage

- Version on 2026-11-21: `none`
- Folders: `src/RimMandrake/Wreckage/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings (a) | `design/Jawa/worldbuilding/biomes/wreck_fields.md:161` | "Life is in circles around live wrecks, and nowhere else." (Wreck fields have no concept folder; Wreckage is the nearest source folder.) | TEXT-TO-REVIEW |

Not ruled yet (wait for his card): none.

## CreatureBehaviors

- Version on 2026-11-21: `none`
- Folders: `src/RimMandrake/CreatureBehaviors/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings A6 | `design/RimMandrake/unified_direct_sun_heat_2026-10-19.md:269`<br>`infrastructure/state/items/DIRECT_SUN_SETTINGS_WIRE_FEWER_KNOBS.md:24`<br>`design/concepts/TerminalBiomes/cleanse/tickets.md:317` | "No new cross-biome switch is built"; "Unsupported: may work outside our biomes, not tested" (2026-10-15). CreatureBehaviors holds the Direct Sun engine. (also in TerminalBiomes) | AMBIGUOUS |
| code 29 | `src/RimMandrake/CreatureBehaviors/Source/RM_MapComponent_ShadeGrid.cs:172-175` | Every map-wide sun-heat effect needs the biome to carry RM_SunHeatExtension (the "Stillshade" sun-exposure mechanic; census could not tell Long Shade from Stillsand). (also in LongShade, Stillsand) | MECHANIC-GATE |
| code 30 | `src/RimMandrake/CreatureBehaviors/Source/RM_MapComponent_PinnedSun.cs:63`<br>`src/RimMandrake/CreatureBehaviors/Source/RM_HeatSoundscape.cs:127`<br>`src/RimMandrake/CreatureBehaviors/Source/RM_HeatSoundscape.cs:175`<br>`src/RimMandrake/CreatureBehaviors/Source/RM_TrackGridPatches.cs:106`<br>`src/RimMandrake/CreatureBehaviors/Source/RM_TrackSurfaceExtension.cs:84` | Pinned sun, heat soundscape and track surface run only on biomes with the extension or listed in biomes. Pinned sun serves Stillsand. | MECHANIC-GATE |

Ruled 2026-11-21 (convert at the next version): A6: no switch reads a biome; each "Enable outside this biome" switch becomes a plain on/off, default on, and the "Unsupported" label goes.
Not ruled yet (wait for his card): none.

## DivingInteraction

- Version on 2026-11-21: `none`
- Folders: `src/RimMandrake/DivingInteraction/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings A4 | `CLAUDE.md:184`<br>`design/RimMandrake/standing_rulings.md:233`<br>`design/RimMandrake/biome_rulings.md:210` | "No biome has its own heat kind ... except the Scald" (card 2026-11-20). Open: biome exception, or physics of steam and hot water anywhere? (Scald lives in TerminalBiomes and DivingInteraction.) (also in TerminalBiomes) | AMBIGUOUS |
| code 40 | `src/RimMandrake/DivingInteraction/Source/RM_MapComponent_ScaldVentForecast.cs:43`<br>`src/RimMandrake/DivingInteraction/Source/RM_MapComponent_ScaldImmersionBerth.cs:32` | The vent forecast (steam clock) and the immersion berth run only on Scald floor maps (defName). (also in TerminalBiomes) | MECHANIC-GATE |
| code 41 | `src/RimMandrake/DivingInteraction/Source/RM_ChillFireGate.cs:30`<br>`src/RimMandrake/DivingInteraction/Source/RM_MapComponent_ChillBoilShroud.cs:106` | The Chill boil shroud runs only on Chill seabed maps (defName plus pocket-map flag). (also in TerminalBiomes) | MECHANIC-GATE |
| code 42 | `src/RimMandrake/DivingInteraction/Source/RM_SeaDiveHatch.cs:44-45`<br>`src/RimMandrake/DivingInteraction/Source/RM_SeaDiveHatch.cs:68-69` | The sea-dive hatch accepts only biomes in SeaGenerators (defName table). | UNCLEAR |

Ruled 2026-11-21 (convert at the next version): A4: hot water is physics, not a Scald exception; the Scald's clock is rewritten to read hot water and its steam on any map.
Not ruled yet (wait for his card): none.

## EnvironmentalHazards

- Version on 2026-11-21: `none`
- Folders: `src/RimMandrake/EnvironmentalHazards/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| code 18 | `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_WarmGround.cs:93-94` | Warm ground (floor heat) runs only where the biome carries RM_WarmGroundExtension and Enabled. Serves The Rot. (also in TheRot) | MECHANIC-GATE |
| code 19 | `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_AcceleratedRot.cs:65-66` | Accelerated rot (food spoils faster) runs only where the biome carries RM_AcceleratedRotExtension. Biome served: the census does not name it. | MECHANIC-GATE |
| code 20 | `src/RimMandrake/EnvironmentalHazards/Source/RM_IncidentWorker_SporeCloud.cs:25`<br>`src/RimMandrake/EnvironmentalHazards/Source/RM_SporeAllergyIncidents.cs:11`<br>`src/RimMandrake/EnvironmentalHazards/Source/RM_SporeAllergyIncidents.cs:29`<br>`src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_LivingProduce.cs:35`<br>`src/RimMandrake/EnvironmentalHazards/Source/RM_Patch_LivePrepViability.cs:68`<br>`src/RimMandrake/EnvironmentalHazards/Source/RM_HediffComp_SheenExposure.cs:43` | Spore cloud, spore allergy, live-produce heat, strict live prep, sheen exposure: per-biome switch RM_KitFronts.Enabled(key, biome). Serves The Rot kit. (also in TheRot) | MECHANIC-GATE |
| code 21 | `src/RimMandrake/EnvironmentalHazards/Source/RM_IncidentWorker_SteamDevil.cs:27`<br>`src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_RoilVortexSpawner.cs:75` | Steam devils and roil vortices appear only in Greentide (defName). (also in Greentide) | MECHANIC-GATE |
| code 22 | `src/RimMandrake/EnvironmentalHazards/Source/RM_HediffComp_ForgeOnSurvival.cs:132-133`<br>`src/RimMandrake/Miasma/Patches/RM_Miasma_ForgeOnSurvival.xml:74-224` | The forge-on-survival hediff effect fires only in Miasma (7 onlyInBiomes entries). (also in Miasma) | MECHANIC-GATE |
| code 23 | `src/RimMandrake/EnvironmentalHazards/Source/RM_IncidentWorker_ContagionProbe.cs:36` | The contagion probe incident fires only on The Forge (defName). (also in TheForge) | UNCLEAR |
| code 24 | `src/RimMandrake/EnvironmentalHazards/Source/RM_IncidentWorker_WalkerSurfacing.cs:39`<br>`src/RimMandrake/TerminalBiomes/Defs/IncidentDefs/RM_WalkerSurfacing.xml:63` | The walker surfacing incident is limited to listed biomes (allowedBiomes). (also in TerminalBiomes) | UNCLEAR |
| code 25 | `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_StrandingPools.cs:165`<br>`src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_StrandingPools.cs:286`<br>`src/RimMandrake/EnvironmentalHazards/Source/RM_JobGiver_ReturnToWater.cs:49` | Stranding pools and returning to water run only if the biome carries RM_StrandingPoolsExtension. Biome served: not named. | UNCLEAR |
| code 26 | `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_GradientAxis.cs:233`<br>`src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_GradientAxis.cs:277`<br>`src/RimMandrake/EnvironmentalHazards/Source/RM_GameCondition_GradientSurge.cs:51` | The gradient axis and gradient surge need the biome's extension. Biome served: not named. | UNCLEAR |
| code 27 | `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_WaterTruce.cs:64`<br>`src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_CarriedFilthHediffLink.cs:32` | Water truce and the carried-filth hediff link need the biome's extension. Biome served: not named. | UNCLEAR |
| code 28 | `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_SumpLivingMap.cs:87` | Sump living map (census did not read the context). Biome read. (also in TheSump) | UNCLEAR |

Not ruled yet (wait for his card): none.

## ExplosiveGrowth

- Version on 2026-11-21: `none`
- Folders: `src/RimMandrake/ExplosiveGrowth/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings R6 | `design/RimMandrake/explosive_growth_ruled_spec_2026-10-16.md:228`<br>`design/RimMandrake/explosive_growth_ruled_spec_2026-10-16.md:372` | Our plants outside our biomes get vanilla growth, "labelled unsupported" (card 2026-10-17, OQ-10). | REVERSED |
| rulings R7 | `infrastructure/state/items/EXPLOSIVE_PLANT_GROWTH_1.md:5-8` | Scope is Baroque Biomes' own biomes (2026-10-16 words). | REVERSED |
| rulings A11 | `design/RimMandrake/explosive_growth_ruled_spec_2026-10-16.md` | Section 6, setting A: vanilla crops in our biomes need water nearby. Applied everywhere, it changes vanilla crops on the whole planet. | AMBIGUOUS |
| rulings A12 | `design/Jawa/worldbuilding/biomes/the_cracked_lands.md:273`<br>`infrastructure/state/items/EXPLOSIVE_PLANT_GROWTH_1.md:5-8` | Two growth rulings disagree: "the owner took it planet-wide" (2026-09-06) against "only natively apply to plants within the Baroque Biomes" (2026-10-16). (also in CrackedLands) | AMBIGUOUS |
| code 65 | `src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthRegistry.cs:95-104`<br>`src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthRegistry.cs:129-134`<br>`src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs:135`<br>`src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs:176`<br>`src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs:340`<br>`src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs:479`<br>`src/RimMandrake/ExplosiveGrowth/Source/RM_SoakSources.cs:54`<br>`src/RimMandrake/ExplosiveGrowth/Source/RM_IncidentWorker_BloomBurst.cs:41` | Explosive growth runs only in HomeBiomes; vanilla crops need water only in scope; soak refused in noSoakBiomes; snowmelt applies in snowmeltBiomes. (also in CrackedLands) | MECHANIC-GATE |
| switch | `src/RimMandrake/ExplosiveGrowth/Source/ExplosiveGrowthMod.cs:122`<br>`src/RimMandrake/ExplosiveGrowth/Source/ExplosiveGrowthMod.cs:243` | nativesSameRuleInOtherBiomes "UNSUPPORTED: our plants follow the same rule in other biomes" (default false). | SWITCH (ruled 2026-11-21) |

Ruled 2026-11-21 (convert at the next version): A11 (his card, 2026-11-21 5:34 PM PST): vanilla crops need water nearby wherever the ground is dry and hot, a condition, not 'in our biomes'. Temperate maps are untouched. 'Dry and hot' is defined as a measurable condition when Explosive Growth next advances. A12 (the Conductor's call under his cards of 2026-11-21): no conflict is left. Explosive growth belongs to the plant species and acts wherever those plants and water are. The Baroque biomes are where the plants are native (biome data). Switch nativesSameRuleInOtherBiomes: each becomes a plain on/off for its mechanic, default on, with no biome in it (the Conductor's call 2026-11-21: the same as the six-switch ruling).
Not ruled yet (wait for his card): none.

## FlowWorks

- Version on 2026-11-21: `0.1.0`
- Folders: `design/concepts/FlowWorks/`, `src/RimMandrake/FlowWorks/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings (unnumbered) | `design/RimMandrake/sprinklers_design_2026-10-16.md:112` | "The 2026-10-15 rule keeps us out of other biomes". The census did not read it in context. | AMBIGUOUS |
| rulings C10 | `design/RimMandrake/biome_rulings.md:217` | "Natives should drink their own environmental water" (2026-11-01). Biome data, worded by biome. | WORDING |

Not ruled yet (wait for his card): none.

## BiomesShell

- Version on 2026-11-21: `none`
- Folders: `src/RimMandrake/BiomesShell/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings R8 | `design/RimMandrake/biome_mod_architecture.md:485`<br>`design/RimMandrake/biome_mod_architecture.md:494-496` | A biome-defName allowlist; default answer "yes on RM_X, no elsewhere". The design is itself a biome check. | REVERSED |
| switch | `src/RimMandrake/BiomesShell/Source/RM_BiomesMod.cs:123-130` | Per-biome roster enabled[key] (default true). It gates Pyrelands and ExplosiveGrowth mechanics (mechanicsGated). | SWITCH (ruled 2026-11-21) |

Ruled 2026-11-21 (convert at the next version): switch Per-biome roster enabled[key]: each becomes a plain on/off for its mechanic, default on, with no biome in it (the Conductor's call 2026-11-21: the same as the six-switch ruling).
Not ruled yet (wait for his card): none.

## Minerals

- Version on 2026-11-21: `none`
- Folders: `src/RimMandrake/Minerals/`

| census row | file:line | what is confined | class |
|---|---|---|---|
| code 66 | `src/RimMandrake/Minerals/Source/RM_MineralQuarry.cs:116-132` | The mineral quarry picks its plan by biome (UNCLEAR). (also in RustCathedral, SleepingIce, Wastes, Webwork, WeepingStones) | MECHANIC-GATE (UNCLEAR for Wastes storms and Minerals quarry) |
| switch | `src/RimMandrake/Minerals/Source/Kernel/RM_MineralPolicyKernel.cs:17`<br>`src/RimMandrake/Minerals/Source/Kernel/RM_MineralPolicyKernel.cs:239` | OtherBiomes policy per mineral row (default not read by the census). | SWITCH (ruled 2026-11-21) |

Ruled 2026-11-21 (convert at the next version): switch OtherBiomes policy per mineral row: each becomes a plain on/off for its mechanic, default on, with no biome in it (the Conductor's call 2026-11-21: the same as the six-switch ruling).
Not ruled yet (wait for his card): none.

## Rule texts (corrected by this item)

Corrected on 2026-11-21 by item RIMMANDRAKE_RULE_MECHANICS_ARE_UNIVERSAL_THE_BIOME_ONLY_SHOWCASES. These rows are rule texts, not a mod's design.

| census row | file:line | what is confined | class |
|---|---|---|---|
| rulings R1 | `CLAUDE.md:219` | "We promise biome mechanics only inside our own biomes." The Forge haze commit cites it. | REVERSED |
| rulings A1 | `design/RimMandrake/standing_rulings.md:178-185` | "Biome mechanics are promised inside our own biomes only" (2026-10-15 release words). | AMBIGUOUS |
| rulings A2 | `src/RimMandrake/rimflow/concept_floor.json:26` | biome_scope, standing and not waivable: "promised inside our biomes only". A program enforces it. | AMBIGUOUS |
| rulings A3 | `src/RimMandrake/rimflow/roles/designer_write.md:81` | "Others are biomes in scope only". | AMBIGUOUS |

Precedents that already state the rule (census section b; no change, no row count): Direct Sun (`CLAUDE.md`, `design/RimMandrake/standing_rulings.md`, `design/RimMandrake/biome_rulings.md`, `design/RimMandrake/unified_direct_sun_heat_2026-10-19.md:166`); shade-seeking 2026-11-10 (`design/RimMandrake/biome_rulings.md` section 5); Rot warm mat 2026-10-22; explosive growth 2026-09-06 (`design/Jawa/worldbuilding/biomes/the_cracked_lands.md:273`); seas 2026-11-20; cover card 2026-11-19; anima trees and rites 2026-10-11 and 2026-10-01; the "Featured here / Merely active here" pattern; "learned here, works anywhere" know-how items; slime `design/RimMandrake/RM_gelatinous_slime_mod.md:170`.


## Dated design records that state the old reading

These records cite the 2026-10-15 ruling as a confinement. That ruling now governs testing only (`design/RimMandrake/standing_rulings.md` §Every mod ships superb Mod Settings). Each is read again when its mod advances.

- `design/RimMandrake/flowworks_settings_audit_2026-10-18.md:5`
- `design/RimMandrake/artist_biome_inspiration_design.md:147`
- `design/RimMandrake/fulgurite_lightning_design_pass_2026-10-15.md:190`
- `design/RimMandrake/thirst_fluids_design_2026-10-17.md:27`
- `design/RimMandrake/biome_transitions_judgment_2026-11-01.md:35`, `design/RimMandrake/biome_transitions_judgment_2026-11-01.md:51`
- `design/RimMandrake/rot_warm_mat_portable_2026-10-22.md:25`, `design/RimMandrake/rot_warm_mat_portable_2026-10-22.md:107`
- `design/RimMandrake/sun_and_shade_modularity_2026-10-19.md:11`, `design/RimMandrake/sun_and_shade_modularity_2026-10-19.md:242`
- `design/RimMandrake/sprinklers_design_2026-10-16.md:70`, `design/RimMandrake/sprinklers_design_2026-10-16.md:109`, `design/RimMandrake/sprinklers_design_2026-10-16.md:151`
- `design/RimMandrake/explosive_growth_deep_dive_2026-10-16.md:382`
- `design/RimMandrake/flowworks_natural_water_play_2026-10-17.md:386`, `design/RimMandrake/flowworks_natural_water_play_2026-10-17.md:443`
- `design/RimMandrake/designer_brief_for_gpt_2026-11-02.md:104`
- `design/RimMandrake/designer_codex_2026-11-09/GelatinousSlime/record.json:43`
- `design/RimMandrake/designer_codex_2026-11-09/Stillsand/record.json:85`
- `design/RimMandrake/fluff_cuts_2026-10-23.md:186` (the switches "stay, off and labelled": by his card of 2026-11-21 each becomes a plain on/off, default on)
- `design/RimMandrake/webworks_open_questions_2026-10-22.md:48`, `design/RimMandrake/webworks_open_questions_2026-10-22.md:71` (the same switch sentence)
