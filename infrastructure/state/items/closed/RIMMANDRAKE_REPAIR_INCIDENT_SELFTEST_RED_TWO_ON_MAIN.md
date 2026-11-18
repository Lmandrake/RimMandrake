# RIMMANDRAKE_REPAIR_INCIDENT_SELFTEST_RED_TWO_ON_MAIN

## spec
`python3 src/RimMandrake/rimflow/selftest_incident.py` is red on origin/main (seen 2026-11-16 09:50Z, base bb95b7bb56)
with two checks unrelated to each other:
1. "no alarm site in the tree is unreadable by the census": `Utils/ops_watch.py:1084` (point key Name) and `:1090`
   (point key Subscript) raise alarms with computed keys the census cannot read (ops_watch.py last touched e474d53b19,
   designer stall counts the Codex lane).
2. "every role_launch alarm falling through to cause roles is a reviewed fault": new kind `codex_stop` from
   role_launch.py (last touched 2f14540d72, stage five by program) has no reviewed route.
Fix: make the census able to read the two ops_watch sites (literal kind or a declared kind list), and give
`role:*:codex_stop` a reviewed route in `rimflow/alarm_routes.json` (or add it to the reviewed-fault list with its why).

## verify
`python3 src/RimMandrake/rimflow/selftest_incident.py` exits 0.

## criteria
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_incident.py` exits 0 with 0 FAIL lines; on base it exits 1
with exactly these 2 FAILs (watched 2026-11-16).

## refs
file: src/RimMandrake/Utils/ops_watch.py
file: src/RimMandrake/rimflow/alarm_routes.json
file: src/RimMandrake/rimflow/role_launch.py
