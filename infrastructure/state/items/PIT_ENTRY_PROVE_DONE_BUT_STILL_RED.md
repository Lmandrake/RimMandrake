## spec
Filed by the Producer, Producer weekly plan 2026-10-29 (run folder D:\ClaudeWork\rimmandrake\producer\2026-10-29T0045Z_weekly), goal 2. Broken: RM_Ladder <- WATERED_PIT_FIX_NO_WAY_IN (2026-10-24, item done);
RM_PitRamp <- the same and PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH (2026-10-23). A done item whose latest verify is not a pass
is either a real regression or an instrument miscount in mod_completion; separate the two first.

## verify
- L2: a pawn enters and leaves a watered pit by a ladder and by a ramp on the current build (path state read).
- PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH's ramp and lowered-ladder rows PASS (its own verify carries the rest).
- If mod_completion miscounted, the miscount is filed against mod_completion with the evidence.
- `mod_completion.py FlowWorks` no longer lists RM_Ladder or RM_PitRamp as broken.
- Stopping point: finish.
