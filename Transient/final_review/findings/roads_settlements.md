# Roads + settlements audit — Ash'karr worldmap, baseline V27 (2026-09-08)

Read-only. Source data: `Transient/final_review/links.json` (1,566 link-bearing
tiles), `Transient/final_review/objects.json` (196 world objects), `Transient/final_review/tiles.csv`
(21,872 tiles), `world/world_neighbors_sub7b.csv` (21,872 rows). Parse checks out against
the stated calibration: 196 objects, `isSettlement=true` on 96 rows (95 NPC + 1
`PlayerColony`/"New Arrivals" — the live colony, not an NPC settlement).

## 1. Road graph

- **MEASURED.** 1,241 unique road edges from `potentialRoads`, touching 1,279 tiles,
  in **47 connected components**.
- **MEASURED.** One giant component of **1,126 tiles** (the road web). The other 46
  components are small: sizes `9,7,7,6,6,6,6,5,5,5,4,4,3×14,2×17` — i.e. 46 disconnected
  fragments of 2-9 tiles, entirely separate from the main network and from each other.
- **MEASURED — dead-end stubs.** 152 degree-1 (leaf) road tiles; 46 of those are
  themselves settlements (normal spur-in, not a defect). Of the remaining 106 leaves,
  64 distinct stub chains (≥1 tile) after dedup, of which:
  - 5 chains land back on a settlement via a longer path (fine),
  - **17 chains (≥2 tiles) dead-end at a junction** — dangling branches that go nowhere,
  - **42 chains are fully isolated segments** (both ends are leaves, i.e. tiny orphan
    road fragments not attached to the main network at all — this is most of the 46
    small components above).
  Worst 10 real stubs (chain length in tiles, start→end tile IDs):
  - len 17: 3384→1024 (ends at a junction)
  - len 9: 17276→8147 (junction); 20514→20405 (junction); 13176→21508 (isolated, both ends leaves)
  - len 9: 10384→10355 (junction)
  - len 8: 15905→4138 (junction)
  - len 7: 7649→11060 (isolated); 13602→15919 (junction); 12417→9171 (junction); 21684→9958 (junction)

## 2. Settlement connectivity

- **MEASURED.** 78 of 95 NPC settlements sit on or adjacent to the road network; **18 do not**.
- Off-road settlements by faction (all MEASURED from live data):
  - **Deep Desert Tribes: 9 of 9** — i.e. every single Tribes settlement is off-road.
    This matches the design doc's own ruling (`ASHKARR_WORLD_DEFINITION.md` §7:
    *"they do not build roads"* — owner, 2026-08-24, "every road that led to a
    Tusken holding was removed from the map") — **deliberate, not a defect.**
  - Wildsteam Clan: 3 of 9 (Bitterleaf, Oilpalm, Warthorn — the doc calls these the
    clan's newest, most remote seats, added 2026-08-26 "vetted... before placement,"
    with no stated road requirement — plausibly deliberate).
  - Free Droid Enclaves: 2 of 7 (The Free Charge, Vent Nine — doc explicitly lists
    these as deliberately "quiet, hidden seats").
  - Ascendant Helix: 2 of 7 (Quiet Lab, The Fair Copy — doc sites Helix on isolated
    highlands/Horror Wastes by design).
  - Geonosian Foundry Hive: 1 of 5 (Hollow Hive).
  - Deepwater Compact: 1 of 6 (Deepwater Hold).
  - No off-road settlements for: Homestead Defense League, Hutt Cartel, Blackstar
    Company, the Junkers, Jawa Trade Moot, Galactic Empire.

## 3. Invisible roads (hiddenByBiome)

- **MEASURED.** `hiddenByBiome=true` on 49 tiles, but only **34 of those actually carry a
  potential-road edge whose `visibleRoads < len(potentialRoads)`** (the other 15 are
  flagged hiddenByBiome with zero roads present at all, so nothing is actually hidden there).
