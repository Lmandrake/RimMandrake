# FlowWorks water look drill, 2026-11-25 (RIMMANDRAKE_DRILL_FLOWWORKS_WATER_LAYERS_HE_SAW_STACKED_BLUE)

Game: ArchSmall, save `FW_WATERDRILL_20261125.rws` (a copy of `FLOWWORKS_OWNER_REVIEW_VISIT13_SMALL_20261125_0957.rws`).
His pictures: `D:\ClaudeWork\rimmandrake\showings\FLOWWORKS_WALK3_20261125\1.png` to `5.png`.

## What his pictures show (read 6:45 PM PST, before any code)

- 1.png, 2.png: the wet pit (station 6) draws a pale band along the north wall and pale strips down the west and east
  walls. The side strips run the whole height of the pit up to the north band, so the corners are square overlaps.
  The dry pit (station 5) has mitred (diagonal) corners and dark walls.
- 3.png: an E/W sluice, east side drained by hand: water look runs about two squares past the gate into the drained
  side, then stops at a soft vertical edge.
- 4.png: an N/S sluice: water look one square past the gate into the drained side, and a band wider than the pit at
  the gate's row.
- 5.png: the depth row. At 1.5 m and deeper a pale band at the north wall and pale strips at the sides; at 5.0 m the
  bands stack (lighter strips at the sides, a lighter band at the top, a brighter body).

## Theories, written before the first experiment

Code read first: `Superdeep/RM_ExcavationWalls.cs` (Regenerate, ReliefCell, SeeThrough, SideUnder, WetEdges),
`RM_WaterLooks.cs` (deep tint, wet wall band), `Sheet/SectionLayer_RMSheetWater.cs`.

- **T-corner (station 6).** A wet pit draws TWO geometries. The relief faces are planned for the dry part above the
  water only (`PlanStep(..., lv)`), and `SeeThrough` redraws the drowned part as plain rectangles: a band between the
  side walls' feet and side strips at full height to `stripTop`, lit by the OLD flat light lift
  (`LightAlpha(WallFaceLight/WallSideLight)`), not by the relief shade (`FaceShadeStep`, `StepK`). So under water the
  corners lose their mitre and the walls turn pale.
  *Proves it false:* the census on station 6's north-west corner square shows no `SeeThrough` rectangle (no
  queue-2440 face quad of full side-strip height) under the waterline, or a mitred polygon there.
- **T-stack (station 22; his theory).** The water over one square is not one surface: the floor sheet, each depth band
  of the drowned north wall, each band of each side strip, the deep tint (≥5 m) and the wet-wall shadow band are
  separate quads with different alpha and different extents, so their edges show as stacked bands.
  *Proves it false:* the census on an edge square of station 22 shows ONE water-coloured contribution covering the
  square (area 1) and no other.
- **T-drain-real.** The drained side really still holds water in the squares next to the gate (the depth engine keeps
  it, or the shut sluice seals its whole square), so the look is right and the fault is the drain.
  *Proves it false:* `WaterDlAt` / mouse-over depth reads 0 on a drained square that still draws water look.
- **T-drain-sheet.** The spill-sheet layer (`SectionLayer_RMSheetWater`) keeps a film or sheet tier on the drained
  squares (it redraws only on a terrain change).
  *Proves it false:* the census shows no `SectionLayer_RMSheetWater` draw on the drained square.
- **T-drain-terrain.** The drained squares keep a vanilla water terrain (the terrain rung is not rewritten when the
  water goes), and vanilla draws water there with its edge fade.
  *Proves it false:* the terrain at the drained square is a dry pit floor, or the census shows no vanilla water
  material on it.
- **T-drain-note.** `SeeThrough` runs on a drained square because its level note (`RM_SubmergeDraw.NoteAt`) reads the
  body's level, not the square's own water.
  *Proves it false:* `note == 0` on the drained square (no `SheetMat` quad in the census).

## Experiments

### Experiment 1, about 7:00 PM PST: the census on the walk save, parent build (ArchSmall)

New bridge read `jawa/cell_draw_census` (generic: every section-layer sub-mesh that covers part of one square, with its
clipped area, extent, queue and vertex alpha). It can see: `SectionLayer_Terrain` shows on every square read.

| square | what tints it as water |
|---|---|
| station 6 corner (33,110) | `SheetMat` q2449: 18 triangles = 9 pieces, alpha 0..136, area 0.75; `SectionLayer_RMWetWallBand` q2441 dark band area 0.34; drowned walls lit at alpha up to 92 (the dry pit's own corner: 48) |
| station 6 middle (34,109) | `SheetMat`: 1 piece, alpha 136, area 1.0 |
| station 22 corner (55,136) | `SheetMat`: 9 pieces alpha 0..229; `SectionLayer_RMDeepWaterTint` q2441 alpha 36..144 (corner averaging); black tint q2446 area 1.29 (overlaps itself) |
| station 7 drained (31,119), dl 0 | vanilla `SectionLayer_Terrain` `RM_WaterThin` edge fade from the gate square (8 triangles, alpha 0..255) and `Watergen`; no FlowWorks layer |
| station 7 gate (30,119) | holds 0.5 m by the engine (the known "shut sluice seals its whole square"); its sheet covers the whole square, the drained half too |
| station 9 drained (43,119), dl 0 | the same vanilla edge fade from the gate square |

Verdicts:
- **T-stack: TRUE** (his theory, in substance). Several water-tint draws of different extent and alpha lie on one square.
- **T-corner: TRUE.** The drowned walls are plain rectangles in the old flat light (alpha 92 against the dry pit's 48), so the
  corners lose the mitre and the walls turn pale.
- **T-drain-real: FALSE** for the drained squares (dl 0, dry channel terrain). The gate square does hold water.
- **T-drain-sheet: FALSE.** No `SectionLayer_RMSheetWater` draw on any drained square.
- **T-drain-terrain: TRUE, in a form I did not write.** It is not the drained square's own terrain; it is vanilla's edge fade of
  the NEIGHBOUR's water terrain (render precedence 392 over the channel floor's 325). Rim ground squares get the same fade, and
  the walls layer already hides it there with `Collar`; a dug square had no such reprint.
- **T-drain-note: FALSE.** The drained squares draw no `SheetMat`.

### The rule, solved offline first

`src/RimMandrake/FlowWorks/model/water_surface.py` (sweep: 7 pit shapes of the walk map and stepped ones, every quarter-notch
level, 1920 wet squares; a depth oracle inverts the face curves independently of the clipping). Rule: draw a wet square as the
DRY pit (plan at level 0), then ONE sheet, one alpha per square, over the dry pit cut by the waterline on each face; a shut
sluice with one dry side carries the sheet on its wet half; a dry dug square beside liquid terrain reprints its own floor.
Planted faults all go red (no waterline cut 1198 failures, the old rectangles 567, floor only 1267, a sluice that never
halves 8); the rule is green (0).
