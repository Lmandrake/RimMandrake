# SELFTEST_RUNNER_SPEED_1 progress
- 00:10 started. Baseline profile run in background -> /tmp scratch log.
- 00:20+ baseline running; long pole selftest_deployed_biome_refs.py (scans Steam Mods+Data on drvfs)
- 00:45 baseline: 554s wall (78/80, fail sound_paths, 1 unmeasured); biome_refs 541s long pole. Fixed biome_refs (parallel grep, scandir walk, per-file cache; 541s->177s cold, ~46s warm) and runner (LPT order, live progress, killpg timeouts, TIMEOUT counted separately, 16 workers). NOTE biome_refs now genuinely FAILs: 19 RUT_TheRot refs dangle (orig script fails identically).
- 00:52 final: wall 80.9s (was 554s; reported 30+ min under peer contention + cold workshop scan). 77/80: FAIL biome_refs (19 genuine dangling RUT_TheRot refs, rotsporekit absent), FAIL sound_paths (Wasteland Spacedrone clip, pre-existing), 1 UNMEASURED tool_metadata (no DLL build).
