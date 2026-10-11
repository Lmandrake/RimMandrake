# 01 — Handoff corpus audit (2026-10-11)

Scope: `infrastructure/state/handoffs/` (214 files on disk: 213 `*_HANDOFF_*.md` + 1 misfiled item file), `infrastructure/state/LESSONS_INBOX.md`, and `handoff.py --harvest` / `--cull`. All counts below come from python scripts I ran. The scripts and their outputs are in the scratchpad, `/home/mandrake/.seat-tmp/BENCH/claude-1000/-home-mandrake-rm-bench/2f152d1c-c54b-43dc-9d64-f5af5a496986/scratchpad/` (`corpus.py`, `extract.py`, `themes2.py`, `durable.py`, `ptr_report.txt`). That directory is throwaway.

## 0. Instruments run

| command | result |
|---|---|
| `handoff.py --harvest` | **Not read-only.** It *writes* `infrastructure/state/handoffs/harvest_20261011.md`: 1,675 lines covering **88 handoffs with lesson content since 2026-09-25T20:05:04Z**. To keep the tree untouched I moved the file to the scratchpad (`.../scratchpad/harvest_20261011.md`). It is regenerable, so the curation pass can rerun it. |
| `handoff.py --cull` | `nothing to cull: no handoff is superseded + harvest-covered + older than 30 days`. The causes are in §3. |
| `.handoff.json` | `lessons_file` = `infrastructure/state/lessons` + `LESSONS_INBOX.md`, so the dir is drain-aware. `cull_days` uses the default of 30. |

**Corpus census (MEASURED):**
- Files per seat prefix: BENCH 9, BENCH_REBOOT 85, FOUNDRY 23, FOUNDRY_REBOOT 87, MACBENCH 1, MACBENCH_REBOOT 8, plus 1 non-handoff file (`CANON_REINTEGRATION_EXECUTION_1.md`, BENCH 2026-09-04, which handoff.py cannot see).
- Total size **11,468,920 bytes**, median 25 KB, largest 547 KB (`FOUNDRY_HANDOFF_202609271458.md`).
- 🔴 **80% of the corpus bytes is the auto-generated `## Tree state at wrap` / `## Game / bridge / tree state at wrap` dirty-file list** (56% + 24%). In the largest file, 541,707 of ~547,000 chars are tree state. `handoff.py` caps `## Commits` (`commits_cap`) but writes the dirty list with no cap at all (`~/dev/Lodestar/bin/handoff.py` lines 400–414). The lesson sections ("carry forward" + "Traps learned") are only 4% of the bytes.

**LESSONS_INBOX.md (MEASURED):**
- Its header says it is "a gitignored view". That is false: `git ls-files` lists it as tracked, and its last commit was `aefcca607` on 2026-10-02.
- The view is **stale**. It was rendered 2026-10-02 01:01 and holds 169 bullets, while `infrastructure/state/lessons/` now holds **298 lesson files** (+README). 37 of those were filed today, and the seat split is FOUNDRY 132 / BENCH 128 / UNSEATED 35 / MACBENCH 3.
- **No lesson file has ever been deleted** (`git log --diff-filter=D -- infrastructure/state/lessons` is empty). The header's "Last drained 2026-09-23" is the last real curation. handoff.py's last-drain detector finds `013b058d5` (2026-09-25 13:05 PDT, "Curate 2026-09-25 git lessons into skills", −5 lines).

## 1. Recurring themes (3+ handoffs)

How this was measured: 1,081 bullets were extracted from every lesson-bearing section ("carry forward", "Traps learned", "Traps for whoever resumes") of all 213 handoffs. The counts are **distinct handoffs** matching a theme regex (`themes2.py`). Themes marked *broad* match any mention, not just traps, and are inflated. "Durable" was checked by regex across repo `CLAUDE.md`, `infrastructure/state/lessons/` (298), `LESSONS_INBOX.md`, `design/RimMandrake/GIT_WORKFLOW.md`, `skills/` (93 md), `infrastructure/agents/`, the memory dir (198), `~/.claude/skills` and `~/.claude/CLAUDE.md` (`durable.py`).

