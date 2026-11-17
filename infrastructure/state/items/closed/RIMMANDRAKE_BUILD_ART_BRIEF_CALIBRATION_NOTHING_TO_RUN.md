# RIMMANDRAKE_BUILD_ART_BRIEF_CALIBRATION_NOTHING_TO_RUN

## spec

The `art_judge_brief` row of `infrastructure/state/judge_calibration.json` has no `model_check` and no `free_check`, so
`python3 src/RimMandrake/rimflow/refusal_contract.py calibrate` can never move it off UNTESTED (it reads UNTESTED since
2026-11-13; measured 2026-11-17 by `calibrate --no-run`). Under UNTESTED its refusals are advisory, so the art judge
(`.claude/agents/rm-judge.md`, brief `design/RimMandrake/art_judge_brief.md`) sends nothing back.

Found by RIMMANDRAKE_LAND_JUDGE_PROMPT_CALLS_FOUR_ANSWERED_BY_CARD, whose J5 asked for "one calibration batch on the exact
final coverage brief (and the art brief)": the coverage brief was calibrated (8 of 8 planted cases, hash 5f9fdb20);
the art brief could not be, because there is nothing to run. Not fixed in that run: the fix is a new judge harness
(which images, canon references and sibling sheets the rm-judge brief is shown per subject, and how its KEEP / REDO /
UNSURE maps to the registry's pass / refuse), which is design work, not a known one-line fix.

Build a model check for the art judge brief, on the pattern of `src/RimMandrake/rimflow/coverage_calibration.py`: stage
each planted subject, put it to a fresh Opus judge with the brief's real text, write one `{id, expect, got}` row per
case to `$RM_CALIBRATION_RESULTS`, and name it in the row's `model_check`. Cases both ways: the registry row already
names them (`infrastructure/state/art_eval/regression.jsonl`, 5 expect ACCEPT, 6 expect NOT_ACCEPT); add one planted
owner-kept subject (checklist step 2, E3: no REDO of kept art by a delegated call) and one north facing whose fix must be
a rear-view redraw (the point-27 example).

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --model art_judge_brief` writes a
`last_run` for `art_judge_brief` whose `cases` line is "N planted case(s) ran and came out as planted" with N >= 11, and
`calibrate --no-run` then reads `art_judge_brief  CALIBRATED`. On the base (2026-11-17) it cannot run: the row has no
`model_check`, so the command leaves it UNTESTED (watched: `calibrate --no-run` reads UNTESTED).

## criteria

- The art judge brief has a runnable calibration check named in its registry row.
- Its cases go both ways and include an owner-kept subject and a north-facing repair.
- The brief reads CALIBRATED at its current text.

## refs

file: design/RimMandrake/art_judge_brief.md
file: .claude/agents/rm-judge.md
file: src/RimMandrake/rimflow/coverage_calibration.py
file: infrastructure/state/judge_calibration.json
file: infrastructure/state/art_eval/regression.jsonl
