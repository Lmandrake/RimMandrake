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
