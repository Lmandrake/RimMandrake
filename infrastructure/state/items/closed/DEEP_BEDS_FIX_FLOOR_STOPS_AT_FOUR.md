## spec
found-by: BENCH bridge run (2026-10-23, run 1 driver 4, HEAD 39ec8aac5e deployed, 14-mod fw_gss_sitting).
Class: MOD presumed (prior PASS now FAIL), unproven.

Repro: `python.exe src/RimMandrake/FlowWorks/northstar/deep_lake_proof.py <out> --fresh-map` from a D: export.
Evidence: `Transient/bridge_run_1_20261023/deep_lake3.json`, `Transient/bridge_run_1_20261023/deep_lake3.log`.

The DEEP_LAKE_FIX_PAINTED_LAKE_JOINS_WILD harness fix worked: `BODY id=1 cells=5184 limitless=False truncated=False`,
and the painted lake reads `deep=4356 shallow=828`. But the body reads `deepest=4` and `bedSum=19080` with
deepBedsEnabled=True, lakeDepthScale=2, deepBedMaxDepth=20 set by the proof. Both readbacks are in the json
(settings_before / settings_restored).
So DL_lake_over_4000_is_limited FAILs on deepest>4, and DL_drained_reads_gradual_hollow FAILs (deepestDry 4,
lakebedAbyss 0). Both colonist rows are UNMEASURED ("no dry square past bed 4"). shallow_dries_first and
refill_restores_exact_shape PASS.
The 2026-10-22 belt on the same proof read deepest=12, PASS (northstar/deep_lake_result_20261022T1200_belt.json).
First thing to check: RM_LiquidStock.cs:236 lays deep beds only when `!AnyMovingWater(map, found)`. If a moving-water
square sits inside or touches the painted rect on this fresh map, the result is SITE, not MOD. Read
AnyMovingWater for body 1 live before you change code. Blocks DRAWDOWN_DIAGNOSE_THIRTEEN_BEFORE_TWELVE A1.
