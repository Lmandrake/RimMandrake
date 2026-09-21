# World label size hierarchy — the offline half

`WORLD_LABEL_SIZE_HIERARCHY_1` · 2026-09-21 · **offline only: no savegame written, no
bridge call, no game touched.**

Owner ruling, 2026-09-21: *"size the whole planet."*

---

## 1. Instruments, and whether they agree

| what | instrument | result |
|---|---|---|
| the 71 features | the canonical save's `<features>` block, `xml.etree.ElementTree` on the block taken to the **LAST** `</features>` | 71 features, all `WB_MapLabelFeature`, **all at `maxDrawSizeInTiles = 10`**, 0 unnamed — the briefed figures confirmed |
| tile → feature | the save's own **`tileFeatureDeflate`** array (raw-DEFLATE, 43,744 bytes = 21,872 × `ushort`) | every one of the 21,872 tiles is assigned; **0 tiles unassigned** (no `0xFFFF`); 71 distinct values |
| tile adjacency | `world/world_neighbors_sub7b.csv` — the **engine's own** neighbour dump (`jawa/world_neighbors`), the same file `worldgeom.py` uses | degree histogram **exactly 12 pentagons / 21,860 hexagons**, which is the geodesic-sphere invariant. The graph is sound. |
| tile positions | `world/world_tiles_sub7b.csv` — engine dump (`jawa/world_tile_export`) | measured **median tile spacing 1.4924°** (mean 1.4759°) |
| cross-check on membership | `world/ASHKARR_WORLDMAP_tiles.csv` `region` column — ⚠️ **a RECORD exported 2026-09-12, used as a cross-check only, never as the planet** | **exact agreement: all 71 names present, Jaccard = 1.000 on all 71.** Not "close" — identical tile sets. |

🔑 **`ashkarr_paint.py` was checked and rejected as the cross-check instrument.** Its 15
`regions.append(...)` calls do not carry stored tile arrays — they recompute membership
from procedural predicates (`arc < 20`, ridge distances, sea-component ids) — and the
names are pre-split: it still says **`The Fall Line Barrens`**, the name the owner
replaced with `The Breaks` on 2026-09-12. It describes an earlier paint, not this planet.
The record CSV is the cross-check that exists, and it agrees perfectly.

### 🔴 A real defect found and fixed on the way: `tileFeature` holds the uniqueID

`worldmap.py`'s own comment said the array was an *index into the features list*. It is
not — it holds the feature's **`uniqueID`**, and on this save those run **21..92** while
the list positions run 0..70. So `worldview.py`, which joined
`feature_idx == f["index"]`, was **labelling the wrong regions** on every Ash'karr
render: the first 21 features matched 0 tiles and were silently dropped (`len(idx) < 8`),
and the rest picked up some other region's tiles. Its `report.json` per-region tile
counts were wrong the same way.

Fixed in this change: `worldmap.features()` now returns `uid`, and `worldview.PlanetView`
remaps `feature_idx` into list-position space once, at load. ✅ The fix is
cross-validating — the renderer's report now independently reproduces my tile counts
(Deadstone 2051, Dune Sea 1692, Glare 879), from a different code path.

### ⚠️ One measured correction to the Fall Line spec

`design/Jawa/worldbuilding/fall_line_major_region_label.md` gives mean tile spacing as
**1.373°** and the Fall Line's span as **20.3 tiles**. The degrees agree (27.84°, which I
reproduce), but 1.373° is `sqrt(4π/21872)` — the spacing of *square* cells. Hexagons pack
at `sqrt(area / (√3/2))`, giving **1.4757°**, and the engine graph measures **1.4924°
median**. So the Fall Line spans **18.7 tiles, not 20.3**. That file has been corrected.

---

## 2. Vanilla's own formula, applied literally

MEASURED from the engine (`RimWorld/FeatureWorker.cs`, `AssignBestDrawPos`, and
`Verse/WorldFloodFiller.cs`): the flood fill is seeded from **every edge tile at
traversal distance 0**, `bestTileDist` is the deepest distance reached, and

