# RIMMANDRAKE_MEASURE_CLONE_LAG_FROM_LAST_PULL_CHURN_TRIPS

## spec
`clone_reading` in `src/RimMandrake/rimflow/maturation_dispatch.py` sets `behind_since` on the first tick that sees the
dispatch clone behind and clears it only on a tick that sees it exactly level. Origin takes ledger commits about every
minute and the dispatch clone pulls `--ff-only` about every 90 s, so a healthy clone can read behind on six ticks in a row
and cross the 5 min line of `maturation.clone_behind_min` (alarm `OPS_DISPATCH_CLONE_BEHIND_UNSTICK_YUYW`). Measured: the
alarm read 6.0 min from 2:23 to 2:42 PM PST on 2026-11-19 while the reflog shows a fast-forward every 1-2 min; at 3:33
PM it read behind 6 for 3.0 min, and the clone was level a minute later. The same transient crossed 12.1 min at 04:50
PST on 2026-11-16 (note on the alarm item).

The danger the alarm guards is that the timers run old code. The age of the code is the time since HEAD last moved,
not the time since the last exactly-level tick. Fix: `clone_counts` also returns HEAD's sha; `clone_reading(st, now,
got, head=<sha>)` keeps `behind_since` while HEAD is unchanged and restarts it at `now` when HEAD advanced. An unknown
HEAD (None) never restarts the clock. A level tick still clears it. A refused fetch stays UNMEASURED.

## refs
file: src/RimMandrake/rimflow/maturation_dispatch.py

## criteria
1. A clone that fast-forwards every 90 s under steady churn never reads `behind_min` of 5 or more.
2. A clone whose HEAD does not move accumulates `behind_min` as today.
3. Level reads 0; a blind fetch stays UNMEASURED; an unknown HEAD does not reset the clock.

## verify
Acceptance test: `python3 design/specs/maturation_dispatch/accept_clone_lag_from_last_pull.py` from the repo root; 5/5
PASS on a correct fix. Watched it fail on base 5f6bc60113 (TypeError: `clone_reading()` has no `head` argument).
Then add its cases to `selftest_maturation_dispatch.py`.
