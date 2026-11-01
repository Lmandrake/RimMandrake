# RimFlow v3 build-out: closeout (2026-10-31)

Item `RIMFLOW_V3_BUILD_WHAT_WAS_ONLY_PROSE`. The title asked for every designed part. The owner's card of 2026-10-29 ("Keep hole-fixers, stop the rest") narrowed it to four kept modules and parked the rest pending the v3 collapse. This file is that scope's record.

## Kept modules

Reviews of record are in `D:\ClaudeWork\rimmandrake\v3_review\blind\closeout_96e854cc\`: each read the text `git show` gave at the sha named here (inputs in `in\` and `in2\`, prompts `p_*.md`, `p2_*.md`). The selftests are named in the proof line of the item's contract.

| Module | State | Blind Codex review at 96e854cc53 | Findings | Re-review at 831b57bdc2 |
|---|---|---|---|---|
| Goodbye + backstop | Built. Goodbye restart on. Backstop on for FOUNDRY, off for BENCH. | `r_goodbye.md` | 2 P1 | `r2_goodbye.md`: CLEAN (P0/P1) |
| Findings fold | Built, runs in testq-tick | `r_findings.md` | 1 P1, 4 P2 | `r2_findings.md`: CLEAN (P0/P1) |
| Grant-expiry warning | Built. Nothing renews a grant. | `r_grant.md` | 1 P3, no production defect | Code unchanged after 96e854cc53; that review stands |
| Doc/config reconcile | Items 1-5 of as-built §8 hold | `r_doc.md` | 6 P2 | `r2_doc.md`: CLEAN |

Every P0/P1 at 96e854cc53 (there were no P0):

| Finding | Disposition |
|---|---|
| Goodbye #1, P1: a replacement window that takes his message and dies before running wake is never recorded, so the next window loses that message | Filed: `SEAT_GOODBYE_FIX_REPLACEMENT_DIED_UNREAD` |
| Goodbye #2, P1: a message recovered and answered is replayed once the window that answered it dies owing a later one | Fixed in 831b57bdc2 (`recovered_done`, test G8c) |
| Findings #1, P1: a literal `<ts>` collides with the marker, so two failures merge | Fixed in 831b57bdc2 (escape rule, test C7) |

The P2s were all fixed in 831b57bdc2: findings #2 to #5 (test C7) and doc 1 to 6. The doc's ticket count stays stated as 4 or 5 because its sources disagree and were not re-counted. The grant P3 (the `cmd_next` wiring is checked by source text) is filed: `GRANT_TEST_PROVE_NEXT_REALLY_WITHHOLDS`.

**Tests run red.** The final selftests were run against older code in a scratch copy. `selftest_findings_fold.py`: 24 failures on aeb223e7be, 6 on 96e854cc53 (`red_findings_on_*.txt`). `selftest_seat_restart.py`: G8b and G8c fail on aeb223e7be, G8c fails on 96e854cc53 (`red_restart_on_*.txt`; the other failure at each sha is the scratch copy's, a file it lacks).

## Earlier passes on 10-31

Those reviews read fragments of an uncommitted tree, so no sha can be given for what they read. They are kept in `...\blind\closeout\` as history; the table above is the record. What they found was fixed in 5621583215 (first pass: 3 goodbye P1, findings P1 #1, 6 findings P2, grant `hold_needs`) and 96e854cc53 (second to fourth passes: 5 P2, 1 P3, the P1 on partial table rows).

**Rebutted there, findings #2 (P1, "retire and reopen are absent").** That prompt described the original design. The coordinator simplified the program after two blind reviews so that it groups and reports and never retires or reopens (`findings_fold_rules.json` `_doc`). As-built §2.19a said the opposite and was corrected in 96e854cc53.

**Accepted risk, not re-reported.** Owner 2026-10-29: "Leave the goodbye kill on. If I'm typing at the same time it's an acceptable risk."

## Parked or dropped, not built here

| Item | State | Patch |
|---|---|---|
| `V3_HEALTH_BUILD_DAILY_PULSE_DAY_ONE` | parked | `D:\ClaudeWork\rimmandrake\v3_build\health\parked.patch` |
| `OPS_MODEL_BUILD_V3_TWIN_FIT_DAILY` | parked | `D:\ClaudeWork\rimmandrake\v3_build\model\parked.patch` |
| `AUDITOR_BUILD_WAITING_INDEX_REQUEUE_SCAN`, `INNOVATOR_BUILD_EXPIRY_WATCHDOG_REVERTS`, `HELPERS_BUILD_SHARED_CAP_ACROSS_ROLES` | parked | `D:\ClaudeWork\rimmandrake\v3_build\roles\parked.patch` |
| `PRODUCER_CADENCE_DESIGN_MORE_THAN_WEDNESDAYS`, `TESTLANE_PLAN_WIRE_PRODUCER_PICKS_UNHEARD` | dropped | `D:\ClaudeWork\rimmandrake\v3_build\producer\parked.patch` |

The five parked items still read `doing` with no lease. They wait on `V3_COLLAPSE_BUILD_AFTER_THE_QUIET_MONTH`, which settles them against the trial's winner (`design/RimMandrake/rimflow_v3_collapse_settlement_2026-10-31.md`).

## Open

- `SELFTEST_DISPATCHER_FIX_NINE_RED_BEFORE_ME`: 9 rows of `selftest_dispatcher.py` fail with and without this work (same FAILED list at cd7a8ff7bb).
- `FINDINGS_FOLD_VET_NOTES_BEAT_THE_REVIEW`: re-derive the 61 early live notes.
- `SEAT_GOODBYE_FIX_QUEUED_PROMPT_LOST`: low priority, by the owner's accepted risk.
- `SEAT_GOODBYE_FIX_REPLACEMENT_DIED_UNREAD` and `GRANT_TEST_PROVE_NEXT_REALLY_WITHHOLDS`: from the reviews above.
