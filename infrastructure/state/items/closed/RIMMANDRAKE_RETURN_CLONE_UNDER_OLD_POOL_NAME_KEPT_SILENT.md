# RIMMANDRAKE_RETURN_CLONE_UNDER_OLD_POOL_NAME_KEPT_SILENT

## spec

`src/RimMandrake/rimflow/run_store.py` `Effects.remove_clone` returns `None` at its first line when the clone path
does not start, as text, with `<pool root>/clones/`. It writes no journal line for that refusal.

Commit `80aac7adf0` (2026-11-26 1:49 AM PST) moved the pool root from `/home/mandrake/rm/relentless` to
`/home/mandrake/rm/runs`. `/home/mandrake/rm/relentless` is now a symlink to `runs`. A run that started before the
move has a record whose `clone` field holds the old name.

Failure that happened, 2026-11-26: run `rm-detached-bench-rimmandrake-drive-explosiveknockback-in-1795685337` has the
record clone `/home/mandrake/rm/relentless/clones/RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_VISIT_TWO_RUN_TWO.det`.
The pool root reads `/home/mandrake/rm/runs`. Its return printed `KEPT ... the clone stayed: its bundle or its removal
failed (alarm on the relentless journal)` three times (3:20 AM, 3:35 AM and 3:43 AM PST). The journal
`/home/mandrake/rm/runs/store/journal.jsonl` holds no alarm line for it. At 3:35 AM PST `left_open_continue` refused
the continuation of the Explosive Knockback visit, because the clone was held. The clone is clean and level with
origin, and no process holds its lock.

Fix: `remove_clone` compares real paths (symlinks resolved on both sides). Any refusal of a clone writes an alarm line
that names the clone and the reason. Look for the same text compare of a pool path in the files of the refs; fix each
one that the same case reaches.

## refs

file: src/RimMandrake/rimflow/run_store.py
file: src/RimMandrake/rimflow/detached_helper.py

## verify

A new selftest case: a clone whose path goes through a symlink to the pool root is bundled, then parked or removed.
The case fails on the base commit `494166fef6` and passes on the fix.

Live, seen red at 3:43 AM PST 2026-11-26:
`python3 src/RimMandrake/rimflow/detached_helper.py return --unit rm-detached-bench-rimmandrake-drive-explosiveknockback-in-1795685337`
prints `KEPT`. On the fix it gives the clone back.

## criteria

- A clone under the pool, named through a symlink to the pool root, is returned like any other clone.
- A clone outside the pool is still refused, and the refusal writes one alarm line with the clone and the reason.
- The clone of the run named above is back in the pool, or removed, and its lock file is gone.
