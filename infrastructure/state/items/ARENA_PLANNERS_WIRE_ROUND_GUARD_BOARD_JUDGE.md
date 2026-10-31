# ARENA_PLANNERS_WIRE_ROUND_GUARD_BOARD_JUDGE

## Status (2026-10-30, FOUNDRY builder, sha 6942c578be)
Board half wired: `ralph_c_loop.Board.__init__` takes a required `contains=` (`board_contains`: fix shas from the
judge's hidden files via `arena_trial.hidden_fix_shas`, relation from `arena_rounds.contains_for`; a task without a
base or fix sha refuses the board). `Board.assign` gives only `arena_rounds.first_givable` over the open tasks and
says "sibling order: X waits on Y" when it holds one back.

Judge half: no wiring is needed for order. `arena_judge.ArmMap.assign(arm, task, base, head)` gives no task and
forms no rounds; it only allocates a blind id for a submission that already exists (its one caller is `judge()`).
Skipping it cannot run tasks out of order. arena_judge.py is frozen for the trial (vet cache key) and was not touched.

Remaining gap (filed as a note on ARENA_PLANNERS_ENFORCE_SIBLING_ORDER, not fixed here): ralph_a_loop and trio_loop
work their `--tasks` list in the given order with no sibling check, so an out-of-order list would run out of order.

## criteria
- A1 L0: `run_selftests.py --only src/RimMandrake/Utils/arena/selftest_arena_ralph_c.py` passes: P6 (a2 refused T2 while a1 holds T1, given after), the two guard MUTATIONS go RED, and t_board_contains (T2 -> [T1], Refused on a missing fix, TypeError with no contains).
- A2 L0: `ArmMap.assign` gives no task (read: arena_judge.py `judge()` is its only caller), so the judge needs no order guard.
- A3 L1: a live ralph_c board run over the trial list logs "sibling order: ... waits on ..." for a contained task and never gives it before its contained task is done.
