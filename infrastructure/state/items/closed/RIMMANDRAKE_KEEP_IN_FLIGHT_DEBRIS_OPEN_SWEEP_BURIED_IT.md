## spec
`wrapup.row_standing()` returns False for a filed clone row while the clone is IN FLIGHT: a process has its cwd
inside it (RIMMANDRAKE_SPARE_LIVE_CLONE_FROM_DEBRIS_FIFTH_RUN_SAME) or a live cleanse run holds its dot-sibling lock
(OPS_WRAPUP_SKIP_CLONES_OF_LIVE_FLEET_RUN, cf4a8a4d02). `sweep()` read that as "every filed row cleared" and moved
the record to resolved/, so once the run ended with its dirt still there, the row never stood again: in flight was
turned into cleared, for good. Found by the Codex review of cf4a8a4d02 in
RIMMANDRAKE_VERIFY_REMOTE_LANDINGS_FOUR_SKIPPED_THE_DOOR; reproduced here on Linux (sweep (1, 0) while the lock was
live, then standing 0 with the lock freed and the clone still dirty; the cwd case identical, so it predates cf4a8a4d02).
Fix: `wrapup.row_in_flight()`; sweep keeps a record open while any of its clone rows is in flight. Standing and
alarm behaviour while in flight are unchanged (the row still does not stand).

## verify
python3 src/RimMandrake/rimflow/acceptance/wrapup_sweep_keeps_in_flight_accept.py   # PASS 2 of 2 in-flight kinds stand again after the run
Watched failing on 988f9fb5ac: rc 1, "FAIL in-flight debris resolved for good by a sweep: cwd, lock".
Also GREEN after: selftest_wrapup_live_clone, _handoff_env, _session_claims, _restore, _void_relaunch,
selftest_settings_fields_batch. selftest_wrapup's W1 FAIL is pre-existing (identical at cf4a8a4d02^ and now).
Expected: 1 pass.

## criteria
- A sweep run while a filed clone is in flight (cwd or lock) leaves its record open; the row stands again once the
  run has ended with the clone still dirty.
