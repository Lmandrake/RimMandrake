# RIMMANDRAKE_HOLD_ALL_ON_UNREADABLE_STORE_TICK_CRASHED_INSTEAD

## spec
With the control store unreadable, `maturation_dispatch.py tick` raised `mod_owner_hold.Unreadable` from
`maturation_autonomy.widen` and `_tick` (a traceback every minute, no reading written) instead of holding every mod and
saying `CONTROL UNREADABLE: <cause>`. Nothing launched either way (launch_unit refuses on an unreadable store), but the
crash hid the cause. Found 2026-11-18 by a dry tick with `RM_CONTROL_DB` on a missing file.

## verify
`RM_CONTROL_DB=/tmp/missing-control.db python3 src/RimMandrake/rimflow/maturation_dispatch.py tick --no-page` exits 0,
every mod reads `held ... CONTROL UNREADABLE`, and `launched 0` (exit 1 with a traceback at 2a780e4846: watched).

## criteria
The verify command as written.

## refs
file: src/RimMandrake/rimflow/maturation_dispatch.py
file: src/RimMandrake/rimflow/maturation_autonomy.py
