## spec
Filed by the Producer, daily run 2026-10-29 (run folder D:\ClaudeWork\rimmandrake\producer\2026-10-29T1601Z_run), goal 2
of CONDUCTOR_GOALS block 1 ("the 14 broken parts ... fixed, each proved in game").

LIQUID_WAKES_FIX_FOOTPRINTS_GONE_QUIET, GLOWTANK_SALT_FIX_ONE_PINCH_ONLY, PIT_ENTRY_PROVE_DONE_BUT_STILL_RED and
UNIVERSAL_PIPE_FIX_LAST_RULING_STILL_RED are done, and HOSE_SPILL_FIX_OFF_SWITCH_STILL_POURS is validated (A2 partial),
yet `mod_completion.py FlowWorks` (2026-10-29 16:0xZ) still lists 13 broken parts, because the part's LATEST L2 row is
the old failing one: the scripts that hold those rows were not re-run on the current build.

Rows to re-run on the current build (each is the broken part's source row in mod_completion):
- `fw_live_checks.py` W1_wakes_terrain_walked (RM_Fill_Water, RM_SlimeGreen, RM_Tar, liquidWakesEnabled)
- `glow_tank_live.py` GLOWTANK_SALT_DRAWN_ONE_UNIT, GLOW_TANK_LIQUID_FEED_1 A2 (RM_Fluid_BoilingWater, RM_Liquid_BoilingWater, RM_WaterBoiling, RM_LiquidTank)
- `fw_live_checks.py` L5_switched_off_hose_spills and HOSE_SPILL_FIX_OFF_SWITCH_STILL_POURS A2 (RM_Liquid_FreshWater)
- the ladder / ramp rows of PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH and WATERED_PIT_FIX_NO_WAY_IN (RM_Ladder, RM_PitRamp)
Not in scope: the grate rows (GRATE_FIRE_FIX_SOLID_DECK_BURNS_TOO, waiting on a design ruling).

## verify
- L2: each row above re-run on the current build in one game-up; each reads PASS, or MOD-FAIL filed as its own item
  with the cause, or UNMEASURED with a named reason. No row's bar is changed here.
- L0: `mod_completion.py FlowWorks` re-run afterwards; every part whose row passed no longer lists as broken.
- Stopping point: finish.

## criteria
- A1 L2: every listed row re-run on the current build, each PASS, MOD-FAIL (filed) or UNMEASURED with a reason
- A2 L0: `mod_completion.py FlowWorks` no longer lists as broken any part whose row passed in A1
