## spec
designer_stage.py exam_errors compares examiner to author by exact string, so "agent:a0123456789abcdef (designer)" as author and the same id "(examiner)" as examiner pass. Parent finding 4. Fix: same_agent() both ways, as reader_errors already does.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py (section examiner_is_author_by_id, 1 case red on base 25d20f71e0, watched).

## refs
file: src/RimMandrake/rimflow/designer_stage.py
parent: RIMMANDRAKE_FIX_DESIGNER_STAGE_CODEX_REVIEW_FINDINGS

## criteria
- Its section of selftest_designer_review_findings.py fails on base and passes after; minimal diff inside designer_stage.py.

## verify
python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_stage selftest_designer_repin selftest_designer_stage_land selftest_designer_park
