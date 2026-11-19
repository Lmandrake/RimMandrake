## spec
The Codex check of the follow-up repairs (2026-11-18, D:\ClaudeWork\rimmandrake\conductor\cr\r_ds_split_repairs_check.txt) found four incomplete: an unparseable exam_control/copy.json raised Refused out of control_copy_errors (run left open, charge unsaved); park_summary crashed on a malformed record.json (close_run or open_run parking, e.g. RIMFLOW_MODE=afk); an ask with no author bypassed the independent-review check; a concept with no item could still accept a waiting_owner result and wait for good. Fixes in designer_stage.py only: copy.json parse failure is an exam error; park_summary normalises a malformed record; an ask names its author; waiting_owner needs the concept's item. Existing data: 0 sent asks without an author under design/concepts [measured].
Acceptance test: python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py (section repair_check_leftovers, 5 cases red on b71e54ede2 in a throwaway clone, watched).

## refs
file: src/RimMandrake/rimflow/designer_stage.py

## criteria
- Its section of selftest_designer_review_findings.py fails on base and passes after.

## verify
python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py
