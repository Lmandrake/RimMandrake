# Git workflow — the operating doc (2026-10-02)

Rationale and measurements: `git_workflow_plan_2026-10-01.md` (plan) and the dated
`git_migration_*_2026-10-02.md` records (what was built). This file states what IS.

## Where work happens

| place | what it is |
|---|---|
| `/home/mandrake/rm/bench`, `/home/mandrake/rm/foundry` | the seat clones — ext4, plain git, **one writer each** (the seat's own window). Every seat launches from its clone. |
| `D:\Luke\dev\RimMandrake` (`/mnt/d/Luke/dev/RimMandrake`) | **read-only mirror** of origin/main, refreshed every 5 min by `rm-mirror.timer` (`./mirror sync`). No `.git`. Never write it; Windows tools (the game deploy, Explorer, python.exe) read it. `MIRROR_HEAD` names its commit; `MIRROR_STALE` appears if a refresh failed. |
| `/home/mandrake/rm/mirror.git` | the mirror's bare fetch-only repo |
| `D:\ClaudeWork\rimmandrake\artpipe\` | artpipe queue/state (not in git): `pending/ active/ done/ failed/ _artsrc/ registry.jsonl` |
| `D:\ClaudeWork\rimmandrake\build\`, `D:\ClaudeWork\rimmandrake\scratch\codex\` | build staging and codex.exe staging (drive-local scratch) |
| `/home/mandrake/rm/store.git` | the shared object store: bare, fetched from `mirror.git`, never pruned. Throwaway clones borrow from it, never from a seat clone |
| `/home/mandrake/rm/scratch/<SEAT>/` | throwaway ext4 clones, made only with `python3 src/RimMandrake/Utils/scratch_clone.py clone "<purpose>"` (never `/tmp`: tmpfs). Trial with telemetry: `design/RimMandrake/objstore_trial_2026-10-08.md` |

A session in the `D:\` mirror cannot commit: `./publish` refuses under `/mnt/`, and the
`block_shared_tree_merge.py` hook refuses whole-tree git there.

## The loop (seat)

```
./publish -m "subject" path/one path/two        # commit those paths, replay onto origin/main, push; prints PUBLISHED <sha>
land.sh <sha> <path>...                         # land one commit already made (any clone; plumbing)
land.sh -m "subject" <path>...                  # land working-tree bytes of the paths without a local commit
./sync                                          # realign this clone's main with origin/main (seat_sync.py)
```

- `./publish` (`src/RimMandrake/Utils/publish.py`) commits by pathspec, re-creates any local commit not yet upstream on
  origin/main by plumbing (`merge-tree` + `commit-tree`), moves main there with `git reset --keep`, pushes, and retries up
  to 8 times when origin moved. It **never stashes**, so it works in a dirty clone: it refuses only on a real conflict or
  when you hold an uncommitted edit to a file origin changed, naming the path, with your commit intact on HEAD.
- `land.sh` (`src/RimMandrake/Utils/land.sh`; `/home/mandrake/.seat-tmp/land.sh` is a one-line wrapper) publishes ONE
  commit or explicit paths by plumbing, retries a lost push race, then runs `./sync --no-fetch` itself. `LAND_REPO`
  defaults to the clone the cwd is in. stdout is exactly `PUBLISHED <sha>`; pass it to `rimflow close --sha`.
- `./sync` moves main to origin/main with `git reset --keep` only when every local commit is already upstream (git cherry
  `-`, or the same bytes per path) and no dirty file holds bytes other than upstream's; else it prints `REFUSED: <why>`
  and changes nothing. Local commits go to `backup/<seat>-pre-sync-<stamp>-<sha>`. Never stash, never `--hard`.
- Pathspec on the commit (`git commit <paths>`), never `git add -A`/`.`/`-a` (hook-enforced). Never `--force`. Never a file over ~50 MB.
- Proof of publication is `git merge-base --is-ancestor <sha> origin/main`, never an empty `git log origin/main..HEAD`.
- Origin is SSH (`git@github.com:Lmandrake/RimMandrake.git`).
- Committed and pushed is the only durable state: commit at each finished unit and push at once.
- Do not `git pull --rebase` in a seat clone: it refuses on ANY dirty file, and a seat clone is always a little dirty.

## Subagents

- 🔴 **Worktrees are OFF** (owner, 2026-10-02, by card). Never `isolation: "worktree"`, never `git worktree add`; `.claude/hooks/block_worktrees.py` refuses both and the WorktreeCreate hook refuses `claude --worktree`. Why: worktree agents duplicated whole checkouts and stranded work on side branches.
- A writing helper edits in its window's clone; the window commits explicit paths with `./publish`. Writing helpers run one at a time when their paths could overlap.
- Brief helpers: `reset --hard`, `checkout --`, `stash` on paths they did not create are forbidden; a conflict is reported, never cleared.
- The drained worktree work is under `archive/*` tags on origin (`git checkout <tag> -- <path>` restores a file); `design/RimMandrake/git_migration_drain_2026-10-02.md` is the census.

## Generated and per-writer state (nothing shared to conflict on)

| state | where |
|---|---|
| ledger | `infrastructure/state/ledger/events/<SEAT>.jsonl`, append-only, `merge=union`; `events.jsonl` is frozen. `ledger_lint.py` (and the pre-push hook `block_ledger_lint.py`) refuses an edited or reordered line. `model.read()` orders by content, so file order does not matter. Never resolve a shard with `checkout --ours/--theirs`. Events stranded in a seat clone that cannot push: `ledger_sync.py --seat <SEAT>` (dry run; `--apply` appends the missing lines and pushes from a throwaway clone under `/home/mandrake/rm/scratch/<SEAT>/` that is deleted when the run ends; `--clone <dir>` keeps a reusable one). |

**Pre-push guards run as a git-native hook** (`infrastructure/githooks/pre-push`, DLL/source-stamp + ledger lint; also the Claude PreToolUse hooks) via `core.hooksPath`, which is **set per clone**: `git config core.hooksPath infrastructure/githooks` (done in `~/rm/bench` and `~/rm/foundry`; a fresh clone must set it). Selftest: `python3 infrastructure/githooks/selftest_pre_push.py`.
| queue views | rendered on read, untracked: `python3 src/RimMandrake/rimflow/cli.py queue <SEAT>`. `queue/HUMAN.md` is the owner's hand-written inbox and stays tracked. |
| lessons | one file each in `infrastructure/state/lessons/` (`python3 src/RimMandrake/Utils/lessons.py add "…"`); `lessons.py render` makes the untracked `LESSONS_INBOX.md` view |
| code review status | append-only records `infrastructure/state/code_review/<SEAT>.jsonl` (`merge=union`), written only by `code_review_status.py`; review waves are one file each under `code_review/waves/` |
| health heartbeat | `Transient/codebase_health*`, `codebase_health_last.json`, `dashboards/hub/data/*.json` are untracked; `rm-codebase-health.timer` regenerates them in the FOUNDRY clone |
| `Transient/` | **untracked since 2026-10-18** (owner, by card). `Transient/.gitignore` ignores everything except itself, every `*.decisions.json`, and the pins `src/RimMandrake/Utils/transient_pin.py` manages (`add`/`rm`/`cited --add`/`untrack`). Files stay on disk: `./sync`, `./publish` and `land.sh` (via `seat_sync.reset_keep`) never delete a file upstream merely stopped tracking. Unpinned output is only in the clone that wrote it — not on `D:\`, GitHub or the other seat. |
| `conversations/` | committed by the handoff: `handoff.py` lands every new/changed record via `conversations_land.py` (owner 2026-10-18, *"the next handoff plays catchup"*). A handoff through `~/dev/Lodestar/bin/handoff.py` runs `python3 src/RimMandrake/Utils/conversations_land.py --apply` right after `conversations.py`. |
| Saves folder | keep only the canonical save(s) and saves awaiting review (`infrastructure/state/saves_awaiting_review.txt`); a backup lives until the operation it guards is verified. `python3 src/RimMandrake/Utils/saves_prune.py` reports (dry run); `--apply` deletes only uncited debug saves > 72 h and backups > 24 h — never a `CANONICAL_*` save. |

## Builds, DLLs, tools that need Windows

- C# builds: `python3 src/RimMandrake/Utils/winbuild.py <Mod|csproj>` stages the sources on `D:\ClaudeWork\rimmandrake\build\`, runs Windows dotnet, copies the DLL **and its `.srchash` back as a pair**. The JawaBench companion builds through `bridgetools/build.py`, which stages the same way.
- A committed DLL must be pushed with its `.srchash` (`dll_source_stamp.py`; guard `block_dll_source_mismatch.py` on push). **`./publish` lands DLLs; no agent resolves a DLL conflict or rebuilds one by hand to land.** A replay conflict on ONLY `.dll`/`.dll.srchash` pairs takes origin's side, then publish rebuilds each such DLL from the source committed at the new HEAD in a throwaway src-only `git clone --shared` under `/home/mandrake/rm/scratch/<SEAT>/` (never the worktree, so a peer's uncommitted C# cannot leak in), commits the pair and pushes. A `DLL_SOURCE_STAMP_GUARD_1` pre-push refusal gets the same rebuild and one retry. A conflict on any other path, or a peer's uncommitted edit to that DLL pair, still refuses and names the paths. Selftest: `src/RimMandrake/Utils/selftest_publish.py`.
- `codex.exe` cannot run from an ext4 cwd: `codex_image.py` and `gpt_consult.py` stage the call in `D:\ClaudeWork\rimmandrake\scratch\codex\<job>\` and copy results back.
- artpipe: the daemon runs from the FOUNDRY clone with `ARTPIPE_STATE_DIR=/mnt/d/ClaudeWork/rimmandrake/artpipe`. Art is copied into a clone for commit with `artpipe_state.py collect <job> --to src/…`; `artpipe_state.py find <term>` searches finished jobs.
- Anything bridge or game-facing from WSL runs under `python.exe` against the **mirror** path.
- Selftests that run Windows `dotnet.exe` fail from an ext4 clone with MSB3101/MSB3030/MSB1009 — not regressions; `src/RimMandrake/Utils/selftest_winstage.py` stages them on the Windows drive.

## History and recovery

- The old shared tree's worktrees, branches and stashes were drained into `archive/*` tags on origin (reachable, not accepted into main) plus `refs/rescue/*`; see `git_migration_drain_2026-10-02.md`. `git tag -l 'archive/*'` lists them.
- Never merge in a tree others write; there is no such tree any more — each clone has one writer.

## Scratch clones

- Scratch clones cost ~7-14 GB each (18 strays filled 276 GB, 2026-10-11). Prefer `land.sh`/`./publish`; if you must clone,
  use `scratch_clone.py`, `--reference <seat clone>` or `--filter=blob:none`.
- **Reaper** (owner by card 2026-10-18: delete after 24 h if fully pushed): `python3 src/RimMandrake/Utils/scratch_reap.py`
  (dry run; `--apply` deletes) judges every clone under `/home/mandrake/rm/scratch/**` and `~/.seat-tmp/**` and every
  session dir `~/.seat-tmp/<SEAT>/claude-*/<project>/<uuid>/`. It deletes only what is > 24 h old, has no commit off every
  remote (stale refs are re-checked against `mirror.git`), no changed or untracked file, no stash, no borrower, no
  running process, and is named by no ledger event, item or handoff — anything else is REFUSED and written to
  `~/.local/state/rm-scratch-reap/alarms.log`. `rm-scratch-reap.timer` runs it hourly, dry run until `--apply` is added.
  Deleting by hand: the same checks first (a scratchpad held CRACKEDLANDS_FULL_RENAME_1's only commits, 2026-10-18).
- Repo weight, measured 2026-10-11: bench `.git` holds 101,797 loose objects (4.4 GiB) + 155 packs (5.6 GiB), never gc'd.
  Running `git gc` there is the owner's call; run it when no window is mid-git.

## Traps

Each of these cost at least one lost or mis-published change. Most are hook-enforced or fixed in the tools above; the
rest are discipline.

| trap | what happens | do instead |
|---|---|---|
| `git add a b c 2>/dev/null` | one missing path fails the WHOLE add silently; the commit then runs on an empty or partial index and "succeeds" | never silence `git add`; check `git show --stat HEAD` |
| a deleted path on `git add` | `git add <deleted>` errors and kills the `&&` chain; the push after it says "Everything up-to-date" | put a deleted path on the commit pathspec only |
| pathspec commit takes the WORKTREE | `git commit <path>` is an implicit `git add` of that path: a blob you staged with `update-index` is ignored, and a peer's unsaved lines in the same file ride along | check `git diff --stat <path>` first; build partial commits in a temp index (`GIT_INDEX_FILE`) |
| pathspec commit cannot remove-but-keep | `git rm --cached p` then `git commit p` re-adds `p` from the worktree | commit through a temp index (`GIT_INDEX_FILE=… git read-tree HEAD; git rm --cached …; write-tree; commit-tree`), then `git reset -q -- p` in the real index |
| untracked can't be pathspec-committed | `git commit <new file>` → "did not match any file(s) known to git"; a `git commit <dir>` silently skips new files in it | `git add -- <new file>` first (explicit path), then `git commit <paths>` |
| `-F -` after `--` | `git commit -- p -F -` treats `-F` and `-` as pathspecs | options before `--`, paths after |
| bare `git commit` | commits the WHOLE index, including what a helper staged in the same clone | always name paths (hook-enforced) |
| `.git/index.lock` exists | a background helper's read-only `git status` holds it for a second; a failed `./publish` then committed NONE of its paths | wait a few seconds and retry; never delete a lock younger than a minute; check `git status` after any failed publish |
| compound command refused whole | a `PreToolUse` hook (blanket stage, DLL stamp, sheet guard) refuses the entire Bash call before the shell runs — any file write chained before the commit never happened either | keep file writes and git commands in SEPARATE Bash calls; a hook's refusal means nothing in that call ran |
| zsh refspec modifier | `git push origin $N:refs/heads/main` — zsh reads `:r` as a modifier and mangles the refspec | `"${N}:refs/heads/main"` |
| land.sh duplicates | landing by plumbing leaves the clone "ahead N, behind M" with patch-equivalent copies; a stale clone shows phantom selftest reds (ledger_lint NOT_APPEND, a "lost" bridge tool) | `land.sh` now syncs itself; otherwise `./sync`. Re-check a red on a synced clone before fixing it |
| autostash | `pull --rebase --autostash` re-applied peers' dirty files and stranded 53 in `stash@{0}` (2026-10-10) | never stash; `./publish` and `./sync` use `reset --keep` |
| pre-push ledger lint judges the LOCAL HEAD | a correct plumbing push from a clone behind origin is refused NOT_APPEND | `./sync` first, then land |
| served review-sheet output | all of `Transient/` is untracked since 2026-10-18 except `*.decisions.json` and pins; `refresh_sheets.py` prints `UNPUBLISHED:` only for a rebuilt sheet that is pinned (tracked) | publish a pinned rebuilt sheet; an unpinned one needs nothing |
| a fetch OOM-kills the window | fetching the 5.5 GiB pack inside a 10G-capped seat scope | `systemd-run --user --scope --quiet -p MemoryMax=20G git fetch origin main` |
| a real merge commit | the blanket-stage hook refuses `git commit --no-edit` mid-merge (no pathspec possible) | `GIT_EDITOR=true git merge --continue` |
