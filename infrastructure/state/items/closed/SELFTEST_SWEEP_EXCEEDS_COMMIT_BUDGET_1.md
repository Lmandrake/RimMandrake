# SELFTEST_SWEEP_EXCEEDS_COMMIT_BUDGET_1

## spec

Make "run every selftest before commit" actually run every selftest inside a
normal tool timeout, and make a truncated/failed run visibly distinct from
an all-pass. Update the CLAUDE.md Tools line to whatever the new invocation
is (superseding the raw `for` loop in place).

## what shipped

`src/RimMandrake/Utils/run_selftests.py` — finds every `selftest_*.py` under
`src/`, runs them in a thread pool (default 8 workers, each subprocess given
a 240s cap), and always prints an explicit `N/N passed` plus a named `FAILED:
...` list. Never silently truncates: a hung/slow test reports `TIMEOUT` by
name instead of disappearing. CLAUDE.md's Tools block now points at it.

Found and fixed one real flake this introduced: `selftest_render.py` carries
a hard 100ms self-timing budget inside `render.bench()` (`render.py:653`,
`return 0 if over <= 0 else 1`) that blows out under the CPU/IO contention
of 7 other tests running concurrently — not a bug in the runner, a real
timing assumption in that test that never had to survive contention before.
Fixed by running it `SEQUENTIAL_ISOLATED` — alone, after the parallel pool,
never overlapping another selftest.

Also fixed, found only because the new runner doesn't hide it anymore:
`selftest_one_path_seam.py` was catching a real hardcoded LocalLow path
literal in `design/Jawa/research_review/make_research_prefill.py` (a frozen
dump-capture path — fixed to build off `game_paths.LOCALLOW` for the
machine-specific prefix while keeping the specific capture timestamp
pinned, since that review sheet must stay pinned to the dump it was ruled
against, never drift to a newer capture).

## measured, 2026-09-03 (this machine)

25 selftests, 8 workers: **23/25 pass**, wall ≈153s (dominated by
`selftest_cli.py`'s own ~150s solo floor — 87 real subprocess spawns,
deliberately not in-process per that file's own docstring). Two more
pre-existing, unrelated failures were also caught along the way and
confirmed real+reproducible standalone (not caused by this item, not fixed
here):
- `selftest_cli.py`: `a_free_bridge_offer_says_how_to_take_it` — reproduces
  serially and alone, unrelated to parallelism.
- `selftest_river_link_order.py` — already tracked as
  `RIVER_LINK_ORDER_SELFTEST_DRIFT_1` (BLOCKED, owner call pending).

## verify

`python3 src/RimMandrake/Utils/run_selftests.py` completes without ever
truncating and always prints `N/N passed`; a deliberately-broken selftest
shows up as a named `FAIL` in that summary, not as silence. Confirmed
across three consecutive runs (green, one induced flake fixed, clean rerun).

## criteria — partially closed, remainder split off

**Met:** no seat can get a partial sweep that reads as green — the core bug
is gone. **Not fully met:** "well under 120s" — the sweep's wall time is now
~153s, still dominated by `selftest_cli.py`'s own ~150s solo floor. Fixing
that needs surgery *inside* `selftest_cli.py` (give its 87 cases independent
scratch dirs so they can run concurrently as real subprocesses, without
converting to in-process calls — that tradeoff is explicitly rejected by the
file's own docstring). That's real, separate work, split to
[[PARALLELIZE_SELFTEST_CLI_INTERNAL_1]] rather than bundled in here.
