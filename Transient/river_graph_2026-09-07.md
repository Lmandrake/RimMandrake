# Ash'karr river graph — derived from the frozen world data (ASHKARR_RIVER_LEDGER_1)

Generated 2026-09-07. Source of truth: `world/ASHKARR_WORLDMAP_tiles.csv` (21872 rows) and `world/ASHKARR_WORLDMAP_links.csv` (1665 rows, kind counts: {'river': 292, 'road': 1373}). Every number below came from parsing these two CSVs with Python's `csv` module — nothing here is a grep/wc count.

This is a DATA report. Where the painted map and the R1 lore ruling (the Scald is a perched ocean whose outflow makes the world's rivers, drawn at −350 m only because RimWorld cannot render an ocean at altitude) disagree, both readings are given, clearly labelled.

## 0. Headline numbers

- Tiles with non-zero `river_flow`: **298** (matches the brief's MEASURED 298).
- Rows in `ASHKARR_WORLDMAP_links.csv` with `kind == river`: **292**.
- Distinct tiles touched by a river-kind link: **308**.
- Distinct rivers (connected components — see §1 for the rule): **16**.
- River-touching tiles NOT carrying non-zero `river_flow` (all ocean-biome tiles at the downstream end of a link — flow is a land-tile stat): **11** — [1310, 2931, 3450, 8493, 11943, 15175, 16893, 16897, 17342, 19361, 19369].
- `river_flow` tiles with NO corresponding link row at all (a data gap, not part of any named river below): **1** — [11183].

## 1. Grouping rule: what counts as "one river"

Every row of `ASHKARR_WORLDMAP_links.csv` with `kind == river` is an undirected edge between two tiles (`a`,`b`), tagged with a size class (`def`: Creek/River/LargeRiver/HugeRiver). **One river = one connected component of this tile graph.** A component may contain multiple tributary heads (degree-1 land tiles) that merge at degree-≥3 confluence tiles before reaching a single lowest-elevation terminus — that is one river system, not several, exactly as "the Amazon and its tributaries" is one river. Where a component's terminus is a Scald or sea water tile, that tile is reported as the *mouth*; where no such water tile is touched, the mouth is just the lowest-elevation tile in the component (a terminal basin).

This produced **16 rivers** from the 308 river-linked tiles. Sizes (tile count, largest first): [102, 91, 32, 11, 11, 10, 7, 7, 6, 6, 5, 5, 5, 5, 3, 2].

Caveat: the CSV stores no explicit flow-direction field — only which two tiles are linked. Direction below is *inferred* from elevation (water runs downhill), never asserted from the `a`/`b` column order — see §3 for the one place that order was checked and found NOT to reliably encode direction (it correlates with elevation only ~87% of the time globally, and is much noisier tile-to-tile within a single path; UNMEASURED whether the game engine itself stores or needs directionality beyond what elevation implies).

## 2. Per-river detail

| river | tiles | mouth tile (elev, biome) | source tile(s) (elev) | biomes crossed (land tiles) | flow class (max def) | max river_flow | reaches water | terminal basin |
|---|---:|---|---|---|---|---:|---|---|
| R01 | 102 | 6213 (1m, ZBiome_Grasslands) | 11961 (2021m); 11965 (2011m); 7101 (2001m); 11092 (1695m); 2338 (1496m); 21322 (1426m); +16 more | BiomeCypreJungle×74, AB_OcularForest×10, ZBiome_Grasslands×9, Volcano×3, AB_PyroclasticConflagration×3, LavaField×2, AB_MiasmicMangrove×1 | LargeRiver | 11206.0 | — | **yes** |
| R02 | 91 | 1310 (-350m, RUT_TheScald) | 17237 (1473m); 17293 (966m); 17294 (961m); 1669 (886m); 2933 (397m); 2931 (-350m); +3 more | BiomeCypreJungle×57, AB_MiasmicMangrove×22, AridShrubland×5, ZBiome_DesertOasis×1, AB_OcularForest×1 | HugeRiver | 26176.0 | Scald, RUT_TwilightSea | no |
| R03 | 32 | 19361 (-350m, RUT_TheScald) | 12366 (71m) | BiomeCypreJungle×15, AB_MechanoidIntrusion×8, AB_MiasmicMangrove×5, Scarlands×3 | HugeRiver | 28936.0 | Scald | no |
| R04 | 11 | 14319 (84m, BiomeCypreJungle) | 11088 (991m); 6229 (733m); 11085 (461m) | BiomeCypreJungle×11 | Creek | 79.0 | — | **yes** |
| R05 | 11 | 8493 (-350m, RUT_TheScald) | 3473 (26m) | BiomeCypreJungle×9, AB_MiasmicMangrove×1 | River | 1825.0 | Scald | no |
| R06 | 10 | 19369 (-350m, RUT_TheScald) | 8331 (13m) | BiomeCypreJungle×6, AB_MiasmicMangrove×3 | River | 1085.0 | Scald | no |
| R07 | 7 | 15127 (459m, AridShrubland) | 2928 (1329m) | AridShrubland×6, AB_OcularForest×1 | Creek | 170.0 | — | **yes** |
| R08 | 7 | 11915 (1m, BiomeCypreJungle) | 15155 (551m); 7041 (387m) | BiomeCypreJungle×7 | Creek | 34.0 | — | **yes** |
| R09 | 6 | 16893 (-350m, RUT_GreySea) | 16871 (1720m) | AridShrubland×4, AB_OcularForest×1 | Creek | 120.0 | RUT_GreySea | no |
| R10 | 6 | 16882 (1m, AridShrubland) | 16957 (1342m) | AridShrubland×5, AB_OcularForest×1 | Creek | 145.0 | — | **yes** |
| R11 | 5 | 16897 (-350m, RUT_GreySea) | 9160 (1627m) | AridShrubland×2, ZBiome_Badlands×1, AB_OcularForest×1 | Creek | 95.0 | RUT_GreySea | no |
| R12 | 5 | 11943 (-350m, RUT_TheScald) | 11945 (1587m); 11946 (1407m) | AB_OcularForest×2, BiomeCypreJungle×2 | Creek | 45.0 | Scald | no |
| R13 | 5 | 16634 (1m, AridShrubland) | 16645 (612m) | AridShrubland×5 | Creek | 120.0 | — | **yes** |
| R14 | 5 | 7653 (99m, BiomeCypreJungle) | 19482 (1045m) | BiomeCypreJungle×5 | Creek | 56.0 | — | **yes** |
| R15 | 3 | 11914 (1m, BiomeCypreJungle) | 1312 (392m) | BiomeCypreJungle×3 | Creek | 26.0 | — | **yes** |
| R16 | 2 | 17324 (145m, BiomeCypreJungle) | 7043 (287m) | BiomeCypreJungle×2 | Creek | 18.0 | — | **yes** |

Notes on structure: rivers with more than one source tile listed are dendritic (multiple tributary heads merging through branch/confluence tiles) rather than single strands. Branch-node counts per river: {'R01': 17, 'R02': 8, 'R03': 0, 'R04': 1, 'R05': 0, 'R06': 0, 'R07': 0, 'R08': 0, 'R09': 0, 'R10': 0, 'R11': 0, 'R12': 0, 'R13': 0, 'R14': 0, 'R15': 0, 'R16': 0}.

Per-river elevation-vs-path-distance monotonicity (does elevation fall steadily from source to mouth, tile by tile along the graph distance?) — this is a noisy coarse-grid DEM, so exact monotonicity is not expected; it is reported as a sanity check, not a grading:

| river | % of adjacent distance-steps where elevation does not rise moving toward the mouth |
|---|---:|
| R01 | 56.4% (44 violations / 101 steps) |
| R02 | 46.7% (48 violations / 90 steps) |
| R03 | 54.8% (14 violations / 31 steps) |
| R04 | 80.0% (2 violations / 10 steps) |
| R05 | 80.0% (2 violations / 10 steps) |
| R06 | 66.7% (3 violations / 9 steps) |
| R07 | 100.0% (0 violations / 6 steps) |
| R08 | 66.7% (2 violations / 6 steps) |
| R09 | 100.0% (0 violations / 5 steps) |
| R10 | 100.0% (0 violations / 5 steps) |
| R11 | 100.0% (0 violations / 4 steps) |
| R12 | 75.0% (1 violations / 4 steps) |
| R13 | 75.0% (1 violations / 4 steps) |
| R14 | 100.0% (0 violations / 4 steps) |
| R15 | 100.0% (0 violations / 2 steps) |
| R16 | 100.0% (0 violations / 1 steps) |

Full tile-by-tile listing (lat/lon/arc/elev/biome/degree/distance-from-mouth) is in the companion CSV, `Transient/river_graph_2026-09-07.csv`.

## 3. Rivers touching the Scald, and which direction the DATA has them running

**5 of the 16 rivers touch `RUT_TheScald`**: R02, R03, R05, R06, R12.

For every river link directly bordering a Scald water tile (9 edges, listed below), the Scald tile sits at elev **−350 m — the lowest elevation on the planet** — and the tile on the other end of that same edge is always higher. Reading elevation the only way the data supports (water runs downhill), **every one of these edges reads as INFLOW: water entering the Scald**, never leaving it. This holds for all 9 boundary edges with no exception.

| river | edge (a,b) | river def | which side is the Scald tile |
|---|---|---|---|
| R02 | 17342, 17343 | LargeRiver | a |
| R02 | 15175, 15173 | River | a |
| R02 | 2931, 7791 | River | a |
| R02 | 1310, 15141 | River | a |
| R03 | 19361, 19404 | HugeRiver | a |
| R05 | 8493, 19371 | Creek | a |
| R06 | 19369, 2014 | River | a |
| R12 | 11943, 777 | Creek | a |
| R12 | 11943, 11947 | Creek | a |

**This is the map-as-drawn picture.** Per ruling R1, the lore has it backwards on purpose: the Scald is a perched ocean whose outflow makes these rivers, and its −350 m reading is an engine artifact (RimWorld cannot render an ocean at altitude) rather than a fact about the world. So the DATA says inflow; the LORE says these are the world's outflows. Both statements are recorded here on purpose per R18 — this is the disagreement the repaint (§5) exists to resolve.

## 4. Terminal basins vs. sea-reaching rivers

- **Terminal basin (ends on land, touches no Scald or sea water tile) — 9 rivers:** R01, R04, R07, R08, R10, R13, R14, R15, R16.
- **Reaches the Scald — 5 rivers:** R02, R03, R05, R06, R12 (see §3).
- **Reaches a named sea (RUT_GreySea / RUT_TwilightSea / SeaIce) and not the Scald — 2 rivers:** R09, R11.
- **R02 is the one river touching BOTH** — its connected component includes tributary arms reaching `RUT_TheScald` AND a separate arm reaching `RUT_TwilightSea` (tile 3450). By the §1 grouping rule these count as one river system with two mouths; it is listed once in the totals above under whichever category is checked first, so is called out here explicitly to avoid double-counting confusion.

SeaIce: **0 rivers touch it** — UNMEASURED whether any SeaIce tile exists on this map at all beyond what's in the tiles CSV; not checked separately since no river component's water tiles carried that biome.

## 5. Repaint spec: links that read as inflow-to-Scald and would need reversing for R1's outflow

**9 river links, across the 5 Scald-touching rivers, currently encode flow INTO the Scald** (the table in §3, repeated here as the literal reversal list — reverse the `a`/`b` sense of each row so the Scald side is upstream, not downstream):

```
river,a,b,def,scald_side
R02,17342,17343,LargeRiver,a
R02,15175,15173,River,a
R02,2931,7791,River,a
R02,1310,15141,River,a
R03,19361,19404,HugeRiver,a
R05,8493,19371,Creek,a
R06,19369,2014,River,a
R12,11943,777,Creek,a
R12,11943,11947,Creek,a
```

**Scope warning, not a guess dressed as a measurement:** flipping just these %d boundary rows changes only where each river touches the Scald. A physically consistent outflow repaint would also need the elevation PROFILE of each of these 5 rivers' full paths re-graded so the Scald end is genuinely the high point (today it is the planet's lowest reading, −350 m, by construction). That re-grading is a build decision — how high, how the slope is drawn on a coarse tile grid — not something this data pass can derive. **UNMEASURED: the full re-grade.** What IS measured and handed over cleanly is the exact link list above, which is where any repaint script starts.

## 6. UNMEASURED

- Whether `ASHKARR_WORLDMAP_links.csv`'s `a`/`b` column order is meant by the exporter/engine to encode flow direction at all — no field documents this, and the empirical correlation with elevation (b higher than a in 253/292 = 86.6%% of all river edges planet-wide, but noisy and inconsistent within a single river's own path — see §2's monotonicity table) is not strong enough to assert it as a rule. Direction claims in this report come only from elevation.
- Whether tile 11183 (`river_flow=41`, `Wasteland`, no link row) belongs to one of the 16 named rivers or is a separate, un-linked feature (a spring, a data-entry gap, or a lone lake outlet) — not resolvable from these two CSVs alone.
- What the actual in-engine river rendering does with a reversed link at map-generation time — this report is about the world-tile data only; RimWorld's local river visuals are generated at map load, and whether that step reads `links.csv`-style directionality or recomputes flow from local elevation was not checked here (no game session was available — RimWorld was mid-load for this whole task).
- Named/lore identity of each of the 16 rivers (i.e. which is "the river the Miasma sheet calls X") — this report identifies rivers only by graph structure (R01..R16), not by any design-doc name; matching them up is a separate task.

---
*Companion file: `Transient/river_graph_2026-09-07.csv` — one row per river-linked tile, with river_id, coordinates, elevation, biome, degree, and graph distance from that river's mouth.*
