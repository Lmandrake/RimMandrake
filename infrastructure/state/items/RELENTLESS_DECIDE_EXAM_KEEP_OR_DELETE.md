## spec
Owner card 2026-11-06: the exam gets one last test. About 30 fresh done runs AFTER the sha of the EXAM_SETTER_FIX_DEMANDS_ITS_OWN_MECHANISM fix (32bcb9b44f, rebind approved 2026-11-06). Grade every red with a fresh judge (one that did not set or fix the exam), as the 2026-11-06 grading of 18 reds did.
Keep the exam only if it is wrong at most 10% of its reds AND it caught at least one real defect the blind check missed. Otherwise delete the exam AND the dispute layer (relentless_exam*.py/json, relentless_dispute*.py/json, their selftests and references; wrong material is deleted, each inbound reference fixed).
Do NOT flip anything to enforce either way: RELENTLESS_ENFORCE_BOXRUN_EXAM_DISPUTE waits for this verdict. No new rules, layers or judging machinery.
Done when: the count of fresh runs, the graded reds with the judge's reasons, the wrong-rate and the catches are written to a report path, and the exam is kept or deleted by that rule (deletion in revertable commits).
Source: /mnt/d/ClaudeWork/rimmandrake/conductor/briefs/relentless_design_review_2026-11-06.md; redesign_final.md