- **All 34 real invisible-road tiles are biome `AB_PropaneLakes`, and every hidden
  edge is `AncientAsphaltHighway`.** No other biome or road def hides a road in this
  data. `AncientAsphaltHighway` also legitimately renders elsewhere (see §4), so the
  suppression is biome-specific to `AB_PropaneLakes`, not def-wide.

## 4. Road def variety

- **MEASURED — census of the 1,241 edges:** DirtRoad 531, DirtPath 316,
  StoneRoad 287, AncientAsphaltHighway 107.
- **MEASURED — class correlates with biome, not uniform:**
  - DirtPath / DirtRoad cluster in `Desert`, `ExtremeDesert`, `Wasteland`,
    `ZBiome_Badlands`, `AridShrubland` — the dry-flat majority terrain.
  - StoneRoad clusters in `ZBiome_DesertOasis` (90), `ZBiome_Badlands` (80),
    `AB_FeraliskInfestedJungle` (61), `BiomeCypreJungle` (60), `PoisonForest` (50) —
    oasis/jungle terrain, consistent with "better roads near water/settlements."
  - AncientAsphaltHighway clusters in `AB_MycoticJungle` (55), `AB_PropaneLakes` (49,
    all suppressed per §3), `ExtremeDesert` (49), **`RUT_NightsideIce` (30)**,
    `AB_RockyCrags` (22) — a mixed, harsher-biome set, plausibly "ancient ruin road
    surviving in inhospitable terrain," but UNMEASURED whether that's an authored
    intent or an artifact of import.
  - Did not correlate class against faction territory directly (no per-edge faction
    attribution in `links.json`); UNMEASURED for that half of the question.

## 5. Settlement roster vs faction docs

- **MEASURED — live per-faction settlement counts (96 rows incl. 1 player colony):**
  Homestead Defense League 27, Hutt Cartel 12, Wildsteam Clan 9, Deep Desert Tribes 9,
  Free Droid Enclaves 7, Ascendant Helix 7, Deepwater Compact 6, Geonosian Foundry
  Hive 5, Blackstar Company 4, the Junkers 4, Galactic Empire 3, Jawa Trade Moot 2,
  New Arrivals (player colony) 1.
