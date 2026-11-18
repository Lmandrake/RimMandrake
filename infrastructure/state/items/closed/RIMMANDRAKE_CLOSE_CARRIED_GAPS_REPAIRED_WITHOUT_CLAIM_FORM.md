# RIMMANDRAKE_CLOSE_CARRIED_GAPS_REPAIRED_WITHOUT_CLAIM_FORM

## spec

FIX (owner by card 2026-11-17 "Judge ruling -> Adopt the four rules (Recommended)"; spec design/specs/2026-11-17-judge-flaws-not-polish/6_proposed_ruling_plain.md, rule 2 "decide whether each listed problem was fixed by reading the fix itself, never by whether a form was filed", and "Two bugs fixed", second bug).

FINDING: src/RimMandrake/rimflow/coverage_judge.py delta_merge (line 395) re-adds every carried (unclaimed) gap as `unfixed` and flips a covered word to not_covered, whatever the judge's own checklist rows say. Pyrelands look 8: no claim form matched, the judge redid every row the three carried gaps name, every part ok, and said the changes answer them; the merge refused anyway. The delta prompt (line 385) tells the judge carried gaps are "carried on file (do not repeat them)", so it has no way to close one.

CONTRACT (delta_merge and two sentences; delta_plan and the rows it asks for are unchanged):
- A carried gap CLOSES when all hold, read from the judge's OWN checklist this look (before the prior rows are appended): it names at least one id; every id it names has a row the judge wrote this look; each such row has at least one part and every part has ok True; no gap the judge returned this look (kept or dropped by the merge) names any of its ids.
- A closed gap leaves rec["gaps"] and is listed in rec["answered"] as {"gid","ids","what"}. Every other carried gap is carried exactly as today. A covered word with no carried gap left stands. Closure is by rows, not severity.
- delta_prompt: replace the heading "Gaps still open, carried on file (do not repeat them)" so the prompt carries, verbatim: "A carried gap is closed when every row on its ids that you write this look is all ok; one you find still open, write its row with the part not ok."
- src/RimMandrake/rimflow/roles/designer_lock.md item 3: replace "A gap you do not claim stays open;" with "A gap you do not claim stays open unless the judge's own rows on all its ids read ok; then it is closed and listed as answered."

FILES: src/RimMandrake/rimflow/coverage_judge.py (delta_merge, delta_prompt heading only); src/RimMandrake/rimflow/roles/designer_lock.md (that one sentence). No other file, no refactor.

ACCEPTANCE TEST (watched failing on base bbfc765143): python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_carried_gap_closes_on_ok_rows.py
Base read: "cases read 19; wrong 12 (worst); limit 0", exit 1, e.g. "WRONG look-8 replay: covered: got not_covered". Input kinds: the look-8 replay (tickets/look8_replay.json, real look-7 gaps and look-8 rows); a mix; a row not redone (prior row ok); a not-ok part; a row with no parts; a gap the judge repeats; one it repeats that the merge drops; a gap with no ids; partial ids; the judge's own open gap beside a closing carried gap; a polish carried gap; the prompt sentence; the designer_lock sentence. Done = "wrong 0".

CONFLICTING TESTS: none found (prototype by monkeypatch: every verify test below stayed green).

VERIFY: python3 src/RimMandrake/Utils/run_selftests.py --only selftest_coverage_delta,selftest_coverage_judge,selftest_coverage_judge_loop,selftest_judge_calibration,selftest_designer_quick_look   (and the case file reads wrong 0). Commit this fix on its own (the card: "two bug fixes as own commits").

CALIBRATION NOTE: coverage_judge.py and roles/designer_lock.md are in refusal_contract.brief_hash; any edit makes the coverage judge's brief UNTESTED (refusals advisory, covered verdicts unsigned) until recalibrated. Expected; recalibration is owed separately (RIMMANDRAKE_RECALIBRATE_JUDGE_THEN_RESTAMP_PYRELANDS_ONCE).

## verify

    python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_carried_gap_closes_on_ok_rows.py     # must read: wrong 0
    python3 src/RimMandrake/Utils/run_selftests.py --only selftest_coverage_delta,selftest_coverage_judge,selftest_coverage_judge_loop,selftest_judge_calibration,selftest_designer_quick_look

## criteria

- `python3 design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_carried_gap_closes_on_ok_rows.py` prints `wrong 0` (it read wrong > 0 on base bbfc765143).
- `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_coverage_delta,selftest_coverage_judge,selftest_coverage_judge_loop,selftest_judge_calibration,selftest_designer_quick_look` all green.
- The diff touches only the files under ## refs.

## refs

file: src/RimMandrake/rimflow/coverage_judge.py
file: src/RimMandrake/rimflow/roles/designer_lock.md
file: design/specs/2026-11-17-judge-flaws-not-polish/tickets/look8_replay.json
file: design/specs/2026-11-17-judge-flaws-not-polish/tickets/case_carried_gap_closes_on_ok_rows.py

## What the card said

<!-- answered 2026-11-18T01:17:04Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** Tue Nov 17, 5:12 PM PST. The proposed ruling is written in the plain wording we just settled and is open in Typora (D:\Luke\dev\RimMandrake\design\specs\2026-11-17-judge-flaws-not-polish\6_proposed_ruling_plain.md). It holds the four rules: (1) the judge may refuse only when a promise is not kept, when nobody would notice a broken promise, or when a test or file is itself wrong; (2) one full inspection, then one check of the repairs; (3) a refusal may not create new requirements; (4) only your promises must be proven, the Designer's extra warnings are tips. It also fixes two bugs (a finding rated polish can block; a repaired problem stays refused when a form is missing). 'Recalibrated' means the changed judge is run against known cases before its refusals count. Nothing has been run against a judge yet. Which way do you rule?
**Picked:** Adopt the four rules (Recommended)
**Its description:** Why: few rules you can read and tune, each with one dial. Buys: prompt text plus two small fixes, undone by reverting one commit. Costs: with one full inspection, what the first look misses reaches play; unproven until recalibrated and one mod runs. Recommended: it is the smallest change that stops the repeat looks.
**Other options:** Only the two bug fixes now · Adopt GPT's nine rulings · Four rules, second reader always
