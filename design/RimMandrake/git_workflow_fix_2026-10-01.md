# Git workflow fix — 2026-10-01

Owner: *"design the correct response to this worktree issue … This is miserably slow and
tangled right now."*

## 1. Problem (measured 2026-10-01)

- The shared checkout `/mnt/d/Luke/dev/RimMandrake` was **303 commits behind** origin/main
  with 10 local commits, only **2** of them not already upstream by patch (cherry-picks
  re-landed under other shas). ~2,250 untracked files and ~295 daemon deletions mean
  `pull --rebase` refuses and `reset --keep` refuses on one untracked collision, so
  `shared_sync.py` could neither publish (it refuses interleaved upstream/local commits)
  nor catch up.
- **132 registered worktrees, 124 under `.claude/worktrees/` on drvfs.** Each is a full
  28,469-file checkout. Manual worktrees on `/tmp` (18 G tmpfs) filled it to 100 %.
- Worktrees were the tool for *publishing safely*, and publishing is what kept failing:
  rebase conflicts on ledger shards resolved by hand with plumbing, push races between
  4 windows + agents, and `rimflow close` defaulting to a local HEAD sha that never
  reached origin.

The root cause: **every route to origin went through a checkout** (the shared tree's
index, or a 4 GB worktree), and a checkout is the expensive, contended, stateful thing.
A commit on origin needs none of it — only blobs, a tree and a parent.

## 2. Decision

**Publish by plumbing, with no checkout at all.** One tool,
`src/RimMandrake/Utils/publish.py` (wrapper `./publish`):

1. `git fetch` origin/main. Build the commit in a **private temporary index on ext4**
   (`GIT_INDEX_FILE`, `read-tree origin/main`), touching only the named paths:
   `hash-object -w` the file, `update-index --index-info`, `write-tree`, `commit-tree
   -p origin/main`. Nothing in any working tree or the shared index moves. Cost is
   O(named paths) plus one read-tree.
2. **Per-path 3-way, never a blind overwrite.** For each path: base = the path at
   `merge-base(HEAD, origin/main)`, ours = the file on disk, theirs = origin/main. If
   upstream did not move the path, ours wins; if it did, `git merge-file` combines them;
   a real conflict refuses and pushes nothing.
3. **Ledger shards union automatically.** `infrastructure/state/ledger/events/*.jsonl` is
   append-only, so the result is upstream's lines in order plus our lines upstream lacks.
   No hand plumbing.
4. **Push race = rebuild on the new tip and retry** (fetch, redo steps 1-3, push; up to 8
   times; never `--force`). Then `merge-base --is-ancestor <sha> origin/main` proves it.
5. It prints `PUBLISHED <full sha>` and the exact `rimflow close --sha` to run — the
   published sha, never local HEAD.
6. `--commit <sha>…` publishes existing local commits the same way (ours = commit, base =
   its parent), skipping any already upstream by patch (`git cherry`), so interleaved
   cherry-picks stop mattering. `--sync` = publish every local-only commit, then catch up.
7. **Catch-up** (`--catchup`) moves the shared tree to origin/main per path: for each
   path upstream changed, hash the disk copy; untouched → write upstream's bytes;
   already equal → nothing; locally edited → 3-way merge into the file if clean; else
   **refuse with nothing moved** and name the files. Order is files → index entries →
   `update-ref` CAS against the old HEAD, so a peer commit mid-run makes it stop rather
   than drop a commit (the `shared_sync.py` race). Untracked files are never read, moved
   or deleted, except an untracked file colliding with an upstream add, which is a
   reported conflict unless byte-identical.
8. **Janitor** (`--worktrees [--apply]`): removes worktrees that are clean and whose
   commits are all upstream (by patch); never `--force`. New manual worktrees, when one
   is genuinely needed (a build, a merge), go under `/home/mandrake/wt` (ext4), never
   `/tmp`.

## 3. Alternatives ruled out

- **Keep worktrees as the publish route, just shallower/sparse.** A sparse worktree still
  needs a checkout, an index, a branch, a rebase and cleanup; it fixes disk size but not
  the rebase conflicts, the push race, the stale-worktree pile or the wrong sha.
  Plumbing removes the checkout entirely.
