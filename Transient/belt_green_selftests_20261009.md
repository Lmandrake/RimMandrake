# belt green selftests 20261009
- placeholder_detect: now PASS 0/150 (3 runs); no red reproduced. Nothing changed by me.
- utinnipatches_dump: RED, cause = 668b2663b (today 07:06) lifted the DEPLOY_HOLD on RUT_FoundrySalvageCache + RUT_FoundryFloor_SalvageCache; the load-14 dump (capturedUtc 2026-10-09T01:58:44Z, live game dump) predates the lift, so both defs are absent. Fix = a new live DefDump capture after the deploy (a game load); not done offline. Not weakened.
- run_selftests: 350/353 pass, only the above FAILs. Output: Transient/belt_green_selftests_run_20261009.txt
