# Player-truth testing pilot (FlowWorks: pits, ladders, pipes, hoses, levelling)

Date: 2026-10-26. Seat: BENCH. Status: PILOT DONE. 19 truths swept offline; 1 violation class filed (PIPE_ELBOW_FIX_SEAM_JOGS).

## The question

The owner, 2026-10-26: "They had embarrassing mistakes. The perspectives on the ladders would be the
reverse of the walls they leaned on. People stuck in pits couldn't walk around the pit, they could only
move along the southern edge. pipes with big graphic gaps that didn't connect. Hoses whose ends suddenly
kinked in the wrong direction then terminated. Deep water in half of a pit and empty pit in the other,
without flow. How do we make a system that moves towards a more realistic, sensible testing scheme? Can
we even?"

A player-truth is a plain property a player would expect, written as a check on game logic or
geometry and swept over the whole input space offline, rather than over the few cases a developer
thought to try.

## 1. Truth list

Each truth is written the way a player would say it. Where a truth came straight from his complaint, it is marked with the complaint (C1 to C5) it came from.

**Ladders (C1: "the perspectives on the ladders would be the reverse of the walls they leaned on")**
- PT01: A ladder hangs on a real wall: a raised side, never open floor or a drop.
- PT02: A ladder leads up only the wall it shows, and it does lead up that wall.
- PT03: Turning or mirroring the map does not change which wall a ladder takes.
- PT04: A ladder keeps its wall on reload. Resolving its own turn again gives the same wall.
- PT13 (C1): The east and west pictures stand on the wall side of their cell.
- PT14: The west picture is the east picture mirrored.
- PT15 (C1): A leaning ladder's top is nearer its wall than its foot.

**Pits (C2: "people stuck in pits ... could only move along the southern edge")**
- PT05: If you can step from A to B, you can step from B to A.
- PT06: Pathing and the pocket grid agree on who can reach whom.
- PT07 (C2): A pit has no favourite side. Turning the pit turns its walkable regions with it.
- PT08 (C2): A flat pit floor is walkable in every direction, to every floor cell.
- PT09: A pit too deep to climb traps you, and a ladder on any wall cell gets you out.

**Pipes (C3: "pipes with big graphic gaps that didn't connect")**
- PT16 (C3): A pipe tile reaches every edge it links to, at that edge's middle, so there is no gap.
- PT17 (C3): Two linked tiles meet with the same cross-section across their seam, so there is no jog.
- PT18: A pipe tile does not reach an edge it does not link to, so there is no stub to nowhere.
- PT19: A pipe tile is one piece, with no floating cap or coupling.

**Hoses (C4: "hoses whose ends suddenly kinked in the wrong direction then terminated")**
- PT10 (C4): A hose leaves its reel along the outlet and arrives along the inlet. It starts and ends on the ports, and turns no more than 90 degrees in its first or last cell.

**Levelling (C5: "deep water in half of a pit and empty pit in the other, without flow")**
- PT11 (C5): Water poured anywhere in a pit levels across the whole pit. It forms one surface, nothing is left perched, and the water is conserved.
- PT12 (C5): Digging the dry half of a flooded pit lets the water flow into it.

**Truths these sweeps cannot reach**
- R1 (render-only, C2): A pawn in a pit draws sunk the same on every edge row. The history here is the south-row draw clamp, 59e29aa39d.
- R2 (render-only, C4): The drawn hose mesh follows the lay polyline to the port.
- R3 (render-only): Ladder and pipe art draw at the right altitude, over the wall and under pawns.
- L1 (live-only, C2): Vanilla's region and reachability caches agree with our masks. This covers the Verse d9 fill and the live inputs to RM_ClimbJoins.
- L2 (live-only, C5): Levelling actually ticks on a real map, with the right tick type and scheduling.
- L3 (live-only): A pawn really climbs a ladder: the job, the reservation and the animation.

## 2. Status of each truth

