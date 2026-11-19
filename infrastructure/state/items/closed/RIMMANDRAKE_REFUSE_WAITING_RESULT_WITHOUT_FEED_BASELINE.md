## spec
A waiting_owner result accepted while the OWNER feed is unreadable stores waiting_owner_feed null, and owner_moved treats a null baseline as never answered, so the concept waits for good even after he answers. Fix: result_errors refuses a waiting_owner result as UNMEASURED when the feed cannot be read.
Found by the Codex full-file review of the split fixes, 2026-11-18 (answer kept at D:\ClaudeWork\rimmandrake\conductor\cr\r_ds_split_fixes.txt).
Acceptance test: python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py (section waiting_result_needs_feed_baseline, 1 case(s) red on 8992cdc87e, watched).

## refs
file: src/RimMandrake/rimflow/designer_stage.py

## criteria
- Its section of selftest_designer_review_findings.py fails on base and passes after; minimal diff inside designer_stage.py.

## verify
python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py
