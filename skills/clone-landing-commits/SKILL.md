---
name: clone-landing-commits
description: How to get a commit from a RimMandrake seat clone (/home/mandrake/rm/bench or /home/mandrake/rm/foundry) onto origin/main and keep the clone level afterwards — ./publish, land.sh, ./sync (seat_sync.py) — and how to recover a clone that reads "ahead N, behind M", is full of duplicates, or refuses to pull. Use before ANY commit or push in this repo, whenever `git pull --rebase` refuses ("unstaged changes"), a push is rejected non-fast-forward, a landing printed PUBLISHED but the clone still looks behind, selftests go red on a clone that may be stale (ledger_lint NOT_APPEND, a "lost" bridge tool), a hook refused a git command, someone suggests stash / --autostash / reset --hard / a scratch clone to get unstuck, or you are briefing a helper that will commit. Also use when asked how landing, publishing or syncing works here.
---

# Landing commits from a seat clone

A seat clone has one owning window, but its helpers share the tree and the index, and review-sheet servers keep a
few files dirty at all times. So the tools below never need a clean tree, never stash, and never `--hard`.
Proof of publication is `git merge-base --is-ancestor <sha> origin/main` — nothing else.

## The one landing path

```
./publish -m "subject" path/one path/two     # commit those paths + replay onto origin/main + push
land.sh <sha> <path>...                      # land one commit you already made (paths must cover it)
land.sh -m "subject" <path>...               # land the paths' working-tree bytes, no local commit needed
```

- All three print `PUBLISHED <sha>` (pass it to `rimflow close --sha`) and retry when origin moves mid-push.
- `./publish` is the default. It refuses, naming the path and leaving your commit on HEAD, only on a real conflict or
  when you hold an uncommitted edit to a file origin changed.
- `land.sh` is for when you must not move HEAD or must publish a subset; it then realigns the clone itself.
  Installed as `/home/mandrake/.seat-tmp/land.sh`; `LAND_REPO` defaults to the clone you are in.
- Brand-new file: `git add -- <file>` first (explicit path), then publish it. Keep file writes and git in SEPARATE
  Bash calls — a hook refusal cancels the whole call, writes included.
- Commit messages: subject plus at most 2-3 lines; end with the session's attribution lines.

## Sync: making the clone level again

`./sync` (`src/RimMandrake/Utils/seat_sync.py`) fetches and runs `git reset --keep origin/main` only when that loses
nothing: every local commit is already upstream (patch- or content-equivalent) and no dirty file holds bytes other than
upstream's. Otherwise it prints `REFUSED: <why>` and changes nothing. `./sync --dry-run` shows the plan.

## Recovery

| you see | do |
|---|---|
| `ahead N, behind M` after landings | `./sync` — the N are duplicates of landed commits; they go to a `backup/<seat>-pre-sync-*` branch |
| `REFUSED: local commit X is NOT on origin/main` | X is real unpublished work: `land.sh X <its paths>`, then `./sync`. If X is a peer's, leave it and tell them |
| `REFUSED: dirty file(s) ... hold other bytes` | that edit collides with upstream: publish it, or copy it aside yourself, then `./sync` |
| `pull --rebase` refuses / you are told to stash | don't; use `./publish` or `./sync` |
| red selftest on a clone you have not synced | `./sync` and re-run before fixing anything |
| `.git/index.lock` exists | a helper's git call holds it for a second: wait and retry, never delete a fresh lock |

Never `git stash`, `--autostash`, `reset --hard`, `checkout -- <path>` on files you did not write, `push --force`, or
worktrees. A scratch clone costs 7-14 GB: only via `scratch_clone.py`, and before deleting one check unpushed commits
AND untracked files.

## Traps

The full list — silenced `git add`, pathspec commits taking the worktree, untracked paths, `-F -` after `--`, the zsh
`$N:refs` modifier, compound-command refusals, pre-push lint on a stale HEAD — is
the **Traps** table in `design/RimMandrake/GIT_WORKFLOW.md`. Read it before improvising any git you have not done here
before.
