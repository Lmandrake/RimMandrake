# PARALLELIZE_SELFTEST_CLI_INTERNAL_1

Split off SELFTEST_SWEEP_EXCEEDS_COMMIT_BUDGET_1. That item's core bug — a
sweep that silently truncates at the 120s tool timeout and reads as green —
was fixed by `src/RimMandrake/Utils/run_selftests.py`. But `selftest_cli.py`
alone measured ~150s solo (2026-09-03), so it stayed the sweep's long pole
and the sweep as a whole did not hit "well under 120s".

## what shipped

Gave each of the 43 cases in `src/RimMandrake/rimflow/selftest_cli.py` its
own scratch directory (`.rimflow_selftest_cli/<case-name>/`, via
`threading.local()` — `_tmp()` resolves to the calling thread's own dir) and
ran them through a `ThreadPoolExecutor` (12 workers) instead of a plain
`for` loop. Every case still drives the CLI as a **real subprocess**, exactly
as before and as the file's own docstring insists on (an in-process call
cannot see a refusal's real exit code or whether its message survived to the
terminal) — nothing about what a case tests changed, only that 43 of them no
longer share one directory and can't run at the same time.

`env()`, `prose()`, `fresh()`, `_bridge_events()`, `_mirror_holder()` and the
~8 test bodies that referenced the old module-level `TMP` directly now all
go through `_tmp()`. The `t_the_bridge_mirror_never_disagrees_...` case,
which already spins up two racing subprocesses *within* one case, is
unaffected — those two still share that one case's own directory on purpose.

## measured, 2026-09-03 (this machine)

`selftest_cli.py` alone: **~150s → ~11s**, run three times back to back with
identical results each time (42/43 passed — the one failure is
`a_free_bridge_offer_says_how_to_take_it`, pre-existing, reproduces solo and
serial too, confirmed unrelated to this change: game-state-dependent, not
parallelism-dependent). No new flakiness from the concurrency — the
throwaway-scratch-dir cleanup (`_run_case`'s `finally: shutil.rmtree`) leaves
nothing behind.

Full `run_selftests.py` sweep: **wall time 153.6s → 28.1s, 23/25 passed** —
`selftest_cli.py` is no longer the long pole. The two remaining failures are
both pre-existing and out of scope here: `selftest_river_link_order.py`
(tracked, `RIVER_LINK_ORDER_SELFTEST_DRIFT_1`, BLOCKED on an owner call) and
`selftest_cli.py`'s one game-state-dependent case above.

This also retroactively satisfies the "well under 120s" half of
`SELFTEST_SWEEP_EXCEEDS_COMMIT_BUDGET_1`'s own criteria, which that item
left unmet and split off to here.

## verify

`python3 src/RimMandrake/rimflow/selftest_cli.py` solo, 3 consecutive runs:
42/43 each time, ~11s each time. `python3 src/RimMandrake/Utils/run_selftests.py`
full sweep: 28.1s wall, `selftest_cli.py` no longer among the slowest lines.

## criteria

All 43 cases still pass (well, the same 42 that passed before — one
pre-existing, unrelated failure), still as real subprocesses — no case
converted to an in-process call. No two concurrently-running cases share a
scratch directory (confirmed: 3 clean consecutive runs, no leftover state,
no new flakiness). `selftest_cli.py` is no longer the sweep's long pole —
confirmed via a fresh full-sweep timing. **Met.**
