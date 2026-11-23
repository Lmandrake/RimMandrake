# RIMMANDRAKE_BUILD_KEEPER_SAVE_RAND_STATE_DIVERGENCE_FINDER

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

for scenes in a hunt: a save and the random state at arm, the replay procedure, the trajectory fingerprint, "diverged at tick T". It measures the replay rate.

Built when its need is measured ("Later tickets, each when its need is measured" in the build order).
Needs: the measurement ticket; built when the first hunt needs it.

Depends on: `RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED`.

## verify

Acceptance test (offline), 7 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_scene_replay.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

Offline: `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_scene_replay.py`, 7 checks

Live test: none drafted in the build order for this ticket.

## criteria

- The acceptance test prints 7 checks passed and exits 0.
- At least one planted fault per promise was seen red before the ticket closes (the build order names no plant here).
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
