## spec
program_result ignores a verdict's top-level criteria_suspect, which designer_can_fix honours, so a suspect verdict becomes a program return to stage 3 (Designer rework). Follow-up of RIMMANDRAKE_ROUTE_FLAWED_CRITERION_GAPS_OFF_DESIGNER_REWORK.
Found by the Codex full-file review of the split fixes, 2026-11-18 (answer kept at D:\ClaudeWork\rimmandrake\conductor\cr\r_ds_split_fixes.txt).
Acceptance test: python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py (section program_honours_criteria_suspect, 1 case(s) red on 8992cdc87e, watched).

## refs
file: src/RimMandrake/rimflow/designer_stage.py

## criteria
- Its section of selftest_designer_review_findings.py fails on base and passes after; minimal diff inside designer_stage.py.

## verify
python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py