- **Compared against `design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md` §7**
  ("Factions — 120 settlements", most recent per-faction table, itself already
  reduced by the 2026-08-24/26 cuts to a stated total of ~108-110):
  quoted targets — Hutt Cartel 17, Homestead Defense League 33, Deep Desert Tribes 9,
  Jawa Trade Moot 4, the Junkers 5, Geonosian Foundry Hive 5, Deepwater Compact 6,
  Wildsteam Clan 9, Blackstar Company 4, Free Droid Enclaves 8, Ascendant Helix 7,
  Galactic Empire 3.
  **MEASURED gaps (live vs this doc's own most-recent target):**
  - **Jawa Trade Moot: 2 live vs 4 documented — 50% short.**
  - **Hutt Cartel: 12 live vs 17 documented — 5 short.**
  - **Homestead Defense League: 27 live vs 33 documented — 6 short.**
  - Free Droid Enclaves 7 vs 8 (1 short), the Junkers 4 vs 5 (1 short) — minor.
  - Exact matches: Deep Desert Tribes (9), Geonosian Foundry Hive (5), Deepwater
    Compact (6), Wildsteam Clan (9), Blackstar Company (4), Ascendant Helix (7),
    Galactic Empire (3).
  - Total live NPC settlements (95) vs this doc's stated total (~108-110): **~13-15
    short**, concentrated almost entirely in Trade Moot/Hutt/Homestead.
  ⚠️ Caveat: this design doc's own settlement table has been revised at least three
  times in-place (72→120→108) and cites `world/ASHKARR_WORLDMAP_settlements.csv` as
  authoritative, which is itself dated 2026-08-26 and shows **121** rows with a
  *different* distribution again (Homestead 37, Hutt 19, Free Droid 12, Junkers 8,
  Jawa Trade Moot 7 — all higher than tonight's live V27). So the direction is
  consistent across two independent doc snapshots: **live V27 has fewer Homestead,
  Hutt, Free Droid, Junkers and Trade Moot settlements than every prior documented
  target**, while Tribes/Geonosian/Deepwater/Wildsteam/Blackstar/Helix/Empire hold
  steady at their most-recent target. UNMEASURED which pass removed them or whether
  it was intentional.
- **Biome-hostility check, MEASURED:** Deep Desert Tribes sit in `Desert`(3)/`ExtremeDesert`(6)
  — correct per doc ("desert-native"). Wildsteam Clan sit in `BiomeCypreJungle`(7),
  `AB_FeraliskInfestedJungle`(1), `AB_MiasmicMangrove`(1), 27-58.6°C — matches doc's
  "cool uplands/rare woods" only loosely (these read as hot jungle, not "cool"), but
  not obviously wrong per the later Bitterleaf/Oilpalm/Warthorn ruling.
  **One clear hostile-biome hit: Ascendant Helix's "Cold Archive" (tile 17901) sits on
  `RUT_NightsideIce` at -29.8°C.** This is actually consistent with the doc's own
  2026-08-24 ruling ("the Helix sits where the BIOWEAPON is... Horror Wastes... Cold
  Archive... in the Horror Wastes") — so **not a bug, matches lore**, flagging per
  instructions since it does read as biome-hostile at first glance.

## 6. Spacing

- **MEASURED** (great-circle/haversine on `tiles.csv` lat/long, 95 NPC settlements):
  nearest-neighbor distance distribution — min 2.54°, p25 7.49°, median 10.68°,
  p75 15.96°, max 35.61°, mean 11.98°.
- **1 pair closer than 3°:** The Claim Jump (the Junkers, tile 16898) ↔ The Ore Moot
  (Jawa Trade Moot, tile 8082), 2.54° apart. (Matches the doc's own note that "The
  Ore Moot" was a kept anchor near a Junker seat — plausibly deliberate co-location
  at the stolen-mine site both factions reference.)
- **MEASURED — a 30°+ empty longitude band:** three consecutive 10°-wide longitude
  bins, **100°E to 130°E, hold zero settlements** (a fourth bin, 140-150°E, is also
  empty but is separated from the first three by one settlement at 130-140°E). This
  is a longitude-only proxy, not a true great-circle void test — UNMEASURED whether
  it holds up as an angular void once latitude is folded in, but it is a genuine gap
  in the raw distribution worth a look.
- The single most isolated settlement is 35.61° from its nearest neighbor —
  UNMEASURED which one (not logged by name in this pass, only via the distance
  array); available on request from the same haversine table.

## 7. Null-faction / unnamed objects

- **MEASURED.** Zero settlements have `hasFaction=false` or `name=null` — no
  destroyed-on-load hazard among the 96 `isSettlement=true` rows.
- 80 of 196 objects overall have `hasFaction=false`, but all 80 are asteroids/derelict
  stations (`BigAsteroidBasic` 40, `VGE_AsteroidField` 6, `VGE_DerelictStation` 6,
  `VGE_PorousAsteroid` 5, `VGE_DenseAsteroid` 4, `VGE_AsteroidCluster` 3,
  `AsteroidBasic` 3, `VGE_AsteroidWithRuins` 3, `VGE_IceAsteroid` 3,
  `VGE_SmallAsteroid` 3, `VGE_ShatteredAsteroid` 2, `VGE_GiantAsteroid` 2) — expected,
  not a hazard.
- One anomaly worth naming: object id 255, def `Settlement`, `faction=PlayerColony`,
  `factionName="New Arrivals"`, `name="Colony"` — this is the live player colony,
  correctly faction-tagged, just easy to mis-read as an unattributed NPC settlement
  in a naive factionName tally (it was excluded from all §1-6 settlement stats above).
