# FUNGALFOREST_RAID_MERGE_1 — per-tile merge plan (measured 2026-09-07)

Offline plan only. Nothing painted, nothing committed to the world. Produced while
RimWorld was mid-load, from `world/ASHKARR_WORLDMAP_tiles.csv` (21872 rows) and
`world/world_neighbors_sub7b.csv`, parsed with Python's `csv` module — no grep/wc/strings
on either file. See `infrastructure/state/items/FUNGALFOREST_RAID_MERGE_1.md` for the
owner's ruling and the prior region×sector cluster spec already on file there; this
plan re-derives the same merge at PER-TILE granularity, using the neighbors CSV directly,
as a cross-check on that spec (see §6).

## 1. MEASURED — current BMT_FungalForest tile count and distribution

**425 tiles** currently carry `biome == BMT_FungalForest` (measured by
iterating every row of the tiles CSV with `csv.DictReader` and comparing the `biome`
column — not grepped).

| field | min | max | mean |
|---|---|---|---|
| arc | 74.02 | 132.87 | 110.48 |
| temp_c | -43.9 | 24.3 | -14.95 |
| elev_m | 1.0 | 1506.0 | 718.71 |
| rain_mm | 0.0 | 14.0 | 0.09 |

All 425 tiles measure `rain_mm` between 0 and 14 (mean 0.09) — this is a dry/underground
biome painted onto the surface, consistent with the owner's ruling that it never belonged
there. `elev_m` spans 1–1506 (mean 719), i.e. it sits across both lowland and highland
terrain — elevation was not a distinguishing feature of where it got painted.

Region breakdown (from the tiles CSV `region` column):

| region | tiles |
|---|---|
| Nightspill | 107 |
| Sporefields | 85 |
| South Crags | 78 |
| Stillwood | 49 |
| Sweatwood | 44 |
| Frostcaps | 30 |
| Hanging Wood | 11 |
| Blindwood | 10 |
| Stepwood | 9 |
| Mould Marches | 2 |

## 2. Adjacency method

For every one of the 425 tiles, its neighbor list was read from
`world_neighbors_sub7b.csv` (`n0`..`n5`, `-1` meaning no edge) and each neighbor's `biome`
looked up in the tiles CSV. Two tiers of tiles resulted:

- **216 boundary tiles** have at least one non-`BMT_FungalForest` neighbor directly —
  their new biome is read straight off that neighbor set.
