# RIMMANDRAKE_HOLD_UNREADABLE_STORE_TICK_CRASH_BACK_SLICE_TWO

## spec
The dispatch tick crashes again on an unreadable control store. The 2026-11-18 fix
(RIMMANDRAKE_HOLD_ALL_ON_UNREADABLE_STORE_TICK_CRASHED_INSTEAD, 1b0012a11b) made it hold every mod and say why.
Slice 2 (c180799371) then moved the counts into the store, so `pipeline_control.used` raises Unreadable.
`maturation_dispatch.gather` calls `maturation.build_facts`, which calls `used`, before the tick reads the hold.
So the tick dies with a traceback before it can hold anything. Nothing launches, but nothing says why either.
Found by RIMMANDRAKE_PROVE_PIPELINE_CONTROL_ASKS_MET_HE_ASKED_BEFORE, running the closed ticket's acceptance test.
Fix: `gather` takes an Unreadable store as a fact of the mod; the hold read then holds every mod as UNREADABLE.
Not touched: pipeline_control.py (sibling runs edit it).

## verify
D=$(mktemp -d); mkdir $D/md; RM_MATURATION_DISPATCH_DIR=$D/md RM_CONTROL_DB=$D/missing-control.db python3 src/RimMandrake/rimflow/maturation_dispatch.py tick --no-page
Passes: exit 0, every mod reads `CONTROL UNREADABLE`, and `launched 0`.
Watched failing on 957ec0da0c: exit 1, traceback `pipeline_control.Unreadable: the control store: not initialised`.

## criteria
- The tick on a missing store exits 0, holds every advancing mod as CONTROL UNREADABLE, and launches 0.
- selftest_maturation_dispatch stays green.

## refs
file: src/RimMandrake/rimflow/maturation_dispatch.py
