## spec
close_run records pinned_at from the closing repo's HEAD (the Dispatcher's clone), while the concept's files live and land from clone_of(d); repin's input_changes then runs in the concept's clone and may not resolve the anchor (UNMEASURED refusal of a legitimate re-pin). Fix: anchor from clone_of(d) or repo, as artifact_repo already does.
Found by the Codex full-file review of the split fixes, 2026-11-18 (answer kept at D:\ClaudeWork\rimmandrake\conductor\cr\r_ds_split_fixes.txt).
Acceptance test: python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py (section pin_anchor_from_concept_clone, 1 case(s) red on 8992cdc87e, watched).

## refs
file: src/RimMandrake/rimflow/designer_stage.py

## criteria
- Its section of selftest_designer_review_findings.py fails on base and passes after; minimal diff inside designer_stage.py.

## verify
python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py
