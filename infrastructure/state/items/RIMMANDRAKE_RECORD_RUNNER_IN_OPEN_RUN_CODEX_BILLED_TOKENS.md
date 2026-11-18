## spec
designer_stage.py open_run's running record omits runner, so the retry path (prev.get("runner") == "codex") never fires and a dead Codex run of a runner=codex concept is charged its whole token reservation instead of runner_spend UNMEASURED. Parent finding 6 = second review finding 12. Fix: record st["runner"] in the running record when the concept names one (no runner = the Claude default, charged as today). No role_launch.py change.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py (section open_run_records_runner, 2 cases red on base 25d20f71e0, watched).

## refs
file: src/RimMandrake/rimflow/designer_stage.py
parent: RIMMANDRAKE_FIX_DESIGNER_STAGE_CODEX_REVIEW_FINDINGS

## criteria
- Its section of selftest_designer_review_findings.py fails on base and passes after; minimal diff inside designer_stage.py.

## verify
python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_stage selftest_designer_repin selftest_designer_stage_land selftest_designer_park
