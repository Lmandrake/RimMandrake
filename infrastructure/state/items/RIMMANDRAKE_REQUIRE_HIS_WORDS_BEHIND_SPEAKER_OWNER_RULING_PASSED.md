## spec
designer_stage.py authority_errors: an entry with speaker "owner" (a quotation, or an owner-only kind such as floor_disable with no words) whose every cited OWNER:<tsn> event carries none of his words (no ownerSaid, no byCard: a per-ruling Conductor event in the OWNER shard) passes, so Conductor text is stored as his. Parent finding 2, second review finding 8 (speaker part). Fix: when OWNER.jsonl was read, at least one cited OWNER event must hold his words; owner_ev None stays unjudged. The scope_source half of finding 8 is NOT built: under CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM a Conductor event carries his authority (note on the parent). Existing data: design/concepts/ExplosiveKnockback/record.json scope s_design_item would fail this if that LOCKED concept ever reopened (measured 2026-11-18).
Acceptance test: python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py (section speaker_owner_needs_his_words, 2 cases red on base 25d20f71e0, watched).

## refs
file: src/RimMandrake/rimflow/designer_stage.py
parent: RIMMANDRAKE_FIX_DESIGNER_STAGE_CODEX_REVIEW_FINDINGS

## criteria
- Its section of selftest_designer_review_findings.py fails on base and passes after; minimal diff inside designer_stage.py.

## verify
python3 src/RimMandrake/rimflow/selftest_designer_review_findings.py
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_stage selftest_designer_repin selftest_designer_stage_land selftest_designer_park
