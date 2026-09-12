# WORLDMAP_FINAL_REVIEW_1 — Landmarks & Settlements Audit

Offline, read-only. Instruments: `Transient/worldreview/landmarks.json` (3414 rows, live
dump), `Transient/worldreview/settlements.json` (196 world objects), `Transient/worldreview/world_info.json`
(21 factions), `Transient/worldreview/features.json` (71 features), `world/ASHKARR_WORLDMAP_tiles.csv`
(21872 rows, read via `csv.DictReader` — the whole file, not a grep/`wc` scan),
`infrastructure/state/canon.yml`. All counts below are MEASURED from these files; no
number is copied from a doc without re-deriving it here.

---

## 1. Settlements

**Live dump**: `settlements.json.count` = 196 world objects; `settlements` (def=Settlement) = 96.
`byDef`: Settlement 96, plus 15 asteroid/derelict/infestation world-object types (100
non-settlement objects: 80 `objectsWithNoFaction` — asteroids — and 20 `Insect`
infestations).

**Faction roster reconciliation** (`world_info.json` reports `factionCount: 21`):

- `canon.yml` `factions.on_map` (12 names) ∪ `factions.no_settlements: [Mechanoid]` = **13**,
  matching canon's stated "campaign roster … 13, arrived at independently of the map."
- The other **8** of the live 21 are non-campaign/system factions: `Insect`, `Entities`,
  `Ancients`, `AncientsHostile`, `HoraxCult`, `AM_EnemyPirate`, `TribalHostile`,
  `DP_GenericHostile`. 21 − 13 = 8. ✅ Reconciles exactly.
- ⚠️ **Note, not re-filed**: `AM_EnemyPirate` still appears as a live faction slot in
  `WorldGrid.factions` even though `canon.yml` (PIRATE_DEFNAME_DRIFT_1) records it as a
  dead/superseded defName replaced by `Pirate`. It holds 0 settlements and 0 objects in
  `byFaction` — a harmless ghost slot, not a settlement-count issue.

**Live settlement count per faction** (96 total, `isSettlement:true` objects only,
`RUT_Jawa_` prefix stripped for comparison with canon's plain names):

| Faction | Live (measured) | canon.yml `by_faction` |
|---|---:|---:|
| OutlanderCivil | 27 | 13 |
| Jawa_HuttCartel | 12 | 8 |
| Jawa_WildsteamClan | 9 | 4 |
| TribeCivil | 9 | 9 |
| Jawa_FreeDroidEnclaves | 7 | 3 |
| Jawa_AscendantHelix | 7 | 3 |
| Jawa_DeepwaterCompact | 6 | 5 |
| Jawa_GeonosianFoundryHive | 5 | 5 |
| Pirate | 4 | 4 |
| Jawa_Junkers | 4 | 8 |
| Empire | 3 | 3 |
| Jawa_IndigenousTribes | 2 | 7 |
| PlayerColony | 1 | — (not a roster faction) |
| **Total** | **96** | **72** |

**Findings:**

- ✅ The SET of factions holding settlements matches canon's `on_map` list exactly (same
  12 names, no extras, no omissions).
- 🔴 **canon.yml internal inconsistency**: `settlements.total: 120` ("RE-MEASURED
  2026-08-23") but `settlements.by_faction` sums to 72 (the value that same block says
  was superseded by the 120 re-measurement). The sub-table was never updated when the
  total was. Neither figure matches the live count.
- 🔴 **canon.yml `settlements.total` (120) does not match tonight's live dump (96)**.
  Live is 24 settlements short of canon's claimed current total. Per-faction, the
  live distribution is also structurally different from canon's stale table (e.g.
  OutlanderCivil 27 live vs 13 canon; Jawa_IndigenousTribes 2 live vs 7 canon). This
  reads as canon.yml's settlements section being stale against the current frozen
  world, not as a live-dump defect — flagging for whoever owns canon.yml next, not
  re-deriving which number is "right."
- 🟡 **1 settlement on an ice biome**: id 249 "Cold Archive" (`RUT_Jawa_AscendantHelix`),
  tile 17901, biome `RUT_NightsideIce`. All other 95 settlements sit on non-ice,
  non-sea biomes.
- ✅ Bounds/water sanity: all 96 settlement tiles fall inside the valid CSV range
  (min tile 135, max 21765, of 0–21871); none sit on a `water=1` CSV tile; none have
  a null/missing faction (the `factionWarning` about a null-faction Settlement being
  destroyed on load does not apply to any of the 96 — it's a generic caveat, not a
  live hit here).

