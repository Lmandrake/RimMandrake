# BOUNDARY: a check tree names its owner and goes when its owner ends, Design Version 0.1.0

Code: `one` in `_run_tree_checks` and `install_term_handlers` in `src/RimMandrake/Utils/publish.py`; `own_dir`,
`own_dir_for_run` and `owner_alive` in `src/RimMandrake/Utils/selftest_own_dirs.py`; the module-level `TMP` of
`src/RimMandrake/rimflow/selftest_wrong_check_fixed_in_sitting.py`; `CHECK_TREE`, `fixture_dirs`, `handed_over` and
`sweep_fixtures` in `src/RimMandrake/Utils/scratch_reap.py`. Item:
`RIMMANDRAKE_SPEED_SCRATCH_REAP_SEAT_TMP_PUBLISH_CHECK_RESIDUE_2M`, written Fri 2026-11-27. Each promise has a test of
its name in `src/RimMandrake/Utils/selftest_check_tree_owner.py`.

## Why

On 2026-11-27 `~/.seat-tmp/BENCH` held 2,029,541 entries. 279 folders held 1,128,987 of them: 98 `publish_check_*`
trees (607,507 entries) and 181 `wrong_check_*` trees (521,480 entries). The scratch reap's borrower `find` walks that
folder, and it took 129 s of its 327 s there.

- `./publish` made a `publish_check_` tree for each check, and removed it in a `finally`. A SIGKILL skips the `finally`,
  and so did a SIGHUP, because only SIGTERM had a handler (`_on_term`). 80 of the 98 trees date from 2026-11-23 and
  2026-11-24, before that handler existed.
- `selftest_wrong_check_fixed_in_sitting.py` made its `wrong_check_` tree at import, and removed it only at the end of
  its own `main()`. Four other selftests import the module for its fixtures. Each of their runs left a tree.
- The scratch reap's fixture sweep matched only `selftest_*` and `tmpXXXXXXXX`, so nothing removed either name.

## The design

- A check tree carries its owner. The tree is made by `own_dir`, which writes a marker with the owner's pid and the
  start time of that pid, and a registry entry for its tag (`publish_check`, `wrong_check`).
- The owner removes the tree on every end that a process can catch:
  - a normal end, a refusal or an exception, through the `with` block or `atexit`;
  - SIGTERM or SIGHUP, through `_on_term` in publish, and through own_dir's handler in the selftest.
- A SIGKILL cannot be caught. Then the next `own_dir` of the same tag removes the tree. That is the next check of any
  publish, or the next import of the selftest module. A tree is removed only when its marker matches its registry entry
  and that pid is gone, or now has another start time.
- The scratch reap is the backstop. Its fixture sweep knows the two old names. It holds every tree whose marker names an
  owner that may still run, or whose marker it cannot read.

## The danger the limits guard

- **A tree with no marker is aged, under `FIXTURE_TTL_S` (24 h, unchanged).** A tree with no marker was made by code
  older than this page, so its owner cannot be read. The danger is a live check that loses its TMPDIR. The longest real
  publish that a record shows is about 49 min: the p90 wait of 39 min plus the p90 checks of 9.7 min, on
  `design/specs/2026-11-26-slow-actions/one_page.md`. One timed run there took 1,811 s. 24 h is more than 29 times
  that. The tree must also be untouched, with its newest mtime or ctime inside counted, and no process may use it.
- **`WAIT_S` (600 s) in the selftest.** It is a hang guard for a child that never starts or never ends. The child
  starts in a few seconds at load 27.

## ACCEPTS (the only inputs this is built for)

- **a-check-of-publish.** A check that `_run_tree_checks` runs: a Python file in the landing tree, run with its own
  TMPDIR.
- **an-importer-of-the-fixture-module.** A selftest that imports `selftest_wrong_check_fixed_in_sitting` and uses its
  `TMP`. It may `rmtree` `TMP` itself.
- **a-tree-under-a-seat-tmp.** A `publish_check_*`, `wrong_check_*` or `selftest_*` directory directly under
  `~/.seat-tmp/<SEAT>/`.

## DOES NOT SURVIVE (not promised)

- **a-check-that-outlives-a-killed-publish.** A check child runs in its own session, so a SIGKILL of publish leaves the
  child running. The next publish removes the child's tree under it. Nobody reads that child's result.
- **a-killed-owner-whose-tag-never-runs-again.** The tree waits for the scratch reap's 24 h rule.
- **a-reused-pid-in-the-same-clock-tick.** A pid that is reused with the same start time reads as alive. Then the tree
  is kept, which is the safe side.

## PROMISES (each one is owed a test of the same name)

- **a-terminated-publish-leaves-no-tree.** A SIGTERM to a publish in a check leaves no check tree after it exits.
- **a-hangup-publish-leaves-no-tree.** A SIGHUP to a publish in a check leaves no check tree after it exits.
- **a-killed-publish-tree-goes-at-the-next-run.** The tree of a publish killed by SIGKILL is removed by the next
  `_run_tree_checks`, and no check tree is left.
- **an-imported-wrong-check-tree-goes-at-exit.** A process that imports `selftest_wrong_check_fixed_in_sitting` and
  exits leaves no tree.
- **a-killed-wrong-check-tree-goes-at-the-next-run.** The tree of an importer killed by SIGKILL is removed by the next
  import.
- **a-tree-whose-owner-lives-is-kept.** A tree whose owner process lives is kept by the next publish, and kept by the
  scratch reap's sweep three days later, untouched and with no file handle open in it. Seen red on the planted fault
  "every owner reads gone" and on "the sweep ignores the marker".
- **an-aged-unmarked-check-tree-is-swept.** An unmarked `publish_check_` or `wrong_check_` tree is swept a day
  untouched, a git fixture inside it included. A young one is kept, and so is one that a process uses.
