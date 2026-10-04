# MessyConduit sheet round 2 — report

## Status
DONE offline: 11 stations added (19-29); --plan clean; awaiting the main window's --build (bridge).

## Reading notes
- REGION (8,6,228,106) is fully used by rows A-D (z 8..~104); quicktest colonists stand near 125,125, so new stations go in a SECOND region north of them.
- jawa/set_fog supports action=refog (per-station fog), jawa/set_roof_batch 'RoofRockThick:x,z,w,h', jawa/blueprint_place one blueprint per call.
- Modern colour mode Mixed = a different colour per power net (the 'random mix' lever).

## New stations
Plan (numbers append after 18; existing 1-18 unchanged). New ROW E/F/G live in a second region REGION2 (8,140,242,110), north of the quicktest colonists (~125,125), reaching the NE map corner for the edge station.
- 19 POLE CLUSTER (diverse devices: lamp, heater, sun lamp, mini-turret, batteries adjacent; stove, hi-tech bench, TV, walk-in freezer with in-wall cooler + wall lamp at distance; a lamp mast overhead)
- 20 ELECTRIC ROOM (walled room full of devices, messy conduit + a tangle, masts carrying power overhead across it)
- 21 MOUNTAIN TUNNEL (granite mass + RoofRockThick + refog around a winding conduit tunnel and cavern; a roofed mast whose link must be refused)
- 22 HOSE MAZE: TWO ROUTES (layout + hook hose_maze_hook)
- 23 HOSE MAZE: OBVIOUS ROUTE WALLED (layout + hook hose_block_wall_hook)
- 24 MAP EDGE, 25 RIVER CROSSING, 26 ROOF BOUNDARY, 27 LONG SPAN + DIAGONALS, 28 CONVERGING HUB, 29 NETS SIDE BY SIDE + MERGE + HALF-BUILT (save-load)
Defs verified in RimSage: ElectricStove 3x1, HiTechResearchBench 5x2 (Metallic stuff), Turret_MiniTurret 1x1 (Metallic stuff), FlatscreenTelevision 2x1, WallLamp (attached to wall, rot points at wall), SunLamp, Cooler, WaterproofConduit, WaterMovingChestDeep/WaterMovingShallow, RoofRockThick/RoofConstructed. Mast maxLinks 4, lamp mast 3, bracket 2; span range 20 (dx^2+dz^2 <= 400); hose maxLength 30, route*1.08 <= 30.

## Layout (global origins, REGION2)
Row E showpieces z=144: 19 @ (12,144) 40x26 · 20 @ (62,144) 35x22 · 21 @ (108,144) 48x32. Row F hose mazes: 22 @ (166,144), 23 @ (194,144), 18x11.
Row G challenges z=192: 25 river @12 · 26 roof @54 · 27 long span @96 · 28 hub @156 · 29 nets @196 · 24 map edge @ (222,226) so its local (27,23) is the map corner (249,249).
human_review.py now supports per-station: terrain (painted before build), roof (re-laid after every unroof pass, `station_roofs`), fog (`station_fog`: refog rects then unfog rects, applied last, never unfogAll), blueprints (jawa/blueprint_place, faction Player, ignoreValidity), WaterproofConduit cells, stuffed devices (turret, hi-tech bench = Steel), links with an EXPECTED refusal verdict (recorded under `expected_refusals`, a mismatch becomes a note), and hose hooks.
Hose hooks (HOSE workstream slot): `hose_maze_hook` / `hose_block_wall_hook` delegate to `validation_hose.review_maze(R, station)` / `validation_hose.review_block_wall(R, station)` when those exist; otherwise the default records a census (the block-wall default builds the steel wall over station 23's `block` cells after laying, steps 60 ticks, censuses before/after).
--goto N0 frames the north gallery. clear()/calm()/no_roofs() cover both regions.

## Plan output
`python3 src/RimMandrake/MessyConduit/human_review.py --plan` -> layout ok: 29 stations + free area. The checker is new-strict for 19+: footprint, on-map, expected-vs-range for every link, no mast within span range of another station's mast, regions disjoint, numbering 1..N. Sanity probe: planted a 21-cell link marked Ok, an off-footprint device and a station moved within span range: all three caught.
Expected refusals (shown on purpose): 21 cavern pole Roofed; 26 inside pole Roofed; 27 the 21-cell pair OutOfRange; 28 fifth pole FullA.
Live-only unknowns for the --build: WaterproofConduit on WaterMovingShallow (survived count), Cooler rotation in 19/20 (blue side should face in), blueprint_place on a PowerConduit under ignoreValidity, whether the hose router finds the maze route within maxLength 30 (short route ~19 cells, long ~22).
Note: --plan regenerated KEYSHEET.md/html WITHOUT the "This build" JSON block the last live build had written; the next --build restores it.

## Selftests
- validation.py offline: 5/7 PASS; the 2 FAILs are outside this file (O3_core_selftest tangle_off in the C# core; O5 Aerial/TapClamp art size 128 vs 64). Neither reads human_review.py.
- northstar_matrix/selftest.py: 53/54; the 1 FAIL is C2 (live shots carry no aligned OFF pairs), unrelated.

## Commits
