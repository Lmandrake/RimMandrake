# RIMMANDRAKE_UNBLOCK_IDLE_STOP_OWN_RUNNER_REFUSES_SEVEN_TIMES

## spec

`src/RimMandrake/Utils/testq/idle_stop.py` stops a SteveDesktop game that is idle with no job running or pending, "for
the memory". The next job starts the game again.

Measured 2026-11-26 in `/mnt/d/ClaudeWork/rimmandrake/testq/tick.log`: 7 lines `idle N min with no job: not stopped`
(2026-11-26T00:09Z to 10:58Z; Steve2 idle up to 562 min, Steve1 31 min) and 0 lines `stopped for the memory`. Each
refusal reads:

    not stopped (exit 2: ... (game_instance.py stop) (another seat's live hold needs --force; ...)
    host_guard: RUNNER holds stevedesktop gen 2646); asked again in 30 min

`/mnt/d/ClaudeWork/rimmandrake/testq/stevedesktop_idle.json` holds the same refusal (`refused_at`, `why`).

The lane's own RUNNER hold on the game refuses the lane's own idle stop, while no job runs. So an idle game is never
stopped, and it keeps its memory.

The cause is not classed. Two candidates:

- the worker does not release the RUNNER hold when a job ends, so the hold outlives the job;
- the RUNNER hold is meant to stay between jobs, and `idle_stop.py` must stop the game as the RUNNER.

First step: with both games idle, read the lock record on SteveDesktop (holder, generation, holder process alive or
not) and class the cause. This step reads only; it needs no game time.

Not done in the run that filed it: that run was a steward wake session, and its brief barred any live act on a game.
The proof of this fix is a live stop of Steve1 or Steve2.

## refs

file: src/RimMandrake/Utils/testq/idle_stop.py

## verify

Acceptance test: none yet, live-app behaviour with the cause not classed. After the cause is classed, the fixer writes
an offline selftest of `idle_stop.py` with a RUNNER hold and no job. That selftest must read "stopped", and it must be
red on the base commit.

Live check: `grep -c 'with no job: stopped for the memory' /mnt/d/ClaudeWork/rimmandrake/testq/tick.log` reads 0 at
filing. After the fix and one idle window, it reads 1 or more.

## criteria

- An idle SteveDesktop game with no job running or pending is stopped by the tick.
- A game that a job or a helper drives is not stopped.
- The next job starts a stopped game.
