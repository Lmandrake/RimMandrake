# Work bundle WB-pipeline-conductor-tools-20261126-093136

System: pipeline:conductor-tools. Three members. State: ENDED (every member has an outcome), 2026-11-26.

| member | outcome | commit | evidence |
|---|---|---|---|
| RIMMANDRAKE_CHECK_SEAT_RESTART_TIMER_MONOTONIC_MAY_FIRE_LATE | done already, closed | ae9f0ecdc0 | `seat_restart._tick_soon` arms `systemd-run --on-calendar=<wall-clock due>`; `seat_restart.py` has no `--on-active`; `selftest_seat_restart` (`t_dispatcher_ticks_use_wall_clock_slots`) GREEN on 2026-11-26 |
| RIMMANDRAKE_CUT_CONDUCTOR_DAY_SPEND_PAST_ADVISORY_CAP | dropped, stale | - | the Conductor `daily_token_cap` is 10800000 since 1a612cc1ea (owner's order 2026-11-24, all caps tenfold); the reported day of 1316863 is 12% of it |
| RIMMANDRAKE_TRIM_CONDUCTOR_QUICK_RUN_OVER_BY_A_FIFTH | dropped, stale | - | the Conductor `quick_token_cap` is 3600000 since 1a612cc1ea; the reported run of 436026 is 12% of it |

Step A: 1 done already, 2 stale, 0 kept. Steps B and C had no members.

What the next context needs about this system:
- The item prose of RIMMANDRAKE_CHECK_SEAT_RESTART_TIMER_MONOTONIC_MAY_FIRE_LATE was absent, so `claim` was refused by
  the preflight (E12 no `## refs`, E1 no spec). `close` does not run that preflight, so a done-already member closed
  without a claim.
- The tenfold caps carry the note "review after steven's reset (2:00 PM PST 2026-11-25)" in 1a612cc1ea. That review
  is not work of these tickets.
