## spec
designer_stage.py close_run crashes instead of rejecting a malformed result: record.json [1] (AttributeError at stage 0/1), {"asks": 3} (TypeError at stage 2 and on waiting_owner) after record_errors already named the shape; an interaction scene with no id (KeyError in scene_errors); an unparseable result.json (read_json raises Refused, so nothing is recorded or charged and the run stays open). Second review finding 9 and lane B's probes. Fix: stop at record_errors' structural errors, skip id-less scenes in the interaction pass, and turn an unreadable result.json into a rejection with its charge.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py (section malformed_results_reject, 6 cases red on base 25d20f71e0, watched).

## refs
file: src/RimMandrake/rimflow/designer_stage.py
parent: RIMMANDRAKE_FIX_DESIGNER_STAGE_CODEX_REVIEW_FINDINGS

## criteria
- Its section of selftest_designer_review_findings.py fails on base and passes after; minimal diff inside designer_stage.py.

## verify
python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_stage selftest_designer_repin selftest_designer_stage_land selftest_designer_park
