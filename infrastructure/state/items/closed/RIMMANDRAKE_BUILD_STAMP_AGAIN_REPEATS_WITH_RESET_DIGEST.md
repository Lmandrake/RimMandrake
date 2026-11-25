# RIMMANDRAKE_BUILD_STAMP_AGAIN_REPEATS_WITH_RESET_DIGEST

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** repeats of one plan on fresh stamps; N copies side by side as one cluster; the reset digest of the
  station and of each mod's digest hook, compared with the first stamp; the periodic comparison with a fresh process;
  launches, valid opportunities and exposures counted apart.
- **Needs:** the stage map, the verdict ledger and the mod hooks tickets.

Depends on: `RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS`, `RIMMANDRAKE_BUILD_SCENE_VERDICT_LEDGER_RECEIPT_IS_NOT_VERDICT`, `RIMMANDRAKE_BUILD_MOD_TRACE_AND_RESET_HOOKS_BY_REFLECTION`.

## verify

Acceptance test (offline), 8 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_scene_repeats.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_scene_repeats.py`, 8 checks.

- **Live test (UNRUN):** 20 stamped copies of the chosen-rescue scene finish in less wall time than 3 single runs
  take today; a planted cross-talk between two copies is a breach; **a mod state left dirty on purpose changes the
  reset digest and stops the repeat**.

Live state at filing: UNRUN.

## criteria

- The acceptance test prints 8 checks passed and exits 0.
- At least one planted fault per promise was seen red before the ticket closes (the build order names no plant here).
- The live test was run and its result is on the ticket, or it is recorded UNRUN with its command.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
