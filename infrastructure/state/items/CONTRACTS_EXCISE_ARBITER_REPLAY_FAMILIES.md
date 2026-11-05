## problem
The Arbiter role is retired (CONCEPT_LOCK_UNBLOCK_SIGNER_NEVER_CALLED, owner "Go ahead." 2026-11-05; shas b0a1058ccb,
ecb3a546c4, b1cfdbf572). `rimflow/arbiter_pending.py` stayed because the contracts package still reads it:
`contracts/replay_worker.py` (verdicts / tiers_history families, `verdicts_read_stores`, `tiers_read_jsonl`),
`contracts/replay.py` (FAMILIES, STORES paths under D:\ClaudeWork\rimmandrake\arbiter*, model map),
`contracts/compat.py` (verdict_row_problems, tiers_row_problems), `contracts/models.py` section 4 (ArbiterVerdict,
TiersHistoryRow), `contracts/export.py` + `schemas/arbiter_*.schema.json` (C5), `fixtures/make_fixtures.py`
(verdict_lines, tiers_lines), `fixtures/verdicts.jsonl`, `fixtures/tiers_history.jsonl`, `fixtures/expected.json`,
`fixtures/allowances.json`, `selftest_contracts.py` (C6 import, C11).
## do
Delete both families and the export/schemas, regenerate fixtures/expected.json, then `git rm` arbiter_pending.py.
Fix every inbound reference (contracts/__init__.py line 9). Leave D:\ClaudeWork\rimmandrake\arbiter\ data on disk.
selftest_contracts currently reads UNMEASURED in seat clones (base commit c8d1d12855 absent): check C2/C4/C8 in a
clone that has it.
## also seen
infrastructure/state/CONDUCTOR_GOALS.md goal 1 (due 11-04) still names the Arbiter as "the thing that tests Foundry";
the Conductor owns that file.
