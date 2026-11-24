A time budget read off an idle machine is wrong on ours: Archmagi stood at load 20 to 50 for most of 2026-11-10 to 2026-11-24, and selftest_maturation_autonomy.py took 599 s at load 45 against 36 s alone, so a deadline of 5 times the idle run was 0.3 of the loaded run. Set a budget from the loaded record (time_budget.FACTOR), or guard on progress (src/RimMandrake/Utils/progress_guard.py).
item: RIMMANDRAKE_MEASURE_TIME_BUDGETS_AGAINST_REAL_RUNS_HE_SEES_TEN_PERCENT
home: design/specs/2026-11-24-time-budgets/boundary.md
