## spec
The Stop hook `.claude/hooks/handoff_restart.py` treated a headless Dispatcher role run (env `RM_ROLE_UNIT`, window
'ROLE Conductor ...') as the BENCH seat window: its HANDOFF READY requested a seat restart, seat_restart refused
("this window is 'ROLE Conductor rm-role-conductor-1794788785', not 'CONDUCTOR' / 'AGENT BENCH'"), and the hook blocked
the turn, heading to the restart:BENCH:handoff_refused alarm at 3 blocks. A role run is ended by its own unit
(wrapup.py already keys it as unit:<RM_ROLE_UNIT>), so `on_stop` returns "role" and does nothing when RM_ROLE_UNIT is set.

## criteria
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_handoff_restart.py` prints PASS (case "a role run's HANDOFF
READY: no check, no request, no block"). Watched fail on the base: TypeError, on_stop() got an unexpected keyword 'env'.
