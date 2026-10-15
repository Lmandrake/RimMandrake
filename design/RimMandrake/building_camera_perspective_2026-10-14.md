# The building camera — measured from shipped art (2026-10-14)

Item `TANK_TALL_BUILD_TWICE_THE_DRINK`. Owner, 2026-10-14: *"The art for the tall tanks isn't very good. They
should be from the same perspective used to look at machines and the wall. Do some research to define that camera
perspective angle based on other tall art, then re-generate the tank art accordingly."* and *"Once that tall art
camera perspective is learned, please record it in the appropriate art regeneration skills."*

Everything below is measured from the textures. Nothing is taken from memory.

## The convention

| property | value | how measured |
|---|---|---|
| projection | **orthographic**: vertical edges are parallel, they do not converge | silhouette width at 35/50/65/80 % of height, 7 refs: constant to ±3 px except where a fitting sits |
| camera elevation | **~35° above horizontal** (band 29–38°) | top rim of upright cylinders: minor/major = sin(elevation) |
| top rim of a round thing | **minor/major 0.56 ± 0.04** (band 0.48–0.64) | ellipse fit on the silhouette's top arc, `ellipse_fit.py` |
| top face | always visible and the **brightest** surface | luminance; every upright cylinder's lid is its lightest region |
| bottom of a round thing | the lower half of the same ellipse, or hidden by a flat base/skid | refinery centre tank bottom arc 0.57 |
| light | **overhead and from the front**: highlight on the centre / centre-left of the front face, sides darker, no cast shadow painted (the engine draws building shadows) | left / middle / right thirds of the body's mid band: refinery 82/129/91, VFE steel tank 222/251/160, KOTOR tanks 108/150/108 |
| wall front face | a light band at the south edge, **30–39 % of the wall's drawn depth**, top face the rest | luminance runs down a horizontal wall piece |
| outline | Ludeon: a dark outline ~2 px at 64 px/cell (~3 % of a cell). Vanilla Expanded at 128 px/cell keeps a thin one. Our FlowWorks family is painted without one — keep the family | eye, `references.png` |
| height inside the footprint | Ludeon and VE fit the whole drawing inside the footprint (`drawSize` = `size`, overhang ≈ 0): a tall thing spends footprint DEPTH on its height | north/south overhang of the alpha bbox, 21 of 27 refs within ±0.1 cell |
| height above the footprint | when a thing is taller than its footprint is deep, mods extend the canvas **north**: `drawSize.y` > `size.z`, `drawOffset.z = (drawSize.y − size.z)/2`, base on the footprint's south edge | Column +0.31, KotOR water tank +1.0, KOTOR tibanna/rhydonium +1.47, FT antenna +5.54 cells north, south overhang ≤ 0.15 |

⚠️ **The walls and the round machines do not agree on one camera.** A wall's front band is 30–39 % of its depth;
a cube seen orthographically at 35° would show ~60 %. RimWorld keeps the ground grid unforeshortened (every cell is
square on screen) and draws vertical faces as a stylised band, while round machines are painted with a real ~35°
ellipse. For anything round, the ellipse is the binding measurement; for anything boxy, a lit top face with a
front band about a third of the depth is.

## References (27 buildings + 4 wall atlases)

Contact sheet: `Transient/building_perspective_2026-10-14/references.png` (48 px/cell, footprint in yellow).
Tools and raw numbers: `src/RimMandrake/FlowWorks/art_source/TankTall/perspective/` (`collect_refs.py`,
`measure_refs.py`, `ellipse_fit.py`, `measurements.json`). Sizes are from the live def dump (`defs.sqlite`); Core
and DLC art from the extracted bundle cache, mod art as loose PNGs. The Odyssey `ChemfuelTank`/`LargeChemfuelTank`
draw Vanilla Gravship Expanded's astrofuel art in this mod list; Ludeon's own art for them is shown as the
`_vanillaArt` rows.

