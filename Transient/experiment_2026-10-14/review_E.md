# Review E: full-file reviews (BENCH, 2026-10-15)

Checks: correctness; static per-game state across reloads (lesson 20261015T025544Z); hostiles kept off ladders; raised ladders block everyone.

## src/RimMandrake/FlowWorks/Source/Superdeep/RM_PocketGrid.cs: FULL review, CLEAN (all 425 lines)
- Static state: `grids` is a ConditionalWeakTable keyed by Map (a reload or new game makes new Map objects, so no carry-over); `settingsSalt` only counts up; `maxFlightTime` caches a StatDef (defs do not change within a session). No table keyed by thing or pawn IDs.
- UsableLadderIn: a pawn query uses RM_LadderRules.LadderLetsOut → RM_PitTrapMath.LadderUsable(raiseLowerOn && raised → false; prison door → MayClimb). Hostiles are still off ladders on their own queries. A pawnless query uses RM_ClimbJoins.LoweredLadderAt (`!EffectivelyRaised` = !(raised && ladderRaiseLowerEnabled)), the same raised test as the pawn path, so a raised ladder blocks every query.
- The pawnless "any lowered ladder" only reaches vanilla's pawnless StartPath precheck. Hostile movement is still decided by its own CanReach, the ladder offset grid and the step floor.
- ProofPocket comp is never -1 (InBounds checked); BandOf returns null for k ≥ MaxDepth and every caller handles it.

## src/RimMandrake/FlowWorks/Source/RM_PocketGridMath.cs: FULL review, CLEAN (all 200 lines)
(The brief put it under Superdeep/; it lives in Source/.)
- Label: a BFS with a ramp join in either direction; queue size n is enough because each cell is labelled once. LadderIsAWay / ReachVetoed match the caller in RM_SuperdeepTrap.RelativeVeto (sameComponent=false is passed after the same-component early return). Trapped and BandFor are correct. No static state.

## src/RimMandrake/GimmeSomeSlack/validation_aerial.py: FULL review, CLEAN (all 814 lines)
- rebuild_m2's RuntimeError("HARNESS: ...") is correct. Under proof_all, `block()` turns it into one AERIAL_block HARNESS FAIL row. When it fires (M14/M14b/M15), the only probe setting changed is skipreseed, which is already back to false, so no setting leaks.
- Not significant, left as is: an exception anywhere in run_live drops the rows that block already measured (proof_all keeps only the block FAIL row). This predates the change and is common to every block. The direct `oc[O1]` / `ak[M1]` indexing would raise in the same way on a site fault. `lamp_on` at line 179 is computed and never used.
- No per-game static state (a Python harness).
