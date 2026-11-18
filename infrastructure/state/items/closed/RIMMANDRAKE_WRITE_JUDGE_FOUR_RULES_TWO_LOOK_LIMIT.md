# RIMMANDRAKE_WRITE_JUDGE_FOUR_RULES_TWO_LOOK_LIMIT

## spec

FIX (owner by card 2026-11-17 "Judge ruling -> Adopt the four rules (Recommended)"; spec design/specs/2026-11-17-judge-flaws-not-polish/6_proposed_ruling_plain.md, the four rules and "How it is built" steps 1 and 3; the owner: "We need judges that turn away incomplete work, but not work that isn't tuned just-so or, worse, forever needing more tuning").

FINDING: the coverage judge's prompts carry none of the four rules, and the look limit is three refusals (coverage_judge.py line 89 NOT_COVERED_LIMIT = 3), so a mod can be judged in three or more looks, each free to raise new demands.

CONTRACT (prompt text and one number; the exact sentences are in the case file, constants R1A R1B R2_FIRST R2_LATER R3 R4 R4_DESIGNER, and must appear verbatim, whitespace-flattened):
- Rule 1 (R1A, R1B), rule 3 (R3) and rule 4 (R4) in all three prompts: the full look (prompt(), round 1), the full re-judge (prompt(), prior True) and delta_prompt().
- Rule 2: R2_FIRST in the round-1 full look only; R2_LATER in the full re-judge and the delta prompt.
- R3 also in RECORD_TEXT (line 125). R4_DESIGNER in roles/designer_write.md ("The tree" section).
- NOT_COVERED_LIMIT = 2: one refusal does not stop, the second stops, a malformed round is not a look, a release grants one look and its refusal stops again. JUDGE_RUNS_MAX stays 4 (the error guard).
- Remove the old limit text: "third not_covered" from all prompts (lines 371, 981) and "The third not_covered" from the module docstring (line 42; line 19's "One pass lists every gap" now holds for the first look only) and the comment at line 87; "This one pass must list EVERY gap" (line 1007) from the re-judge and delta prompts (keep a list-every-gap line only in R2_FIRST); "stops at its third refusal" in roles/designer.md (line 82); "third `not_covered`" in roles/designer_lock.md (line 21); "judge stops at its third not_covered" in design/RimMandrake/standing_rulings.md (line 597) -> say the second.
- KEEP the earlier card's J2 lines in both full prompts ("Judge the situations exercised and alternatives ruled out, ..." and "Hunt parameter regimes and regions, not examples."); selftest_judge_card_answers guards them.

FILES: src/RimMandrake/rimflow/coverage_judge.py; src/RimMandrake/rimflow/roles/designer_write.md, designer.md, designer_lock.md; design/RimMandrake/standing_rulings.md (that line); src/RimMandrake/rimflow/selftest_coverage_judge_loop.py and selftest_designer_park.py (below). No other file, no refactor. Not in this ticket: routing the leftovers "to the owner as a short list" (file 6 step 3 tail) - name it in your commit message as not done.

ACCEPTANCE TEST (watched failing on base bbfc765143): python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_four_rules_two_looks.py
Base read: "cases read 35; wrong 27 (worst); limit 0", exit 1, e.g. "WRONG NOT_COVERED_LIMIT is 2: got 3". Input kinds: the limit over 1 and 2 refusals, a malformed round, a release and its look; every prompt kind; RECORD_TEXT; the docstring; the three role files and the standing ruling; the J2 guard. Done = "wrong 0".

CONFLICTING TESTS (measured by prototype with the limit at 2): selftest_coverage_judge_loop.py 16 fails (its scaffolding assumes three rounds) and selftest_designer_park.py 3 fails ("lift: the next look is judged", "fixable: the Designer's rework run opens", "healthy attended walk: two refusals then covered"). Re-express them in terms of CJ.NOT_COVERED_LIMIT, never a literal, keeping their bars: judging stops at the limit, one alarm, no judge runs after the stop, a release grants one look. Under rule 2 a park lifted at the look limit leads to the stopped hold, not another look; the healthy walk becomes one refusal then covered. Do not weaken any other case.

VERIFY: python3 src/RimMandrake/Utils/run_selftests.py --only selftest_coverage_judge_loop,selftest_designer_park,selftest_judge_card_answers,selftest_coverage_judge,selftest_coverage_delta,selftest_judge_calibration   (and the case file reads wrong 0).

CALIBRATION (the card: "unproven until recalibrated"): changing these prompts changes the brief's calibration identity (refusal_contract.brief_hash over coverage_judge.py, roles/designer_scene_contract.md, roles/designer_lock.md, bar_rule.py), so the judge's refusals do NOT bind (advisory, covered unsigned) until it is recalibrated. Recalibration is a separate owed step, RIMMANDRAKE_RECALIBRATE_JUDGE_THEN_RESTAMP_PYRELANDS_ONCE, with three cases: Pyrelands look 8 must close; the fire-immunity test where the beast never touches fire must be refused; "test the giant against every roster kind" must not block. Do not recalibrate in this ticket.

## verify

    python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_four_rules_two_looks.py     # must read: wrong 0
    python3 src/RimMandrake/Utils/run_selftests.py --only selftest_coverage_judge_loop,selftest_designer_park,selftest_judge_card_answers,selftest_coverage_judge,selftest_coverage_delta,selftest_judge_calibration

## criteria

- `python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_four_rules_two_looks.py` prints `wrong 0` (it read wrong > 0 on base bbfc765143).
- `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_coverage_judge_loop,selftest_designer_park,selftest_judge_card_answers,selftest_coverage_judge,selftest_coverage_delta,selftest_judge_calibration` all green.
- The diff touches only the files under ## refs.

## refs

file: src/RimMandrake/rimflow/coverage_judge.py
file: src/RimMandrake/rimflow/roles/designer_write.md
file: src/RimMandrake/rimflow/roles/designer.md
file: src/RimMandrake/rimflow/roles/designer_lock.md
file: design/RimMandrake/standing_rulings.md
file: src/RimMandrake/rimflow/selftest_coverage_judge_loop.py
file: src/RimMandrake/rimflow/selftest_designer_park.py
file: design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_four_rules_two_looks.py

## What the card said

<!-- answered 2026-11-18T01:17:04Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** Tue Nov 17, 5:12 PM PST. The proposed ruling is written in the plain wording we just settled and is open in Typora (D:\Luke\dev\RimMandrake\design\specs\2026-11-17-judge-flaws-not-polish\6_proposed_ruling_plain.md). It holds the four rules: (1) the judge may refuse only when a promise is not kept, when nobody would notice a broken promise, or when a test or file is itself wrong; (2) one full inspection, then one check of the repairs; (3) a refusal may not create new requirements; (4) only your promises must be proven, the Designer's extra warnings are tips. It also fixes two bugs (a finding rated polish can block; a repaired problem stays refused when a form is missing). 'Recalibrated' means the changed judge is run against known cases before its refusals count. Nothing has been run against a judge yet. Which way do you rule?
**Picked:** Adopt the four rules (Recommended)
**Its description:** Why: few rules you can read and tune, each with one dial. Buys: prompt text plus two small fixes, undone by reverting one commit. Costs: with one full inspection, what the first look misses reaches play; unproven until recalibrated and one mod runs. Recommended: it is the smallest change that stops the repeat looks.
**Other options:** Only the two bug fixes now · Adopt GPT's nine rulings · Four rules, second reader always
