# RIMMANDRAKE_SEED_DESIGNER_WITH_A_DRAFT_TO_VERIFY

## spec

The brief of RIMMANDRAKE_DRAFT_BIOME_DESIGNER_PASSES_WITH_CODEX_BEFORE_RESET gives the Designer the four Codex lane-E
first-touch drafts (`D:\ClaudeWork\rimmandrake\codex_experiment_20261115\designer\`) as input to verify, not as its
output. The stage machine had no way to do that: the packet carries only the manifest's role files, record.json and the
built section, so a draft could reach a run only by hand-editing a prompt.

Fix: `designer_stage.py init <dir> --mod M --draft <file> [--draft-by WHO]` records the draft's absolute path and sha256 in
stage.json (`draft_input`). Every stage 0-3 packet then carries one line naming it as A DRAFT TO VERIFY, with its sha
checked at packet time (unchanged / CHANGED / UNREADABLE) and the rule: confirm every claim against the source, cite the
source never the draft, record its errors. Stages 4 and 5 do not carry it. A missing file refuses init.

Acceptance test: `python3 src/RimMandrake/Utils/selftest_codex_runner.py`, test `test_draft_is_input_to_verify`. It failed
on the base (ERROR, no `draft` parameter) and passes after: 14 tests, 0 failures; `selftest_designer_stage.py` ALL PASS.
