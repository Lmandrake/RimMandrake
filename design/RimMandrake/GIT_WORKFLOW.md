# Git workflow — the operating doc (2026-10-02)

Rationale and measurements: `git_workflow_plan_2026-10-01.md` (plan) and the dated
`git_migration_*_2026-10-02.md` records (what was built). This file states what IS.

## Where work happens

| place | what it is |
|---|---|
| `/home/mandrake/rm/bench`, `/home/mandrake/rm/foundry` | the seat clones — ext4, plain git, **one writer each** (the seat's own window). Every seat launches from its clone. |
| `D:\Luke\dev\RimMandrake` (`/mnt/d/Luke/dev/RimMandrake`) | **read-only mirror** of origin/main, refreshed every 5 min by `rm-mirror.timer` (`./mirror sync`). No `.git`. Never write it; Windows tools (the game deploy, Explorer, python.exe) read it. `MIRROR_HEAD` names its commit; `MIRROR_STALE` appears if a refresh failed. |
| `/home/mandrake/rm/mirror.git` | the mirror's bare fetch-only repo |
| `D:\Luke\dev\_artpipe\` | artpipe queue/state (not in git): `pending/ active/ done/ failed/ _artsrc/ registry.jsonl` |
| `D:\Luke\dev\_rmbuild\`, `D:\Luke\dev\_rmscratch\codex\` | build staging and codex.exe staging (drive-local scratch) |
| `/home/mandrake/rm/store.git` | the shared object store: bare, fetched from `mirror.git`, never pruned. Throwaway clones borrow from it, never from a seat clone |
| `/home/mandrake/rm/scratch/<SEAT>/` | throwaway ext4 clones, made only with `python3 src/RimMandrake/Utils/scratch_clone.py clone "<purpose>"` (never `/tmp`: tmpfs). Trial with telemetry: `design/RimMandrake/objstore_trial_2026-10-08.md` |

A session in the `D:\` mirror cannot commit: `./publish` refuses under `/mnt/`, and the
`block_shared_tree_merge.py` hook refuses whole-tree git there.

## The loop (seat)

```
git add/commit <explicit paths>  →  git pull --rebase origin main  →  git push origin HEAD:main
./publish -m "subject" path/one path/two        # the same, wrapped; prints PUBLISHED <sha>
```

- Pathspec on the commit (`git commit <paths>`), never `git add -A`/`.`/`-a` (hook-enforced). Never `--force`. Never a file over ~50 MB.
- `./publish` retries up to 8 times on a non-fast-forward, checks `merge-base --is-ancestor` after any ambiguous push, and aborts (naming the paths) on a real rebase conflict, leaving the commit on HEAD. Pass the printed sha to `rimflow close --sha`.
- Proof of publication is `git merge-base --is-ancestor <sha> origin/main`, never an empty `git log origin/main..HEAD`.
- Origin is SSH (`git@github.com:Lmandrake/RimMandrake.git`).
- Committed and pushed is the only durable state: commit at each finished unit and push at once.

## Subagents

- 🔴 **Worktrees are OFF** (owner, 2026-10-02, by card). Never `isolation: "worktree"`, never `git worktree add`; `.claude/hooks/block_worktrees.py` refuses both and the WorktreeCreate hook refuses `claude --worktree`. Why: worktree agents duplicated whole checkouts and stranded work on side branches.
- A writing helper edits in its window's clone; the window commits explicit paths with `./publish`. Writing helpers run one at a time when their paths could overlap.
- Brief helpers: `reset --hard`, `checkout --`, `stash` on paths they did not create are forbidden; a conflict is reported, never cleared.
- The drained worktree work is under `archive/*` tags on origin (`git checkout <tag> -- <path>` restores a file); `design/RimMandrake/git_migration_drain_2026-10-02.md` is the census.

## Generated and per-writer state (nothing shared to conflict on)

| state | where |
|---|---|
| ledger | `infrastructure/state/ledger/events/<SEAT>.jsonl`, append-only, `merge=union`; `events.jsonl` is frozen. `ledger_lint.py` (and the pre-push hook `block_ledger_lint.py`) refuses an edited or reordered line. `model.read()` orders by content, so file order does not matter. Never resolve a shard with `checkout --ours/--theirs`. |

**Pre-push guards run as a git-native hook** (`infrastructure/githooks/pre-push`, DLL/source-stamp + ledger lint; also the Claude PreToolUse hooks) via `core.hooksPath`, which is **set per clone**: `git config core.hooksPath infrastructure/githooks` (done in `~/rm/bench` and `~/rm/foundry`; a fresh clone must set it). Selftest: `python3 infrastructure/githooks/selftest_pre_push.py`.
| queue views | rendered on read, untracked: `python3 src/RimMandrake/rimflow/cli.py queue <SEAT>`. `queue/HUMAN.md` is the owner's hand-written inbox and stays tracked. |
| lessons | one file each in `infrastructure/state/lessons/` (`python3 src/RimMandrake/Utils/lessons.py add "…"`); `lessons.py render` makes the untracked `LESSONS_INBOX.md` view |
| code review status | append-only records `infrastructure/state/code_review/<SEAT>.jsonl` (`merge=union`), written only by `code_review_status.py`; review waves are one file each under `code_review/waves/` |
| health heartbeat | `Transient/codebase_health*`, `codebase_health_last.json`, `dashboards/hub/data/*.json` are untracked; `rm-codebase-health.timer` regenerates them in the FOUNDRY clone |

## Builds, DLLs, tools that need Windows

- C# builds: `python3 src/RimMandrake/Utils/winbuild.py <Mod|csproj>` stages the sources on `D:\Luke\dev\_rmbuild\`, runs Windows dotnet, copies the DLL **and its `.srchash` back as a pair**. The JawaBench companion builds through `bridgetools/build.py`, which stages the same way.
- A committed DLL must be pushed with its `.srchash` (`dll_source_stamp.py`; guard `block_dll_source_mismatch.py` on push). FOUNDRY alone commits DLLs; after a merge touching a mod's `Source/`, rebuild — never pick a side's DLL.
- `codex.exe` cannot run from an ext4 cwd: `codex_image.py` and `gpt_consult.py` stage the call in `D:\Luke\dev\_rmscratch\codex\<job>\` and copy results back.
- artpipe: the daemon runs from the FOUNDRY clone with `ARTPIPE_STATE_DIR=/mnt/d/Luke/dev/_artpipe`. Art is copied into a clone for commit with `artpipe_state.py collect <job> --to src/…`; `artpipe_state.py find <term>` searches finished jobs.
- Anything bridge or game-facing from WSL runs under `python.exe` against the **mirror** path.

## History and recovery

- The old shared tree's worktrees, branches and stashes were drained into `archive/*` tags on origin (reachable, not accepted into main) plus `refs/rescue/*`; see `git_migration_drain_2026-10-02.md`. `git tag -l 'archive/*'` lists them.
- Never merge in a tree others write; there is no such tree any more — each clone has one writer.

## Landing when `pull --rebase` is refused (land.sh)

When peers' unstaged edits make `pull --rebase` refuse, use `/home/mandrake/.seat-tmp/land.sh` (tracked copy and README:
`src/RimMandrake/Utils/land.sh`, `land_README.md`). `land.sh <sha> <path>...` replays that one commit; `land.sh -m "<msg>" <path>...`
builds it in a temp index from origin/main. It refuses no-sha, paths outside the list, and anything already on origin/main, never
touches the shared index, and prints `PUBLISHED <sha>`. Never run it without an explicit sha or paths.
