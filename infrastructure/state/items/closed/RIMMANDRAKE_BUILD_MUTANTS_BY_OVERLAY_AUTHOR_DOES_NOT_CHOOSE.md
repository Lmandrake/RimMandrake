# RIMMANDRAKE_BUILD_MUTANTS_BY_OVERLAY_AUTHOR_DOES_NOT_CHOOSE

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** `mutants.json` per mod with its lint and the two kinds (live, compiled); the seeded draw;
  `scene.py both-ways <scene>`: the green run and the red run each from the fixture save loaded fresh, with the random
  state written back; each mutant's witness (a recorded fact that differs because of the mutant); a list of at least
  two mutants per bar, reviewed by an agent that did not write the scene; both receipts in the scene's history; the live switch of one of our Harmony patches (off and
  on, with a call counter that proves it).
- **Needs:** the verdict ledger, the compiler and the deviation record tickets.

Depends on: `RIMMANDRAKE_BUILD_SCENE_VERDICT_LEDGER_RECEIPT_IS_NOT_VERDICT`, `RIMMANDRAKE_BUILD_SCENE_FILE_COMPILER_AND_LINT_NO_GAME`, `RIMMANDRAKE_BUILD_DEVIATION_RECORD_SETTINGS_FIELD_JOINS_FIRST`.

## verify

Acceptance test (offline), 13 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_scene_mutants.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_scene_mutants.py`, 13 checks: a mutant that only switches
  the feature off is refused (1); a mutant must name a bar (1); the draw is the same for one scene and build, and the
  scene file cannot set it (2); the red run's receipt can never count as a pass (1); a red run that ends SUCCESS reads
  "mutant not killed" (1); a red run with no exposure proves nothing and says so (1); a red run whose witness did not change reads "mutant not
  used" (1); a bar with one mutant is refused (1); a red run that fails on another
  condition than the mutant names is reported as such (1); both runs start from the same fixture hash (1); a compiled
  mutant is listed "needs build" and is not run live (1); a bar whose killed mutants are all value changes says so (1).

Live test: none drafted in the build order for this ticket.

## criteria

- The acceptance test prints 13 checks passed and exits 0.
- At least one planted fault per promise was seen red before the ticket closes (the build order names no plant here).
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
