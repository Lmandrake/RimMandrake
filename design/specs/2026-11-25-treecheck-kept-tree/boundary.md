# BOUNDARY: ./publish keeps one check tree per tree-check slot of the machine and reuses it, Design Version 0.2.0

Code: `src/RimMandrake/Utils/publish.py` (`full_head_tree`, `_kept_tree_exact`, `_sync_kept_refs`, `_on_term`), and the
pool's `shed` in `src/RimMandrake/Utils/scratch_clone.py`. Item: `RIMMANDRAKE_REUSE_TREECHECK_TREE_EACH_PUBLISH_WRITES_THREE_GIG`,
written 2026-11-25; the trees moved from the clone to the machine under `RIMMANDRAKE_SHRINK_STEVEDESKTOP_CLONES_FOUR_FILL_ITS_EIGHTY_GIG`
the same day. Each promise has a test of its name in `src/RimMandrake/Utils/selftest_treecheck_kept.py`.

## The failure

Before this page, `full_head_tree` made a new `git clone --shared` and a full checkout for every door check, then
deleted it. On SteveDesktop, 2026-11-25 12:05 AM PST, one such checkout wrote 3.36 GB (1,171 MB in 20 s) and held
`/proc/pressure/io` at `full avg10=59.74`. Four builder runs there were 5.5 hours old, and each publish of each run paid
the checkout again. On Archmagi the same checkout takes about 27 s.

## The second failure (the same day)

One kept tree per clone was 4.7 GB in each clone. On SteveDesktop, where `~/rm` is an 80 GB disk on the NVMe, at
11:56 AM PST four helper clones of 10 to 11 GB each (4.7 GB of it the kept tree) left 8.5 GB free, and the pool
refused a fifth run at its disk floor.

## The design

- The machine keeps `kept_n()` trees, one per tree-check slot (`treecheck_slots.slots_n()`, 2; `PUBLISH_KEPT_TREES`
  overrides): `<RM_ROOT>/treecheck-kept/rm-treecheck-kept-<i>`, each guarded by a flock on `rm-treecheck-kept-<i>.lock`
  beside it (`PUBLISH_KEPT_ROOT` overrides the folder). Every door check takes a slot first, so no more callers than
  trees come at once. A call takes the first free tree, the one this clone used last first (`.git/rm-kept-top`): the
  fewest files differ.
- A tree may last have served another clone. A reuse repoints it at this clone: its `objects/info/alternates` names
  this clone's objects (as a fresh `git clone --shared` of it would) and its `remote.origin.url` names this clone.
  `checkout -f` reads none of the last clone's commits (measured 2026-11-25: a checkout whose old HEAD is in no
  object store succeeds), so the last clone may be gone.
