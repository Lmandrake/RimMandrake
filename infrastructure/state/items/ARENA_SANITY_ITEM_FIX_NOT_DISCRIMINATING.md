# ARENA_SANITY_ITEM_FIX_NOT_DISCRIMINATING

## Finding
The census sanity item STEVEDESKTOP_WORKER_BUILD_DURABLE_ATTEMPTS's check selftest_steve_worker.py fails at the fix too under
the judge route (fail/fail; vet cache /mnt/d/ClaudeWork/rimmandrake/arena/judge/vet_cache.jsonl), so `arena_tasks.py census`
(default --sanity) exits 2 on SANITY now that the vet gates the pool. RP_TANKS_ROW_FIX_LEVELS_WHAT_RULING_FORBADE is the only
labelled task that survives the vet (pass at fix, fail at base).
## Done when
Either the sanity item discriminates again after ARENA_RUNNER_FIX_FROZEN_PATHLIB_DENIED / ARENA_TREE_FIX_OMITS_CHECK_READ_PATHS,
or the sanity default moves to an item that does (TANKS_ROW is a candidate), with a selftest.
