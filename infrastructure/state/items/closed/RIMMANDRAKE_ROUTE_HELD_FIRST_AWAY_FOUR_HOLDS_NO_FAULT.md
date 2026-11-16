# RIMMANDRAKE_ROUTE_HELD_FIRST_AWAY_FOUR_HOLDS_NO_FAULT

## spec
`restart:<seat>:held_first` (seat_restart.py `_held_tell`) is a first-hold courtesy note: one Conductor-log line
(`raise_first`), once per restart. It has no route of its own, so it falls through `restart:*` into a seats
incident for Operations. seats-20261115234127 re-joined and escalated to the owner's rung on four such holds
(2026-11-16 02:06, 04:43, 06:23, 09:42Z), each a background command the restart waited on, none a fault.
The bound-exceeded alarm `restart:*:held` already routes program. Route `restart:*:held_first` program too,
above `restart:*`.

## verify
`python3 src/RimMandrake/rimflow/selftest_incident.py` gains a check that `restart:BENCH:held_first` routes program
while `restart:BENCH:clone_unlanded`, `hard_stuck` and `orphan` still reach a seats incident.

## criteria
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_incident.py` exits 0; the new check fails on base
bb95b7bb56 (watched) and passes after the route is added.

## refs
file: src/RimMandrake/rimflow/alarm_routes.json
file: src/RimMandrake/rimflow/selftest_incident.py
