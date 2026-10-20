# World layers rescue: canonical save -> w9 stamp files

Written by `src/RimMandrake/Utils/world_layers_export.py` (item `WORLD_LAYERS_RESCUE_THE_SAVE_HAS_MORE`).
OFFLINE: the save was only read. Every number below is the tool's own count on this run.

## Provenance

- save: `/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves/CANONICAL_ASHKARR_START_2026-09-12.rws` (sha256/16 `1ff329161abeaa8c`, 616 modIds in its header)
- decode captures, ranked by share of the save's modIds loaded:
  - `2026-10-19T15-02-31Z` 536 mods, share 0.856
  - `2026-10-19T13-18-11Z` 536 mods, share 0.856
  - `2026-08-29T13-30-02Z` 584 mods, share 0.810
  - `2026-10-19T22-45-42Z` 498 mods, share 0.792
- profile checked: `/home/mandrake/rm/foundry/deployed/config/ModsConfig.CANDIDATE_2026-10-19.xml` (367 active mods)
- `raw/` = names as the save holds them; `ported/` = the historical renames in the tool (`HISTORICAL_RENAMES`, each cited), then `naming_rename_map.csv` def rows whose new name exists, then `retired_mutators_port_map.json` (a separate, reported step)
- shortHash decode: every capture, plus a collision check (Verse.ShortHashGiver raw hash, +16 bump window); an ambiguous hash is settled by the record CSV only when it names exactly one hash-consistent candidate (see Decode notes)

## Counts (save)

| layer | count |
|---|---|
| tiles | 21872 |
| river_entries | 326 |
| road_entries | 1242 |
| mutator_entries | 27856 |
| mutator_tiles | 14421 |
| landmarks | 3008 |
| settlements_npc | 95 |
| settlements_player | 1 |
| factions | 26 |
| features | 71 |
| landforms | 64 |

## Identity diff vs committed `world/ASHKARR_WORLDMAP_*.csv` (raw names)

### tiles
```
{"new": 153104, "record": 153104, "adds": 222, "losses": 222, "tiles_changed_by_column": {"biome": 222}, "biome_transitions_top": [["ZBiome_Grasslands", "RM_FE_Pyrelands", 222]]}
```
### links
```
{"new": 1568, "record": 1713, "adds": 65, "losses": 210, "add_sample": [["road", 61, 7649, "AncientAsphaltHighway"], ["road", 61, 7651, "AncientAsphaltHighway"], ["road", 301, 9087, "AncientAsphaltHighway"], ["road", 938, 12910, "AncientAsphaltHighway"], ["road", 939, 12914, "AncientAsphaltHighway"], ["road", 939, 12918, "AncientAsphaltHighway"], ["road", 1528, 16448, "AncientAsphaltHighway"], ["road", 1560, 16641, "DirtPath"]], "loss_sample": [["road", 57, 7623, "AncientAsphaltHighway"], ["road", 57, 7624, "AncientAsphaltHighway"], ["road", 161, 8247, "AncientAsphaltHighway"], ["road", 161, 8250, "AncientAsphaltHighway"], ["road", 399, 9675, "AncientAsphaltHighway"], ["road", 399, 9678, "AncientAsphaltHighway"], ["road", 497, 10265, "AncientAsphaltHighway"], ["road", 497, 10267, "AncientAsphaltHighway"]], "river": {"edges_save": 326, "edges_record": 326, "shared_topology": 326, "added_edges": 0, "lost_edges": 0, "def_changed_on_shared": 0}, "road": {"edges_save": 1242, "edges_record": 1387, "shared_topology": 1177, "added_edges": 65, "lost_edges": 210, "def_changed_on_shared": 0}}
```
### mutators
```
{"new": 27856, "record": 10084, "adds": 18384, "losses": 612, "add_sample": [[1, "VEE_Mycelium"], [1, "AB_MoldyEnvironment"], [3, "Cavern"], [3, "MixedBiome"], [4, "VEE_LessSolarPower"], [5, "VEE_LessSolarPower"], [6, "sw_SarlaccLair"], [6, "VEE_MoreSolarPower"]], "loss_sample": [[3, "Mountain"], [53, "Caves"], [107, "Mountain"], [126, "Mountain"], [151, "Mountain"], [171, "Coast"], [239, "CoastalIsland"], [291, "VEE_SaltPlains"]], "tiles_save": 14421, "tiles_record": 6710}
```
### landmarks
```
{"new": 3008, "record": 563, "adds": 2462, "losses": 17, "add_sample": [[3, "Cavern"], [6, "sw_Sarlacc"], [7, "sw_Sarlacc"], [8, "AncientToxVent"], [15, "Ruins"], [16, "VEE_GravelBeach"], [22, "VEE_SerpentineCanyons"], [24, "VEE_MeteorCrater"]], "loss_sample": [[2920, "sw_Sarlacc"], [2358, "VEE_Cenotes"], [2949, "Peninsula"], [11830, "Peninsula"], [12508, "Peninsula"], [8181, "Peninsula"], [11851, "Peninsula"], [788, "Peninsula"]], "retyped_same_tile": 8, "tiles_only_in_save": 2454, "tiles_only_in_record": 9}
```
### settlements
```
{"new": 95, "record": 121, "adds": 87, "losses": 113, "add_sample": [[4366, "Empire", "Oxalate Watch"], [135, "Empire", "Ashgarrison"], [7722, "RUT_Jawa_GeonosianFoundryHive", "The Unfinished Work"], [20366, "RUT_Jawa_GeonosianFoundryHive", "Oxide Deep"], [21576, "RUT_Jawa_GeonosianFoundryHive", "The Godmouth"], [675, "RUT_Jawa_GeonosianFoundryHive", "Founder's Kiln"], [8497, "RUT_Jawa_GeonosianFoundryHive", "Hollow Hive"], [19350, "RUT_Jawa_FreeDroidEnclaves", "No Master"]], "loss_sample": [[3289, "Empire", "Oxalate Watch"], [6617, "Empire", "Ashgarrison"], [14719, "Jawa_GeonosianFoundryHive", "The Unfinished Work"], [20427, "Jawa_GeonosianFoundryHive", "Oxide Deep"], [11335, "Jawa_GeonosianFoundryHive", "The Godmouth"], [14574, "Jawa_GeonosianFoundryHive", "Founder's Kiln"], [19422, "Jawa_GeonosianFoundryHive", "Hollow Nave"], [248, "Jawa_FreeDroidEnclaves", "The Trade Socket"]], "moved_same_name_faction": 27, "moved_sample": [["Rainshadow", "OutlanderCivil", 9962, 2607], ["The Blind Wells", "TribeCivil", 3156, 21638], ["Greenline", "OutlanderCivil", 15051, 18359], ["Sweetwell", "OutlanderCivil", 5538, 19945], ["Redscarp", "TribeCivil", 6, 6570], ["Ashgarrison", "Empire", 6617, 135], ["Cold Catch", "OutlanderCivil", 4848, 12953], ["Pumphouse", "OutlanderCivil", 3436, 18166]], "names_only_in_save": 60, "names_only_in_record": 86}
```
### factions
```
{"record": "none", "new": 26}
```
### features
```
{"record": "none", "new": 71}
```
### landforms
```
{"record": "none", "new": 64}
```

