# Boundary: the lock commit of a Design Version is a commit that every clone can read

Code: `landed_lock_commit` and `autolock_and_land` in `src/RimMandrake/rimflow/maturation_autonomy.py`; `lock_bars` (its
refusal for a lock commit that cannot be read) and `_git_has_commit` in `src/RimMandrake/rimflow/maturation.py`. Tests:
each promise has a test of its name in `src/RimMandrake/rimflow/selftest_lock_commit_is_landed.py`.

The failure, 2026-11-27 4:16 AM PST: the tick locked Wrecked Machines 0.1.0 and wrote the HEAD of the dispatch clone,
`b53e34d70527cdd6ab1d8c37c74716851708ddc1`, as `locked_from_commit` in `version/VERSION.json`. That HEAD was a ledger
commit of the dispatch clone ("ledger: DISPATCHER notes (2)"). The landing replayed that ledger commit on origin/main
under another sha, so origin/main never held `b53e34d705`. The steward run in a fresh clone ran
`maturation.py lock-bars WreckedMachines` and read `REFUSED: tree.json at b53e34d705... cannot be read`. The mod stood
at the Designer. The locked files were the same at `b53e34d705` and at its parent `063eb68488`, which origin/main holds.

Offline simulation: no. This code is no state machine. The tests run the real code on real git repos in a temp folder.

## ACCEPTS (the only inputs this is built for)

- **a-clone-of-the-repo.** A git clone whose remote-tracking ref `origin/main` exists. The clone's HEAD is on
  origin/main, or holds commits that origin/main lacks.
- **a-concept-folder.** `design/concepts/<Mod>/` with the files of `maturation.LOCK_PINNED`, some of which can be absent.
- **a-locked-version-file.** `version/VERSION.json` with `state` locked and a `locked_from_commit`.

## DOES NOT SURVIVE (not promised)

- **a-folder-that-is-no-git-clone.** `landed_lock_commit` returns UNMEASURED. A clone with no `origin/main` ref gets its
  HEAD: nothing there says that HEAD is not landed.
- **a-locked-file-changed-in-the-working-tree-only.** The lock reads `tree.json` from the working tree and names a
  commit. A locked file that is edited and not committed is not seen.
- **an-origin-main-ref-that-is-stale.** The landed commit is read from the clone's own `origin/main` ref, with no fetch.
  A stale ref still names a commit that origin/main holds.
- **a-lock-commit-written-by-hand.** A hand lock that writes a `locked_from_commit` which never landed is not prevented.
  `lock_bars` refuses that record and names the repair.

## LIMITS

- Each git call of `landed_lock_commit` and `_git_has_commit` has the deadline of the class `call` in
  `src/RimMandrake/Utils/time_budget.py`, which names its danger (a hung local command holds its caller with no end)
  and its longest real run. The deadline is a hang guard, never a speed bar.

## PROMISES (each one is owed a test of the same name)

- **the-pipeline-lock-names-a-commit-on-origin-main.** `autolock_and_land` writes as `locked_from_commit` the clone's
  HEAD when origin/main holds HEAD. When HEAD holds commits that origin/main lacks, and each locked file is the same at
  HEAD and at the last commit that origin/main holds, the lock names that last commit. A fresh clone of origin/main then
  records the bars with `lock_bars`.
- **a-lock-over-unlanded-locked-files-is-refused.** When a commit that origin/main lacks changed a locked file,
  `autolock_and_land` raises before it writes a file. The error names each locked file that differs and the act that
  clears the refusal (land the mod's concept files). No VERSION.json is locked and nothing is landed.
- **lock-bars-says-when-the-lock-commit-is-not-in-the-clone.** When the clone does not hold the commit that
  `locked_from_commit` names, the refusal of `lock_bars` says so and names the repair: set `locked_from_commit` to the
  commit of origin/main that holds the same locked files, with a journal line. A commit that is in the clone and has no
  `tree.json` keeps its own refusal ("tree.json at ... cannot be read"). Neither case writes `locked_bars.json`.

Later lists beside this page: `polish.md` (none yet); `next_version.md` (none yet).
