# RIMMANDRAKE_BUILD_SCENE_FILE_COMPILER_AND_LINT_NO_GAME

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** `src/RimMandrake/Utils/scene_compile.py`: the scene file of `02_needs_design.md` §11 -> a run plan;
  defaults expanded and printed; the hash of the expanded contract; lint against the frozen def dump
  (`observed/inventory/DefDump_OFFICIAL/`); `needs.map`; fixtures by name. The three worked examples as real files.
- **Needs:** the run-plan ticket's plan format.
- The lint cannot know whether a success is already true before the act; that is decided at run time by the judge on
  the first sample (the judge ticket's check). GPT named this hole in my first draft.

Depends on: `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`.

## verify

Acceptance test (offline), 13 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_scene_compile.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_scene_compile.py`, 13 checks: the three worked examples
  compile (3); a misspelt def is refused by name (1); a path whose first step is not an alias is refused (1); a
  success on "mod says" alone is refused (1); a kind B scene with no budget is refused (1); a kind A scene with an
  allowed miss is refused (1); a "throughout" condition that the success must break is refused (1); a condition on a
  tap that the plan does not arm is refused (1); a condition on the middle of a tick with no tap is refused (1); the
  expanded contract's hash changes when a default changes (1); one file compiles to the same bytes twice (1).

Live test: none drafted in the build order for this ticket.

## criteria

- The acceptance test prints 13 checks passed and exits 0.
- At least one planted fault per promise was seen red before the ticket closes (the build order names no plant here).
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
