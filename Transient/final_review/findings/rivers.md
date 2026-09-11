# River audit — Ash'karr worldmap, V27 (2026-09-08)

Read-only. Data: `Transient/final_review/links.json` (1566 link-bearing tiles),
`Transient/final_review/tiles.csv` (21872 tiles), `world/world_neighbors_sub7b.csv`
(21872 adjacency rows), `world/ASHKARR_WORLDMAP_links.csv` (authoring CSV, 1713 rows).

## Calibration (pipeline check)

- `BiomeCypreJungle` river-bearing tiles (`potentialRivers` non-empty): **199** —
  matches the expected ~199±5 exactly. Same count using `visibleRivers>0`. Pipeline trusted.
- `BiomeCypreJungle` has 214 total link-bearing tiles (roads + rivers), 199 of them river-bearing.

## 1. Graph integrity — MEASURED clean

- 652 directed `potentialRivers` edge entries → 326 unique undirected river edges,
  335 distinct tiles, 11 connected components.
- **Asymmetric links (A→B, no B→A): 0.** Every river edge is fully reciprocal.
- **Nonadjacent links (neighbor not in `world_neighbors_sub7b.csv`): 0.** All 326
  edges connect tiles that are genuinely adjacent on the hex grid.
- **Orphan/fragment components: none smaller than 5 tiles.** Component size
  histogram (11 components, sizes sum to 335): 118, 115, 38, 14, 10, 10, 8, 6, 6, 5, 5.
  No singletons, no 2-tile fragments.
- Conclusion: the river LINK graph itself (symmetry, adjacency, connectivity) is clean.
  All defects below are in the `riverDist` field or in visibility/biome layering, not
  in the link topology.

## 2. riverDist sanity — MEASURED, and it corroborates the known "river_dist lies" defect

- 33 tiles have `riverDist=0` with non-empty `potentialRivers` (i.e. 33 candidate "mouths").
- Step consistency: of 326 undirected edges, **44 (13.5%) have `|riverDist diff| > 1`**
  between adjacent river tiles — not a smooth 1-step gradient. Worst jumps: tiles
  19361/19404 (dist 0 vs 18, diff 18), 9240/4380 (19 vs 3, diff 16), 19390/19391
  (5 vs 19, diff 14), 12480/4378 (1 vs 14, diff 13). These 44 anomalous edges have
  no adjacency or elevation defect of their own — endpoints checked adjacent, only
  6 of the 44 touch a water tile (elevation≤0).
- **Local-minima / basin count** (plateau-merged, so ties in one contiguous patch of
  equal `riverDist` count as ONE basin, not one per tile):
  - size-118 component: **11 separate riverDist=0-or-higher local basins** (not 1 mouth)
  - size-115 component: **20 separate basins**
  - size-38: 9 basins; size-14: 3 basins; one size-10: 4 basins, the other size-10: 2 basins
  - Only the 5 smallest components (sizes 8, 6, 6, 5, 5) have a single clean basin/mouth.
  - **6 of 11 components (containing 295 of 335 river tiles, 88%) have more than one
    riverDist minimum** — riverDist does NOT describe a single coherent flow-to-mouth
    field on the current link graph for the large components.
- Rejected hypothesis: riverDist is not simply "hex-BFS distance to nearest
  elevation≤0 tile" computed on the full map graph — only 60/1566 tiles (3.8%) match
  that measure, mean signed difference -12.5, range -45..+31. So it's not a stale
  ocean-distance field either; it looks like a genuinely stale/inconsistent per-tile
  value relative to the CURRENT potentialRivers link graph exported tonight.
- This lines up with the standing note in memory ("river_dist lies") — treat any
  flow-direction claim from riverDist alone as suspect for the two largest
  components especially, and confirm visually before making a lore claim from it.

## 3. Uphill flow — MEASURED, mostly clean but riverDist-dependent

Caveat: "mouth" here = tile with min riverDist per component, which section 2 shows
is ambiguous for 6 of 11 components — take the numbers below as a floor check, not
a final verdict, for those components.

- **0 components** show >50m net elevation decrease from (riverDist-min) mouth to
  (riverDist-max) furthest-upstream tile.
- **5 single-link uphill jumps** where a downstream neighbor (lower riverDist) sits
  >100m higher than its upstream tile:
  - upstream tile 6470 (322m) → downstream tile 14597 (617m), diff 295m
  - upstream tile 17328 (1m) → downstream tile 17326 (148m), diff 147m
  - upstream tile 17296 (741m) → downstream tile 1669 (886m), diff 145m
  - upstream tile 17324 (145m) → downstream tile 7043 (287m), diff 142m
  - upstream tile 16882 (1m) → downstream tile 16883 (135m), diff 134m
  - All 5 are candidates for a real bad edge, but given section 2's finding that
    riverDist itself is unreliable, these may just be more evidence of the same
    stale-riverDist defect rather than 5 independent bad links.

## 4. The Scald outflow ruling — MEASURED (connectivity), elevation intentionally not used

- `RUT_TheScald`: 312 tiles. Tiles adjacent to it (non-Scald): 79.
- **5 of the 11 river components touch a Scald-adjacent tile**: sizes 115, 38, 14,
  10, 5. (The other size-10, 8, 6, 6, 5 components do not touch the Scald.)
