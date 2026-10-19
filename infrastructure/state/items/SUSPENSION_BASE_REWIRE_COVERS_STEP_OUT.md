## spec
Child 1 of `FLOWWORKS_BRIDGES_DESIGN_SPAN_ANYTHING` (stage S0 of `design/RimMandrake/flowworks_bridges_design_2026-10-17.md` §10). Pure refactor, **no behaviour change**.
- Lift `Building_PitCover` (`src/RimMandrake/FlowWorks/Source/Pits/Building_PitCover.cs`) into a span base class
  (deck cell, mass on deck, collapse → descent event); pit covers become its hidden **trap** tier (own look, Q8).
- One read `RM_SpanUtility.DeckedAt(map, c, out float deckHeightM)` replaces "is covered" at the seven call sites
  (`design/RimMandrake/flowworks_bridges_design_2026-10-17.md` §1 table: `RM_PitStepCost.cs:56-78`, `RM_Patch_SuperdeepShooting.cs:93-95`, `RM_PitExposure.cs:33`,
  `RM_PitFillEffects.cs:58-60`, `RM_SlimeSlip.cs:43`, `RM_LiquidFire.cs:506-513, :552-559`). Re-grep at build; do
  not trust the line numbers.
- The read carries a "floor band passes under" flag that is always false for covers (the underpass item sets it).
Dependencies: none; can start now. Art: none. ESTIMATE 1 to 1.5 agent-days, no live time.

## verify
- L1: selftests: every existing pit-cover selftest passes unchanged; new selftest: `DeckedAt` on a cover cell returns
  true, height 0, floor band false; on an open dug cell false.
- L1: `code_review_status.py check` CLEAN on every touched file.
- L2 (folded into the next live session of the core item, not its own load): a cover still holds 40/120/220 kg and
  drops a pawn through the descent event when exceeded (state read: pawn's cell depth after the trigger).
