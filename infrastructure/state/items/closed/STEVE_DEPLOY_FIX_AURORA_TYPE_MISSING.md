# STEVE_DEPLOY_FIX_AURORA_TYPE_MISSING

## proof (corrected 2026-11-17, drain of the retired judge)
    python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/modcheck/selftest_modcheck_deploy_closure.py

Measured 2026-11-17: rc=0, RESULT: GREEN.
Evidence: /Users/mandrake/ClaudeWork/scratch/rm-drain-logs/proofs/STEVE_DEPLOY_FIX_AURORA_TYPE_MISSING.txt

The code fix landed at 73760d1e3d (`modcheck/runner.py` +28: deploy closure carries closure members' own hard
deps, plus the selftest case), under the sibling item STEVE_LANE_UNSTICK_BRAKED_UNOWNED_D283.

## why this is ready, not done
The green selftest proves the closure logic now carries the dep; it does not prove the Steve host has the
file. The original fault was an ABSENT WeatherSuite DLL on the Steve host, and that is cured by running the
deploy, not by a selftest: `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod <name> --apply` on the
host, then re-reading the Aurora type. Writing a file is not deploying it. That step is unreachable from a
Mac clone with no C:\ path.

Next worker (on the Steve host): deploy, then confirm the Aurora type resolves in a load with no red.
