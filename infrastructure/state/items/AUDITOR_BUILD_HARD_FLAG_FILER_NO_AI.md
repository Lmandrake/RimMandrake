## spec
A program with no AI files every hard flag in the Auditor pre-screen (`audit_prescreen.py` -> prescreen.json
`hard_flagged`) as a defect ticket, so filing never waits on audit capacity (roles/auditor.md "The daily audit" step 1).
- Runs in the Auditor's pre_launch, right after the pre-screen. If the pre-screen is missing, torn, stale or
  malformed, it exits 2 (fail closed, and the Auditor does not start).
- Files one ticket per hard-flagged (item, sha), with `caused_by` set to the item, for the item's owning work seat.
  Dedupe is on the ledger through the `[hardflag ITEM@SHA]` marker, so a rerun never refiles.
- Records the run in `D:\ClaudeWork\rimmandrake\auditor\hardflag_filed.json` (OK or PARTIAL). A refused filing is
  loud but exits 0, and the Auditor files those rows by hand.

## verify
`python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_audit_hardflag_file.py
src/RimMandrake/rimflow/selftest_dispatcher.py` passes. `audit_hardflag_file.py --dry-run` against a fresh
pre-screen lists one ticket per hard flag.
