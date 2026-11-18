# RIMMANDRAKE_FIX_RUNG_AT_STAMPED_BEFORE_LOCK_WAIT

## spec
Split from `DISPATCHER_FIX_INCIDENT_BELLS_OVERWRITE` (Codex round 4, claim 4), verified red on 28e44286c3.
decide() stamps a ring's rung_at/rung_iso with the tick's start; execute() writes the inbox after the ingest.lock wait (git_lock, up to 90 s outside a beat). A lease the seat takes in that wait is read by handoff_seen() as the ring's hand-off, recording a false 'verified' and clearing the no-hand-off streak. Fix: when the ring is written, move the pending ring's rung_at/rung_iso to that moment (the tick clock plus the real time spent in execute).

## refs
file: src/RimMandrake/rimflow/dispatcher.py
file: src/RimMandrake/rimflow/selftest_dispatcher_incident_bells.py

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_dispatcher_incident_bells.py` exits 0 (its "claim 4" lines ok). Watched red on base 28e44286c3: rung_at stayed the tick start after a 2.2 s lock wait.

## criteria
- after a lock wait, the pending ring's rung_at is at least tick start + the wait, and rung_iso moves with it.

## review
Codex review of the fix, two looks (`D:\ClaudeWork\rimmandrake\scratch\dispatcher_incident_bells_review_20261118\codex_review_1.md`, `codex_review_2.md`); every flaw it found was given a test, watched red, and repaired in the same sha.
- the live tick passes its real clock to execute as its own argument (never in fx, whose emptiness turns on the owed-sources sync), so observation time and a sub-second wait across a second boundary count too.
