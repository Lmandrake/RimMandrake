## spec
Found by EVIDENCE_SHADOW_FIX_REPORT_NEVER_READS_ZERO, on a 2026-11-06 22:30Z snapshot (`evidence_gate.py rescore`, receipts included): 3 of 170 rows stay unexplained. One is the ruled unrunnable case (OPS_CHURN_DIAGNOSE_RELENTLESS_BBZJ_VGUX). These two are not:

- RELENTLESS_VET_FULL_FILE_BEFORE_CLEAN closed at 88360b389b, whose own record holds a red run from before the clean mark. Its candidate 0a0e109a3b is a descendant, `_same_work` says True, and the candidate holds a green run and a Marker PASS. `_record_for` returns the close sha's own record first, so the stale red wins over the pass.
- RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN closed at e8c7158e6f, with no record there. Its candidate 0a387e4e0e holds green + PASS, but `_same_work` says False, so no record is read. Why it says False is not yet read: the diff and the item's commits are the place to look.

Also unexplained by anything yet: DEPLOY_GUARD_FIX_EXCLUDE_DIR_MISMATCH has accept rows at f160d57cf8 (2026-11-06 13:52Z to 21:58Z) and the ledger holds no close event for the item, whose store state is `blocked`. Something refuses after the shadow row is written, so those rows count closes that never happened.

Do not add a cohort for these. Done when: each case is either a predicate fix pinned by selftest_evidence_gate, or a row the reading keeps calling unexplained with the reason filed here.

## outcome by case (read 2026-11-06)

- DEPLOY_GUARD_FIX_EXCLUDE_DIR_MISMATCH: those closes never happened because they were never real. `selftest_relentless_nocode_close.py` closes a fixture carrying that real item id at the real f160d57cf8 on a throwaway ledger, and its cli subprocess inherits a worker's `RELENTLESS_ROOT`, so `cli._evidence_shadow` logged the fixture's close to the real store. Reproduced into a temp root: same row shape, `closed_by` relentless. The store's state.json for the item has not changed since 2026-11-05. Fixed by `evidence_gate.own_root`, pinned in selftest_evidence_gate (red under the old guard). **The rows already in the append-only log stay, and the reading keeps calling them unexplained for this reason**; `report --since` past this fix leaves them out. No cohort.
- RELENTLESS_VET_FULL_FILE_BEFORE_CLEAN: `_record_for` takes the close sha's own record first, as the spec says.
- RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN: `_same_work` says False only because `src/RimMandrake/rimflow/relentless.py` differs between e8c7158e6f and the candidate, changed by 35fbf75bb7, another item's commit (RELENTLESS_VET_FULL_FILE_BEFORE_CLEAN), in a file this item's own commits touched. No commit naming this item touches code after e8c7158e6f.
- The two predicate fixes belong to EVIDENCE_GATE_FIX_WORK_SHA_HIDES_CANDIDATE, filed first with the same two cases and in progress on the same two functions when this was read. This item waits on it, then checks both real rows against what it pinned.
