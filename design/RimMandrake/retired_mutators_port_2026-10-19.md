# Retired-donor world-tile mutators and landmarks: ported to our own defs, 2026-10-19

Owner, 2026-10-19, verbatim: *"Reproduce the mutators into our own code, then proceed with deprecation of the donors."*
Input list: the FOUNDRY census `Transient/retired_mutators_list_2026-10-19.md` (21 Alpha Biomes and 5 Star Wars Animal
Collection mutators in the canonical save, plus 5 landmarks).

**Machine-readable mapping:** `design/RimMandrake/retired_mutators_port_map.json` (read by
`src/RimMandrake/Utils/save_donor_rewrite.py --mutators-only` and by the one-time repaint, `BIOME_PAINT_ONCE_AT_THE_END_1`).
**Guard:** `src/RimMandrake/Utils/selftest_retired_mutator_ports.py` (every port exists; nothing of ours names a retired
mutator or landmark; hash simulation; planted-negative probe).

## Counts

| | count |
|---|---:|
| TileMutatorDefs created (RM_ 17, RSW_ 2) | 19 |
| LandmarkDefs created (RM_) | 3 |
| reused, already ported 2026-10-15 (`RSW_SarlaccLair`, `RSW_DeadSarlaccCave`, `RSW_Sarlacc`, `RSW_DeadSarlacc`) | 4 |
| partly reproduced (`RM_DerelictClusters`, `RSW_WildGalacticPlants`) | 2 of the 19 |
| **not reproduced** (`AB_DerelictArchonexus`, `AB_DerelictBioLab`, `AB_DerelictKemeticTemple`, `WildDantooinePlants`) | 4 |

Supporting defs created: 3 vent buildings, `RM_MagmaVent`, `RM_MagmaThermalGenerator`, `RM_MycoticCollector`, game
conditions `RM_AmbientRadiation` and `RM_MoldyEnvironment`, thought `RM_MoldyEnvironment`, 9 GenStepDefs. C#
(`src/RimMandrake/EnvironmentalHazards/Source/RM_WorldMutatorPorts.cs`, namespace `RimMandrake.EnvironmentalHazards`):
a vent worker, an infesting-animal worker, the radiation condition, the outdoors thought worker, a tile-locked
PlaceWorker and a magma-eruption comp, each behind its own Mod Settings toggle (EnvironmentalHazards, section
"World-tile features"). Written from each donor def's fields and description plus vanilla's own workers (read with
RimSage); no donor C# was read or copied.

## Mapping, old -> ours

"Tiles" = canonical save entries / tiles (`CANONICAL_ASHKARR_START_2026-09-12.rws`, MEASURED by grid decode).

