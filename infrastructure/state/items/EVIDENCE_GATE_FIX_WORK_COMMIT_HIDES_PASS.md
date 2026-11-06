## spec
Found by EVIDENCE_SHADOW_FIX_REPORT_NEVER_READS_ZERO, on a 2026-11-06 22:30Z snapshot (`evidence_gate.py rescore`, receipts included): 3 of 170 rows stay unexplained. One is the ruled unrunnable case (OPS_CHURN_DIAGNOSE_RELENTLESS_BBZJ_VGUX). These two are not:

- RELENTLESS_VET_FULL_FILE_BEFORE_CLEAN closed at 88360b389b, whose own record holds a red run from before the clean mark. Its candidate 0a0e109a3b is a descendant, `_same_work` says True, and the candidate holds a green run and a Marker PASS. `_record_for` returns the close sha's own record first, so the stale red wins over the pass.
- RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN closed at e8c7158e6f, with no record there. Its candidate 0a387e4e0e holds green + PASS, but `_same_work` says False, so no record is read. Why it says False is not yet read: the diff and the item's commits are the place to look.

Also unexplained by anything yet: DEPLOY_GUARD_FIX_EXCLUDE_DIR_MISMATCH has accept rows at f160d57cf8 (2026-11-06 13:52Z to 21:58Z) and the ledger holds no close event for the item, whose store state is `blocked`. Something refuses after the shadow row is written, so those rows count closes that never happened.

Do not add a cohort for these. Done when: each case is either a predicate fix pinned by selftest_evidence_gate, or a row the reading keeps calling unexplained with the reason filed here.
