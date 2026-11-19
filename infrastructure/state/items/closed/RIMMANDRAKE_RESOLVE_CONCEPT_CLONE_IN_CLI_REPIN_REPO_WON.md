## spec
designer_stage.py main: the repin verb passes REPO, so repin()'s own "repo or clone_of(d) or REPO" never reaches clone_of and a concept in another clone is re-pinned against this clone's history. Parent finding 9. Fix: pass no repo.
Acceptance test: python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py (section cli_repin_reads_concept_clone, 1 case red on base 25d20f71e0, watched).

## refs
file: src/RimMandrake/rimflow/designer_stage.py
parent: RIMMANDRAKE_FIX_DESIGNER_STAGE_CODEX_REVIEW_FINDINGS

## criteria
- Its section of selftest_designer_review_findings.py fails on base and passes after; minimal diff inside designer_stage.py.

## verify
python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_stage selftest_designer_repin selftest_designer_stage_land selftest_designer_park
