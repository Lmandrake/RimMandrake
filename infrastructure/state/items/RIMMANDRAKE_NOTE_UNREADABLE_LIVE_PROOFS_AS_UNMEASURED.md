## spec
built_evidence swallows every OSError listing infrastructure/state/live_proofs, so an unreadable folder reads as no proofs and stage 0 can finish without accounting for them, against its own docstring (notes name what could not be read). Fix: a missing folder is no proofs; any other OSError is a note.
Found by the Codex full-file review of the split fixes, 2026-11-18 (answer kept at D:\ClaudeWork\rimmandrake\conductor\cr\r_ds_split_fixes.txt).
Acceptance test: python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py (section unreadable_live_proofs_noted, 1 case(s) red on 8992cdc87e, watched).

## refs
file: src/RimMandrake/rimflow/designer_stage.py

## criteria
- Its section of selftest_designer_review_findings.py fails on base and passes after; minimal diff inside designer_stage.py.

## verify
python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py
