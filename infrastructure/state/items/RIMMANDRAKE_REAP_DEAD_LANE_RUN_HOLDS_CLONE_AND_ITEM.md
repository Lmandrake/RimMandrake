## spec
The ticket lane (`list_dispatch.py`, the Workshop Pipeline) launched the run
`rm-detached-bench-rimmandrake-read-fix-8f9257b859-with-fre-1795860231` at 2:05 AM PST 2026-11-28. Its record stayed
`status: launching`. Its unit never existed (`systemctl --user status`: could not be found), it wrote no transcript and
it has no `.err` file. The record kept the pool clone
`/home/mandrake/rm/runs/clones/RIMMANDRAKE_READ_FIX_8F9257B859_WITH_FRESH_EYES.det`.

From then on each lane tick read the item `RIMMANDRAKE_READ_FIX_8F9257B859_WITH_FRESH_EYES` as
`codex_lander_failed refused: clone ... is held: run ... is launching in it`. `detached_helper.py status` read the run as
`DEAD (unit inactive, finish never ran)`, and the liveness beat (`run_alive.py`) wrote `act: lapse, gone: its unit is
not running`. No program ended the record. The Conductor ran `detached_helper.py finish --unit` and `return --unit` by
hand at 2:57 AM PST, 52 minutes after the launch.

The Maturation Pipeline tick has this chore for a run on an advancing mod (`slow_chores` and `reap_run` in
`maturation_dispatch.py`). The ticket lane has no such chore.

Owed outcome: a detached run of the ticket lane whose unit is dead and whose finish never ran is finished and its clone
returned by a program, and the lane then offers its item again. A run that was killed on purpose keeps its own path.
Also find why this launch left no unit, and write the cause on the item.

## verify
A selftest, red on the base: a lane run's record reads `launching` (older than the launch grace) or `running`, its unit
is dead, and the lane's tick finishes it and returns its clone; a record younger than the grace is left alone; a unit
whose state cannot be read is left alone (could not look).

## criteria
- case 1 (dead lane run is finished and its clone returned by the tick) red on the base, green after;
- case 2 (a young `launching` record is not touched) green;
- case 3 (unit state unreadable: nothing is finished, the tick says could not look) green;
- a planted fault ("finish every launching record") turns case 2 red.

## refs
file: src/RimMandrake/rimflow/list_dispatch.py
file: src/RimMandrake/rimflow/detached_helper.py
file: src/RimMandrake/rimflow/run_alive.py
file: src/RimMandrake/rimflow/maturation_dispatch.py
