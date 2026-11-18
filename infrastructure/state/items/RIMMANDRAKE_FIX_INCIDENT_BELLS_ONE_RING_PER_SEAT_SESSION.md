# RIMMANDRAKE_FIX_INCIDENT_BELLS_ONE_RING_PER_SEAT_SESSION

## spec
Split from `DISPATCHER_FIX_INCIDENT_BELLS_OVERWRITE` (Codex round 4, claims 2 and 3), verified red on 28e44286c3.
Two incident doorbells for one seat in one pass each call do_ring on the same inbox file (one per seat): the second destroys the first. And an incident ring carries no session_id, so a `claude -p` child that re-armed the seat's doorbell takes it (doorbell.take_ring only skips a ring addressed to another session), the case one_seat() refuses for ordinary rings. Fix: a pass's bells for one seat go out as ONE ring carrying every text; each ring carries the seat window's session (st seats.<seat>.session_id) when one is known.

## refs
file: src/RimMandrake/rimflow/dispatcher.py
file: src/RimMandrake/rimflow/selftest_dispatcher_incident_bells.py

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_dispatcher_incident_bells.py` exits 0 (its "claim 2 / claim 3" lines ok). Watched red on base 28e44286c3: BENCH rung twice, the first text lost; the ring's session None with sid-window known.

## criteria
- two bells for one seat in one pass: one ring, both texts; a lone bell elsewhere unchanged; the pass still reports each bell;
- a bell to a seat with a known window session carries it; with none, it goes unaddressed as before.

## review
Codex review of the fix, two looks (`D:\ClaudeWork\rimmandrake\scratch\dispatcher_incident_bells_review_20261118\codex_review_1.md`, `codex_review_2.md`); every flaw it found was given a test, watched red, and repaired in the same sha.
- bells collected before a later ring raised are held, not lost; a session not learned this tick (PAUSE, or a read with no id) is not trusted: the bell goes unaddressed.
