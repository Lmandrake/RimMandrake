## spec
ask_errors compares review.by to the ask's author as whole strings, so the author's own agent id under another label ("(author)" vs "(reviewer)") reviews its own ask. Same class as RIMMANDRAKE_MATCH_EXAMINER_TO_AUTHOR_BY_ID_NOT_LABEL. Fix: same_agent both ways, exact match kept.
Found by the Codex full-file review of the split fixes, 2026-11-18 (answer kept at D:\ClaudeWork\rimmandrake\conductor\cr\r_ds_split_fixes.txt).
Acceptance test: python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py (section ask_reviewer_is_author_by_id, 1 case(s) red on 8992cdc87e, watched).

## refs
file: src/RimMandrake/rimflow/designer_stage.py

## criteria
- Its section of selftest_designer_review_findings.py fails on base and passes after; minimal diff inside designer_stage.py.

## verify
python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py
