# RIMMANDRAKE_TRACE_ROLE_RUN_LOST_DONE_STRANDING_NOW_CAUGHT

## spec
Split from RIMMANDRAKE_LAND_DESIGNER_RUN_DONE_BUT_NEVER_HARVESTED (closed at 5d1e71e53d with its part 2): DesignerCodex
run `rm-role-designercodex-1794846919` (Cauldron stage 3, 2026-11-16T16:35:19Z) finished `subtype: done` and
stage.json advanced to stage 4, but the Dispatcher journal holds only its `role_launch` line: no `role_done`, no
`role_stage`, and the run was absent from `state.json`/`runs.json` when looked at. Root cause UNKNOWN. Neighbouring
evidence: journal 16:50:29Z "unit inactive, scope inactive, its process check UNMEASURED; kept as running" (another
run, same tick window). Since 5d1e71e53d, seat_dirt.tidy lands such a concept folder 30 min after it settles with no
run open, so a lost done no longer strands files; but a lost done still skips the harvest's alarms, chain_next and
the turn escalation.

Owed: find the path in role_launch/dispatcher where a run record leaves tracking without role_done (read the
Dispatcher journal and runs.json history around 2026-11-16T16:35-16:58Z), then fix it.

## verify
Acceptance test: none yet, root cause unknown. The fixer reproduces first and writes a selftest in which a run record
leaves tracking by the found path, asserting a role_done (or an alarm naming the lost run) on the next tick; watched
failing on base before the fix.

## criteria
- The path that drops a run without role_done is named with evidence.
- A selftest fails on base and passes after.

## refs
file: src/RimMandrake/rimflow/role_launch.py
file: src/RimMandrake/rimflow/dispatcher.py
