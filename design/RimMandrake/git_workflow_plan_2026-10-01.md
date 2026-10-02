# RimMandrake git workflow — integrated plan (2026-10-01)

Status: DRAFT, revised 2026-10-02 against two reviews (`git_plan_gpt_review_2026-10-02.md`,
`git_plan_literature_check_2026-10-02.md`; dispositions in §7). Nothing here is implemented. Inputs:
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

- **Push ambiguity** (client timed out, remote may have accepted): before any retry, `git fetch origin`
  and `git merge-base --is-ancestor HEAD origin/main`; ancestor ⇒ it landed, record it and stop.
- **Who may advance `main`** is the one open value choice (§6, choice 1). The pool is built so every
  option works: slots always push a submission ref `refs/heads/submit/<seat>/<name>` first; under the
  recommended option the seat lands its own slots' submissions (`git fetch` → `rebase` → `push
  HEAD:main` → delete the submit ref), so only the two seat clones ever write `main`.

### 2.2 Subagent worktree pool

- **Mechanism:** project `WorktreeCreate` hook (X1's `/home/mandrake/wt/x1/pool_hook.py`, measured
  end-to-end on CC 2.1.285). Real stdin is `cwd` + `name` (+`prompt_id`), not the documented
  `base_path`/`worktree_name`; stdout line 1 = path; non-zero exit = clean Agent-tool error.
- **Placement/size:** `/home/mandrake/rm/pool/<seat>/slot{N}` — **start at 2 slots per seat, 4 total**,
  each a linked worktree of that seat's clone. X1 measured pool-full behaviour, not throughput, RAM or
  queue latency, so no number is proven; 2 is the smaller safe start. The hook appends one telemetry line
  per allocation to `/home/mandrake/rm/pool/telemetry.jsonl` (`ts, seat, slot, outcome alloc|full|rescue,
  wait_s`, plus `MemAvailable`). **Raise to 3/seat** when a seat logs ≥3 `full` outcomes a day on 3
  consecutive days *and* `MemAvailable` never fell below 8 GiB in that window; lower to 1 if it did.
  **Full checkouts**, persistent: the 11 s / 4.1 G cost is paid once per slot; recycling is
  `git checkout -B agent/<name> origin/main`, an ext4 delta. Sparse is rejected as default because the
  hook cannot know which paths an agent will touch and builds need all of `src/`.
- **Ownership:** `slotN.lock` JSON `{pid, pid_start, session_id, transcript_path, name, generation,
  base_sha, started}`. `pid` = the `claude` ancestor found by walking `/proc` (X1 trap: `getppid()` is a
  dying `sh -c`); `pid_start` = field 22 of `/proc/<pid>/stat`; `session_id`/`transcript_path` come from
  the hook's real stdin (X1); `generation` increments on every allocation. **Busy ⇔ pid alive AND its
  start time equals `pid_start`** (defeats PID reuse) **OR any process has its cwd or an open file under
  the slot** (`/proc/*/cwd`, `/proc/*/fd` scan — catches a descendant still writing after its parent
  died). Each allocation also runs `git worktree lock --reason "<session_id> gen <n>"` so git and
  Claude Code's own sweep leave a held slot alone (docs: the built-in sweep skips locked worktrees);
  recycle unlocks first. `flock` only on `alloc.mutex` during allocation. `WorktreeRemove` never fired in
  5 runs, so nothing depends on it.
- **Recycle rule (at allocation, never at exit):** a dead-owner slot is reset only if clean **and** its
  HEAD is an ancestor of origin/main (or of its own landed submit ref). Reset is `git checkout -B` +
  `git clean -fd` — ignored `bin/`/`obj/` stay as a warm build cache; slots never commit DLLs, so a stale
  output can mislead only a local build, which MSBuild's incremental check rebuilds.
- **Dirty or unlanded dead slot → rescued LOCALLY, never pushed.** The hook snapshots it into the seat
  clone as `refs/rescue/<seat>/<name>-<utc>` (a commit of tracked changes plus untracked non-ignored
  files ≤5 MB each; ignored files and anything larger are listed by path in the commit message, not
  stored), then classifies each path — `source`, `doc`, `generated` (§2.4 list), `binary`,
  `suspect-secret` (name/content pattern: `*.pem`, `id_*`, `token`, `.env`) — and writes one ledger event
  `rescue` with the ref and class counts. Then it resets the slot. `rimflow next` lists open rescues to
  the seat, which lands, cherry-picks or drops each one by hand; nothing auto-publishes. Rescue refs are
  kept 30 days, then a weekly sweep lists (never deletes) any still unresolved. **This path was written
  but never exercised (X1 UNMEASURED); Phase 7 cannot go live until a test kills an agent mid-edit in a
  slot and the rescue ref is shown to hold the edit.**
- **Full pool:** hook exits 1 with "pool full: slots held by pids …" (measured); the seat runs the task
  without isolation if it is a quick single-path edit, otherwise queues it. Read-only subagents never
  take a slot.
- **Landing:** inside the slot, `git pull --rebase origin main` (X1: recycled slots race origin; rebase is
  required and sufficient), then push to `submit/<seat>/<name>` (§2.1); who moves it onto `main` is §6
  choice 1. Slots never commit DLLs.
- **Isolation trap (Claude Code docs):** a slot must be reached by its own path, never by `cd` into the
  seat clone; Claude Code refuses edits whose git identity resolves into the main checkout, and never
  resumes into `\\wsl.localhost` spellings.

### 2.3 What D:\ becomes

`D:\Luke\dev\RimMandrake` = **plain exported tree of origin/main, no `.git`, no writers.**
- **No index or lock lives on drvfs.** Git on a 9p/drvfs mount has a documented index-corruption and
  transient-`index.lock` class (microsoft/WSL#11619; `core.preloadindex` over 9p), and the freeze would
  otherwise run checkouts there concurrently with Explorer/Steam/antivirus readers. So the mirror's git
  dir is a bare repo on ext4, `/home/mandrake/rm/mirror.git` (fetch-only), and the tree is written with
  `git --git-dir=/home/mandrake/rm/mirror.git --work-tree=/mnt/d/Luke/dev/RimMandrake checkout -f
  --detach origin/main`: index on ext4, only changed files rewritten on D:\, same `core.autocrlf` as the
  seat clones so the export carries identical bytes. The old `D:\…\RimMandrake\.git` is renamed to
  `D:\Luke\dev\_rm_old_git_2026-10\` after the drain (§5) and kept until the owner says delete.
- Updated by one systemd user timer (5 min) plus an on-demand `./mirror sync` FOUNDRY runs before a
  deploy. Both take `flock /home/mandrake/rm/mirror.lock` (non-blocking for the timer: a run already in
  progress means skip), so they cannot race. A failed checkout leaves the previous tree plus a
  `MIRROR_STALE` marker file the next run clears; readers of the mirror tolerate a stale tree.
- Write guard: a `PreToolUse` hook refuses Write/Edit and every git verb targeting that path. Its
  first, narrower form ships in Phase 1 while seats still live there (§4).
- **Callers that need a Windows-drive path:**
  - `codex.exe` (GPT consults, `skills/generating-images/scripts/codex_image.py`, the artpipe codex
    worker): **fails** from an ext4 cwd and **hangs** reading `\\wsl.localhost` paths (measured). They
    run with cwd and inputs in `D:\Luke\dev\_rmscratch\codex\<job>\` (untracked, outside any repo):
    copy inputs in, run, copy outputs back to the caller's clone.
  - `dotnet.exe` builds: **decided — rsync to a Windows directory is the default route.** FOUNDRY
    rsyncs the mod's project dir from its clone to `D:\Luke\dev\_rmbuild\<Mod>\`, runs
    `C:\Users\Mandrake\.dotnet\dotnet.exe build` there, and copies DLL + `.srchash` back (the stamp is
    project-relative, so it survives). Evidence: the UNC-cwd route has documented failures in cmd.exe,
    the dotnet SDK, NuGet and MSBuild (dotnet/sdk#19169, NuGet/Home#13989, dotnet/msbuild#7001), so it
    is not probed. A Linux dotnet SDK is rejected for now, measured 2026-10-02: none is installed in WSL
    (`~/.dotnet` absent, no `dotnet` on PATH); the only SDK is the Windows user-local 8.0.423; and the 40
    csproj files carry **104** hardcoded `RimWorldManaged` = `C:\Program Files (x86)\…\Managed` paths,
    so a Linux build needs a property override across all of them plus a second, unproven toolchain
    producing shipped DLLs. Cost accepted: each build pays drvfs I/O for one project dir, not the repo.
  - artpipe daemon: today `cd /mnt/d/Luke/dev/RimMandrake && python3 …/artpipe/artpiped.py`, writing
    queue JSON into git. Its queue state moves to `D:\Luke\dev\_artpipe\` (untracked); how finished art
    reaches `src/` must be read from `artpiped.py` before Phase 5 moves it. It must leave before the
    mirror freeze (Phase 6), because the mirror has no writers.
- Already fine from ext4 (measured): `python.exe` bridge scripts (keep passing relative paths),
  `powershell.exe`. `deploy_custom_mods.py` resolves ROOT from `__file__` and writes
  `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods` via `/mnt/c` — works from any clone.
  `cmd.exe` falls back to `C:\Windows` (only `start steam://` uses it; cwd-independent).

