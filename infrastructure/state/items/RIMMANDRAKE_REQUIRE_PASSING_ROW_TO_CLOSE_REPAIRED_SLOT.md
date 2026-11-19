## spec
Codex full-file review of coverage_judge.py (2026-11-18, round 2, finding 1, reproduced by Codex in isolation): an unchecked repair can close a gap and let coverage sign. Prior gap g1 names leaf_wall, whose checklist part failed. Change only the sheet, make no fix claim, and answer `repairs=[{"gap":"g1","repaired":true,...}]` with an empty checklist and no gaps: the delta owes no checklist ids, `all(...)` over the missing rows is true, the slot closes, the old failed row is merged back and coverage can sign (around `coverage_judge.py` `_slots`, line ~574).
Fix: closing a slot requires a present, passing checklist row for every id of that slot.

## verify
Acceptance test: drafted, NOT yet watched failing: one case in `src/RimMandrake/rimflow/selftest_coverage_delta.py` with the scenario above, expecting the slot to stay open and nothing signed; expected 1 new check PASS after the fix.

## criteria
No repair slot closes without a passing row for each of its ids.

## refs
file: src/RimMandrake/rimflow/coverage_judge.py

## done 2026-11-19 (detached helper of the Conductor, item RIMMANDRAKE_READY_PIPELINE_FOR_WRECKED_MACHINES_HE_HOLDS_GO)
`_slots` closes a slot only when every one of its ids has a checklist row this look and each row is all ok, in the
new `repairs` form too (a slot with no ids still closes on its answer: no row to require). The delta keeps its scope
(rows owed for claimed and changed ids only): a carried slot nobody claims stays open unless the judge writes its rows.
Boundary page `design/specs/2026-11-19-coverage-signoff-and-slots/boundary.md`; tests `selftest_coverage_signoff.py`
(`t_a_repaired_slot_closes_only_with_a_passing_row_per_id`, `t_an_unchecked_repair_never_signs`: the Codex scenario
signed `covered` on base, merges to not_covered now). The healthy fixture in `selftest_coverage_judge_loop.py` signed
with an empty checklist (this hole); it now carries its two passing rows.
