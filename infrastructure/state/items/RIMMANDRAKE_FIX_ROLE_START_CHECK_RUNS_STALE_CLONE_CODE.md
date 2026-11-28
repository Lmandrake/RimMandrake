## spec
From 1:32 AM to 2:30 AM PST 2026-11-28 the Dispatcher tried 22 times to start the Designer on DirectSun. Each start
ended `held at launch: REFUSED by control: refused at start: OFF (mod:DirectSun, act ct_000303 ...)`. Act ct_000303 is
`./pipe off DirectSun --design-ok`: the switch that keeps builds off and admits the mod's Designer (built at f7ed85ef64).

Cause, as far as the Conductor read it: a role unit's start check is `ExecCondition=control.py condition <run>`, and
`control.launch_unit` builds that command with `hook_cmd("condition", rid, p, clone)`, so the check runs the copy of
`control.py` in the role's own clone. systemd runs ExecCondition before ExecStart, and the role clone's `./sync` is the
first step of ExecStart (`role_launch.py`, "role-sync"). The Designer clone `/home/mandrake/rm/roles/Designer` stood at
67149ed174, 153 commits behind origin, so its `control.py` did not know `--design-ok` and refused the admitted run.
After the Conductor synced that clone by hand at 2:35 AM PST (to ed1fb6760e), the next Designer start passed
(`rm-role-designer-1795862365`, then the chained `rm-role-designer-1795862643`).

Second fault: each refused start wrote an open entry and an abort entry into `design/concepts/DirectSun/stage.json` in
the Designer clone (about 265 uncommitted lines at 2:35 AM PST).

Owed outcome:
- the start check of a run never decides on code that is older than the code that admitted the run;
- a start that the control store refuses leaves no open or abort entry in the concept's stage record.

## verify
A selftest, red on the base: a role clone whose `control.py` is older than the switch grammar of the store (a
`design_ok` switch on the mod) still starts that mod's admitted Designer run; a start that the store refuses adds no
entry to the concept's `stage.json`.

## criteria
- case 1 (stale role clone, design-ok switch, Designer run starts) red on the base, green after;
- case 2 (a refused start writes no stage entry) red on the base, green after;
- case 3 (a mod that is plain `pipe off`, no design-ok, still refuses its Designer at start) green before and after;
- a planted fault ("the start check always passes") turns case 3 red.

## refs
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/role_launch.py
file: src/RimMandrake/rimflow/role_clones.py
file: src/RimMandrake/rimflow/designer_stage.py
