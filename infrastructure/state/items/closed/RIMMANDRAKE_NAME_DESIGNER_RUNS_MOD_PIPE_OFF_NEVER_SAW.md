## spec
Found 2026-11-19 by RIMMANDRAKE_PIN_MOD_MODEL_FABLE_EVERY_STAGE_ROLES_OPUS. A Designer run reached the control store's
admission (`control.launch_unit`) with no mod: `role_launch.launch` reads `role["mod"]` or `role["concept"]`, but
`launch_role` put the concept in `designer_dir` only. So the run was admitted under no mod, and a `pipe off <Mod>` typed
after the run-now was asked did not refuse it at admission or at its start check (ExecCondition). The request-time
check (`owner_held`, role_launch.py) still refused new asks, so only a request already queued when the switch went off
slipped through.

## fix (landed with the parent item, same sha)
`launch_role` sets `out["mod"]` to the concept folder's name for every stage-machine run.

## criteria
Every Designer launch is admitted by control under its concept's mod; a `pipe off <Mod>` refuses one asked before the switch.

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_mod_model_pin.py`, test `t_designer_launch_names_its_mod`
(a Designer launch on WreckedMachines after `pipe off WreckedMachines` is refused by control and systemd-run is never
called). Watched failing on base b2bdcaafc8 ("ok True, unit ... started"), passing after.
