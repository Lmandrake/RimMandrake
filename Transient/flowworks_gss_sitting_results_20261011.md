# FlowWorks + GSS live sitting results, 2026-10-11 (FOUNDRY)
Tier fw_gss_sitting. Skeleton first; sections filled as run.

## Step 0 deploy
Deployed FlowWorks, ExplosiveGrowth, composed biomes (applied); GSS and RiverColors already in sync. Deployed FW/GSS DLL hashes equal repo blobs (3c9de555, 8cde82e0). JawaBench companion rebuilt+deployed. modset fw_gss_sitting applied (17 mods). Config backup + sha256: Transient/fwgss_cfg_backup/. Launched via launch_ready.py --profile minimal.
## Watchdog log
(pending)
## A1 log/defs read
READY 87s, pid 6816. Harmony: FlowWorks patched 38 missing 0; GSS patched 25 missing 0 (plus other biome mods all missing 0). 0 lines: RM_Liquid_Lava, excludeLiquids, RM_Bottle_, dbh, MatSingle/ResolveIcon/Graphic_Linked; 0 exceptions. 12 Config error lines = 6 defs RM_FE_* (ExplosiveGrowth) 'burnedDef is flammable' x2 (not FW/GSS). Watchdog 13:15: DEAD stale unrelated heartbeat 'situational_rerun' (no runner of ours) - no remedy. QUARRY get_defs sweep: pending.
## A2-A5 map, GREEN-MIN, extension proof
A4 validation_v2 --live --fresh-map: GREEN 61 PASS / 0 FAIL / 0 UNMEASURED (13:21, validation_v2_result_20261011T132117.json, ticks 14089). All criteria-deciding rows PASS (verify to record).
A2: start_debug_game_ready ok via prove_quicktest_world.py (Playing in 11s).

## A6-A11
(pending)
## A12-A15
(pending)
## Findings / blockers
(pending)
preflight O14 failed_ops (no crash path) -> proceeding, judged on A1 log
profile: companion_profile.json test expiry had lapsed (17:00Z); renewed to 02:00Z same campaignSaves (backup in cfg_backup). Run 1 of validation_v2 (131544) was under CAMPAIGN profile -> void
A5 run1 (141116) polluted: Huck BloodLoss surprise from A4 + ActiveFluid already classified -> 103 UNMEASURED, 4 FAIL (1 harness NameError _note in taken_by_land). Rerun on fresh map.

## FINAL (stopped by owner order, 14:40)
PASSED: deploy of FlowWorks/ExplosiveGrowth/biomes (GSS+RiverColors already in sync); A1 Harmony FW 38/GSS 25 missing 0, 0 Lava/excludeLiquids/Bottle/dbh/LinkedGraphic lines, 0 exceptions; A4 validation_v2 GREEN 61/61 (validation_v2_result_20261011T132117.json).
FAILED/FINDINGS: A5 extension_proof run1 (extension_result_20261011T141116.json) polluted (Huck BloodLoss surprise, ActiveFluid already classified): 39 PASS/103 UNMEASURED/4 FAIL; breakdown in Transient/fwgss_extension_nonpass_20261011.txt. Harness bug: NameError '_note' in taken_by_land. plot_C canal_fill_front FAIL (mouth cell F<1 after 3 pulses) not reproduced on a clean map. ExplosiveGrowth: 6 'burnedDef is flammable' config errors (RM_FE_*). Preflight O14 failed_ops (no crash). MakeThing error RM_Bottle_BoilingWater stuff=null in log.
Run 2 of extension_proof on a fresh map (stamp in .seat-tmp/ts2) was killed unfinished; no result JSON.
STILL OWED: everything A5 onward (A5 clean rerun, A6-A16), B1/B2, FULL, L3/L4. No rimflow verify recorded (BENCH takes over).
STATE: game RUNNING (fresh debug Desert map, pid 6816), ModsConfig = fw_gss_sitting (17 mods; original backup Transient/fwgss_cfg_backup/ModsConfig.xml and deployed/config/ModsConfig.before-tier-fw_gss_sitting.xml; restore: modset_builder.py --restore). companion_profile.json test renewed to 2026-10-12T02:00Z.
