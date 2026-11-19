## spec
designer_stage.py owner_moved: when the OWNER shard is unreadable owner_feed is None, None != the recorded hash, so open_run opens a waiting_owner concept as though he had answered. Second review finding 10. Fix: an unreadable feed refuses as UNMEASURED (could-not-look is not an answer); the concept stays waiting_owner.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py (section unreadable_owner_feed_is_not_an_answer, 1 case red on base 25d20f71e0, watched).

## refs
file: src/RimMandrake/rimflow/designer_stage.py
parent: RIMMANDRAKE_FIX_DESIGNER_STAGE_CODEX_REVIEW_FINDINGS

## criteria
- Its section of selftest_designer_review_findings.py fails on base and passes after; minimal diff inside designer_stage.py.

## verify
python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_stage selftest_designer_repin selftest_designer_stage_land selftest_designer_park
