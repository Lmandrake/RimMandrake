# Mod retirement audit — what the seven low-survival mods ACTUALLY ship

Decision document, 2026-09-05. Companion to
`design/Jawa/worldbuilding/creature_recognizability_rule.md` §6 ("Retire whole mods
where little survives"). **Nothing here has been executed** — no ModsConfig edit, no
deploy, no removal.

🔴 **The premise of the audit: creature survival is not a retirement decision.** Four
of these mods have zero surviving creatures under the strict recognizability rule and
three of the four are still KEEPs, because the fauna was never the reason they were
installed.

## Verdicts at a glance

| mod | packageId | live fauna → survive | verdict |
|---|---|---|---|
| Megafauna | `Spino.Megafauna` | 15 → 0 | **RETIRE-AFTER-ABSORB** (patch cleanup only) |
| Beasts of the Rim (Continued) | `Mlie.BeastsoftheRim` | 10 → 0 | **RETIRE-AFTER-ABSORB** (one About.xml dep) |
| Mythic Ages: Megafauna Bestiary | `veterano.mythicages.megafaunabestiary` | 10 → 0 | **RETIRE** — clean kill |
| GRiNDTerra Biomes | `GRimTerra.Biomesmod` | 9 → 0 | 🔴 **KEEP** — 15 biomes, 123 terrains, 117 plants |
| Biomes! Caverns | `BiomesTeam.BiomesCaverns` | 89 → 9 | 🔴 **KEEP** — 1,003 planet tiles, a precept in the shipped ideoligion |
| Biomes! Polluted Lands | `BiomesTeam.BiomesPollutedLands` | 37 → 9 | **KEEP** — 40 plants, 18 genes, a faction, our SeasWaterline fish |
| Jurassic Rimworld (Dinosaurs Only) | `Mlie.JurassicRimworldDinosaursOnly` | 28 → 5 | **RETIRE-AFTER-ABSORB** (owner already ruled) |

All seven are ACTIVE in the frozen 601-mod list
(`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`).

## Method and instruments

- Content inventory: every `Defs`-rooted XML in each mod's **1.6** folder (plus shared
  root folders), parsed with ElementTree and counted by root child tag. Older version
  folders, `OldDefs/`, `LegacyAssets/` and `Source/` excluded — the game does not load them.
- Live-vs-cut fauna: `python3 src/RimMandrake/Utils/cherrypicker.py --type ThingDef`
  against the **live** Cherry Picker settings (1,291 cut ThingDefs, 2026-09-04 15:31),
  intersected with each mod's animal ThingDefs. These reproduce the recognizability
  table's "live" column exactly (15 / 10 / 89 / 38 / 9 / 10 / 28), so the two agree.
- Planet usage: `world/ASHKARR_WORLDMAP_tiles.csv` (21,872 tiles — the frozen world),
  biome counted directly. ⚠️ The `.rws` saves were NOT grepped: biomes there are
  shortHash indices in compressed grids and a text scan returns a wrong number.
- Our own usage: `src/` grepped for each packageId and each defName prefix, then the
  hits parsed per-biome.

---

## 1. Megafauna — `Spino.Megafauna` (workshop 1055485938, 6.7 MB)

**Content.** 62 ThingDefs = **38 animals** + 20 eggs/body-part items + 4 wool/milk
resources. 38 PawnKindDefs. 14 BodyPartDefs, 7 BodyDefs, 7 BodyPartGroupDefs (Flipper,
Fangs, GlyptodonCarapace, Pincer, Stinger, six centipede segments), 2 DamageDefs
(`ToxicSting`), 1 ManeuverDef, 1 ToolCapacityDef, 2 `Megafauna.MegafaunaToggleableSpawnDef`.
**Zero** biomes, terrains, plants, buildings, research, incidents, factions. 2 patch ops.

**Assembly.** `1.6/Assemblies/Megafauna.dll` — see §8.

**Reverse deps.** No hard dependency anywhere. Vanilla Genetics Expanded (ACTIVE)
declares `loadAfter Spino.Megafauna` — an ordering hint only, harmless when the mod is gone.

