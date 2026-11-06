## Problem
`disk.scratch_dirty_end` has read 5-7 problems almost every run since 2026-11-01 (incident disk-20261101160557). Census 2026-11-03 21:2xZ, `scratch_reap.py --json` (report only): 1104 refused, 9.74 GB.

- 954 of the 1104 (27.5 MB) refuse with `canonical save inside: CANONICAL_Tracked.rws` (some also `_Dropped`, `_Colony`). All 954 sit under `~/.seat-tmp/BENCH/` in `tmp*` or `selftest_run_*` dirs, and those three names appear only in `src/RimMandrake/Utils/selftest_scratch_reap.py`. None is a real canonical save. `~/.seat-tmp/BENCH` holds 591 `tmp*` dirs. The canonical guard is right to refuse them; the litter is the fault.
- Likely leak, UNMEASURED: the selftest's `TemporaryDirectory` never cleans up when the run is killed (it has timed out under load, 600 s tag).
- Other refusals, not part of the litter: 86 for `.git is a file/link` (20 MB, also selftest dirs); `RELENTLESS_DESIGN` and `transfer` under `rm/scratch/BENCH` (4.3 GB), held only because a DISPATCHER shard note names them; session dirs over the 512 MB preserve cap (3.4, 1.2 and 0.7 GB).

## Fix
1. Stop the leak: the selftest removes what it plants even when killed, or a later run removes its own earlier dirs. Do not weaken the canonical guard (`leftovers.CANONICAL_MARKS`).
2. Remove the existing litter once each dir is checked as selftest-made; a real canonical save outside the fixture names stays refused.
3. Look at the named `rm/scratch/BENCH` clones and the over-cap session dirs: unlanded work or not. Report what they were, then release or keep them.

## Not fixed by this
`session_dirs` 554 against the end line of 300: 535 of 555 are YOUNG, so that line reads a busy machine rather than a leak. Raising a line is a loosening and stays with the owner (Conductor); the end reading stays above 0 until that is decided.

## Done when
`refused` is under its end line (60) through a day of nightly and hand runs. Close with `--live "unit=rm-scratch-reap.timer reading=/home/mandrake/.local/state/rm-scratch-reap/sanity.json max_age=3h"`.