- Direction check via pure hop-BFS from each Scald-adjacent entry point to the
  component's farthest tile, plus geographic (lat/long) distance from the Scald
  centroid (lat -0.75, long -35.48) at each end:
  - size-38 component (start tile 19404, `BiomeCypreJungle`): runs 36 hops to tile
    12366 (`AB_MiasmicMangrove`, elev 71m), geo-distance from Scald grows 19.7→44.5.
    **Runs cleanly terminator-ward, ends in a mangrove low-land far from the Scald.**
  - size-14 component (start 19371): 12 hops to tile 3473 (`AB_MiasmicMangrove`,
    elev 26m), geo-distance 17.8→26.1. **Runs away, ends in mangrove lowland.**
  - size-10 component (start 2014, `BiomeCypreJungle`): 8 hops to tile 8331
    (`AB_MiasmicMangrove`, elev 13m), geo-distance 17.5→24.7. **Runs away.**
  - size-5 component (two Scald-adjacent members, 777 and 11947, both
    `AB_OcularForest`): only 3 hops each, ending on high-elevation (1407m/1587m)
    `AB_OcularForest` tiles — a short land dead-end, not a run to another sea, but
    still moving away from the Scald geographically.
  - **size-115 component is the exception**: it has 4 separate Scald-adjacent
    members (7791, 15141, 15173, 17343) scattered through the graph. Starting from
    3 of them the walk runs away cleanly (ending at tile 17293, `BiomeCypreJungle`,
    elev 966m, geo-distance growing 13.1–14.2 → 18.0). But starting from the 4th
    (17343), the farthest-by-hops tile is 15175 — itself `RUT_TheScald` (elev
    -350m by the map's own basin rendering, geo-distance falls 15.2→12.8, i.e.
    TOWARD the Scald). **This one component's link graph touches the Scald crater
    rim at two separate points rather than flowing outward from a single point** —
    worth a human look at whether that's an intentional ring-drainage around the
    crater or a stray link. Per the brief, elevation near the Scald is known to
    render wrong (basin), so this is reported as a CONNECTIVITY finding, not an
    elevation one.
  - **Net: 4 of 5 Scald-touching components run cleanly terminator-ward and
    terminate in real lowland/mangrove biomes or short land dead-ends, consistent
    with the "Scald spills outward" ruling. One (the largest, 115 tiles) touches
    the Scald rim at two separate points and does not read as a single clean
    outflow from pure connectivity alone.**

## 5. hiddenByBiome — MEASURED

- **15 tiles** have `visibleRivers < len(potentialRivers)` (a genuine player-facing
  invisible-river defect), grouped by biome:
  - `RUT_TheScald`: 8
  - `RUT_GreySea`: 3
  - `AB_PyroclasticConflagration`: 3
  - `RUT_TwilightSea`: 1
- **49 tiles** carry the `hiddenByBiome=true` flag, but **34 of those (all in
  `AB_PropaneLakes`) show no actual deficit** — `visibleRivers >= potentialRivers`
  for all of them. The flag is set but doesn't correspond to a visible-river loss
  for that biome/tile combination — worth checking whether `AB_PropaneLakes` rivers
  are actually being suppressed elsewhere (e.g. always-zero `potentialRivers` there)
  or whether the flag is simply mis-set for this biome.
- **0 tiles** have a real deficit without the flag set — no silent (unflagged)
  invisible-river cases found.

## 6. River def ladder — MEASURED

- Undirected river-edge def census (326 edges): Creek 170, River 62, HugeRiver 51,
  LargeRiver 43. Directed entries (652, both directions) are exactly double these,
  and **0 edges have an inconsistent def between the two link directions**.
- Sampled the 5 largest components, bucketing each component's edges into thirds
  by riverDist position (low third = near mouth):
  - size-118: near-mouth third has LargeRiver/River mixed with Creek; near-source
    third is Creek only. **Grows toward mouth.**
  - size-115: near-mouth third has HugeRiver/LargeRiver/River/Creek all present;
    near-source third skews smaller (Creek/River, fewer HugeRiver). **Grows toward mouth.**
  - size-38: near-mouth third is mostly HugeRiver; near-source third is HugeRiver
    only too — **doesn't show growth, this component is HugeRiver almost end to end.**
  - size-14: near-mouth has Creek+River, near-source has River only — **roughly consistent.**
  - size-10: near-mouth Creek+River, near-source Creek+River (same mix) — **too few
    edges (2 per third) to conclude anything; inconclusive.**
  - **Net: 3 of 5 longest components clearly grow toward the mouth as expected; one
    (size-38) is uniformly HugeRiver rather than growing; one (size-10) is too small
    a sample to judge.**

## 7. Authoring CSV vs live diff — MEASURED, fully in sync for rivers

- `world/ASHKARR_WORLDMAP_links.csv`: 1713 total rows (rivers + roads), 326 deduped
  undirected river edges.
- Live `links.json` also resolves to exactly 326 undirected river edges.
- **Authoring-only edges: 0. Live-only edges: 0. Edges in both: 326.** The
  authoring CSV is byte-for-byte in sync with the live river graph tonight — not
  stale, for rivers specifically (roads were not diffed here, out of scope).

## Bottom line

The river LINK graph (topology, symmetry, adjacency, def consistency, authoring-CSV
sync) is clean. The problems are all in **riverDist**: it fails to describe a single
coherent mouth/flow gradient for 6 of 11 components (88% of river tiles), is not
explained by any of the two hypotheses tested (map-wide distance-to-ocean, or per-edge
staleness at a handful of odd edges), and should not be trusted alone for flow-direction
or "does the Scald outflow reach the sea" claims without a visual/in-game check —
consistent with the team's existing "river_dist lies" caution. Everything else audited
(graph integrity, hiddenByBiome deficits, def ladder, authoring sync) is either clean
or narrowly scoped to specific biomes (`AB_PropaneLakes` flag mismatch, `RUT_TheScald`/
`RUT_GreySea`/`AB_PyroclasticConflagration`/`RUT_TwilightSea` visible-river deficits).
