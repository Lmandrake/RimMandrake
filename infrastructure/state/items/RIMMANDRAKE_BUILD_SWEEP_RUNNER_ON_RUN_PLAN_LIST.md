# RIMMANDRAKE_BUILD_SWEEP_RUNNER_ON_RUN_PLAN_LIST

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

steps 3 and 4 of `04_live_tuning.md`: `scene.py sweep` (plans that differ in their overlay, the repeated baseline, the shuffled order, the "cannot rank" answer), export, the absorbed check.

Built when its need is measured ("Later tickets, each when its need is measured" in the build order).
Needs: the repeats and def-field tickets.

Depends on: `RIMMANDRAKE_BUILD_STAMP_AGAIN_REPEATS_WITH_RESET_DIGEST`, `RIMMANDRAKE_BUILD_DEF_FIELD_OVERLAY_WITH_WRITE_RECIPES`.

## verify

Acceptance test (offline), 9 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_scene_sweep.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

Offline: `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_scene_sweep.py`, 9 checks

Live test: none drafted in the build order for this ticket.

## criteria

- The acceptance test prints 9 checks passed and exits 0.
- At least one planted fault per promise was seen red before the ticket closes (the build order names no plant here).
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