**Verdict**: settlement faction ROSTER matches canon exactly (12 factions + Mechanoid
= 13-faction campaign roster, 21 world factions total, reconciled); settlement
COUNT and per-faction DISTRIBUTION do not match canon.yml's stale `settlements:`
block (96 live vs 120 claimed); 1 settlement flagged on ice biome.

---

## 2. Landmarks

3414 total landmark placements across **65** distinct LandmarkDefs.

### Per-def counts (descending)

| Count | Def | Count | Def | Count | Def |
|---:|---|---:|---|---:|---|
| 582 | Cavern | 34 | AncientHeatVent | 5 | VEE_AlluvialFan |
| 362 | VEE_Cenotes | 29 | VEE_SerpentineCanyons | 5 | VEE_CactusFields |
| 351 | Valley | 25 | VEE_MeteorCrater | 4 | VEE_StoneForest |
| 159 | Cliffs | 24 | CoastalIsland | 4 | VEE_QuicksandPits |
| 150 | Ruins | 22 | VEE_SaltPlains | 3 | AB_MagmaticQuagmire |
| 142 | Crevasse | 20 | AncientWarehouse | 3 | VEE_RelictDelta |
| 140 | VEE_GravelBeach | 19 | VEE_PebbleDunes | 3 | AncientInfestedSettlement |
| 126 | DryLake | 18 | VEE_StagnantRivulet | 2 | VEE_RedDesert |
| 120 | VEE_DryRiver | 18 | VEE_DustBowl | 2 | Plateau |
| 111 | VEE_JaggedRocks | 17 | Archipelago | 2 | HotSprings |
| 108 | IceDunes | 14 | VEE_QuicksandDunes | 2 | AncientLaunchSite |
| 107 | Chasm | 14 | AncientChemfuelRefinery | 2 | VEE_ContaminatedReservoir |
| 107 | AncientSmokeVent | 13 | Bay | 2 | AncientToxVent |
| 106 | Harbor | 13 | Hollow | 1 | VEE_ToxicCrater |
| 97 | TerraformingScar | 12 | VEE_RockRidge | 1 | AbandonedColonyOutlander |
| 77 | RUT_ComplexStructures | 12 | ToxicLake | 1 | LavaCrater |
| 76 | Oasis | 10 | VEE_SulfuricLake | 1 | LavaLake |
| 42 | AncientGarrison | 9 | AbandonedColonyTribal | 1 | Basin |
| 36 | Dunes | 9 | FrozenRuins | 1 | AB_QuicksandPits |
|  |  | 9 | VEE_FleshPits | 1 | VEE_ResurgentCaldera |
|  |  | 7 | AB_TarLakes | 1 | VEE_CraterLake |
|  |  | 7 | sw_DeadSarlacc | 1 | RUT_GapingDoom |
|  |  | 6 | AncientQuarry |  |  |
|  |  | 6 | sw_Sarlacc |  |  |

Sum: 3414 (65 defs). ✅ Total agrees with `landmarks.json.count`.

### Named specials

- 🔴 **sw_Sarlacc = 6, not 1.** All 6 instances, with tiles:
  - tile **2920** "Biamb Sarlacci Burrow" — **this is the same tile named in the
    already-filed SARLACC_WORLDMAP_RELOCATE_1.** As of this dump, the sw_Sarlacc at
    2920 has **not moved** — the relocation has not landed yet. Not re-filing per
    instructions, just reporting current location.
  - 5 further, unexpected instances: tile 6 "Wahenseum Creature", tile 7 "Ouleria
    Sarlacc", tile 44 "Caisen Creature", tile 64 "White Chough Sarlacci Burrow",
    tile 65 "Pit of Red".
- 🔴 **sw_DeadSarlacc = 7, not 4.** Tiles: 1837, 2462, 2463, 2468, 15623, 15905, 20456.
  (2462/2463/2468 are a tight adjacent cluster — worth a look at whether that's one
  intended placement duplicated three times.)
- ✅ **RUT_GapingDoom = 1**, at tile 2403 "The Gaping Doom" — present as expected.

### Art-patch coverage (`src/RimUtinni/AshkarrLandmarkArt/Patches/LandmarkIcons.xml`)

- 48 distinct LandmarkDefs are targeted by the icon patch.
- ✅ **0 of the 48 patched defs have zero placed instances** — every def the art patch
  expects to paint is actually placed at least once on the live world. Clean.
