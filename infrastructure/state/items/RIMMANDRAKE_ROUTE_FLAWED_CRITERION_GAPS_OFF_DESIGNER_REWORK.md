## spec
designer_stage.py designer_can_fix ignores each gap's criterion_verdict despite its docstring ("none whose criterion the judge calls flawed"), so a second_refusal park over a flawed or unattainable criterion is lifted as Designer rework (standing ruling: a flawed criterion goes to the neutral fixer, never the builder). program_result has the same hole, and also converts a verdict whose contract.advisory is set (park_summary and coverage_judge read both places) into a program return to stage 3. Parent finding 7, lane B probe 'nested advisory'. Fix in designer_stage.py only; coverage_judge.py untouched (its brief was just calibrated).
Acceptance test: python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py (section flawed_criterion_not_designers, 4 cases red on base 25d20f71e0, watched).

## refs
file: src/RimMandrake/rimflow/designer_stage.py
parent: RIMMANDRAKE_FIX_DESIGNER_STAGE_CODEX_REVIEW_FINDINGS

## criteria
- Its section of selftest_designer_review_findings.py fails on base and passes after; minimal diff inside designer_stage.py.

## verify
python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_stage selftest_designer_repin selftest_designer_stage_land selftest_designer_park
