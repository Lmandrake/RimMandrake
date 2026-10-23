# BENCH live diagnose round 2 — 2026-10-23

Game: UP, save RM_fw_walkthrough_20261022d. Bridge: BENCH ("BENCH live diagnose round 2").

| # | item | verdict | evidence | filed |
|---|---|---|---|---|
| 1 | RIVER_DOME_DIAGNOSE_WHITE_BLOB_AFLOAT | NOT A DEFECT: vanilla Muffalo seen from behind (north facing), half in water | r2/dome_muffalo_repro.png, r2/dome_muffalo_compare.png | legibility fix filed (see detail) |
| 2 | KLUDGED_HOSE_PRUNE_TAIL_TO_NOWHERE | MOD (hose end draw), reproduced on save d | r2/kludged_repro.png, r2/kludged_repro_zoom.png, r2/kludged_census.txt | (see detail) |
| 3 | TERRAIN_CROSSES_DIAGNOSE_DARK_BLOTCHES | NOT A DEFECT: base terrain SoilRich (vanilla rich soil) in small map-gen patches | r2/crosses_cells.txt, r2/mapC_terrain.txt | closed |
| 4 | POLE_CABLE_FIX_FORGOT_TO_SAG | PENDING | | |
| 5 | MODERN_TANK_PORT_REDRAW_COUPLER_FLOATS | PENDING | | |
| 6 | LEVELLING_FILLS_DIAGNOSE_WATER_GOES_MISSING | PENDING | | |
| 7 | ART_RESOLUTION_MEASURE_AT_MAX_ZOOM | PENDING | | |

## Detail

### 1. White dome afloat (map R station R1)
The R1 'current carries things' station (review_map_rivers.station_ops r_current) spawns a wild Muffalo one cell into the water
beside the crossing. Reproduced on save d map R (mapId 48): jawa/spawn_pawn Muffalo at 127,104 (WaterMovingShallow) draws the same
plain pale-blue dome with a ragged lower edge. A second Muffalo on land at 129,107 forced North draws the identical dome (plus its tail):
it is the vanilla Muffalo's north (rear) texture, the ragged edge is its fur hem, and the water hides the tail. No missing texture,
no placeholder. Only fault: a rear-facing muffalo does not read as an animal in a review shot -> the station should face it
along the current (E/W).

### 2. Kludged hose tail to nowhere
Reproduced on save d map C: Kludged pumping station god-built at 150,190 (rot 0, south port 150,189), Modern reel at 149,180,
lay:149,180,150,189 -> coupled to the station, fellBack true. Cell 150,188 (the port's straight lead-out cell) is WaterShallow
(the save's canal scene), so the router approaches the port cell from the EAST (centreCells ... 152,189 -> 151,189 -> 150,189).
The end fitting is still drawn port-normal (N-S) with its full straight lead-in, so the part of that lead-in south of where the
side-approaching hose joins shows as a short stub pointing into the canal. Not the stager: any player whose port lead-out cell is
blocked gets the same draw. MOD: the hose end must bend into the port from the side it actually arrives on (or the lead-in
must be trimmed to the join).

### 3. Dark cross blotches (snapshot_wall_route.png, map C ~113-118, 200-211)
get_cell_info over 100-118 x 198-214: every dark cell is base terrain SoilRich among GrasslandSoil, no thing, filth or
pipe in those cells (r2/crosses_cells.txt). Whole-map terrain read (jawa/get_terrain_batch, r2/mapC_terrain.txt, '#' = SoilRich):
842 SoilRich cells, mostly large natural blobs (e.g. x 155-180, z 131-157); the crosses are small patches of the same map-gen
noise at cell resolution. No terrain writer is on the map: RM_Swale and RM_SiltTrap 0 of 24661 things. Vanilla rich soil, not a
render layer and not a FlowWorks artefact. Nothing to fix.