### Git / shared clone (the owner's named pain point)
| theme | handoffs | since 10-01 | durable where | gap / proposal |
|---|---|---|---|---|
| Shared tree sweeps another writer's staged/dirty files (pathspec, whole-index commit, `git status` path lists incl. `??`) | 33 | 7 | CLAUDE.md Git §, GIT_WORKFLOW, 8 lessons, 4 memory | Recorded in too many places. MERGE into one GIT_WORKFLOW section and delete the 8 lesson files. |
| Worktrees (slow on /mnt/d, dead-agent locks, relativeworktrees breaks SourceLink) | 31 | 9 | 16 lessons, 10 memory, GIT_WORKFLOW | **Worktrees are OFF (owner 2026-10-02)**, so most of these lessons are obsolete. DELETE the worktree how-to lessons; keep only "never". |
| `.git/index.lock` contention / stale lock (incl. Windows git holding it, invisible to pgrep) | 28 | 4 | 5 lessons, 2 memory, global git-efficiency | Not in GIT_WORKFLOW. MOVE a 5-line procedure there (fuser / tasklist.exe check → age → remove). |
| PreToolUse/pre-push hook refuses the whole compound command | 14 | 4 | CLAUDE.md, 3 lessons, 1 skill | KEEP CLAUDE.md line; delete the 3 lessons. |
| Peer `reset --hard` / `--autostash` / refused merge erased work | 13 | 7 | CLAUDE.md, global CLAUDE, GIT_WORKFLOW | Recorded. Still recurring after the clone split, so the remaining cause is helpers inside one clone. Add "helpers never pull" to the subagent brief template. |
| Publication proof (`merge-base --is-ancestor`, cherry-mark, shared_sync lies) | 12 | 3 | CLAUDE.md, GIT_WORKFLOW, 4 lessons | `shared_sync.py` is pre-clone-era tooling, so those 4 lessons are DELETE candidates. |
| Clone lags origin / phantom diffs / drvfs stale reads | 11 | 3 | GIT_WORKFLOW, 2 lessons, memory | KEEP. |
| Ledger jsonl conflict (plumbing, never `--ours`) | 5 | 0 | CLAUDE.md, GIT_WORKFLOW | Solved by per-seat shards. KEEP. |

### Game / bridge / deploy
| theme | handoffs | since 10-01 | durable where | gap / proposal |
|---|---|---|---|---|
| Bridge call "succeeds" but nothing changed, or a wrong/nested JSON key reads as 0 (`list_pawns` health nesting, `get_defs` list fields) | 72 *broad* / 13 narrow | 0 narrow | rimbridge skill (12 skill files), 9 memory | `list_pawns["health"]["hediffs"]` is in 1 skill only. Add a "known response shapes" table to the rimbridge skill. |
| Stale modal / hang / livelock (`search_debug_actions`) | 34 *broad* | 5 | rimbridge, rimworld-debug-testing | Recorded. |
| Minimal-list vs full-list mismatch (manifest `modCount`, quicktest ≠ campaign) | 29 | 5 | 11 skill files, 6 memory | Recorded. |
| Repo ≠ game copy / stale DLL (`Could not find type`, md5 repo vs game) | 8 | 2 | rimworld-deploy (2), 1 lesson | KEEP in rimworld-deploy. |
| csproj `EnableDefaultCompileItems` omission | 5 | 1 | **CLAUDE.md only** + 1 skill | MOVE out of CLAUDE.md into the rimworld-modding C# reference. It is a fact, not a rule. |
| Cold-load timing / `launch_and_wait.sh` exits 0 on timeout | 8 | 1 | 3 skill files, 1 lesson | Recorded. |
| ModsConfig reset to Core-only (corrupted-mods recovery) | 3 | 0 | CLAUDE.md, 4 skill files | Recorded. |
| MayRequire semantics | 10 | 2 | CLAUDE.md, 6 lessons, 18 skill files | Over-recorded. Delete the 6 lesson files once the skill is confirmed to hold them. |

### Subagents
| theme | handoffs | durable | proposal |
|---|---|---|---|
| Forks/subagents exceed brief; subagent verdicts wrong | 11 | memory only (1) | PROMOTE to the `efficient-subagents` skill: a brief must forbid destructive git and restarts explicitly, and a verdict is evidence, not a finding. |
| 600 s watchdog / ending own turn to "wait" | 7 | CLAUDE.md, 2 skill files, 2 lessons, 4 memory | Recorded. |
| `model` param required, including `Explore` | 6 | CLAUDE.md, 2 lessons | Recorded. |

