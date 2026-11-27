# Work bundle WB-cause-RIMMANDRAKE-READ-FIX-CEAB7B4958-WITH-FRESH-EYES-20261127-214222

State: every member done. Context after the one group: 157678 of 1000000 tokens (GO ON).

| ticket | class | outcome | commit |
|---|---|---|---|
| `RIMMANDRAKE_MOVE_PAGES_TO_DATA_STALE_TWICE_HALF_HOUR` | REAL | fixed: the PAGES rows now live in `src/RimMandrake/Utils/boundary_pages.json` (the loader is `boundary_check.load_pages`; an unreadable list gives UNREADABLE exit 3) | a2b07e7a0a, landed c90669d5c5 |

Also done in this run:
- polish 6e2ec28ebe: `code_review_status.code_files` now reads a repo-root file named bare or as `./name`. The line beside
  the clean-means-promises-tested page is taken and removed.
- ebd8b492f4: `steve_lane_sweep.py` no longer passes `shadow=` to `account_plan.tick`. Commit d82260b948 had removed that
  parameter, so `selftest_steve_lane_sweep.py` was red on origin/main and refused the door.
- 3ed7b9d56a (landed 01e724c1a9): a prose repair in `standing_rulings.md`.
- Filed `RIMMANDRAKE_STEADY_LEASE_RENEW_TEST_WALL_CLOCK_SIX_SECONDS`: `selftest_lease.py` flaked at the door.

Next: nothing. The bundle's end files the fresh reader.
