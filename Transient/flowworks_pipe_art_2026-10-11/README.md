# Universal pipe art (RM_UniversalPipe), four looks: study and result, 2026-10-11

Ordered by the owner (rulings #1 and #8 in `design/RimMandrake/gss_flowworks_rulings_2026-10-11.md`). Look at
`pipe_networks_and_icons.png` first. `pipe_atlases_raw.png` shows the four atlases, and
`study_donor_pipe_atlases.png` shows the donor pipes it was modelled on.

## Atlas format (read from the engine, not guessed)
`Graphic_Linked` + `MaterialAtlasPool`: the index is N=1, E=2, S=4, W=8, counted from the bottom row of a 4x4 grid. Each sub-material
shows only the **inner 3/4** of its quarter tile (offset 1/32, scale 0.1875), so every tile has 1/8 padding on all sides.

## Donor study (measured at the displayed cell edge)
| mod | atlas | pipe width | look |
|---|---|---|---|
| vanilla PowerConduit | 320 (60 px/cell) | 0.27 cell, centred | flat grey, square junction boxes |
| Dubs Bad Hygiene sewage/air | 512 (96) | 0.29 cell; horizontals sit off-centre, toward the north | white PVC, collar joints |
| VE Chemfuel / Nutrient Paste | 640 (120) | 0.27 cell, centred | painted pipe, flanged elbows, valve wheels on tees/crosses, round end caps; vertical crossing off by 1 px between tiles |
| Alpha Biomes propane | 512 (96) | 0.31 cell | dark teal, rounded junction caps |
| Rimefeller oil | 534 (101) | 0.55 cell | chunky cast iron, bolted flanges |

## What was built
The pieces are composited by `src/RimMandrake/FlowWorks/art_source/pipe/build_pipe_atlas.py`. The inputs are two generated images per look:
a straight strip, and a junction box with an end cap (in `raw/`). The atlas is 704 px (132 px/cell). The pipe is 0.30 cell wide and centred;
the hub is 0.55 cell. Tees and crosses get the look's junction box with its valve. Dead ends get the look's end cap, and a lone pipe shows the box.
The strip is mirrored across the pipe's axis and cut into a palindromic period, half a cell and then its mirror. Because of that, every crossing
joins pixel-identically in any orientation. `check_pipe_atlas.py` proves it: 0 failures and a worst join diff of 0 on all four atlases.
The same check finds the VE atlas misaligned by 1 px, so it can catch a real seam fault.

Material language follows the hose reel looks:
- Scrapper: rust-brown welded scrap with blue-grey patch plates and a brass valve wheel.
- Industrial: dark gunmetal with bolted flanges and hazard-striped boxes.
- Modern: glossy red enamel with chrome.
- Futuristic: pearl-white ceramic with a cyan light line.

## Your call later
- Mirroring the strip makes each cell's detail symmetric. On a long run this reads as a regular rhythm of sections.
- Elbows are bent pipe, not a separate fitting.
- None of this has been seen in game. It needs the def pointed at `RimMandrake/FlowWorks/Pipe/<Look>/UniversalPipe_Atlas`.
