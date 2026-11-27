# Work bundle WB-machine-SteveDesktop-20261126-210654 (machine:SteveDesktop)

## Step A, the reality sort (2026-11-26, 1:15-1:40 PM PST)

- `OPS_STEVE_FEED_IDLE_LANE_HURP`: done already. Its last two rings (2026-11-25 04:52Z and 10:57Z) were the lane
  PAUSED by an owner order; b382fc340a (`ops_watch.py` reads quiet while the steward is PAUSED, red on parent in
  `selftest_steve_idle_takeable.py`) fixed that class. The alarm cleared 2026-11-25 11:53Z; it reads 0 min now
  (MEASURED). It owes a guard: shown red with the b382fc340a hunk pulled out, then closed.
- `OPS_STEVE_DIAGNOSE_INVALID_SHARE_UKDG`: keep. The alarm reads 0.04 now (MEASURED) and is clear, but its ring of
  2026-11-25 15:59Z (0.153) was mostly DELIVERY, our machinery: `invalid_class.py --since 2026-11-24T16:00:00Z` reads
  11 of 161 INVALID, DELIVERY 8 (companion_stale 5, tier_modsconfig_drift 3), UNKNOWN 3, GAME 0.

## Step B, the check

- companion_stale: every death after c9b3414628 was a build tied job (proofs or checks) whose sha's companion left
  origin/main while it waited; admission sent it knowing the worker would refuse it. Check:
  `selftest_companion_stage.py`, test `t_a_build_tied_job_whose_companion_left_origin_main_is_cancelled_unspent`
  (5 fails on the parent).

## Step C, the work

- Fix: `testq.admit` cancels such a job on Steve1 with the reason (Steve2 is unchanged: the probe reads only Steve1's
  copies). Boundary: `design/specs/2026-11-24-lane-job-follows-companion/boundary.md`.
- Polish (testq.py changed): `fill_rank_declared` checks its last ranking; its bound `FILL_DROP_ROUNDS` names its
  danger (the 900 s tick). The truncated `both_busy` polish line is deleted as not worth the touch.
- Not taken: tier_modsconfig_drift (3: ModsConfig swap markers on Steve1/Steve2). A separate cause; see the item note.
