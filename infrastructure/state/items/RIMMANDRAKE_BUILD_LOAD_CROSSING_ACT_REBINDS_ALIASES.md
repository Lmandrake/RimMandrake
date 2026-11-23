# RIMMANDRAKE_BUILD_LOAD_CROSSING_ACT_REBINDS_ALIASES

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

the act op "save and load in the middle": settle after the load, bind each alias by its saved id with a link record, arm the record and the probes again, continue the timeline.

Built when its need is measured ("Later tickets, each when its need is measured" in the build order).
Needs: the run-plan and calm tickets.

Depends on: `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`, `RIMMANDRAKE_BUILD_CALM_PROFILE_BREACH_LOG_AND_LEASE`.

## verify

Acceptance test (offline), 6 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_scene_load_crossing.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

Offline: `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_scene_load_crossing.py`, 6 checks

Live test: none drafted in the build order for this ticket.

## criteria

- The acceptance test prints 6 checks passed and exits 0.
- At least one planted fault per promise was seen red before the ticket closes (the build order names no plant here).
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
