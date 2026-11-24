# RIMMANDRAKE_BUILD_LOAD_CROSSING_ACT_REBINDS_ALIASES

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

**Split by pass three (2026-11-23, `design/specs/2026-11-23-bridge-v2/11_design.md`).** The Python part of this ticket
is no longer here: binding each alias again by its saved id is the verb `s.act.reload`
(`contracts/act.md`), built when a scene first needs a load in the middle. This ticket keeps the C# duty only.

- **Builds (C# only):** the **load barrier**: a load inside a session ends paused; the recorders, the taps and the
  session's epoch are armed again before any tick can run; the trace continues with a link record that holds the saved
  id of each bound thing.

Built when its need is measured ("Later tickets, each when its need is measured" in the build order).
Needs: the instruments ticket and the calm ticket.

Depends on: `RIMMANDRAKE_WIDEN_SLICE_INTO_RUN_UNTIL_AND_ACT_BATCH`, `RIMMANDRAKE_BUILD_CALM_PROFILE_BREACH_LOG_AND_LEASE`.

## verify

Acceptance test (offline), 4 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_scene_load_crossing.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test (pass three):** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_scene_load_crossing.py`, 4 checks on
  the C# core: after a load inside a session the game is paused and no tick has run (1); the recorders are armed before
  the first tick after the load (1); the trace has one link record with the saved id of each bound thing, and `n` has no
  gap (1); a load with no open session is not touched by the barrier (1).

Live test: none drafted in the build order for this ticket.

## criteria

- The acceptance test prints 4 checks passed and exits 0.
- At least one planted fault per promise was seen red before the ticket closes (the build order names no plant here).
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
