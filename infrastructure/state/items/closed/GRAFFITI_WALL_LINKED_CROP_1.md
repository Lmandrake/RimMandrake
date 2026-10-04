# GRAFFITI_WALL_LINKED_CROP_1 — do our wall marks draw only a 1/16 crop of their art?

## answer (FOUNDRY builder, 2026-10-04) — YES. MEASURED offline from engine source + our PNGs; no screenshot needed

**Mechanism (RimSage, decompiled 1.6):** `GraphicData` wraps any graphic with a `linkType` via
`GraphicUtility.WrapLinked` (GraphicData.cs:158). `Graphic_Linked.Print` / `Graphic_LinkedCornerFiller.Print`
draw `MaterialAtlasPool.SubMaterialFromAtlas(subGraphic.MatSingleFor(thing), linkSet)`, and `MaterialAtlas`
builds 16 sub-materials with `mainTextureScale (0.1875, 0.1875)` at offset `((i%4)*0.25+1/32, (i/4)*0.25+1/32)`,
link bits N=1 E=2 S=4 W=8 (`GenAdj.CardinalDirections` order). So every linked mark draws a 0.1875² window
(3.5% of the image area) chosen by its wall neighbours. All 45 `RM_Graffiti_*` defs carry
`<linkType>CornerFiller</linkType>` + `linkFlags Wall`.

**What that window holds in our art** (62 PNGs under `src/RimMandrake/Graffiti/Textures/Things/Filth/Art/`, alpha>32
coverage of the sampled window, computed with the exact UVs above):

| wall neighbours | mean coverage | PNGs drawing nothing (<1%) |
|---|---|---|
| one wall N / E / S / W | 0.32 / 0.31 / 0.28 / 0.23 | 16 / 16 / 21 / 20 of 62 |
| two opposite walls (N+S / E+W) | 0.64 / 0.66 | 2 / 1 of 62 |
| no wall | 0.08 | 38 of 62 |

- `RM_Graffiti_Scratches` (all 3 variants): **0.000 against any single wall — the mark is invisible.**
- Even where a window has paint, it is an arbitrary 3.5% fragment of a centred motif (a glyph, a cross-out,
  a flyer), never the motif. The donor's full-bleed `RM_Graffiti_Vandal` spray survives because any crop of it
  is paint (and still draws nothing on an E, S or W wall).

So the framework places marks next to walls correctly, and what it draws there is not the art.
The fix is a look decision and is filed as `GRAFFITI_LINKED_MARK_FIX_1`.
