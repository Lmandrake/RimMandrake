You are pre-reviewing three CANDIDATE sprites for a new RimWorld building before a human sees them. Be a strict art
director. Attached: RM_Fountain_A/B/C_checker.png (each the shipped 256x384 PNG over a checkerboard; real alpha).

Intended subject: "RM_Fountain" — a small, simple decorative stone fountain for the FlowWorks mod. 1x1 cell
footprint, drawSize (1 wide, 1.5 tall) cells, the extra height extending NORTH (up the canvas); not rotatable, one
facing (south view). The art is pale neutral stone because the game multiplies a stuff colour (granite, marble,
steel...) over it. In game its water spills onto the ground around it (a separate overlay draws the ground water),
runs to a ring ditch and is pumped back. Three design options: A tiered bowl (basin, pedestal, upper bowl with
three falling curtains, short jet); B spout pillar (basin, column, two side spouts arcing into the basin, top jet);
C cairn spring (ring of fitted stones, stacked slab cairn, water trickling down).

Hard rules to check:
C3 camera: orthographic, ~35 degrees above horizontal; every round rim an ellipse about 0.56 as tall as it is wide
(band 0.48-0.64); top faces lit and fully visible; vertical edges parallel (no perspective convergence).
C6 water/pipe plane: a pipe or spout shows its open bore only where it truly turns toward the camera; the basin water
surface must lie in the horizontal plane (an ellipse inside the rim, not tilted up); falling water and jets vertical.
D3: the silhouette sits inside the footprint (the basin fills most of the cell width; the column rises north).
D4: real alpha, no ground shadow, no backdrop, no halo. B1: painterly vanilla-RimWorld style with a clean dark
outline readable at 32 px per cell. B4: colour reads as material.

For EACH candidate give: verdict PASS / FIX / REDO; every concrete defect you can SEE (with location); whether it
reads at 32 px/cell (imagine it 32x48 px); and one line of fix instructions for an image-edit pass. Then rank the
three and say which best serves "a fountain whose water falls out onto the ground". Be concise.