### Measurement instruments / shell
| theme | handoffs | since 10-01 | durable | proposal |
|---|---|---|---|---|
| zsh: no word-split, `"$c:refs"` `:r` modifier, foreground `sleep` blocked | 23 | **11** | CLAUDE.md (word-split only), 5 global skill files | The `:r`-modifier trap is recorded **nowhere** (regex NONE). Still recurring. PROMOTE to a global skill (§4). |
| Stale dump / snapshot / CSV-as-record / `defs.sqlite` 0-byte decoy | 26 | 5 | CLAUDE.md, measuring-large-artifacts | `defs.sqlite` decoy is in 2 skills + memory. KEEP. |
| Windows/WSL bridging (python.exe paths, powershell, tasklist, WSLENV) | 18 | 3 | spread across CLAUDE.md and memory | PROMOTE to the same global shell skill. |
| `pkill -f` / `pgrep -f` match own shell | 13 | 3 | 1 lesson, 4 memory, 1 skill | PROMOTE to the global shell skill. Delete the lesson. |
| `grep -c` / `wc` counts lie | 9 | 1 | CLAUDE.md, measuring-large-artifacts, block_blind_scan hook | Recorded. |
| CRLF from python.exe | 7 | 1 | CLAUDE.md | MOVE to the global shell skill. |

### Disk
| theme | handoffs | since 10-01 | durable | proposal |
|---|---|---|---|---|
| /tmp tmpfs filling (18 GB) and breaking every agent; scratch placement | 17 | 5 | 4 lessons, GIT_WORKFLOW, global CLAUDE | Placement is recorded. **There is no disk monitoring anywhere**: the regex for `df -`/"disk fills" matched NONE, and `src/RimMandrake/Utils/pulse/pulse.py` has no disk metric. This is the owner's telemetry ask (§4). |

