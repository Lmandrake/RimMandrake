# RimFlow v3 build-out: closeout (2026-10-31)

Item `RIMFLOW_V3_BUILD_WHAT_WAS_ONLY_PROSE`. The title asked for every designed part. The owner's card of 2026-10-29 ("Keep hole-fixers, stop the rest") narrowed it to four kept modules and parked the rest pending the v3 collapse. This file is that scope's record. Reviews are in `D:\ClaudeWork\rimmandrake\v3_review\blind\closeout\`.

## Kept modules

Fix commits: 490b8514d3 as published in a7fef090eb's history (first pass), and the commit that adds this file (passes 2 to 4). Selftests are named in the proof line of the item's contract.

| Module | State | Fresh blind Codex review 10-31 | Outcome |
|---|---|---|---|
| Goodbye + backstop | Built. Goodbye restart on. Backstop on for FOUNDRY, off for BENCH. | `r_goodbye.md`: NOT CLEAN, 3 P1 | All 3 fixed: state saved before the request is consumed; a forced restart cannot outlive its backstop switch; a recovering wake does not replay what a dead window answered |
| Findings fold | Built, runs in testq-tick | `r_findings.md`: NOT CLEAN, 2 P1, 6 P2 | 7 fixed; #2 rebutted below |
| Grant-expiry warning | Built. Nothing renews a grant. | `r_grant.md`: NOT CLEAN, 2 P2 | `hold_needs` must hold bridge and game-up and never offline. The selftest claim is false: that test passes. |
| Doc/config reconcile | Items 1-5 of as-built §8 hold | `r2_doc.md`: NOT CLEAN, 2 P3 | One fixed ("read by no live program"). The other cites a key path that existed only in the review's own fragment. |

Re-reviews of the fixes: `r2_fix.md` (no P1; 5 P2, 1 P3, all fixed), `r3_fix.md` (1 P1, fixed: partial table rows are refused), `r4_fix.md` (CLEAN).

**Rebutted, findings #2 (P1, "retire and reopen are absent").** The prompt described the original design. The coordinator simplified the program after two blind reviews so that it groups and reports and never retires or reopens (`findings_fold_rules.json` `_doc`). As-built §2.19a said the opposite and is corrected.

**Accepted risk, not re-reported.** Owner 2026-10-29: "Leave the goodbye kill on. If I'm typing at the same time it's an acceptable risk."

## Parked or dropped, not built here

| Item | State | Patch |
|---|---|---|
| `V3_HEALTH_BUILD_DAILY_PULSE_DAY_ONE` | parked | `D:\ClaudeWork\rimmandrake\v3_build\health\parked.patch` |
| `OPS_MODEL_BUILD_V3_TWIN_FIT_DAILY` | parked | `D:\ClaudeWork\rimmandrake\v3_build\model\parked.patch` |
| `AUDITOR_BUILD_WAITING_INDEX_REQUEUE_SCAN`, `INNOVATOR_BUILD_EXPIRY_WATCHDOG_REVERTS`, `HELPERS_BUILD_SHARED_CAP_ACROSS_ROLES` | parked | `D:\ClaudeWork\rimmandrake\v3_build\roles\parked.patch` |
| `PRODUCER_CADENCE_DESIGN_MORE_THAN_WEDNESDAYS`, `TESTLANE_PLAN_WIRE_PRODUCER_PICKS_UNHEARD` | dropped | `D:\ClaudeWork\rimmandrake\v3_build\producer\parked.patch` |

The five parked items still read `doing` with no lease. Their state is the supervisor's and the Conductor's to settle once the collapse is decided (`RIMFLOW_V3_SHRINK_FEWER_CHAIRS_SAME_JOBS`).

## Open

- `SELFTEST_DISPATCHER_FIX_NINE_RED_BEFORE_ME`: 9 rows of `selftest_dispatcher.py` fail with and without this work (same FAILED list at cd7a8ff7bb).
- `FINDINGS_FOLD_VET_NOTES_BEAT_THE_REVIEW`: re-derive the 61 early live notes.
- `SEAT_GOODBYE_FIX_QUEUED_PROMPT_LOST`: low priority, by the owner's accepted risk.
- The new findings tests were not separately run red on the old code (the scratch copy could not import `contracts`); the Codex re-reviews read them instead.
