## spec
Codex full-file review of coverage_judge.py (2026-11-18, round 2, finding 1, reproduced by Codex in isolation): an unchecked repair can close a gap and let coverage sign. Prior gap g1 names leaf_wall, whose checklist part failed. Change only the sheet, make no fix claim, and answer `repairs=[{"gap":"g1","repaired":true,...}]` with an empty checklist and no gaps: the delta owes no checklist ids, `all(...)` over the missing rows is true, the slot closes, the old failed row is merged back and coverage can sign (around `coverage_judge.py` `_slots`, line ~574).
Fix: closing a slot requires a present, passing checklist row for every id of that slot.

## verify
Acceptance test: drafted, NOT yet watched failing: one case in `src/RimMandrake/rimflow/selftest_coverage_delta.py` with the scenario above, expecting the slot to stay open and nothing signed; expected 1 new check PASS after the fix.

## criteria
No repair slot closes without a passing row for each of its ids.

## refs
file: src/RimMandrake/rimflow/coverage_judge.py
