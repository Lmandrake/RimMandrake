# BOUNDARY: ./publish keeps one check tree per clone and reuses it, Design Version 0.1.0

Code: `src/RimMandrake/Utils/publish.py` (`full_head_tree`, `_kept_tree_exact`, `_sync_kept_refs`, `_on_term`), and the
pool's `shed` in `src/RimMandrake/Utils/scratch_clone.py`. Item: `RIMMANDRAKE_REUSE_TREECHECK_TREE_EACH_PUBLISH_WRITES_THREE_GIG`,
written 2026-11-25. Each promise has a test of its name in `src/RimMandrake/Utils/selftest_treecheck_kept.py`.

## The failure

Before this page, `full_head_tree` made a new `git clone --shared` and a full checkout for every door check, then
deleted it. On SteveDesktop, 2026-11-25 12:05 AM PST, one such checkout wrote 3.36 GB (1,171 MB in 20 s) and held
`/proc/pressure/io` at `full avg10=59.74`. Four builder runs there were 5.5 hours old, and each publish of each run paid
the checkout again. On Archmagi the same checkout takes about 27 s.

## The design

- One kept tree per clone: `<git dir>/rm-treecheck-kept`, guarded by a flock on `<git dir>/rm-treecheck-kept.lock`.
- A reuse makes the kept tree the commit under test with three git calls: `clean -ffdx` (every file a check run
  left), `checkout -f --detach <sha>` (git rewrites only the paths whose content differs, or whose stat says they
  were touched), and a ref sync (`update-ref --stdin`) that gives the tree the same refs a fresh `git clone --shared`
  of the clone would have. Then it reads the tree: HEAD is the sha, `status --porcelain --ignored -uall` is empty, and
  `ls-files -v` marks no path assume-unchanged or skip-worktree. Any step that fails, or a reading that is not exact,
  removes the kept tree and makes a fresh one in its place, and the output says why.
- **Two users of one clone at once: the second makes its own tree** (a fresh, random-named tree, removed after, as
  before this page). It never waits. Why not wait: `split_pre_existing` opens two trees inside the pipeline checks'
  own tree, in one process, so a wait would wait on itself. Two `./publish` processes of one clone are already in line
  on the clone lock (`clone_lock`), so the second-tree path is the nested case, not a race.
- Why per clone and not one per machine: the disk holds it. Measured 2026-11-25 12:08 AM PST: Archmagi `/` 416 GB
  free, SteveDesktop `/` 753 GB free; the floor (`ops.disk_brake_free_gb` in `src/RimMandrake/Utils/slot_rules.json`)
  is 210 GB on both. 16 kept trees at the largest size seen (4.6 GB) are 74 GB: Archmagi 342 GB free, SteveDesktop
  679 GB, both above the floor with the largest clone (about 15 GB) taken off. A per-machine tree would need a lock
  across clones and a checkout of a different clone's commit each time, so it would rewrite more files per publish.
- Why not a checkout of only the paths the checks read: the checks name no such list, and a check that reads a file
  outside a guessed list would go green blind (the sparse-clone lessons of 2026-11-15). The kept tree judges the whole
  commit, as before.
- The pool keeps a clone's kept tree when it hands the clone to the next run (`shed` removes only the random-named
  trees). The next run's first publish reuses it; promise 2 makes it exact first.

- `publish.py` and this page's selftest are pipeline files (`pipeline_tests.json`), so a change to either runs this
  selftest at the door. `publish.py` was not one before: the slots selftest named it as an input, and that input could
  never fire. `scratch_clone.py` stays out: as a pipeline file it reads red on 14 older lines in the could-not-look and
  time-budget lints (measured 2026-11-25), so a change to `shed` runs this selftest only by hand.

## ACCEPTS (the only inputs this is built for)

- **a-clone-with-a-commit-at-head.** As on the publish door's page: a git work tree whose top is the repo top.
- **a-rev-the-clone-holds.** `rev` names a commit in the clone's object store (HEAD, a replayed tip, a merge base).
- **a-filesystem-with-flock.** The git dir is on a local filesystem where `flock` works (ext4 here).

## DOES NOT SURVIVE (not promised)

- **a-check-orphan-that-writes-after-its-publish-died.** A check child left running by a publish killed with SIGKILL
  can write into the kept tree while the next publish's checks run. The exactness reading is taken once, before the
  checks. A SIGTERM is handled (promise 7), and `subprocess.run` kills its direct child then.
- **an-edit-that-keeps-size-mtime-ctime-and-inode.** git tells an edited file by its stat (size, mtime, ctime, inode).
  A write always moves ctime on Linux, so only a forged filesystem could hide one.
- **the-red-re-run-trees.** `split_pre_existing` runs inside the pipeline checks' kept tree, so its two trees (HEAD's
  commit and the base) are fresh trees, as before this page. Only a publish with a red pipeline check pays them.

## PROMISES (each one is owed a test of the same name)

- **a-second-checkout-rewrites-only-the-files-that-differ.** Two calls for two commits that differ in one file: the
  second call leaves every unchanged file as it was (inode, mtime and ctime the same), and writes the changed file.
- **the-kept-tree-is-exactly-the-commit.** Before each use, the kept tree holds the commit and nothing else: a file a
  check run left (untracked or ignored) is gone, an edit to a tracked file is undone, and a stale or extra ref
  (`origin/main` on an old commit, a branch a check made) is set back to what a fresh clone holds.
- **a-tree-that-cannot-be-made-exact-is-made-fresh.** A kept tree that git cannot read (a broken `.git`, a missing
  object) is removed and made again from nothing, the output says why, and the checks run on the fresh tree.
- **a-second-user-makes-its-own-tree.** While one caller (this process, nested, or another process) holds the kept
  tree, a second call yields a different, fresh tree of its own rev, and removes it after. Neither tree changes the
  other.
- **a-rev-other-than-head-is-checked-out.** A call with `rev` of an older commit yields a tree at that commit, and the
  next call with HEAD moves the same kept tree back.
- **a-clone-back-from-the-pool-gets-no-wrong-tree.** A kept tree left by the last run in a clone (with stray files, an
  edit and a stale ref), after `shed` and a new commit in the clone, is the new commit exactly at the next call. `shed`
  keeps the kept tree and removes a random-named one.
- **a-check-tree-keeps-no-tree-of-its-own.** A call whose `top` is a check tree (`split_pre_existing` is handed the
  kept tree) makes a fresh tree and removes it after; nothing is kept inside a check tree's `.git`. A leftover tree
  inside the kept tree's `.git` (a killed red re-run's) is removed at the next reuse. (Seen on this item's first
  publish, 2026-11-25 12:39 AM PST: the red re-run made a second 4.9 GB kept tree inside the first.)
- **a-killed-publish-leaves-no-random-tree.** A publish ended by SIGTERM (`timeout N ./publish`, a unit stop) runs its
  clean-up: the random-named tree it made is removed. The random-named trees left by older code are still removed by
  the stale sweep after `CHECKTREE_STALE_S`, and the sweep never removes the kept tree or its lock.

## LIMITS

- No new limit. The git calls of a reuse are bounded by the existing hang guard `CHECKTREE_GIT_TIMEOUT_S` (1800 s; its
  danger and evidence are written beside it in `publish.py`).

## PROOF

- See the item's notes: the selftest red on the base commit and green on the fix, and the live publishes on Archmagi
  and SteveDesktop (seconds and bytes written by the checkout).