- **Fix `shared_sync.py` in place.** `git replay` replays commits as units; the
  interleaving refusal and the `reset --keep` untracked-file refusal are inherent to
  moving whole commits and a whole tree. Per-path is what a never-clean tree needs.
  `shared_sync.py` now delegates to `publish.py --sync`.
- **Merge/rebase in the shared tree with autostash.** Forbidden for cause (215 files
  lost 2026-09-25) and the hooks stay as they are.
- **Bigger `/tmp`, or more janitoring alone.** Treats the symptom; agents still need a
  checkout to publish.
- **Server-side (PR/merge queue).** Correct at team scale, but adds latency and a GitHub
  dependency to every ledger write; one append-only union rule handles the conflicts
  that actually occur.

Residual limits: a path edited both locally and upstream in overlapping lines refuses —
the right outcome. Worktrees remain valid for *building* (a DLL rebuild after a merge);
they are no longer the way to *publish*. `isolation: "worktree"` agent checkouts are
placed by the harness under `.claude/worktrees/` and cannot be relocated by this tool;
the janitor keeps their count down.

## 4. What shipped

Shipped and selftested (`src/RimMandrake/Utils/selftest_publish.py`, 9/9 against a throwaway
bare repo + clones under `~/.cache/publish-selftest`; auto-discovered by `run_selftests.py`):

- `src/RimMandrake/Utils/publish.py` + wrapper `./publish`: path publish (3-way, ledger union,
  push-race rebuild, `PUBLISHED <sha>` + the `rimflow close --sha` line), `--commit`,
  `--sync`, `--catchup [--dry-run]`, `--worktrees [--apply]`.
- Tests cover: other dirty/untracked files and the shared index untouched; published sha ≠
  local HEAD; push race rebuilt on the peer's tip; shard union order; clean 3-way merge and a
  refused overlap that pushes nothing; deletion; interleaved cherry-picked local commits (only
  the genuinely local one is published, then catch-up lands HEAD on origin); untracked-file
  collision refused then accepted when identical; catch-up keeping an uncommitted edit and
  untracked files, and refusing an overlapping edit with HEAD unmoved; janitor removing only
  the clean worktree.
- `shared_sync.py` is now a wrapper for `publish --sync`. CLAUDE.md Git section rewritten to
  point at `./publish`; the stale `shared_sync.py` race paragraph and the hand-union ledger
  procedure are removed.
- Live: `./publish --catchup --dry-run` on the shared tree recognised 9 of its 10 local commits
  as already upstream (including one `git cherry` misses, by content) and refused only on
  `e55ff18da` (northstar's, unpublished), so it moved nothing. This doc and the tool were
  published with `./publish` itself.

Remaining:

- NEXT: whoever owns `e55ff18da` runs `./publish --commit e55ff18da`, then anyone runs
  `./publish --catchup` to bring the shared tree from ~303 behind to origin/main.
- NEXT: run `./publish --worktrees` (dry run) once the background prune finishes, then
  `--apply`. The janitor is untested on the full 124-worktree set: the dry run over drvfs took
  >10 min, so it may need a time cap or a per-worktree timeout.
- NEXT: update `infrastructure/agents/CHARTER.md` § Git: replace "brief it to finish with
  `git fetch && git rebase origin/main && git push`" with "finish with `./publish -m … <paths>`".
- NEXT: the curated skills `parallel-agent-worktrees` and `git-efficiency` get the same pointer.
  The LESSONS_INBOX line for it is appended in the shared tree but NOT published: the file was
  also changed upstream in overlapping lines and `./publish` correctly refused. Publish it
  once the shared tree has caught up.
- NEXT: a line-union rule for LESSONS_INBOX.md was ruled out: curation deletes lines upstream,
  and a union would bring them back. Only the never-trimmed ledger shards are unioned.
- NEXT: catch-up's compare-and-swap failure path (peer commits mid-run) is reasoned about,
  not selftested; add a test that moves HEAD between the plan and `update-ref`.

## 5. The command agents use

```
./publish -m "subject line" path/one path/two          # shared tree or any worktree
./publish --commit <sha>                               # an existing local commit
./publish --sync                                       # all local-only commits, then catch up
./publish --catchup [--dry-run]                        # move the shared tree, keep all edits
./publish --worktrees [--apply]                        # janitor
```
Then `rimflow close <ID> --sha <the PUBLISHED sha>`.
