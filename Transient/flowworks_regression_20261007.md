# FlowWorks north-star v2 regression, 59/0/0 to 50/9/0 (2026-10-07)

This was an offline investigation. No bridge or game was used, and nothing was edited or committed.

## Inputs
- PASS run: `validation_v2_result_20261006T064707.json`, DLL `5d44e05927dc`. That is the srchash at **55e446ee8** (2026-10-06 02:17).
- FAIL run: `validation_v2_result_20261007T140351.json`, DLL `eeeba804299f`. That is the srchash at **f056d3012** (2026-10-07 03:15).
- **21 FlowWorks DLL rebuilds lie between the two stamps**, and no v2 run happened in between. Every commit from 790fd4e8d to f056d3012 is therefore unvalidated by v2.
- Env difference: the FAIL run also loads `mandrake.rm.gimmesomeslack`. 169e004f6 added it to the flowworks tier because JawaBench needs it. I found no evidence that it affects the result.

## What each failing row read
| row | PASS run | FAIL run |
|---|---|---|
| P3_walk_in_held | walked in True, held, 1 descent, fall 4.9 | **walked in False**, pawn never entered (ended (166,103), its spawn spot) |
| P4_ladder_frees | held False lip 8/8 | held None, "pawn off-cell" (cascade from P3: the pawn was never in the pit) |
| P4b_ladder_raised_strands | inspect "Ladder_raised: ..." | every semantic check passes (held True lip 0/8 canReach False; lowered held False lip 8/8). It fails on the **inspect-string match only**: the text now reads "Ladder up: ..." / "Ladder down: ..." |
| P5n_own_faction_carveout | colonist in True | **colonist in False** |
| X1_pawn_height_ladder | D1..D4 = 0.3/0.6/0.9/1.2 | D1 0.3, then **D2, D3, D4 all sink=0.5 drawDz=-0.5** |
| X2_pawn_lowers_walking_in | arrived True, sink 0 to 1.2 | **arrived False**, sink 0 to 0 |
| X3_pawn_rises_walking_out | sink 1.2 to 0 | sink 0 to 0 (cascade: X2 never reached D4) |
| X4_pit_wall_over_head | drawn 1.2 down | drawn 0 down (cascade from X2; would still fail at 0.5 because of H2) |
| X5_slime_occupant_below_surface | 1.2 down | **0.5 down** |

There are two independent signatures here: **pawns never enter the open D=4 cell**, and **the sink is capped at exactly 0.5**.

## Hypotheses (ranked)

