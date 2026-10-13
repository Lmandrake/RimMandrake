# tank loop live proof (2026-10-13 night, BENCH helper)
Item: TANK_LOOP_PROVE_LIVE_DONE_TOO_SOON. Chains: toggle_tank_loop, toggle_bottle_loop. Owner ModsConfig md5 ee01dae9e30d121c78d88e474dacd8e8 before and after (verified).
Build: FlowWorks DLL deployed from HEAD 03fa69c87d (>= 28efd07e01), VERIFIED in sync. Tier ratchet_pilot (22) + mandrake.rm.patches = 23 (`Transient/bench_live_20261013c/ModsConfig.ratchet_pilot_plus_patches.xml`). Code run from git archive `D:\Luke\dev\_rmscratch\night_tank_20261013`. Steam launch, pid 16168, killed by PID.
Evidence: `Transient/night_20261013/fw_live/` tank_proof_run1.log, tank_proof_run2.log, tank_proof_result2.json, Player.tank_proof.log (0 exceptions), deploy_plan_FlowWorks_tank.txt.

## Result
- run 1: bottle_loop_on/off PASS; tank loop chain FAIL in setup: `ProofTank 155,124;Store;RM_Liquid_FreshWater;100` -> "REFUSED: tank would not take 100". HARNESS defect: the chain staged 100 units into an RM_LiquidTank whose capacity is 80 (pond-unify, 2026-10-12).
- fix: TANK_STAGE_UNITS = 60 in extensions.py toggle_tank_loop; selftest fake ProofTank now refuses > 80 so the class is caught offline.
- run 2 (extension_proof --live --chains toggle_tank_loop,toggle_bottle_loop): 5/5 PASS, all_green, runValidity CLEAN, 176 s. Real movement in the evidence: draw-out 60 -> 59 units with the loop ON; pour-in Empty -> 1/80; loop OFF: 60 stays 60 for 3000 ticks, Fill tank stays empty.
## Harness defects (named)
1. toggle_tank_loop staged 100 units into an 80-unit tank (fixed above).
2. The guard / site-backup defects of part 1 (TESTENV_GUARD_UNSTICK_..., TESTENV_SITE_BACKUP_REPAIR_...), closed at 03fa69c87d.
## Threats: none new. A WEDGED belt_watchdog reading at +76 s of cold load was just loading; HEALTHY afterwards.
## Teardown
modset_builder --restore verified md5 ee01dae9; game killed by PID 16168; `./game --why "tank loop proof done" down`; bridge released.
