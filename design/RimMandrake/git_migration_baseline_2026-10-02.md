# Git migration baseline and Windows-path audit — 2026-10-02

Plan: `design/RimMandrake/git_workflow_plan_2026-10-01.md` (Phase 0 and Phase 1). Measured in a
fresh ext4 clone of origin/main; counts are commits on `origin/main` by committer date.

## (a) Baseline numbers

"Ledger/sync" = subject contains `ledger` or `sync` (so it includes `chore(sync): laptop`).
"Trouble" = subject mentions rebase, conflict, recover, lock or stash. Subject matching is a floor:
a rebase stop that was resolved without a commit message naming it is invisible here.

| date | commits | ledger/sync | trouble |
|---|---|---|---|
| 2026-09-24 | 489 | 123 | 14 |
| 2026-09-25 | 303 | 105 | 12 |
| 2026-09-26 | 357 | 96 | 27 |
| 2026-09-27 | 150 | 21 | 16 |
| 2026-09-28 | 151 | 31 | 6 |
| 2026-09-29 | 173 | 37 | 6 |
| 2026-09-30 | 136 | 17 | 3 |
| 2026-10-01 | 283 | 64 | 7 |
| 2026-10-02 (partial) | 5 | 1 | 0 |

`git status --short` latency, one run each: **`/mnt/d/Luke/dev/RimMandrake` 15.31 s** (drvfs, read
only) versus **`/home/mandrake/rm/bench` 0.06 s** (ext4). Phase 2's bar (<0.5 s) is met by ext4 today.

## (b) Windows-path audit

Search: `git grep` for `/mnt/d/Luke/dev/{RimMandrake,Rimworld}`, `D:\Luke\dev\{RimMandrake,Rimworld}`
and the `D:/` form in `src/ skills/ .claude/ infrastructure/ game bridge publish`.
`/mnt/d/Luke/dev/Rimworld` is a symlink to `RimMandrake` (made 2026-09-30), so the old spelling still
resolves but always lands in the shared D:\ tree, never the caller's clone.

**3,901 hits.** By class:

| class | hits | action |
|---|---|---|
| `infrastructure/artpipe/done|failed` manifests and logs | 3,442 | Historical records of finished jobs. Left: rewriting provenance gains nothing, and nothing executes them. |
| ledger, handoffs, item prose, evidence, dashboards | 178 | Historical prose / events. Left (ledger is append-only; deletion rule applies to wrong content, not old addresses). |
| docs / skills prose (`.md`) | 63 | Left; refreshed when each doc is next touched. `skills/rimbridge-companion/SKILL.md`, `skills/rimworld-quests/references/mod_patterns.md` and `skills/rimworld-ideoligion/references/*` carry most. |
| `.csproj` / `.cs` build-instruction comments | 113 in 107 files | Left: XML/`//` comments telling a human which `dotnet.exe build D:\...` line to run. Phase 3's rsync build route replaces these lines wholesale; not code. Item `REPO_RENAME_SYMLINK_RETIRE_1` already tracks them. |
| `.py` executable paths | 42 files | **FIXED** (below). |
| `.sh` | 4 files | **FIXED** (below). |
| `game`, `bridge`, `publish`, `.claude/settings.json` | 0 | Already root-relative (`${CLAUDE_PROJECT_DIR:-.}`, `__file__`). |

**Fixed (commit "Derive repo root from __file__ ..."):** 42 Python files (`skills/validate_skills.py`,
20 in `src/RimMandrake/Utils/`, 12 `bridgetools/prove_*`/`probe_now`/`shoot_planet`/`check_map_biomes_live`,
6 desert-wraps art scripts, 8 SWBestiary art scripts, `LanternDeeps/wire_art.py`,
`SacredGraffiti/art_bench/center_pad.py`) now define
`_RM_ROOT = Path(__file__).resolve().parents[N]` and build the path from it; and 4 shell scripts
(`rimbench/gl_sheet_run.sh`, `bridgetools/crash_watch.sh`, `loadsweep/biome_load_proof.sh`,
`claude_bounded.sh`) derive the root from `${BASH_SOURCE[0]}`. All still compile (`py_compile`, `bash -n`).
Behaviour change by design: a script run from a clone now reads and writes that clone, not D:\.

**Left, with reason (executable, still hardcoded):**

