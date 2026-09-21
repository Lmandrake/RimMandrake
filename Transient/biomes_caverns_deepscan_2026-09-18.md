# Deep scan: Biomes! Caverns / Polluted Lands / Fossils — 2026-09-18

Read-only census. Target packageIds: biomesteam.biomescaverns, biomesteam.biomespollutedlands, biomesteam.biomesfossils

## Location

- Biomes! Caverns (BiomesTeam.BiomesCaverns): `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/2969748433/`
- Biomes! Fossils (BiomesTeam.BiomesFossils): `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3100958580/`
- Biomes! Polluted Lands (BiomesTeam.BiomesPollutedLands): `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3390196656/`
- All three found under the Steam workshop root; none present under the RimWorld/Mods local-mods root.

## Biomes! Caverns

Folder analyzed: `1.6/` subtree (also has parallel `1.4/`, `1.5/` copies). Ships a bundled sub-mod, "Caveworld Flora Unleashed", at `1.6/CaveworldFloraUnleashed/` (own Assemblies/Defs/Patches, no separate About.xml — loaded as part of this mod, not a standalone packageId). Also carries `1.6/Mods/*` (11 subfolders: AlphaAnimals, AlphaBiomes, AlphaMythology, MedievalOverhaul, MusicExpandedPatch, UINotIncluded, VanillaBrewingExpanded, VanillaFactionsExpandedMechanoid, VanillaFurnitureExpandedArchitect, VanillaHelixienGasExpanded, VanillaPlantsExpandedMushrooms, VBgE, VFE) and `Common/Mods/PathfindingFramework` — these are third-party-compat patch bundles that only load if the target mod is also active, not core content. `1.6/DLC/*` (Anomaly, Biotech, Ideology, Odyssey, Royalty) holds DLC-conditional patches/defs. `1.6/Landforms/` has 4 LandformDefs (BMT_CrystalCaverns, BMT_EarthenDepths, BMT_FungalForest, BMT_Mineshaft).

### 1. Def counts (element parse, `1.6/Defs`)

