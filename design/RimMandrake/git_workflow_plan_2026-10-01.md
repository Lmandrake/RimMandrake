# RimMandrake git workflow — integrated plan (2026-10-01)

Status: DRAFT for owner ruling. Nothing here is implemented. Inputs, all on origin/main:
`git_workflow_fix_2026-10-01.md` (the shipped `./publish`), `git_workflow_review_gpt61_2026-10-01.md`,
`git_research_2026-10-01.md`, `git_experiments_2026-10-01.md` (E1–E5), `git_x1_worktree_pool_2026-10-01.md`,
`git_x2_history_replay_2026-10-01.md`, `git_windows_tool_probe_2026-10-01.md`, all in `D:\Luke\dev\RimMandrake\design\RimMandrake\`.

## 1. Diagnosis

Ranked by measured contribution. "K=5" = X2's replay of 3,403 real commits (09-17..10-01), each
cherry-picked onto a base 5 commits stale.

1. **Generated files are tracked, so every writer conflicts on output nobody authored.** Rendered queue
   views are the largest non-mergeable class: 810 conflicted commits at K=5 (`queue/FOUNDRY.md` 738,
   `queue/BENCH.md` 647 path hits). Health html/json (22), `CODE_REVIEW_STATUS.json` (15), plus
   generated-ish residue X2's regex missed (`items/DIRTY_CODE_REVIEW_STANDING_LOOP_1.md` 62,
   `state/codebase_health_last.json` 30, `dashboards/hub/data/health.json` 23). 212 of 3,403 commits
   touch *only* generated artifacts. The artpipe daemon's queue state is tracked too (3,373 `done/` +
   442 `pending/` JSON), which is why the shared tree shows ~295 daemon deletions. Precedent:
   `.gitignore` already untracks four older queue views (DECIDE/BUILD/CHECK/REP); the current three
   were left tracked.
2. **Append-only coordination files are merged as text.** Ledger shards: 962 conflicted commits at
   K=5; 1,218 commits (36%) touch a ledger jsonl, ~475 are pure "ledger sync" bookkeeping. E2:
   4 writers × 10 rounds, no attributes → 24 rebase conflicts per run; `merge=union` or one-file-per-record
   → **0**. No `.gitattributes` exists on origin. Fixing (1)+(2) together takes the K=5 conflict rate
   **43.6% → 13.6%** (K=1 14.2% → 3.9%).
3. **Writable checkouts live on drvfs.** `git status` 10–12 s on drvfs vs 0.04 s on ext4 (≈300×);
   `git checkout` 4 m 37 s vs 10.7 s; full worktree 11 s / 4.1 G vs sparse 0.95 s / 318 M. 124 of 132
   worktrees were under `.claude/worktrees/` on drvfs; the prune dry run exceeded 10 min.
4. **Many writers per tree, no ownership, unbounded lifecycle.** Shared tree: 215 files lost 09-25
   (refused merge + peer `index.lock`), `reset --hard` ate 3 staged files 09-18, and today a peer ran
   `git checkout origin/main -- src` (overwrites uncommitted `src/` edits) — agents improvise
   destructive catch-ups because the tree is 303 behind with ~2,250 untracked files and no safe
   forward path. Worktree week: 132 worktrees, 146 branches, 68 never merged holding 257 unique
   commits, `/tmp` at 100%, throughput 268 → 178 commits/day, recovery-subject commits 2.4% → 4.2%
   (one confounded week).
5. **Publication and acceptance disagree.** `./publish` lands work under new shas, so the shared tree's
   originals read "unpushed" forever and the handoff gate refuses; per-path 3-way misses
   rename/delete/mode cases `merge-tree` handles (E3); `LESSONS_INBOX.md` concurrent appends refuse.
6. **Residual, genuine conflicts** (K=5): source 111, DLL/`.srchash` 71, docs/item md ~350. Source
   conflicts are the ones git *should* surface; DLL conflicts are avoidable (one writer, §2.7).

## 2. Target architecture

Invariant (GPT review, adopted): **one exclusive owner per writable workspace, bounded write slots,
every writable workspace on ext4.**

### 2.1 Seat clones (ext4)

| seat | path | kind |
|---|---|---|
| BENCH | `/home/mandrake/rm/bench` | full clone of `git@github.com:Lmandrake/RimMandrake.git` |
| FOUNDRY | `/home/mandrake/rm/foundry` | full clone; sole deployer, sole DLL committer |

Separate clones (not worktrees of one repo) give each seat its own object store, refs, config and
`index.lock` — no cross-seat lock contention at all. ~3.2 GiB packed each against 870 GB free. Each is
written only by its seat session and that seat's non-isolated edits; workflow is **plain git**:
`git commit <paths>` → `git pull --rebase` → `git push`, retry on non-ff. With §2.4/§2.5 in place the
rebase rarely stops; when it does it stops on a real conflict, in a tree with one owner, where
resolving it is safe. `rimflow close --sha HEAD` becomes correct again because HEAD *is* what was pushed.

### 2.2 Subagent worktree pool

- **Mechanism:** project `WorktreeCreate` hook (X1's `/home/mandrake/wt/x1/pool_hook.py`, measured
  end-to-end on CC 2.1.285). Real stdin is `cwd` + `name` (+`prompt_id`), not the documented
  `base_path`/`worktree_name`; stdout line 1 = path; non-zero exit = clean Agent-tool error.
- **Placement/size:** `/home/mandrake/rm/pool/<seat>/slot{0..2}` — **3 slots per seat, 6 total**, each a
  linked worktree of that seat's clone. **Full checkouts**, persistent: the 11 s / 4.1 G cost is paid once
  per slot (25 G total); recycling is `git checkout -B agent/<name> origin/main`, an ext4 delta. Sparse is
  rejected as default because the hook cannot know which paths an agent will touch and builds need all
  of `src/`.
- **Ownership:** `slotN.lock` JSON `{pid, name, base_sha, started}`; pid = the `claude` ancestor found by
  walking `/proc` (X1 trap: `getppid()` is a dying `sh -c`, which handed two sessions the same slot).
  Busy ⇔ pid alive. `flock` only on `alloc.mutex` during allocation. `WorktreeRemove` never fired in 5
  runs, so nothing depends on it.
- **Recycle rule (at allocation, never at exit):** a dead-owner slot is reset only if clean **and** its
  HEAD is an ancestor of origin/main. Otherwise it is *rescued first*: dirty files committed to
  `rescue/<name>-<utc>`, pushed to origin, recorded in the seat's ledger shard; then reset. An OOM-killed
  agent loses nothing and strands nothing locally.
- **Full pool:** hook exits 1 with "pool full: slots held by pids …" (measured); the seat runs the task
  without isolation if it is a quick single-path edit, otherwise queues it. Read-only subagents never
  take a slot.
- **Landing:** inside the slot, plain `git pull --rebase origin main && git push origin HEAD:main`
  (X1: recycled slots race origin; rebase is required and sufficient). Slots never commit DLLs.

### 2.3 What D:\ becomes

`D:\Luke\dev\RimMandrake` = **read mirror, detached at origin/main, no writers.**
- Updated by one systemd user timer (5 min) plus an on-demand `./mirror sync` FOUNDRY runs before a
  deploy: `git fetch && git checkout --detach origin/main`. Safe because nobody edits it; a
  `PreToolUse` hook refuses Write/Edit and `git commit|add|reset|checkout|stash` targeting that path.
- **Callers that need a Windows-drive path:**
  - `codex.exe` (GPT consults, `skills/generating-images/scripts/codex_image.py`, the artpipe codex
    worker): **fails** from an ext4 cwd and **hangs** reading `\\wsl.localhost` paths (measured). They
    run with cwd and inputs in `D:\Luke\dev\_rmscratch\codex\<job>\` (untracked, outside any repo):
    copy inputs in, run, copy outputs back to the caller's clone.
  - `dotnet.exe` builds (`C:\Users\Mandrake\.dotnet\dotnet.exe`; `selftest_aftermath.py` already
    converts to a D-drive path): **UNMEASURED from a UNC cwd.** Phase 0 probes it. If it works, FOUNDRY
    builds in its clone; if not, it builds in `D:\Luke\dev\_rmbuild\` (rsync of the project dir from
    its clone, build, copy DLL + `.srchash` back; the stamp is project-relative, so it survives).
  - artpipe daemon: today `cd /mnt/d/Luke/dev/RimMandrake && python3 …/artpipe/artpiped.py`, writing
    queue JSON into git. Its queue state moves to `D:\Luke\dev\_artpipe\` (untracked); how finished art
    reaches `src/` must be read from `artpiped.py` before Phase 2b moves it.
- Already fine from ext4 (measured): `python.exe` bridge scripts (keep passing relative paths),
  `powershell.exe`. `deploy_custom_mods.py` resolves ROOT from `__file__` and writes
  `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods` via `/mnt/c` — works from any clone.
  `cmd.exe` falls back to `C:\Windows` (only `start steam://` uses it; cwd-independent).

