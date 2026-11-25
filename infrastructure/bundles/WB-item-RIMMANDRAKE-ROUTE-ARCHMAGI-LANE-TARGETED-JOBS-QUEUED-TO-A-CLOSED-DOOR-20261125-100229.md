# WB-item-RIMMANDRAKE-ROUTE-ARCHMAGI-LANE-TARGETED-JOBS-QUEUED-TO-A-CLOSED-DOOR-20261125-100229

System: the testq Archmagi backfill lane (`src/RimMandrake/Utils/testq/testq.py` submit and archmagi_tick).

## Done

| member | class | outcome | commit |
|---|---|---|---|
| RIMMANDRAKE_ROUTE_ARCHMAGI_LANE_TARGETED_JOBS_QUEUED_TO_A_CLOSED_DOOR | REAL | fixed; live pass on the real tick; 3 stranded jobs cancelled | 73b6879214 |

## What the next context needs

- The Archmagi lane is a full-list, never-deploy, never-launch borrow of ArchBig, and it is off in `testq-tick.service`
  (no `TESTQ_ARCHMAGI=1`). It can never admit a targeted job. Agents routed three targeted FlowWorks re-runs there on
  2026-11-25 because SteveDesktop was paused for its SSD move.
- Fix: each tick writes `archmagi_state.json` key `admits` (on, profiles); `submit --lane archmagi` refuses a job the
  lane would never admit, with its path to pass. No reading: queued with `lane_warning`.
- Selftest `t_closed_door` in `selftest_testq_archmagi.py`: red 6 on base, green on fix.
- Cancelled J20261125T090025Z-12e1ce, J20261125T094856Z-501503 and J20261125T100829Z-9199e0; notes on
  HARNESS_REPAIR_CAUSE_8135787B_3, HARNESS_REPAIR_CAUSE_3EA971C0 and HARNESS_REPAIR_CAUSE_4AFBF8A2_3.
- `selftest_stage6_checks.py` FAIL 2 on base too (ExplosiveKnockback test table), not this system.

## Context size after each group

- group 1: 174106 of 1000000 tokens.

## Next

Nothing: the bundle is complete. The fresh reader found nothing significant. The list_effect tick closed the member
when its check held. Polish (no ticket): a lane archmagi filler/guard/sweep job is still queued though S3 never admits
one; a `tier:` name in TESTQ_ARCHMAGI_PROFILES would pass submit; the reading lags a unit change by one tick.
