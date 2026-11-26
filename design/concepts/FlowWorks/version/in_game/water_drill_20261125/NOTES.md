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

### The fix, offline, 8:30 PM PST (published d72a515be5)

- `RM_ExcavationWalls`: a square under a clear liquid passes level 0 to every face (`float lv = sheet ? 0f : lvTrue`), so it
  draws the dry pit (faces, floor shade, lip bands, cast shadow); `WaterSurface` prints the dry floor opaque and lays ONE sheet
  (one colour, one alpha: the liquid's Seen with the wet-ground darkening composed in) over the dry pit cut by the waterline on
  each face, then the damp band inside each dry face. `SeeThrough`, `SideUnder` and the drowned rectangles are deleted.
- A shut sluice: the sheet covers only the half toward the wet side (`RM_PitReliefMath.SluiceHalf`); a face-on gate whose
  south side is drained draws its face dry (`GateFaceDry`).
- A dry dug square beside liquid terrain reprints its own floor (`ReprintsFloor`): vanilla's edge fade of the gate square's
  water no longer lies on the drained side.
- `SectionLayer_RMWetWallBand` and its setting are deleted (a second layer of unmitred rectangles); the deep tint skips dug
  squares (their water is the one sheet).
- `FillPictured` dirties the neighbours too (a sluice square's sheet reads its neighbours' levels).
- Red-then-green: `WaterLook_one_sheet_over_the_dry_pit_cut_by_the_line` and `WaterLook_sluice_parts_the_sheet_and_a_drained_floor_reprints`
  red on planted faults (`red_planted_no_waterline_cut.patch`, recorded on T_UNDERLIQUID), green on the fix.


### Experiment 2, about 8:35 PM PST: the fix build on ArchSmall

- Census: station 6's corner square now draws ONE sheet colour (alpha 172) over the dry pit's own faces (wall light 0..48,
  the same 88 shade triangles as station 5's dry corner); station 22's corner ONE sheet colour (alpha 237); no deep tint and
  no wall band on any dug square.
- Look (`after1_st22_east_walls_culled.png`): stations 20 to 22 drew their EAST wall dry. **False theory of my own:** I had
  taken the sheet pieces to be orientation-free. They are not: an east face mirrored without reversing its vertex order winds
  the other way and the GPU culls it (the drawer's own `SideFaceStep` reverses its east arrays for this). Red first: a SelfTest
  winding assertion (every piece winds as the floor's quads) failed on `3x3 d1 (2,0)`; fix: `ReliefFaces` reverses the
  mirrored east polygon; green.

### Experiment 3, about 8:50 PM PST

- Look: one even surface everywhere, but the brim-full pit (22) lost its black rim outline under the sheet, while the dry pit
  (23) keeps it. The outline marks the rim, which stands above the water: it is now drawn after the sheet, in the sheet's own
  sub-mesh (SelfTest: `outlineMat = sheetMatDrawn` before `DrawOutline()` after `WaterSurface`).

### Experiment 4, about 9:00 PM PST: every station, both sluice axes drained, the count check red then green

- Captures (fix build, 3 builds after the parent): `after_st05_06`, `after_st17_19`, `after_st20_22`, `after_st22`,
  `after_st07_08_full` / `_drained` (7 east and 8 west drained), `after_st09_10_full` / `_drained` (9 north and 10 south
  drained), `after_st28_33` (water in holes), `after_st24_27` (sprinklers, untouched). Every one read at about 82 screen pixels
  a square. I see none of the three faults: station 6 matches station 5's corners under one surface; the depth row is one
  even surface per pit (a 2 m pit shows its walls through the water as one mitred frame, as the dry pit draws them); each
  drained side is dry ground up to the gate, in both axes; at station 10 the gate's face is dry (the water stands behind it).
- `northstar/water_one_surface_live.py --drain` (kind A, the census read; offline selftest of its verdicts with planted
  readings, 10 of 10): on the PARENT build (73ecd94b31's DLL) all four rules FAIL for the reported reasons
  (`live_parent_73ecd94b31.json`: station 6's corner 5 sheet alphas, the wall band and the deep tint on dug squares, drained
  squares under vanilla's water fade with no cover, gate sheets over 0.92..1.0 of the square); on the fix build all four PASS
  (`live_fix.json`: 24 wet squares one sheet each, 8 drained squares dry, every gate's sheet 0.5 of its square).

### Not this cause

- Station 33 (his 6.png): the colonist stands drawn over the pit's east wall. Pawns are drawn in real time, not by the section
  layers this drill changed (the census cannot see them, by design); a different cause [guess ~80%], not worked here.
- The gate square still HOLDS water by the engine when one side is drained (the known "a shut sluice seals its whole square",
  `RIMMANDRAKE_MEND_FLOWWORKS_LIQUID_RULES_FIVE_OLD_DEFECTS`); the look now shows it on the wet half only.

### Lessons

- A count read (`jawa/cell_draw_census`) settled in one run what three earlier fixes argued by eye; it also found a cause
  nobody had named (vanilla's terrain edge fade of a NEIGHBOUR's liquid).
- A polygon mirrored for the other side must have its vertex order reversed, or the GPU culls it.
- Never release a game's lock to re-take it under `game_lock.py run`: another run takes the game in the gap.
