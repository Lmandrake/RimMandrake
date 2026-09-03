# PARALLELIZE_SELFTEST_CLI_INTERNAL_1

Split off SELFTEST_SWEEP_EXCEEDS_COMMIT_BUDGET_1. That item's core bug — a
sweep that silently truncates at the 120s tool timeout and reads as green —
is fixed by `src/RimMandrake/Utils/run_selftests.py` (parallel top-level
runner, explicit N/N, never truncated). But `selftest_cli.py` alone measures
~150s solo (2026-09-03, this machine: `2:31.99 total`, 7.98s user + 10.93s
system — the rest is process-spawn/9p wait, not CPU), so it's still the
sweep's long pole and the sweep as a whole does not hit "well under 120s".

Root cause: 87 cases, each shelling out to a real `python3 cli.py ...`
subprocess (`run()` at `src/RimMandrake/rimflow/selftest_cli.py:75`).
**Not swappable for in-process calls** — the file's own docstring is
explicit about why: "the two things most likely to be wrong in a CLI are
exactly the two an in-process call cannot see: what exit code a refusal
returns, and whether the model's own message survived to the terminal."
Respect that; converting to in-process would be a regression in what the
test can catch, not a speedup worth taking.

The real lever: every case currently shares one hardcoded scratch dir
(`TMP = REPO/.rimflow_selftest_cli`, `selftest_cli.py:35`), wiped by
`fresh()` at the start of each case — so cases are already logically
independent of each other, they just can't run concurrently because they'd
race on that one shared directory. ~14 call sites reference the `TMP`
global directly (lines 67-68, 104, 113-114, 138, 305, 315, 391, 612, 764,
767, 853, 962-963) — not funneled through one or two helpers, so this is a
real mechanical pass, not a one-line fix.

## spec

Give each case (or a small pool of workers) its own scratch directory
instead of one shared `TMP`, and run the 87 cases through a thread/process
pool inside `selftest_cli.py`, keeping every case a real `python3 cli.py`
subprocess invocation exactly as today. `env()`/`prose()`/`fresh()` and the
~8 test bodies that touch `TMP` directly all need to resolve a per-case
path (e.g. `threading.local()`, or thread each case's own dir through an
explicit parameter) instead of the module-level global.

## verify

`python3 src/RimMandrake/rimflow/selftest_cli.py` alone drops from ~150s to
roughly the slowest single case's wall time (well under 30s expected, most
individual `run()` calls measured well under 1s). Re-run the full
`run_selftests.py` sweep afterward and confirm total wall time is well
under 120s with `selftest_cli.py` no longer the dominant line.

## criteria

All 87 cases still pass, still as real subprocesses (no case converted to
an in-process call). No two concurrently-running cases share a scratch
directory. `selftest_cli.py` solo wall time is no longer the sweep's long
pole.
