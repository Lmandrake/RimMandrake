## spec
found-by: BENCH bridge run (2026-10-23, run 1 driver 4, HEAD 39ec8aac5e deployed, 14-mod fw_gss_sitting).
Class: HARNESS (proven by reading the source).

Repro: `python.exe src/RimMandrake/FlowWorks/northstar/deep_stone_live.py <out> --fresh-map`. Evidence: `Transient/bridge_run_1_20261023/deep_stone3.json` (job_probe,
job_order), `Transient/bridge_run_1_20261023/deep_stone3.log`.

DS_superdeep_cut_turns_up_deep_stone is UNMEASURED/SITE: "WorkGiver_DigCanal hands this pawn no job
(shouldSkip=None hasJobOnCell=None deleted=None)". The probe reply has NO workGiver or pawn block. Cause:
deep_stone_live.py:149 calls `jawa/flowworks_job_probe(..., pawn=cids[0])`, but the tool's parameter is
`pawnId` (src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchFlowWorksJobProbeTools.cs:67). The pawn is
dropped, so the WorkGiver half never runs. The same run's `jawa/ordered_job RM_DigCanalJob` was accepted=True,
nowRunningRequested=True. The job gate (job_gate) then rejects a run whose order was taken.
Fix: pass pawnId=, and add a selftest that the probe kwargs match the tool signature. Then rerun --fresh-map: expect
dig accepted, depth 3->4. Keeps DEEP_STONE_FIX_NOBODY_PICKS_UP_SHOVEL and PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS
A2 owed.
