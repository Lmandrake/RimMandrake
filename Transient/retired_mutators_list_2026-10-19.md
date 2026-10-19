# Retired-donor world-map data: mutators, landmarks and other per-tile data, 2026-10-19

Prepared by FOUNDRY, offline, read-only. Question (owner): *which mutators did our worldmap use that come from retired donors (Alpha Biomes AB_, Star Wars Animal Collection wild plants + Sarlacc lairs, any other)?* Answer first, detail after.

## The short answer

- **Only two retired donors ever put a TileMutator on the planet: Alpha Biomes (21 mutators in the save, 8 of them also in the authoring CSV) and Star Wars Animal Collection (5 mutators in the save, 2 in the CSV).** Every other retired donor (ReGrowth, GrimTerra, Horrors, Cockroach, Isopoda, VFE Insectoids 2, Alpha Genes, Alpha Animals, Biomes! Core/Caverns/Polluted) contributes **zero** mutators and **zero** landmarks to the canonical save or the CSV (MEASURED: grid decode resolved every one of the 162 distinct mutator hashes; none belongs to them).
- **Everything non-retired the map uses** (Odyssey landforms, Core, Vanilla Landmarks Expanded `VEE_*`: the other 78 of the CSV's 88 mutator names) is out of scope.
- Of the 88 CSV names, **10 are retired-donor**: Alpha Biomes 8 (`AB_*`) and SWAC 2 (`sw_*`). The wild-plant mutators were **never in the CSV**: vanilla world generation rolled them onto desert tiles.
- **The CSV and the save disagree** on almost every row (the CSV is the 2026-08-23 authoring record; the save carries what worldgen/the paint actually produced). Both numbers are shown below; nothing is reconciled.
- The three lost biome hashes in the save (1135 / 546 / 222 tiles) are **not** AB_ biomes: they are our own renamed `RUT_ForsakenCrags`, `RUT_PoisonForest` and `RM_FE_Pyrelands`, already repaired in `CANONICAL_ASHKARR_START_2026-10-18_DONORFREE_REPAIRED.rws`. `donor_save_residue_2026-10-19.md` step 2 names AB_ biomes for them; that is wrong (see Disagreements).

## Instruments and saves compared

| label | file (in `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\`) | what it is |
|---|---|---|
| **canon** | `CANONICAL_ASHKARR_START_2026-09-12.rws` (17,483,421 bytes, mtime 2026-10-09) | the owner's canonical save, unedited |
| **df-10-15** | `CANONICAL_ASHKARR_START_2026-09-12_donorfree.rws` | 2026-10-15 strip of 1,429 SWAC mutator entries and the sw_ -> RSW_ landmark rename; AB_ left in |
| **df-10-18** | `CANONICAL_ASHKARR_START_2026-10-18_DONORFREE.rws` | second donor-free copy; AB_ mutators and landmarks gone |
| **df-rep** | `CANONICAL_ASHKARR_START_2026-10-18_DONORFREE_REPAIRED.rws` | df-10-18 plus the live lost-biome repair (BENCH, 2026-10-19) |

Instruments (all MEASURED, none a blind scan): **grid decode** = `/home/mandrake/.seat-tmp/FOUNDRY/sp/dec.py` (inflates `tileMutatorDefsDeflate` ushort shortHashes + `tileMutatorTilesDeflate` int32 tile ids, resolves hashes against DefDump captures 2026-08-29T13-30-02Z [584 mods, includes donors] and 2026-10-19T11-23-54Z; same method as `phase0_save_mutators_restore_NOTE.md`; landmark and river/road/hilliness grids the same way). **CSV** = Python `csv` parse of `world/ASHKARR_WORLDMAP_mutators.csv` (6,710 rows, 88 distinct names; last commit 2026-08-23T21:39-07:00, a RECORD) and `world/ASHKARR_WORLDMAP_landmarks.csv` (563 rows). **Census** = `save_donor_census.py` on canon. `measure` is not on this seat's PATH, so no `measure` figure appears. Save cells read `entries / distinct tiles` (a tile can hold one mutator twice).

## Table 1. TileMutators on the map that derive from retired donors (26 rows: Alpha Biomes 21, SWAC 5)

"Def of ours" = a src/ XML/C# def that names it (MEASURED by whole-word search of `src/`). Mutator ports/refs in `.py` tooling (`ashkarr_landmarks.py`, `worldmap_effects.py`, `worldmap_prefill.py`) are not defs.

| defName | retired source | what it does to the tile | CSV tiles | canon save (entries / tiles) | CSV tiles also in canon | df-10-15 | df-10-18 / df-rep (each entries / tiles) | current state | def of ours? |
|---|---|---|---|---|---|---|---|---|---|
| `WildDantooinePlants` | SWAC `mlie.starwarsanimalcollection` | Wild plants band: a stretch of the tile grows many Plant_Dantuber_Wild (biomes AridShrubland/Grasslands/Tundra) | 0 (not in CSV) | 4 / 4 | - | 0 / 0 | 0 / 0 / 0 / 0 | stripped 2026-10-15 (donorfree copy); NO port yet (item HUBBA_GOURD_MUTATOR_MIGRATE_AT_THE_REPAINT) | No (item-tracked, no def) |
| `WildGalacticPlants` | SWAC `mlie.starwarsanimalcollection` | Wild plants band: a stretch of the tile grows many Plant_Chakroot_Wild (biomes AridShrubland/BorealForest/ColdBog/GlacialPlain/Grasslands/LavaField/TemperateForest/TemperateSwamp/TropicalRainforest/TropicalSwamp/Tundra) | 0 (not in CSV) | 2 / 2 | - | 0 / 0 | 0 / 0 / 0 / 0 | stripped 2026-10-15 (donorfree copy); NO port yet (item HUBBA_GOURD_MUTATOR_MIGRATE_AT_THE_REPAINT) | No (item-tracked, no def) |
| `WildTattooinePlants` | SWAC `mlie.starwarsanimalcollection` | Wild plants band: a stretch of the tile grows many Plant_HubbaGourd_Wild (biomes AridShrubland/Desert/ExtremeDesert) | 0 (not in CSV) | 1403 / 1403 | - | 0 / 0 | 0 / 0 / 0 / 0 | stripped 2026-10-15 (donorfree copy); NO port yet (item HUBBA_GOURD_MUTATOR_MIGRATE_AT_THE_REPAINT) | No (item-tracked, no def) |
| `sw_DeadSarlaccCave` | SWAC `mlie.starwarsanimalcollection` | Dead sarlacc: a hollow carcass cave to explore and salvage | 4 | 12 / 8 | 4 | 0 / 0 | 0 / 0 / 0 / 0 | stripped 2026-10-15 (donorfree copy); replaced by RSW_ mutator (ported, re-apply at repaint) | None (ported as RSW_DeadSarlaccCave) |
| `sw_SarlaccLair` | SWAC `mlie.starwarsanimalcollection` | Sarlacc pit: a living sarlacc and its burrow generated on the map | 1 | 8 / 8 | 0 | 0 / 0 | 0 / 0 / 0 / 0 | stripped 2026-10-15 (donorfree copy); replaced by RSW_ mutator (ported, re-apply at repaint) | No def references it; 3 XML comments + 1 C# comment (history only). Ported as RSW_SarlaccLair |
| `AB_AgariluxPrime_Mutator` | Alpha Biomes `sarg.alphabiomes` | Spawns an Agarilux Prime that releases spores DESTROYING EVERYTHING around it. | 0 (not in CSV) | 10 / 10 | - | 10 / 10 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_AmbientRadiation` | Alpha Biomes `sarg.alphabiomes` | 🔴 Game condition: background radiation subtly affects health and mutation rates. | 0 (not in CSV) | 104 / 104 | - | 104 / 104 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_AncientBloodRainVent` | Alpha Biomes `sarg.alphabiomes` | Periodically vents vaporised blood that condenses into blood rain over the map. | 0 (not in CSV) | 43 / 43 | - | 43 / 43 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_AncientDeathPallVent` | Alpha Biomes `sarg.alphabiomes` | 🔴 Periodically vents archites that REANIMATE CORPSES — your own dead get up. | 0 (not in CSV) | 33 / 33 | - | 33 / 33 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_AncientFreezingVent` | Alpha Biomes `sarg.alphabiomes` | Periodically vents freezing air across the map — recurring cold shocks. | 0 (not in CSV) | 61 / 61 | - | 61 / 61 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_AncientGreyPallVent` | Alpha Biomes `sarg.alphabiomes` | Periodically vents smoke that plunges the map into DARKNESS — solar and plant growth stop. | 0 (not in CSV) | 42 / 42 | - | 42 / 42 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_BumbledroneNests` | Alpha Biomes `sarg.alphabiomes` | Places 3–4 bumbledrone hives on the map — persistent hostile swarm spawners. | 26 | 26 / 26 | 26 | 26 / 26 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_DerelictArchonexus` | Alpha Biomes `sarg.alphabiomes` | Spawns one of five derelict archonexus structures — the highest-tier salvage in the mod. | 0 (not in CSV) | 2 / 2 | - | 2 / 2 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_DerelictBioLab` | Alpha Biomes `sarg.alphabiomes` | Spawns an abandoned biotech lab prefab to loot; investigating it can attract company. Flat tiles only. | 0 (not in CSV) | 5 / 5 | - | 5 / 5 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_DerelictClusters` | Alpha Biomes `sarg.alphabiomes` | 🔑 Scatters derelict MECHANOID CLUSTER structures to scavenge — steel, plasteel and components, no raid attached. | 0 (not in CSV) | 171 / 171 | - | 171 / 171 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_DerelictKemeticTemple` | Alpha Biomes `sarg.alphabiomes` | Spawns a derelict kemetic temple structure to explore and strip. | 0 (not in CSV) | 5 / 5 | - | 5 / 5 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_EdibleAirborneMicrofungi` | Alpha Biomes `sarg.alphabiomes` | Unlocks a microfungi collector building — edible ingredients pulled straight from the air. | 0 (not in CSV) | 30 / 30 | - | 30 / 30 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_FeraliskNest` | Alpha Biomes `sarg.alphabiomes` | Seeds feralisks into the tile — aggressive predators that will come for colonists. | 28 | 70 / 70 | 28 | 70 / 70 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_GeothermalHotspots` | Alpha Biomes `sarg.alphabiomes` | Unlocks an efficient biome geothermal plant under Furniture → build biome structures. | 5 | 8 / 8 | 5 | 8 / 8 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_GiantFossils` | Alpha Biomes `sarg.alphabiomes` | Scatters giant skeleton structures across the map — bone salvage and huge natural cover. | 0 (not in CSV) | 7 / 7 | - | 7 / 7 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_LocustPlagues` | Alpha Biomes `sarg.alphabiomes` | Adds locust swarms that strip unprotected yellow grass — a standing threat to grazing and crops. | 31 | 31 / 31 | 31 | 31 / 31 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_MagmaVents` | Alpha Biomes `sarg.alphabiomes` | Places 6–12 magma vents that erupt with molten rock and searing gas. | 10 | 8 / 5 | 5 | 8 / 5 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_MagmaticQuagmire` | Alpha Biomes `sarg.alphabiomes` | Molten, cracking, burning ground with no ponds — flat inland tiles only. | 3 | 6 / 3 | 3 | 6 / 3 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_MoldyEnvironment` | Alpha Biomes `sarg.alphabiomes` | 🔴 Game condition: being outdoors is near-unbearable — a standing mood cost on every outdoor job. | 0 (not in CSV) | 40 / 40 | - | 40 / 40 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_QuicksandPits` | Alpha Biomes `sarg.alphabiomes` | Shallow quicksand pools that impede movement across the map. Inland only. | 1 | 1 / 1 | 1 | 1 / 1 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |
| `AB_TarLakes` | Alpha Biomes `sarg.alphabiomes` | Impassable tar pools that CANNOT EVEN BE BRIDGED — permanent no-go ground. Inland only. | 11 | 10 / 10 | 10 | 10 / 10 | 0 / 0 / 0 / 0 | in canonical save; 0 in 10-18 DONORFREE copy (stripped there); no RSW_/RUT_ replacement | No (python tooling only) |

Totals (MEASURED): Alpha Biomes 713 mutator entries in canon, 713 in df-10-15, 0 in df-10-18; SWAC 1429 in canon, 0 in df-10-15. CSV tiles carrying a retired mutator: 92 (sum of rows 120).

### Table 1b. Retired-donor mutator defs that exist but are on **no** tile (CSV 0, canon 0: MEASURED)

| defName | retired source | what it does |
|---|---|---|
| `WildAlderaanPlants` | SWAC `mlie.starwarsanimalcollection` | Wild plants band: a stretch of the tile grows many Plant_HydenockTree_Wild (biomes TemperateForest/TemperateSwamp/ColdBog/BorealForest/TropicalSwamp/TropicalRainforest) |
| `WildFelucianPlants` | SWAC `mlie.starwarsanimalcollection` | Wild plants band: a stretch of the tile grows many Plant_FelucianGlowspore_Wild (biomes TropicalRainforest/TropicalSwamp) |
| `WildNabooPlants` | SWAC `mlie.starwarsanimalcollection` | Wild plants band: a stretch of the tile grows many Plant_Bubblespore_Wild (biomes ColdBog/TemperateSwamp/TropicalSwamp) |
| `WildRylothPlants` | SWAC `mlie.starwarsanimalcollection` | Wild plants band: a stretch of the tile grows many Plant_MunchFungus_Wild (biomes Glowforest) |
| `AB_BlizzariskNest` | Alpha Biomes `sarg.alphabiomes` | Seeds blizzarisks into the tile — cold-adapted aggressive predators. |
| `AB_ButterflySwarms` | Alpha Biomes `sarg.alphabiomes` | Adds harmless small butterflies to the animal roll — decoration, not a threat. |
| `AB_DerelictResort` | Alpha Biomes `sarg.alphabiomes` | Spawns a derelict resort prefab. Warm coastal tiles only (20–40°C, 1–6 coastal sides). |
| `AB_DessertTrees` | Alpha Biomes `sarg.alphabiomes` | Fills the map with dessert trees — an edible tree crop. |
| `AB_DigestiveSurface` | Alpha Biomes `sarg.alphabiomes` | 🔑 The ground DIGESTS DROPPED ITEMS left too long — you cannot stockpile outdoors here. |
| `AB_DiminutiveRegion` | Alpha Biomes `sarg.alphabiomes` | 🔴 FORCES THE MAP TO 100×100 — a quarter of normal area; everything is inside mortar range. |
| `AB_DunealiskNest` | Alpha Biomes `sarg.alphabiomes` | Seeds dunealisks into the tile — desert-adapted aggressive predators. |
| `AB_ExplodingAnimals` | Alpha Biomes `sarg.alphabiomes` | 🔴 Game condition: EVERY ANIMAL DETONATES ON DEATH — hunting and animal raids both become explosive. |
| `AB_ExtremeTemperatureFluctuations` | Alpha Biomes `sarg.alphabiomes` | 🔴 Game condition: scorching days and freezing nights — unheated rooms and crops both fail. |
| `AB_FleshTrees` | Alpha Biomes `sarg.alphabiomes` | Fills the map with flesh trees — organic harvest rather than wood. |
| `AB_GelatinousMemoryEcho` | Alpha Biomes `sarg.alphabiomes` | 🔴 Game condition: stored memory echoes occasionally bleed into reality as events. |
| `AB_GoldenTrees` | Alpha Biomes `sarg.alphabiomes` | Fills the map with golden cube trees — gold-yielding wood. |
| `AB_HealingSprings` | Alpha Biomes `sarg.alphabiomes` | Springs with curative properties — free healing on a mountainous inland tile. |
| `AB_LuminescentTrees` | Alpha Biomes `sarg.alphabiomes` | Fills the map with luminescent trees — light without power. |
| `AB_MutagenicSprings` | Alpha Biomes `sarg.alphabiomes` | Springs that MUTATE colonists and animals that touch them — inland tiles only. |
| `AB_NarrowRegion` | Alpha Biomes `sarg.alphabiomes` | 🔴 FORCES THE MAP TO 100×400 — a tall narrow battlefield instead of a square one. |
| `AB_OcularTransformation` | Alpha Biomes `sarg.alphabiomes` | Fills the map with alien ocular trees instead of ordinary flora. |
| `AB_OversaturatedSoil` | Alpha Biomes `sarg.alphabiomes` | Swaps fertile ground for even more fertile ground — higher crop yield with no work. |
| `AB_PetalStorms` | Alpha Biomes `sarg.alphabiomes` | Petal-storm weather at +50 commonality (five times the usual bump) — mood up, visibility and accuracy down. |
| `AB_PollinationFrenzy` | Alpha Biomes `sarg.alphabiomes` | 1.1x plants, paid for with worse allergies. |
| `AB_PropaneLakes` | Alpha Biomes `sarg.alphabiomes` | Lakes of liquid hydrocarbons — flammable terrain rather than water. |
| `AB_QuiveringSurface` | Alpha Biomes `sarg.alphabiomes` | The living ground raises movement difficulty across the whole map. |
| `AB_ResidualOverclocking` | Alpha Biomes `sarg.alphabiomes` | Unlocks a collector building that taps leftover mechanoid energy for power. |
| `AB_SterileGround` | Alpha Biomes `sarg.alphabiomes` | Only grass grows here — BUT DISEASE CHANCE DROPS 75%, which is a serious long-run saving. |
| `AB_SymbioticNutrients` | Alpha Biomes `sarg.alphabiomes` | Colonists need 10% less nutrition to feel full — a permanent food saving. |
| `AB_TechnoTrees` | Alpha Biomes `sarg.alphabiomes` | Fills the map with half-synthetic techno trees — component-yielding flora. |
| `AB_WideRegion` | Alpha Biomes `sarg.alphabiomes` | 🔴 FORCES THE MAP TO 400×100 — a long thin battlefield instead of a square one. |

Count by source in the 2026-08-29 capture: Alpha Biomes 48 defs (21 used above, 27 unused); SWAC 9 defs (5 used above, 4 unused). The current Steam workshop copy of Alpha Biomes (`1841354677`, 1.6/Defs XML) declares **59** TileMutatorDefs and an earlier 2026-10-04 dump showed **90** (that dump is overwritten; UNMEASURED now): 11 names exist only in the workshop XML (`AB_TarHoles`, `AB_ObsidianSpires`, `AB_DerelictLibrary`, `AB_ReddishWaters`, `AB_ReddishRains`, `AB_TumorousGrowths`, `AB_CerebrospinalFluid`, `AB_SugarChunks`, `AB_SweetRocks`, `AB_SweetFlora`, and others of the flora/soil kind). None of them is in the save or the CSV, so they do not change the answer.

## Table 2. Every other per-tile modification that derives from a retired donor

| kind | name | retired source | what it is | CSV | canon save | df-10-15 | df-10-18 / df-rep (each entries / tiles) | current state | def of ours? |
|---|---|---|---|---|---|---|---|---|---|
| LandmarkDef | `sw_DeadSarlacc` | SWAC `mlie.starwarsanimalcollection` | Landmark: a dead sarlacc cave (rolls sw_DeadSarlaccCave) | 4 | 7 | 0 | 0 / 0 | replaced by `RSW_DeadSarlacc` landmark in df-10-15 (7 there) | No (`RSW_DeadSarlacc` is ported as RSW_ landmark def) |
| LandmarkDef | `sw_Sarlacc` | SWAC `mlie.starwarsanimalcollection` | Landmark: a living sarlacc pit (rolls sw_SarlaccLair) | 1 | 8 | 0 | 0 / 0 | replaced by `RSW_Sarlacc` landmark in df-10-15 (8 there) | No (`RSW_Sarlacc` is ported as RSW_ landmark def) |
| LandmarkDef | `AB_HealingSprings` | Alpha Biomes `sarg.alphabiomes` | Landmark: curative springs | 0 | 0 | 0 | 0 / 0 | defined, on no tile | No (python tooling only) |
| LandmarkDef | `AB_MagmaticQuagmire` | Alpha Biomes `sarg.alphabiomes` | Landmark: molten cracking burning ground | 3 | 3 | 3 | 0 / 0 | in canon; removed in df-10-18 | No (python tooling only) |
| LandmarkDef | `AB_MutagenicSprings` | Alpha Biomes `sarg.alphabiomes` | Landmark: mutating ocular springs | 0 | 0 | 0 | 0 / 0 | defined, on no tile | No (python tooling only) |
| LandmarkDef | `AB_PropaneLakes` | Alpha Biomes `sarg.alphabiomes` | Landmark: propane lakes (flammable) | 0 | 0 | 0 | 0 / 0 | defined, on no tile | No (python tooling only) |
| LandmarkDef | `AB_QuicksandPits` | Alpha Biomes `sarg.alphabiomes` | Landmark: quicksand pools that slow movement | 1 | 1 | 1 | 0 / 0 | in canon; removed in df-10-18 | No (python tooling only) |
| LandmarkDef | `AB_TarLakes` | Alpha Biomes `sarg.alphabiomes` | Landmark: impassable tar pools (the landmark that rolls AB_TarLakes) | 7 | 7 | 7 | 0 / 0 | in canon; removed in df-10-18 | No (python tooling only) |
| BiomeDef (tile biome grid) | all 30 retired-donor BiomeDefs (AB 12, GrimTerra 15, Horrors 1, Alpha Genes 2) | see Table 3 | biome of tile | **0 tiles in the CSV** (CSV biome column is all `RUT_*`/`ZBiome_Grasslands`) | **0 tiles** (MEASURED: 21,872 tiles; 19,925 `RUT_` + 44 `RM_` resolve, 1,903 unresolved = our renamed biomes) | 0 | 0 / 0 | none ever on the grid | Mentions only: ~19 XML files in src/ (7 RUT_ BiomeDefs, ~10 patches, TheSump, SWBestiary, WarLab) name AB_ biomes as comments or as xpath patch targets that match nothing once Alpha Biomes is gone; `RUT_Abyss` states it replaces donor `AB_RockyCrags` |
| world-gen biome keys (`worldGenerationData` in the save) | 11 AB_ BiomeDef keys (e.g. `AB_PropaneLakes`, `AB_TarPits`, `AB_FeraliskInfestedJungle`) | Alpha Biomes | commonality/score offsets, not tiles | n/a | 11 (census, MEASURED; 2 keys per biome: commonalities + score offsets) | not re-measured | not re-measured | unresolved keys the load will drop | No |
| settlement tile biome (record column) | `AB_FeraliskInfestedJungle` 5, `AB_RockyCrags` 4, `AB_MiasmicMangrove` 1, `AB_MycoticJungle` 1 (Alpha Biomes); `BMT_FungalForest` 1 (Biomes! Caverns, `biomesteam.biomescaverns`); `HorrorWastes` 1 (Horrors) | donors above | the old biome name stored beside 121 settlements | `world/ASHKARR_WORLDMAP_settlements.csv` (13 of 121 rows) | tile biome in the save is `RUT_*` for those tiles (not re-joined here, UNMEASURED) | - | - | stale text in a record | No |
| river type | `Creek` 170, `River` 62, `LargeRiver` 43, `HugeRiver` 51 tiles | **Core only** | river grid | links.csv: same 4 defs | MEASURED same 4 defs, 0 retired | = | = | no donor involvement | - |
| road type | `DirtPath` 321, `DirtRoad` 527, `StoneRoad` 287, `AncientAsphaltHighway` 107 tiles | **Core only** | road grid | links.csv same 4 defs (different counts: edges vs tiles) | MEASURED, 0 retired | = | = | no donor involvement | - |
| hilliness | 5 levels (1-5) | engine enum | hilliness grid | tiles.csv `hilliness` 1-5 (9360/6035/3698/2424/355) | MEASURED 21,872 bytes, no def | = | = | no donor involvement | - |
| named-region features (`tileFeature`) | world feature ids | none (names, not defs) | region labels | meta.json regions | not def-resolved | - | - | no donor involvement | - |
| things and pawns on the world | 91 `AB_Mech_Ruined*` buildings, ~400 unresolved `AB_`/`AA_` Thing names, pawn `AA_Eyeling669122` | Alpha Biomes / Alpha Animals | not tile data; map-level residue | n/a | census: 291 AB names / 1187 hits, 626 SWAC names / 4226 hits, 493 Alpha Animals names / 2442 hits | - | - | carried in canon, repair steps in `donor_save_residue_2026-10-19.md` (cited, not re-measured) | - |

CSV-vs-save landmark note: the CSV records `sw_Sarlacc` 1 and `sw_DeadSarlacc` 4; the save holds 8 and 7 (worldgen added the rest). `AB_TarLakes` CSV 7 / save 7, `AB_MagmaticQuagmire` 3 / 3, `AB_QuicksandPits` 1 / 1. `AB_PropaneLakes`, `AB_HealingSprings`, `AB_MutagenicSprings` landmarks: 0 in CSV and 0 in canon.

## Table 3. The rest of Alpha Biomes (the item `ALPHA_BIOMES_CENSUS_THE_REST_OF_IT`): category counts

Three counts for one mod; they differ because they are three different instruments, and the difference is not reconciled here. **capture** = DefDump 2026-08-29 (what the game loaded, 584 mods). **workshop XML** = every `<defName>` under `workshop/content/294100/1841354677/1.6/**/Defs` by element type via `save_donor_census.donor_defs` (MEASURED, includes defs the game skips). The earlier 2026-10-04 dump (since overwritten) showed 132 terrains, 90 mutators, 23 landmarks (UNMEASURED now).

| category | capture 2026-08-29 | workshop XML | note |
|---|---|---|---|
| terrains | 91 | 110 | |
| weather | 11 | 9 | |
| thoughts | 16 | 11 | |
| biomes | 12 | 12 | |
| tile mutators | 48 | 59 | |
| landmarks | 6 | 21 | |
| things (buildings, items, plants, animals) | 379 | 254 | |
| KCSG symbols | 49 | 40 | |
| KCSG structure layouts | 23 | 26 | |
| hediffs | 18 | 21 | |
| game conditions | 7 | 7 | |
| special spawns | 12 | 12 | |
| **all defs** | **743** | **830** | |

The item's "~130 other AB_ names" does not match one clean slice: terrains+weather+thoughts+biomes+mutators+landmarks = 91 terrains + 11 weather + 16 thoughts + 12 biomes + 48 mutators + 6 landmarks = 184 names (capture) or 222 (workshop XML). Full capture name lists are in the JSON next to this report's generator: `/home/mandrake/.seat-tmp/FOUNDRY/sp/ab_names_0829.json`.

### Alpha Biomes names by category (capture 2026-08-29)

- **WeatherDef (11):** `AB_AcidRainWeather`, `AB_ForsakenNight`, `AB_ForsakenNight_Alternate`, `AB_ForsakenRainyNight`, `AB_ForsakenRainyNight_Alternate`, `AB_ForsakenThunderstorm`, `AB_ForsakenThunderstorm_Alternate`, `AB_PetalStorms`, `AB_RedFog`, `AB_VolcanicAsh`, `AB_VolcanicAshRain`
- **BiomeDef (12):** `AB_FeraliskInfestedJungle`, `AB_GallatrossGraveyard`, `AB_GelatinousSuperorganism`, `AB_IdyllicMeadows`, `AB_MechanoidIntrusion`, `AB_MiasmicMangrove`, `AB_MycoticJungle`, `AB_OcularForest`, `AB_PropaneLakes`, `AB_PyroclasticConflagration`, `AB_RockyCrags`, `AB_TarPits`
- **LandmarkDef (6):** `AB_HealingSprings`, `AB_MagmaticQuagmire`, `AB_MutagenicSprings`, `AB_PropaneLakes`, `AB_QuicksandPits`, `AB_TarLakes`
- **ThoughtDef (16):** `AB_ForsakenNight`, `AB_ForsakenRain`, `AB_ForsakenThunderstorm`, `AB_GelatinousEchoes_Bad`, `AB_GelatinousEchoes_Good`, `AB_HealingSpringwaterThought`, `AB_MoldyEnvironment`, `AB_MutagenicOcularWater`, `AB_PetalStorms`, `AB_PsychotropicFungusHigh`, `AB_PsychotropicFungusWithdrawal`, `AB_Quicksand`, `AB_RawRimeNodulesHigh`, `AB_RedFogThought`, `AB_RedFogThoughtPositive`, `AB_VolcanicAshThought`
- **TerrainDef (91):** `AB_AlienWoodFloors_CrystalWood`, `AB_AlienWoodFloors_MushroomStalks`, `AB_AlienWoodFloors_RedWood`, `AB_ArtificialTar`, `AB_AsphaltBridge`, `AB_AsphaltFloor`, `AB_BlackPebbles`, `AB_BrokenPoolTiles`, `AB_CompactedSand`, `AB_CrackedMud`, `AB_Cragstone_Rough`, `AB_Cragstone_RoughHewn`, `AB_Cragstone_Smooth`, `AB_DarkGravel`, `AB_DarkMud`, `AB_DenseGrass`, `AB_DenseMud`, `AB_FertileGrassyFlowerySoil`, `AB_FertileGrassyFlowerySoil_Oversaturated`, `AB_FertileMarsh`, `AB_FertileMud`, `AB_FineForsakenSand`, `AB_FineSand`, `AB_FlagstoneCragstone`, `AB_FlagstoneMudstone`, `AB_FlagstoneObsidian`, `AB_FlagstoneRoseQuartz`, `AB_ForsakenRock`, `AB_ForsakenSand`, `AB_GrassyFlowerySoil`, `AB_GrassySand`, `AB_HardenedGrass`, `AB_HardenedGrassFertile`, `AB_LiquidLava`, `AB_LiquidSlime`, `AB_LushGrass`, `AB_Mudstone_Rough`, `AB_Mudstone_RoughHewn`, `AB_Mudstone_Smooth`, `AB_MutagenicOcularWaterFlood`, `AB_MycoticGrass`, `AB_MycoticSoil`, `AB_MycoticSoilRich`, `AB_Obsidian`, `AB_Obsidianstone_Rough`, `AB_Obsidianstone_RoughHewn`, `AB_Obsidianstone_Smooth`, `AB_PackedIce`, `AB_PackedSnow`, `AB_ParchedEarth`, `AB_PropaneLake`, `AB_Quicksand`, `AB_RichCrackedMud`, `AB_RichSlime`, `AB_Slime`, `AB_SlimeGrass`, `AB_SlimeStone_Rough`, `AB_SlimeStone_RoughHewn`, `AB_SlimeStone_Smooth`, `AB_SlimyMud`, `AB_SnowOverRocks`, `AB_SoilOnCrackedMetal`, `AB_SolidPropane`, `AB_SolidifiedLava`, `AB_Tar`, `AB_TarMud`, `AB_TileCragstone`, `AB_TileMudstone`, `AB_TileObsidian`, `AB_TileRoseQuartz`, `AB_VolcanicGravel`, `AB_WebbedMarshyTerrain`, `GU_AlienSand`, `GU_AlienSandFine`, `GU_AncientMetals_RoughHewn`, `GU_AncientMetals_Smooth`, `GU_MetalFloor1`, `GU_MetalFloor2`, `GU_MetalFloor3`, `GU_MossyRed`, `GU_Piping`, `GU_RedWaterDeep`, `GU_RedWaterMovingChestDeep`, `GU_RedWaterMovingShallow`, `GU_RedWaterOceanDeep`, `GU_RedWaterOceanShallow`, `GU_RedWaterShallow`, `GU_RichAlienSand`, `GU_RoseQuartz_Rough`, `GU_RoseQuartz_RoughHewn`, `GU_RoseQuartz_Smooth`

### Other retired donors: world-facing defs (capture 2026-08-29)

| source | BiomeDef | TileMutatorDef | LandmarkDef | on the canon tile grid? |
|---|---|---|---|---|
| GrimTerra `grimterra.biomesmod` | 15 (BiomeArcticOasis, BiomeAreeb, BiomeCypreJungle, BiomeGRimberlands, BiomeGRimerald, BiomeGRimethyst, BiomeGRimonade, BiomeGRimond, BiomeGRimphire, BiomeGRimworld, BiomeGrindland, BiomeGRuby, BiomeGRuquoise, BiomeMist, BiomeToxlands) | 0 | 0 | no (0 tiles, 0 mutators, 0 landmarks: MEASURED) |
| Horrors `mlie.horrors` | 1 (HorrorWastes) | 0 | 0 | no (0 tiles, 0 mutators, 0 landmarks: MEASURED) |
| Alpha Genes `sarg.alphagenes` | 2 (AG_PocketPlane, AG_NereidPocketPlane) | 0 | 0 | no (0 tiles, 0 mutators, 0 landmarks: MEASURED) |
| ReGrowth 2 `regrowth.botr.core` | 0 | 0 | 0 | no (0 tiles, 0 mutators, 0 landmarks: MEASURED) |
| Cockroach `lingluo.cockroach` | 0 | 0 | 0 | no (0 tiles, 0 mutators, 0 landmarks: MEASURED) |
| Isopoda `who.vfee.isopodageneline` | 0 | 0 | 0 | no (0 tiles, 0 mutators, 0 landmarks: MEASURED) |
| VFE Insectoids 2 `oskarpotocki.vfe.insectoid2` | 0 | 0 | 0 | no (0 tiles, 0 mutators, 0 landmarks: MEASURED) |
| Alpha Animals `sarg.alphaanimals` | 0 | 0 | 0 | no (0 tiles, 0 mutators, 0 landmarks: MEASURED) |
| Biomes! Core `biomesteam.biomescore` | 0 | 0 | 0 | no (0 tiles, 0 mutators, 0 landmarks: MEASURED) |

## Disagreements and cautions (not reconciled)

- CSV vs save mutator counts differ on every shared row (Table 1). Largest: `AB_FeraliskNest` CSV 28 vs save 70; `AB_GeothermalHotspots` 5 vs 8; `sw_SarlaccLair` 1 vs 8; `sw_DeadSarlaccCave` 4 vs 12. The CSV is a 2026-08-23 authoring record; the canon save (mtime 2026-10-09) carries worldgen plus later work.
- Thirteen AB_ mutators are in the save but not the CSV at all (`AB_AmbientRadiation` 104, `AB_DerelictClusters` 171, `AB_AncientFreezingVent` 61 ...). They were rolled by vanilla worldgen, not authored.
- The `phase0_save_mutators_restore_NOTE.md` says the sarg.alphabiomes mutators "were left in place" in the 10-15 copy (agrees: df-10-15 still holds all 21) and that `sw_DeadSarlaccCave` is 12 entries (agrees: 12 entries on 8 tiles; the JSON's "16 tiles" is the Lair (8) plus Cave (8) union).
- `donor_save_residue_2026-10-19.md` item 2 attributes the lost-biome hashes 59367 / 65189 / 58457 to AB_ biomes. Measured: those hashes resolve to no def in any capture; BENCH's ledger note (WORLDMAP_REPAIR_LOST_BIOMES_ROCKY_TEXTURES) and the CSV counts (RUT_ForsakenCrags 1135, RUT_PoisonForest 546, ZBiome_Grasslands 222) match them to our renamed biomes, and 58457 is exactly `StableStringHash(RM_FE_Pyrelands)`. That doc also lists `AB_PropaneLakes x2` as a landmark; the save holds no such landmark (it appears only as a world-gen biome key).
- `retired_mods.json` lists 22 mods; seven of them (Alpha Genes, VFE Insectoids 2, GrimTerra, Isopoda, ReGrowth 2, Horrors, Cockroach) are still in the 2026-10-19 live capture (542 mods) because the candidate donor-retired list is not yet the live ModsConfig. Biomes! Core, Caverns and Polluted Lands and `zylle.morevanillabiomes` are not in the retired list; Core/Caverns/Polluted are already absent from the live list, `zylle.morevanillabiomes` (the `ZBiome_` biomes) is still present and is not treated as retired here.
- Resolver limit: hashes were resolved against the 2026-08-29 and 2026-10-19 captures only. All 162 mutator hashes in canon resolved uniquely.

## What I could not find

- `measure` CLI: not on this seat's PATH; counts come from the instruments above instead.
- The 2026-10-04 dump behind the 90 / 132 / 23 figures: `defs.sqlite` was rebuilt today (04:54) from the donor-free capture, so those three numbers are not re-checkable.
- No RimSage MCP needed: donor def sources were read from the DefDump captures and the Steam workshop copies of `sarg.alphabiomes` and `mlie.starwarsanimalcollection`. ReGrowth, GrimTerra, Horrors, Cockroach, Isopoda, Insectoids 2, Alpha Genes contribute no world-grid data, so their folders were not walked for mutators.