| file | line(s) | reason / fix owed |
|---|---|---|
| `src/RimMandrake/Utils/install_wt_seat_profiles.py` | 83,84,123,133 | Writes Windows Terminal profiles that launch seats in D:\. The target path IS the point; Phase 2/3 repoints it to `/home/mandrake/rm/<seat>` when the owner relaunches. |
| `src/RimMandrake/Utils/install_fleet_shortcut.py` | 53,54 | Same: creates a Windows shortcut to a launcher script on D:\. Repoint at Phase 2. |
| `src/RimMandrake/Utils/rimbench/render_terrain.py` | 390 | Concatenated string literal the AST fixer skips; derive from `__file__` by hand. |
| `src/RimStarWars/StarWarsPatches/Source/BlastDoorFrameAsyncFix/{build,render,verify}_*.py` | 8,124 / 27 / 32 | Output dir is a path that does not exist in the tree (`src/RimStarWars/BlastDoorFrameAsyncFix`), so the scripts are already stale; dead-file candidates, not worth a mechanical edit. |
| docstring usage lines (`python.exe D:\\...`, `cd /mnt/d/... &&`) | ~10 | Examples in docstrings/messages (`bridge_latency_bench.py`, `bridgetools/build.py`, `check_map_biomes_live.py`, `prove_*`); `build.py:102` is an error message telling a human where to run it. Cosmetic; replace with "from the repo root". |
| `VERSION ... Project: D:/Luke/dev/Rimworld/...` headers | 20 | Docstring headers, inert. |
| `.claude/hooks/selftest_block_blanket_git_stage.py:32` | 1 | Test input string naming the guarded path on purpose. |
| `.claude/hooks/block_shared_tree_merge.py` | docstring | Intentional: names the guarded D:\ roots. |

**`~/.claude/` audit:** `settings.json` hooks use `$HOME/dev/Machinist/...` and `$HOME/dev/Placard/...`
(other repos, unaffected). The project `.claude/settings.json` uses `${CLAUDE_PROJECT_DIR:-.}`, so it
follows a clone. Seven skills are symlinks into `/mnt/d/Luke/dev/<other repo>` (claude-remote-control,
confident-wrong-numbers, git-efficiency, measuring-large-artifacts, question-card, review-sheets,
web-access) — none into RimMandrake, so no change. **One real dependency:** Claude's per-project
memory and session dir is keyed by the launch cwd,
`~/.claude/projects/-mnt-d-Luke-dev-RimMandrake/` (242 entries incl. `memory/MEMORY.md`). A launch from
`/home/mandrake/rm/bench` gets a new empty key, so Phase 2 must symlink the new key's `memory/` to this
one before the first relaunch (already in the Phase 2 row). `~/.claude/CLAUDE.md` mentions D:\ only as
the generic machine description. Remaining D:\ strings in `~/.claude` are logs/backups/Ollama skills.

## (c) rimflow ledger reader (`src/RimMandrake/rimflow/model.py`, `read()` line 844)

- **Order: yes.** `read()` merges the frozen `events.jsonl` and every `events/<SEAT>.jsonl` and sorts by
  `(str(ts), file rank, within-file order)`; stable, so a seat's own sequence is never permuted.
  Measured today: 13,825 events, sorted by `ts`.
- **Dedupe by id: NO, and it could not be.** `id` is the *item* id (many events share one), and the
  reader has no event-level key; it never drops a line. A line duplicated by a union merge, or the same
  event present in two files, would be replayed twice (a double `claim`/`close` lands in `world.errors`
  rather than being absorbed). Measured today: 0 exact-duplicate lines among 13,825 events, so nothing is
  currently affected. The Phase 4 "union merge on ledger shards" therefore needs a dedupe keyed on the
  whole canonical line (or a per-event key added at write time) — left for the agent owning `model.py`.
- Malformed line: raises `LedgerError` naming the repair tool (no silent skip).

## Phase 1 — D:\ guard

`.claude/hooks/block_shared_tree_merge.py` now, when the target tree (cwd, `cd X &&`, `git -C X`) resolves
to `/mnt/d/Luke/dev/RimMandrake` or `/mnt/d/Luke/dev/Rimworld`, also refuses `git checkout <ref> -- <path>`
and `git restore --source/-s`, applies every whole-tree refusal **by path** (no longer dependent on the
`.git` being readable), and refuses `git worktree add <path under /mnt/d>` from any cwd. The message names
`/home/mandrake/rm/<seat>`. ext4 clones and `/home/mandrake/wt/*` are unaffected. Selftest
`.claude/hooks/selftest_block_shared_tree_merge.py`: 75/75 (28 new cases). Piped-JSON check of the
hook script confirmed deny on D:\ and silence on `/home/mandrake/rm/bench`. Hooks added mid-session do not
fire in running windows; the plan's success bar ("refused in a fresh window") still needs one fresh launch.
