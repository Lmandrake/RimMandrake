# Git workflow — the operating doc (2026-10-02)

Rationale and measurements: `git_workflow_plan_2026-10-01.md` (plan) and the dated
`git_migration_*_2026-10-02.md` records (what was built). This file states what IS.

## Where work happens

| place | what it is |
|---|---|
| `/home/mandrake/rm/bench` | the seat clone — ext4, plain git, **one writer** (the seat's own window). The seat launches from its clone. (FOUNDRY is retired and its clone is deleted.) |
| `D:\Luke\dev\RimMandrake` (`/mnt/d/Luke/dev/RimMandrake`) | **read-only mirror** of origin/main, refreshed every 5 min by `rm-mirror.timer` (`./mirror sync`). No `.git`. Never write it; Windows tools (the game deploy, Explorer, python.exe) read it. `MIRROR_HEAD` names its commit; `MIRROR_STALE` appears if a refresh failed. |
| `/home/mandrake/rm/mirror.git` | the mirror's bare fetch-only repo |
| `D:\ClaudeWork\rimmandrake\artpipe\` | artpipe queue/state (not in git): `pending/ active/ done/ failed/ _artsrc/ registry.jsonl` |
| `D:\ClaudeWork\rimmandrake\build\`, `D:\ClaudeWork\rimmandrake\scratch\codex\` | build staging and codex.exe staging (drive-local scratch) |
| `/home/mandrake/rm/store.git` | the shared object store: bare, fetched from `mirror.git`, never pruned. Throwaway clones borrow from it, never from a seat clone |
| `/home/mandrake/rm/scratch/<SEAT>/` | throwaway ext4 clones, made only with `python3 src/RimMandrake/Utils/scratch_clone.py clone "<purpose>" [--sparse <dirs the task needs>]` (never `/tmp`: tmpfs). The default is a cone-sparse tree (root files, `.claude`, `infrastructure`, `skills`, `src/RimMandrake/Utils`, `src/RimMandrake/rimflow`, ~200 MB), not the whole ~4 GB; `--checkout` only for repo-wide work, say why in the purpose. Trial with telemetry: `design/RimMandrake/objstore_trial_2026-10-08.md` |

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
- Proof of publication is `git merge-base --is-ancestor <sha> origin/main`, never an empty `git log origin/main..HEAD` and never the exit code: `./publish` can exit 120 with no output yet have pushed.
- Origin is SSH (`git@github.com:Lmandrake/RimMandrake.git`).
- Committed and pushed is the only durable state: commit at each finished unit and push at once.
- Do not `git pull --rebase` in a seat clone: it refuses on ANY dirty file, and a seat clone is always a little dirty.

## Subagents

- 🔴 **Worktrees are OFF** (owner, 2026-10-02, by card). Never `isolation: "worktree"`, never `git worktree add`; `.claude/hooks/block_worktrees.py` refuses both and the WorktreeCreate hook refuses `claude --worktree`. Why: worktree agents duplicated whole checkouts and stranded work on side branches.
- A writing helper edits in its window's clone; the window commits explicit paths with `./publish`. Writing helpers run one at a time when their paths could overlap.
- Brief helpers: `reset --hard`, `checkout --`, `stash` on paths they did not create are forbidden; a conflict is reported, never cleared.
- The drained worktree work is under `archive/*` tags on origin (`git checkout <tag> -- <path>` restores a file); `design/RimMandrake/git_migration_drain_2026-10-02.md` is the census.
- A helper must never rewrite commits it did not author. A guard refusal (e.g. the art push guard refusing deletion of owner-kept PNGs) is reported back and the parent lands it; one rm-fixer rewrote four unpublished local commits in the shared clone, one a peer's, to drop the deletions (trees matched, nothing lost, but never again).

## Generated and per-writer state (nothing shared to conflict on)

| state | where |
|---|---|
| ledger | `infrastructure/state/ledger/events/<SEAT>.jsonl`, append-only, `merge=union`; `events.jsonl` is frozen. `ledger_lint.py` (and the pre-push hook `block_ledger_lint.py`) refuses an edited or reordered line. `model.read()` orders by content, so file order does not matter. Never resolve a shard with `checkout --ours/--theirs`. Events stranded in a seat clone that cannot push: `ledger_sync.py --seat <SEAT>` (dry run; `--apply` appends the missing lines and pushes from a throwaway clone under `/home/mandrake/rm/scratch/<SEAT>/` that is deleted when the run ends; `--clone <dir>` keeps a reusable one). |

**Pre-push guards run as a git-native hook** (`infrastructure/githooks/pre-push`, DLL/source-stamp + ledger lint; also the Claude PreToolUse hooks) via `core.hooksPath`, which is **set per clone**: `git config core.hooksPath infrastructure/githooks` (done in `~/rm/bench`; a fresh clone must set it). Selftest: `python3 infrastructure/githooks/selftest_pre_push.py`.
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
- A history rewrite of origin/main strands every remote clone that pulls `--ff-only` ('ahead N, behind N'; SteveDesktop's `~/rm/runner` and testq paused REFUSED/SYNC after the work-history excise). Re-point remote clones in the same change. The reset-hard hook matches ssh command text too; `git switch --detach origin/main; git branch -f main origin/main; git switch main` moves a clean clone and still refuses over local edits.

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
- **Check `df -h /` before spawning clone-heavy agents, and when a git write fails with `Out of diskspace`.** Seat scratch (`~/.seat-tmp/<SEAT>/*_export`, clean clones, `ledger_sync` repos) and `/home/mandrake/rm/scratch` clones are 7-23 GB each and filled the root disk to 1.5 MB free. Delete finished ones at once (after 0 unpushed commits) and shallow- or `--filter=blob:none`-clone new ones.
- **A seat fanning out helpers must take pool clones (`scratch_clone.py`) or delete its own once landed.** 17 work-package clones under `~/rm/scratch/<SEAT>` made outside the pool were left after their work landed, read YOUNG to `scratch_reap` until the TTL, and fired a SCRATCH_OUTSIDE_CAP alarm for hours. A dirty ledger shard in such a clone is usually a rewritten copy of lines already on origin/main (check by set difference).
- **`scratch_reap` sanity END lines must count only what the run LEFT (rows not DELETED/YOUNG), never a whole-population count:** `session_dirs` and `rm_scratch_clones` each alarmed on live young work. Whole counts stay readings; `ops_watch` OP2 reads `rm_scratch_clones`.

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
| `handoff.py` UNPUSHED gate refuses a fully published tree | the gate compares SHAs, not patches; publish rebases, so the local SHAs differ from origin's | prove equivalence with `git log --cherry-mark origin/main...HEAD`, then `./sync`; do not reach for `--force` |
| `handoff.py --wake` in a stale shared checkout | it prints that checkout's newest handoff, not origin's, so a window can wake on an old one | read `git show origin/main:infrastructure/state/handoffs/<newest>` instead |
| a plumbing-built push (patch diffed from the wrong parent, `git apply` failing inside a pipe to `tail`) | pushed an EMPTY commit with a misleading message | assert the apply succeeded (`set -o pipefail`) and that the resulting tree differs from `origin/main` before pushing |
| `git commit && git pull --rebase && git push` in ONE Bash call | the pre-push/PreToolUse ledger hook judges HEAD BEFORE the compound runs, so it is refused NOT_APPEND even though the rebase would fix it | run commit, pull/rebase and push as separate Bash calls; never stash a peer's dirty files to rebase (`./publish` replays without a stash) |
| `./publish` refuses ('not mine to overwrite', `reset --keep` refused, exit 2) because a PEER has an uncommitted edit to a file origin changed, or to the mod DLL pair (their `winbuild.py` output, `+dirty` in the `.srchash`) | your commit stays local and every later publish waits on that peer; the temp-index + `commit-tree` + push workaround is refused by the ledger_lint push hook, which lints the stale local HEAD | land WITHOUT touching the tree: `tree=$(git merge-tree --write-tree --merge-base=C^ origin/main C)`; `commit-tree` it onto `origin/main`; `git push origin <tip>:main` (local main stays diverged; the next publish's `git cherry` skips it). Or from a throwaway `git clone --shared --no-checkout <seat clone> /home/mandrake/rm/scratch/<SEAT>/land`: set `origin` to the real remote, `checkout -B main origin/main`, cherry-pick, push (there HEAD IS origin+1, so the lint passes). Ledger shard lines: append only the new ones. For a peer's dirty DLL pair only: back the pair up under `D:\ClaudeWork\rimmandrake\backups\`, `git show HEAD:<path> > <path>` for both files, `./publish` (it rebuilds from committed source), then `winbuild.py <Mod>` again so the working copy carries the peer's source. Tell the report whose edit blocked it |
| `./publish` replay stops on YOUR commit, or refuses a DLL conflict because a helper's commit in the same clone was replayed (local HEAD keeps its pre-replay twin), in a clone dirty with peers' files | rebase, `--autostash` and stash are all refused or destructive there | rebuild the local chain by plumbing (`git merge-tree --merge-base=c^` + `commit-tree`, your conflicted file given as a resolved blob via a temp `GIT_INDEX_FILE`), re-check HEAD has not moved, then `git reset --keep` to the new tip. Or restore worktree files to origin ONLY for paths in `git diff --name-only <your-commit> origin/main` that are NOT in your own commit's diff (looping over `HEAD..origin` overwrote one's own changes once), `git update-ref refs/heads/main origin/main`, `git reset -q -- <those paths>`, `./publish` your paths. Before `git checkout <your-commit> -- <paths>` confirm none of those paths changed on origin |
| `winbuild.py` stages the WORKTREE | in a clone holding another helper's uncommitted C#, the built DLL bakes it in (`+dirty` srchash) and `DLL_SOURCE_STAMP_GUARD_1` refuses the push | build from a src-only scratch clone at HEAD: `git clone --shared --no-checkout <seat clone> <ext4 dir>; git sparse-checkout set src; git checkout HEAD` (~8 s; a full clone onto `D:\ClaudeWork` took 8.5 min), `winbuild.py` there, copy the `.dll` + `.srchash` back. If origin moved with another DLL commit, replay your source commits onto `origin/main` there (take origin's DLL), rebuild, then `git reset --keep` the seat clone to that tip and `./publish`. First check whether a peer already pushed your source with a DLL rebuilt over it (`git cherry`; literal-grep a new method name in origin's DLL with `MEASURE_ALLOW_SCAN=1`) |
| `./publish` 'git reset --keep refused' on `infrastructure/state/ledger/events/<SEAT>.jsonl` in a shared worktree | another agent's ledger line sits uncommitted AND already on origin | if `git show origin/main:<shard> \| cmp - <shard>` says identical, `git checkout -- <shard>` and re-run `./publish`: `reset --keep` writes origin's copy back and nothing is lost |
| a side or scratch clone commits/cherry-picks with the global identity | the commit carried the owner's personal email on the PUBLIC repo | in any side clone run `git config user.email 313496996+Lmandrake@users.noreply.github.com` before committing or cherry-picking |
| `./publish` refuses on an untracked file origin also added (e.g. `conversations/*.md` landed by another seat) | an identical untracked copy blocks the replay | `cmp` it against `origin/main`, move the identical copy aside, re-run |
| `publish.py`'s `git push` hangs 9+ minutes | the commit may already be on origin | `git branch -r --contains <sha>` before re-publishing or waiting; stop only your own push by PID |
| `./publish -m "..."` with a ledger shard path inside a helper/background process | a background helper can fail `./publish` and `git push` with `Permission denied (publickey)` while the parent's pushes work; its commits stay local | the parent checks `git status -sb` for `ahead N` after each helper and publishes itself |
| a temp `GIT_INDEX_FILE` commit (`read-tree HEAD; add; write-tree; commit-tree -p HEAD`) in a shared clone | racy: if a peer commits between `read-tree` and `commit-tree`, the new commit silently reverts the peer's files | read HEAD ONCE, build the index from that same sha, and `update-ref refs/heads/main NEW OLD` with that sha as the expected old value |
| two helpers edit the same file at once and each wants to commit only its own hunks | `git commit <path>` takes the WORKTREE file (peer's hunks ride along; seen with `auditor.md`, `dispatcher_schedule.json`, `arena_eventlog.py`, a csproj line), a pathspec-less commit is hook-blocked, a bare `--amend` is refused, and `git apply --cached --unidiff-zero` with filtered `-U0` hunks inserts at the NEW-side line numbers of the full diff (wrong positions); `code_review_status.py mark-clean` then refuses the file until the peer commits, and `./publish` refuses while any peer's build left the mod DLL dirty | plan it: agree with the parent who commits the shared file whole, or land your edit first. If you must split: build the blob (HEAD content + your lines inserted after anchor lines), `git hash-object -w`, then commit through a PRIVATE index (`GIT_INDEX_FILE=tmp git read-tree HEAD; git update-index --cacheinfo 100644,<blob>,<path>; git commit-tree $(git write-tree) -p HEAD; git update-ref refs/heads/main <new> <old>`), assert the blob against the worktree, then `git diff` to confirm the peer's hunks are still in the worktree. A `git commit -- paths` leaves any OTHER staged path (e.g. a peer's csproj line) staged. If a foreign hunk rode along, say so in the commit |
| a helper told 'never pull' is also told to `./publish` in a clone a running trial loads code from | `./publish` is a tree move (fetch + rebase, reflog `reset: moving to <sha>`): 21 HEAD moves hit the clone during a trial freeze, and the arms' gate/judge/snapshot subprocesses load disk code per call, so verdicts ran newer code than the runner | arms run from a read-only pin; while a trial runs from a live clone no helper publishes there (commit local only) |
- **`git rm` stages a deletion into the index; delete with plain `rm` then a pathspec commit.** A directory pathspec sweeps untracked build output (`bin/`, `obj/`), so read `git status` on it first. Two windows of one seat share a clone and its index; an `index.lock` "File exists" means a commit is running now, so wait and never delete it.
- **Re-measure state numbers immediately before acting.** Peers' commits land on origin/main continuously; your clone does not see them until `git pull --rebase`, and the read-only D:\ mirror trails origin by up to 5 minutes (`MIRROR_HEAD` names its commit). Mod counts, deploy drift and `git log` decay in minutes, so a pre-load brief's "577 active mods, no new assembly" was false within twenty. Diff before escalating (`modlist_swap --status` read `UNRECOGNISED` while membership and order were byte-identical, formatting only). Correct in place and strike the dead reading rather than silently overwriting it.
| a wake after a logout or crash | the predecessor's tail (local commits already on origin under other hashes, uncommitted ledger and art-ledger files, sheet webps) is unpushed, and a crash can leave empty loose git objects and a stale `.git/index.lock` that pass a commit but fail `git fsck` and the DLL stamp guard | first `git status -sb` against a fresh fetch, and `git fsck --no-dangling`; fix empty objects by deleting them and `git hash-object -w` on the identical working file, never trust the handoff's "everything pushed" |
| a retired seat clone is emptied or left stale while a service still runs from it | `rm-scratch-reap` failed every run on 'ledger corpus missing' (`DEFAULT_CORPUS` still named `/home/mandrake/rm/foundry`); `rm-mirror.service` and `rm-codebase-health.service` ran code from the retired foundry clone whose HEAD stopped at 2026-11-02, so landed fixes to `mirror.py` and `codebase_health_publish.py` never went live (they are outside `ops_clocks.json`) | before retiring a clone, grep `src/` and the unit files for it as a root; give such services a non-seat home; `PROTECTED` lists in `scratch_reap.py` naming it are harmless |
| a landed fix to a timer's code | it is not running until the clone the unit runs from (e.g. `/home/mandrake/rm/dispatch` for `rm-scratch-reap`) syncs; an alarm between landing and that sync is the old code, yet `live_repeats` counts it as the fix dying | replay the guard on the pre-fix rev (`selftest --rev`) to answer it |
| a judge reads `OWNER.jsonl` from its own clone's working tree | it is only as fresh as that clone's last pull: `~/rm/dispatch` was behind origin and refused a Designer run WAITING_OWNER with his answer already published | read the owner's word as working tree UNION origin/main (`concept_tree.owner_lines`) after a `git fetch` (`role_launch.judge_sync`); never pull a clone under a running seat to get it. `--per-ruling` notes also land on OWNER.jsonl, so 'an OWNER event exists' is not 'he answered': require `ownerSaid` or `byCard` |
| a backup path cited in a ledger note | it is not durable proof: a bundle folder under `D:\ClaudeWork\backups\leftovers` named in a note was absent days later, so its blob-identity claim could not be rerun and only commit ancestry remained measurable | when dropping a clone, name the main commits that hold its work in the note; treat the bundle as a convenience |
- Rehearsing parallel integration: clone an integration repo with `-b main` (its HEAD may sit on the candidate branch mid fan-in); `git cherry-pick --continue` fails on an empty pick, use `--skip`; a board's `done` must mean LANDED before dependents are given.