- A repo outside `RM_ROOT` (a selftest's temp repo) keeps its one tree in its own git dir, as before, so no test writes
  the machine's trees.
- A clone's own kept tree of the old layout (`<git dir>/rm-treecheck-kept`) is removed at its next publish when no
  publish holds its lock, and by the pool's `shed`.
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
- Why per machine and not per clone: the disk. A tree per clone is 4.7 GB per clone, 75 GB for a pool of 16, more
  than SteveDesktop's whole `~/rm` disk. The machine's two trees are 9.4 GB whatever the count of clones. The cost: a
  reuse for another clone also rewrites the files that differ between the two clones' commits, a few hundred at most
  between clones near origin/main.
- Why not a checkout of only the paths the checks read: the checks name no such list, and a check that reads a file
  outside a guessed list would go green blind (the sparse-clone lessons of 2026-11-15). The kept tree judges the whole
  commit, as before.
- The pool's `shed` removes every check tree in a clone it hands to the next run; the machine's trees are not in the
  clone. The next run's first publish reuses a machine tree; promise 2 makes it exact first.

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
- **a-second-user-makes-its-own-tree.** While one caller (this process, nested, or another process) holds a kept
  tree, a second call gets another of the machine's kept trees; while all are held, a fresh tree of its own rev, removed
  after. No tree changes another.
- **a-rev-other-than-head-is-checked-out.** A call with `rev` of an older commit yields a tree at that commit, and the
  next call with HEAD moves the same kept tree back.
- **a-clone-back-from-the-pool-gets-no-wrong-tree.** A kept tree left by the last run in a clone (with stray files, an
  edit and a stale ref), after `shed` and a new commit in the clone, is the new commit exactly at the next call. `shed`
  removes every check tree in the clone (a random-named one, the old layout's kept tree and its lock) and never a
  machine tree.
- **a-check-tree-keeps-no-tree-of-its-own.** A call whose `top` is a check tree (`split_pre_existing` is handed the
  kept tree) makes a fresh tree and removes it after; nothing is kept inside a check tree's `.git`. A leftover tree
  inside the kept tree's `.git` (a killed red re-run's) is removed at the next reuse. (Seen on this item's first
  publish, 2026-11-25 12:39 AM PST: the red re-run made a second 4.9 GB kept tree inside the first.)
- **a-killed-publish-leaves-no-random-tree.** A publish ended by SIGTERM (`timeout N ./publish`, a unit stop) runs its
  clean-up: the random-named tree it made is removed. The random-named trees left by older code are still removed by
  the stale sweep after `CHECKTREE_STALE_S`, and the sweep never removes the kept tree or its lock.
- **one-kept-tree-serves-every-clone-of-the-machine.** A kept tree that served clone X is reused for clone Y: it is
  exactly Y's commit with the refs of a fresh clone of Y, it rewrites only the files that differ, it borrows Y's
  objects and names Y as its origin. After X is removed, and with the tree's HEAD on a commit only X held, Y still
  reuses it. More clones add no tree, on the machine or in a clone.
- **a-clone-keeps-no-kept-tree-of-its-own.** A clone's own kept tree of the old layout is removed at its next call and
  the output says so; while an older publish holds its lock, it stays and the checks still run.
- **a-repo-outside-rm-root-keeps-its-tree-in-its-own-git-dir.** A repo outside `RM_ROOT` keeps one tree in its own
  `.git` and reuses it; a clone under `RM_ROOT` uses the machine's.

## LIMITS

- No new limit. The git calls of a reuse are bounded by the existing hang guard `CHECKTREE_GIT_TIMEOUT_S` (1800 s; its
  danger and evidence are written beside it in `publish.py`).

## PROOF

- 2026-11-25, the machine's trees: the selftest is green, 11 of 11, and 18 of 18 planted faults are caught (among them
  alternates not repointed, origin not repointed, a tree per clone again, the old tree kept, one tree whatever the
  slots). `evidence/` holds the readings of the per-clone version below.

- The selftest, 2026-11-25 1:00 AM PST: red on the base commit 0070ebed21 (`evidence/selftest_red_on_base.txt`, 9
  failing; its second checkout rewrote 41 of 41 files), green on the fix (`evidence/selftest_green_on_fix.txt`, 8 of 8;
  1 of 41 files rewritten), and 14 of 14 planted faults caught (`evidence/selftest_mutants.txt`).
- Archmagi, 2026-11-25 12:28 AM to 1:02 AM PST, two `./publish` runs of this item's clone
  (`evidence/archmagi_publishes.txt`): the first checkout, a fresh kept tree, took 35.4 s and wrote 4,897 MB. Each
  later checkout was a reuse: 1.4 s and 46 MB, 3.8 s and 40 MB, 0.7 s and 39 MB.
- SteveDesktop, 2026-11-25 1:04 AM to 1:08 AM PST, two `./publish` runs of the seat clone `~/rm/bench`
  (`evidence/stevedesktop_publish_fresh.txt`, `evidence/stevedesktop_publish_reuse.txt`, made by
  `evidence/kept_measure.py`): the fresh kept tree took 127.0 s and wrote 4,898 MB; the reuse took 1.0 s and wrote
  53 MB. `/proc/pressure/io` read `full avg10` 72 and 58 at the two starts, from the other runs on that disk, so the
  pressure during the 1 s reuse cannot be told apart from theirs. The publish's wall fell from 205 s to 42 s.
- Bytes written are the publish process's `/proc/self/io` `write_bytes` across the checkout (reaped git children
  included); `full_head_tree` prints them on every use.
