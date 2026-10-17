# WATER_SURFACE_REPAIR_LEVEL_OR_BUST

Owner, 2026-10-17: *"We need VERY smooth water. That's water's one primary characteristic: a level surface... Right now
I'm seeing 0,4,0,0,4 patterns in places that show the water isn't even flowing at all, so let's certainly fix that first."*

## First fix (FOUNDRY helper, 2026-10-17)

Two different 0/4 patterns were in the live walk (`Transient/fw_scenes/live/`, S2 and S5/S6):

1. **Natural pond, 0 4 0 / 4 4 4 / 0 4 4, stock 26 vs cells 24 (S5 A, S6).** Not the current source. The game ran a
   FlowWorks DLL deployed 2026-10-16 23:07 (its `.srchash` has no `RM_PondDepthMath.cs`), before the pond depth model
   (`0b60f7a80`, POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD). That DLL still used the old full-or-empty recession
   (`RM_LiquidStock.Recede`): with lakes running deep, each square weighs its bed (4), so a stock of 26 supports 6 whole
   squares (24) and the 2 levels left over stay in the stock where nobody can see them. `ProofFluidRow` reads a natural
   square as 4 if it is water and 0 if not. With the current source, `StagePond` draws the same stock as one flat
   surface, and the picture always holds floor(stock) (`PondDepth_S1`). Offline, the same scene (`Level_S5A`) ends with
   the pond at [4 4 4 4 4 4 4 4 3], which holds 35 = the stock.
2. **Dug pond, [4 0 4 0] while filling (S2). This was a real kernel defect, and it is fixed.** The water creep hold
   (CANAL_FRONT_FIX_WRONG_END_WETS_FIRST) held every square that received water that pulse. A mouth that its source
   paid every pulse was therefore held every pulse: it never joined its wet region, so the level solve never spread it.
   It filled to the brim beside dry squares on the same floor. Fix (`RM_FlowKernel.frontStamp`): the water hold now
   applies only to the FRONT, meaning a square that was dry when it took its first unit this pulse. The front still
   advances one square a pulse. Thick liquids keep the old whole-square hold. Offline S2 is now [1 0 1 0] → [1 1 1 1]
   → [2 2 2 2] … with every pulse within one level. Before the fix, the offline run reproduced the live trace exactly.

Guards: `Source/SelfTest/LevelSurfaceChecks.cs` (S2, S5A, S5B, S5F at the shipped kernel flags). The Python
`PulseOracle` (`northstar/validation_v2.py`) was changed to the same rule in the same commit, and the kernel matches it
in all five modes on 3000/3000 scenes.

## Open: for the design/ruling pass, not the first fix

- S5 A at the current source: the pond gives ONE level to its 0.5 m canal and then stops: pond 35, canal [1 0 0 0 0 0 0 0 0 0].
  Every surface is within one level, and it meets the redrawn S5 rows: at most 9 canal cells are wet, the pond keeps
  at least 27, and "whether Part A's top 0.5 m ends mostly in the pond or in the canal" is excluded. But the true level
  is −0.53 everywhere, and at a resolution of one level it reads as "a full pond beside a dry canal". The cause is the
  head rule's integer drawdown s (`RM_PondDepthMath.SourceMayGive`): once one level of a 9-square band has gone, s = 1,
  and a D=1 canal's floor is no longer below the surface. A finer depth resolution is the place to show this.
- Live proof owed: deploy the new DLL (game down), then rerun S2, S5 and S6 of `northstar/water_scenes_walk.py`.