### 2.4 Generated artifacts leave git

| artifact | fate | regenerated by | consumer |
|---|---|---|---|
| `infrastructure/state/queue/{BENCH,FOUNDRY,HUMAN}.md` | gitignore, `rm --cached` | `post-merge`/`post-rewrite`/`post-checkout` hook in every clone runs `rimflow render -- --overwrite-queues`; `rimflow next/show` already read the ledger | agents; owner via rimflow or the hub Artifact; **no longer browsable on github.com** |
| `Transient/codebase_health{.html,.json,_artifact.html}` | gitignore | existing post-commit heartbeat (15-min rule) | owner via the published Artifact (already cross-machine) |
| `infrastructure/state/codebase_health_last.json` | gitignore (per-machine state) | same | generator only |
| `infrastructure/dashboards/hub/data/*.json` (regenerable) | gitignore | `regen_hub.py` (seconds) | the hub Artifact publish |
| `items/DIRTY_CODE_REVIEW_STANDING_LOOP_1.md` (generated part) | split: prose stays, generated table moves to a gitignored view | its generator | agents |
| `infrastructure/artpipe/{pending,active,done,failed}/` | leave git → `D:\Luke\dev\_artpipe\` | artpipe daemon | daemon, `fill_queue.py` |
| `infrastructure/state/CODE_REVIEW_STATUS.json` | **not derived** — it is a record. Becomes append-only `state/code_review/<SEAT>.jsonl` (`path, sha256, verdict, ts`), current state = last record per path | `code_review_status.py` writes records | `check`, health map |

### 2.5 Ledger and inboxes

- **Ledger: `merge=union` on per-seat shards, now.** Measured 0 conflicts (E2), same replay result as
  one-file-per-event (X2b), zero migration, readers already merge shards. Line in `.gitattributes`:
  `infrastructure/state/ledger/events/*.jsonl merge=union`. Preconditions, checked in Phase 0: every
  event one line with a trailing newline, readers key by `id` and order by timestamp not file position,
  duplicate `id` with identical content deduped. One-file-per-event is rejected for the ledger: it buys
  nothing measured and multiplies tracked files at ~250 events/day. Frozen `events.jsonl` untouched.
- **`LESSONS_INBOX.md`: one file per lesson** (`infrastructure/state/lessons/<utc>-<seat>-<slug>.md`),
  rendered view gitignored. Union is wrong here: curation deletes lines and union resurrects them.

### 2.6 `./publish`

In owned clones, plain git replaces it. Kept as a thin wrapper so the command agents know survives:
`./publish -m … <paths>` = `git commit <paths>` + pull --rebase + push + retry + `PUBLISHED <HEAD>`.
The plumbing path stays only for emergency publishing from somewhere with no owned clone, with
per-path 3-way replaced by `merge-tree --write-tree` (E3: rc 0/1, renames carried, zero worktree side
effects) and a `source sha → accepted sha` receipt the handoff gate reads. **Retire `--catchup`,
`--sync` and `shared_sync.py`**: they exist only to move a multi-writer tree, which no longer exists.

### 2.7 DLL / `.srchash`

`.gitattributes`: `*.dll binary` and `*.dll.srchash -merge`. Only FOUNDRY's clone commits
`Assemblies/*.dll` (hook refuses elsewhere); slots and BENCH commit source only. On a source rebase
FOUNDRY rebuilds; `block_dll_source_mismatch.py` keeps enforcing on push. Removes the 71-hit class.

## 3. Jujutsu

**Verdict: no adoption and no pilot in RimMandrake.**
- Does not fix the actual slowness: on drvfs `jj st` 17.8–19.3 s, *worse* than git's 10.3 s (E5). On
  ext4 its 0.02 s gain over git's 0.04 s is irrelevant.
- Ignores `.gitattributes` and git hooks (research §2): the union fix and the whole push-time guard
  layer (`block_dll_source_mismatch.py` et al.) vanish under jj.
- Shared operation log: plain `jj undo` in ws1 undid ws3's commit (E4, measured). `--allow-backwards`
  push dropped 7–9 of 20 updates with **zero reported failures**; repo-wide `main` bookmark conflicts;
  `jj abandon` tried to delete remote main.
- Auto-tracks untracked files (2,250 here) on every command, including `status`.
A pilot makes sense only in a small single-agent repo, after this plan lands, if at all.

## 4. Migration plan

| # | phase | seat | reversible by | success bar |
|---|---|---|---|---|
| 0 | Baseline + probes: daily count of rebase stops / `./publish` refusals / ledger-sync commits; `git status` latency per tree; `dotnet.exe` build from a `\\wsl.localhost` cwd; rimflow reader dedupe/order under union | BENCH (probe), FOUNDRY (dotnet) | n/a | numbers recorded in this doc |
| 1 | **Untrack generated artifacts (§2.4 rows 1–4) + `.gitattributes` union on ledger shards + render hooks** — one commit | FOUNDRY (owns `src/`, rimflow) | `git rm` the attribute, re-add files | ledger-sync commits <10/day (from ~34); 0 conflicts on those paths for 3 days; replay K=5 ≤ 15% |
| 2a | `CODE_REVIEW_STATUS` → records; lessons → one file each; DIRTY_LOOP table split | FOUNDRY | revert commit; old file kept frozen | 0 conflicts on those paths for 7 days |
| 2b | artpipe queue state out of git, after reading how outputs land | FOUNDRY | move dirs back | `git status` in mirror shows 0 artpipe churn |
| 3 | BENCH clone on ext4; owner relaunches BENCH there; memory dir carried over | BENCH + owner (launch) | relaunch in D:\ | `git status` <0.5 s; a full day of plain pull --rebase with ≤1 manual resolution |
| 4 | FOUNDRY clone on ext4 + build route from Phase 0; DLL single-writer rule | FOUNDRY + owner (launch) | relaunch in D:\ | build + deploy from clone proven once; deploy records source sha |
| 5 | Pool hook live, 3 slots/seat, rescue refs | BENCH (hook), each seat adopts | remove hook from settings | ≤6 pool worktrees; 0 new `.claude/worktrees/`; 0 local-only commits in dead slots |
| 6 | Drain D:\ (below), freeze it as mirror, timer, codex scratch dir | BENCH | delete the freeze hook | 0 worktrees on drvfs; 257 unique commits reachable from origin refs |
| 7 | Retire `--catchup`/`--sync`/`shared_sync.py`; rewrite `block_shared_tree_merge.py` as "refuse writes to the mirror"; CHARTER § Git, CLAUDE.md § Git, `parallel-agent-worktrees`/`git-efficiency` skills | BENCH | revert | no doc names a retired verb (grep) |

Phase 1 is first because it is the largest measured payoff (≈30 points of K=5 conflict rate) for one
reversible commit with no relaunch.

## 5. What it costs / what breaks

- **Windows consumers:** `codex.exe` callers must stage through `D:\Luke\dev\_rmscratch\codex\` (code
  change in `codex_image.py` and the artpipe worker). `dotnet.exe` builds possibly through
  `D:\Luke\dev\_rmbuild\`. Anything opening repo files in Explorer (`show.sh`) gets
  `\\wsl.localhost\Ubuntu\home\mandrake\rm\…` paths or the mirror. Owner-facing paths in docs change.
- **Claude harness:** auto-memory is keyed by project path
  (`~/.claude/projects/-mnt-d-Luke-dev-RimMandrake/memory/`) — a session launched in
  `/home/mandrake/rm/bench` gets a *new, empty* memory dir; it must be symlinked to the old one before
  the first launch. `settings.local.json`, `CLAUDE_PROJECT_DIR`-relative hooks, Waypoint/Lodestar
  registry entries and the `~/dev` symlink point at D:\ and need the new path.
- **Hooks:** `block_shared_tree_merge.py` (path-matches the main worktree, still names `/mnt/d/Luke/dev/Rimworld`) → rewritten;
  `block_blanket_git_stage.py` and `queue_lint.py` (shared-index assumptions, `is_generated`) → keep,
  update generated list; `block_dll_source_mismatch.py` → keep, adds the FOUNDRY-only rule;
  `warn_unclosed_queue_item.py`/`warn_close_live_proof_owed.py` match `git` text → unaffected.
  `.git/hooks/post-commit` is a manual symlink per clone → each new clone installs it (set
  `core.hooksPath src/RimMandrake/Utils/git_hooks` instead).
- **Owner on another machine:** queue views disappear from github.com; he reads them via rimflow in
  his Mac clone or the hub Artifact.
- **Draining the 132 worktrees / 68 unmerged branches (257 unique commits):** one script, read-only
  classification first: (a) every commit patch-equal or content-equal upstream (`git cherry` plus
  `./publish`'s content check, which caught one `git cherry` missed) → delete branch, remove worktree;
  (b) anything else → push branch to `refs/heads/archive/<branch>` on origin, then remove the worktree
  (never `--force`; dirty worktrees get a `rescue/` commit first). Nothing is reconciled into main by
  inference — GPT's warning that ancestry ≠ acceptance. Run it from ext4 against the D:\ repo with a
  per-worktree timeout (the drvfs dry run exceeded 10 min).
- **The shared tree's 10 local commits:** 9 already upstream by content; `e55ff18da` (northstar)
  is not. `./publish --commit e55ff18da`, verify `merge-base --is-ancestor` on the result, then the
  freeze resets D:\ to detached origin/main. The 2,250 untracked files and uncommitted edits are copied
  to `D:\Luke\dev\_rm_shared_tree_leftovers_2026-10\` (tar, kept until the owner says delete) before
  the mirror's first checkout.
- **Disk:** 2 clones × ~7 G + 6 slots × 4.1 G ≈ 40 G on ext4; drvfs frees ~124 × 4 G.

## 6. Decisions for the owner

1. **Run Phase 1 now** — untrack the generated queue views/health/hub data and union-merge the ledger
   shards; cost: `queue/*.md` no longer browsable on github.com. Recommend **yes**.
2. **Move both seats to ext4 clones and make `D:\Luke\dev\RimMandrake` a no-writer mirror of
   origin/main** (you relaunch each window once; BENCH first). Recommend **yes**.
3. **Subagent pool: 3 persistent full slots per seat (6 total), queue when full.** Recommend **yes**;
   alternative is 2/seat if RAM pressure shows.
4. **Archive, don't review, the 68 unmerged branches** — push each to `archive/*` on origin and
   remove the worktrees. Recommend **yes**.
5. **No Jujutsu in RimMandrake, not even a pilot.** Recommend **yes**.