Kinds of check:
- **sweep**: an offline sweep over the whole input space, on production pure logic (C#) or on the shipped PNGs (Python). Neither uses a model, because the functions under test are the shipped ones: RM_LadderWallMath, RM_CliffMaskMath, RM_PocketGridMath, HoseReelLinkChecks.LayLink and HoseRelay.DrawnEnd, and ArrayWorld with the shipped levelling flags.
- **related hand-picked checks**: files whose cases touch the same logic (identified by file, not audited case by case). The pilot covers the whole space.

| Truth | Status | Where checked | Cases | Violations |
|---|---|---|---|---|
| PT01 ladder hangs on a wall | sweep (related hand-picked checks: LadderWallChecks.cs) | PlayerTruthSweeps.cs | 25,920 | 0 |
| PT02 ladder leads up its wall | sweep (related hand-picked checks: LadderWallChecks.cs) | PlayerTruthSweeps.cs | every hung case of the 25,920 | 0 |
| PT03 ladder rotate/mirror equivariant | sweep, new | PlayerTruthSweeps.cs | all non-tie cases | 0 |
| PT04 ladder stable on reload | sweep, new | PlayerTruthSweeps.cs | every hung case of the 25,920 | 0 |
| PT05 steps symmetric | sweep (related hand-picked checks: CliffMaskChecks.cs) | PlayerTruthSweeps.cs | 786,432 | 0 |
| PT06 masks match pockets | sweep (related hand-picked checks: PocketGridChecks.cs) | PlayerTruthSweeps.cs | 786,432 | 0 |
| PT07 pit has no favourite side | sweep, new | PlayerTruthSweeps.cs | 786,432 | 0 |
| PT08 flat floor walkable every way | sweep, new | PlayerTruthSweeps.cs | 511 shapes x depth 1..4 x K | 0 |
| PT09 deep pit traps, ladder frees | sweep (related hand-picked checks: WallClimbChecks.cs) | PlayerTruthSweeps.cs | every wall cell | 0 |
| PT10 hose ends straight | sweep (related hand-picked checks: HoseEndLipChecks.cs, HoseReviewChecks.cs) | PlayerTruthSweeps.cs | 1,137 lays (15 refused as too close) | 0 |
| PT11 pour levels the pit | sweep (related hand-picked checks: LevelPourChecks.cs) | PlayerTruthSweeps.cs | 992 scenes | 0 |
| PT12 second dig floods | sweep, new | PlayerTruthSweeps.cs | 496 scenes | 0 |
| PT13 ladder art on the wall side | sweep, new | selftest_player_truths_art.py | 5 families x E/W | 0 |
| PT14 west mirrors east | sweep, new | selftest_player_truths_art.py | 5 families | 0 |
| PT15 leaning ladder leans in | sweep, new | selftest_player_truths_art.py | portable E/W | 0 |
| PT16 pipe reaches linked edges | sweep (related hand-picked checks: PipeStraightVariantChecks, selftest_pipe_seat) | selftest_player_truths_art.py | 4 looks x 16 masks | 0 |
| PT17 seams match | sweep, new | selftest_player_truths_art.py | 4 looks x every linked pair | **156** (PIPE_ELBOW_FIX_SEAM_JOGS) |
| PT18 no stub to an unlinked edge | sweep, new | selftest_player_truths_art.py | 4 looks x 16 masks | 0 |
| PT19 tile is one piece | sweep, new | selftest_player_truths_art.py | 4 looks x 16 masks | 0 |
| R1 pawn sink same on every edge | render-only | (PitDrawHoldChecks.cs covers the clamp math) | - | - |
| R2 hose mesh follows lay | render-only | (HoseDrawGeometryChecks.cs, partly) | - | - |
| R3 art altitude | render-only | live review | - | - |
| L1 vanilla caches agree | live-only | live proof | - | - |
| L2 levelling ticks live | live-only | live proof | - | - |
| L3 pawn climbs | live-only | live proof | - | - |

Of the 25 truths, 19 can be checked offline, 3 are render-only and 3 are live-only.

## 3. Sweeps run against current code

**C# logic sweeps**
- File: src/RimMandrake/FlowWorks/Source/SelfTest/PlayerTruthSweeps.cs.
- Run: `python3 src/RimMandrake/Utils/selftest_flowworks_stock.py --only 'PlayerTruth_*'`.
- Result: 13/13 cases passed. That is PT00 (the probes) plus PT01 to PT12.
- Evidence: D:\ClaudeWork\rimmandrake\player_truth_pilot\st_truths.txt and st_truths_water.txt.

PT00 shows that each instrument can fail. It runs every check against an injected copy of the bug it guards:
- A reversed ladder breaks PT01 in more than half of the cases.
- A "no south step in pits" fault makes both PT07 and PT08 throw.
- A synthetic end hook reads more than 90 degrees.
- A reversed inlet is told apart from a correct one.
- A half-filled pit that has not been pulsed reads as perched by at least 2.9 notches.

The water sweeps also show the water moved: it spread in 992 of 992 pour scenes and reached the new half in 496 of 496 second-dig scenes. A pass there therefore means the water levelled, not that it never moved.

**Python art sweeps**
- File: src/RimMandrake/FlowWorks/Tools/selftest_player_truths_art.py.
- Inputs: the shipped PNGs, through fw_compositor.atlas_tile, which emulates vanilla's linked-atlas crop.
- Probes: each truth catches its own injected defect:
  - east and west swapped;
  - the first fix's far-side placement, which shifts the picture half a cell;
  - west equal to east instead of mirrored;
  - a straight cut short of its edge;
  - an off-centre straight;
  - an arm out to an unlinked edge;
  - a detached piece.
- Result: PT13 to PT16, PT18 and PT19 hold. PT17 fails 156 times.
- Evidence: D:\ClaudeWork\rimmandrake\player_truth_pilot\art_truths.txt.

**The violation: PIPE_ELBOW_FIX_SEAM_JOGS**
- Scope: the Modern, Industrial and Futuristic atlases. Scrapper is clean.
- In a 132 px tile with an 18 px bore, every straight, tee and cross crosses its edge at px 57-74. The elbows (masks 3, 6, 9 and 12) cross at 54-71 or 60-77. Each elbow is shifted 3 px toward its outer corner.
- So an elbow beside a straight jogs 3 px, and an elbow beside an elbow jogs 6 px.
- Failing case: Modern, mask 3 (N+E), east edge at rows 54-71, beside mask 10 (E-W straight), west edge at rows 57-74. Overlap is 0.71.
- Filed for BENCH. The fix belongs in the atlas compose.

**Two thresholds came from the art, not from guesses**
- The first PT16 run demanded a run of 15% of the tile. It flagged 128 "gaps" that were really just the 18 px bore. PT16 now measures against the pipe's own bore.
- The first PT19 probe used a speck smaller than the speck floor, so it was blind. The probe was enlarged until it fails.

Both slips were caught by looking at the numbers before filing. Without that look they would have produced 128 false items and one blind truth.

## 4. Would the scheme have caught his five?

The ledger gives the root cause of each complaint.

| Complaint | Root cause (ledger) | Caught by | Verdict |
|---|---|---|---|
| C1: ladder perspective reversed | Art: E/W textures swapped. The first fix then sat them on the far side of the cell (LADDER_EW_FIX_LEANS_THE_WRONG_WAY). | PT13 and PT15. Both injected forms fail in the probes. | **Yes** |
| C2: pit walkable only along the south edge | No item. Nearest history is the pit sink draw clamp (59e29aa39d: "on a south-row cell it capped every pawn at 0.5"). | A pathing cause would fail PT07 and PT08; their probe injects exactly that. A draw-clamp cause is R1, which is render-only. | **Partly.** Yes if the cause was in the pathing math. If it was the draw clamp, only a unit check of the clamp (PitDrawHoldChecks) or a live look catches it. |
| C3: pipe gaps | Art: the compose tile-vs-cell bug left the elbow kink, detached caps and couplings in the padding (PIPE_ATLAS_REBUILD_OTHER_LOOKS_KINK). | PT16, PT17 and PT19. Probes cover a gap, a jog and a detached piece. | **Yes.** It still finds a residual 3 px jog today. |
| C4: hose end kinks then stops | The lay end sat a cell short of the port (HOSE_END_FIX_CELL_SHORT_OF_PORT). | PT10, which checks that the end is on the port and the arrival heading is within 35 degrees. | **Yes** for the lay geometry. Mesh drawing is R2. |
| C5: water perched in half a pit | The water walk never crossed a pond to its other mouths (LEVEL_WATER_FIX_POND_SPLITS_ARMS). | PT11 and PT12. The perched probe shows the check can see it. | **Yes**, if the split shape is in the swept rectangles. Two-mouth ponds are in them. |

So the scheme would have caught 4 of the 5 outright, and the fifth (C2) only if its cause was in the pathing logic. Counting C2 as half gives 4.5/5.

The art defects were the cheapest to catch: they were two of the five, and each costs under a minute to sweep. Previously they were caught only by the owner's eye.

## 5. Cost to run

- **C# logic sweeps:** about 100 s to build the SelfTest and 62 s to run all 13 cases.
  - PT10 (hoses, 1,137 full lays) takes 55 s of that.
  - The other cases take under 7 s together; the 786,432-case mask sweeps take 1 to 2.6 s each.
  - Runs with the rest of the SelfTest, so there is no extra build.
- **Python art sweep:** about 20 s for all 69 assets and the probes.
- **Writing it:** this pilot took one helper session. Each new truth is 20 to 80 lines, because it reuses the production pure functions and the existing harnesses (ArrayWorld, CordWorld, fw_compositor).
- **Nothing here needs the game, the bridge or a deploy.**

## 6. Truths passing X/Y as the definition of done

Proposal:
1. Each mod or feature keeps a truth list: the PTnn lines above, plus the R and L lines that cannot be swept.
2. A feature is **done** when its offline score is Y/Y. Every sweepable truth must pass, with its probe proving the instrument can fail. The report is "X/Y truths, N probes bite". A truth whose probe does not bite counts as failing, not passing.
3. Render-only and live-only truths are scored separately, as R/L x/y. They are discharged by a recorded live look or proof. A feature can be "offline done" and still owe "live x/y".
4. A new owner complaint becomes a new truth before it becomes a fix: write it, watch it fail on current or reverted code, then fix. It joins the score permanently, so the same class cannot return unseen.
5. mod_completion.py (e638d40550) can read the score from the SelfTest's "PlayerTruth_" cases and the art sweep's exit, and report it per mod.

Today, FlowWorks pits/ladders/pipes/hoses/levelling score **18/19 offline**, with all probes biting (PT17 open: PIPE_ELBOW_FIX_SEAM_JOGS), and **live 0/6 recorded**.

The answer to "can we even?" is yes, for the sweepable class. Four of his five complaints were properties a program can state and sweep exhaustively in seconds to a minute. The open risk is the render and live layer (R1 to L3), where a cheap version would be a scripted screenshot per truth that a judge reads.
