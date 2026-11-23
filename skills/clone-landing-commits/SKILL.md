---
name: clone-landing-commits
description: How to get a commit from a RimMandrake seat clone (/home/mandrake/rm/bench) onto origin/main and keep the clone level afterwards — ./publish, land.sh, ./sync (seat_sync.py) — and how to recover a clone that reads "ahead N, behind M", is full of duplicates, or refuses to pull. Use before ANY commit or push in this repo, whenever `git pull --rebase` refuses ("unstaged changes"), a push is rejected non-fast-forward, a landing printed PUBLISHED but the clone still looks behind, selftests go red on a clone that may be stale (ledger_lint NOT_APPEND, a "lost" bridge tool), a hook refused a git command, someone suggests stash / --autostash / reset --hard / a scratch clone to get unstuck, or you are briefing a helper that will commit. Also use when asked how landing, publishing or syncing works here.
---

# Landing commits from a seat clone

A seat clone has one owning window. But the helpers of that window share the tree and the index. Review-sheet
servers also keep a few files dirty at all times. So the tools below never need a clean tree, never stash, and never use `--hard`.

Proof of publication is `git merge-base --is-ancestor <sha> origin/main` — nothing else.

## The one landing path

```
./publish -m "subject" path/one path/two                 # commit those paths + replay onto origin/main + push
src/RimMandrake/Utils/land.sh <sha> <path>...            # land one commit you already made (paths must cover it)
src/RimMandrake/Utils/land.sh -m "subject" <path>...     # land the paths' working-tree bytes, no local commit needed
```

- All three commands print `PUBLISHED <sha>`. Pass that sha to `rimflow close --sha`.
- All three commands retry when origin moves during the push.
- `./publish` is the default. The usual refusals are:
  - A real conflict. The refusal names the path. Your commit stays on HEAD.
  - A red tree check or pipeline check. The refusal names the check. `./publish` takes the commit of this run off HEAD
    and leaves your files as they were. (If HEAD moved during the checks, the commit stays, and the refusal says so.)
    Fix the fault, then publish the paths again
    (`design/RimMandrake/GIT_WORKFLOW.md` §`./publish`).
- If you hold an uncommitted edit to a file that origin changed, one of these happens:
  - If the edit merges cleanly, `./publish` carries the edit across and lands your commit.
  - If the edit really overlaps origin's change, `./publish` still pushes your commit. It leaves the clone's branch in
    place, leaves your edit alone, and prints `LANDED, CLONE NOT MOVED: <why>`.
  - If the edit really overlaps and the landing must rebuild a DLL, `./publish` refuses. The refusal names the path.
    Your commit stays on HEAD.
- Use `land.sh` when you must not move HEAD, or when you must publish a subset. After the push, `land.sh` realigns the
  clone itself.
- `land.sh` is `src/RimMandrake/Utils/land.sh`. `land.sh` is not on PATH. The old copy `/home/mandrake/.seat-tmp/land.sh` is
  absent (measured 2026-11-23).
- `LAND_REPO` defaults to the clone that you are in.
- For a brand-new file, run `git add -- <file>` first (explicit path). Then publish the file.
- Keep file writes and git in SEPARATE Bash calls. A hook refusal cancels the whole call, writes included.
- A commit message is a subject plus at most 2-3 lines. End the message with the session's attribution lines.

## Sync: making the clone level again

`./sync` (`src/RimMandrake/Utils/seat_sync.py`) fetches. Then it runs `git reset --keep origin/main`, only when the
reset loses nothing:

- Each local commit is already upstream: patch-equivalent, or content-equivalent (upstream has the same bytes and mode
  at each path).
- No dirty file that upstream also changed holds bytes other than upstream's, unless the edit merges cleanly with
  upstream.

Otherwise `./sync` prints `REFUSED: <why>` and changes nothing. `./sync --dry-run` shows the plan.

## Recovery

| you see | do |
|---|---|
| `ahead N, behind M` after landings | Run `./sync`. The N commits are duplicates of landed commits. `./sync` keeps them on a `backup/<seat>-pre-sync-*` branch. |
| `REFUSED: local commit X is NOT on origin/main` | X is real unpublished work. Run `src/RimMandrake/Utils/land.sh X <its paths>`, then `./sync`. If X is a peer's commit, leave X and tell the peer. |
| `REFUSED: N dirty file(s) really overlap upstream's change` (the old text was `REFUSED: dirty file(s) ... hold other bytes`) | That edit collides with upstream. Publish the edit, or copy it aside yourself. Then run `./sync`. |
| `pull --rebase` refuses, or someone tells you to stash | Do not stash. Use `./publish` or `./sync`. |
| red selftest on a clone you have not synced | Run `./sync` and run the selftest again before you fix anything. |
| `.git/index.lock` exists | A helper's git call holds the lock for a second. Wait and retry. Never delete a fresh lock. |

Never use any of these:

- `git stash`, `--autostash`, `reset --hard`, `push --force`, or worktrees;
- `checkout -- <path>` on files that you did not write.

Make a scratch clone only with `scratch_clone.py`:

- The clone is sparse by default: ~200 MB of tooling directories.
- Name the directories that the task needs with `--sparse <dir>...`.
- Use `--checkout` (the whole tree, ~4 GB) only for repo-wide work.
- Before you delete a scratch clone, check for unpushed commits AND untracked files.

More traps for this section: [references/traps.md](references/traps.md) § Recovery.

## Traps

The full list is the section **Traps** in `design/RimMandrake/GIT_WORKFLOW.md`. Read that section before you improvise
any git that you have not done here before. The section covers these traps, among others:

- a silenced `git add`;
- a pathspec commit that takes the worktree;
- untracked paths;
- `-F -` after `--`;
- the zsh `$N:refs` modifier;
- refusals of a compound command;
- the pre-push lint on a stale HEAD.

More traps for this section: [references/traps.md](references/traps.md) § Traps.
