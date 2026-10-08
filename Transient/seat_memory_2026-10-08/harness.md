# Harness memory pen (rm-harness.slice) — 2026-10-08

Executes ticket SEAT_MEMORY_CLONES_DRIVES_1, phase-1 harness isolation (design doc §7 table row
"Harness slice", §8 #1 #9 #10). Files: `src/RimMandrake/Utils/run_selftests.py`,
`src/RimMandrake/Utils/rm-harness.slice`, `src/RimMandrake/Utils/selftest_run_selftests.py`.

## Design choices
- **One scope PER TEST** (not one for the pool): each test gets its own `MemoryMax` (cap) and
  `MemorySwapMax=0`, so a cap kill names exactly one test, and the scope's own `memory.events`
  says whether the OOM killer fired. `OOMPolicy=continue` keeps a tiny wrapper (`run_selftests.py
  --_harness-child`) alive in the scope to read `memory.events`/`memory.peak` after the test exits
  and report them on one stderr line; `RuntimeMaxSec=timeout+60` reaps orphans if the runner is
  SIGKILLed. Cost: ~0.1 s systemd-run per test, amortised across workers.
- **Fail closed twice:** a probe scope must land under `rm-harness.slice` AND that slice must have a
  numeric `memory.max` (systemd silently creates an unbounded slice for an unknown name); and each
  test's wrapper re-reads `/proc/self/cgroup` and refuses (rc 97, status PLACEMENT) before running
  the test if it is not in the pen. No probe -> 1 worker in the caller, summary says
  `NOT CONTAINED (<why>) ... --workers N IGNORED`.
- **Admission on live state, no counter:** start the next (slowest-first) test that fits
  `slice memory.current - inactive_file + reserved-but-untouched of our running tests + its estimate
  <= 12G - 2G`; estimate = recorded peak x1.25 (unknown 1G, unknown MEMORY_HEAVY 6G); always start one
  if nothing of ours is running. Per-test `memory.peak` stored in `selftest_peaks.json` beside the
  timings cache; cap = clamp(2 x peak, 3G, 10G), unknown 6G, MEMORY_HEAVY 10G.
- **MEMORY_HEAVY**: still one at a time, but as a lane BESIDE the admitted pool (their isolation was
  memory-only, which admission now covers) — saves ~200 s serial tail. `selftest_render.py`
  (SEQUENTIAL_ISOLATED, CPU timing) still runs alone at the end. Uncontained: old serial behaviour.
- KILLED-by-cap is its own status and count, returns rc 1, and wins even if the test exited 0.
- Measured per-test peaks (2026-10-08): utinnipatches_dump 4.38G, modcheck 2.63G, sw semantics
  2.41G, mandrakepatches 2.13G, two at 1.69G, everything else <= 0.31G.

## Baseline (before)
- 10-08 23:05 FOUNDRY run, 16 workers in-seat: 329/336, wall 223.9 s, **4 rc-137** (OOM), 3 real FAILs
  (`Transient/selftest_after_l0_20261008.txt`).
- Serial sum of last timings: 2631 s (~44 min), 340 entries.
- BENCH seat at start: `claude-seat-BENCH-1206281.scope` memory.current 1.8 GB, peak 2.1 GB, oom_kill 0.

## Proof (a) full suite
Placement checked first: probe -> `/user.slice/user-1000.slice/user@1000.service/rm.slice/rm-harness.slice`
(`systemctl --user show rm-harness.slice`: MemoryMax=12884901888, MemorySwapMax=2147483648); a
2-test `--only` run passed contained before the pool was launched.

| run | workers | result | wall | rc 137 | seat oom_kill | seat memory.peak |
|---|---|---|---|---|---|---|
| before (10-08 23:05, FOUNDRY seat, in-seat) | 16 | 329/336 | 223.9 s | **4** | 23 that night | 10G cap hit |
| after run 1 (BENCH seat, contained) | 8 | **338/338** | 307.1 s | 0 | 0 -> 0 | — |
| after run 2 (BENCH seat, contained, default) | 6 | **338/338** | 297.9 s | 0 | 0 -> 0 | 2684588032 -> 2684588032 (unchanged: tests charge nothing to the seat) |

Full outputs: `suite_run1_w8.txt`, `suite_run2_default.txt` (this folder).

## Proof (b) planted bomb
Temporary `src/RimMandrake/Utils/selftest_zz_planted_bomb.py` (8 GiB in 512 MiB steps; deleted,
never committed), run via `--only`, unknown-peak cap 6G:
```
BEFORE seat: max 0 oom 0 oom_kill 0 oom_group_kill 0
bomb cgroup: 0::/user.slice/user-1000.slice/user@1000.service/rm.slice/rm-harness.slice/rm-harness-1247732-2.scope
KILLED by memory cap: oom_kill=1 in its scope, peak 6.00 GiB, cap 6.00 GiB, rc 137
0/1 passed (... 1 killed-by-cap, 0 failed) — contained in rm-harness.slice (max 12G), 6 workers
AFTER seat:  max 0 oom 0 oom_kill 0 oom_group_kill 0
rm-harness.slice memory.events: oom 1 oom_kill 1
```
Runner rc 1. Fail-closed check: `run_selftests.py --_harness-child -- python3 -c 'print("TEST RAN")'`
from the seat printed the refusal marker (placement = claude-seat-BENCH-1206281.scope), rc 97, and
"TEST RAN" never printed. Fallback check: `RM_SELFTEST_NO_HARNESS=1 ... --workers 8` -> `NOT CONTAINED
(RM_SELFTEST_NO_HARNESS set) — ran in the caller's cgroup with 1 worker, --workers 8 IGNORED`.
The same planted break (512 MiB vs 128 MiB cap -> KILLED) now lives in `selftest_run_selftests.py`.
"Before" for the bomb is the record (10-07/08 seat oom_kill 23, Claude killed), not a re-run: a
6-8G bomb inside this 10G seat would have risked killing this Claude.

## Still-failing tests
None. All 7 of the 10-08 failures pass now: the 4 rc-137 (mandrakepatches, modcheck, sw semantics,
utinni dump) were OOM, and the 3 non-OOM ones (artpipe_state, solarmirrors_fuzz,
items_glob_live) pass on current main (fixed or environmental since; not touched here).

## Unproven
- Two runners at once (BENCH + FOUNDRY) sharing the pen: admission reads the slice's live memory so
  it should account for the other, but this was not exercised.
- The northstar/judge drivers do not use the pen yet (design §4 item 3 names them); only selftests do.
- `selftest_peaks.json` lives in `$TMPDIR` (tmpfs, wiped on reboot); first run after a reboot
  admits on default estimates (1G / 6G heavy), which run 1 shows is still safe.
