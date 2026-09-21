# The Fall Line as a major world region — the label pass

Owner directive, 2026-09-20, verbatim: *"Definite put fall line as a major world
region with beautiful clear label on worldmap."*

Item: `FALL_LINE_MAJOR_REGION_LABEL_1`.

## 🔴 Why nothing on Ash'karr currently reads as "major"

MEASURED 2026-09-20 from `CANONICAL_ASHKARR_START_2026-09-12.rws`, parsed with
`xml.etree.ElementTree` — the planet carries **71 world features**, every one of them
a `WB_MapLabelFeature`, and **all 71 have `maxDrawSizeInTiles = 10`.**

That is the bottom of the engine's own size curve. MEASURED from the decompiled
engine, `RimWorld/Planet/WorldFeature.cs`:

```
EffectiveDrawSizeCurve:  10 -> 15    25 -> 40    50 -> 90    100 -> 150    200 -> 200
EffectiveDrawSize => EffectiveDrawSizeCurve.Evaluate(maxDrawSizeInTiles)
```

⇒ Every label on the planet draws at **effective size 15, the minimum**. The Dune Sea
(1,692 tiles) is lettered exactly as large as Notch. There is no visual hierarchy at
all, which is precisely the thing the owner is reacting to. The Fall Line is not
missing a label — it has one, and it is indistinguishable from seventy others.

## How the engine sets these normally, and why ours are flat

`RimWorld/FeatureWorker.cs`, `AssignBestDrawPos` — MEASURED:

```csharp
float maxDrawSizeInTiles = (float)bestTileDist * 2f * 1.2f;
newFeature.drawCenter = worldGrid.GetTileCenter(tile);
```

`bestTileDist` is the region's **inradius**: a flood fill inward from its edge tiles,
taking the deepest one. So vanilla sizes a label by how FAT a region is, not how long.
`drawCenter` is that deepest interior tile, tie-broken toward the centroid.

Ours are all exactly 10 because they were authored by Worldbuilder at a flat default,
not computed by that routine.

🔑 **`drawAngle` exists on `WorldFeature` and vanilla NEVER sets it** (it is not written
by `AssignBestDrawPos` and defaults to 0). Our companion's `world_features_set` can set
it — `WORLDMAP_BRIDGE_SURFACE.md` G4 calls it out as capability vanilla lacks. That is
the lever for making a long region's label run ALONG the region instead of flat across it.

## The Fall Line's measured geometry

From `world/ASHKARR_WORLDMAP_tiles.csv` (canonical), region `Fall Line`:

| | |
|---|---|
| tiles | **155** |
| lat range | −4.01 … 12.87 (**12.3 tiles**) |
| lon range | 40.11 … 64.94 (**18.1 tiles**) |
| max span | 27.84° = **18.7 tiles** (tile 710 ↔ tile 11585) |
| centroid, projected to the sphere | `(60.7127, 8.3209, −79.0236)` |
| current saved `drawCenter` | `(74.0402, 15.3778, −65.4173)` |

Planet radius is 100 and mean tile spacing is **1.4924°** — MEASURED 2026-09-21 as the
median edge length over all 65,610 edges of the engine's own neighbour dump
(`world/world_neighbors_sub7b.csv`), mean 1.4759°, and matching the closed form for a
hexagonal packing, `sqrt((4π/21872) / (√3/2))` = 1.4757°.

⚠️ The coordinate convention was calibrated, not assumed:
`x = R·cos(lat)·cos(lon), y = R·sin(lat), z = −R·cos(lat)·sin(lon)` reproduces the saved
`drawCenter` of `Fall Line` to within 4.2 units and of `The Breaks` to within 0.9.

## ⛔ The Fall Line does NOT absorb The Breaks

`The Breaks` (153 tiles, immediately south) is **the owner's own name**, ruled by card
2026-09-12: *"Fall Line Barrens → The Breaks"*
(`design/Jawa/world_rename_proposals.md`, executed by `WORLD_NAME_FIXES_1`). It is a
deliberate separate region, not drift. This pass makes the **Fall Line** major and
leaves The Breaks alone.

🔑 This also corrects `STALE_VIVIFIED_WORLDMAP_CITED_1` on one point: the canonical
worldmap's `The Breaks` is CURRENT and correct; `fall_line.md`'s `Fall Line Barrens`
is the stale name. The stale-CSV defect is real, but its direction is the opposite of
what it first looked like.

## What to apply

One `world_features_set` on the `Fall Line` feature, then `jawa/world_commit`
(⛔ nothing is visible without the commit).

| field | from | to | why |
|---|---|---|---|
| `maxDrawSizeInTiles` | 10 | **26** | effective draw size 15 → 42. The label then spans well beyond the region's own 18.7-tile width, which is how a major region reads, and sits clearly above the 15 every other label uses. 🔑 It is a deliberate PROMOTION, not a computed size: the Fall Line is 155 tiles, 38th of 71 by area, and the planet-wide curve in `WORLD_LABEL_SIZE_HIERARCHY_1` gives it 16.0 (effective 25) |
| `drawAngle` | 0 | **0 for the first look** | the angle's sign and zero-point are **UNMEASURED** — vanilla never writes this field, so there is no example to calibrate against. Set it only as a second iteration, judged by looking |
| `drawCenter` | `(74.0402, 15.3778, −65.4173)` | unchanged for the first look | it is inside the region and near its deepest interior; moving it and resizing it at the same time makes the result unattributable |

🔴 **One change, then LOOK.** Size first, screenshot, owner judges; angle and centre
only if the first look asks for them.

## Verify

1. `world_features_get` reads back `maxDrawSizeInTiles: 26` on `Fall Line` — raw field,
   not a cached property.
2. `jawa/world_commit` runs all its steps.
3. A screenshot of the world map at an altitude that shows the belt, with **no dialog
   open** — an open dialog blanks the frame to pure black
   (`rimworld-world-editing` §4).
4. The owner looks at it.

⚠️ **Membership is a tile field, not a feature field.** `WorldFeature.Tiles` is derived
from `worldGrid[i].feature == this`. Our CSV's `region` column is OUR bookkeeping and
does not always agree: the saved `drawCenter` of `Dune Sea` is 103 units from the
nearest tile the CSV assigns to it, and `Lantern Deeps` 82. For `Fall Line` and
`The Breaks` the two agree closely, so this pass is safe — but ⛔ do not assume the CSV
`region` column is the engine's feature membership for any other region without reading
it live first.
