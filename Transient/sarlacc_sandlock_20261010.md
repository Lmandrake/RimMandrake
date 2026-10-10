# Sarlacc swimmer sand-lock halt (2026-10-10)
Owner card: RM_SandLockCondition also stops the young sarlacc swimmer (road and seep modes).
Code: `RSW_SandLockHalt` in `src/RimStarWars/Sarlacc/Source/RSW_SwimmerRoad.cs`; job giver returns a Wait job while
`RM_ConditionGround.SandLocked(pawn.Position)` (gated by sandLockEffectsEnabled); the 250-tick map-component pass ends
an in-flight Goto, throws churned dust at its cell, and messages stall and release once each.
All numbers (250-tick wait, puff count/colour) PROVISIONAL. Lock tests the swimmer's own cell (sand terrain set).
Validation: `ash_act_problems` + `selftest_longshade_ashact.py` (4 new planted defects). Owed L2: swimmer under a live lock.
