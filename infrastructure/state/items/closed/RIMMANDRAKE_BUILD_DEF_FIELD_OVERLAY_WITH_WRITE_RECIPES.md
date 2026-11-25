# RIMMANDRAKE_BUILD_DEF_FIELD_OVERLAY_WITH_WRITE_RECIPES

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

step 2 of `04_live_tuning.md`: def-field writes through the record, the first recipes, the UNVERIFIED state, the fingerprint before and after.

Built when its need is measured ("Later tickets, each when its need is measured" in the build order).
Needs: the deviation record.

Depends on: `RIMMANDRAKE_BUILD_DEVIATION_RECORD_SETTINGS_FIELD_JOINS_FIRST`.

## verify

Acceptance test (offline), 10 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_overlay_recipes.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

Offline: `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_overlay_recipes.py`, 10 checks.

experiments E3, E4, E5, E7 of that file

Live state at filing: UNRUN.

## criteria

- The acceptance test prints 10 checks passed and exits 0.
- At least one planted fault per promise was seen red before the ticket closes (the build order names no plant here).
- The live test was run and its result is on the ticket, or it is recorded UNRUN with its command.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
