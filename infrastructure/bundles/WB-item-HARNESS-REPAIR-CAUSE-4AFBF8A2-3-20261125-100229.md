# WB-item-HARNESS-REPAIR-CAUSE-4AFBF8A2-3-20261125-100229

System: modcheck live runner (src/RimMandrake/Utils/modcheck/runner.py), the site hold after live drivers.

## Members

| member | class | commits | state |
|---|---|---|---|
| HARNESS_REPAIR_CAUSE_4AFBF8A2_3 | REAL, class SITE (note 4) | 04278d644f, 4fd408d81b (both on origin/main) | fixes landed; live re-run owed |

## Learned

- The re-run J20261125T082455Z-f27001 ran at 04278d644f only (the first fix): INVALID HARNESS, "after the live drivers:
  companion profile is 'campaign', not 'test'". 4fd408d81b (the second fix) targets that refusal. No re-run includes it yet.
- The re-run J20261125T085621Z-04f989 (at dbe3190599, which does NOT contain 4fd408d81b) was cancelled by the owner,
  2026-11-25 1:05 AM PST: SteveDesktop is wound down for the move of its clones to the SSD; resubmit to an Archmagi game.
- The item's outcome check names job J20261125T082455Z-f27001 by id; it must be re-shaped to the new job id.
- Negative control `retest.py passed J20261124T073045Z-a73766 HARNESS_REPAIR_CAUSE_4AFBF8A2_3` exits 1 (2026-11-25 2:08 AM PST).

## Next, in order

1. Take the job id of the Archmagi-lane re-run (submitted 2026-11-25 ~2:08 AM PST at cc04baa6ad).
2. Re-shape the outcome check to that job id; wait for the job; `retest.py passed <job> HARNESS_REPAIR_CAUSE_4AFBF8A2_3`.
3. Close with 4fd408d81b and the reading.

## Context size after each group

- after reading and submit: 98548 of 1000000
