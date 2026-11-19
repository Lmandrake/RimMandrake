## spec
Second pass of RIMMANDRAKE_REJECT_MALFORMED_DESIGNER_RESULTS_NOT_CRASH: an unparseable exam.json/scenes.json/floor.json raises Refused out of result_errors, so close_run leaves the run open and its charge unsaved; record [1] on a stage-3 return with a question crashes quick_look_errors; inventory {"id": []} crashes unaccounted; non-string sources crash working_record, so the repair run never opens. Fix: run files that do not parse are errors in result_errors; the shape guard runs before the return branch; unaccounted and working_record tolerate bad values.
Found by the Codex full-file review of the split fixes, 2026-11-18 (answer kept at D:\ClaudeWork\rimmandrake\conductor\cr\r_ds_split_fixes.txt).
Acceptance test: python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py (section malformed_run_files_second_pass, 5 case(s) red on 8992cdc87e, watched).

## refs
file: src/RimMandrake/rimflow/designer_stage.py

## criteria
- Its section of selftest_designer_review_findings.py fails on base and passes after; minimal diff inside designer_stage.py.

## verify
python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py
