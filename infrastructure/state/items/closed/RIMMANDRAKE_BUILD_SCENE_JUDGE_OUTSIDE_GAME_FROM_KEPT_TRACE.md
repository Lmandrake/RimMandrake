# RIMMANDRAKE_BUILD_SCENE_JUDGE_OUTSIDE_GAME_FROM_KEPT_TRACE

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** `src/RimMandrake/rimflow/scene_judge.py`: plan + trace + receipt facts -> one of the seven outcomes,
  the classifier row, the first failed condition with its observed values. It checks the evidence contract first and
  answers COULD NOT LOOK when a point fails. `--rejudge <run folder>` adds a line to the run's history and refuses, by
  naming the missing track or tap, a question that the trace cannot answer. The Python condition evaluator gains
  `count`, `seq`, `before`, `after` over tap records. One exit code per outcome.
- **Needs:** the trace schema of the ticket above. No game. Its fixtures are the slice's recorded traces and hand-made
  ones.

Depends on: `RIMMANDRAKE_WIRE_COND_RUN_INTO_TICK_BUILT_NEVER_JOINED`.

## verify

Acceptance test (offline), 31 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_scene_judge.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_scene_judge.py`, 31 checks: one trace for each of the
  nine classifier rows of `02_needs_design.md` §7 (9); the evidence contract: no closing record, a dropped row in the
  needed span, a missing first sample, a missing last sample, a tap that a condition needs and the plan did not arm
  (5); a success already true at the first sample is refused at run time (1); a success with no exposure is refused
  (1); a "mod says" record alone decides nothing (1); a mod bug that walks its own actor into a hazard is UNRESOLVED,
  not ENVIRONMENT FAULT (1); a giver's refusal is MOD FAILURE, not APPARATUS FAULT (1); `--rejudge` with an unchanged
  checker gives the same outcome and adds one history line (1); `--rejudge` with a condition on an unrecorded value is
  refused by name (1); the first outcome is never overwritten (1); an alias whose object was replaced with no link
  record is COULD NOT LOOK (1); each exit code (7); an unknown key in a plan is refused by name (1).

Live test: none drafted in the build order for this ticket.

## criteria

- The acceptance test prints 31 checks passed and exits 0.
- Each plant below was seen red before the ticket closes.
- **Wrong code that must go red:** classifier rows 4 and 5 swapped; a dropped span read as an empty span; an empty
  trace read as "no forbidden effect"; a re-judgement that overwrites the first outcome.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