### H1: the open-pit path veto (790fd4e8d, 2026-10-06 11:49). Covers P3, P4, P5n, X2, X3 and the walk half of X4.
- `Source/Superdeep/RM_PitPathing.cs:191-240` (TryPlan) and the Harmony prefix on `Pawn_PathFollower.GenerateNewPathRequest` at `:301-330`. Any route that starts outside a pit and ends on an OPEN superdeep cell goes to `RM_PitTrapMath.PlanRoute`.
- `Source/RM_PitTrapMath.cs:244-269`: when the start is not a pit and the destination needs the pit with **no ladder in that pit**, the route is `PitLeg.AvoidPits`, which per the code comment means "no way down: the pathfinder refuses". The open-pit grid makes the cell impassable (offset >= 10000). The veto has no exception for faction, draft or forced order.
- The harness walks a drafted colonist (`jawa/order_pawn draft=True`) onto (166,100) D=4, onto (172,100) D=4, and along the X strip to (134,70) D=4. None of these pits has a ladder, so each order is refused and the pawn stays put. That matches "arrived False" and the pawn ending on its spawn cell.
- **This is ruled behaviour, not an accident.** FLOWWORKS_PIT_FALL_ONLY_FORCED_1 (owner, typed 2026-10-06): *"You can't fall in by careless colonist pathing. Only if they get blown/forced in do they fall."* So P3, P5n and X2 encode the pre-ruling model, in which a colonist walks in. No v2 run happened after 790fd4e8d, which is why this was never seen.
- Open question for the owner: is a drafted, explicitly ordered move "careless pathing"? The code treats it as such. I cannot settle that from the ruling text.
- Minimal fix: **harness, not mod.** Get the pawn onto the floor by a route the ruling allows:
  - X2/X3/X4: put a lowered `RM_Ladder` on the strip's D=4 cell (or a D=1..3-only walk plus a placed D=4 pawn), so the walk ends with `StepTo` the ladder.
  - P3 must become a *forced* entry (the row's own premise of a fall plus a hold), for example a flyer or knockback arrival that `RM_Patch_PawnFlyer_LandInPit` counts.
  - P5n needs a ladder or a forced entry with the carve-out on.
  - Whoever rewrites the rows should check that the row-to-bar mapping in validation_v2.py `:763-772` still says what the north-star bars say.
- Single live re-check: before the walk-in order, `jawa/spawn_batch ops="RM_Ladder:166,100"`, then `jawa/order_pawn` a drafted colonist to (166,100). If it arrives, the veto is the only blocker. If it does not arrive with a ladder present, H1 is wrong.

### H2: the lip clamp in a100d8e2e (2026-10-06 23:13). Covers X1 and X5, and would also fail X2 and X4 once H1 is fixed. This is a genuine conflict with validated bars.
- `Source/Superdeep/RM_PitDepthDraw.cs:83-104` (`Clamped`) scans south from the pawn's cell to the first shallower cell and sets `lipZ = cand.z + 1`. `Source/RM_PitDrawMath.cs:69-81` (`ClampSinkToLip`) caps the sink at `room = (c.z + 0.5) - lipZ`.
- For any cell on the **south row** of a dug region, `room = (c.z+0.5) - c.z = 0.5`. The X scenes are a **1-cell-wide strip** at z=70, and (x,69) is undug. Every strip cell is therefore a south-row cell, so D2/D3/D4 cap at 0.5 and D1 (0.3) escapes. The FAIL numbers show exactly that.
- X5's hare on (134,70) reads 0.5 for the same reason.
- `ProofPawnSink` (`RM_PromotionProofs.cs:70`) reads the real `RM_Patch_PitDepthDrawOffset.SinkOf`, so this is the mod's real draw, not a harness artefact.
- Side defect: `wallOverHead` is still computed from the unclamped depth (`RM_PromotionProofs.cs:71`). X1 shows `wallOverHead=1.2` beside `sink=0.5`, so the proof is now inconsistent with what is drawn.
- **This is a design conflict, not a typo.** The commit's goal is that a D4 pawn on a pit's south row must not draw outside the opening. That cannot coexist with the north-star bars "D4 drawn 1.2 down" and "wall >= 1.2 x a person's height" in any pit 1 or 2 cells deep north-south, or on any pit's south row.
- Minimal fix options, which the owner should choose between; I will not pick one by grader convenience:
  - (a) Revert the clamp and solve the owner's muffalo case with the lip cover alone. The cover already spans the real sprite after the same commit.
  - (b) Clamp only when the sprite's drawSize exceeds the cell, so a muffalo is clamped and a colonist or hare is not.
  - (c) Re-scope the bars to interior cells and re-validate on his word.
  - Do not move the X scenes to a wider pit just to make the rows pass. That would hide a real draw behaviour from the bar.
- Single live re-check: `ProofPawnSink` on a hare in the **interior** of a 3x3 D=4 pit should read 1.2. On that pit's south row it should read 0.5. Both readings together confirm the clamp alone.

### H3: inspect-string rename (169e004f6, 2026-10-06 22:25). Covers P4b only. The harness is stale.
- The keyed string `RMFlow_LadderRaisedInspect` is now "Ladder up: nobody can climb down or out." (`Languages/English/Keyed/FlowWorks_Keys.xml:15`). The lowered text became "Ladder down: ...".
- validation_v2.py `:2267-2270` requires the substrings `"raised"` and `"lowered"` in the inspect text. Every semantic part of P4b passes.
- Fix: match "up"/"down", or better, `lr["raised"]` alone. Offline only, no live check needed.

## Ruled out or not implicated
- **The sluice commits fe20a045f and f056d3012** change only door and flow logic (`RM_FlowDoors.cs`, `RM_FlowKernel.cs`, `Flood_FlowWorks.cs`) and add 7 lines to `RM_PitTrapMath.cs`. None of that touches PlanRoute or the sink. Not implicated.
- **The container-materials commits** (6b67d6bd2, 374b8275f, 69966f276 and the rest) are defs and recipes. Not implicated.
- **3425843d9 (step cost)** changes only the walked-step base cost through a prefix on `PathGrid.CalculatedCostAt` (perceivedStatic=false). Passability is unchanged, so it cannot stop descent.
- **8991803ee and c4c481143** affect lip-cover drawing for shallower pawns and cover breaking. Neither touches the sink value or the route.

## What I could not determine
- I did not check against live behaviour. Everything above is from the result JSONs, the source and the diffs.
- I did not confirm that the strip's D=4 cell (134,70) is the only superdeep cell on the X walk. That follows from `IsSuperdeepExcavation` (depth >= Superdeep), which I did not dereference.
- I did not try to find whether a P-scene pit has any ladder before the P3 order. The P3 detail and the code both say none.
- The owner has not said whether a drafted direct order counts as "careless pathing". That decides whether H1 is "harness stale" or "mod over-broad".
- I did not find the item file for PIT_LIP_OCCLUDES_OUTSIDE_1 under `infrastructure/state/items`.