```
maxDrawSizeInTiles = bestTileDist * 2f * 1.2f
```

so it is **1.2 × the inscribed diameter**. An edge tile is one with a neighbour outside
the region (or on a layer edge — no tile is, on a closed planet). I implemented exactly
that: BFS from the edge set, roots at 0, over the engine's neighbour graph.

🔴 **Applied literally it does not deliver the ruled ask, and the report has to say so.**

- Range **2.4 … 33.6**. But `EffectiveDrawSizeCurve` is flat at 15 for anything ≤ 10, so
  **48 of the 71 regions still draw at the floor** — visually unchanged from today.
- It **inverts** the order the eye expects, because it measures *fatness*, not extent:
  **Ammonia Flats (818 tiles) → 33.6**, the largest on the planet, while
  **Deadstone (2,051 tiles) → 19.2** and **Gray Crags (577 tiles) → 9.6**, i.e. still
  the floor. A long or crooked region is punished for its shape.
- For the Fall Line it produces **7.2 → effective 15**: literally no change at all.

That is not a bug in my implementation — it is what vanilla does, and on a vanilla planet
it is fine, because vanilla features are sparse blobs on an unnamed sea of tiles. Our
planet is **fully partitioned**: all 21,872 tiles carry one of 71 authored names. The
routine was never asked this question.

---

## 3. The proposed curve: vanilla's formula, with a shape-independent inradius

Keep vanilla's constants and its meaning — `1.2 × inscribed diameter` — and estimate the
inradius from the region's **area** instead of its narrowest waist. A hex disc of `r`
rings holds `3r² + 3r + 1` tiles, so

```
r_eff = (-3 + sqrt(12·N - 3)) / 6                     N = the region's tile count
maxDrawSizeInTiles = r_eff * 2 * 1.2                  vanilla's own expression
effectiveDrawSize  = EffectiveDrawSizeCurve(maxDrawSizeInTiles)
```

It is a **curve, not a table** — a region authored next year gets a size from its tile
count with no hand edit — and it is what the item's own spec asks for (*"derive each
feature's `maxDrawSizeInTiles` from its tile count"*).

Why not the two alternatives I also computed:

| candidate | range | above the floor | why not |
|---|---|---|---|
| vanilla-literal, `inradius × 2.4` | 2.4 … 33.6 | 23 of 71 | §2 — 48 regions unchanged, order inverted |
| `max span × 1.2` | 6.6 … 94.7 | 70 of 71 | rewards **fragmentation**. 8 regions are in more than one piece (Salt is in **7**), and 63-tile **Pyrelands**, scattered across 51 tiles of sphere, would outrank 500-tile regions at 61.2 |
| **area-equivalent inradius × 2.4** | **4.3 … 61.5** | **60 of 71** | ✅ monotone in extent, immune to shape and to fragmentation, vanilla's constants |

---

## 4. The Fall Line: ruled 26 vs what the formula gives

| | value | effective |
|---|--:|--:|
| vanilla-literal (inradius 3) | 7.2 | 15.0 |
| **proposed curve** (155 tiles) | **16.0** | **25.0** |
| `max span × 1.2` (18.7 tiles) | 22.4 | 35.7 |
| 🔴 **owner-ruled, applied, photographed** | **26.0** | **42.0** |

**They differ, and I am not reconciling them by moving either one.**