- **209 interior tiles** are surrounded ONLY by other `BMT_FungalForest` tiles (this
  biome sits in contiguous blobs tens of tiles wide, not single tiles) — direct adjacency
  gives no information for these, so they were resolved by a multi-source breadth-first
  search across the `BMT_FungalForest`-only subgraph: each interior tile inherits the
  label of its NEAREST already-resolved tile (graph-hop distance, not lat/lon distance),
  which is what keeps the assignment following the actual terrain per sub-pocket instead
  of painting one biome over an entire blob (the owner's "nonbullseye" instruction).
- **0 tiles** were unreachable (no fully-enclosed pocket with zero resolvable boundary
  anywhere in it) and **0 tiles** had all-water neighbor sets.

Full adjacency + assignment detail for all 425 tiles is in the appendix table (§7); it is
too large to narrate tile-by-tile in prose.

## 3. PROPOSED per-tile reassignment and summary counts

**Rule:** most common biome among a tile's non-`BMT_FungalForest` neighbors (direct tier)
or among its nearest resolved neighbors by BFS hop-distance (interior tier); ties broken
by whichever candidate biome's map-wide mean (temp_c, rain_mm) is closer to this tile's
own (temp_c, rain_mm), rain weighted down 50:1 against temp since rain is near-zero and
near-constant across every candidate here.

| receiving biome | tiles gained | of which by direct majority | by BFS interior fill | tied picks (flagged §4) |
|---|---|---|---|---|
| AB_MycoticJungle (the Rot) | 352 | 179 | 173 | 3 |
| Desert | 53 | 24 | 29 | 7 |
| BiomeGRimond (Blue Desert) | 8 | 6 | 2 | 3 |
| AB_RockyCrags (Forsaken Crags) | 8 | 4 | 4 | 1 |
| RUT_NightsideIce (the deep-night highland) | 4 | 3 | 1 | 1 |
| **TOTAL** | **425** | 216 | 209 | 15 |

425 tiles resolved, 0 left unassigned after the merge (matches the MEASURED count in §1 —
every dissolved tile lands somewhere).

## 4. NEEDS OWNER RULING — genuinely ambiguous tiles

**0 tiles** are isolated (unreachable pocket) or all-water-bounded — none exist in this
dataset. But **15 tiles** had a genuine tie in their deciding vote (two or three candidate
biomes with equal support) that this plan broke automatically by temp/rain closeness. Since
that tie-break is a judgment call, not a measurement, these are flagged for the owner to
confirm or override. The "proposed" column is this plan's auto-pick; "candidates" lists
everything tied.

| tile | region | tier | arc | temp_c | proposed | tied candidates |
|---|---|---|---|---|---|---|
| 223 | South Crags | interior | 124.39 | -31.3 | AB_MycoticJungle (the Rot) | BiomeGRimond, AB_MycoticJungle |
| 2766 | Stillwood | interior | 130.47 | -40.1 | RUT_NightsideIce (the deep-night highland) | RUT_NightsideIce, AB_MycoticJungle |
| 3761 | South Crags | direct | 124.36 | -31.0 | BiomeGRimond (Blue Desert) | BiomeGRimond, AB_RockyCrags |
| 4099 | Sporefields | interior | 90.0 | 12.6 | Desert | AB_MycoticJungle, Desert |
| 5648 | Sweatwood | interior | 83.34 | 16.5 | Desert | Desert, AB_MycoticJungle |
| 7560 | Sweatwood | interior | 77.97 | 20.4 | Desert | AB_MycoticJungle, Desert |
| 8620 | South Crags | interior | 122.93 | -29.0 | AB_RockyCrags (Forsaken Crags) | BiomeGRimond, AB_RockyCrags |
| 8621 | South Crags | interior | 123.65 | -30.2 | BiomeGRimond (Blue Desert) | BiomeGRimond, AB_RockyCrags |
| 9699 | Hanging Wood | direct | 116.96 | -20.9 | AB_MycoticJungle (the Rot) | AB_RockyCrags, AB_MycoticJungle |
| 10178 | Sporefields | interior | 96.05 | 5.7 | Desert | Desert, AB_MycoticJungle |
| 13764 | Sweatwood | direct | 74.02 | 24.0 | Desert | Desert, AB_MycoticJungle |
| 15662 | Sporefields | interior | 95.21 | 6.2 | Desert | AB_MycoticJungle, Desert |
| 15924 | Stepwood | interior | 86.06 | 14.3 | Desert | Desert, AB_MycoticJungle |
| 17377 | Blindwood | direct | 129.44 | -35.4 | BiomeGRimond (Blue Desert) | BiomeGRimond, AB_PropaneLakes, AB_MycoticJungle |
| 20119 | Hanging Wood | interior | 119.22 | -23.7 | AB_MycoticJungle (the Rot) | AB_MycoticJungle, AB_RockyCrags |

Pattern in the ties: `Desert` vs `AB_MycoticJungle` (the Rot) at the warm dayside edge
(Sporefields/Sweatwood/Stepwood, arc 74–96), and `BiomeGRimond` (Blue Desert) vs
`AB_RockyCrags` (Forsaken Crags) vs the Rot at the cold nightside edge (South Crags/
Blindwood/Hanging Wood/Stillwood, arc 117–131) — i.e. exactly the two frontiers where the
dissolved biome sat between two already-adjoining neighbours in comparable proportion.
The owner may prefer to rule these as a block (e.g. "South Crags ties go to whichever
neighbour is closer by tile count in that cluster") rather than tile-by-tile.

## 5. Impact on each receiving biome's stated arc range

Arc ranges below are each biome's own sheet in `design/Jawa/worldbuilding/biomes/` (read
only, not modified — another agent is editing that directory live).

| receiving biome | sheet's stated arc range | new tiles' arc range and fit |
|---|---|---|
| AB_MycoticJungle (the Rot) (352 tiles) | 89–130 (`the_rot.md`) | arc 75.3–132.9 pushes past BOTH ends — new min 75.3 is 14° below the sheet's dayside edge, new max 132.9 is 3° past its nightside edge |
| Desert (53 tiles) | 60–88 core (`desert.md`; already only ~51% of the def sits inside this per `WORLDMAP_DESERT_BAND_REPAIR_1`) | arc 74.0–96.1 — mean 86.5 fits, but max 96.1 adds MORE tiles past 88°, compounding the already-open band-repair issue |
| BiomeGRimond (Blue Desert) (8 tiles) | Deadstone ring 126–143, lobes to 155 in places (`the_blue_desert.md`) | arc 123.7–131.4 — slightly below 126 at the low end, otherwise inside |
| AB_RockyCrags (Forsaken Crags) (8 tiles) | 99–121 (`forsaken_crags.md`) | arc 118.5–122.9 — top end 1.9° past 121, otherwise inside |
| RUT_NightsideIce (the deep-night highland) (4 tiles) | 128–159, 802 tiles measured (`nightside_ice.md`) | arc 130.5–131.9 — fully inside, and only 4 tiles vs. its own 802 (0.5% growth) |

**The Rot (`AB_MycoticJungle`) is the one that matters**: it gains 352 of the 425 tiles
(83% of the merge), growing from its own 1,939-tile base (per `README_BIOME_GRAMMAR.md`)
by ~18%, and the new tiles push its arc footprint outside the range its own sheet states —
both ends. That range statement in `the_rot.md` line 17 will need a follow-up edit once
this merge is ruled and painted (not done here — that file is being edited live by another
agent right now).

`Desert` gaining 53 tiles, mostly past arc 88, compounds a defect ALREADY open under
`WORLDMAP_DESERT_BAND_REPAIR_1` (only ~51% of `Desert` sits in its own stated 60–88 band
today) rather than creating a new one — worth flagging to whoever picks that item up next.

`BiomeGRimond` (+8), `AB_RockyCrags` (+8) and `RUT_NightsideIce` (+4) are each too small a
gain (0.4–0.7% of the biome's own current tile count) to matter to their sheets' stated
ranges on their own.

## 6. Cross-check against the item file's existing cluster spec

`FUNGALFOREST_RAID_MERGE_1.md` already carries a region×30°-sector cluster table (tiles
summing to 425 — the SAME measured count as §1 here) that assigns the Rot to 8 of its 10
listed clusters, the Wasteland to `South Crags sector 9` (16 tiles) and a split Rot/
Wasteland to `South Crags sector 8` (62 tiles). This per-tile plan instead finds the Rot
receiving 352/425 (83%), with `Desert`, `BiomeGRimond`, `AB_RockyCrags` and
`RUT_NightsideIce` splitting the rest — **`Wasteland` does not appear at all** in this
per-tile result, because no `BMT_FungalForest` tile in the current CSV has a `Wasteland`
neighbor close enough (by graph-hop or direct adjacency) to win a vote; the item file's
`South Crags sector 9` cluster resolves here to `BiomeGRimond`/`AB_RockyCrags` instead
(see the tied tiles 3761/8620/8621 in §4, all `South Crags`, all torn between those two).
This is a real disagreement between the two methods, not a measurement error in either —
the item file's spec works at coarse sector granularity and may be using a wider adjacency
window than immediate-neighbor/BFS; **the owner should decide which method's South Crags
call to keep** before painting.

## 7. Appendix — full per-tile table (425 rows)

`tier`: **D** = direct (had a non-FungalForest neighbor); **I** = interior (BFS-filled,
`dist` = hop count to nearest resolved tile). `nbr biomes` lists each distinct
non-FungalForest biome seen among DIRECT neighbors only (empty for pure-interior tiles).

| tile | region | arc | temp_c | tier | nbr biomes (direct) | assigned | tie? |
|---|---|---|---|---|---|---|---|
| 46 | Sweatwood | 78.01 | 20.9 | I(d1) | — | Desert |  |
| 57 | Stillwood | 130.2 | -39.7 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 99 | Sporefields | 96.59 | 4.0 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 219 | South Crags | 117.3 | -25.1 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 223 | South Crags | 124.39 | -31.3 | I(d2) | — | AB_MycoticJungle (the Rot) | TIE |
| 248 | Nightspill | 113.93 | -21.6 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 279 | Sporefields | 90.0 | 12.4 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 281 | Sporefields | 95.77 | 5.0 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 329 | Nightspill | 119.67 | -22.5 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 428 | Nightspill | 121.9 | -31.0 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 483 | Sporefields | 96.84 | 5.1 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 538 | Stepwood | 85.99 | 13.7 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 604 | Frostcaps | 123.44 | -31.3 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 606 | Frostcaps | 124.14 | -30.3 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 608 | Stillwood | 130.76 | -40.5 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 811 | Nightspill | 117.9 | -24.0 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 969 | Nightspill | 121.58 | -31.0 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 1054 | Nightspill | 102.06 | -5.9 | D | AB_MycoticJungle:4 | AB_MycoticJungle (the Rot) |  |
| 1078 | Sweatwood | 82.1 | 18.4 | D | Desert:1 | Desert |  |
| 1079 | Sweatwood | 81.96 | 16.8 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 1080 | Sweatwood | 74.07 | 24.3 | D | Desert:3 | Desert |  |
| 1081 | Sweatwood | 77.94 | 19.5 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 1144 | Stillwood | 125.97 | -33.6 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 1146 | Stillwood | 128.42 | -37.3 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 1148 | Stillwood | 128.42 | -37.3 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 1382 | Sporefields | 85.85 | 16.4 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 1383 | Sporefields | 87.8 | 14.9 | D | Desert:1 | Desert |  |
| 1394 | Sporefields | 94.15 | 6.8 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 1395 | Sporefields | 98.29 | 1.6 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 1396 | Sporefields | 92.2 | 9.4 | I(d2) | — | Desert |  |
| 1397 | Sporefields | 94.49 | 7.2 | I(d1) | — | Desert |  |
| 1398 | Mould Marches | 100.84 | -2.2 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 1440 | Stepwood | 86.11 | 14.5 | D | Desert:2, AB_MycoticJungle:1 | Desert |  |
| 1683 | Blindwood | 130.56 | -36.0 | D | BiomeGRimond:2 | BiomeGRimond (Blue Desert) |  |
| 1706 | Nightspill | 116.36 | -20.5 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 1776 | Frostcaps | 119.15 | -24.9 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 1777 | Frostcaps | 121.68 | -27.3 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 2116 | South Crags | 114.79 | -22.9 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 2117 | South Crags | 119.15 | -29.0 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 2119 | South Crags | 119.76 | -27.1 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 2138 | South Crags | 122.13 | -28.6 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 2139 | Hanging Wood | 119.97 | -24.8 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 2142 | South Crags | 128.7 | -36.2 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 2288 | Nightspill | 117.79 | -26.6 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 2292 | Nightspill | 113.95 | -20.2 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 2293 | Nightspill | 117.95 | -25.2 | I(d3) | — | AB_MycoticJungle (the Rot) |  |
| 2318 | Nightspill | 121.97 | -30.1 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 2673 | Nightspill | 100.71 | -4.3 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 2674 | Nightspill | 103.34 | -7.7 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 2696 | Sweatwood | 75.45 | 23.2 | D | Desert:3 | Desert |  |
| 2698 | Sweatwood | 79.47 | 20.7 | D | Desert:2 | Desert |  |
| 2699 | Sweatwood | 80.67 | 18.8 | I(d2) | — | Desert |  |
| 2700 | Sweatwood | 76.66 | 21.6 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 2701 | Sweatwood | 79.29 | 18.9 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 2764 | Stillwood | 128.2 | -37.0 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 2765 | Stillwood | 127.98 | -37.0 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 2766 | Stillwood | 130.47 | -40.1 | I(d1) | — | RUT_NightsideIce (the deep-night highland) | TIE |
| 3002 | Sporefields | 85.67 | 17.2 | D | Desert:2 | Desert |  |
| 3014 | Sporefields | 96.36 | 3.8 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 3015 | Sporefields | 98.59 | 1.0 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 3016 | Sporefields | 94.33 | 6.5 | I(d3) | — | AB_MycoticJungle (the Rot) |  |
| 3017 | Sporefields | 94.44 | 7.0 | I(d2) | — | Desert |  |
| 3018 | Sporefields | 98.81 | 1.0 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 3019 | Sporefields | 96.7 | 4.2 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 3396 | Frostcaps | 117.1 | -20.3 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 3397 | Frostcaps | 119.39 | -24.5 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 3734 | South Crags | 115.0 | -22.4 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 3735 | Hanging Wood | 115.16 | -21.6 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 3736 | South Crags | 117.1 | -26.6 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 3737 | South Crags | 119.39 | -28.2 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 3738 | South Crags | 119.6 | -27.6 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 3739 | South Crags | 117.47 | -24.3 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 3758 | South Crags | 124.36 | -31.7 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 3759 | South Crags | 122.18 | -28.0 | I(d3) | — | AB_MycoticJungle (the Rot) |  |
| 3760 | South Crags | 122.18 | -28.0 | I(d1) | — | AB_RockyCrags (Forsaken Crags) |  |
| 3761 | South Crags | 124.36 | -31.0 | D | BiomeGRimond:1, AB_RockyCrags:1 | BiomeGRimond (Blue Desert) | TIE |
| 3762 | South Crags | 126.55 | -34.6 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 3763 | South Crags | 126.55 | -34.0 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 3908 | Nightspill | 115.16 | -24.0 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 3910 | Nightspill | 112.63 | -19.3 | D | AB_MycoticJungle:4 | AB_MycoticJungle (the Rot) |  |
| 3912 | Nightspill | 115.29 | -22.3 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 3913 | Nightspill | 116.57 | -24.5 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 3938 | Nightspill | 123.27 | -31.7 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 3939 | Nightspill | 124.66 | -33.8 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 4095 | Sporefields | 92.03 | 10.1 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 4097 | Sporefields | 87.88 | 15.2 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 4098 | Sporefields | 92.12 | 9.5 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 4099 | Sporefields | 90.0 | 12.6 | I(d2) | — | Desert | TIE |
| 4108 | Sporefields | 93.96 | 7.5 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 4109 | Sporefields | 96.09 | 4.3 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 4391 | Blindwood | 128.67 | -33.8 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 4395 | Nightspill | 120.47 | -21.6 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 4397 | Nightspill | 118.82 | -24.0 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 4398 | Nightspill | 117.32 | -19.0 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 4399 | Nightspill | 118.21 | -16.6 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 4816 | South Crags | 117.6 | -23.3 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 4817 | South Crags | 119.88 | -25.5 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 4818 | South Crags | 119.95 | -24.7 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 4819 | Hanging Wood | 117.73 | -21.7 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 4838 | Hanging Wood | 117.73 | -21.7 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 4842 | Hanging Wood | 119.95 | -24.4 | D | AB_RockyCrags:2 | AB_RockyCrags (Forsaken Crags) |  |
| 4988 | Nightspill | 123.1 | -32.2 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 4989 | Nightspill | 120.44 | -29.5 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 4990 | Nightspill | 119.23 | -27.5 | I(d3) | — | AB_MycoticJungle (the Rot) |  |
| 4991 | Nightspill | 120.63 | -28.4 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 4992 | Nightspill | 123.3 | -32.6 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 4994 | Nightspill | 120.03 | -29.8 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 4996 | Nightspill | 118.95 | -28.1 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 5202 | Frostcaps | 116.86 | -20.1 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 5314 | Sporefields | 90.0 | 12.6 | I(d1) | — | Desert |  |
| 5316 | Sporefields | 92.23 | 9.6 | I(d1) | — | Desert |  |
| 5318 | Sporefields | 94.54 | 7.3 | D | Desert:2 | Desert |  |
| 5320 | Sporefields | 96.77 | 4.6 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 5321 | Sporefields | 99.07 | 1.7 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 5632 | South Crags | 114.55 | -23.3 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 5633 | South Crags | 116.86 | -26.9 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 5648 | Sweatwood | 83.34 | 16.5 | I(d2) | — | Desert | TIE |
| 5649 | Sweatwood | 84.63 | 14.4 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 5650 | Sweatwood | 84.73 | 15.7 | I(d1) | — | Desert |  |
| 5651 | Stepwood | 87.36 | 12.9 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 5654 | Sweatwood | 80.61 | 16.9 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 5656 | Sweatwood | 83.29 | 14.8 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 5946 | South Crags | 122.03 | -29.5 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 5947 | South Crags | 124.27 | -31.1 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 6044 | Stillwood | 125.73 | -34.0 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 6048 | Frostcaps | 121.43 | -28.0 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 6049 | Frostcaps | 123.71 | -30.7 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 6056 | Frostcaps | 123.95 | -30.2 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 6057 | Stillwood | 126.19 | -33.7 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 6059 | Frostcaps | 121.88 | -27.4 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 6061 | Stillwood | 126.37 | -33.7 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 6062 | Stillwood | 128.58 | -37.5 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 6068 | Stillwood | 130.66 | -40.9 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 6069 | Stillwood | 132.87 | -43.9 | D | AB_MycoticJungle:2, RUT_NightsideIce:1 | AB_MycoticJungle (the Rot) |  |
| 6073 | Stillwood | 128.58 | -37.3 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 7286 | Nightspill | 119.15 | -25.4 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 7287 | Nightspill | 116.47 | -21.6 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 7288 | Nightspill | 115.23 | -20.9 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 7289 | Nightspill | 116.62 | -23.5 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 7290 | Nightspill | 119.29 | -26.4 | I(d3) | — | AB_MycoticJungle (the Rot) |  |
| 7291 | Nightspill | 120.59 | -27.9 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 7532 | Nightspill | 100.69 | -4.6 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 7533 | Nightspill | 102.03 | -6.2 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 7534 | Nightspill | 103.31 | -8.1 | D | AB_MycoticJungle:4 | AB_MycoticJungle (the Rot) |  |
| 7556 | Sweatwood | 76.69 | 21.6 | I(d1) | — | Desert |  |
| 7557 | Sweatwood | 76.77 | 22.2 | D | Desert:2 | Desert |  |
| 7558 | Sweatwood | 78.11 | 21.5 | D | Desert:2 | Desert |  |
| 7559 | Sweatwood | 79.37 | 20.2 | I(d1) | — | Desert |  |
| 7560 | Sweatwood | 77.97 | 20.4 | I(d2) | — | Desert | TIE |
| 7561 | Sweatwood | 79.31 | 19.4 | I(d2) | — | Desert |  |
| 7624 | Stillwood | 129.61 | -39.0 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 7625 | Stillwood | 128.78 | -37.8 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 7626 | Stillwood | 131.06 | -40.9 | D | RUT_NightsideIce:1 | RUT_NightsideIce (the deep-night highland) |  |
| 7627 | Stillwood | 131.69 | -41.9 | D | RUT_NightsideIce:3, AB_MycoticJungle:1 | RUT_NightsideIce (the deep-night highland) |  |
| 7874 | Sporefields | 97.19 | 2.8 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 7875 | Sporefields | 98.01 | 2.0 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 7876 | Sporefields | 95.77 | 4.7 | I(d3) | — | AB_MycoticJungle (the Rot) |  |
| 7877 | Sporefields | 95.13 | 5.8 | I(d3) | — | AB_MycoticJungle (the Rot) |  |
| 7878 | Sporefields | 97.38 | 3.2 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 7879 | Sporefields | 95.92 | 5.1 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 8253 | Frostcaps | 118.77 | -22.8 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 8257 | Frostcaps | 117.94 | -21.9 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 8594 | South Crags | 116.47 | -24.7 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 8595 | South Crags | 115.82 | -23.3 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 8596 | South Crags | 117.94 | -26.7 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 8597 | South Crags | 118.77 | -27.1 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 8598 | South Crags | 118.13 | -25.7 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 8599 | South Crags | 116.65 | -23.9 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 8618 | South Crags | 125.11 | -32.7 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 8619 | South Crags | 123.65 | -30.8 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 8620 | South Crags | 122.93 | -29.0 | I(d2) | — | AB_RockyCrags (Forsaken Crags) | TIE |
| 8621 | South Crags | 123.65 | -30.2 | I(d1) | — | BiomeGRimond (Blue Desert) | TIE |
| 8622 | South Crags | 125.11 | -32.5 | I(d1) | — | BiomeGRimond (Blue Desert) |  |
| 8623 | South Crags | 125.84 | -33.6 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 8770 | Nightspill | 113.95 | -21.3 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 8772 | Nightspill | 115.27 | -22.8 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 8773 | Nightspill | 115.22 | -23.5 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 8799 | Nightspill | 124.63 | -33.8 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 8955 | Sporefields | 91.38 | 10.8 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 8957 | Sporefields | 88.62 | 14.0 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 8958 | Sporefields | 90.71 | 11.6 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 8959 | Sporefields | 89.29 | 13.5 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 8968 | Sporefields | 94.47 | 6.6 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 8969 | Sporefields | 95.29 | 5.6 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 8971 | Sporefields | 96.61 | 3.9 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 9251 | Blindwood | 127.36 | -32.0 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 9253 | Blindwood | 127.86 | -32.0 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 9255 | Nightspill | 120.72 | -23.7 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 9256 | Nightspill | 119.91 | -25.3 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 9257 | Nightspill | 118.6 | -21.3 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 9258 | Nightspill | 118.4 | -19.6 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 9259 | Nightspill | 119.45 | -20.6 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 9676 | South Crags | 118.39 | -23.6 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 9677 | South Crags | 119.17 | -24.0 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 9678 | Hanging Wood | 118.46 | -22.6 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 9698 | Hanging Wood | 118.46 | -22.4 | D | AB_RockyCrags:2 | AB_RockyCrags (Forsaken Crags) |  |
| 9699 | Hanging Wood | 116.96 | -20.9 | D | AB_RockyCrags:2, AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) | TIE |
| 9848 | Nightspill | 121.82 | -31.0 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 9849 | Nightspill | 120.53 | -29.4 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 9850 | Nightspill | 120.59 | -28.9 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 9851 | Nightspill | 121.95 | -30.8 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 9852 | Nightspill | 123.26 | -32.3 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 9853 | Nightspill | 123.19 | -32.4 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 9856 | Nightspill | 118.8 | -27.9 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 9857 | Nightspill | 117.57 | -27.0 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 10174 | Sporefields | 90.75 | 11.6 | D | Desert:1 | Desert |  |
| 10175 | Sporefields | 89.25 | 13.3 | D | Desert:3 | Desert |  |
| 10176 | Sporefields | 91.5 | 10.7 | D | Desert:3 | Desert |  |
| 10178 | Sporefields | 96.05 | 5.7 | I(d1) | — | Desert | TIE |
| 10179 | Sporefields | 95.32 | 7.0 | D | Desert:2 | Desert |  |
| 10180 | Sporefields | 97.56 | 4.1 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 10181 | Sporefields | 98.35 | 2.9 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 10182 | Sporefields | 97.63 | 3.8 | D | AB_MycoticJungle:2, Desert:1 | AB_MycoticJungle (the Rot) |  |
| 10183 | Sporefields | 96.1 | 5.8 | D | Desert:3 | Desert |  |
| 10493 | South Crags | 116.0 | -25.4 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 10508 | Sweatwood | 84.65 | 14.8 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 10509 | Stepwood | 85.98 | 13.1 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 10510 | Sweatwood | 84.68 | 15.3 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 10511 | Stepwood | 86.02 | 14.1 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 10512 | Stepwood | 87.33 | 12.6 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 10513 | Stepwood | 87.32 | 12.2 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 10514 | Sweatwood | 80.61 | 16.7 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 10516 | Sweatwood | 81.95 | 15.6 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 10904 | Frostcaps | 124.88 | -33.0 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 10908 | Frostcaps | 122.86 | -30.0 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 10909 | Frostcaps | 124.3 | -32.0 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 10916 | Frostcaps | 123.33 | -29.1 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 10917 | Frostcaps | 124.77 | -31.4 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 10921 | Stillwood | 125.58 | -32.8 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 10928 | Stillwood | 131.43 | -41.8 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 10929 | Stillwood | 132.19 | -42.5 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 10932 | Stillwood | 129.34 | -38.3 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 10933 | Stillwood | 130.0 | -39.7 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 12146 | Nightspill | 119.22 | -25.7 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 12147 | Nightspill | 117.84 | -23.6 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 12148 | Nightspill | 116.54 | -22.1 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 12149 | Nightspill | 116.59 | -22.6 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 12150 | Nightspill | 117.94 | -24.5 | I(d3) | — | AB_MycoticJungle (the Rot) |  |
| 12151 | Nightspill | 119.27 | -26.0 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 12496 | Nightspill | 119.24 | -17.8 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 13095 | Nightspill | 121.43 | -31.2 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 13096 | Nightspill | 122.97 | -32.1 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 13097 | Nightspill | 121.71 | -30.8 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 13098 | Nightspill | 120.19 | -29.4 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 13099 | Nightspill | 120.33 | -29.5 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 13599 | Nightspill | 99.37 | -2.3 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 13603 | Nightspill | 99.39 | -2.0 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 13604 | Nightspill | 100.72 | -4.0 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 13605 | Nightspill | 102.05 | -6.1 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 13748 | Sweatwood | 80.74 | 19.6 | I(d1) | — | Desert |  |
| 13749 | Sweatwood | 82.03 | 18.0 | I(d1) | — | Desert |  |
| 13750 | Sweatwood | 80.83 | 20.0 | D | Desert:3 | Desert |  |
| 13752 | Sweatwood | 83.38 | 16.8 | I(d1) | — | Desert |  |
| 13753 | Sweatwood | 83.45 | 17.1 | D | Desert:2 | Desert |  |
| 13754 | Sweatwood | 80.63 | 18.1 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 13755 | Sweatwood | 80.61 | 17.5 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 13756 | Sweatwood | 81.99 | 17.5 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 13757 | Sweatwood | 83.31 | 16.0 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 13758 | Sweatwood | 81.95 | 16.1 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 13759 | Sweatwood | 83.29 | 15.6 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 13761 | Sweatwood | 75.39 | 22.8 | D | Desert:1 | Desert |  |
| 13764 | Sweatwood | 74.02 | 24.0 | D | Desert:2, AB_MycoticJungle:2 | Desert | TIE |
| 13765 | Sweatwood | 75.34 | 22.8 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 13766 | Sweatwood | 76.63 | 21.2 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 13767 | Sweatwood | 77.95 | 19.9 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 13768 | Sweatwood | 79.28 | 18.3 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 13769 | Sweatwood | 79.27 | 18.1 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 14144 | Stillwood | 127.38 | -35.7 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 14145 | Stillwood | 126.57 | -35.0 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 14146 | Stillwood | 125.14 | -32.8 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 14147 | Frostcaps | 124.55 | -31.4 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 14148 | Stillwood | 125.38 | -32.3 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 14149 | Stillwood | 126.79 | -34.4 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 14152 | Stillwood | 127.16 | -36.2 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 14153 | Stillwood | 126.32 | -35.0 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 14156 | Stillwood | 127.61 | -36.0 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 14157 | Stillwood | 129.03 | -38.3 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 14158 | Stillwood | 127.0 | -35.1 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 14159 | Stillwood | 127.8 | -36.2 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 14160 | Stillwood | 129.22 | -38.6 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 14161 | Stillwood | 129.86 | -39.4 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 14162 | Stillwood | 131.3 | -41.6 | D | AB_MycoticJungle:2, RUT_NightsideIce:1 | AB_MycoticJungle (the Rot) |  |
| 14163 | Stillwood | 131.93 | -42.3 | D | RUT_NightsideIce:3 | RUT_NightsideIce (the deep-night highland) |  |
| 14169 | Stillwood | 129.86 | -39.7 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 14170 | Stillwood | 129.22 | -38.5 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 14171 | Stillwood | 127.8 | -36.3 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 14172 | Stillwood | 127.0 | -35.4 | D | AB_MycoticJungle:4 | AB_MycoticJungle (the Rot) |  |
| 14176 | Stillwood | 131.3 | -42.0 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 14177 | Stillwood | 132.1 | -43.0 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 15360 | Nightspill | 117.76 | -23.2 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 15361 | Nightspill | 116.38 | -21.7 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 15386 | Nightspill | 115.09 | -20.5 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 15390 | Nightspill | 115.17 | -20.5 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 15391 | Nightspill | 113.86 | -19.1 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 15572 | Sporefields | 85.05 | 17.6 | D | AB_MycoticJungle:2, Desert:1 | AB_MycoticJungle (the Rot) |  |
| 15576 | Sporefields | 87.23 | 15.4 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 15577 | Sporefields | 86.46 | 16.4 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 15578 | Sporefields | 87.12 | 16.0 | I(d1) | — | Desert |  |
| 15579 | Sporefields | 86.34 | 16.5 | D | Desert:3 | Desert |  |
| 15580 | Sporefields | 88.56 | 14.4 | I(d1) | — | Desert |  |
| 15581 | Sporefields | 89.27 | 13.3 | I(d1) | — | Desert |  |
| 15582 | Sporefields | 88.52 | 14.0 | D | Desert:2 | Desert |  |
| 15644 | Sporefields | 94.95 | 5.7 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 15645 | Sporefields | 93.54 | 7.5 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 15646 | Sporefields | 93.39 | 8.2 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 15647 | Sporefields | 92.77 | 8.9 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 15648 | Sporefields | 94.74 | 6.2 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 15649 | Sporefields | 95.54 | 4.9 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 15650 | Sporefields | 96.91 | 3.1 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 15651 | Sporefields | 97.75 | 2.1 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 15652 | Sporefields | 97.44 | 2.6 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 15655 | Sporefields | 99.14 | 0.6 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 15656 | Sporefields | 93.66 | 7.7 | I(d3) | — | Desert |  |
| 15657 | Sporefields | 92.96 | 8.6 | I(d2) | — | Desert |  |
| 15658 | Sporefields | 92.88 | 8.3 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 15659 | Sporefields | 91.44 | 10.4 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 15660 | Sporefields | 90.73 | 11.5 | I(d2) | — | Desert |  |
| 15661 | Sporefields | 91.48 | 10.6 | I(d1) | — | Desert |  |
| 15662 | Sporefields | 95.21 | 6.2 | I(d2) | — | Desert | TIE |
| 15663 | Sporefields | 95.99 | 5.2 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 15664 | Sporefields | 93.72 | 8.0 | I(d1) | — | Desert |  |
| 15665 | Sporefields | 93.0 | 8.9 | D | Desert:1 | Desert |  |
| 15666 | Sporefields | 93.76 | 8.1 | D | Desert:2 | Desert |  |
| 15667 | Sporefields | 95.27 | 6.2 | I(d1) | — | Desert |  |
| 15668 | Sporefields | 99.99 | -1.0 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 15669 | Sporefields | 99.42 | -0.3 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 15673 | Mould Marches | 100.25 | -1.1 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 15675 | Sporefields | 98.17 | 2.3 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 15676 | Sporefields | 97.48 | 3.4 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 15922 | Sweatwood | 84.78 | 15.8 | D | Desert:2 | Desert |  |
| 15924 | Stepwood | 86.06 | 14.3 | I(d1) | — | Desert | TIE |
| 15925 | Stepwood | 87.39 | 13.1 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 17376 | Blindwood | 128.1 | -33.3 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 17377 | Blindwood | 129.44 | -35.4 | D | BiomeGRimond:1, AB_PropaneLakes:1, AB_MycoticJungle:1 | BiomeGRimond (Blue Desert) | TIE |
| 17378 | Blindwood | 130.03 | -35.8 | D | BiomeGRimond:1 | BiomeGRimond (Blue Desert) |  |
| 17379 | Blindwood | 131.41 | -37.3 | D | BiomeGRimond:4 | BiomeGRimond (Blue Desert) |  |
| 17380 | Blindwood | 129.2 | -34.1 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 17381 | Blindwood | 129.66 | -34.5 | D | AB_MycoticJungle:3, BiomeGRimond:1 | AB_MycoticJungle (the Rot) |  |
| 17517 | Nightspill | 116.19 | -18.9 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 17518 | Nightspill | 117.7 | -22.3 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 17519 | Nightspill | 117.5 | -20.1 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 17524 | Nightspill | 116.04 | -17.2 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 17525 | Nightspill | 117.15 | -15.8 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 17855 | Sporefields | 99.86 | 0.7 | D | AB_MycoticJungle:4 | AB_MycoticJungle (the Rot) |  |
| 17931 | Frostcaps | 116.25 | -18.9 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 17936 | Frostcaps | 118.55 | -23.2 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 17937 | Frostcaps | 120.0 | -25.8 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 17938 | Frostcaps | 117.71 | -21.9 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 17939 | Frostcaps | 118.3 | -23.1 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 17942 | Frostcaps | 121.06 | -26.0 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 17943 | Frostcaps | 120.23 | -25.0 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 17944 | Frostcaps | 120.84 | -26.6 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 17945 | Frostcaps | 122.28 | -28.7 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 17946 | Frostcaps | 123.12 | -29.5 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 17947 | Frostcaps | 122.51 | -28.3 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 17969 | Stillwood | 125.72 | -32.5 | D | AB_MycoticJungle:4 | AB_MycoticJungle (the Rot) |  |
| 17970 | Stillwood | 127.15 | -35.0 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 17971 | Stillwood | 127.92 | -36.2 | D | AB_MycoticJungle:4 | AB_MycoticJungle (the Rot) |  |
| 17981 | Stillwood | 127.92 | -35.8 | D | AB_MycoticJungle:4 | AB_MycoticJungle (the Rot) |  |
| 19970 | South Crags | 115.98 | -22.0 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 19971 | South Crags | 116.79 | -22.6 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 19976 | South Crags | 114.16 | -21.5 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 19977 | South Crags | 115.63 | -23.9 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 19978 | South Crags | 113.95 | -22.1 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 19980 | South Crags | 115.41 | -24.4 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 19981 | South Crags | 116.25 | -25.8 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 19982 | South Crags | 117.71 | -27.9 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 19983 | South Crags | 118.55 | -28.1 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 19984 | South Crags | 118.3 | -28.4 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 19987 | South Crags | 120.0 | -29.3 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 19988 | South Crags | 120.84 | -29.4 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 19989 | South Crags | 120.23 | -28.6 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 19993 | South Crags | 121.06 | -29.2 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 19994 | South Crags | 120.42 | -28.4 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 19995 | South Crags | 118.95 | -26.3 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 19996 | South Crags | 118.28 | -25.0 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 19997 | South Crags | 119.08 | -25.4 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 19998 | South Crags | 121.23 | -29.2 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 19999 | South Crags | 120.56 | -27.4 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 20108 | South Crags | 122.9 | -29.5 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 20109 | South Crags | 121.43 | -26.7 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 20110 | South Crags | 121.35 | -27.8 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 20111 | South Crags | 120.66 | -26.3 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 20112 | South Crags | 122.82 | -29.9 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 20113 | South Crags | 123.6 | -30.6 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 20114 | South Crags | 121.45 | -26.7 | I(d2) | — | AB_RockyCrags (Forsaken Crags) |  |
| 20115 | South Crags | 120.71 | -25.7 | I(d1) | — | AB_RockyCrags (Forsaken Crags) |  |
| 20116 | South Crags | 120.71 | -25.6 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 20117 | Hanging Wood | 119.22 | -23.6 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 20118 | Hanging Wood | 118.48 | -22.7 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 20119 | Hanging Wood | 119.22 | -23.7 | I(d1) | — | AB_MycoticJungle (the Rot) | TIE |
| 20120 | South Crags | 122.9 | -28.7 | D | AB_RockyCrags:2 | AB_RockyCrags (Forsaken Crags) |  |
| 20122 | South Crags | 121.43 | -26.6 | D | AB_RockyCrags:2 | AB_RockyCrags (Forsaken Crags) |  |
| 20126 | South Crags | 125.81 | -33.3 | D | BiomeGRimond:2, AB_MycoticJungle:1 | BiomeGRimond (Blue Desert) |  |
| 20132 | South Crags | 127.28 | -35.2 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 20133 | South Crags | 127.98 | -35.1 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 20134 | South Crags | 127.98 | -35.7 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 20138 | South Crags | 125.05 | -31.9 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 20139 | South Crags | 125.81 | -32.8 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 20140 | South Crags | 127.24 | -33.7 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 21008 | Nightspill | 116.51 | -25.1 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 21009 | Nightspill | 117.87 | -26.2 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 21010 | Nightspill | 119.07 | -28.5 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 21011 | Nightspill | 119.16 | -28.0 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 21012 | Nightspill | 117.69 | -27.0 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 21013 | Nightspill | 116.43 | -25.4 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 21033 | Nightspill | 113.96 | -20.7 | D | AB_MycoticJungle:1 | AB_MycoticJungle (the Rot) |  |
| 21034 | Nightspill | 113.91 | -19.8 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 21036 | Nightspill | 115.27 | -21.4 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 21037 | Nightspill | 115.29 | -22.0 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 21038 | Nightspill | 116.63 | -23.5 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 21039 | Nightspill | 116.61 | -23.6 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 21040 | Nightspill | 117.92 | -25.7 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 21041 | Nightspill | 119.28 | -26.9 | I(d3) | — | AB_MycoticJungle (the Rot) |  |
| 21042 | Nightspill | 117.96 | -25.0 | I(d3) | — | AB_MycoticJungle (the Rot) |  |
| 21043 | Nightspill | 119.3 | -26.6 | I(d3) | — | AB_MycoticJungle (the Rot) |  |
| 21188 | Nightspill | 123.31 | -31.6 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 21189 | Nightspill | 123.32 | -32.1 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 21190 | Nightspill | 120.64 | -28.5 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 21191 | Nightspill | 121.97 | -30.6 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 21192 | Nightspill | 120.62 | -28.4 | I(d2) | — | AB_MycoticJungle (the Rot) |  |
| 21193 | Nightspill | 121.95 | -29.9 | I(d1) | — | AB_MycoticJungle (the Rot) |  |
| 21196 | Nightspill | 124.65 | -33.8 | D | AB_MycoticJungle:3 | AB_MycoticJungle (the Rot) |  |
| 21218 | Nightspill | 121.9 | -29.6 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
| 21223 | Nightspill | 120.53 | -27.3 | D | AB_MycoticJungle:2 | AB_MycoticJungle (the Rot) |  |
