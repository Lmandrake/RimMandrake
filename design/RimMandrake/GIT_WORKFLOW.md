# Git workflow — the operating doc (2026-10-02)

This file states what IS. The reasons and the measurements are in two places:
- the plan, `git_workflow_plan_2026-10-01.md`;
- the dated `git_migration_*_2026-10-02.md` records, which say what was built.

## Where work happens

| place | what it is |
|---|---|
| `/home/mandrake/rm/bench` | The seat clone: ext4, plain git, **one writer** (the seat's own window). The seat launches from its clone. (FOUNDRY is retired, and its clone is deleted.) |
| `D:\Luke\dev\RimMandrake` (`/mnt/d/Luke/dev/RimMandrake`) | The **read-only mirror** of origin/main. `rm-mirror.timer` refreshes it every 5 min (`./mirror sync`). The mirror has no `.git`. Never write the mirror. Windows tools read it: the game deploy, Explorer, python.exe. `MIRROR_HEAD` names its commit. `MIRROR_STALE` appears if a refresh failed. |
| `/home/mandrake/rm/mirror.git` | The mirror's bare, fetch-only repo. |
| `D:\ClaudeWork\rimmandrake\artpipe\` | The artpipe queue and state (not in git): `pending/ active/ done/ failed/ _artsrc/ registry.jsonl` |
| `D:\ClaudeWork\rimmandrake\build\`, `D:\ClaudeWork\rimmandrake\scratch\codex\` | Build staging and codex.exe staging (scratch on the Windows drive). |
| `/home/mandrake/rm/store.git` | The shared object store: bare, fetched from `mirror.git`, never pruned. Throwaway clones borrow objects from it, never from a seat clone. |
| `/home/mandrake/rm/scratch/<SEAT>/` | Throwaway ext4 clones. Make them only with `python3 src/RimMandrake/Utils/scratch_clone.py clone "<purpose>" [--sparse <dirs the task needs>]`. Never make them in `/tmp`: `/tmp` is tmpfs. See "Scratch clones" below for the default tree and `--checkout`. |

A session in the `D:\` mirror cannot commit:
- `./publish` refuses under `/mnt/`;
- the `block_shared_tree_merge.py` hook refuses whole-tree git there.

## Landing work (seat)

```
./publish -m "subject" path/one path/two        # commit those paths, replay onto origin/main, push; prints PUBLISHED <sha>
land.sh <sha> <path>...                         # land one commit already made (any clone; plumbing)
land.sh -m "subject" <path>...                  # land working-tree bytes of the paths without a local commit
./sync                                          # realign this clone's main with origin/main (seat_sync.py)
```

### `./publish` (`src/RimMandrake/Utils/publish.py`)

- `./publish` commits by pathspec.
- Then `./publish` re-creates each local commit that is not yet upstream on top of origin/main. The replay uses
  plumbing (`merge-tree` + `commit-tree`). `./publish` then moves main there with `git reset --keep`.
- Then it pushes. When origin moved, it retries up to 8 times.
- `./publish` **never stashes**, so it works in a dirty clone. It refuses only in two cases. In each case it names the
  path, and your commit stays intact on HEAD:
  - a real conflict;
  - you hold an uncommitted edit to a file that origin changed.

**The tree checks before the push.**
- Before it pushes, `./publish` runs the fast whole-tree checks listed in `src/RimMandrake/Utils/publish_tree_checks.json`.
  The checks run in parallel (about 13 s, measured 2026-11-12).
- On a red check, `./publish` refuses. The refusal names the check, its FAIL line and the fix (owner by card
  2026-11-12; `validation_map_and_rules.md` rule 10).
- A publish of only ledger or lesson files skips the checks. A check that times out gives a warning.
- In a sparse clone (the default of `scratch_clone.py`), the checks run on a throwaway full checkout of HEAD. That
  checkout is a `git clone --shared` in the clone's git dir, and costs about 20 s more. So a sparse clone publishes with
  no bypass and no un-sparsing.

**The two skip variables.**
- `RM_PUBLISH_SKIP_TREE_CHECKS="<why>"` bypasses the tree checks once, out loud. A sparse clone is not a reason.
- Each skip variable (this one or `RM_PUBLISH_SKIP_PIPELINE_CHECKS`) writes a `Door-skipped: <VAR>: <why>` trailer on
  the landed commit. `git log --format='%(trailers:key=Door-skipped)'` finds those trailers.
- `./publish` refuses a skip on a landing that has no commit of its own.

### `land.sh` (`src/RimMandrake/Utils/land.sh`)

- `land.sh` publishes ONE commit, or explicit paths, by plumbing. It retries a lost push race. Then it runs
  `./sync --no-fetch` itself.
- `LAND_REPO` defaults to the clone that the cwd is in.
- The stdout of `land.sh` is exactly `PUBLISHED <sha>`. Pass that sha to `rimflow close --sha`.
- The old one-line wrapper `/home/mandrake/.seat-tmp/land.sh` is absent (measured 2026-11-23). Run the repo copy.

### `./sync`

- `./sync` moves main to origin/main with `git reset --keep` only when both conditions are true:
  - each local commit is already upstream (git cherry marks it `-`, or upstream has the same bytes per path);
  - no dirty file holds bytes other than upstream's.
- Otherwise `./sync` prints `REFUSED: <why>` and changes nothing.
- `./sync` saves local commits to `backup/<seat>-pre-sync-<stamp>-<sha>`.
- Never stash. Never use `--hard`.

### Rules for every commit

- Put the pathspec on the commit (`git commit <paths>`). Never use `git add -A`/`.`/`-a`. A hook enforces this.
- Never use `--force`.
- Never commit a file over ~50 MB.
- The proof of publication is `git merge-base --is-ancestor <sha> origin/main`.
  - An empty `git log origin/main..HEAD` is not proof.
  - The exit code is not proof: `./publish` can exit 120 with no output and still have pushed.
- Origin is SSH (`git@github.com:Lmandrake/RimMandrake.git`).
- Committed and pushed is the only durable state. Commit at each finished unit and push at once.
- Do not `git pull --rebase` in a seat clone. A pull with rebase refuses on ANY dirty file, and a seat clone is always a
  little dirty.

## Subagents

- 🔴 **Worktrees are OFF** (owner, 2026-10-02, by card).
  - Never use `isolation: "worktree"`. Never run `git worktree add`. `.claude/hooks/block_worktrees.py` refuses both.
  - The WorktreeCreate hook refuses `claude --worktree`.
  - Why: worktree agents duplicated whole checkouts and stranded work on side branches.
- A writing helper edits in its window's clone. The window commits explicit paths with `./publish`.
- If the paths of two writing helpers could overlap, run the helpers one at a time.
- Tell each helper in its brief: `reset --hard`, `checkout --` and `stash` are forbidden on paths that the helper did
  not create. The helper reports a conflict and never clears it.
- The drained worktree work is under `archive/*` tags on origin. `git checkout <tag> -- <path>` restores a file. The
  census is `design/RimMandrake/git_migration_drain_2026-10-02.md`.
- A helper must never rewrite commits that it did not author.
  - A helper reports a guard refusal back, and the parent lands the work. An example of a guard refusal: the art push
    guard refuses the deletion of PNGs that the owner kept.
  - Evidence: one rm-fixer rewrote four unpublished local commits in the shared clone to drop the deletions. One of those
    commits was a peer's. The trees matched and nothing was lost, but never again.

## Generated and per-writer state (nothing shared to conflict on)

| state | where |
|---|---|
| ledger | `infrastructure/state/ledger/events/<SEAT>.jsonl`, append-only, `merge=union`. `events.jsonl` is frozen. `ledger_lint.py` (and the pre-push hook `block_ledger_lint.py`) refuses an edited or reordered line. `model.read()` orders events by content, so the file order does not matter. Never resolve a shard with `checkout --ours/--theirs`. For events stranded in a seat clone that cannot push, run `ledger_sync.py --seat <SEAT>` (a dry run). `--apply` appends the missing lines and pushes from a throwaway clone under `/home/mandrake/rm/scratch/<SEAT>/`; the run deletes that clone when it ends. `--clone <dir>` keeps a reusable clone. |
| queue views | Rendered on read, untracked: `python3 src/RimMandrake/rimflow/cli.py queue <SEAT>`. `queue/HUMAN.md` is the owner's hand-written inbox, and it stays tracked. |
| lessons | One file each in `infrastructure/state/lessons/` (`python3 src/RimMandrake/Utils/lessons.py add "…"`). `lessons.py render` makes the untracked `LESSONS_INBOX.md` view. |
| code review status | Append-only records `infrastructure/state/code_review/<SEAT>.jsonl` (`merge=union`). Only `code_review_status.py` writes them. Each review wave is one file under `code_review/waves/`. |
| health heartbeat | `Transient/codebase_health*`, `codebase_health_last.json` and `dashboards/hub/data/*.json` are untracked. `rm-codebase-health.timer` regenerates them in the bench clone (`/home/mandrake/rm/bench`). |
| `Transient/` | **Untracked since 2026-10-18** (owner, by card). `Transient/.gitignore` ignores everything except three things: itself, every `*.decisions.json`, and the pins that `src/RimMandrake/Utils/transient_pin.py` manages (`add`/`rm`/`cited --add`/`untrack`). The files stay on disk: `./sync`, `./publish` and `land.sh` (via `seat_sync.reset_keep`) never delete a file only because upstream stopped tracking it. Unpinned output is only in the clone that wrote it — not on `D:\`, GitHub or the other seat. |
| `conversations/` | The handoff commits them: `handoff.py` lands every new or changed record via `conversations_land.py` (owner 2026-10-18, *"the next handoff plays catchup"*). A handoff through `~/dev/Lodestar/bin/handoff.py` runs `python3 src/RimMandrake/Utils/conversations_land.py --apply` right after `conversations.py`. |
| Saves folder | Keep only the canonical save(s) and the saves awaiting review (`infrastructure/state/saves_awaiting_review.txt`). A backup lives until the operation that it guards is verified. `python3 src/RimMandrake/Utils/saves_prune.py` reports (a dry run). `--apply` deletes only uncited debug saves > 72 h old and backups > 24 h old — never a `CANONICAL_*` save. |

**Pre-push guards run as a git-native hook.**
- The hook is `infrastructure/githooks/pre-push`: the DLL/source-stamp check and the ledger lint. The Claude PreToolUse
  hooks also run these guards.
- Git finds the hook through `core.hooksPath`, which is **set per clone**: `git config core.hooksPath
  infrastructure/githooks`. `~/rm/bench` has this setting. A fresh clone must set it.
- Selftest: `python3 infrastructure/githooks/selftest_pre_push.py`.

## Builds, DLLs, tools that need Windows

**C# builds.**
- `python3 src/RimMandrake/Utils/winbuild.py <Mod|csproj>` stages the sources on `D:\ClaudeWork\rimmandrake\build\` and
  runs Windows dotnet. Then it copies the DLL **and its `.srchash` back as a pair**.
- The JawaBench companion builds through `bridgetools/build.py`, which stages the same way.

**A committed DLL.**
- Push a committed DLL with its `.srchash` (`dll_source_stamp.py`; the guard `block_dll_source_mismatch.py` runs on
  push).
- **`./publish` lands DLLs; no agent resolves a DLL conflict or rebuilds one by hand to land.**
- A replay conflict on ONLY `.dll`/`.dll.srchash` pairs: `./publish` takes origin's side. Then `./publish` rebuilds each
  such DLL from the source committed at the new HEAD, commits the pair and pushes.
  - The rebuild runs in a throwaway src-only `git clone --shared` under `/home/mandrake/rm/scratch/<SEAT>/`, never in
    the worktree. So a peer's uncommitted C# cannot leak in.
- A `DLL_SOURCE_STAMP_GUARD_1` pre-push refusal gets the same rebuild and one retry.
- `./publish` still refuses in two cases, and names the paths:
  - a conflict on any other path;
  - a peer's uncommitted edit to that DLL pair.
- Selftest: `src/RimMandrake/Utils/selftest_publish.py`.

**Codex.**
- On Archmagi/WSL2, Codex defaults to `~/.local/bin/codex` with `~/.codex`.
- `RM_CODEX_SIDE=wsl|win` selects the runtime. `gpt_consult.py` and `agent_runner.py` also accept `--codex wsl|win`.
- Linux calls use Linux paths, and scratch under `~/.local/state/rimmandrake/scratch/codex`. `CODEX_SCRATCH` overrides
  that scratch path.
- Other hosts keep their previous default.
- Both installs share the account quota. The meter reads both histories.
- On the Windows side, `codex.exe` cannot run from an ext4 cwd. So `codex_image.py` and `gpt_consult.py` stage the call
  in `D:\ClaudeWork\rimmandrake\scratch\codex\<job>\` and copy the results back.

**artpipe.**
- The daemon (`rm-artpiped.service`) runs from `/home/mandrake/rm/roles/artpiped` with
  `ARTPIPE_STATE_DIR=/mnt/d/ClaudeWork/rimmandrake/artpipe`.
- To copy art into a clone for a commit, run `artpipe_state.py collect <job> --to src/…`.
- `artpipe_state.py find <term>` searches finished jobs.

**Other Windows-facing work.**
- From WSL, run anything bridge-facing or game-facing under `python.exe`, against the **mirror** path.
- Selftests that run Windows `dotnet.exe` fail from an ext4 clone with MSB3101/MSB3030/MSB1009. Those failures are not
  regressions. `src/RimMandrake/Utils/selftest_winstage.py` stages those selftests on the Windows drive.

## History and recovery

- The worktrees, branches and stashes of the old shared tree were drained into two places:
  - `archive/*` tags on origin (reachable, not accepted into main);
  - `refs/rescue/*`.

  See `git_migration_drain_2026-10-02.md`. `git tag -l 'archive/*'` lists the tags.
- Never merge in a tree that others write. No such tree is left: each clone has one writer.
- A history rewrite of origin/main strands every remote clone that pulls `--ff-only` ('ahead N, behind N').
  - Evidence: SteveDesktop's `~/rm/runner` and testq paused REFUSED/SYNC after the work-history excise.
  - Re-point the remote clones in the same change.
  - The reset-hard hook matches ssh command text too.
  - `git switch --detach origin/main; git branch -f main origin/main; git switch main` moves a clean clone. That
    sequence still refuses over local edits.

## Scratch clones

**The default tree.** `scratch_clone.py` makes a cone-sparse tree by default: a sparse checkout that holds the
root files, `.claude`, `infrastructure`, `skills`, `src/RimMandrake/Utils` and `src/RimMandrake/rimflow`. That tree is
~200 MB, not the whole ~4 GB. Use `--checkout` only for repo-wide work, and say why in the purpose. Trial with
telemetry: `design/RimMandrake/objstore_trial_2026-10-08.md`.

**Cost.**
- Scratch clones cost ~7-14 GB each. Evidence: 18 strays filled 276 GB (2026-10-11).
- Prefer `land.sh`/`./publish`. If you must clone, use `scratch_clone.py`, `--reference <seat clone>` or
  `--filter=blob:none`.

**Reaper** (owner by card 2026-10-18: delete after 24 h if fully pushed).
- Command: `python3 src/RimMandrake/Utils/scratch_reap.py` (a dry run; `--apply` deletes).
- The reaper judges three kinds of thing:
  - every clone under `/home/mandrake/rm/scratch/**`;
  - every clone under `~/.seat-tmp/**`;
  - every session dir `~/.seat-tmp/<SEAT>/claude-*/<project>/<uuid>/`.
- The reaper deletes a thing only when all of these are true:
  - the thing is > 24 h old;
  - it has no commit that is off every remote (the reaper re-checks stale refs against `mirror.git`);
  - it has no changed or untracked file and no stash;
  - no other clone borrows from it, and no process runs in it;
  - no ledger event, item or handoff names it.
- The reaper REFUSES anything else, and writes it to `~/.local/state/rm-scratch-reap/alarms.log`.
- `rm-scratch-reap.timer` runs the reaper hourly. The unit now runs it with `--apply` (measured 2026-11-23).
- To delete a clone by hand, do the same checks first. Evidence: a scratchpad held the only commits of
  CRACKEDLANDS_FULL_RENAME_1 (2026-10-18).

**Repo weight**, measured 2026-10-11: the bench `.git` holds 101,797 loose objects (4.4 GiB) + 155 packs (5.6 GiB).
At that measurement, nobody had run `git gc` there. To run `git gc` there is the owner's call. Run it when no window is
mid-git.

**Check `df -h /` before you spawn clone-heavy agents, and when a git write fails with `Out of diskspace`.**
- Seat scratch is 7-23 GB per item: `~/.seat-tmp/<SEAT>/*_export`, clean clones, `ledger_sync` repos, and clones under
  `/home/mandrake/rm/scratch`. Together they filled the root disk to 1.5 MB free.
- Delete finished ones at once, after you see 0 unpushed commits.
- Make new ones as shallow clones or with `--filter=blob:none`.

**A seat that fans out helpers must take pool clones (`scratch_clone.py`), or delete its own clones once landed.**
- Evidence: 17 work-package clones under `~/rm/scratch/<SEAT>` were made outside the pool. They stayed after their work
  landed. They read YOUNG to `scratch_reap` until the TTL ended (24 h: `scratch_reap.py`). They fired a
  SCRATCH_OUTSIDE_CAP alarm for hours.
- A dirty ledger shard in such a clone is usually a rewritten copy of lines already on origin/main. Check by set
  difference.

**`scratch_reap` sanity END lines must count only what the run LEFT (rows not DELETED/YOUNG), never a whole-population
count.**
- Evidence: `session_dirs` and `rm_scratch_clones` each alarmed on live young work.
- The whole counts stay as readings. `ops_watch` OP2 reads `rm_scratch_clones`. (OP2 is the
  `disk.scratch_outside_cap` alarm: `ops_watch.py` names it so, read 2026-11-23.)

**Never clone or write large files under `/tmp`.**
- `/tmp` is an 18G tmpfs that all workers share. `/tmp` is often 99-100% full.
- Its pages count against the seat's 10G `MemoryMax` (`src/RimMandrake/Utils/claude_bounded.sh`). The pages stay
  counted after the writer dies.
- Evidence: a 12G `git clone` into `/tmp` plus 16 parallel selftest workers (0.8-2.1G each) got the seat OOM-killed (23
  processes).
- `git init` there fails 'Out of diskspace'.
- A mutant test can do `cp file /tmp/x.bak; mutate; cp /tmp/x.bak file`. When the first `cp` hits ENOSPC, the test
  TRUNCATES the source, or writes a 64 KiB copy. So:
  - take the backup with `git show HEAD:<path>`, or on ext4 (`~/.seat-tmp/<seat>`), or in `D:\ClaudeWork` scratch;
  - `cmp` the backup before you overwrite;
  - chain the steps with `&&`.
- Seat processes use `TMPDIR=~/.seat-tmp/<SEAT>`. So tests pass, while anything that writes `/tmp` directly fails.
- Selftests also crashed ENOMEM with TMPDIR on `/mnt/d`. With `TMPDIR=~/.seat-tmp/<seat>/x` they ran green.
- A full `/tmp` also shows as python scripts that exit 120 with EMPTY output (the stdout flush hits ENOSPC). That looks
  like a silent tool failure. Run `df /tmp` before you trust a silent exit 120.
- When you are done, delete any `/tmp` scratch copies of a mutation test (once ~10 GB together). Agent scratch never
  belongs in `/tmp`.
- Keep the selftest worker count low (`run_selftests.py --workers`).

**A whole-repo export into tmpfs `/tmp` can be OOM-killed mid-stream by the 6 GiB tool cap.**
- The tracked tree is 3.58 GB. The tar plus the extract is about 7 GB.
- The kill leaves a truncated tree that gives a confident wrong proof. Evidence: a donor-off worker read flyers 5 and
  FAIL offline, where the truth was 24 and PASS.
- Treat `tar: Unexpected EOF` or exit 137 in an export step as no result.
- Measured: `infrastructure/state/facts/oom_kills_2026-11-03.md`.

**A full replay-tree write on `/mnt/d` (drvfs) takes minutes; on ext4 it takes seconds.**
- Evidence: an export of a 7.7 GB / 48k-file tree took ~20 min on drvfs vs 42 s on ext4. `git add` took >600 s vs
  130 s.
- A full-tree checkout of this repo takes ~40 s on ext4, and outlasts 60 s on drvfs.
- Put scratch clones and exported trees on ext4 (e.g. `/home/mandrake/rm/<dir>`), never beside a log on `/mnt/d`.
- A tree export peaks at ~4.4 GB RSS. So two exports at once sit near a 12G slice.

## Traps

Each trap below cost at least one lost or mis-published change. Hooks enforce most of them, or the tools above fix them.
The rest are discipline. Each trap gives what happens, then what to do instead.

### Staging and committing

**`git add a b c 2>/dev/null`**
- What happens: one missing path fails the WHOLE add silently. The commit then runs on an empty or partial index and
  "succeeds".
- Do instead: never silence `git add`. Check `git show --stat HEAD`.

**A deleted path on `git add`**
- What happens: `git add <deleted>` errors and kills the `&&` chain. The push after it says "Everything up-to-date".
- Do instead: put a deleted path on the commit pathspec only.

**A pathspec commit takes the WORKTREE**
- What happens: `git commit <path>` is an implicit `git add` of that path. Git ignores a blob that you staged with
  `update-index`. A peer's unsaved lines in the same file ride along.
- Do instead: check `git diff --stat <path>` first. Build partial commits in a temp index (`GIT_INDEX_FILE`).

**A pathspec commit cannot remove-but-keep**
- What happens: `git rm --cached p` then `git commit p` re-adds `p` from the worktree.
- Do instead: commit through a temp index (`GIT_INDEX_FILE=… git read-tree HEAD; git rm --cached …; write-tree;
  commit-tree`). Then run `git reset -q -- p` in the real index.

**An untracked file cannot be pathspec-committed**
- What happens: `git commit <new file>` → "did not match any file(s) known to git". A `git commit <dir>` silently skips
  new files in that dir.
- Do instead: `git add -- <new file>` first (explicit path), then `git commit <paths>`.

**`-F -` after `--`**
- What happens: `git commit -- p -F -` treats `-F` and `-` as pathspecs.
- Do instead: put options before `--` and paths after.

**A bare `git commit`**
- What happens: the commit takes the WHOLE index, including what a helper staged in the same clone.
- Do instead: always name the paths. A hook enforces this.

**`.git/index.lock` exists**
- What happens: a background helper's read-only `git status` holds the lock for a second. A failed `./publish` then
  committed NONE of its paths.
- Do instead: wait a few seconds and retry. Never delete a lock younger than a minute. Check `git status` after any
  failed publish.

**A compound command is refused whole**
- What happens: a `PreToolUse` hook (blanket stage, DLL stamp, sheet guard) refuses the entire Bash call before the
  shell runs. Any file write chained before the commit never happened either.
- Do instead: keep file writes and git commands in SEPARATE Bash calls. A hook's refusal means that nothing in that call
  ran.

**A zsh refspec modifier**
- What happens: in `git push origin $N:refs/heads/main`, zsh reads `:r` as a modifier and mangles the refspec.
- Do instead: `"${N}:refs/heads/main"`.

**A temp `GIT_INDEX_FILE` commit (`read-tree HEAD; add; write-tree; commit-tree -p HEAD`) in a shared clone**
- What happens: the commit is racy. If a peer commits between `read-tree` and `commit-tree`, the new commit silently
  reverts the peer's files.
- Do instead: read HEAD ONCE. Build the index from that same sha. Run `update-ref refs/heads/main NEW OLD` with that sha
  as the expected old value.

**Two helpers edit the same file at once, and each wants to commit only its own hunks**
- What happens:
  - `git commit <path>` takes the WORKTREE file, so the peer's hunks ride along. Seen with `auditor.md`,
    `dispatcher_schedule.json`, `arena_eventlog.py` and a csproj line.
  - A pathspec-less commit is hook-blocked. A bare `--amend` is refused.
  - `git apply --cached --unidiff-zero` with filtered `-U0` hunks inserts at the NEW-side line numbers of the full diff
    (wrong positions).
  - `code_review_status.py mark-clean` then refuses the file until the peer commits.
  - `./publish` refuses while any peer's build left the mod DLL dirty.
- Do instead: plan it. Agree with the parent who commits the shared file whole, or land your edit first. If you must
  split:
  1. Build the blob: HEAD content, plus your lines inserted after anchor lines. Run `git hash-object -w`.
  2. Commit through a PRIVATE index: `GIT_INDEX_FILE=tmp git read-tree HEAD; git update-index --cacheinfo
     100644,<blob>,<path>; git commit-tree $(git write-tree) -p HEAD; git update-ref refs/heads/main <new> <old>`.
  3. Assert the blob against the worktree.
  4. Run `git diff` to confirm that the peer's hunks are still in the worktree.

  A `git commit -- paths` leaves any OTHER staged path staged (e.g. a peer's csproj line). If a foreign hunk rode
  along, say so in the commit.

**`git rm` stages a deletion into the index; delete with plain `rm`, then a pathspec commit.**
- A directory pathspec sweeps untracked build output (`bin/`, `obj/`). So read `git status` on the directory first.
- Two windows of one seat share a clone and its index. An `index.lock` "File exists" means that a commit runs now. So
  wait, and never delete the lock.

### Landing, syncing and pushing

**`land.sh` duplicates**
- What happens: a landing by plumbing leaves the clone "ahead N, behind M", with patch-equivalent copies. A stale clone
  shows phantom selftest reds (ledger_lint NOT_APPEND, a "lost" bridge tool).
- Do instead: `land.sh` now syncs itself. Otherwise run `./sync`. Re-check a red on a synced clone before you fix it.

**autostash**
- What happens: `pull --rebase --autostash` re-applied peers' dirty files and stranded 53 in `stash@{0}` (2026-10-10).
- Do instead: never stash. `./publish` and `./sync` use `reset --keep`.

**The pre-push ledger lint judges the LOCAL HEAD**
- What happens: the lint refuses a correct plumbing push from a clone behind origin, with NOT_APPEND.
- Do instead: run `./sync` first, then land.

**`git commit && git pull --rebase && git push` in ONE Bash call**
- What happens: the pre-push/PreToolUse ledger hook judges HEAD BEFORE the compound runs. So the hook refuses the call
  with NOT_APPEND, even though the rebase would fix it.
- Do instead: run commit, pull/rebase and push as separate Bash calls. Never stash a peer's dirty files to rebase
  (`./publish` replays without a stash).

**A real merge commit**
- What happens: the blanket-stage hook refuses `git commit --no-edit` mid-merge (no pathspec is possible).
- Do instead: `GIT_EDITOR=true git merge --continue`.

**A fetch OOM-kills the window**
- What happens: the fetch of the 5.5 GiB pack runs inside a 10G-capped seat scope.
- Do instead: `systemd-run --user --scope --quiet -p MemoryMax=20G git fetch origin main`.

**A plumbing-built push (a patch diffed from the wrong parent, `git apply` failing inside a pipe to `tail`)**
- What happens: the push sent an EMPTY commit with a misleading message.
- Do instead: assert that the apply succeeded (`set -o pipefail`). Assert that the resulting tree differs from
  `origin/main` before you push.

**`./publish` refuses ('not mine to overwrite', `reset --keep` refused, exit 2) because of a PEER's uncommitted edit**
- The cause is a peer's uncommitted edit to one of two things:
  - a file that origin changed;
  - the mod DLL pair (the peer's `winbuild.py` output, `+dirty` in the `.srchash`).
- What happens: your commit stays local, and every later publish waits on that peer. The ledger_lint push hook refuses the workaround of a temp index + `commit-tree` + push. That hook lints the stale
  local HEAD.
- Do instead: land WITHOUT a touch to the tree. Two ways:
  - Plumbing: `tree=$(git merge-tree --write-tree --merge-base=C^ origin/main C)`. Run `commit-tree` on that tree onto
    `origin/main`. Run `git push origin <tip>:main`. Local main stays diverged; the next publish's `git cherry` skips
    it.
  - A throwaway clone: `git clone --shared --no-checkout <seat clone> /home/mandrake/rm/scratch/<SEAT>/land`. Set
    `origin` to the real remote, `checkout -B main origin/main`, cherry-pick, push. There HEAD IS origin+1, so the lint
    passes.
- For ledger shard lines: append only the new ones.
- For a peer's dirty DLL pair only:
  1. Back the pair up under `D:\ClaudeWork\rimmandrake\backups\`.
  2. Run `git show HEAD:<path> > <path>` for both files.
  3. Run `./publish`. It rebuilds from the committed source.
  4. Run `winbuild.py <Mod>` again, so the working copy carries the peer's source.
- Tell the report whose edit blocked it.

**`./publish` replay stops on YOUR commit, or refuses a DLL conflict, in a clone dirty with peers' files**
- The DLL case: a helper's commit in the same clone was replayed, and the local HEAD keeps its pre-replay twin.
- What happens: rebase, `--autostash` and stash are all refused or destructive there.
- Do instead, one of two ways:
  - Rebuild the local chain by plumbing: `git merge-tree --merge-base=c^` + `commit-tree`. Give your conflicted file as
    a resolved blob via a temp `GIT_INDEX_FILE`. Re-check that HEAD has not moved. Then `git reset --keep` to the new
    tip.
  - Restore worktree files to origin ONLY for paths in `git diff --name-only <your-commit> origin/main` that are NOT in
    your own commit's diff. (A loop over `HEAD..origin` overwrote the agent's own changes once.) Then run
    `git update-ref refs/heads/main origin/main` and `git reset -q -- <those paths>`, and `./publish` your paths.
- Before `git checkout <your-commit> -- <paths>`, confirm that none of those paths changed on origin.

**`winbuild.py` stages the WORKTREE**
- What happens: in a clone that holds another helper's uncommitted C#, the built DLL bakes that C# in (`+dirty` srchash).
  `DLL_SOURCE_STAMP_GUARD_1` then refuses the push.
- Do instead:
  1. First check whether a peer already pushed your source with a DLL rebuilt over it (`git cherry`; literal-grep a new
     method name in origin's DLL with `MEASURE_ALLOW_SCAN=1`).
  2. Build from a src-only scratch clone at HEAD: `git clone --shared --no-checkout <seat clone> <ext4 dir>; git
     sparse-checkout set src; git checkout HEAD`. The src-only clone takes ~8 s; a full clone onto `D:\ClaudeWork` took 8.5 min.
  3. Run `winbuild.py` there. Copy the `.dll` + `.srchash` back.
  4. If origin moved with another DLL commit, replay your source commits onto `origin/main` there (take origin's DLL)
     and rebuild. Then `git reset --keep` the seat clone to that tip, and run `./publish`.

**`./publish` 'git reset --keep refused' on `infrastructure/state/ledger/events/<SEAT>.jsonl` in a shared worktree**
- What happens: another agent's ledger line sits uncommitted AND is already on origin.
- Do instead: if `git show origin/main:<shard> \| cmp - <shard>` says identical, run `git checkout -- <shard>` and re-run
  `./publish`. `reset --keep` writes origin's copy back, and nothing is lost.

**`./publish` refuses on an untracked file that origin also added (e.g. `conversations/*.md` landed by another seat)**
- What happens: an identical untracked copy blocks the replay.
- Do instead: `cmp` the file against `origin/main`. Move the identical copy aside, and re-run.

**The `git push` of `publish.py` hangs 9+ minutes**
- What happens: the commit may already be on origin.
- Do instead: run `git branch -r --contains <sha>` before you re-publish or wait. Stop only your own push, by PID.

**`./publish -m "..."` with a ledger shard path inside a helper/background process**
- What happens: a background helper can fail `./publish` and `git push` with `Permission denied (publickey)`, while the
  parent's pushes work. The helper's commits stay local.
- Do instead: the parent checks `git status -sb` for `ahead N` after each helper, and publishes itself.

**A helper told 'never pull' is also told to `./publish` in a clone that a running trial loads code from**
- What happens: `./publish` is a tree move (fetch + rebase, reflog `reset: moving to <sha>`). Evidence: 21 HEAD moves
  hit the clone during a trial freeze. The arms' gate, judge and snapshot subprocesses load disk code per call. So the
  verdicts ran newer code than the runner.
- Do instead: the arms run from a read-only pin. While a trial runs from a live clone, no helper publishes there
  (commit local only).

### Identity, handoffs and wakes

**A side or scratch clone commits or cherry-picks with the global identity**
- What happens: the commit carried the owner's personal email on the PUBLIC repo.
- Do instead: in any side clone, run `git config user.email 313496996+Lmandrake@users.noreply.github.com` before you
  commit or cherry-pick.

**The `handoff.py` UNPUSHED gate refuses a fully published tree**
- What happens: the gate compares SHAs, not patches. Publish rebases, so the local SHAs differ from origin's.
- Do instead: prove equivalence with `git log --cherry-mark origin/main...HEAD`, then run `./sync`. Do not reach for
  `--force`.

**`handoff.py --wake` in a stale shared checkout**
- What happens: it prints that checkout's newest handoff, not origin's. So a window can wake on an old handoff.
- Do instead: read `git show origin/main:infrastructure/state/handoffs/<newest>`.

**A wake after a logout or crash**
- What happens:
  - the predecessor's tail is unpushed: local commits already on origin under other hashes, uncommitted ledger and
    art-ledger files, sheet webps;
  - a crash can leave empty loose git objects and a stale `.git/index.lock`. Those pass a commit but fail `git fsck` and
    the DLL stamp guard.
- Do instead: first run `git status -sb` against a fresh fetch, and `git fsck --no-dangling`. Fix an empty object: delete
  it, then run `git hash-object -w` on the identical working file. Never trust the handoff's "everything pushed".

**A judge reads `OWNER.jsonl` from the working tree of its own clone**
- What happens: the file is only as fresh as that clone's last pull. Evidence: `~/rm/dispatch` was behind origin, and
  refused a Designer run WAITING_OWNER while his answer was already published.
- Do instead: read the owner's word as the working tree UNION origin/main (`concept_tree.owner_lines`), after a
  `git fetch` (`role_launch.judge_sync`). Never pull a clone under a running seat to get it.
- `--per-ruling` notes also land on OWNER.jsonl. So 'an OWNER event exists' does not mean 'he answered'. Require
  `ownerSaid` or `byCard`.

### Services, clones and records

**A retired seat clone is emptied or left stale while a service still runs from it**
- What happens: evidence from the retired foundry clone:
  - `rm-scratch-reap` failed every run on 'ledger corpus missing', because `DEFAULT_CORPUS` still
    named the retired clone `/home/mandrake/rm/foundry`;
  - `rm-mirror.service` and `rm-codebase-health.service` ran code from the retired foundry clone, whose HEAD stopped at
    2026-11-02. So the landed fixes to `mirror.py` and `codebase_health_publish.py` never went live (they are outside
    `ops_clocks.json`).
- Do instead: before you retire a clone, grep `src/` and the unit files for it as a root. Give such services a non-seat
  home. `PROTECTED` lists in `scratch_reap.py` that name the clone are harmless.

**Served review-sheet output**
- What happens: all of `Transient/` is untracked since 2026-10-18, except `*.decisions.json` and pins.
  `refresh_sheets.py` prints `UNPUBLISHED:` only for a rebuilt sheet that is pinned (tracked).
- Do instead: publish a pinned rebuilt sheet. An unpinned sheet needs nothing.

**A landed fix to a timer's code**
- What happens: the fix is not running until the clone that the unit runs from syncs (e.g. `/home/mandrake/rm/dispatch`
  for `rm-scratch-reap`). An alarm between the landing and that sync comes from the old code. Yet `live_repeats` counts
  it as the fix dying.
- Do instead: to answer such an alarm, replay the guard on the pre-fix rev (`selftest --rev`).

**A backup path cited in a ledger note**
- What happens: the path is not durable proof. Evidence: a bundle folder under `D:\ClaudeWork\backups\leftovers` was
  named in a note and was absent days later. Its blob-identity claim could not be rerun; only commit ancestry stayed
  measurable.
- Do instead: when you drop a clone, name in the note the main commits that hold its work. Treat the bundle as a
  convenience.

### Other rules

- Rehearsing parallel integration:
  - Clone an integration repo with `-b main`. Its HEAD may sit on the candidate branch mid fan-in.
  - `git cherry-pick --continue` fails on an empty pick. Use `--skip`.
  - A board's `done` must mean LANDED before dependents are given.
- **Re-measure state numbers immediately before acting.**
  - Peers' commits land on origin/main all the time. Your clone does not see them until `./sync`.
  - The read-only D:\ mirror trails origin by up to 5 minutes (`MIRROR_HEAD` names its commit).
  - Mod counts, deploy drift and `git log` decay in minutes. Evidence: a pre-load brief's "577 active mods, no new
    assembly" was false within twenty.
  - Diff before you escalate. Evidence: `modlist_swap --status` read `UNRECOGNISED` while membership and order were
    byte-identical; only the formatting differed.
  - Correct in place, and strike the dead reading. Do not silently overwrite it.
