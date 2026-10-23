# BENCH live diagnose round 2 — 2026-10-23

Game: UP, save RM_fw_walkthrough_20261022d. Bridge: BENCH ("BENCH live diagnose round 2").

| # | item | verdict | evidence | filed |
|---|---|---|---|---|
| 1 | RIVER_DOME_DIAGNOSE_WHITE_BLOB_AFLOAT | NOT A DEFECT: vanilla Muffalo seen from behind (north facing), half in water | r2/dome_muffalo_repro.png, r2/dome_muffalo_compare.png | legibility fix filed (see detail) |
| 2 | KLUDGED_HOSE_PRUNE_TAIL_TO_NOWHERE | MOD (hose end draw), reproduced on save d | r2/kludged_repro.png, r2/kludged_repro_zoom.png, r2/kludged_census.txt | (see detail) |
| 3 | TERRAIN_CROSSES_DIAGNOSE_DARK_BLOTCHES | NOT A DEFECT: base terrain SoilRich (vanilla rich soil) in small map-gen patches | r2/crosses_cells.txt, r2/mapC_terrain.txt | closed |
| 4 | POLE_CABLE_FIX_FORGOT_TO_SAG | MOD: red = Modern PipeSpan on Scrapper poles (look fallback bug), FIXED 2ae04e1509 (GSS), live look after deploy; sag = owner's 2% setting | AerialProbe styles (detail) | note on item; stays open for the judge |
| 5 | MODERN_TANK_PORT_REDRAW_COUPLER_FLOATS | CAPTURED both lanes W+E on all 3 tanks; all 12 ends 'coupled to <tank>' | r2/tank_modern_{208,214,220}_W_E_bothlanes.png, r2/modern_upper_census.txt | note; for the judge |
| 6 | LEVELLING_FILLS_DIAGNOSE_WATER_GOES_MISSING | HARNESS: rehearsal's ProofStageBasin staged over walk_gaps' filled ponds; reproduced exactly (200 levels at the first basin strip) | r2/level_after_walkgaps_watch.log, r2/walkgaps_pitfall_watch.log, r2/level_watch_pitfall.log | LEVEL_REHEARSAL_FIX_POURS_ON_FULL_PONDS; closed |
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

### 4. Pole cable red and straight (map R C1) + hose/pipe/hose at map C 25,130
Map R (save d) has the C1 pipe poles at 128,73 / 133,73. GSS AerialProbe `styles`: both poles rawStyle null, engine StyleDef
RM_PipePole_Scrapper (they DRAW the Scrapper mast), but the anchor's look reads "Modern" (GSS defaultLook) and the span draws
spanTex PipeSpan in look Modern. Deployed FlowWorks/Textures/.../PipePole/Modern/PipeSpan.png mean colour (207,38,39) = the
bright red; Scrapper's is (118,97,83), the copper of the C1 ground pipe. Cause: AerialLineProfiles.LookOfThing for a Pipe-kind
anchor fell from RawStyle straight to StylePicker.DefaultLook. Fix 2ae04e1509: fall back to the drawn StyleDef's look first
(GSS DLL rebuilt, not yet deployed; live look owed after the end-of-round deploy).
Sag: the span is 5 cells and pipePoleSag is 2% (owner's line-widths card 2026-10-20, per RM_PipePoles.xml), i.e. ~0.1 cell -
"nearly straight" is that setting, not a bug; the C1 sign's "sags over the ditch" over-promises for a 5-cell span (judge's call).
Map C 25,130 run: RM_UniversalPipe 23,128-133 with RM_HoseReels (rot W) at 24,134 and 24,127 - C7's staged "one hose net"
(two reels on one pipe, c07_bathhouse_tower.py). The beige pieces above and below the pipe are each reel's pipe link, drawn in
hose material, then the pipe between: by design of the scene, not a draw fault.

### 5. Modern tank ports, upper lane
Map C save d, tanks RM_LiquidTankTall 116,208 / RM_UniversalCargoTank 116,214 / RM_UniversalCargoTankXTall 116,220. West lower
lane = the save's reels 104,z. Added Modern reels (HoseProbe place:...:god): west upper 108,z+3 -> 115,z+1; east upper 124,z+3 ->
118,z+1; east lower 121,z-3 -> 118,z. Every lay layOk, every free end 'coupled to <tank>' at (115|118).5, (z|z+1).5. Captures use
the round-1 framing (rect 115,z 4x2 pad 1). First look: on all three tanks each of the four couplers meets a drawn grey fitting
face, no bare stub into plain wall (XTall frame crops the tank top, as round 1 did).

### 6. Levelling rehearsal: 200 levels destroyed
Player.log: the 101 'conservation exception' lines (2.0 each, total 200) follow the load of RM_LINES_PITFALL_20261023T015102,
on which round 1 ran walk_gaps_proof (01:51:25-01:53:31) and then pipe_levelling --rehearsal (01:53:58-01:55:46). The engine's
destroyed-liquid counter (RM_MapComponent_Excavation.overflowDestroyedTotal, read via jawa/map_comp_read after EVERY mutating
bridge call, tools/watch.py) on that save:
- rehearsal alone on map C (save d) and on a fresh load of the PITFALL save: 0 destroyed (level links ran, moves 29 / 20);
- walk_gaps ponds+ports alone on a fresh PITFALL load: 0 destroyed (PONDS_HOSE_LEVEL dl 450000 before and after: conserved);
- walk_gaps THEN rehearsal (round 1's order): 0 -> 200 at the first ProofStageBasin strip (5;2;90;138;4;4), Player.log 101 -> 201.
Verdict HARNESS: the rehearsal's basin A (x5..95) lands on walk_gaps' filled ponds (origin 40,40) and the staging call's
TrySetDriverFill rewrites cells another scene already filled; the engine discloses the loss as designed. Levelling itself
conserved liquid in every run. Fix filed: LEVEL_REHEARSAL_FIX_POURS_ON_FULL_PONDS.
