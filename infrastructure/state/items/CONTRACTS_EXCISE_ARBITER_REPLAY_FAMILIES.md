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

## proof (corrected 2026-11-17, drain of the retired judge)
    python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/contracts/selftest_contracts.py

Work landed at b47c87d04be6 (both families, export and schemas dropped; arbiter_pending.py removed).

## why this is NOT closed: three checks are UNMEASURED, not passing
Measured 2026-11-17: `run_selftests` prints RESULT: GREEN and rc=0, but the file's own line underneath reads

    UNMEASURED ... 366 ok, 0 fail, 3 checks skipped (C2 C4 C8): UNMEASURED, not a pass or a fail

`run_selftests`'s GREEN means "FAIL 0 and CRASH 0", which a skip satisfies. The skip's cause is measured: the
replay base in `src/RimMandrake/contracts/replay.py:40`

    BASE = "c8d1d12855"   # HEAD before the contracts wiring (2026-10-27)

is not a valid object name in this shared clone NOR in the parent repo at /Users/mandrake/dev/RimMandrake/.git
(`git cat-file -t c8d1d12855` -> "fatal: Not a valid object name" in both). That commit is unreachable from
either, so C2/C4/C8 cannot be read here at all — "could not look", not "passed".
This is exactly the gap the item's own `## do` anticipated: "selftest_contracts currently reads UNMEASURED in
seat clones (base commit c8d1d12855 absent): check C2/C4/C8 in a clone that has it."
Evidence: /Users/mandrake/ClaudeWork/scratch/rm-drain-logs/proofs/CONTRACTS_EXCISE_ARBITER_REPLAY_FAMILIES.txt

Next worker: either run the line above in a clone whose history contains c8d1d12855 and read C2/C4/C8, or
find out whether that sha survives anywhere (it may have been lost to a history rewrite, in which case BASE
needs re-pinning to a reachable pre-wiring commit and the re-pin is itself the work). Do not close on the
GREEN: three of this item's own checks have never been read.
