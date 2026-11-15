# RIMMANDRAKE_FIX_PYRELANDS_ROUND_SIX_SEVENTEEN_GAPS

## spec

His card, Sun 2026-11-15 12:22 PM PST (OWNER:1794774724955142310, on `BAROQUE_SCRIPT_MEASURE_PREP_AND_CONTROLS`):
"Fix the 17 gaps, one final look". Builders fix the 17 PROBLEM and CORRECTION gaps of round 6. The 1 POLISH gap (g3)
stays in `design/concepts/Pyrelands/version/polish.md` and is not part of passing. The exam is retaken, then the coverage
judge looks ONE more time. This supersedes his 2026-11-14 limit (OWNER:1794721773574845016) for exactly that one look;
it is not a rework loop.

Inputs (all tracked):
- `design/concepts/Pyrelands/coverage_verdict.json`, judge `rm-coverage-judge-1794750987`, 18 gaps, all `return_to` 3.
  Each gap's `what`, `where`, `evidence` and `smallest_fix` are the work.
- `design/concepts/Pyrelands/version/gaps_sorted.md` "Round 6" (the sort: 14 PROBLEM, 3 CORRECTION, 1 POLISH).
- `design/concepts/Pyrelands/record.json` decision `d_fix_seventeen_round_six_gaps` (his card, recorded).
- Precedent: `RIMMANDRAKE_APPLY_PYRELANDS_JUDGE_EDITS_ALL_TWENTY_ATTAINABLE` (the "Fix all 12" card, same route).

Do, in this order, as ONE item (one re-pin; a second re-pin would owe a second look):
1. Apply the `smallest_fix` of g1, g2 and g4-g18 to the tree, sheet, scene text, record or code they name. Read each
   gap's `where` and `evidence` first; do not guess a defName or a scene id. Code changes go through the normal gates
   (`code_review_status.py check`, the tests for what changed).
2. Commit; every commit message carries `OWNER:1794774724955142310` (designer_stage.py `change_tied` ties a commit to the
   card by that string).
3. Write `design/concepts/Pyrelands/coverage_fixes.json`:
   `{"against": "rm-coverage-judge-1794750987", "claims": [{"gap": "g1", "evidence": "<file and place>"}, ...]}` with one
   claim per fixed gap, plus g3 with evidence `record.json d_fix_seventeen_round_six_gaps: g3 is POLISH, out of passing in
   his words (OWNER:1794774724955142310); kept in version/polish.md`.
4. Re-pin ONCE: `python3 src/RimMandrake/rimflow/designer_stage.py repin design/concepts/Pyrelands --source
   OWNER:1794774724955142310@<sha>` for every commit that moved a stale input (including the commit that recorded the
   card in `record.json`), with a why that says: "his card 2026-11-15: fix the 17 round-6 gaps, ONE final look; release
   once; a not_covered pauses Pyrelands for him again".
5. Do NOT run `coverage_judge.py release` or `run`, and do not hand-launch any stage. The re-pin is a `locked_change`;
   the maturation tick then owes the chain steward (`maturation_autonomy.py` chain_owed), which retakes the Cold Reader
   exam, releases once and runs the ONE look.

## verify
- `coverage_fixes.json` against `rm-coverage-judge-1794750987` with 18 claims (17 fixes + g3 out in his words).
- `design/concepts/Pyrelands/stage.json` history ends with one new `locked_change` newer than the 14:05:35Z coverage_stop.
- A dry maturation tick (`maturation_dispatch.py tick --no-page` in a fresh clone) shows the Pyrelands row owing the
  chain steward, not paused.

## Watch out
- The exam on file (`exam.json`, taken at `292b94bca8`, 05:37 PST) fails the exam gate tightened at `677d7dfdb4`
  (07:53 PST): no scenario marked `"by": "challenger"`, control `missed_ids` unset, no `exam_control/copy.json`
  (`designer_stage.py` exam_errors, lines ~1063 and ~1185). `coverage_judge.py` status/run skips on a failing exam
  (coverage_judge.py:753-755) before it would judge. So the chain's retake must meet `roles/designer_exam.md` in full
  (`designer_stage.py exam-control <dir> --leaf <id>`, the control Reader, Challenger-marked scenarios), or the one
  look never runs. This item does not take the exam; it only must not leave it worse.

## limits
- The one-look limit is enforced by `coverage_judge.py` stop_reason (only rounds after the last release count): after the
  chain's single release, a not_covered stops judging and maturation pauses on the coverage stop. No second release
  without his word.
