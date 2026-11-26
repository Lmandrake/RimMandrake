# BOUNDARY: the run store and the helper pool live under ~/rm/runs, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/run_store.py` (`DEFAULT_ROOT`, `RM_RUNS_ROOT`, `RM_RUNS_RULES`),
`src/RimMandrake/rimflow/detached_helper.py` (`pool_root`, `same_path`, `owns_clone`, `clone_holders`, `project_dir`),
`src/RimMandrake/Utils/scratch_clone.py` (`pool_root`, `clone_in_use`). Item
`RIMMANDRAKE_RENAME_RUN_STORE_AND_POOL_OFF_TICK_PATH`, written 2026-11-26. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_run_root_rename.py`.

Why: the store and the pool were named for a retired pipeline. The tree moved to `~/rm/runs` on each machine while
runs were live, and the old path stays as a symlink to the new one. History (the ledger, closed items, handoffs, run
records) names the old path and still resolves. So a run record, a unit's working directory or a transcript folder
can name the pool by either path, and a reader compares them by their real path.

## ACCEPTS (the only inputs this is built for)

- **a-clone-path-by-either-name.** A clone path through `~/rm/runs` or through the old symlink, in a run record, a
  `/proc/<pid>/cwd` or a claude transcript folder name.
- **the-run-root-from-the-environment.** `RM_RUNS_ROOT` (and `RM_RUNS_RULES`), else the default `~/rm/runs`.

## DOES NOT SURVIVE (not promised)

- **a-pool-reached-through-a-second-symlink-chain-that-is-removed-while-a-run-reads-it.** realpath then fails over.
- **a-unit-outside-the-repo-that-sets-the-old-env-names.** None did on 2026-11-26 on SteveDesktop or Archmagi; the
  old names are not read.

## PROMISES (each one is owed a test of the same name)

- **the-run-root-is-neutral.** `run_store.DEFAULT_ROOT`, `detached_helper.pool_root()` and `scratch_clone.pool_root()`
  name `~/rm/runs`, and `RM_RUNS_ROOT` moves the store. Red on the base: they name the retired path.
- **a-symlinked-pool-clone-is-seen-in-use.** `scratch_clone.clone_in_use` sees a live process whose cwd is in the
  clone when the clone is named through a symlink. Red on the base: it reads the clone as idle.
- **a-record-by-the-old-path-is-the-same-clone.** `owns_clone` and `clone_holders` treat a record that names the clone
  through the symlink as the same clone. Red on the base: the run does not own or hold it.
- **a-transcript-folder-is-found-by-either-path.** `project_dir` returns the folder that exists, of the path as given
  or of its real path. Red on the base: it returns the given path's folder, which does not exist.
