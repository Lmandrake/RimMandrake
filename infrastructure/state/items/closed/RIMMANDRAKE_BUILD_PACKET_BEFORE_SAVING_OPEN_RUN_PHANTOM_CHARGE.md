## spec
designer_stage.py open_run writes the running record before building the packet, so a packet that raises (malformed record.json crashes working_record) leaves a run that never launched, and the next open charges its whole reservation as "never closed". Second review finding 11. Fix: build the packet before persisting; working_record tolerates a non-object record.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py (section packet_failure_leaves_no_run, 2 cases red on base 25d20f71e0, watched).

## refs
file: src/RimMandrake/rimflow/designer_stage.py
parent: RIMMANDRAKE_FIX_DESIGNER_STAGE_CODEX_REVIEW_FINDINGS

## criteria
- Its section of selftest_designer_review_findings.py fails on base and passes after; minimal diff inside designer_stage.py.

## verify
python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_stage selftest_designer_repin selftest_designer_stage_land selftest_designer_park
