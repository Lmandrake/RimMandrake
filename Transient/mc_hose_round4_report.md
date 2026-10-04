# MessyConduit HOSE round 4 report — 2026-10-04

Owner's review (typed): reel should be 2x2 and much larger; no pale hose strip on emptied reel;
station 22 wrong pipe/reel connectivity; station 23 completable maze failed and hose vanished;
question: can water be shown flowing OVER the messy wires?

## 1. Reel size (2x2)
- Measured: def `size (2,2)` was already live (the deployed def matches the repo); `drawSize 2.3` on a 256 px canvas whose
  art fills 240 x 199 px, so the reel drew **2.15 x 1.79 cells**. In his station-22 shot (65 px per cell) the reel spans
  145 x 120 px = 2.2 x 1.85 cells: a squat side view, so it read as small next to the 0.47-cell-wide plump hose.
- Now `drawSize (2.8,2.8)`: the art draws **2.63 x 2.18 cells** (1.22x linear, 1.49x area), overhanging the 2x2 footprint by
  0.3 cell either side, as vanilla buildings do. Shadow volume scaled to match (1.6, 0.35, 1.35).

## 2. Pale strip on emptied reel
- It was in the round-3 art itself: `Reel_Deployed.png` painted one wrap of pale hose round the drum's underside and a
  length dropping from it through the base. artpipe searched first (`artpipe_state.py find reel`): only the two round-1/2
  stored-reel jobs, no strip-free deployed variant.
- `src/RimMandrake/Utils/mockups/messy_conduit/reel_round4_art.py` (deterministic, no image generation) paints it out: the
  drum's bare underside rebuilt column by column from the drum above it, darkened to its rim; the gap above the base
  rail cleared; the rail rebuilt from itself. 0 pale-hose pixels left in the strip's boxes. Installed through the art ledger
  (`install_image`, reason `script:...reel_round4_art.py`), sha 0a1d91e51497 (old 5b179364eda8, kept in the store).

## 3. Station 22 connectivity
- Station 22 places no pipes: its "two pipe segments" are two LENGTHS of hose joined by a joiner (two brass couplings
  face to face, each in a cloth wrap). Found: the joiner sat ON the bend's apex (B17 put joiners at bends), but a joiner is
  a rigid ~2.3-cell run (`JoinerHalf` = 0.49 x fitting size + 0.55 = 1.15 cells each side at full plump), longer than the
  whole 90-degree bend (radius 1.2 -> ~1.9 cells). So the brass lay diagonally across the corner while both hose lengths bent
  away under it - the misaligned joint in his crop.
- Fix (`HoseMath.Joints(C, spacing, half, flat, plump)` + `StraightenAt`): each bend still gets its joiner (B17 kept), but it
  slides to the nearest place within 3 cells where the planned route AND both drawn poses are straight (turn under 10 deg)
  for the joiner's full length, clear of the ends and other joiners; the hose under it is laid exactly on the run's chord
  (blended back over 0.5 cell) and the joiner is drawn along that chord. No straight run near a bend -> no joiner there
  (never a bent or wall-clipping one). Station 22 keeps 1 joiner.
- "Inappropriate connectivity to the hose reel": the hose started at the footprint centre, which is under the PUMP body
  beside its brass inlet, so going west it emerged right at the inlet coupling and read as plugged into the pump. Now it
  leaves under the DRUM (`HoseReelRect.Mouth`, +0.44 east / -0.40 south of the centre, from the art at drawSize 2.8) and
  shows coming off the drum through the gap above the base rail (the pale strip that used to fake that is gone, item 2).
  The pump's brass inlet stays the pipe/tank side (DrawFeed, round 2 port rule, unchanged).
- Selftests (r4): every joiner on stations 22/23/owner maze sits on a straight run (worst off-axis < 0.02 cell); an L-bend's
  joiner sits beside the corner, not across it; the mouth is inside the footprint under the drum, a 1x1 reel keeps its centre.

## 4. Station 23 maze failure
- What happened: the screenshot shows walls the owner added himself (read off a cell grid over 20261004163103_1.jpg:
  stubs (2,9) (6,9) (11,9) (4,8) (8,8) (10,8)-(10,7), and (3,7) + the column x=2, z=2..7 closing the chamber's west
  corridor). Reproduced offline cell for cell (`HoseSelfTest.StationMaze` + `Round4`, the production HoseMath/CordPlanner).
- Measured: the only way out now runs south, up the far west side and zig-zags along the top. Pulled taut it is
  **36.0 cells**; the hose is **30**. So the maze is completable, but not by this hose: the retract ("route too long") was
  the designed answer, not a planner miss. The hose did not vanish: it was reeled in (the reel shows the stored art, and the
  message top-left says so) - but the message gave no numbers, so it read as a disappearance.
