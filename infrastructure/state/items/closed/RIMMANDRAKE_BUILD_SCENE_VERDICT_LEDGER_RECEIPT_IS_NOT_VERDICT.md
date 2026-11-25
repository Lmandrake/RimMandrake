# RIMMANDRAKE_BUILD_SCENE_VERDICT_LEDGER_RECEIPT_IS_NOT_VERDICT

One ticket of the Bridge v2.0 build order. Read `design/specs/2026-11-23-bridge-v2/06_build_order.md` §How to read a ticket, then
`design/specs/2026-11-23-bridge-v2/05_build_design.md`. Filed by `RIMMANDRAKE_FILE_BRIDGE_TWO_BUILD_ORDER_THEN_WIRE_FIRST_SLICE`.

## spec

- **Builds:** `src/RimMandrake/rimflow/scene_verdicts.py` and `scene_runs.jsonl` in a mod's version folder: the
  rules of kinds A, B and C over the runs of one claim on one build; a pass held by an UNRESOLVED run; a kind B budget
  and INCONCLUSIVE; a reclassification added, never overwritten; the hunt notice. A run counts for no bar when its
  receipt has an overlay stamp, the taint mark, an arm that was not compared with the reference, a PROOF build, or a
  map kind that the bar does not accept. The Stage 6 exit reads it.
- **Needs:** the judge ticket. No game.

Depends on: `RIMMANDRAKE_BUILD_SCENE_JUDGE_OUTSIDE_GAME_FROM_KEPT_TRACE`.

## verify

Acceptance test (offline), 17 checks printed as passed, exit 0:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_scene_verdicts.py
```

Seen red on base `adfddcb1f8` on 2026-11-23: exit 1 ("--only names no such file"): the selftest file does not exist yet. Expected after the build: exit 0.

- **Offline test:** `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_scene_verdicts.py`, 17 checks: kind A decides on one
  valid run (2); kind B passes on one SUCCESS only with no MOD FAILURE and no UNRESOLVED (3); a spent budget gives
  INCONCLUSIVE (1); X of Y for a result random by design (1); one UNRESOLVED holds the pass until classed (1); a
  reclassification keeps the history (1); a replay is not a sample (1); a cluster counts as one cluster (1); a stamped
  run reads TUNED and counts for nothing (1); a run with the taint mark and `overlay: none` counts for nothing (1); an
  uncompared arm counts for nothing (1); a change that does not touch what the scene reads keeps the verdict (1); a
  serious single UNRESOLVED opens a hunt notice with the four parts that the policy names (1); zero, none, could not
  look and failed are four answers in the summary (1); a re-judged run shows both outcomes (1).

Live test: none drafted in the build order for this ticket.

## criteria

- The acceptance test prints 17 checks passed and exits 0.
- Each plant below was seen red before the ticket closes.
- **Wrong code that must go red:** a ledger that checks the overlay stamp and not the taint mark; a kind B pass with
  an UNRESOLVED run standing.
- Each new Harmony patch site is in `src/RimMandrake/bridgetools/HOOKS.md`; each new pipeline file has its promises on
  `design/specs/2026-11-23-bridge-v2/boundary.md` first.