**Our content.** `src/RimUtinni/Doctrine/Patches/MegafaunaYield.xml` (37 Megafauna
defNames), `AnimalTolerances_Ashkarr.xml` (15), `CreatureNames_Ashkarr.xml` (17),
`CreatureResize_Ashkarr.xml` (3), `BiomeCast_Ashkarr.xml` (7 kinds cast onto Ash'karr).
**Every one is wrapped in `PatchOperationConditional`/`PatchOperationFindMod`**, so all
of it becomes a silent no-op rather than an error. ⚠️ Bare-name matching over-counts:
`Daeodon` is vanilla and `Arthropleura` is also a Jurassic defName.

**VERDICT — RETIRE-AFTER-ABSORB.** Nothing to absorb *creatively* (0 of 15 survive, and
the mod is 38 recognisable Pleistocene mammals — mammoth, smilodon, aurochs, giant
sloth — which is the exact failure mode the rule exists to catch). What must happen
first is bookkeeping: strip the dead Megafauna groups out of MegafaunaYield.xml and the
four Ash'karr patches, and drop `Spino.Megafauna` from the `loadAfter` list in
`src/RimUtinni/Doctrine/About/About.xml`. Then it is safe.

---

## 2. Beasts of the Rim (Continued) — `Mlie.BeastsoftheRim` (2194018641, 3.5 MB)

**Content.** 45 ThingDefs = **19 animals** + 20 leathers/wool + 6 eggs. 19 PawnKindDefs.
That is the entire mod — no biomes, terrain, plants, buildings, research, incidents,
factions, hediffs, damage types. **No C# assembly at all.** Zero patch operations.

**Reverse deps.** 🔴 **`mandrake.rsw.seaswaterline` (OUR mod) declares a HARD
`<modDependencies>` entry on `mlie.beastsoftherim`.** Retiring the mod without editing
that About.xml leaves our own mod advertising a missing dependency. The actual content
coupling is thin: `Waterline_Lane1.xml` references exactly one Beasts of the Rim
creature (`Megasquid`, 6 hits) against 50 hits on Biomes! Polluted Lands fish.

**Our content.** `MegafaunaYield.xml` (6 defNames), `AnimalTolerances_Ashkarr.xml` (3),
`BiomeCast_Ashkarr.xml` (7) — all gated, all silent on retirement.

**VERDICT — RETIRE-AFTER-ABSORB.** The purest fauna-only mod in the set: it ships
animals and the leather they drop, nothing else, and not one line of C#. Absorb list is
empty (0 of 10 survive — its roster is armadillo, black bear, penguin, zebra, mandrill,
neanderthal, plus *After Man* speculative megafauna that still read as "big antelope",
"big elephant"). **Two edits gate it:** remove `mlie.beastsoftherim` from SeasWaterline's
`<modDependencies>` and `<loadAfter>`, and decide what `Waterline_Lane1.xml`'s Megasquid
lane becomes.

---

## 3. Mythic Ages: Megafauna Bestiary — `veterano.mythicages.megafaunabestiary` (3537788184, 31 MB)

**Content.** 140 ThingDefs = **21 animals** + 72 items (meat/milk/cheese/wool/horn/drug
lines) + 7 buildings + 40 weapons and abstracts. 61 ThoughtDefs, 57 SoundDefs, 37
RecipeDefs, 21 HediffDefs, 21 PawnKindDefs, 6 IncidentDefs (`MA_GreatGnautHerd`,
`MA_PlastemmothMigration`, `MA_SimbakubHunt`, `MA_DunbearAwakens`, …), 4 BodyDefs,
1 AbilityDef, 1 DesignationCategoryDef (`MA_MythicProduction_Tribal`), 1 StuffCategoryDef.
**Zero** biomes, terrains, plants, factions, research.

⚠️ The one thing worth a second look is the **flat tribal workstation set** —
`MA_MythicCraftingSpot`, `MA_FlatButcherBlock`, `MA_FlatCookingTable`,
`MA_FlatCraftingBench` under `MA_MythicProduction_Tribal`, with 4 WorkGiverDefs and 37
recipes behind them. That is genuine primitive-production content and is thematically
close to a Jawa scavenger clan. **It is not used by anything of ours today** — the only
occurrence anywhere in `src/` is `MA_MythicProduction_Tribal` in a category denylist in
`gen_furniture_register.py`.

**Assembly.** `1.6/Assemblies/MythicAges.dll` — see §8.

**Reverse deps.** **NONE.** No hard dependency, no `loadAfter`, no patch anywhere in the
601-mod list or the deployed folder. The only outside references are ours, and both are
gated: `MegafaunaYield.xml` and one `<li>Mythic Ages: Megafauna Bestiary</li>` FindMod
block in `PawnFlavorPhase2_ThoughtDef.xml`.

**Our content.** 10 `MA_` creatures cast in `BiomeCast_Ashkarr.xml`; all gated. No use
of its items, buildings, incidents or recipes.

**VERDICT — RETIRE. This is the clean kill.** Zero surviving creatures, zero dependents,
zero of its non-fauna content is wired into anything we have built, and every reference
to it is already conditional. Its 61 thoughts, 37 recipes and 6 incidents all exist
purely to service its own 21 animals; with the animals cut the rest is unreachable.
If the tribal workbench set is wanted, that is a **separate, later** decision — take the
four buildings as an `Absorbed_*` set, don't keep 31 MB and a DLL for them.

---

## 4. GRiNDTerra Biomes — `GRimTerra.Biomesmod` (3537211820, 255 MB) 🔴 KEEP

The mod is named "Biomes" and the name is honest. Fauna is **3 % of what it ships.**

**Content.** **15 BiomeDefs** · **123 TerrainDefs** · 136 ThingDefs of which **117 are
plants** (and only 9 animals, 9 filth, 1 item) · **11 WeatherDefs** (coloured fogs and
snows, `TheMist`) · 13 ScatterableDefs · 9 PawnKindDefs · 19 patch operations.

**What it is doing for us right now — two separate, independent jobs:**

1. **`BiomeCypreJungle` is painted on the frozen planet: 191 tiles** of
   `world/ASHKARR_WORLDMAP_tiles.csv`, and per `ASHKARR_WORLD_DEFINITION.md` §5b it
   carries two Wildsteam Clan settlements placed on the owner's own coordinates —
   ***Oilpalm*** (tile 4271, 58.6 °C, the clan's hottest seat) and ***Warthorn***
   (tile 16641, 1,128 m, a jungle massif). It also forms one of the two groves flanking
   the Scald.
2. 🔴 **Its plants are the flora backbone of the DESERT, which is the campaign's home
   biome.** `src/RimUtinni/UtinniPatches/Patches/BiomeFlora_Ashkarr.xml` uses **all 117 of its
   plant defs — every single one**, and they are concentrated exactly where the colony lives:
   `AridShrubland` 21 of 66 plants · `ZBiome_Grasslands` 20 of 45 · `Desert` 10 of 30 ·
   `ZBiome_DesertOasis` 9 of 50 · `AB_RockyCrags` 8 · `AB_FeraliskInfestedJungle` 7 ·
   `ZBiome_Badlands` 6 · `PoisonForest` 6. Desert + ExtremeDesert + AridShrubland alone
   is **8,088 of 21,872 tiles**.

**Reverse deps.** `GRimTerra.Worldmap` (ACTIVE) and our own `mandrake.rm.patches`
declare `loadAfter GRimTerra.Biomesmod` — soft only. `GRimTerra.TerrainRetexturemod`
(ACTIVE) has an **empty** `<modDependencies>` block, so it does not hard-require it.

**Our content.** `src/RimMandrake/MandrakePatches/Patches/GrimTerraTexPaths_Fix.xml`
(we repair four of its broken texPaths), plus `BiomeFlora_Ashkarr.xml`,
`BiomeCast_Ashkarr.xml`, `PlantTolerances_Ashkarr.xml`, `AnimalTolerances_Ashkarr.xml`,
and `JawaBenchWorldTools.cs`.

**VERDICT — KEEP, and the fauna question is a non-question.** The right action is to
**cut its 9 animals** (`GRimCobra`, `GRimTortoise`, `GRimMonitorLizard`, `GRimBullfrog`,
`GRimLavaSnail`, `GRimPinkbird`, `GRimQuail`, `GRimStoneCrab`, `ThrumbaToad` — a cobra,
a tortoise, a bullfrog and a quail, all instantly nameable) in Cherry Picker and keep
everything else. Retiring the mod would erase 191 authored planet tiles, two named
settlements, and the desert flora the world was written around.

---

## 5. Biomes! Caverns — `BiomesTeam.BiomesCaverns` (2969748433, 329 MB) 🔴 KEEP

**Content.** 403 ThingDefs = **90 animals** + **105 plants** + 46 items + 12 buildings +
138 apparel/abstracts. **3 BiomeDefs** (`BMT_CrystalCaverns`, `BMT_EarthenDepths`,
`BMT_FungalForest`) · **6 BiomeVariantDefs** · **4 Geological-Landforms landform files**
(Crystal Caverns, Earthen Depths, Fungal Forest, Mineshaft) · **13 TerrainDefs** ·
**13 IncidentDefs** (CaveIn, Earthquake, four diseases, `BMT_ThrumbungusPasses`,
`BMT_SporeCloud`, …) · 3 ResearchProjectDefs · 3 GenStepDefs · 3 GameConditionDefs ·
20 HediffDefs · 19 RecipeDefs · 57 SoundDefs · 23 music tracks · 12 fish · 11 thoughts ·
4 FeatureDefs + 4 RulePackDefs (named cavern features) · 2 WeatherDefs · **1 MemeDef
(`BMT_CavernDweller`)** · **1 PreceptDef (`BMT_FungusEating_DontCare`)** · a chemical,
a need, a stuff appearance, a terrain affordance, a world object. 73 patch operations,
and compat folders for 14 other mods plus all five DLCs.

**Planet usage — the decisive number.** `BMT_CrystalCaverns` **578 tiles** and
`BMT_FungalForest` **425 tiles** = **1,003 of 21,872 tiles (4.6 % of the frozen world)**,
and one settlement sits on `BMT_FungalForest`.

🔴 **Blocker: the shipped ideoligion references it.** `src/Jawa/ideoligion/The Salvation.rid`
— the campaign's saved religion — contains the precept **`BMT_FungusEating_DontCare`**.
A `.rid` holding a dead defName cannot be repaired by removing the mod; it is exactly the
`Could not load reference to` class of failure.

**Flora coupling.** `BiomeFlora_Ashkarr.xml` uses **92 of Caverns' 99 plant defs** (the
file's 131 `BMT_` entries are 92 Caverns + 39 Polluted Lands), carrying
`BMT_FungalForest` (62 of its 69 plants), `BMT_CrystalCaverns` (20 of 42), `Wasteland`
(17 of 44 — and Wasteland is 1,699 tiles), `PoisonForest` (13 of 35), `AB_TarPits` (6 of 9).

**Reverse deps.** No hard dependency from another mod. `mandrake.rm.patches` and
`mandrake.rut.researchretag` declare `loadAfter`. ⚠️ **One un-gated patch of ours:**
`src/RimStarWars/Armoury/Patches/Absorbed_AdditionalMods/kotorweapons/BiomesCaverns/Absorbed_Kotorweapons_BiomesCaverns_Patch_KotORCrystalFormationInjector.xml`
adds KotOR crystals to `BMT_CrystalsGenerator` with no FindMod wrapper — it would go
silently dead, not error. `ResearchRetag` retags `BMT_AdvancedFungi` and
`BMT_ResearchMushrooms`.

**VERDICT — KEEP, decisively.** 9 of its 89 creatures survive; the other 80 should be
cut in Cherry Picker. The mod itself is load-bearing three times over: 4.6 % of the
planet's tiles, 131 plants in our authored flora, and a precept baked into the shipped
`.rid`.

---

## 6. Biomes! Polluted Lands — `BiomesTeam.BiomesPollutedLands` (3390196656, 68 MB) KEEP

**Content.** 144 ThingDefs = **39 animals** + **40 plants** + 15 items + 1 building +
48 eggs/abstracts. **18 `BiomesCore.Defs.BMT_GeneDef` genes** + 1 GeneCategoryDef
(`BMT_MutaGenes` — acidic glands, cluster eyes, conjoined heart, impaling claws,
psychic cortex, evermutating cells) · 15 HediffDefs · 9 DamageDefs · **1 FactionDef
(`BMT_PustuleHornets`)** with its own GenStepDef hive and raid-loot ThingSetMaker ·
1 QuestScriptDef (`BMT_MutapoxJoins`) · 3 IncidentDefs · 3 fish · 2 AbilityDefs ·
2 ThinkTreeDefs · 1 TerrainDef · 1 StatDef · 5 thoughts. 54 patch operations. Ships
full C# source at `3390196656/Source/`. **No BiomeDefs of its own** — it enriches
polluted *vanilla* biomes.

**Reverse deps.** 🔴 **`mandrake.rsw.seaswaterline` (OUR mod) declares a HARD
`<modDependencies>` on `biomesteam.biomespollutedlands`.** `Waterline_Lane1.xml` is
built on its fish: `BMT_MucklurkerCatfish`, `BMT_TaintedTurtle` and the three
`BMT_MutatingTumorfish` stages, 50 references.

**Our content.** `src/RimUtinni/FactionSlate/Patches/OnlyOurFactions.xml` explicitly
handles `BMT_PustuleHornets` (zeroing `startingCountAtWorldCreation`) — i.e. we have
already made a deliberate decision about its faction rather than ignoring it. Its plants
supply part of the `Wasteland`, `PoisonForest` and `AB_TarPits` flora above.

**VERDICT — KEEP.** 9 of 37 creatures survive, which is already above the retirement
band, and the non-fauna content — 41 plants, an 18-gene mutation set, a faction we have
positioned, a quest, and the fish our own SeasWaterline mod is built on — is the
reason it is installed. Cut the 28 recognisable animals, keep the mod.

---

## 7. Jurassic Rimworld — Dinosaurs Only (Continued) — `Mlie.JurassicRimworldDinosaursOnly` (3541510004, 81 MB)

Owner has already named this one for retirement, absorbing **Segnosaurus + 4**.

**Content.** 403 ThingDefs = **131 animals** + 8 items (three dino leathers, DinoChitin,
`Snailglass`) + 264 fertilised/unfertilised eggs. **228 SoundDefs** (four calls per
dinosaur) · 131 PawnKindDefs · 4 HediffDefs + 3 DamageDefs + 3 ManeuverDefs +
3 ToolCapacityDefs (Troodon venom, Gera acid, Pulmonoscorpius sting) · 1 BodyDef +
1 BodyPartGroupDef (tail attacker) · 2 WorkGiverDefs (Paste, Silk) · 1 RecipeDef ·
1 IncidentDef (`ManhunterPackBigAnimals`). **Zero** biomes, terrains, plants, buildings,
research, factions. Zero patch operations. Three small assemblies — see §8.

**Reverse deps.** No hard dependency anywhere in the 601-mod list. Every reference is
ours and gated: `MegafaunaYield.xml`, `AnimalBiomeDuplicates_Fix.xml` /
`AnimalBiomeDuplicates_Generated.xml`, `BiomeCast_Ashkarr.xml` (21 `JRW` kinds cast),
`CreatureNames_Ashkarr.xml`, `CreatureResize_Ashkarr.xml`, `AnimalTolerances_Ashkarr.xml`.

**VERDICT — RETIRE-AFTER-ABSORB.** What must be absorbed is only the 5 survivors
(Segnosaurus + 4) as `Absorbed_*` ThingDef/PawnKindDef pairs with their textures, four
SoundDefs each, and — if any of the five carries one — the venom/acid HediffDef +
DamageDef + ManeuverDef + ToolCapacityDef quartet, which is easy to forget because it
lives in four separate def types. Nothing else in the mod exists independently of the
dinosaurs. **Nothing else in the world would be lost:** no biome, no terrain, no plant,
no tile.

---

## 8. The C# assemblies

**How this was determined:** no decompiler is installed, so the load-bearing question was
answered from the XML side — every `Class="…"`, `compClass`, `<workerClass>` and dotted
custom def type referenced by each mod's own defs, plus a search for those namespaces in every other
workshop and deployed mod. That answers *"does anything outside this mod name a type it
defines"*, which is the question that matters. Anything about internal Harmony behaviour
below is INFERRED and marked as such.

| assembly | size | what it is | verdict |
|---|---|---|---|
| `Megafauna.dll` | 11 KB | Harmony-patches `BiomeDef.CommonalityOfAnimal` and `MapTemperature.SeasonAcceptableFor` (season/biome gating for its own animals). Defines `Megafauna.MegafaunaToggleableSpawnDef` (2 defs — a Mod Settings panel letting the player toggle which of its animals spawn). Ships ModCheck + its own Harmony copy in the 1.0 folder to auto-patch A Dog Said and Giddy-up; the only third-party classes its XML names are `GiddyUpCore.CompProperties_Mount` / `DrawingOffsetPatch`, i.e. it *consumes* Giddy-up, not the reverse. | **FAUNA-ONLY** |
| `BiomesCaverns.dll` + `BMT_ThingDefReplacer.dll` + `Caveworld_Flora_Unleashed.dll` | 66 + 37 KB | 🔴 **BIOME-AND-TERRAIN.** Owns four map GenStep classes — `GenStep_ScatterCrystals`, `GenStep_ScatterStalagmite`, `ScattererValidator_RoughRockBuildable`, `GenStep_ClearCavernCenter_Archonexus` — that generate the cavern maps themselves, plus a bundled Caveworld Flora Unleashed (self-contained: `ThingDef_FruitingBody`, a mushroom-fermenting JobDriver/WorkGiver, `MapComponent_CaveFungus`). Harmony surface (INFERRED) covers cavern-roof detection, drop-pod and shuttle landing legality, siege/raid drop spots, infestation scoring and indoor/outdoor thought workers. Everything else its XML names belongs to **Biomes! Core** (`BiomesCore.CompProperties_*`, `BiomesCore.DefModExtensions.*`) — Caverns is a *consumer* of that framework. | **BIOME-AND-TERRAIN** |
| `BiomesPollutedLands.dll` | 67 KB | Largest surface of the seven, and ships full C# source at `3390196656/Source/`. Defines 17+ XML-referenced types of its own: `GenStep_PollutedHives` (map generation), `GeneExtension` + `HediffCompProperties_GeneHediff` + `RitualOutcomeComp_PawnGenes` (the 18-gene mutation system), `QuestNode_Root_MutapoxWanderer` (the quest), `CompProperties_AbilityCorpseEater`, `CompProperties_AutoTame`, `HediffGiver_PollutedOnly`, and `BMT_PollutedFish.FishExtension`. | **BIOME-AND-TERRAIN** (genes + quest + hives, well beyond fauna) |
| `GRimTerraBiomes.dll` | 11 KB | ⚠️ It carries **no Harmony patch at all** — it is 15 `BiomeWorker_*` subclasses, one per BiomeDef (`BiomeWorker_CypreJungle`, `BiomeWorker_Toxlands`, `BiomeWorker_Areeb`, …), wired by bare `<workerClass>` rather than `Class=`. Those workers decide which world tiles a biome may occupy, so **the DLL is not optional decoration — it is how the 15 biomes exist.** Everything else its defs name is Vanilla Expanded Framework (`VEF.AnimalBehaviours.*`, `VEF.Weathers.WeatherOverlayExtension`, `VEF.Cooking.*`). | **BIOME-AND-TERRAIN** |
| `MythicAges.dll` | 72 KB | Seven XML-referenced comps, **all animal behaviour for its own 21 creatures**: `CompProperties_BurrowSpawner`, `CompProperties_BurrowSpawnerItem`, `CompProperties_HarpeagleNestSpawner`, `CompProperties_NestFeedingCycle`, `CompProperties_PackInstinct`, `CompProperties_PlastemmothInstinct`, `BestiaryManehound.HediffCompProperties_ManehoundRescue`, plus `BurrowIncidentExtension` for its 6 incidents. Nothing outside the mod names any of them. | **FAUNA-ONLY** |
| `DinoShoo.dll`, `ExtraButcheringProducts.dll`, `ManhuntingDinos.dll` | 5 + 8 + 8 KB | Three tiny single-purpose assemblies. Only one is XML-referenced: `ExtraButcheringProducts.CompProperties_SpecialButcherChance` (the chance a butchered dinosaur drops DinoChitin / Snailglass). `ManhuntingDinos` adds `IncidentWorker_DinosaurManhunterPack`, wired from the mod's own `ManhunterPackBigAnimals` IncidentDef; `DinoShoo` is a bare `HarmonyPatches.PatchAll` wrapper whose target could not be identified (INFERRED: a shoo/AI tweak for large animals). All three serve the dinosaurs only. | **FAUNA-ONLY** |
| *(Beasts of the Rim)* | — | **No assembly at all.** Pure XML: animals, their leathers, their eggs. | n/a |

🔑 **The load-bearing answer, for all seven: NOTHING outside these mods names a type any
of them defines.** The two frameworks their XML leans on — **Biomes! Core**
(`biomesteam.biomescore` / `biomesteam.coreframework`) and **Vanilla Expanded
Framework** — are separate, active mods that stay whichever way these decisions go.
Caverns and Polluted Lands are consumers of Biomes! Core, not providers to it.

---

## 9. The clean kills — what can go this week

| | |
|---|---|
| **Mythic Ages: Megafauna Bestiary** | ✅ **Zero absorption, zero dependents.** Nothing outside the mod references it except two of our own patch files, both already gated. Drop it. |
| **Beasts of the Rim (Continued)** | ✅ Zero absorption. **One edit first:** remove `mlie.beastsoftherim` from `<modDependencies>` and `<loadAfter>` in `src/RimStarWars/SeasWaterline/About/About.xml`, and re-home the single `Megasquid` lane in `Waterline_Lane1.xml`. |
| **Megafauna** | ✅ Zero absorption. Cleanup only: dead groups in `MegafaunaYield.xml` and four Ash'karr patches, plus a `loadAfter` line in Doctrine's About.xml. Nothing breaks if the cleanup slips — every reference is conditional. |
| **Jurassic (Dinosaurs Only)** | ⏳ **Absorb 5 first** (Segnosaurus + 4). Already the owner's ruling. No world content at stake. |

Retiring the first three removes **41 MB** and 3 mods from a 601-mod list; adding
Jurassic makes it **122 MB** and 4 mods.

## 10. What would be LOST — the biome mods, concretely

⛔ **These are not retirements. This section exists so the cost is on the record.**

**GRiNDTerra Biomes** — retiring it would delete:
- **`BiomeCypreJungle`, painted on 191 tiles** of the frozen planet, carrying the
  Wildsteam Clan seats ***Oilpalm*** and ***Warthorn***. A biome def missing under a
  world that names it is unrecoverable — the world would have to be re-authored.
- **All 117 of its plant defs**, every one of which the authored Ash'karr flora uses, concentrated in the biomes the
  colony actually lives in: `AridShrubland` (21 of 66), `ZBiome_Grasslands` (20 of 45),
  `Desert` (10 of 30), `ZBiome_DesertOasis` (9 of 50).
- 123 TerrainDefs and 11 coloured weathers (fogs and snows) — the alien-planet
  palette, of which only a slice is currently spent.
- The 15 `BiomeWorker_*` classes in its DLL that decide which world tiles each of its
  biomes may occupy. There is no XML-only version of this mod.
- 14 further unused biomes (Areeb shrublands, The Toxlands, The Evernights, Blue
  desert, Bleached desert, Grazelands, Deadlands, The Grindlands, Overgrown Ruins,
  The Neverglades, Tropical Desepelago, Bluefire Mountains, Arctic/Frozen ruins) —
  headroom, not current cost.
- **Kept in exchange for cutting 9 animals** (cobra, tortoise, monitor lizard,
  bullfrog, lava snail, pinkbird, quail, stone crab, thrumba toad). That is the trade.

**Biomes! Caverns** — retiring it would delete:
- **`BMT_CrystalCaverns` (578 tiles) and `BMT_FungalForest` (425 tiles) — 1,003 tiles,
  4.6 % of the frozen planet**, plus a settlement on the Fungal Forest.
- **The precept `BMT_FungusEating_DontCare` inside the shipped ideoligion**
  `src/Jawa/ideoligion/The Salvation.rid`. A `.rid` cannot be repaired by removing a mod.
- **92 of its 99 plant defs** in the authored flora — 62 of the 69 in Fungal Forest, 20 of 42 in
  Crystal Caverns, **17 of 44 in `Wasteland` (1,699 tiles)**, 13 of 35 in `PoisonForest`.
- 4 Geological Landforms landform definitions, 13 terrains, 3 GenSteps, 13 incidents
  (cave-ins, earthquakes, four cave diseases), 3 research projects, a meme, 12 fish,
  23 music tracks, and compat patches for 14 other active mods.

**Biomes! Polluted Lands** — retiring it would delete:
- The **fish our own SeasWaterline mod is built on** (`BMT_MucklurkerCatfish`,
  `BMT_TaintedTurtle`, three `BMT_MutatingTumorfish` stages) and break a hard
  `<modDependencies>` we declare.
- **39 of its 40 plant defs**, feeding the `Wasteland` / `PoisonForest` / `AB_TarPits` flora.
- **18 mutation genes** + the `BMT_MutaGenes` category — the pollution-mutation
  vocabulary, which nothing else in the stack supplies.
- The `BMT_PustuleHornets` faction we have already deliberately positioned in
  `FactionSlate/Patches/OnlyOurFactions.xml`, its hive GenStep and raid-loot maker,
  and the `BMT_MutapoxJoins` quest.
- It ships **no biome of its own** — it enriches polluted vanilla biomes — so no planet
  tiles are at risk. The loss is flora, genes, faction and fish.

## 11. Blockers

| blocker | affects | fix |
|---|---|---|
| 🔴 `src/RimStarWars/SeasWaterline/About/About.xml` declares a **hard `<modDependencies>`** on `biomesteam.biomespollutedlands` **and** `mlie.beastsoftherim` | Beasts of the Rim (retiring), Polluted Lands (keeping) | Edit our own About.xml before retiring Beasts of the Rim; re-home the `Megasquid` lane in `Waterline_Lane1.xml` |
| 🔴 `The Salvation.rid` holds the precept `BMT_FungusEating_DontCare` | Biomes! Caverns | Not fixable by removal — this alone forecloses retiring Caverns |
| 🔴 1,003 planet tiles on `BMT_CrystalCaverns`/`BMT_FungalForest` and 191 on `BiomeCypreJungle` | Caverns, GRiNDTerra | Not fixable — the world is frozen and hand-authored |
| ⚠️ `Absorbed_Kotorweapons_BiomesCaverns_Patch_KotORCrystalFormationInjector.xml` targets `BMT_CrystalsGenerator` **un-gated** | Biomes! Caverns | Moot while Caverns is kept; wrap in `PatchOperationFindMod` if that ever changes |

**No other mod in the 601-mod list declares a hard dependency on any of the seven.**
Every third-party coupling found was a `loadAfter` ordering hint (Vanilla Genetics
Expanded → Megafauna; GRimTerra World Map → GRiNDTerra Biomes), which is inert when the
target is absent. `GRimTerra.TerrainRetexturemod` has an empty `<modDependencies>` block
and does **not** require GRiNDTerra Biomes.

## 12. What this changes about the recognizability table

The table in `creature_recognizability_rule.md` §6 lists four mods at 0 % survival as if
that made them four retirements. **It makes one and a half.** Mythic Ages is the only
one of the four that is fauna-and-nothing-else *and* unreferenced; Megafauna and Beasts
of the Rim are fauna-only but each carries a small cleanup debt; and GRiNDTerra is a
biome mod whose animals were never the point. The survival percentage measured the
fauna, and for three of the seven the fauna is not what the mod is for.

⇒ **A mod's survival percentage is an input to the retirement question, never the
answer.** The answer is: *what breaks in the frozen world, the shipped ideoligion, and
our own patches if this def set disappears?*
