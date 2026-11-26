# RIMMANDRAKE_RENAME_RUN_STORE_AND_POOL_OFF_TICK_PATH

## spec

The run store (`/home/mandrake/rm/relentless/store`, about 17 GB: items 8.8 GB, orphans 7.0 GB, `journal.jsonl` written
2026-11-19) and the detached-helper pool (`/home/mandrake/rm/relentless/clones`, about 264 entries) are live and named
for the retired Relentless Pipeline. So are the env names `RELENTLESS_ROOT`, `RM_RELENTLESS_ROOT` and `RELENTLESS_RULES`
(read in `cli.py`, `evidence_gate.py`, `ops_health.py`, `bottleneck_measure.py`, `ops_lives.py`, `agent_runner.py`), and two
names that nothing sets any more (`RELENTLESS_GEN`, `RELENTLESS_HELP_NONCE`: only readers and `agent_runner.py`'s
pass-through list name them; the note-box hook that needed `RELENTLESS_GEN` went at `d55f855dbd`). Census row "Class 2
NAME ONLY" of `D:\ClaudeWork\rimmandrake\conductor\retired_era_remains_20261119.md`.

Do, in one commit, with no detached run alive (the pool's clones moved or reaped first): choose neutral paths (for example
`/home/mandrake/rm/runs/store` and `/home/mandrake/rm/runs/pool`), move the trees, change `run_store.DEFAULT_ROOT`,
`detached_helper.pool_root` / `RM_DETACHED_POOL`, every unit and every live reader; rename the env names (keep the old
name read as a fallback for one release only if a unit outside the repo sets it); delete the two dead names. History
(ledger, conversations, closed items, handoffs, recorded fixtures and run results) keeps the old path.

Found by `RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS` (2026-11-19, BENCH); index: `design/RimMandrake/retired_eras_index_2026-11-18.md`.

## verify

Acceptance test, run from the repo root:

    git grep -l -E 'rm/relentless|RELENTLESS_(ROOT|RULES|GEN|HELP_NONCE)' -- src .claude bin \
      ':!*corpus*.json' ':!src/RimMandrake/rimflow/modledger_readings' ':!*_result_*'

prints nothing and exits 1 once done. Watched failing 2026-11-19 BENCH at `fbdf50a5b2`: 42 files listed, exit 0.
Plus `grep -l rm/relentless ~/.config/systemd/user/*` prints nothing.

## criteria

- A1: no live file names `rm/relentless` or a RELENTLESS_* env name (the grep above lists nothing).
- A2: a detached helper launched after the move runs in the new pool and its run lands in the new store (one real launch).

## refs

file: src/RimMandrake/rimflow/run_store.py
file: src/RimMandrake/rimflow/detached_helper.py