The ruled 26 is **1.6× what the curve gives** (16.0), and 3.6× what vanilla-literal
gives. The reason is visible in the data: the Fall Line is **155 tiles — 38th of 71 by
area**. By extent alone it is a middling region. The owner did not ask for it to be
sized; he asked for it to be **major** (*"Definite put fall line as a major world region
with beautiful clear label"*). 26 is a **deliberate promotion above the curve**, not a
data point on it.

✅ **Recommendation: keep the ruled 26 as an explicit override, and say in the record that
it is one.** It is already applied live, already saved to
`ASHKARR_FALLLINE_LABEL26_2026-09-21`, and already judged by eye. The table below and
`proposed_sizes.json` carry 26 for the Fall Line and the curve's value for the other 70.
⛔ I have not bent the curve toward 26 and have not moved 26 toward the curve.

---

## 5. All 71 regions

`now` is what the canonical save holds today (10 for every one of them). `eff` columns
are `EffectiveDrawSizeCurve` — the number the engine actually draws with
(`WorldFeatures.cs`: `texts[i].Size = EffectiveDrawSize * averageTileSize`, i.e. a
label's width on the globe is its effective size **in tiles**).
🔴 = the owner-ruled override.

| # | region | tiles | pieces | inradius | span (tiles) | now | eff now | vanilla-literal | eff | **proposed** | **eff** |
|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 1 | Deadstone | 2051 | 1 | 8 | 78.9 | 10 | 15 | 19.2 | 30.3 | **61.5** | **103.8** |
| 2 | Dune Sea | 1692 | 1 | 8 | 53.6 | 10 | 15 | 19.2 | 30.3 | **55.8** | **97.0** |
| 3 | Glare | 879 | 1 | 7 | 58.0 | 10 | 15 | 16.8 | 26.3 | **39.9** | **69.8** |
| 4 | Kiln | 878 | 1 | 6 | 60.5 | 10 | 15 | 14.4 | 22.3 | **39.9** | **69.8** |
| 5 | Nightspill | 853 | 1 | 7 | 72.5 | 10 | 15 | 16.8 | 26.3 | **39.3** | **68.6** |
| 6 | Twilight Sea | 852 | 1 | 11 | 42.4 | 10 | 15 | 26.4 | 42.8 | **39.2** | **68.4** |
| 7 | Ammonia Flats | 818 | 1 | 14 | 29.4 | 10 | 15 | 33.6 | 57.2 | **38.4** | **66.8** |
| 8 | Umbra | 802 | 1 | 9 | 37.4 | 10 | 15 | 21.6 | 34.3 | **38.0** | **66.0** |
| 9 | Sunreach | 795 | 2 | 8 | 72.5 | 10 | 15 | 19.2 | 30.3 | **37.9** | **65.8** |
| 10 | Long Sand | 721 | 1 | 9 | 58.1 | 10 | 15 | 21.6 | 34.3 | **36.0** | **62.0** |
| 11 | Grey Sea | 617 | 1 | 9 | 41.5 | 10 | 15 | 21.6 | 34.3 | **33.2** | **56.4** |
| 12 | Gray Crags | 577 | 1 | 4 | 61.7 | 10 | 15 | 9.6 | 15.0 | **32.1** | **54.2** |
| 13 | Thornbelt | 502 | 1 | 7 | 46.6 | 10 | 15 | 16.8 | 26.3 | **29.8** | **49.6** |
| 14 | Dew Horn | 491 | 1 | 5 | 43.2 | 10 | 15 | 12.0 | 18.3 | **29.5** | **49.0** |
| 15 | Sootreach | 433 | 1 | 4 | 47.8 | 10 | 15 | 9.6 | 15.0 | **27.6** | **45.2** |
| 16 | Dry Marches | 387 | 1 | 5 | 36.3 | 10 | 15 | 12.0 | 18.3 | **26.0** | **42.0** |
| 17 | Twilight Crags | 384 | 3 | 4 | 55.7 | 10 | 15 | 9.6 | 15.0 | **25.9** | **41.8** |
| 18 | Dew Belt | 362 | 4 | 7 | 41.3 | 10 | 15 | 16.8 | 26.3 | **25.2** | **40.4** |
| 19 | Combs | 360 | 1 | 6 | 32.6 | 10 | 15 | 14.4 | 22.3 | **25.1** | **40.2** |
| 20 | Anvil | 349 | 2 | 5 | 26.7 | 10 | 15 | 12.0 | 18.3 | **24.7** | **39.5** |
| 21 | Rimewall | 338 | 1 | 3 | 44.4 | 10 | 15 | 7.2 | 15.0 | **24.3** | **38.8** |
| 22 | Ashfall Range | 324 | 1 | 4 | 34.5 | 10 | 15 | 9.6 | 15.0 | **23.7** | **37.8** |
| 23 | Scald | 312 | 1 | 8 | 21.8 | 10 | 15 | 19.2 | 30.3 | **23.3** | **37.2** |
| 24 | Sinkground | 276 | 1 | 4 | 34.5 | 10 | 15 | 9.6 | 15.0 | **21.8** | **34.7** |
| 25 | Sporefields | 255 | 1 | 5 | 28.2 | 10 | 15 | 12.0 | 18.3 | **20.9** | **33.2** |
| 26 | Frostcaps | 254 | 1 | 5 | 26.0 | 10 | 15 | 12.0 | 18.3 | **20.9** | **33.2** |
| 27 | Salt | 249 | 7 | 3 | 34.6 | 10 | 15 | 7.2 | 15.0 | **20.7** | **32.8** |
| 28 | Rust Cathedral | 236 | 1 | 5 | 18.5 | 10 | 15 | 12.0 | 18.3 | **20.1** | **31.8** |
| 29 | Scour | 234 | 1 | 4 | 30.6 | 10 | 15 | 9.6 | 15.0 | **20.0** | **31.7** |
| 30 | Damp | 230 | 1 | 3 | 31.2 | 10 | 15 | 7.2 | 15.0 | **19.8** | **31.3** |
| 31 | Cracklands | 227 | 1 | 5 | 25.7 | 10 | 15 | 12.0 | 18.3 | **19.7** | **31.2** |
| 32 | Knuckles | 219 | 1 | 2 | 37.2 | 10 | 15 | 4.8 | 15.0 | **19.3** | **30.5** |
| 33 | Ashen Wastes | 202 | 1 | 6 | 19.2 | 10 | 15 | 14.4 | 22.3 | **18.5** | **29.2** |
| 34 | Cratercrown | 174 | 1 | 2 | 26.2 | 10 | 15 | 4.8 | 15.0 | **17.1** | **26.8** |
| 35 | Glass Reach | 172 | 1 | 2 | 26.7 | 10 | 15 | 4.8 | 15.0 | **17.0** | **26.7** |
| 36 | The Verge | 171 | 1 | 3 | 25.1 | 10 | 15 | 7.2 | 15.0 | **16.9** | **26.5** |
| 37 | Hanging Wood | 165 | 1 | 3 | 25.0 | 10 | 15 | 7.2 | 15.0 | **16.6** | **26.0** |
| 38 | Fall Line 🔴 | 155 | 1 | 3 | 18.7 | 10 | 15 | 7.2 | 15.0 | **26.0** | **42.0** |
| 39 | Sunward Scrub | 154 | 1 | 2 | 35.4 | 10 | 15 | 4.8 | 15.0 | **16.0** | **25.0** |
| 40 | Cinderdark | 153 | 1 | 3 | 25.7 | 10 | 15 | 7.2 | 15.0 | **15.9** | **24.8** |
| 41 | The Breaks | 153 | 2 | 3 | 21.2 | 10 | 15 | 7.2 | 15.0 | **15.9** | **24.8** |
| 42 | Slough | 148 | 1 | 3 | 24.3 | 10 | 15 | 7.2 | 15.0 | **15.6** | **24.3** |
| 43 | Blindwood | 145 | 1 | 2 | 28.6 | 10 | 15 | 4.8 | 15.0 | **15.5** | **24.2** |
| 44 | Stillwood | 142 | 1 | 3 | 24.9 | 10 | 15 | 7.2 | 15.0 | **15.3** | **23.8** |
| 45 | Blight | 140 | 1 | 3 | 23.1 | 10 | 15 | 7.2 | 15.0 | **15.2** | **23.7** |
| 46 | Tallow Ground | 129 | 1 | 3 | 20.9 | 10 | 15 | 7.2 | 15.0 | **14.5** | **22.5** |
| 47 | Mould Marches | 123 | 1 | 3 | 21.1 | 10 | 15 | 7.2 | 15.0 | **14.2** | **22.0** |
| 48 | Cinders | 112 | 1 | 3 | 19.0 | 10 | 15 | 7.2 | 15.0 | **13.4** | **20.7** |
| 49 | Sweatwood | 93 | 1 | 4 | 11.8 | 10 | 15 | 9.6 | 15.0 | **12.1** | **18.5** |
| 50 | Scorch | 90 | 3 | 1 | 24.0 | 10 | 15 | 2.4 | 15.0 | **11.9** | **18.2** |
| 51 | Stepwood | 85 | 1 | 3 | 14.9 | 10 | 15 | 7.2 | 15.0 | **11.6** | **17.7** |
| 52 | Fever Wood | 81 | 1 | 3 | 14.4 | 10 | 15 | 7.2 | 15.0 | **11.3** | **17.2** |
| 53 | Grinding Floor | 79 | 1 | 1 | 21.5 | 10 | 15 | 2.4 | 15.0 | **11.1** | **16.8** |
| 54 | Pan | 79 | 1 | 2 | 16.4 | 10 | 15 | 4.8 | 15.0 | **11.1** | **16.8** |
| 55 | Capwood | 75 | 1 | 2 | 14.1 | 10 | 15 | 4.8 | 15.0 | **10.8** | **16.3** |
| 56 | Fuelmere | 72 | 1 | 1 | 21.9 | 10 | 15 | 2.4 | 15.0 | **10.5** | **15.8** |
| 57 | Wither | 72 | 1 | 2 | 13.1 | 10 | 15 | 4.8 | 15.0 | **10.5** | **15.8** |
| 58 | Fanground | 70 | 1 | 3 | 13.1 | 10 | 15 | 7.2 | 15.0 | **10.4** | **15.7** |
| 59 | Ashwood | 69 | 1 | 2 | 13.9 | 10 | 15 | 4.8 | 15.0 | **10.3** | **15.5** |
| 60 | Sunshelf | 68 | 1 | 1 | 19.4 | 10 | 15 | 2.4 | 15.0 | **10.2** | **15.3** |
| 61 | Pyrelands | 63 | 2 | 1 | 51.0 | 10 | 15 | 2.4 | 15.0 | **9.8** | **15.0** |
| 62 | Frostvein | 61 | 1 | 2 | 13.9 | 10 | 15 | 4.8 | 15.0 | **9.6** | **15.0** |
| 63 | Pale Flats | 60 | 1 | 2 | 8.7 | 10 | 15 | 4.8 | 15.0 | **9.5** | **15.0** |
| 64 | Chalk Marches | 57 | 1 | 2 | 12.7 | 10 | 15 | 4.8 | 15.0 | **9.2** | **15.0** |
| 65 | Coldstone | 57 | 1 | 2 | 14.4 | 10 | 15 | 4.8 | 15.0 | **9.2** | **15.0** |
| 66 | Lantern Deeps | 57 | 1 | 2 | 13.0 | 10 | 15 | 4.8 | 15.0 | **9.2** | **15.0** |
| 67 | Notch | 56 | 1 | 2 | 18.7 | 10 | 15 | 4.8 | 15.0 | **9.1** | **15.0** |
| 68 | Quiet Ground | 43 | 1 | 1 | 15.0 | 10 | 15 | 2.4 | 15.0 | **7.9** | **15.0** |
| 69 | Hollow Verge | 40 | 1 | 1 | 12.8 | 10 | 15 | 2.4 | 15.0 | **7.5** | **15.0** |
| 70 | The Abandoned Mines | 34 | 1 | 1 | 11.5 | 10 | 15 | 2.4 | 15.0 | **6.8** | **15.0** |
| 71 | Salt Gate | 16 | 1 | 1 | 5.5 | 10 | 15 | 2.4 | 15.0 | **4.3** | **15.0** |


**Proposed range: 4.3 … 61.5** (effective **15 … 103.8**), against a flat 10 (effective
15) today. 60 of 71 rise above the curve's floor; the 11 that do not are the regions
under ~66 tiles, for which the engine cannot draw anything smaller than 15 anyway.

Machine-readable: `D:\Luke\dev\Rimworld\Transient\world_label_hierarchy\proposed_sizes.json`

### Regions in more than one piece (measured on the engine neighbour graph)

8 of 71. This is why extent-by-span was rejected, and it is worth the owner's eye
separately — a label is drawn at one point, so a region in 7 pieces gets one name at the
centroid of all of them.

| region | tiles | pieces | largest piece |
|---|--:|--:|--:|
| Salt | 249 | 7 | 138 |
| Dew Belt | 362 | 4 | 268 |
| Twilight Crags | 384 | 3 | 205 |
| Scorch | 90 | 3 | 58 |
| Sunreach | 795 | 2 | 700 |
| Anvil | 349 | 2 | 333 |
| The Breaks | 153 | 2 | 99 |
| Pyrelands | 63 | 2 | 37 |

---

## 6. The picture

Two renders of the same planet, same projection, same everything but the label sizes.

| | |
|---|---|
| `D:\Luke\dev\Rimworld\Transient\world_label_hierarchy\ashkarr_labels_PROPOSED.png` | **the one to look at** — the proposed hierarchy |
| `D:\Luke\dev\Rimworld\Transient\world_label_hierarchy\ashkarr_labels_CURRENT.png` | the same map as the save stands today, every label at 10 |

(`.svg` beside each, zoomable.) Rendered with
`worldview.py --feature-sizes <json>`, a new option added in this change: it drives label
size off `EffectiveDrawSizeCurve` instead of the renderer's own `5.6·√tiles` heuristic, so
the preview scales the way the engine does.

**What the pair shows.** In CURRENT the region names are the *smallest* text on the map —
routinely smaller than settlement names — so the planet reads as a list of 96 settlements
with no geography behind it. In PROPOSED the eye gets a structure: Deadstone, Ammonia
Flats, Sunreach, Glare and Kiln carry the map, Twilight Sea and Long Sand sit a tier
below, and Notch, Damp, Cinderdark and Blight recede to captions.

⚠️ **Preview caveats, so nothing here is over-read:**
- The label is placed at the region's **centroid**, and the renderer suppresses a name
  whose pixel box collides with one already placed. Several small names — the Fall Line
  among them, next to The Breaks — are therefore *absent* from this render rather than
  small. The engine places labels from the saved `drawCenter`, which is not the centroid.
- This is an equirectangular projection; the engine draws on a globe. Relative sizes are
  faithful, absolute screen crowding is not.
- ⛔ The biome fills come from the offline def dump. Nothing in this pass depends on them.

---

## 7. What I could NOT establish

- **Whether the proposed sizes crowd or collide in the actual game.** That needs the
  bridge and the game, and both are held by another window. The preview is a projection,
  not the renderer that ships.
- **Whether `drawCenter` is right for any region other than the Fall Line and The
  Breaks.** Membership now cross-checks perfectly, but `drawCenter` is a separate saved
  field that vanilla computes as the deepest interior tile; ours were authored. The Fall
  Line spec measured Dune Sea's saved `drawCenter` at 103 units from the nearest tile the
  CSV assigns it — that is a `drawCenter` defect, **not** a membership defect, and this
  pass does not touch it. It is worth its own item: a big label anchored outside its own
  region gets worse, not better, when the label grows.
- **Where the owner wants the ceiling.** The curve tops out at 61.5 → effective 104 for
  Deadstone. Whether a label 104 tiles wide is majestic or absurd is a looking decision,
  and the two PNGs are the material for it.
- **Nothing about the live game.** No bridge call was made; the running game is on a
  different mod set under another window's control.

---

## 8. Read-only, proved

`CANONICAL_ASHKARR_START_2026-09-12.rws` — **17,500,721 bytes, mtime 2026-09-20 07:28:55,
md5 `75be9ecd4764a397e9802d997bb9e0b9`** — unchanged, before and after. It was opened for
reading only; no save of any kind was written by this pass.
