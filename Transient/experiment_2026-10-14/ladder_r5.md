# Ladder R5 — V2_LADDER_ROWS_DIAGNOSE_STAGE_FRIGHT (BENCH builder, 2026-10-15)

## State going in
- P4/P4f/P5n FAIL at ce40347df6; masks measured current (R4). Fault downstream.

## Code path traced (drafted colonist -> cell in D4 pit, lowered ladder)
1. jawa/order_pawn: pawned CanReach (ByPawn) -> TryTakeOrderedJob(Goto). Our RelativeVeto, pawned: UsableLadderIn finds the ladder -> no veto. OK.
2. JobDriver_Goto -> Pawn_PathFollower.StartPath. **Vanilla 1.6 (decompiled, RimSage) checks
   `map.reachability.CanReach(pawn.Position, dest, peMode, TraverseParms.For(TraverseMode.PassDoors))` -- NO PAWN.**
3. Our postfix RM_Patch_Reachability_SuperdeepVeto -> RelativeVeto(p = null): k = person band; start surface comp, dest = pocket;
   dest "way in" required `p != null` and UsableLadderIn(null) returned false by design ("pawnless queries get no ladder") -> VETO.
   Out of the pit: TrappedIn(k, cs, null) = true (no ladder for null) -> VETO. -> PatherFailed, Goto ends, pawn never moves.
4. (Not reached, read and fine) GenerateNewPathRequest seam: colonist MayClimb -> no customizer -> vanilla request; swap gives band 2
   (pit 0x0F, lips open toward it, R4 MEASURED); step floor ForPawn -> LadderLetsOut true; step cost capped 450 by vanilla.

## Findings (MEASURED vs INFERRED)
- MEASURED (decompiled source): StartPath's pawnless PassDoors CanReach; our postfix vetoes pawnless surface<->laddered-pocket both ways.
- MEASURED (offline selftest): the old rule vetoes in (P4/P5n shape) and out (P4f shape); the new rule does not.
- INFERRED: this is the live cause of P4/P4f/P5n. Fits all three: P4f pawn never leaves (out vetoed); P4's colonist then also blocked by
  the occupant (harness note); P5n into an empty laddered pit vetoed. P1/P3/climb_proof never walk a ladder, so they stayed green.
- Not the cause (read): masks/swap, ClosedLadders grid (null for colonists), step floor, step cost, PitRooms region split.

## Offline repro (SelfTest)
- CliffMaskChecks `Pawnless_reach_counts_a_lowered_ladder_as_the_masks_do` (production RM_PocketGridMath.ReachVetoed/LadderIsAWay +
  call-site pins). FlowWorks C# SelfTest 324/324.

## Fix
- RM_PocketGridMath.LadderIsAWay(pawnKnown, lowered, mayClimb): pawnless = any lowered ladder (the masks' structural view);
  RM_PocketGrid.UsableLadderIn uses it; RelativeVeto decides via ReachVetoed, pawnless included. Prison door unchanged for pawned
  queries + ClosedLadders grid + step floor.

## Live check for next round
- Deploy FlowWorks at the fix commit; `validation_v2 --live --fresh-map` phase P: P4, P4f, P5n PASS; P1/P3 still PASS; P4b measured.
- If still red: `jawa/static_call` Verse.Reachability CanReach is not callable pawnless from the bridge; instead read
  `order_pawn` row `curJob`/`note` right after the order (waitTicks=30): curJob null + note "Something ended the job" = pather failed at StartPath.

## Code review (A_flowworks_cs, 5 files) -- full-file, every line
- RM_LiquidNet.cs, RM_PitExposure.cs, CliffMaskChecks.cs (incl. the new case), RM_LadderUtility.cs, RM_SuperdeepTrap.cs (after the
  R5 edit): no significant findings -> mark-clean (BENCH.jsonl). Nits only: RM_SuperdeepTrapState.Tick descent block over-indented;
  RM_HoseLinks signature check is per TicksGame, so a hose change while paused is seen on the next tick (liquid only moves in ticks).
- Made DIRTY by the R5 fix and NOT re-reviewed here: RM_PocketGrid.cs, RM_PocketGridMath.cs (were clean before).