## Round trip (written files re-read vs decode, identity multisets)

- raw: {'tiles': True, 'links': True, 'mutators': True, 'landmarks': True, 'settlements': True, 'factions': True, 'features': True, 'landforms': True}
- ported: {'tiles': True, 'links': True, 'mutators': True, 'landmarks': True, 'settlements': True, 'factions': True, 'features': True, 'landforms': True}

## Decode notes

- hashes no capture names: `{"BiomeDef": {"65189": 1, "58457": 1, "59367": 1}}`
- settled (decode differs from the best capture, or no capture names the hash) - 4:
  - BiomeDef 65189: capture `?65189` -> **`RUT_PoisonForest`** (record names exactly one hash-consistent candidate; candidates ['RUT_PoisonForest'])
  - BiomeDef 56104: capture `RM_FloodedCanyon` -> **`RUT_TheForge`** (record names exactly one hash-consistent candidate; candidates ['RM_FloodedCanyon', 'RUT_TheForge'])
  - BiomeDef 58457: capture `?58457` -> **`RM_FE_Pyrelands`** (UNRESOLVED in every capture; the one name whose raw hash is exactly h (historical rename list); record evidence, if any, is not hash-consistent; candidates ['RM_FE_Pyrelands'])
  - BiomeDef 59367: capture `?59367` -> **`RUT_ForsakenCrags`** (record names exactly one hash-consistent candidate; candidates ['RUT_ForsakenCrags'])