### Rimflow / handoff tooling / sheets / art
| theme | handoffs | since 10-01 | durable | proposal |
|---|---|---|---|---|
| Rimflow guards (owner-quote guard refuses mid-turn words, claim refusals, `close --sha`) | 40 narrow | 9 | using-rimflow skill, 4 lessons | KEEP in using-rimflow. Delete the lessons after checking the skill holds them. |
| handoff.py gates (UNPUSHED false alarm on patch-equivalent tree, misfiled with no `.handoff.json`, BRIDGE gate can't tell two BENCH windows apart) | 22 | 5 | CLAUDE.md (BRIDGE), 4 lessons, handoff skill | The UNPUSHED and cherry-mark false alarm belongs to the shared-tree era. Re-measure whether it still fires, then delete. |
| Sheets: rulings never enacted (229 legacy rows), `touchedBySheet` ≠ complete, notes not cleared | 31 *broad* / 6 narrow | 13 / 3 | review-sheets skill (touchedBySheet), memory (sheet enactment, notes) | Memory-only facts (`sheet-enactment-one-pass`, `followed-sheet-notes-must-be-cleared`) should MOVE into `review-sheets`. |
| Art: art already existed / owed install / daemon state | 25 narrow | 1 | CLAUDE.md, `artpipe_state.py find` | Recorded. Trend is down. |

Not recurring (1 handoff): "design scaffolding never carded gets built" (`BENCH_HANDOFF_202609271850`). It is a high-value single lesson but under the 3+ bar.

## 2. Pointer pickup

**Sample:** the last 30 handoffs by commit time, `FOUNDRY_HANDOFF_202610061232` through `BENCH_HANDOFF_202610111523`. They hold **271 `NEXT:` lines**. 201 cite a backticked id, covering **158 distinct ids**, and **70 (26%) cite no id at all**, which breaks the required `` `ID` — state; NEXT: `` form. Every id was checked with `rimflow show`.

| state | ids |
|---|---|
| done | 38 |
| validated | 20 |
| built | 30 (each owes a live leg; not orphaned) |
| dropped / superseded | 3 |
| **open: proposed 23 / ready 2 / doing 10** | **35**, of which **29 are absent from their window's latest handoff**: carried once, then never mentioned again |
| **UNFILED: the id was never a rimflow item** | **32** |

Full per-id list: `.../scratchpad/ptr_report.txt`.

### Orphaned pointers to FILE as items (real work, no item, not carried forward)
- `NORTHSTAR_VALIDATION_V2_RECORD_1` (FOUNDRY 10-06): "NEXT: file it and make both scripts record run_identity". Never filed.
- `SCENE_HARNESS_1` (FOUNDRY 10-09): create `src/RimMandrake/Utils/scenes/` and measure 27 criteria.
- `FLOWWORKS_PIT_CLAMP_LIVE_1` (FOUNDRY 10-08): live `validation_v2.py --live --fresh-map` run owed.
- `WASTELAND_CONTAGION_LIVE_FAILS` (FOUNDRY 10-08): reproduce live per `Transient/acc_biomes_fixes_20261008.md`.
- `DEAD_OR_INERT_SETTINGS` (FOUNDRY 10-08): wire or delete per setting.
- `FLOWWORKS_LIQUID_KITS` (FOUNDRY 10-06): add a feature row to `human_review.py`.
- `CRACKEDLANDS_CHERRYPICKER_LASSO` (FOUNDRY 10-07): set LassoSpawnChance 0 with the game down.
- `RUT_ORPHAN_PNGS` and `FEVERWOOD_UNATTRIBUTED_XML` (FOUNDRY 10-07): a tree-hygiene decision owed.
- `JAWABENCH_DLL_GAME_COPY`, `OLLOPOM_BEAUTY_DEPLOY`, `OLLOPOM_BEAUTY_LIVE_CHECK` (BENCH 10-08..10-11): game-down deploys. Fold them into one `GAME_DOWN_DEPLOY_BATCH` item rather than three.
- `HOSE_PORT_OWNER_QS`, `ROT_REGEN_OPTIONS_SHEET` (BENCH 10-11, latest): owner questions and a sheet awaiting rulings. File both, or keep them as handoff-only if the next wake consumes them.

### Pointers to DROP (state notes or standing instructions, not work)
- `GAME_STATE`, `LANDING`: game state belongs in `./game`.
- `STARWARSRACES_ARMOURY_DEP`: its own text says "NEXT: none".
- `MORNING_QUESTIONS`, `TREE_143_UNCOMMITTED`, `NEW_BUILDS_NOT_RECORDED`, `BIOMES_DEPLOY_PENDING`, `OVERNIGHT_REDRAWS`, `FEVERWOOD_SURPRISES`, `CORPSE_SITE_SAFETY`, `ACCEPTANCE_SITTING_RESUME`, `ACCEPTANCE_MAP_TABLES`: these are superseded by later work (UNMEASURED per id; one check each before dropping).
- `ART_REVIEW_PAUSE` is a standing owner instruction. If it still holds, it belongs in memory, not a pointer.

### Open items that fell out of carry (need a decision, not a pointer)
- `doing` but stale since 10-07..10-09: `ALPHA_ANIMAL_PORTS_REHOME_1` and `SARLACC_SEEKER_ROOTING_1` (both "NEXT: decide stale-drop or build"), `DESTROY_BATCH_NEVER_KILLS_PAWNS_1`, `SEAT_MEMORY_CLONES_DRIVES_1`, `GREYSEA_FLOOR_PASS_1` (x3 mentions).
- `FULL_LIST_LOAD_DIAGNOSE_MINIFY_SAYS_NO` is `doing` while its pointer says "NEXT: rimflow verify/close it citing 88cddfd92 and 63447a6db". It is an un-executed close.
- `proposed` with 4 mentions and never started: `FLYER_STABLE_BODY_GATE_1`, `LEANINGSCRUB_VENOMVINE_SITTING_1`. Both are blocked on the owner and belong on a question card.
- `MATERIAL_MERGE_LOAD_CRASH_1` (proposed, BENCH 10-10): "FOUNDRY restores OuterRim_Durasteel … before any further material removal". This is a crash-class item sitting in `proposed`.

**Root cause:** pointers are written in the "carry forward" style, but nothing makes the *next* handoff re-list or close them. `handoff.py --wake` presents them and does not track them. Proposed fix: `handoff.py` writes an "inherited pointers" block listing every id from the predecessor whose rimflow state is not done/dropped, so a dropped pointer becomes visible as a deletion.

## 3. Prune plan

### Why `--cull` cannot fire (three independent blockers)
1. **The age clock was reset by a move.** `corpus_commit_times()` takes the *newest* commit touching each path and runs without `--follow`. Commit `33521b93e` (2026-09-19, "Handoffs move out of items/ into infrastructure/state/handoffs") touched 82 files, so 85 handoffs carry a 2026-09-19 commit time. The oldest therefore reads 22 days old, below `cull_days` 30. MEASURED: today 0 candidates; as coded, the first ~117 become eligible around **2026-10-20 to 10-25**.
2. **The drain gate.** A candidate must be committed before the last drain, which is `013b058d5` at 2026-09-25T20:05Z. 84 of the 207 superseded handoffs are newer than that and will never cull until a curation pass deletes lesson files. That has not happened since lessons went one-file-each: there are 298 pending lesson files and 0 deletions ever.
3. **Seat-name split.** Cull keys on the text before `_HANDOFF_`, so `BENCH` and `BENCH_REBOOT` (and the FOUNDRY and MACBENCH pairs) count as separate seats. Each family's newest file is protected forever: 6 protected files instead of 3. The MACBENCH families have been idle since 09-29.

### Concrete prune (rule + count)
**Rule:** delete a handoff when (a) it is not the newest per *window* (BENCH / FOUNDRY / MACBENCH, with REBOOT families merged), and (b) its newest commit predates the last drain (2026-09-25T20:05Z), so its lessons were in the inbox at that drain. **Count: 128 files** (MEASURED). A more conservative cut, filename date before 2026-09-20, gives 85 files (FOUNDRY 45, BENCH 39, MACBENCH 1).
- Also DELETE `infrastructure/state/handoffs/CANON_REINTEGRATION_EXECUTION_1.md`. It is a 2026-09-04 item-style handoff, never filed in rimflow, and invisible to handoff.py; its truth lives in `design/Jawa/canon_reintegration_plan.md`.
- Before deleting, run `handoff.py --harvest` with an earlier `since` over those 128 if anyone doubts the 09-23 and 09-25 drains caught them. The 2026-09 source audit quoted in `harvest()` found 43 of 171 lesson claims had been stranded. Risk if wrong: a stranded lesson survives only in git history (recoverable with `git log -p`).
- **Bigger win than deleting:** cap `## Tree state at wrap` in `~/dev/Lodestar/bin/handoff.py` the way `commits_cap` caps commits (count per top-level dir + the first ~20 paths). 80% of 11.5 MB is that list. Risk: low; the full list is reproducible with `git status`.

### Tool fixes (Lodestar, so they fix every repo)
- `corpus_commit_times`: use the *oldest* add (`--diff-filter=A --follow`, or the filename timestamp) for age.
- Merge `<SEAT>_REBOOT` into `<SEAT>` when grouping for "newest per seat".
- Document in `--help` and in the handoff skill that `--harvest` writes a file into the handoff dir.

## 4. Lessons that should become SKILLS

| proposed skill | level | source evidence | why a skill and not a fact |
|---|---|---|---|
| **`wsl-zsh-shell-traps`** (zsh word-split and `:r`/`:h` modifiers in `"$var:..."`, foreground `sleep` blocked → `python3 -c time.sleep`, `pkill -f`/`pgrep -f` self-match, python.exe CRLF and WSL-path misreads, `grep -c` exit-1 double line, `timeout` absent on macOS) | **global `~/.claude/skills`** (applies to every Archmagi project). Note: global CLAUDE.md cites a `wsl-windows-plumbing` skill that does **not exist** (not in `~/.claude/skills`, not found under `~/dev` at depth 4). This would fill that dangling pointer | zsh 23 handoffs (11 since 10-01), WSL 18, pkill 13, CRLF 7 | It is a procedure for writing any shell command, and it keeps recurring. The CLAUDE.md lines then shrink to one pointer. |
| **`shared-clone-git`**, or a `references/shared-clone.md` in global `git-efficiency` | global reference + project GIT_WORKFLOW for repo specifics | 33 + 28 + 14 + 13 + 12 + 11 handoffs; facts spread across ~25 lesson files | One procedure covers index.lock triage, explicit-path commits, publication proof and "helpers never pull/stash/reset". These are the "git keeps challenging us" items the owner named. |
| **`host-health-telemetry`** (disk: `/tmp` tmpfs, `D:` free, `~/.cache`, artpipe state dir; memory and cgroup OOM; a time series and alert thresholds) | project skill now, global later | disk 17 handoffs with zero monitoring; `heavy-ml-in-seat-cgroup-kills-window` memory; `pulse.py` has no disk metric | The owner asked for telemetry time series. Today every disk failure was discovered after it broke agents. |
| **Fold into `efficient-subagents`**: the brief contract (forbid restart, pull/stash/reset and "wait"; verdicts are evidence; forks exceed briefs) | existing skill | 11 + 7 handoffs; fork-overreach recorded only in memory | Recurring procedure; currently memory-only. |
| **Fold into `rimbridge`**: a "response shape" table (nested keys, list-field type names, `success`/`foundCount`) | existing skill | 13 narrow handoffs | Each wrong key silently reads as 0. |
| **Fold into `review-sheets`**: enactment is one pass, clear notes once acted on, `touchedBySheet` ≠ complete | existing skill | 6 narrow / 31 broad; facts live in memory | It is procedure, currently memory-only. |

## Top 10 actions, ranked by value

| # | target | action | why | risk if wrong |
|---|---|---|---|---|
| 1 | `~/dev/Lodestar/bin/handoff.py` L400–414 | cap the tree-state dirty list (like `commits_cap`) | 80% of 11.5 MB of handoffs is unread `git status` | none; `git status` reproduces it |
| 2 | `infrastructure/state/lessons/` (298) | run a curation drain: fold into skills, delete files | unblocks `--cull`; inbox untouched since 09-25 | lessons lost only if deleted without folding (git keeps them) |
| 3 | 128 handoffs (rule in §3) + `CANON_REINTEGRATION_EXECUTION_1.md` | DELETE | superseded and drained; git is provenance | a stranded lesson is recoverable via git log |
| 4 | new global skill `wsl-zsh-shell-traps` | PROMOTE | 23 + 18 + 13 + 7 handoffs, still recurring; `:r` trap recorded nowhere | low |
| 5 | rimflow | file the 10–12 orphaned work pointers in §2; close `FULL_LIST_LOAD_DIAGNOSE_MINIFY_SAYS_NO` | 32 pointer ids were never items; work is invisible to the queue | duplicate items, if some are already done (check each) |
| 6 | `handoff.py` | add an "inherited open pointers" block (predecessor ids whose state is not done) | 29 of 35 open pointers dropped silently from carry | noise if the list is long; cap it |
| 7 | new skill `host-health-telemetry` + a disk metric in `pulse.py` | PROMOTE/BUILD | 17 disk incidents, zero monitoring; owner asked | low |
| 8 | GIT_WORKFLOW.md + global `git-efficiency` | MERGE the git lessons (~25 files) in; delete worktree-era lessons | worktrees are OFF; 31 handoffs of now-obsolete advice | an old lesson re-read and followed (worktree) |
| 9 | `LESSONS_INBOX.md` | fix its header (it is tracked, not gitignored) and re-render, or untrack it | the view shows 169 of 298 lessons; readers think they saw the inbox | none |
| 10 | `handoff.py` `cull` / `corpus_commit_times` | age by first add or filename; merge `_REBOOT` families | the move commit reset all ages; 6 files are protected instead of 3 | an early cull of a handoff someone still wanted (git keeps it) |

## Questions only the owner can answer

1. **Prune depth for handoffs?** (a) delete the 128 superseded pre-drain files now; (b) delete only the 85 from before 2026-09-20; (c) delete nothing by hand and let a fixed `--cull` do it from ~10-20 onward; (d) keep only the newest 10 per window.
2. **Where should the shell-traps skill live?** (a) global `~/.claude/skills` for every project on every machine; (b) this repo's `skills/` only; (c) created under the name `wsl-windows-plumbing`, which global CLAUDE.md already cites but which does not exist.
3. **Disk/host telemetry: how far this week?** (a) a disk-free metric and alert inside `pulse.py` only; (b) a separate host-health time series (disk, memory, cgroup, game TPS) with its own skill; (c) defer until the game-telemetry design lands.
4. **Orphaned pointers: file or drop?** (a) file all ~12 real-work pointers as items now; (b) file only the FOUNDRY live-check ones and drop the rest; (c) drop all and trust that live work resurfaces.
5. **`LESSONS_INBOX.md`:** (a) untrack it as its header claims (a gitignored, rendered view); (b) keep it tracked and re-render on every lesson add; (c) delete it, since `lessons/` is the inbox.