- Two real bugs found on the way, both fixed:
  1. **The length test over-read twisty routes.** Round 3 summed the A* cell path centre to centre x1.08 (a staircase):
     48.5 cells for this maze, where the hose actually lays 34-35. Now `HoseMath.RouteLength` = the A* path pulled taut
     (any-angle, never through a wall or a pinched diagonal) from the reel centre, x `RouteMargin` 1.05. Station 22 reads
     19.9, station 23 as designed 23.6 (re-route fits a 30-cell hose with margin; the old notice's "about 29 of 30" is gone).
  2. **A laid hose could cut through 1-cell wall stubs.** `Clear` tested only the 0.25-cell sample points, so a stiffened
     hose cut stub corners between samples: in this maze 28 fine samples sat inside walls. `Clear` now walks every segment
     at 0.05 cell (graze tolerance 0.06) and refuses a pinched diagonal; if neither the stiffened sprawl, the rounded
     centreline nor the taut plan is clear, the lay fails with a reason and the reel retracts it (never drawn through a wall).
  3. Also: the slack budget is capped to the hose length (`HoseShapeParams.MaxLength`), so a laid hose is never longer than
     the reel holds (21-cell hose on a 19.9 route lays 20.0).
- The retract message and inspect line now carry the numbers: "the way round needs ~36 cells of hose, this reel holds 30".
- Station 23 itself is not wrong (its long way fits), so it keeps its layout; its notice now states the measured numbers.
  If the owner wants his zig-zag maze to complete, the Mod Settings hose length slider (8-60) at 37+ does it (a 40-cell
  hose lays it clear of every wall, selftest `r4 owner maze`).

## 5. Answer: liquid flowing over the cords
Yes, possible. Today's draw order: water TERRAIN (vanilla or a FlowWorks flood, which writes terrain) is drawn at Terrain
altitude, the messy cords at `AltitudeLayer.Conduits` (SectionLayer_RM_MessyCords), hoses just above them (Conduits + 0.004
+ a band per hose). So a cord in a puddle or flood currently draws ON TOP of the water, and a hose already passes over cords.
- **Cheapest workable (recommended): "submerged" cords.** In SectionLayer_RM_MessyCords, when a strand's cell terrain is
  water (vanilla `IsWater` or a FlowWorks liquid terrain), bake a vertex colour that lerps the strand toward the water's
  colour and drops its alpha to ~0.5, and add the Terrain map-mesh flag to the layer's dirty flags so a flood re-prints it.
  Reads as wire lying under water. Cost ~0.5 day + a selftest of the tint rule. Risk low (one section layer, no shader);
  the only cost is a re-print of affected sections when a flood spreads.
- **Better looking: a water film above the cords.** On cord cells whose terrain is water, draw a translucent quad of that
  terrain's own material just above Conduits altitude, so the vanilla water shader's ripples move over the wires. ~1 day.
  Risk medium: the vanilla water shader leans on its depth/reflection setup and terrain edge blending; drawn out of its
  layer it may show seams or the wrong depth tint - needs a live look.
- **Liquid moving over them (a flow direction):** wait for FlowWorks' liquid rendering; nothing to animate a direction from
  yet. Hose contents already show as plump + tint by contents.
Not built (as asked).

## Build / tests / commits
- Hose selftest 114/114 (102 round 3 + 12 round 4: st22/st23/owner-maze routes, wall-clip, pinch, slack cap, joiners,
  L-bend joiner, drum mouth); whole MessyConduit selftest 503/503. Built in a clean clone at the committed source (the
  working tree carries the aerial agent's mid-edit Core files, which do not compile in the selftest right now).
- `winbuild.py MessyConduit`: Build succeeded, 0 errors. DLL built at 9e9f153d4, committed with its .srchash in 18d8ea30a
  (this overwrote the aerial agent's uncommitted working-tree DLL; they rebuild on their next commit anyway).
- run_selftests.py: 173/176; failures are northstar_matrix C2 (pre-existing: live shots in Transient) and two unrelated
  mods (StarWarsPatches semantics, UtinniPatches dump).
- Commits: 9e9f153d4 (code, def, art, ledger event, script, this report), 18d8ea30a (DLL). Both commit subjects came out
  wrong (`publish` keeps only the last -m): 9e9f153d4's subject is its body sentence, 18d8ea30a's is the attribution line.
- Station 23's notice text in `human_review.py` (the measured 25-of-30 and "add your own walls" line) is in the working
  tree only: that file also carries the aerial agent's uncommitted edits to other stations, so it lands with their commit.
- `northstar_matrix/fakegame.py` still models the round-3 length rule (staircase x1.08). It is the stricter rule, so the
  stand-in refuses some routes the game now accepts. Owed: bring it in step.
- Not deployed (game holds the DLL). Owed: `deploy_custom_mods.py --mod MessyConduit --apply` at the next shutdown.

## Unproven live
- Everything visual: the 2.8 drawSize reading as "clearly 2x2" next to walls (it overhangs the footprint by 0.3 cell each
  side); the repainted drum's underside; the hose coming off the drum through the gap above the base rail; the joiner on
  its straight run at station 22's corner.
- The retract message, inspect line and alert showing the cell counts ("needs about 36 cells, this reel holds 30").
- That the new taut-route rule and the station-23 re-route behave in the game as offline (routes 19.9 / 23.6 cells).
