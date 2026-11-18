# RIMMANDRAKE_UNBLOCK_POLISH_GAPS_EVERY_LOOK_NOT_LATE_ONLY

## spec

FIX (owner by card 2026-11-17 "Judge ruling -> Adopt the four rules (Recommended)"; spec design/specs/2026-11-17-judge-flaws-not-polish/6_proposed_ruling_plain.md, "Two bugs fixed", first bug: "A finding the judge itself rated polish can block today").

FINDING: src/RimMandrake/rimflow/bar_rule.py blocks(gap) (line 88) checks severity only for late gaps (line 91). A gap the judge itself rated severity "polish" on a first look (new_since first/changed/unfixed, no miss_of) BLOCKS. coverage_judge.apply_bar_rule then keeps not_covered when every open gap is polish.

CONTRACT (bar_rule.blocks only):
- severity "polish" never blocks, on any look, late or not; the reason string says it is advice.
- severity "problem": today's behaviour, unchanged (round-1 blocks; a late gap blocks only with late_confirmed).
- severity missing or unknown: today's behaviour (a non-late gap fails closed and blocks; a late+miss_of gap stays advisory).
- apply_bar_rule: a not_covered rec whose open gaps are all polish becomes covered, the polish gaps moved to advisory_gaps (it already does this once blocks says False).

FILES: src/RimMandrake/rimflow/bar_rule.py (blocks, plus its docstring line about severity); src/RimMandrake/rimflow/selftest_judge_card_answers.py (one case, below). No other file, no refactor.

ACCEPTANCE TEST (watched failing on base bbfc765143): python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_polish_never_blocks.py
Base read: "cases read 31; wrong 10 (worst); limit 0", exit 1, e.g. "WRONG polish first: blocks=True, want False". It covers every input kind: severity polish/problem/missing/unknown x new_since first/changed/unfixed/late, with and without miss_of and late_confirmed, plus apply_bar_rule on an all-polish rec. Done = "wrong 0".

CONFLICTING TEST (measured by prototype): selftest_judge_card_answers.py line 61, case "round-1 gap blocks whatever its severity", turns red. That expectation was our own reading (2026-11-16 point 26 answered only late gaps); the 2026-11-17 card names it a bug. Change that single case to: a round-1 problem gap blocks, a round-1 polish gap does not (cite this card in the case text). Every other case there stays as is.

VERIFY: python3 src/RimMandrake/Utils/run_selftests.py --only selftest_bar_rule_tuning_numbers,selftest_judge_card_answers,selftest_coverage_judge,selftest_coverage_delta,selftest_judge_calibration,selftest_coverage_refusal_record,selftest_codex_review_fixes   (and the case file above reads wrong 0). Commit this fix on its own (the card: "two bug fixes as own commits").

CALIBRATION NOTE: bar_rule.py is in refusal_contract.brief_hash; any edit makes the coverage judge's brief UNTESTED (refusals advisory, covered verdicts unsigned) until recalibrated. That is expected and owed separately (RIMMANDRAKE_RECALIBRATE_JUDGE_THEN_RESTAMP_PYRELANDS_ONCE); do not recalibrate in this ticket.

## verify

    python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_polish_never_blocks.py     # must read: wrong 0
    python3 src/RimMandrake/Utils/run_selftests.py --only selftest_bar_rule_tuning_numbers,selftest_judge_card_answers,selftest_coverage_judge,selftest_coverage_delta,selftest_judge_calibration,selftest_coverage_refusal_record,selftest_codex_review_fixes

## criteria

- `python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_polish_never_blocks.py` prints `wrong 0` (it read wrong > 0 on base bbfc765143).
- `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_bar_rule_tuning_numbers,selftest_judge_card_answers,selftest_coverage_judge,selftest_coverage_delta,selftest_judge_calibration,selftest_coverage_refusal_record,selftest_codex_review_fixes` all green.
- The diff touches only the files under ## refs.

## refs

file: src/RimMandrake/rimflow/bar_rule.py
file: src/RimMandrake/rimflow/selftest_judge_card_answers.py
file: design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_polish_never_blocks.py

## What the card said

<!-- answered 2026-11-18T01:17:04Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** Tue Nov 17, 5:12 PM PST. The proposed ruling is written in the plain wording we just settled and is open in Typora (D:\Luke\dev\RimMandrake\design\specs\2026-11-17-judge-flaws-not-polish\6_proposed_ruling_plain.md). It holds the four rules: (1) the judge may refuse only when a promise is not kept, when nobody would notice a broken promise, or when a test or file is itself wrong; (2) one full inspection, then one check of the repairs; (3) a refusal may not create new requirements; (4) only your promises must be proven, the Designer's extra warnings are tips. It also fixes two bugs (a finding rated polish can block; a repaired problem stays refused when a form is missing). 'Recalibrated' means the changed judge is run against known cases before its refusals count. Nothing has been run against a judge yet. Which way do you rule?
**Picked:** Adopt the four rules (Recommended)
**Its description:** Why: few rules you can read and tune, each with one dial. Buys: prompt text plus two small fixes, undone by reverting one commit. Costs: with one full inspection, what the first look misses reaches play; unproven until recalibrated and one mod runs. Recommended: it is the smallest change that stops the repeat looks.
**Other options:** Only the two bug fixes now · Adopt GPT's nine rulings · Four rules, second reader always
