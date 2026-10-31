# ARENA_TREE_FIX_OMITS_CHECK_READ_PATHS

## Finding (BENCH/FOUNDRY vet under judge fidelity, 2026-10-30)
arena_judge.materialise builds only TREE_PATHS (src/RimMandrake/Utils, src/RimMandrake/rimflow) plus the task's area dirs.
A hidden check that reads a file outside that set fails identically at base and fix (FileNotFoundError), so the vet
(arena_tasks.py `vet`, which runs materialise+run_hidden) rejects the task as non-discriminating.
Evidence: D:\ClaudeWork\rimmandrake\arena\foundry_vet\label_probe.txt
- RP_CARBON_PRESS_FIX_NO_WORKGIVER_RUNS_BILLS: selftest_coldstorage.py reads src/RimMandrake/TheSump/Defs/... (not materialised)
- RP_ROAST_STICK_FIX_DISABLED_COOK_STAT_ERRORS: reads src/RimStarWars/Cuisine/Source/... (not materialised)
- RP_MISSION_FIXTURE_FIX_RESEARCH_WINDOW_BLINDS, RP_COLD_INSPECT_FIX_PARTIAL_SAYS_ALL_HELD, RP_STEVEDESKTOP_WORKER_BUILD_DURABLE_ATTEMPTS: fail/fail too.
4 of the 14 labelled tasks are lost this way (the other 9 to ARENA_RUNNER_FIX_FROZEN_PATHLIB_DENIED). 40 of 265 vet records are fail/fail.
## Done when
Decide per task: materialise the paths a check reads (e.g. widen the area to the check's read set, measured by a trace at the fix),
or keep the drop and say so. Then rerun `arena_tasks.py vet` (cache key hashes the judge runner, so a materialise change re-vets) and census.
