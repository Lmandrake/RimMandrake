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
| 7 | ART_RESOLUTION_MEASURE_AT_MAX_ZOOM | PARTIAL: test tier max zoom = 114 px/cell (128 px/cell art is enough); owner's Camera+ default max zoom = 456 px/cell by source (128 visibly blurs, 256 slightly soft) - live root-2 shot owed on a Camera+ list | r2/maxzoom_reel_rs2.png, r2/vanillazoom_reel_rs11.png, r2/art_resolution_sim.png | note; stays open |

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

### 7. Art resolution at max zoom-in
Game renders 3467x1826. Live (fw_gss_sitting tier, ray1203.SimpleCameraSetting): set_camera_zoom / zoom_camera below rootSize 8
clamp to 8 even with the bridge's zoom extension on, so this tier's max zoom-in is root 8 = 1826/16 = 114 px per cell
(viewRect 33x19 cells, r2/maxzoom_reel_rs2.png); vanilla closest root 11 = 83 px/cell (r2/vanillazoom_reel_rs11.png).
The owner's full lists all carry brrainz.cameraplus with NO settings file in Config (defaults): Camera+ Source/Settings.cs
(pardeike/CameraPlus) zoomedInPercent = 1, minRootResult = zoomedInPercent * 2 = root 2 -> 1826/4 = 456 px per cell.
Offline sampling of a 512 px texture (Armoury gonk_south.png as 1 cell) to the screen size from 512 vs 256 vs 128 px/cell
(r2/art_resolution_sim.png, rows = 83 / 114 / 456 px/cell): at 83 and 114 the three are indistinguishable (mean abs diff
<= 0.3/255 incl. transparent); at 456 the 128 version is visibly blurred and 256 slightly soft against 512.
Answer: resolution above 128 px/cell is invisible at vanilla or SimpleCameraSetting zoom, visible at Camera+'s default
closest zoom (256 clearly, 512 marginally). Owed: a live root-2 capture on a list with Camera+ to confirm the 456.

## Re-checks (coordinator queue)

| item | run | verdict | evidence |
|---|---|---|---|
| (g) VALIDATION_HOSE_REELS_FIX_STILL_WEST | fresh map, proof_hose --live --only relay | PASS: RL2-RL9 all PASS incl. RL4 (11/11 rows; the relay block emits no RL1 row). verified A1 L1, done | r2/proof_hose_relay_fresh.json/.log |
| (f) PROOF_REELS_FIX_STILL_STAGED_WEST | fresh map, walk_gaps --fresh-map ports; fresh map, pipe_levelling --rehearsal | FAIL (note): PORTS_PIPE_AND_REEL_ON_SIDES PASS, PORTS_ONE_HOSE_PER_SIDE PASS (was UNMEASURED); PORTS_CORNER_REFUSED UNMEASURED/SITE: reel D now builds at 99,49 and lays, but its end at the SE corner 93,43 sits under reel A's footprint (93..94,44..45) and couples to A as a RELAY ('coupled to a relay reel'), so ProofPumpPorts sees corner=0. Rehearsal layFailures 338/384: NO rig reel was built - the fresh map's natural Sandstone fills the rig columns and the rig build_batch uses wipeExisting=False ('would destroy 4 existing thing(s): Sandstone@100,4...'); only pipes landed. Both SITE/HARNESS. | r2/walk_gaps_ports_fresh.json, r2/level_rehearsal_fresh.json, r2/level_fresh_watch.log (0 levels destroyed) |
