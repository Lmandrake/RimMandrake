# RIMMANDRAKE_PRINT_JUDGE_COUNTS_WHEN_COVERAGE_CLOSES

## spec

FIX (owner by card 2026-11-17 "Judge ruling -> Adopt the four rules (Recommended)"; spec design/specs/2026-11-17-judge-flaws-not-polish/6_proposed_ruling_plain.md, "How it is built" step 5: four counts printed when a mod's coverage stage closes).

FINDING: nothing counts, when a mod's coverage closes, how many looks it took, how many refusals were overturned, how many demands were new on unchanged material, or how many refusals bind on a number or line the owner did not say; so no one can tell whether the four rules are working.

CONTRACT:
- coverage_judge.SCHEMA (line 139; gap items at line 152): every gap carries `promise` (string: the owner's promise it rests on, quoted) and `owner_said` (boolean: every number and line the refusal binds on is in the owner's words), both in `required`. Add one RECORD_TEXT sentence asking for both.
- record_round (line 933) adds three integers to each coverage_rounds row: `new_on_unchanged` = gaps in gaps+advisory_gaps tagged late, plus len(rec["dropped"]); `overturned` = gaps in gaps+advisory_gaps with late_confirmed False, or whose criterion_verdict is flawed/unattainable while their judge_criterion_verdict is neither; `not_owner_said` = blocking gaps (rec["gaps"]) with owner_said False.
- New close_counts(st, d=None) -> {"looks","refusals","overturned","new_on_unchanged","not_owner_said"}: looks = covered or not_covered rounds (malformed is not a look); refusals = not_covered rounds; the other three summed (a missing field counts 0).
- New close_line(counts) -> one line containing "looks N", "refusals N", "overturned N", "new demands on unchanged material N", "not in the owner's words N" and "owner overturns: not counted" (the owner's own overturns are outside the program's reach). run() (line 1093) appends it to its message when the verdict signs or judging stops.

FILES: src/RimMandrake/rimflow/coverage_judge.py only. No refactor.

OVERLAP TO NAME: `promise`/`owner_said` overlap GPT's proposed requirement_quote field, which file 6 says not to build now. These two are the least that makes count 4 computable. If the parent vetoes schema fields, drop them and print count 4 as "not computed" instead.

ACCEPTANCE TEST (watched failing on base bbfc765143): python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_stage_close_counts.py
Base read: "cases read 11; wrong 11 (worst); limit 0", exit 1, e.g. "WRONG close_counts exists: got missing". Input kinds: the schema; a round with each kind of gap (late, dropped, reader-overturned, late unconfirmed, a judge confession, owner_said true/false/missing); stages of a covered first look, refusal then covered, two refusals (stopped), a malformed round between. Done = "wrong 0".

CONFLICTING TESTS: any fixture gap that now lacks `promise`/`owner_said` may fail schema validation in selftest_coverage_judge or selftest_coverage_refusal_record; add the two fields to those fixtures, never drop them from `required`.

VERIFY: python3 src/RimMandrake/Utils/run_selftests.py --only selftest_coverage_judge,selftest_coverage_judge_loop,selftest_coverage_delta,selftest_coverage_refusal_record   (and the case file reads wrong 0).

CALIBRATION NOTE: coverage_judge.py is in refusal_contract.brief_hash; any edit makes the brief UNTESTED until recalibrated. Expected; owed separately (RIMMANDRAKE_RECALIBRATE_JUDGE_THEN_RESTAMP_PYRELANDS_ONCE).

## verify

    python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_stage_close_counts.py     # must read: wrong 0
    python3 src/RimMandrake/Utils/run_selftests.py --only selftest_coverage_judge,selftest_coverage_judge_loop,selftest_coverage_delta,selftest_coverage_refusal_record

## criteria

- `python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_stage_close_counts.py` prints `wrong 0` (it read wrong > 0 on base bbfc765143).
- `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_coverage_judge,selftest_coverage_judge_loop,selftest_coverage_delta,selftest_coverage_refusal_record` all green.
- The diff touches only the files under ## refs.

## refs

file: src/RimMandrake/rimflow/coverage_judge.py
file: design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_stage_close_counts.py

## What the card said

<!-- answered 2026-11-18T01:17:04Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** Tue Nov 17, 5:12 PM PST. The proposed ruling is written in the plain wording we just settled and is open in Typora (D:\Luke\dev\RimMandrake\design\specs\2026-11-17-judge-flaws-not-polish\6_proposed_ruling_plain.md). It holds the four rules: (1) the judge may refuse only when a promise is not kept, when nobody would notice a broken promise, or when a test or file is itself wrong; (2) one full inspection, then one check of the repairs; (3) a refusal may not create new requirements; (4) only your promises must be proven, the Designer's extra warnings are tips. It also fixes two bugs (a finding rated polish can block; a repaired problem stays refused when a form is missing). 'Recalibrated' means the changed judge is run against known cases before its refusals count. Nothing has been run against a judge yet. Which way do you rule?
**Picked:** Adopt the four rules (Recommended)
**Its description:** Why: few rules you can read and tune, each with one dial. Buys: prompt text plus two small fixes, undone by reverting one commit. Costs: with one full inspection, what the first look misses reaches play; unproven until recalibrated and one mod runs. Recommended: it is the smallest change that stops the repeat looks.
**Other options:** Only the two bug fixes now · Adopt GPT's nine rulings · Four rules, second reader always
