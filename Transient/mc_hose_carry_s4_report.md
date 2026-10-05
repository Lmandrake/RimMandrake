# Hose carry S4 (live drawing) report

Started Sun Oct  4 23:55:24 PDT 2026

## Plan
Design section 6/7/15 S4. Files: NEW Source/Hose/HoseLive.cs (Verse-free: end-kind rule, carry prefix+tail, retract clip,
auto-retract timing), NEW Source/Hose/HoseEnds.cs (HoseFreeEnd + HoseEnds.Read/FreeEnd()/WaterAt, HoseEvents EndPlaced/EndLifted),
HosePorts.FindAt (free-end port, any faction), RM_MapComponent_Hoses (DrawCarrying prefix mesh cached per trail + per-frame tail
to pawn.DrawPos, LOD at Far zoom: 0.5 sampling, no shadow/end piece; Retracting = laid pose clipped at wound/total; cut-hose
auto-retract = animated ghost at 3 cells/s; Watch(): events + reel mesh reprint on Stored<->out), Graphic_HoseReel (deployed
drum while Carrying/Retracting), HoseProbe census (endKind, freeEnd{}, draw{mode,len,hand,reelArt}, live{} counts), main + SelfTest
csproj, SelfTest/Program.cs + NEW SelfTest/HoseLiveChecks.cs (21 rows, each with a can-fail).

## Cycles

## Result
- selftest_messyconduit 667/667 (21 new). run_selftests 177/179: northstar_matrix (known, Transient PNGs) and
  UtinniPatches/selftest_utinnipatches_dump.py (not touched here).
- Live `validation_hose.py --carry` (validation_hose_carry_20261005T001134.json): CR0-CR6 PASS incl. **CR5c endKind=Free PASS**
  (no edit to CR5c needed: the census now carries endKind). CR7 FAIL is S5's new row: devModeOff labels are clean
  (`Deploy hose`, `Free end: open`) but its control list found nothing under DevMode -> the check, not the mod (S5's to fix).
- Shots (Transient/mc_hose_carry_s4/, run 001920, census beside each in s4_shots_log.json): 01-04 the hose runs from the reel
  to the carrier's hand and wraps the end of the wall he walked round (hand within 1 cell of his cell in all four, drawn length
  = pulled trail + tail); 05 drafted -> the end lies where he stood, settled with slack; 06 laid at the target; 07/08 winding
  -> the hose shortens back toward the reel (19.5 then 11.9 cells drawn of 25.7), end piece riding the cut; 09/10 a walled-in
  laid hose auto-retracts visibly (ghost shortening) while the reel already reads Stored; reel art "deployed" from the grab on.
- Findings: (1) bridge-stepped ticks (step_game_ticks) render no frames, so pawn.DrawPos (and the pawn sprite) stays stale; Hand()
  now falls back to the last trail cell when DrawPos is >1.6 from Position, and the shot script plays real time between shots.
  (2) the screenshot copy helper takes the first EXISTING file, so a same-named PNG left in RimWorld's Screenshots folder by an
  earlier run is copied instead of the new one (cycle-2 shots were all stale); shot names now carry a run stamp.
  (3) The carried line is drawn PULLED TAUT over the walked cells (design section 8's length measure and S2's LayAlong use the
  same pull), so on open ground it cuts corners like a dragged hose; round obstacles it follows the walk. Drawing the raw cell
  centres instead would snap on drop.

## Owed
- Water/Port endKind proven offline (rule) and by code path only: no live water or tank station on this tier (FlowWorks tank
  absent; a pond station is S5's 45/46). FlowWorks liquid terrain is not matched (only TerrainDef.IsWater): its tag is unknown.
- Winding clip steps every 10 ticks (WindBy cadence); not interpolated. Far-zoom LOD not screenshotted.
- The cut-hose ghost covers the 250-tick corridor retract only; CompHoseReel.HolderCheck's winder-less ReelIn stays instant.
- human_review.py --build fails KeyError 43 in label_ops (S5 mid-edit of stations 43-47); this pass used --carry's own scene.
- 23:57:06 read design/S2/S3/debug reports + RM_MapComponent_Hoses, CompHoseReel, HosePorts, Graphic_HoseReel; plan: HoseLive.cs (Verse-free carry line/clip/ghost/endKind rule) + HoseEnds.cs + draw
- 00:00:40 code written (HoseLive.cs, HoseEnds.cs, HosePorts.FindAt, map comp DrawCarrying/clip/ghost/Watch, Graphic_HoseReel, probe census, HoseLiveChecks); building
- 00:01:34 cycle 1: build OK, selftest 667/667 (21 new hoselive rows); deploying
- 00:02:00 game up (12 s); building review map
- 00:06:36 human_review --build KeyError 43 (S5 mid-edit of stations); waiting to retry
- 00:12:22 --carry live: 10 PASS (CR5c endKind=Free PASS), CR7 FAIL (S5's new row; devModeOff labels clean, its control check found nothing in devmode -> check bug, S5's). Running s4_shots.py
- 00:14:26 cycle 1 shots: hose wraps wall OK, reel art deployed, clip+ghost drawn; BUT tail ran back to a stale pawn DrawPos (bridge-stepped ticks render no frame; the pawn sprite itself stayed at the grab cell). Fix: Hand() falls back to the last trail cell when DrawPos is >1.6 from Position; shots now play real time between frames
- 00:19:04 cycle 2: hand tracks the carrier (hand within 1 of carrier cell in all 4 carry shots); looking at PNGs
- 00:19:20 cycle 2 PNGs were STALE: the shot helper copies the first existing file and RimWorld's Screenshots folder still held run 1's same-named PNGs; names now carry a run stamp
- 00:25:31 source committed locally 234620b32 (push refused until the DLL rides with it); DLL rebuilt from that source; publishing DLL+srchash+report+shots
