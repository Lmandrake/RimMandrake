# FALL_LINE_MAJOR_REGION_LABEL_1 — make the Fall Line read as a major world region

## the ask

Owner, 2026-09-20, verbatim:

> *"Definite put fall line as a major world region with beautiful clear label on worldmap."*

## what is actually wrong — it is not a missing label

MEASURED 2026-09-20 from `CANONICAL_ASHKARR_START_2026-09-12.rws` (parsed with
`xml.etree.ElementTree`, not scanned): the planet carries **71 world features, every one
a `WB_MapLabelFeature`, and all 71 sit at `maxDrawSizeInTiles = 10`** — the bottom of the
engine's own size curve.

MEASURED from the decompiled engine, `RimWorld/Planet/WorldFeature.cs`:

```
EffectiveDrawSizeCurve:  10 -> 15   25 -> 40   50 -> 90   100 -> 150   200 -> 200
```

⇒ **Every label on Ash'karr draws at effective size 15, the minimum.** The 1,692-tile
Dune Sea is lettered exactly as large as Notch. 🔑 The Fall Line is not missing a label —
it has one, and it is indistinguishable from seventy others. **The planet has no visual
hierarchy at all**, and that is the thing the owner is reacting to.

Why ours are flat: vanilla's `FeatureWorker.AssignBestDrawPos` computes
`maxDrawSizeInTiles = bestTileDist * 2f * 1.2f` from the region's *inradius*. Ours were
authored by Worldbuilder at a flat default and never went through that routine.

## the full spec

`design/Jawa/worldbuilding/fall_line_major_region_label.md` (110 lines, `04a0b78c9`) —
measured geometry, the calibrated coordinate convention, the `drawAngle` capability
vanilla never uses, and the verify checklist. **Read it before executing; do not
re-derive it.**

## what is owed

The offline half is **DONE and measured**. One bridge sitting remains:

1. `world_features_set` on `Fall Line`: `maxDrawSizeInTiles` **10 → 26** (effective draw
   size 15 → ~41). **This one field only.**
2. `jawa/world_commit` — ⛔ nothing is visible without it.
3. `world_features_get` reads back the raw field as 26.
4. Screenshot of the world map at an altitude showing the belt, **with no dialog open** —
   an open dialog blanks the frame to pure black.
5. Hand the owner the picture.

🔴 **One change, then LOOK.** `drawAngle` and `drawCenter` are deliberately left alone:
the angle's sign and zero-point are **UNMEASURED** (vanilla never writes the field, so
there is nothing to calibrate against), and moving the centre while resizing makes the
result unattributable. Second iteration only, judged by looking.

## traps

- ⛔ **The Fall Line does NOT absorb The Breaks.** `The Breaks` (153 tiles, immediately
  south) is the owner's own name, ruled by card 2026-09-12 (*"Fall Line Barrens → The
  Breaks"*). It is a deliberate separate region, not drift.
- ⚠️ **Feature membership is a TILE field, not a feature field** — `WorldFeature.Tiles`
  derives from `worldGrid[i].feature == this`. Our CSV's `region` column is our own
  bookkeeping and disagrees elsewhere (`Dune Sea`'s saved `drawCenter` is 103 units from
  the nearest tile the CSV assigns it). For `Fall Line` and `The Breaks` the two agree
  closely, so this pass is safe — ⛔ do not assume it for any other region without a live
  read.
- 🔑 The wider finding is worth the owner's attention on its own: **all 71 features are
  flat at the curve's floor.** Whether the rest of the planet gets a hierarchy pass is
  his call, and is not this item.

## state

Blocked only on the bridge. Offline work complete.

## APPLIED 2026-09-21 — live, photographed, and waiting on his eye

Executed on the canonical world (`CANONICAL_ASHKARR_START_2026-09-12`, loaded on the
full 618-mod list; cold load 17:31→17:52, ~21 min).

| | before | after |
|---|---|---|
| `maxDrawSizeInTiles` | 10.0 | **26.0** |
| `effectiveDrawSize` | 15.0 | **42.0** |

MEASURED by reading the **raw field back** after `jawa/world_commit`, not from the
setter's `success: true`. Feature is `uniqueID 73`, 155 tiles — matching the spec's
offline geometry exactly. Histogram after the edit: `{10.0: 70, 26.0: 1}`. `The Breaks`
(uniqueID 63, 153 tiles) is deliberately untouched.

✅ **The spec's headline claim is now confirmed LIVE, independently of the savegame
parse:** the pre-edit histogram was `{10.0: 71}` — every one of the 71 world features sat
at the bottom of the engine's size curve.

### the pictures

| | |
|---|---|
| `D:\Luke\dev\Rimworld\Transient\fall_line\alt420.png` | **the one to look at** — Fall Line beside The Breaks, Grey Sea, The Abandoned Mines, Ashfall Range, Notch |
| `D:\Luke\dev\Rimworld\Transient\fall_line\alt650.png` | whole-planet context; at this altitude Fall Line is the only label that survives |

Full-resolution originals (1810×1198) are in RimWorld's own Screenshots folder:
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\fall_line_alt420.png`

**It works.** At 420 the label is unmistakably larger than every neighbour; the planet now
has a visual hierarchy where it had none.

⚠️ The colony marker sits over the middle of the label at some altitudes, splitting
"Fall" and "Line". Incidental to this change — but if it bothers him, `drawCenter` is the
lever, and it is a second iteration.

### 🔴 the change is LIVE BUT NOT SAVED — deliberately

Nothing was written to `CANONICAL_ASHKARR_START_2026-09-12.rws`. Two reasons:

1. The item's own rule is *"one change, then LOOK"* — the size is his to judge before
   anything is baked in.
2. ⚠️ `rimworld/save_game` has previously written the **current slot** instead of the
   named one. The canonical save is one of only three artifacts ruled to survive the world
   remake; it is not worth risking for a value he has not seen yet.

⇒ Re-applying after his ruling is **one bridge call** on a loaded world. The expensive
part is the load, which any further iteration needs anyway.

## what is still open, and is HIS

🔑 **70 features are still at the curve's floor.** Whether the rest of the planet gets a
size hierarchy — and which regions count as major — is a separate decision and it is his,
not this item's.
