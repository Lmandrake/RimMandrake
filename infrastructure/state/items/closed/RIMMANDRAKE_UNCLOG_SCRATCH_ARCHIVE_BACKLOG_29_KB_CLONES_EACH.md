# RIMMANDRAKE_UNCLOG_SCRATCH_ARCHIVE_BACKLOG_29_KB_CLONES_EACH

## spec

## Finding (Operations, incident disk-20261115210535, measured 2026-11-16 20:10 PST)

The scratch cleaner (`src/RimMandrake/Utils/scratch_reap.py`) archives stale helper/test clones more slowly than they are made, so its backlog grows instead of draining:

- Clone rows judged ARCHIVE rose 149 -> 1131 across the eight apply runs 12:00-19:03 PST (`~/.local/state/rm-scratch-reap/runs.jsonl`); in the last run all 1131 were `deferred` past the time budget (run took 1826 s) and only 64 were archived.
- Most are tiny (~29 KB) `tmpXXXXXXXX` clones that selftests and role runs make under `~/.seat-tmp/BENCH/` and `~/.seat-tmp/runs/<unit>/`; their commits are unpushed by construction, so each needs a bundle.
- They also inflate `selftest_stale`: of 1222 fixtures past the 24 h TTL, 1201 are dirs `sweep_fixtures` hands to the clone judgment (`keeps_work`), leaving 21 it could reap itself. So `selftest_stale` (line 500) and `deferred` hold the `scratch:sanity:*` alarms open while the disk is at 33.5%.
- Separately, `session_stale` (203, line 100) is raised by sessions every detached helper's own `claim`/`start` event names (`"session": <uuid>` in the ledger), which `ledger_mentions` holds for `MENTION_DAYS` (7). Sessions go stale at 24 h, so each one is refused for 6 days by design.

## Fix (the fixer picks; none is decided)

1. Archive throughput: bundle many small clones per run cheaply (one batched pass, or archive the smallest first so the count falls), or treat a mkdtemp clone under a test run's own tmp root as a disposable fixture after a one-line bundle.
2. Make `selftest_stale` count only fixtures `sweep_fixtures` can act on, and leave the handed-over ones to the clone counts.
3. Do not let a helper's own `claim`/`start` `session` field pin its session dir for 7 days once the item is closed (or count those as held-by-design, not stale).

Acceptance test: none, the throughput fix is a design choice the fixer makes. The live oracle: `last_run.json` `deferred` reads 0 and the ARCHIVE count falls in three consecutive apply runs, and `sanity.json` start `selftest_stale` stays under 500.
