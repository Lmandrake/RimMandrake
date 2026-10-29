## spec
Filed by the Producer, Producer weekly plan 2026-10-29 (run folder D:\ClaudeWork\rimmandrake\producer\2026-10-29T0045Z_weekly), goal 2. Broken: RM_Fill_Water, RM_SlimeGreen, RM_Tar, liquidWakesEnabled <-
`fw_live_checks.py:W1_wakes_terrain_walked` (2026-10-11, no later run). Cause: UNMEASURED; the row may be stale (17 days, no
re-run) or the wakes may truly be off. First step: re-run W1 on the current build before touching code.

## verify
- L2: `fw_live_checks.py` W1_wakes_terrain_walked PASS on the current build (a pawn walking each of the three terrains
  leaves a wake while liquidWakesEnabled is on; none when off).
- `mod_completion.py FlowWorks` no longer lists the four parts as broken.
- Stopping point: finish.