| def | mod | canvas | footprint | drawSize (+z offset) | px/cell | N overhang | S overhang | top rim b/a |
|---|---|---|---|---|---|---|---|---|
| Column | Core | 64x128 | 1x1 | 0.5x1.25 +0.2 | 128 | +0.31 | −0.10 | — |
| DeepDrill | Core | 128x128 | 1x1 | 2x2 | 64 | +0.09 | +0.06 | 0.55 (bowl crop) / 0.61 (whole) |
| GeothermalGenerator | Core | 512x512 | 6x6 | 6x6 | 85 | 0 | 0 | — |
| Ship_Engine | Core | 512x512 | 3x4 | 4.25x4.25 | 120 | +0.12 | +0.12 | — |
| ChemfuelPoweredGenerator | Core | 128x128 | 2x2 | 2x2 | 64 | 0 | 0 | — |
| BiofuelRefinery | Core | 192x128 | 3x2 | 3x2 | 64 | 0 | 0 | 0.57 (centre tank) |
| WatermillGenerator | Core | 320x384 | 5x6 | 5x6 | 64 | −0.08 | −0.06 | — |
| AncientGravReactor | Odyssey | 512x512 | 5x5 | 5x5 | 102 | 0 | 0 | — |
| ChemfuelTank (Ludeon art) | Odyssey | 128x128 | 2x2 | 2x2 | 64 | 0 | 0 | — |
| LargeChemfuelTank (Ludeon art) | Odyssey | 256x256 | 3x3 | 3x3 | 85 | 0 | 0 | — |
| ChemfuelTank (VGE art) | VGE | 256x256 | 2x2 | 2x2 | 128 | −0.08 | 0 | — |
| LargeChemfuelTank (VGE art) | VGE | 384x384 | 3x3 | 3x3 | 128 | −0.05 | 0 | — |
| VGE_GiantAstrofuelTank | VGE | 768x384 | 6x3 | 6x3 | 128 | −0.05 | 0 | — |
| VGE_LargeOxygenTank | VGE | 384x384 | 3x3 | 3x3 | 128 | 0 | 0 | — |
| VGE_SmallOxygenTank | VGE | 256x256 | 2x2 | 2x2 | 128 | −0.02 | 0 | — |
| VFEPD_SteelTank | VFE Props | 256x384 | 2x3 | 2x3 | 128 | −0.02 | −0.02 | 0.60 |
| VFEPD_LiquidTank | VFE Props | 256x384 | 2x3 | 2x3 | 128 | −0.02 | −0.02 | 0.58 |
| VFEPD_ChemfuelTank | VFE Props | 256x384 | 2x3 | 2x3 | 128 | −0.02 | −0.02 | 0.58 |
| VHGE_GasTank | VHGE | 256x256 | 1x2 | 2x2 | 128 | −0.02 | 0 | 0.61 |
| Spaceports_FuelTank | Spaceports | 256x512 | 1x2 | 1x2 | 256 | −0.03 | −0.04 | 0.48 |
| KoltoTank | Armoury | 512x512 | 3x3 | 3x3 | 171 | −0.09 | −0.11 | — |
| GravTide_DrainTank | GravTide | 384x384 | 3x3 | 3x3 | 128 | −0.01 | −0.01 | — |
| FT_AntennaTower | Fortifications | 128x512 | 2x2 | 2x8 +2.85 | 64 | +5.54 | +0.15 | — |
| KotOR_watertank | Armoury | 512x512 | 1x1 | 2x2 +0.5 | 256 | +1.00 | 0 | — |
| KOTOR_TibannaTank | Armoury | 256x256 | 2x2 | 3.5x3.5 +0.75 | 73 | +1.47 | −0.03 | — |
| KOTOR_RhydoniumTank | Armoury | 256x256 | 2x2 | 3.5x3.5 +0.75 | 73 | +1.47 | −0.03 | — |
| RM_LiquidTank (ours) | FlowWorks | 512x512 | 2x2 | 2x2 | 256 | −0.26 | −0.25 | — (horizontal drum) |

Wall atlases (front band : top, px down one column of a horizontal piece): Core `Wall_Atlas_Bricks` and
`Wall_Atlas_Smooth` 21 : 33 (front 39 %), Odyssey `AncientFortifiedWall_Atlas` 16 : 37 (30 %), Odyssey
`GravshipHull_Atlas` 32 : 73 (30 %).

Not measured: Biotech's mech gestators and Core's `ShipComputerCore`/`ShipReactor` south facings — those bundles are
not in the extracted cache. Battery was dropped: the cache's bare `Battery` texture is not its south facing.

## How a round tank should look

An upright tank on a 2×2 footprint: the top rim an ellipse **0.56 tall for its width**, the lid face lit and fully
visible with its hatch drawn lying IN that ellipse (not facing the camera), sides vertical and parallel, base on
the footprint's south edge. Extra height goes north: keep `drawSize.x = 2`, raise `drawSize.y`, and set
`drawOffset.z = (drawSize.y − 2)/2` so the base stays on the same ground line as its short sibling.

## Our tanks against it

| tank | top rim | verdict |
|---|---|---|
| RM_LiquidTankTall (installed 2026-10-14) | b/a 0.37 by fit; a domed head in side elevation, no top face | **violates** — rejected by the owner |
| RM_UniversalCargoTankXTall (installed 2026-10-14) | fit unusable (rms 17.6 px, lugs cross the rim); hatch drawn as a full circle facing the camera | **violates** — rejected by the owner |
| RM_LiquidTank (short, horizontal drum) | hatch ellipse ≈ 0.4, no lit top band along the drum; drawing floats 0.25 cell inside the footprint at both ends | **mild violation** — not changed (cosmetic changes need the owner) |
| RM_UniversalCargoTank (short, horizontal drum) | hatch drawn as a near-frontal circle; side elevation of the drum | **violates** — not changed (cosmetic changes need the owner) |
| RM_LiquidTankTall v2 (candidate) | b/a 0.57 (35°), rms 0.4 px | conforms |
| RM_UniversalCargoTankXTall v2 (candidate) | b/a 0.56 (34°), rms 0.3 px | conforms |

The v2 candidates and how they were made: `src/RimMandrake/FlowWorks/art_source/TankTall/v2/` (`guide.py` draws the
grey camera blockout the edit is anchored to; `fit_v2.py`; `scene.py`). Review picture:
`Transient/tall_tanks_2026-10-14b/tall_tanks_v2.png`. The check is now in the sprite validator:
`validate_sprite.py --upright-cylinder` (skill `generating-rimworld-sprites`,
`references/building_camera_perspective.md`).