- ambiguous, NOT settled (best capture's name used) - 7:
  - TileMutatorDef 30233: used `AB_AncientBloodRainVent`; candidates ['AB_AncientBloodRainVent', 'RSW_TradingPost']; record evidence {}
  - TileMutatorDef 31264: used `VEE_ResurgentCaldera`; candidates ['VEE_MangroveTrees', 'VEE_ResurgentCaldera', 'VEE_StagnantRivulet']; record evidence {}
  - TileMutatorDef 14373: used `VEE_DustBowl`; candidates ['VEE_DustBowl', 'VEE_DustStorms']; record evidence {'VEE_DustStorms': 16, 'VEE_DustBowl': 16}
  - TileMutatorDef 55858: used `AncientHeatVent`; candidates ['AncientHeatVent', 'RM_OllathrixNest']; record evidence {}
  - TileMutatorDef 41611: used `VEE_QuicksandPits`; candidates ['GravTide_CollisionZone', 'VEE_QuicksandPits']; record evidence {}
  - TileMutatorDef 28344: used `AncientRuins`; candidates ['AncientRuins', 'Cliffs']; record evidence {'AncientRuins': 60, 'Cliffs': 2}
  - TileMutatorDef 6415: used `AncientSmokeVent`; candidates ['AncientSmokeVent', 'GravTide_TropicalWaters']; record evidence {}
- rename-map rows skipped (new name defined nowhere): 129
- hash conflicts between captures (0):
- player settlements (excluded from the settlements file): `[[277, "Zeddo's Salvage Yard", 17007]]`

## Port step (applied to `ported/`)

| layer | step | old | new | entries |
|---|---|---|---|---|
| landmarks | port_map | `AB_MagmaticQuagmire` | `RM_MagmaticQuagmire` | 3 |
| landmarks | port_map | `AB_QuicksandPits` | `RM_QuicksandPits` | 1 |
| landmarks | port_map | `AB_TarLakes` | `RM_TarLakes` | 7 |
| landmarks | port_map | `sw_DeadSarlacc` | `RSW_DeadSarlacc` | 7 |
| landmarks | port_map | `sw_Sarlacc` | `RSW_Sarlacc` | 8 |
| mutators | port_map | `AB_AgariluxPrime_Mutator` | `RM_AgariluxPrimeSprout` | 10 |
| mutators | port_map | `AB_AmbientRadiation` | `RM_AmbientRadiation` | 104 |
| mutators | port_map | `AB_AncientBloodRainVent` | `RM_AncientBloodRainVent` | 43 |
| mutators | port_map | `AB_AncientFreezingVent` | `RM_AncientFreezingVent` | 61 |
| mutators | port_map | `AB_AncientGreyPallVent` | `RM_AncientGrayPallVent` | 42 |
| mutators | port_map | `AB_BumbledroneNests` | `RM_SwarmHiveNests` | 26 |
| mutators | port_map | `AB_DerelictClusters` | `RM_DerelictClusters` | 171 |
| mutators | port_map | `AB_EdibleAirborneMicrofungi` | `RM_EdibleAirborneMicrofungi` | 30 |
| mutators | port_map | `AB_FeraliskNest` | `RM_OllathrixNest` | 70 |
| mutators | port_map | `AB_GeothermalHotspots` | `RM_GeothermalHotspots` | 8 |
| mutators | port_map | `AB_GiantFossils` | `RM_GiantFossils` | 7 |
| mutators | port_map | `AB_LocustPlagues` | `RM_LocustPlagues` | 31 |
| mutators | port_map | `AB_MagmaVents` | `RM_MagmaVents` | 8 |
| mutators | port_map | `AB_MagmaticQuagmire` | `RM_MagmaticQuagmire` | 6 |
| mutators | port_map | `AB_MoldyEnvironment` | `RM_MoldyEnvironment` | 40 |
| mutators | port_map | `AB_QuicksandPits` | `RM_QuicksandPits` | 1 |
| mutators | port_map | `AB_TarLakes` | `RM_TarLakes` | 10 |
| mutators | port_map | `WildGalacticPlants` | `RSW_WildGalacticPlants` | 2 |
| mutators | port_map | `WildTattooinePlants` | `RSW_WildTattooinePlants` | 1403 |
| mutators | port_map | `sw_DeadSarlaccCave` | `RSW_DeadSarlaccCave` | 12 |
| mutators | port_map | `sw_SarlaccLair` | `RSW_SarlaccLair` | 8 |
| mutators | port_map_NOT_PORTED | `AB_AncientDeathPallVent` | `` | 33 |
| mutators | port_map_NOT_PORTED | `AB_DerelictArchonexus` | `` | 2 |
| mutators | port_map_NOT_PORTED | `AB_DerelictBioLab` | `` | 5 |
| mutators | port_map_NOT_PORTED | `AB_DerelictKemeticTemple` | `` | 5 |
| mutators | port_map_NOT_PORTED | `WildDantooinePlants` | `` | 4 |
| settlements | historical_rename | `RUT_ForsakenCrags` | `RUT_Abyss` | 1 |
| settlements | historical_rename | `RUT_PoisonForest` | `RUT_Cauldron` | 1 |
| tiles | historical_rename | `RM_FE_Pyrelands` | `RM_Pyrelands` | 222 |
| tiles | historical_rename | `RUT_ForsakenCrags` | `RUT_Abyss` | 1135 |
| tiles | historical_rename | `RUT_PoisonForest` | `RUT_Cauldron` | 546 |

## Names in `ported/` NOT resolvable on the profile (5 names, 49 entries)

Listed, not dropped. Status: MOD_NOT_ON_PROFILE (defining packageId known, not active), NO_SOURCE (no capture or src/ defines it), UNRESOLVED_HASH.

| type | defName | entries | packageId | status |
|---|---|---|---|---|
| TileMutatorDef | `AB_AncientDeathPallVent` | 33 | `sarg.alphabiomes` | MOD_NOT_ON_PROFILE |
| TileMutatorDef | `AB_DerelictKemeticTemple` | 5 | `sarg.alphabiomes` | MOD_NOT_ON_PROFILE |
| TileMutatorDef | `AB_DerelictBioLab` | 5 | `sarg.alphabiomes` | MOD_NOT_ON_PROFILE |
| TileMutatorDef | `WildDantooinePlants` | 4 | `mlie.starwarsanimalcollection` | MOD_NOT_ON_PROFILE |
| TileMutatorDef | `AB_DerelictArchonexus` | 2 | `sarg.alphabiomes` | MOD_NOT_ON_PROFILE |

284 names resolve on the profile (54542 entries).