### 2.4 Generated artifacts leave git

**Rule: readers render on read; no git hook regenerates anything.** Hook-driven regeneration is
rejected on three counts: `post-merge`/`post-checkout` never fire for plumbing (`./publish`'s temp
index) or for the mirror's `checkout -f` (githooks docs); hooks are not cloned, and Claude Code's
worktree creation rewrites a shared `core.hooksPath` to an absolute path, silently disabling
repo-managed hooks for the whole clone (anthropics/claude-code#66993); and `git rm --cached` deletes the
file from every other checkout on its next pull, so any checkout whose hook did not run is left with
nothing. So every consumer of a generated view either computes it (`rimflow next/show` already read
the ledger) or calls a render that writes the gitignored file *then* reads it (`rimflow queue <seat>`
= `render --overwrite-queues` + print). A view on disk is a cache; nothing trusts it without re-rendering.
Rollback is reverting the untrack commit, because no consumer depends on the tracked copy.

| artifact | fate | regenerated by | consumer |
|---|---|---|---|
| `infrastructure/state/queue/{BENCH,FOUNDRY,HUMAN}.md` | gitignore, `rm --cached` | on read: `rimflow queue <seat>` renders then prints; `rimflow next/show` already read the ledger | agents; owner via rimflow or the hub Artifact; GitHub visibility is §6 choice 2 |
| `Transient/codebase_health{.html,.json,_artifact.html}` | gitignore | a systemd user timer (15 min) in FOUNDRY's clone, replacing the post-commit heartbeat — no git hook | owner via the published Artifact (already cross-machine) |
| `infrastructure/state/codebase_health_last.json` | gitignore (per-machine state) | same | generator only |
| `infrastructure/dashboards/hub/data/*.json` (regenerable) | gitignore | `regen_hub.py` (seconds) | the hub Artifact publish |
| `items/DIRTY_CODE_REVIEW_STANDING_LOOP_1.md` (generated part) | split: prose stays, generated table moves to a gitignored view | its generator | agents |
| `infrastructure/artpipe/{pending,active,done,failed}/` | leave git → `D:\Luke\dev\_artpipe\` | artpipe daemon | daemon, `fill_queue.py` |
| `infrastructure/state/CODE_REVIEW_STATUS.json` | **not derived** — it is a record. Becomes append-only `state/code_review/<SEAT>.jsonl` (`path, sha256, verdict, ts`), current state = last record per path | `code_review_status.py` writes records | `check`, health map |

### 2.5 Ledger and inboxes

- **Ledger: `merge=union` on per-seat shards, now.** Measured 0 conflicts (E2), same replay result as
  one-file-per-event (X2b), zero migration, readers already merge shards. Line in `.gitattributes`:
  `infrastructure/state/ledger/events/*.jsonl merge=union`. **Decided: union plus two permanent
  invariants, not per-day or per-event files.** Union does not dedupe, gives no order, and keeps both
  old and new line when one side edits in place (literature §2), so it is safe only if these hold
  forever, not just at a Phase 0 check:
  1. **Reader invariant** in the single reader (`rimflow` `model.read()`): parse every line; key by `id`;
     identical duplicate → collapse; order by event timestamp, then `id`, never file position.
  2. **Lint** (`ledger_lint.py`, run by `run_selftests.py` and by a `PreToolUse` guard on `git push`):
     fails on a malformed line, a missing trailing newline, a duplicate `id` with *different* content,
     or any diff to a shard that is not a pure append (a changed or removed line).
  The only real exposure is two windows of one seat sharing a shard; per-seat sharding already confines
  it. Per-day files are rejected: they bound a file's size, not the duplicate/edit hazard, which the
  lint covers either way. One-file-per-event is rejected: it measured the same as union (X2b) and adds
  ~250 tracked files/day. Frozen `events.jsonl` untouched. Concurrent claims of one item both survive a
  union; the reader resolves them deterministically (earliest timestamp wins) and `rimflow next` tells
  the loser.
- **`LESSONS_INBOX.md`: one file per lesson** (`infrastructure/state/lessons/<utc>-<seat>-<slug>.md`),
  rendered view gitignored. Union is wrong here: curation deletes lines and union resurrects them.

### 2.6 `./publish`

In owned clones, plain git replaces it. Kept as a thin wrapper so the command agents know survives:
`./publish -m … <paths>` = `git commit <paths>` + pull --rebase + push (submit ref or `main` per §6
choice 1) + ambiguity check (§2.1) + retry + `PUBLISHED <sha>`. **The plumbing path is deleted, not
kept for emergencies** — two landing policies are how drift returns. With no owned clone, the remedy is
to make one (`git clone` onto ext4). **Retire `--catchup`, `--sync` and `shared_sync.py`**: they exist
only to move a multi-writer tree, which no longer exists. (`merge-tree --write-tree`, E3, stays the
tool for any future integrator that must test a merge without a worktree.)

### 2.7 DLL / `.srchash`

`.gitattributes`: `*.dll binary` and `*.dll.srchash -merge`. Only FOUNDRY's clone commits
`Assemblies/*.dll` (hook refuses elsewhere); slots and BENCH commit source only. On a source rebase
FOUNDRY rebuilds; `block_dll_source_mismatch.py` keeps enforcing on push. Removes the 71-hit class.

## 3. Jujutsu

**Verdict: not now — no adoption and no pilot in RimMandrake while this plan lands.** Revisit only if
agents measurably lose time shaping parallel changes into history, which is not this repo's problem.
- Does not fix the actual slowness: on drvfs `jj st` 17.8–19.3 s, *worse* than git's 10.3 s (E5). On
  ext4 its 0.02 s gain over git's 0.04 s is irrelevant.
- Ignores `.gitattributes` and git hooks (research §2): the union fix and the whole push-time guard
  layer (`block_dll_source_mismatch.py` et al.) vanish under jj.
- Shared operation log: plain `jj undo` in ws1 undid ws3's commit (E4, measured). `--allow-backwards`
  push dropped 7–9 of 20 updates with **zero reported failures**; repo-wide `main` bookmark conflicts;
  `jj abandon` tried to delete remote main.
- Auto-tracks untracked files (2,250 here) on every command, including `status`.
## 4. Migration plan

Order rule: **end the shared writable D:\ tree first, then cut conflicts.** The destructive incidents
(215 files lost, staged files eaten, `checkout origin/main -- src`) all came from many writers in the
D:\ tree; conflict rate costs time, that tree costs work. So D:\ is guarded at once and both seats
leave it by Phase 3, before any conflict work.

| # | phase | seat | reversible by | success bar |
|---|---|---|---|---|
| 0 | Baseline: daily count of rebase stops / `./publish` refusals / ledger-sync commits; `git status` latency per tree; Windows-path audit (every hardcoded `/mnt/d/Luke/dev/RimMandrake` or `D:\Luke\dev\RimMandrake` in `src/`, `skills/`, `.claude/`, `~/.claude/` listed with its fix); confirm rimflow reader semantics (§2.5) on today's shards | BENCH | n/a | numbers and the path list recorded in this doc |
| 1 | **Guard D:\ now:** extend the `PreToolUse` git guard to refuse, on the D:\ tree, `git checkout <ref> -- <path>`, `git restore --source`, `git worktree add` anywhere under `/mnt/d`, and every whole-tree reset/stash/clean it already refuses | BENCH | remove the hook lines | the three named incident commands are refused in a fresh window (hooks added mid-session do not fire) |
| 2 | BENCH clone on ext4; memory dir symlinked and settings/hook paths repointed **before** the first launch; owner relaunches BENCH there | BENCH + owner (launch) | relaunch in D:\ | `git status` <0.5 s; a full day of plain pull --rebase with ≤1 manual resolution |
| 3 | FOUNDRY clone on ext4 + rsync build route (§2.3) + DLL single-writer rule; then the D:\ guard widens to refuse **all** Write/Edit/git on D:\ except the Phase 6 drain script and `./mirror sync`, matched by name | FOUNDRY + owner (launch) | relaunch in D:\ | build + deploy from clone proven once; deploy records source sha; 0 Claude writes to D:\ for 3 days |
| 4 | **Untrack generated views (§2.4 rows 1–4) + render-on-read + union on ledger shards + reader invariant + ledger lint** — one commit | FOUNDRY (owns `src/`, rimflow) | revert the commit | before shipping: X2 harness re-run with exactly this path set, expected ≤15.0% at K=5 (below); live: ledger-sync commits <10/day (from ~34) and 0 conflicts on those paths for 3 days |
| 5 | `CODE_REVIEW_STATUS` → records; lessons → one file each; DIRTY_LOOP table split; artpipe queue state out of git (after reading how outputs land) | FOUNDRY | revert commit; old file kept frozen; move dirs back | X2 re-run with the full §2.4–2.5 path set ≤13.6% at K=5; 0 conflicts on those paths for 7 days |
| 6 | Drain D:\ (§5), freeze it as the exported mirror (§2.3), flocked timer, codex scratch dir | BENCH | restore the renamed `.git` | 0 worktrees on drvfs; every one of the 257 unique commits reachable from an origin ref; no `.git` under `D:\Luke\dev\RimMandrake` |
| 7 | Pool hook live at 2 slots/seat, telemetry, local rescue refs, submit refs, `git worktree lock` — only after the kill-mid-edit rescue test passes | BENCH (hook), each seat adopts | remove hook from settings | rescue test passes; ≤4 pool worktrees; 0 new `.claude/worktrees/`; 0 slot pushes to `main` unless §6 choice 1 says otherwise |
| 8 | Retire `--catchup`/`--sync`/`shared_sync.py` and the plumbing publish path; CHARTER § Git, CLAUDE.md § Git, `parallel-agent-worktrees`/`git-efficiency` skills | BENCH | revert | no doc names a retired verb (grep) |

**Phase 4's bar is now scoped to Phase 4.** The 13.6% replay figure (X2 column c) assumes queue views,
health *and* `CODE_REVIEW_STATUS` removed and *both* ledger and `LESSONS_INBOX` union-merged. Phase 4
does neither of the last two. Adding back their K=5 hits (15 + 32 = 47 commits, worst case all
otherwise clean) bounds Phase 4 at **≤ (463 + 47) / 3,403 = 15.0%** (K=1 ≤ 145 / 3,403 = 4.3%), against
43.6% today. It also untracks `codebase_health_last.json` and hub data that column c did not, so the
true figure is lower; the re-run measures it. 13.6% is Phase 5's bar.

## 5. What it costs / what breaks

- **Windows consumers:** `codex.exe` callers must stage through `D:\Luke\dev\_rmscratch\codex\` (code
  change in `codex_image.py` and the artpipe worker). `dotnet.exe` builds go through
  `D:\Luke\dev\_rmbuild\` (rsync per build). Anything opening repo files in Explorer (`show.sh`) gets
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
  `.git/hooks/post-commit` (the health heartbeat) is **retired**, replaced by the timer in §2.4; no
  clone installs git hooks and nothing sets `core.hooksPath` (Claude Code rewrites it, #66993). Every
  guard that matters is a Claude `PreToolUse` hook, which Claude Code installs per project, not per clone.
- **Owner on another machine:** under §6 choice 2's recommended option queue views disappear from
  github.com; he reads them via rimflow in his Mac clone or the hub Artifact.
- **Draining the 132 worktrees / 68 unmerged branches (257 unique commits):** one script, read-only
  classification first: (a) every commit patch-equal or content-equal upstream (`git cherry` plus
  `./publish`'s content check, which caught one `git cherry` missed) → delete branch, remove worktree;
  (b) anything else → push it as tag `refs/tags/archive/<branch>` on origin, then remove the worktree
  (never `--force`; a dirty worktree's edits are first committed to a local `refs/rescue/…` ref, classified
  as in §2.2, and the commit is archived the same way — after classification, never blind). Tags, not
  `refs/heads/archive/*`: branches would land in every clone's and slot's default fetch and clutter
  GitHub's branch list; a tag on an unmerged commit is not auto-followed by a normal fetch, is visible
  on GitHub, and is standard archive practice. **Archive tags are kept indefinitely** (68 refs cost
  nothing; reftable-scale costs start at tens of thousands) and only the owner deletes them; slot rescue
  refs keep the 30-day rule in §2.2. **Archived means reachable, not accepted:** nothing is reconciled
  into main by inference (ancestry or patch similarity ≠ acceptance); classification of the archive is
  later, per-item work. Run it from ext4 against the D:\ repo with a per-worktree timeout (the drvfs dry
  run exceeded 10 min).
- **The shared tree's 10 local commits:** 9 already upstream by content; `e55ff18da` (northstar)
  is not. `./publish --commit e55ff18da`, verify `merge-base --is-ancestor` on the result, then the
  freeze resets D:\ to detached origin/main. The 2,250 untracked files and uncommitted edits are copied
  to `D:\Luke\dev\_rm_shared_tree_leftovers_2026-10\` (tar, kept until the owner says delete) before
  the mirror's first checkout.
- **Disk:** 2 clones × ~7 G + 4 slots × 4.1 G + bare mirror ~3.2 G ≈ 34 G on ext4 (≈42 G at 3 slots/seat);
  drvfs frees ~124 × 4 G.


## 6. Owner choices

Everything technical in this plan is decided above with its evidence (phase order, build route, ledger
merge, mirror form, slot size and ownership, rescue, archive form, Jujutsu). Two choices are about what
you value, not about facts, so they stay yours. Your hands are needed once besides: relaunching the
BENCH window (Phase 2) and the FOUNDRY window (Phase 3) in their new folders.

**Choice 1 — who is allowed to put work onto the main line?**

- **A. Each window lands its own helpers' work** *(recommended)*
  - Gain: only the two windows ever write the main line, instead of up to six; nothing new to keep running.
  - Cost: the two windows can still race each other (git retries this safely), and nothing builds or tests work before it lands.
- **B. One checker lands everything**
  - Gain: every change is built and tested before it lands, one at a time, so the main line never breaks and never races.
  - Cost: one more always-on process; each landing waits minutes for its turn, and if the checker is down nothing lands.
- **C. Every helper lands its own work directly** (the old plan)
  - Gain: fastest, simplest, nothing waits.
  - Cost: up to six writers racing the main line, and a broken change lands unchecked.

Recommended A: it removes most of the race for no new machinery, and B can be added later on top of
it without changing how helpers work.

**Choice 2 — should the queue pages stay readable on github.com?**

- **A. No — read them through rimflow or the hub page** *(recommended)*
  - Gain: no queue-page merge conflicts at all, nothing extra to run.
  - Cost: you cannot open the queue pages by browsing github.com; you use the hub page or a clone.
- **B. Yes — a timer posts them to a separate GitHub branch every 15 minutes**
  - Gain: still browsable on github.com, still no conflicts on the main line.
  - Cost: one more timer to keep alive, and the GitHub copy can be up to 15 minutes old.

Recommended A: the hub page already shows the queues on any machine, so B buys little.

## 7. Review dispositions

Sources: **G** = `git_plan_gpt_review_2026-10-02.md`, **L** = `git_plan_literature_check_2026-10-02.md`.

| # | point | src | disposition | where / reason |
|---|---|---|---|---|
| 1 | Slots + seats pushing `main` directly is still a mainline race; add a serialized integration gate | G1, G6 | **Accept in part** | Submit refs built in (§2.1, §2.2) so a gate can be added without changing slots; whether a gate runs is a value trade (latency, one more process) → §6 choice 1 |
| 2 | Auto rescue-push of dead dirty slots is unsafe and unexercised | G2, G§2 | **Accept** | Rescue is local refs only, classified, never pushed; Phase 7 gated on a kill-mid-edit test (§2.2) |
| 3 | Phase 1 success bar overclaims the 13.6% figure | G3 | **Accept** | Phase 4 bar bounded at ≤15.0% from X2's own class counts; 13.6% moved to Phase 5 (§4) |
| 4 | D:\ freeze is too late; guard D:\ and move BENCH early | G4, G§4 | **Accept** | Phase 1 guard, BENCH Phase 2, FOUNDRY Phase 3, full D:\ write refusal from Phase 3 (§4) |
| 5 | Generated views leaving git before consumers migrate is brittle | G5 | **Accept** | Render-on-read; no consumer depends on the tracked copy, so rollback is one revert (§2.4) |
| 6 | PID-only slot ownership (reuse, descendant writers) | G6 | **Accept** | Start time + session id + generation + cwd/fd scan + `git worktree lock` (§2.2) |
| 7 | Emergency plumbing `./publish` keeps two integration policies | G7 | **Accept** | Plumbing path deleted; the fallback is cloning onto ext4 (§2.6) |
| 8 | 3 slots/seat is unproven | G§2, G5.3, L4 | **Accept** | Start 2/seat with telemetry and a stated raise/lower rule (§2.2) |
| 9 | `dotnet.exe` from UNC unproven; make rsync default or use a Linux SDK | G§2, L3 | **Accept rsync default; reject Linux SDK** | No SDK in WSL (measured), 104 hardcoded `C:\` HintPaths in 40 csproj, second toolchain unproven (§2.3) |
| 10 | Union safety not proven in readers | G§2, L2 | **Accept** | Permanent reader invariant + `ledger_lint.py` on selftests and push (§2.5) |
| 11 | Pick union+dedupe or per-day/per-event files | L2 | **Union + dedupe + lint chosen** | Measured 0 conflicts (E2, X2b), zero migration; per-day files bound size, not the duplicate hazard (§2.5) |
| 12 | Archive ≠ acceptance | G§2, G5.4 | **Accept** | Stated: archived means reachable, classification is later per-item work (§5) |
| 13 | Stale task-claim protocol missing | G§3 | **Accept** | Reader resolves concurrent claims by earliest timestamp; `rimflow next` tells the loser (§2.5) |
| 14 | Slot recovery for untracked/ignored/large/generated/partial files | G§3 | **Accept** | Untracked ≤5 MB stored, larger and ignored listed by path, each path classified (§2.2) |
| 15 | Push accepted but client timed out | G§3 | **Accept** | Fetch + `is-ancestor` before any retry (§2.1) |
| 16 | Windows path audit beyond listed tools | G§3 | **Accept** | Phase 0 audit of hardcoded D:\ paths with fixes (§4) |
| 17 | Claude memory/settings/hooks before first ext4 launch | G§3 | **Accept** | Phase 2 does it before the relaunch (already in §5; now in the phase row) |
| 18 | Rollback after `git rm --cached` | G§3 | **Accept** | Revert one commit; nothing reads the tracked copy (§2.4) |
| 19 | Archive namespace: who deletes, retention, search | G§3, L6 | **Accept** | Tags `archive/*`, kept indefinitely, owner-only deletion; rescue refs 30 days + list-only sweep (§2.2, §5) |
| 20 | Hook distribution via `core.hooksPath` | G§3 | **Reject** | Claude Code rewrites `core.hooksPath` on worktree creation (claude-code#66993); no git hooks remain, guards are `PreToolUse` (§5) |
| 21 | Hook-driven regeneration fragile (hooksPath, plumbing/reset skip hooks); render on read | L1 | **Accept** | §2.4 rule; health heartbeat moves to a timer |
| 22 | Full `.git` mirror on drvfs repeats the 9p index-corruption class; flock the timer | L5 | **Accept** | Bare repo on ext4 + `--work-tree` export; `flock` on timer and sync; old `.git` renamed aside (§2.3) |
| 23 | Mirror autocrlf must match clones | L5 | **Accept** | Same `core.autocrlf` as seat clones (§2.3) |
| 24 | `archive` as `refs/heads/*` bloats every clone's fetch | L6 | **Accept** | Tags instead (§5) |
| 25 | `git clean -fdx` vs `-fd` at recycle unstated | L4 | **Accept** | `-fd`: ignored build output kept as warm cache; slots never commit DLLs (§2.2) |
| 26 | Add `git worktree lock` per slot | L4 | **Accept** | §2.2 |
| 27 | Slots must not be reached via `cd` into the seat clone | L4 | **Accept** | Noted in §2.2 |
| 28 | rsync build reintroduces drvfs I/O | L3 | **Accept as cost** | One project dir per build, not the repo (§2.3) |
| 29 | Jujutsu "not even a pilot" as permanent is too strong | L7 | **Accept** | Softened to "not now", with a revisit condition (§3) |
| 30 | Phase 1 needs consumers of queue views migrated or warned first | G5.1 | **Accept** | Render-on-read means consumers migrate in the same commit (Phase 4) |

## 8. Owner decisions — taken by question card, 2026-10-02 00:10 PDT

- **Choice 1 → A.** Each window lands its own helpers' work; helpers hand in on `submit/` branches and never push the main line. The one-checker gate (B) stays available as a later layer.
- **Choice 2 → A.** Queue pages leave git and are read through rimflow or the hub page; no github.com copy.