- Informational (not requested, noted in passing): 17 placed LandmarkDefs are NOT
  targeted by this patch at all — `AncientSmokeVent`(107), `Harbor`(106), `Crevasse`(142),
  `IceDunes`(108), `RUT_ComplexStructures`(77), `CoastalIsland`(24), `Archipelago`(17),
  `Bay`(13), `AncientInfestedSettlement`(3), `AncientToxVent`(2), `VEE_CactusFields`(5),
  `VEE_ContaminatedReservoir`(2), `VEE_CraterLake`(1), `VEE_QuicksandPits`(4),
  `VEE_RelictDelta`(1), `VEE_ResurgentCaldera`(1), `RUT_GapingDoom`(1). May be using
  vanilla/mod-default icons deliberately — not asserting a defect, just visibility.

**Landmark findings count: 3** (sw_Sarlacc count/location, sw_DeadSarlacc count, the
ice-biome settlement counts as a settlements finding, not here — landmark-specific
findings are the two Sarlacc discrepancies plus the informational patch-coverage note
is NOT counted as a finding since it measured clean). Counting only genuine
discrepancies against a stated expectation: **2** (sw_Sarlacc, sw_DeadSarlacc).

---

## 3. Density sanity

- 65 LandmarkDefs are spread across **28 of the 29** biomes on the map. The one biome
  with **zero** landmarks: `COMIGO_GreaterSwamp_Tropical` (43 tiles).
- **Top 5 biomes by landmark count**: AB_MycoticJungle 912, AB_RockyCrags 452,
  ZBiome_Badlands 333, RUT_TwilightSea 333, RUT_GreySea 280.
- **Bottom 5 biomes by landmark count** (excluding the zero above): AB_TarPits 4,
  LavaField 2, Volcano 1, RUT_PropaneLake 1, RUT_TheScald 1.
- ✅ **Tiles carrying >1 landmark: 0.** Every one of the 3414 landmarks sits on a
  unique tile.
- 🟡 **Landmarks on `water=1` tiles: 615** (18% of all 3414). All 615 sit inside
  exactly **4** biomes whose entire footprint is a water body — i.e. every landmark
  reported as "on water" is on water because its biome IS a sea/lake, not because a
  landmark leaked onto water inside an ordinary dry biome:

  | Biome | Landmarks on water | Water tiles in that biome |
  |---|---:|---:|
  | RUT_TwilightSea | 333 | 607 |
  | RUT_GreySea | 280 | 472 |
  | RUT_PropaneLake | 1 | 57 |
  | RUT_TheScald | 1 | 312 |

  By def, on water: Crevasse 142, VEE_GravelBeach 129, IceDunes 108, Harbor 106,
  AncientSmokeVent 105, Cavern 8, VEE_Cenotes 7, Valley 7, VEE_JaggedRocks 1,
  VEE_CraterLake 1, DryLake 1. Reads as intentional sea/coastal landmark placement,
  not a stray-placement defect — flagged per instructions, not asserted as a bug.

---

## 4. Features vs CSV region

- `features.json`: 71 features. CSV: **71** distinct `region` values, 21872 tiles total.
- ✅ **Name match is 1:1 both directions**: 0 feature names with no matching CSV
  region, 0 CSV regions with no matching feature name.
- ✅ **tileCount agreement is exact**: comparing every one of the 71 matched
  name/region pairs' `feature.tileCount` against the CSV's per-region row count,
  **0 mismatches**. Confirms the Abandoned Mines regions (Ashfall + Notch, 34 tiles
  from CSV_REGION_SYNC_1) landed correctly and every other feature/region pair still
  agrees exactly.

**Feature↔region mismatches: 0**

---

## Summary

| Check | Result |
|---|---|
| Settlement faction roster (13 campaign / 21 world) | ✅ reconciles exactly |
| Settlement counts vs canon.yml | 🔴 96 live vs canon's stale 120 total (and stale 72-sum by_faction table) |
| Settlement on ice/sea/bounds | 🟡 1 on ice (id 249, Cold Archive, tile 17901); 0 on sea/water; 0 out of bounds |
| sw_Sarlacc | 🔴 6 live vs 1 expected; still at tile 2920 (SARLACC_WORLDMAP_RELOCATE_1 not yet actioned) |
| sw_DeadSarlacc | 🔴 7 live vs 4 expected |
| RUT_GapingDoom | ✅ 1, as expected |
| Art-patch coverage (48 defs) | ✅ 0 patched defs with zero instances |
| Tiles with >1 landmark | ✅ 0 |
| Landmarks on water | 🟡 615, all inside 4 sea/lake-named biomes (looks intentional) |
| Features ↔ CSV regions | ✅ 71/71 match, 0 tileCount mismatches |
