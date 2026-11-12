# BIOME_SHIP_CONTRIBUTIONS_1 art2: blind judge verdict, round 1

Judge: claude-opus-5-5, blind (did not make these). Standard: `design/RimMandrake/art_judge_brief.md`.
What I looked at: contact sheets at 96 and 48 ppc, full-res crops of the mast facings and the 1x1 items, `glasswalk_2x2.png`, and the incumbents.
Footprints were checked from alpha bboxes against drawSize/size. Glasswalk wrap seam was measured: mean |edge diff| 0.63 / 0.91 against interior neighbour diffs of 0.68 / 0.83 (horizontal / vertical), so there is no seam.

| file | verdict | reason |
|---|---|---|
| RM_AerosolScreen.png | KEEP | Reads as a glass-domed projector on a plated base with a gel canister and hazard-striped pad, and the camera shows top faces. Fits 2x2. It is busy, but it stays readable at 48 ppc. |
| RM_AncientCondenserPlant.png | KEEP | A shell-stone housing with a honeycomb lattice, a pump tap on top and water seeping out at the foot: it reads as the old gorrask-shell condenser. It replaces a borrowed picture and is better than it (E1). Fits 2x2. |
| RM_FloatstoneDoor.png | KEEP | A pale neutral flat leaf with a pull handle that will tint cleanly with stuff, and it fits the 1x1 slide like vanilla leaves. Taste: the "spun thread" grain is only faint diagonal streaks, and a stronger grain would sell floatstone better. |
| RM_FloatstoneDoor_MenuIcon.png | REDO | It is almost identical to the leaf: a white slab with a vertical bar handle and a visible top face. Without a frame or threshold it reads as a refrigerator or cabinet, not a door (misreads as another object). |
| RM_Glasswalk.png | KEEP | A near-black glossy surface with soft diagonal sheen streaks, so it reads as hard bitumen glass. It tiles with no seam (measured). In the 2x2 the diagonal streak rhythm repeats slightly, which is acceptable for a floor. |
| RM_GlowerShieldPanel.png | KEEP | An orange porous crust slab in a bolted dark frame with a wall tab: it reads as cured glower crust on a mount, and it stays bold at 48 ppc. |
| RM_HullLinerRig.png | KEEP | A pressure vat of plated maroon segments with a gauge, valve and coiled spray lines, and grey coating drips on it. It matches the description and fits 1x1. |
| RM_LongShadeMast_east.png | REDO | The mast and edge-on vane read correctly. But the stepped base is drawn as a pedestal about 1.5 cells long at the foot, while south and north show a base spanning all 3 cells, so the facings disagree (C2). |
| RM_LongShadeMast_north.png | REDO | Same flaw as south. It is a pure side elevation: the stepped plinth shows only front faces with no top face, which breaks the about 35 degree camera (C3). Otherwise it is a correct mirrored rear. |
| RM_LongShadeMast_south.png | REDO | The black-chitin vane on a lashed mast reads as described, and the height goes north within the 3x3 canvas. But the 3x1 stepped base is a flat front elevation with no visible top surface, and the whole sprite reads like a sail on a board, not a building seen from about 35 degrees (C3). |
| RM_LureAwning.png | KEEP | Pale stitched hides on four lashed poles with guy ropes, at the right camera (the south poles are taller than the north ones). It fills 3x3 and is drawn pale for the stuff tint as intended. It is at least as good as the incumbent. |
| RM_SekkulaathTankCell.png | KEEP | A heavy barred cage over murky green water with timber and iron corners: it reads as a sealed, waterlogged holding cell. It has better camera depth than the incumbent and fits 2x2. |
| RM_SummGreatBone.png | KEEP | One huge, slightly purple-veined long bone that matches "a single bone", where the incumbent was a whole copied skeleton. It overruns 4x2 by about 8 px (0.06 cell) on each end, which is negligible. |
| RM_SunSphere.png | KEEP | A glowing amber glass vessel with a fern-like light culture on a bronze base: it reads as a small cultured sun. The feet dip about 0.06 cell below the 2x2 footprint, which is negligible. |
| RM_TarVault.png | KEEP | Four barrel tops sunk in glossy black tar inside a timber rack with a hoist hook. It matches "barrel-rack packed in tar" better than the incumbent's tar pool, and it fits 2x1. |
| RM_TractionLance.png | KEEP | A braced mount with a hand-cranked rope drum and a launcher tipped with a barbed hook: all three parts the description names are present, and it fits 1x1. |
| RM_WasteCaskBay_east.png | KEEP | Three casks in a column inside the shielded rack, with the readout on the side. It is in proportion with south and fits 1x3 rotated. |
| RM_WasteCaskBay_north.png | KEEP | The rear of the rack, with plain cask backs and the same scale and palette as south. It fits 3x2. |
| RM_WasteCaskBay_south.png | KEEP | A powered shielded rack of three marked casks with a seal readout, top faces visible. It reads clearly and fits 3x2. |
| RM_WindVaporator.png | KEEP | A tall wet mesh fog-catch on lashed poles dripping into a small powered drum. It is slim but still legible at 48 ppc, and it fits 1x1 with height going north. |

Redo direction (RM_FloatstoneDoor_MenuIcon): draw a door, not a slab. Show the pale floatstone leaf set in a door frame (jambs and lintel) on a floor threshold, slightly ajar or with hinges visible, and make the spun-thread grain visible. Drop the fridge-style long vertical bar handle and the boxy top face.
Redo direction (RM_LongShadeMast_south/north): keep the vane and mast as they are, but redraw the 3-cell stepped plinth from the about 35 degree building camera. Each step needs a visible top face; the plinth's top face spans 3 cells wide and about 0.5 cell tall in the image. Its front edge stays on the footprint's south edge, with the vane rising north from the plinth's top face. North is the same base seen from behind.
Redo direction (RM_LongShadeMast_east): make the stepped base run the full 3-cell column (the footprint's north to south ends) as a long plinth seen from about 35 degrees, with the mast standing at its middle and the vane edge-on along it. Match the south facing's step count and materials.

Overall: 16 KEEP, 4 REDO. The mast set needs a building-camera base and a matching east base, and the door menu icon reads as a fridge. Everything else reads as its description, fits its footprint, and beats or equals its incumbent.
