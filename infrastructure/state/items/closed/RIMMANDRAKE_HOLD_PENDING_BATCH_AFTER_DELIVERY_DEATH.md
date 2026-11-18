# RIMMANDRAKE_HOLD_PENDING_BATCH_AFTER_DELIVERY_DEATH

When a seat queues a batch and the first job dies of a DELIVERY fault (`testq/invalid_class.py`: stale companion, stale
swap marker, ...), the tick still admits the rest of the batch into the same fault. On 2026-11-12 between
17:14 and 18:03 UTC, 17 jobs from helper waves on the Conductor's PROVE_* items died `companion_stale` one after another;
11:58-12:13 UTC on 11-06, 3 Relentless jobs died the same tier ModsConfig drift. `repeat_guard.py` judges only new
submissions, so it does not stop a batch that was queued before the first death.

## fix

At admission (testq tick step 4), a pending job whose mod's last INVALID is a DELIVERY cause with nothing relevant
changed (repeat_guard.hold over its chains) waits, with that reason in `testq.py list`, instead of running.

## acceptance test

none yet, written by the builder: which release proves a Steve-side delivery fault has cleared (a stager record, a
canary DONE) is a design call. Fixture: the 11-12 17:14-18:03 UTC wave in testq done/.

## built (2026-11-18, f29a2b7680)

The fixture (testq done/, 2026-11-12 17:13-18:03 UTC) showed all 17 deaths were ONE delivery cause, `companion STALE ...
want 7539f4942fa6`, across 5 mods and mostly distinct chains, so the per-mod repeat_guard hold this item proposed would
have stopped few of them. Built instead: admission (testq.admit) holds ANY pending job whose companion is origin/main's
and not yet on SteveDesktop (filler: cancelled, as before; a job whose companion left origin/main: admitted, the worker
judges, as before). The release is the stager's: the job is admitted once that companion is staged; a wait while the
stager's record says staged asks it to re-probe (companion_recheck.json). Waits show in `testq.py list`.

## verify

    python3 src/RimMandrake/Utils/testq/selftest_companion_stage.py

## criteria

The selftest exits 0 with its admission cases ok; watched red on base (AttributeError: no ADMISSION_WAITS / RECHECK).
Live: UNRUN (SteveDesktop lane paused for the 72 h soak until 2026-11-21T03:29Z); the first live reading is the next
`companion STALE` wave: `python3 src/RimMandrake/Utils/testq/testq.py list --state pending` shows `waits: companion for ...`
and no run of INVALID DEPLOY companion-STALE done records from hand jobs.
