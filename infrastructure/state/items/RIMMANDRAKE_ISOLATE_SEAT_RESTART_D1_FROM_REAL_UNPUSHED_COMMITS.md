## spec

`selftest_seat_restart.py` D1 (`_deferred`) runs `seat_restart request`, which calls `publish_owed_shard(seat, REPO)`;
that reads the REAL clone's unpushed commits (`_other_unpushed`) and prints their paths. So the test's verdict depended
on what the running clone had unpushed: on 2026-11-17 ./publish refused because the unpushed item
`RIMMANDRAKE_UNLOCK_REPIN_VOIDED_EXAM_NEXT_OPEN_REFUSED.md` put the word REFUSED into the print and D1 checks
`"REFUSED" not in out`. Fix: `_deferred` fakes `_other_unpushed` with a fixed path, so the real clone never reaches it.

## criteria

- D1 passes whatever the running clone has unpushed.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_seat_restart.py` prints `PASS: 0 failure(s)` (1 test) in a
clone holding an unpushed commit whose path contains REFUSED. Watched it fail before the fix in exactly that state
(`FAIL  D1 4 live helpers and a dirty shard: DEFERRED`, 1 failure).

## refs

file: src/RimMandrake/rimflow/selftest_seat_restart.py