ThingDef 342 (heuristic split: plant 98, building 10, item/other 234 — creature pawns are separately in PawnKindDef, not ThingDef, in this mod's authoring style), PawnKindDef 90, SoundDef 57, HediffDef 18, RecipeDef 13, IncidentDef 13, TerrainDef 10, ThoughtDef 8, DamageDef 5, BodyDef 4, FeatureDef 4, RulePackDef 4, **BiomeDef 3**, BiomeVariantDef 3, GameConditionDef 3, GenStepDef 2, ResearchProjectDef 2, WeatherDef 2, plus 1 each of a custom `BiomesCore.Defs.AvoidTerrainOnGameStartDef`, DesignatorDropdownGroupDef, WorldObjectDef, ToolCapacityDef, TaleDef, StuffAppearanceDef, ChemicalDef, NeedDef, EffecterDef, TerrainAffordanceDef. (221 XML files scanned, 0 parse errors.)

**BiomeDefs: `BMT_CrystalCaverns`, `BMT_EarthenDepths`, `BMT_FungalForest`.**

Bundled `CaveworldFloraUnleashed/Defs`: ThingDef 25 (plant 18, building 2, item/other 5), ThoughtDef 3, HediffDef 2, JobDef 2, RecipeDef 2, WorkGiverDef 2, ResearchProjectDef 1, TerrainDef 1 (15 files).

`1.6/DLC/*` adds: ThingDef 23, MemeDef 1, PreceptDef 1, GenStepDef 1, DesignatorDropdownGroupDef 1, TerrainDef 1 (Ideology meme/precepts for fungus-eating, Anomaly monolith/obelisk patches, Biotech gene/exostrider patches, Odyssey fish resource + lava patch, Royalty apparel + anima/titles patches).

### 2. C# surface

`Assemblies/BiomesCaverns.dll` (66,048 bytes) — ascii `strings` found 25 matching class-name lines including: `GenStep_CavernRocksFromGrid`, `GenStep_ClearCavernCenter`, `GenStep_ClearCavernCenter_Archonexus`, `GenStep_RocksFromGrid`, `GenStep_ScatterCrystals`, `GenStep_ScatterGroup`, `GenStep_ScatterStalagmite`, `GenStep_Scatterer`, `GenStep_ScattererBestFit`, `GenStep_SpecialTrees`, `GenStep_Archonexus`, `GenStep_ArchonexusResearchBuildings`, plus a large Harmony patch surface (`HarmonyPatch`, and ~25 `*_Patch` postfix/transpiler classes touching drop-pod placement, roofing, room-size thoughts, tunnel hive spawning, wild-plant spawner ticks, thrumbo/gauranlen incident workers, etc.). No MapComponent class name found in this DLL.

`CaveworldFloraUnleashed/Assemblies/Caveworld_Flora_Unleashed.dll` (36,864 bytes) — **`MapComponent_CaveFungus` IS present here** (confirmed via ascii `strings`), alongside `MapComponent`, `MapComponentTick`, `GenCaveFungusReproduction`, `Util_Caveworld_Flora_Unleashed`, `get_IsOnCaveFungusGrower`.

### 3. Patches (`1.6/Patches` core folder only; DLC/Mods-compat patches counted separately above)

65 PatchOperations across 9 files. Distinct xpath targets: 13 raw, 6 with a parseable `defName=` literal: `FueledStove`, `GroundPenetratingScanner`, `Hive`, `Make_Kibble`, `Medicine`, `PodLauncher` — plus non-defName-scoped xpaths hitting `MapGeneratorDef[@Name="MapCommonBase"]/genSteps` (injects cavern gen steps into the base map generator), `ThingDef[@Name="TorchBase"]` (abstract parent, so this reaches every torch-family thing), and a `GenStepDef/genStep/allowRoofed` toggle.

### 4. Contribution paragraph

Biomes! Caverns adds 3 new underground BiomeDefs (crystal caverns, earthen depths, fungal forest) each with their own Landform, plus a large PawnKindDef roster (90) of cave-adapted creatures, matching plants (98 ThingDefs), terrain/rock defs, and custom map-generation C# (crystal/stalagmite scattering, cavern rock carving, room-size/indoor-thought overrides for underground colonies). It bundles the separate "Caveworld Flora Unleashed" content pack (edible/brewable cave fungus, a `MapComponent_CaveFungus` that drives fungus spread/reproduction on the map, plus recipes and a research project), and ships DLC-specific integration for all five expansions (Ideology memes/precepts, Biotech genes, Anomaly monolith interaction, Odyssey fish/lava, Royalty apparel/anima). It is the largest and most structurally load-bearing of the three mods: it is a genuine biome-generation mod with map-gen C#, not just a def pack.

## Biomes! Polluted Lands

Folder analyzed: `1.6/`. Also has `1.6/Mods/Odyssey/Patches/BiomesPollutedLands_Odyssey_Biomes.xml` (Odyssey-conditional compat, patches Odyssey's own polluted biomes). Note: **this mod ships NO BiomeDef of its own** — `grep BiomeDef` across its whole tree returns nothing defining one; its own About.xml confirms it "adds new plants and animals to polluted vanilla biomes as well as some modded ones", i.e. it is a content-injection mod that PATCHES existing biomes (vanilla + its own Caverns biomes + Ashlands/Islands/wasteland biomes from other Biomes! mods) rather than adding new biome geometry.

### 1. Def counts (`1.6/Defs`)

ThingDef 141 (heuristic split: plant 45, building 1, item/other 95 — again creature pawns land in PawnKindDef not category="Animal" ThingDef by this team's convention), PawnKindDef 39, a custom `BiomesCore.Defs.BMT_GeneDef` 18 (mutation genes), HediffDef 15, DamageDef 9, ThoughtDef 5, JobDef 3, IncidentDef 3, ThinkTreeDef 2, AbilityDef 2, BodyDef 1, FactionDef 1, ThingSetMakerDef 1, EffecterDef 1, GeneCategoryDef 1, RecipeDef 1, GenStepDef 1, NeedDef 1, QuestScriptDef 1, TerrainDef 1, StatDef 1. (111 XML files, 0 parse errors.) No BiomeDef, confirming the note above.

### 2. C# surface

`Assemblies/BiomesPollutedLands.dll` (67,072 bytes) — rich surface, ~200+ named classes/members visible via ascii `strings`, including: `GenStep_PollutedHives`, a Harmony patch class `BMT_PollutedLands.HarmonyPatches` plus `Patch_Gene_OverrideBy`, `Harmony_CompWakeUpDormant`, `Harmony_GiveObservedThought`, `Harmony_ThrumboPassPatch`; a mutation-gene system (`Gene_MutagenicFertility`, `Gene_EvermutatingCells`, `Gene_ToxspewingPores`, `Gene_OverdevelopedOrgans`, `Gene_CarrionMetabolism`, `Gene_ConjoinedHeart`, `Gene_BloodExplusion`, `Gene_MoltingRegeneration`, `Gene_ProtectiveLeprosy`); hediffs/comps for the same (`Hediff_Mutapox`, `HediffComp_MutagenicFertility`, `HediffComp_OverdevelopedOrgan`, `HediffGiver_PollutedOnly`); creature/incident behavior (`IncidentWorker_Mutapox`, `IncidentWorker_HungryLocusts`, `IncidentWorker_BunkerBugPasses`, `IncidentWorker_ThrumboPasses`, `IncidentWorker_DiseaseHuman`, `IncidentWorker_HagbloomSprout`, `BMT_Swarmcaller`, `BMT_Maligoat`); a quest layer (`QuestNode_Root_MutapoxWanderer`, `QuestNode_Root_WandererJoin_WalkIn`); and job drivers (`JobDriver_BloodVomit`, `JobDriver_Vomit`). No MapComponent class name found in this DLL. **`MapComponent_CaveFungus` is NOT present here.**

### 3. Patches (`1.6/Patches`)

74 PatchOperations across 14 files. 57 distinct raw xpath targets, 43 with a parseable `defName=` literal. This is overwhelmingly a **biome-patching** surface: it touches `BiomeDef[defName=...]/wildPlants` and `/pollutionWildAnimals` for 23+ distinct vanilla/modded biomes — vanilla (`Desert`, `ExtremeDesert`, `TemperateForest`, `TemperateSwamp`, `TropicalRainforest`, `TropicalSwamp`, `BorealForest`, `ColdBog`, `Tundra`, `IceSheet`, `SeaIce`), this same team's own Caverns biomes (`BMT_CrystalCaverns`, `BMT_EarthenDepths`, `BMT_FungalForest`), its own Islands sub-biomes, and third-party mod biomes (Regrowth's `RG_*Wasteland`, "Mashed Ashlands" `Mashed_Ashlands_*` x11). Also patches `GeneDef[defName="PerfectImmunity"]`, `HediffDef[defName="PenoxycylineHigh"]`, `StatDef[defName="ToxicEnvironmentResistance"]`, `ThoughtDef[AteCorpse/AteRottenFood]`, `HediffDef[PregnantHuman]`, `RitualOutcomeEffectDef[ChildBirth]`, and generic `RecipeDef` ingredient filters (RawBerries/WoodLog).

### 4. Contribution paragraph

Biomes! Polluted Lands is a cross-cutting gameplay-system mod, not a biome-geometry mod: it injects new plants/animals into every polluted vanilla and modded biome (via 74 patches touching 23+ BiomeDefs) and layers a mutation-gene/hediff system on top (18 custom GeneDefs, mutagenic fertility, toxin dependence, mutapox disease with its own incident and quest chain, blood-vomit job/hediff behavior, a swarmcaller creature ability). Its replace-cost is not "redraw a biome" but "recreate the polluted-biome ecosystem content and the mutation mechanic," which is why it carries the heaviest patch-surface of the three despite shipping zero BiomeDefs.

## Biomes! Fossils

Folder analyzed: `1.6/`. Also carries `1.6/Source/` (source dump, not part of what's loaded) and DLC-conditional folder `1.6/DLC` (Royalty: 1 LearningDesireDef, 1 JobDef). About.xml: "Adds dinosaur and other related fossils. Dig up fossil and amber, restore and reconstruct huge skeletons and other fossils, and display them in beautiful museums! ... Safe to add, not safe to remove." No dependency beyond Harmony — **it does not depend on BiomesCore or ship any BiomeDef**; it is unrelated to biome generation.

### 1. Def counts (`1.6/Defs`)

ThingDef 93 (heuristic split: building 7 [display cases etc.], item/other 86 — fossil/amber items, skeleton pieces), DesignatorDropdownGroupDef 6, ThingCategoryDef 2, TraderKindDef 2, DesignationCategoryDef 1, JoyKindDef 1, JobDef 1, JoyGiverDef 1, ResearchProjectDef 1, RoomRoleDef 1, RulePackDef 1, ThoughtDef 1, WorkGiverDef 1. (23 XML files, 0 parse errors.) No BiomeDef, no PawnKindDef, no HediffDef of note. `1.6/DLC` adds LearningDesireDef 1, JobDef 1 (Royalty-conditional).

### 2. C# surface

`Assemblies/BMT_Fossils.dll` (22,016 bytes) — small, self-contained. No `MapComponent`, `GenStep_`, or `HarmonyPatch` string found (366 ascii strings extracted, so this is a genuine "not present" rather than an extraction miss — UTF‑16 recheck via `strings -e l` also came back with only version-resource metadata, no additional classes). Visible classes: `JobDriver_MuseumLearning`, `JobDriver_VisitMuseum`, `JoyGiver_VisitMuseum`, `LearningGiver_MuseumLearning`, `RoomRoleWorker_Museum`, `CompDisplay`/`CompDisplayCase` + `CompProperties_Display`/`CompProperties_DisplayCase`, `PlaceWorker_OnDisplayBase{Large,Medium,Small}`. This is a museum/display-case comp system plus a joy/learning activity, no Harmony, no map generation.

### 3. Patches (`1.6/Patches`)

2 PatchOperations across 2 files. Targets: `FactionDef[@Name="OutlanderFactionBase"]/caravanTraderKinds` (adds its fossil trader to outlander caravans) and `ThingDef[defName="Apparel_PsychicInsanityLance" or defName="Apparel_PsychicShockLance"]/thingCategories` (recategorizes two vanilla psychic-lance items, presumably into a museum-display category).

### 4. Contribution paragraph

Biomes! Fossils is a self-contained content mod unrelated to biome generation: dinosaur/fossil/amber items, dig-up/restore/reconstruct gameplay, and a museum-display-case comp system with a joy activity (visit museum) and a child learning activity (`RoomRoleWorker_Museum`, `LearningGiver_MuseumLearning`). Its footprint on the rest of the mod list is minimal — 2 patches only — so cutting it loses only its own self-contained content, not any shared biome or gene infrastructure the other two mods provide.

## VERDICT

- **Biomes! Caverns — HIGH.** 3 BiomeDefs (`BMT_CrystalCaverns`, `BMT_EarthenDepths`, `BMT_FungalForest`) + matching Landforms + ~90 PawnKindDefs + ~98 plant ThingDefs + custom map-gen C# (GenStep_Scatterer/RocksFromGrid/ClearCavernCenter family) + a bundled second content pack (Caveworld Flora Unleashed, with its own `MapComponent_CaveFungus`) + DLC integration across all five expansions. Cutting it removes actual biome-generation capability, not just flavor content — our own biome kit would have to replace the biomes, the map-gen steps, and the cave-fungus mechanic.
- **Biomes! Polluted Lands — MEDIUM-HIGH.** Zero BiomeDefs of its own (it patches 23+ existing biomes' wildlife/plants instead), but carries a real gameplay system: 18 mutation GeneDefs, a mutapox disease + quest chain, blood-vomit/toxin-dependence hediffs, several IncidentWorkers, and Harmony patches. Replace cost is "recreate the polluted-biome ecosystem + mutation mechanic," not "recreate a biome."
- **Biomes! Fossils — LOW.** Defs-only content mod (93 ThingDefs, no BiomeDef, no PawnKindDef) plus a small self-contained comp system (museum display cases, joy/learning activity). Only 2 patch operations touching the rest of the game. No MapComponent, no GenStep, no Harmony patch in its DLL. Its own About.xml says "safe to add, not safe to remove" but that is a save-compatibility warning, not a mechanical dependency — nothing else in the mod set appears to depend on it structurally.

**`MapComponent_CaveFungus` attribution: it belongs to Biomes! Caverns**, specifically its bundled "Caveworld Flora Unleashed" sub-pack at `1.6/CaveworldFloraUnleashed/Assemblies/Caveworld_Flora_Unleashed.dll`. It is **not** present in Biomes! Fossils' or Biomes! Polluted Lands' DLLs (confirmed absent by ascii-string scan of both, and Fossils' DLL was independently checked to be a genuine "not present" rather than an extraction miss).

## UNKNOWN

- Whether the 1.4/1.5 copies of each mod differ meaningfully from 1.6 in def/patch counts — not scanned (1.6 is the live game version per project facts, so this was deprioritized).
- The exact runtime effect of each Harmony patch (only class/method names were read via `strings`, not decompiled IL) — e.g. whether `Patch_Gene_OverrideBy` in Polluted Lands or the ~25 `*_Patch` classes in Caverns are prefix/postfix/transpiler and what they actually change.
- Whether `1.6/Mods/*` compat-patch bundles in Caverns or the `Odyssey` compat patch in Polluted Lands are currently exercised by the live mod list (would require cross-referencing against `ModsConfig.xml`, which this task's scope excluded).
- Whether Fossils' "safe to add, not safe to remove" warning corresponds to any actual save-corruption risk on removal (would require checking a save with its defs present — out of scope, read-only recon).
- Total texture/sound asset counts were not measured (out of scope — only Defs/Patches/Assemblies were requested).