| donor def | type | tiles | ours | mod | how | status |
|---|---|---:|---|---|---|---|
| `AB_AgariluxPrime_Mutator` | mutator | 10 | `RM_AgariluxPrimeSprout` | TheRot | one `RM_AgariluxPrime` (our earlier port) by GenStep_ScatterThings | new |
| `AB_AmbientRadiation` | mutator | 104 | `RM_AmbientRadiation` | EnvironmentalHazards | permanent condition; a random colonist gains a random non-archite gene ~every 15 days | new |
| `AB_AncientBloodRainVent` | mutator | 43 | `RM_AncientBloodRainVent` | EnvironmentalHazards | vanilla vent layout (5-9 vents) + vanilla `BloodRain` | new |
| `AB_AncientDeathPallVent` | mutator | 33 | none | - | **DROPPED by owner 2026-10-19: no zombies in Utinni; its 33 tiles are stripped, not renamed** | dropped |
| `AB_AncientFreezingVent` | mutator | 61 | `RM_AncientFreezingVent` | EnvironmentalHazards | vanilla vent layout + vanilla `DeepFreeze` | new |
| `AB_AncientGreyPallVent` | mutator | 42 | `RM_AncientGrayPallVent` | EnvironmentalHazards | vanilla vent layout + vanilla `GrayPall` | new |
| `AB_BumbledroneNests` | mutator | 26 | `RM_SwarmHiveNests` | EnvironmentalHazards | **stand-in**: 3-4 vanilla insect `Hive` (bumbledrones retired with no twin) | new |
| `AB_DerelictArchonexus` | mutator | 2 | none | - | needs derelict archotech buildings (donor art) and five prefabs | **not reproduced** |
| `AB_DerelictBioLab` | mutator | 5 | none | - | needs 13 lab layouts (Alpha Genes KCSG, retired) | **not reproduced** |
| `AB_DerelictClusters` | mutator | 171 | `RM_DerelictClusters` | RustCathedral | 4-6 clusters: a vanilla war-machine wreck ringed by mechanoid slag (steel); no plasteel/component salvage | partial |
| `AB_DerelictKemeticTemple` | mutator | 5 | none | - | needs a temple layout (donor KCSG) | **not reproduced** |
| `AB_EdibleAirborneMicrofungi` | mutator | 30 | `RM_EdibleAirborneMicrofungi` | TheRot | flag; `RM_MycoticCollector` (donor numbers: 75 raw fungus / 10 days) buildable only here | new |
| `AB_FeraliskNest` | mutator | 70 | `RM_OllathrixNest` | Webwork | feralisk merged into `RM_Ollathrix` (owner 2026-09-10 / 10-03); a wild group on a new map, more wander in | new |
| `AB_GeothermalHotspots` | mutator | 8 | `RM_GeothermalHotspots` | Pyrelands | flag; `RM_MagmaThermalGenerator` (donor numbers: 3960 W on a geyser) buildable only here | new |
| `AB_GiantFossils` | mutator | 7 | `RM_GiantFossils` | Stillsand | Stillsand's own giant skeletons and skull, ~5-10 per map | new |
| `AB_LocustPlagues` | mutator | 31 | `RM_LocustPlagues` | EnvironmentalHazards | vanilla Odyssey `Locust` (the donor used Alpha Animals' locusts) | new |
| `AB_MagmaVents` | mutator | 8 | `RM_MagmaVents` | Pyrelands | 6-12 `RM_MagmaVent`, 30 apart; eruptions are our comp | new |
| `AB_MagmaticQuagmire` | mutator | 6 | `RM_MagmaticQuagmire` | Pyrelands | vanilla patch worker: volcanic rock, cooled lava, deep lava | new |
| `AB_MoldyEnvironment` | mutator | 40 | `RM_MoldyEnvironment` | TheRot | permanent condition; -10 mood under open sky | new |
| `AB_QuicksandPits` | mutator | 1 | `RM_QuicksandPits` | EnvironmentalHazards | vanilla patch worker: FlowWorks' `RM_DeepSand` pools | new |
| `AB_TarLakes` | mutator | 10 | `RM_TarLakes` | TheSump | vanilla patch worker: FlowWorks' `RM_TarShallow` rim, `RM_TarDeep` (impassable, unbridgeable) | new |
| `sw_SarlaccLair` | mutator | 8 | `RSW_SarlaccLair` | SWBestiary | ported 2026-10-15 | reused |
| `sw_DeadSarlaccCave` | mutator | 12 | `RSW_DeadSarlaccCave` | SWBestiary | ported 2026-10-15 | reused |
| `WildTattooinePlants` | mutator | 1403 | `RSW_WildTattooinePlants` | SWBestiary | vanilla WildPlants worker, `RSW_Plant_HubbaGourd_Wild` | new |
| `WildGalacticPlants` | mutator | 2 | `RSW_WildGalacticPlants` | SWBestiary | 3 of the donor's 5 kinds (chak-root, jogan, nysyllin; no meiloorun or muja fruit port) | partial |
| `WildDantooinePlants` | mutator | 4 | none | - | no RSW_ dantuber plant exists | **not reproduced** |
| `AB_TarLakes` | landmark | 7 | `RM_TarLakes` | TheSump | requires `RM_TarLakes`; the donor's second requirement `AB_TarHoles` (on no tile) is not ported | new |
| `AB_MagmaticQuagmire` | landmark | 3 | `RM_MagmaticQuagmire` | Pyrelands | requires quagmire + magma vents + geothermal hotspots | new |
| `AB_QuicksandPits` | landmark | 1 | `RM_QuicksandPits` | EnvironmentalHazards | requires `RM_QuicksandPits` | new |
| `sw_Sarlacc` | landmark | 8 | `RSW_Sarlacc` | SWBestiary | ported 2026-10-15 | reused |
| `sw_DeadSarlacc` | landmark | 7 | `RSW_DeadSarlacc` | SWBestiary | ported 2026-10-15 | reused |

Rules applied to every port: the donor's label, description, categories, `chanceOnNonLandmarkTile`, hilliness, coast and
river limits are kept; a donor biome in a white/blacklist is replaced by our twin (`AB_PyroclasticConflagration` ->
`RM_Pyrelands` + `RM_FloodedCanyon`, which the canon tiles actually read; `AB_MycoticJungle` -> `RM_TheRot`;
`AB_MechanoidIntrusion` -> `RM_RustCathedral`; `AB_TarPits` -> `RM_TheSump`; `AB_FeraliskInfestedJungle` -> `RM_Webwork`;
`AB_GallatrossGraveyard` dropped). The Ash'karr RUT_ biomes the canon tiles sit on are added to the whitelists from the
Utinni layer (`src/RimUtinni/UtinniPatches/Patches/RUT_RetiredMutatorPorts_Biomes.xml`), so the tier rule holds: RM_
defs name no RUT_ def. The three RM_ landmarks take the Ash'karr icons already painted for the donor ones
(`src/RimUtinni/AshkarrLandmarkArt/Patches/LandmarkIcons.xml`). **PLACEHOLDER ART:** every new building uses a vanilla
texture (vents: ancient smoke vent; magma vent: geothermal vent, tinted; generator: geothermal plant, tinted; collector:
refinery, tinted). New art is the owner's call.

## Owner's frozen 2026-08-16 world-map calls disagree on two rows

`design/Jawa/worldbuilding/review/worldmap_elements.prefill.json` (frozen by the owner) **rejects**
`AB_AncientDeathPallVent` and `AB_AncientFreezingVent`; the canonical save carries them on 33 and 61 tiles. Owner,
2026-10-19: "No death pall, freezing vents are ok. We don't have zombies in Utinni." So the freezing vent is ported and
the death pall vent is DROPPED (its 33 tiles are stripped from the save copy). The gray pall vent (`GrayPall`, darkness)
is a different thing and stays. Every other row is in that file's whitelist.

## Save side

**Tool:** `python3 src/RimMandrake/Utils/save_donor_rewrite.py <in.rws> <out.rws> --mutators-only --table <t.md>`.
It rewrites only `<tileMutatorDefsDeflate>` (each mapped donor shortHash -> the port's) and the `<def>` texts inside
`<landmarks>`; the tile array, entry order and every other byte are untouched; refuses to write in place or over a file.

**shortHash caveat:** a mutator is saved as a 2-byte shortHash, which the game assigns at load by sorting every
TileMutatorDef by defName and bumping collisions (`Verse.ShortHashGiver`). The tool predicts the ports' hashes by
simulating that over the donor-free capture `2026-10-19T11-55-43Z` plus the ports, and refuses unless the simulation
reproduces every live hash of that capture (it did: 353/353). If the deployed mod set changes which TileMutatorDefs
exist, rerun it against a fresh capture before swapping a save.

**Verified copy, superseded by the `_NODEATHPALL` copy below (2026-10-19, canonical save, offline; the canonical save and every file under Saves untouched):**
`D:\Luke\dev\_rmscratch\ported_mutator_saves\CANONICAL_ASHKARR_START_2026-09-12_PORTED_MUTATORS.rws`
(sha256 `3c20801f7ff812d3bd1dbe95bfeb4c714b6857bfa92fd43758ddf5bfdbfd4610`; input sha256 starts `1ff329161abeaa8c`), with
`verify.txt` and `port_table.md` beside it. Independent check (own decoder and own hash simulation):

- all 8 other world grids byte-identical (biome x3, elevation, hilliness, river, road, mutator tiles, feature, pollution);
- 27,856 mutator entries before and after; 2,126 renamed; each port carries exactly its donor's tile set;
- 16 entries on the 4 unported mutators left in place (the load drops them);
- landmarks: 3,008 entries, 26 renamed, order kept;
- every other byte identical; the output parses as XML.

**Current copy (2026-10-19, owner dropped the death pall):**
`D:\Luke\dev\_rmscratch\ported_mutator_saves\CANONICAL_ASHKARR_START_2026-09-12_PORTED_MUTATORS_NODEATHPALL.rws`
(md5 `a6366d9b1f592441832d329b68a6c5e2`, sha256 `ad15abc8f0885bf2a478c24065a9485b11e18260fb02e93861a432a95bd81e82`;
table `port_table_NODEATHPALL.md` beside it). Same tool; the map row carries `"drop": true`, which removes the entry
from BOTH parallel arrays (`tileMutatorTilesDeflate`, `tileMutatorDefsDeflate`). Checked with an own decoder: 27,856 ->
27,823 entries (exactly the 33 `AB_AncientDeathPallVent` entries gone, the 30 other mutators on those tiles kept), all
else byte-identical to the `_PORTED_MUTATORS` copy, XML parses.

This copy is the **canonical** save renamed, so it still carries the residue `donor_save_residue_2026-10-19.md` lists
(lost-biome hashes, donor things and pawns). The BENCH-repaired donor-free save
(`CANONICAL_ASHKARR_START_2026-10-18_DONORFREE_REPAIRED.rws`) has these mutators stripped, so renaming it changes
nothing; putting them back there means inserting entries, which this tool does not do. Swapping either save is BENCH's
`WORLDMAP_REPAIR_LOST_BIOMES_ROCKY_TEXTURES` / the owner's call.

## Owed

- **Deploy** at a game-down window: `deploy_custom_mods.py --compose biomes` (EnvironmentalHazards DLL + all biome
  defs), `--mod UtinniPatches`, `--mod SWBestiary`, `--mod AshkarrLandmarkArt`. Nothing was deployed.
- **Live check after a restart:** the ports load with no config error, a fresh capture lists all 21 new defs, and their
  shortHashes match the predicted ones in `port_table.md`; then load the renamed copy and read a few tiles' mutators
  (e.g. tile of `RM_TarLakes`) through the bridge.
- **Not reproduced:** the 4 rows above, for the owner at the repaint (new structures or art, or cut).
- Placeholder art on 6 new buildings.
