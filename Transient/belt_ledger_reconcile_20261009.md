# Ledger shard reconcile 2026-10-09

Diff of shared-clone working copy vs origin/main (exact line identity; all local-only lines parse as JSON).

| shard | local-only | origin-only |
|---|---|---|
| ledger/events/FOUNDRY | 7 | 14 |
| ledger/events/BENCH | 0 | 52 |
| ledger/events/OWNER | 0 | 0 |
| art/events/BENCH | 0 | 53 |
| art/events/FOUNDRY | 0 | 0 |
| code_review/BENCH | 0 | 3 |
| code_review/FOUNDRY | 0 | 6 |
| code_review/SEED | 0 | 0 |

BENCH shards untouched (report only). Shared working-copy file NOT modified; the next pull reconciles it.

Landed: the 7 local-only FOUNDRY lines (note PATCH_MAYREQUIRE_GUARD_INERT_1, 2 bridge, 2 game, file events for NINEFAULTS_RITE_START_RECHECK_1 and THERETURN_RITE_START_RECHECK_1) appended in order to origin's version via private clone ~/.seat-tmp/ledger_clone.
