# POLISH: a Stage 6 check goes to a Steve game (a record; nobody works it)

- 2026-11-24, RIMMANDRAKE_UNPAUSE_FLOWWORKS_VISIT_TEN_SUMMARY_HAS_NO_EXIT_BLOCK: `ingame_to_run` reads rows only up to visit N-1, so a driver's list of checks to run names a check that the lane already decided in visit N (one extra run, no wrong verdict).
