# RIMMANDRAKE_BUILD_WORLD_EVENT_TAPS_SECOND_FAMILY

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** the taps for a mental state attempt (started or not), a quest registered, a letter, a message, a fire
  started and an explosion (each with its instigator); the tracks for weather, game condition, temperature, hour, the
  camera and the window stack.
- **Needs:** the cast tracks ticket.

Depends on: `RIMMANDRAKE_BUILD_CAST_TRACKS_AND_JOB_TAPS_FIRST_FAMILY`.

## verify

Acceptance test (offline), 9 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_world_taps.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_world_taps.py`, 9 checks: the hook rules for each of
  the six taps (6); an attempt and a start are two records (1); a message is recorded before the rule that hides
  repeats (1); the hook table check passes (1).

Live test: none drafted in the build order for this ticket.

## criteria

- The acceptance test prints 9 checks passed and exits 0.
- At least one planted fault per promise was seen red before the ticket closes (the build order names no plant here).
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
