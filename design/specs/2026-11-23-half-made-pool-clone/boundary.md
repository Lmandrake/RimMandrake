# BOUNDARY: a launch never fails because a pool clone's checkout is incomplete, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/detached_helper.py` (`take_clone`, `move_half_made_aside`, `clone_holds_work`). Item
`RIMMANDRAKE_REPLACE_HALF_MADE_POOL_CLONE_LAUNCH_FAILED_THRICE`, written 2026-11-23. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_take_clone_half_made.py` (real git, real ./sync; only scratch_clone is faked).

Why: on 2026-11-23 (11:12 to 11:16 PM PST) a pool clone whose first checkout died partway (HEAD set, 23,639 files missing,
no `./sync` at its root) made three launches in a row fail with `[Errno 2] No such file or directory: './sync'`, because
take_clone reused any pool directory that had a `.git`. A hand moved the clone aside.

## ACCEPTS (the only inputs this is built for)

- **a-pool-directory-for-an-item.** `<pool>/clones/<ITEM>.det` (or a resume's fresh name): absent, a whole clone, a clone with
  no `./sync` at its root, a directory with no `.git`, or an empty directory.

## DOES NOT SURVIVE (not promised)

- **a-clone-with-sync-but-otherwise-broken.** A clone that holds `.git` and `./sync` is reused as before; its `./sync` still
  decides (a failing sync still refuses the launch).
- **a-failed-fresh-clone.** If scratch_clone itself fails, the launch still fails with its output.

## PROMISES (each one is owed a test of the same name)

- **a-complete-clone-is-reused-unchanged.** A clone with `.git` and `./sync` is synced and reused: same directory, nothing
  moved, no new clone. Red on the base: never (must stay green).
- **a-half-made-clone-is-replaced-not-failed.** A clone with no `./sync` that holds no work (nothing but deleted files, or no
  files at all) is moved beside the pool's clones as `<name>.halfcheckout-<time>`, a fresh clone is made at its place, and the
  returned line says so in one line. Red on the base: `FileNotFoundError: './sync'`.
- **a-half-made-clone-holding-work-is-never-destroyed.** A clone with no `./sync` that holds a commit on no remote ref, a
  changed file or an untracked file is moved (whole, commit intact) to the agent storage root's retired-trees folder, and a
  fresh clone is used. Nothing is deleted. A deleted file is not work (HEAD still holds it); a git answer that cannot be read
  counts as work.
- **a-directory-with-no-git-is-moved-aside-and-replaced.** A non-empty directory with no `.git` goes to retired-trees; an
  empty one is taken away; a fresh clone is made. Red on the base: scratch_clone refused "already exists".
- **a-stale-lock-file-never-blocks-a-launch.** A `.det.lock` file left by a dead holder never blocks (flock dies with its
  holder); the launch proceeds at once.
