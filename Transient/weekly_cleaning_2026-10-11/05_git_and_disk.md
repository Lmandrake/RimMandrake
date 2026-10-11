# 05 — Git usage pain and disk health (weekly cleaning 2026-10-11)

Auditor: BENCH subagent, read-only. All numbers below were measured by a command or python script run on 2026-10-11
unless marked UNMEASURED. Scripts: `census.py` / `snips.py` in this session's scratchpad (throwaway).

## 1. Git: what the workflow is today

- Operating doc: `design/RimMandrake/GIT_WORKFLOW.md` (82 lines). Seat clones `/home/mandrake/rm/{bench,foundry}`, one writer
  each; land with `./publish` (wrapper → `src/RimMandrake/Utils/publish.py`, which runs `git pull -q --rebase --autostash`, line 107)
  or `land.sh` (plumbing: temp index / `merge-tree` replay onto origin/main, push the new sha, **never touches the local branch**).
- `land.sh` exists twice, byte-identical: `/home/mandrake/.seat-tmp/land.sh` and tracked `src/RimMandrake/Utils/land.sh`.
  It **defaults `LAND_REPO=/home/mandrake/rm/foundry`** (line 12), so from BENCH it either refuses a good sha or, in `-m` mode,
  would land FOUNDRY's working-tree bytes (lesson `20261011T070420Z-BENCH-land-sh-defaults-land-repo-home.md`).
- A third sync tool, `src/RimMandrake/Utils/reconcile_clone.py` (backs up, resets index, restores modified paths, pulls), is
  cited only from FOUNDRY handoffs (2026-10-09) and is **absent from GIT_WORKFLOW.md**. GIT_WORKFLOW's last bullet instead
  prescribes a manual `git cherry` + backup branch + `git checkout -B main origin/main` ritual. Two recipes, one problem.
- Guards: 14 `PreToolUse` Bash hooks in `.claude/settings.json` (each a python spawn per Bash call), plus git-native
  `infrastructure/githooks/pre-push` via `core.hooksPath` (set in both clones).
- **State right now:** bench `main...origin/main [ahead 1, behind 1]` (the land.sh duplicate pattern, live), 2 `autostash`
  entries in `git stash list`, a `backup/bench-pre-realign-20261011` branch; foundry `[behind 12]`, clean.
  `git status --porcelain` in bench: **48 tracked-modified files in `Transient/biome_ffar/`** (every one a `*_sheet_*.html` or
  `*.serve.log`) and **1,936 untracked files under `Transient/biome_ffar/img/`** (1,259 .webp, 420 .png, 255 .json).

## 2. Git incident census

Method: python regex scan over 214 handoffs, 299 lessons, 198 memory files (sanity probe: 260 files mention `git`, so the
scanner sees). A count is **files mentioning the pattern**, not incidents; dated incidents below were read from the snippets.

| pattern | files (handoff/lesson/memory) | date span | trend |
|---|---|---|---|
| worktree | 69 (43/16/10) | 09-06..10-08 | gone since worktrees OFF 10-02 — solved |
| rebase | 60 (45/14/1) | 09-04..10-11 | 16 in 10-01..09, 8 in 10-10..11: still live |
| conflict | 58 (42/10/6) | 08-26..10-11 | steady |
| pathspec | 48 (36/8/4) | 09-06..10-09 | fading (hook-enforced) |
| push rejected / non-ff | 45 (35/3/7) | 08-23..10-10 | 15 in 10-01..09: still live |
| index.lock | 40 (33/5/2) | 08-23..10-07 | **0 since 10-07** — solved by per-seat clones |
| stash (any) | 30 (25/3/2) | 08-30..10-10 | live |
| srchash | 24 (20/4/0) | 09-25..10-11 | 14 in 10-01..09 (DLL stamp friction) |
| hook refused compound/whole | 18 (12/6/0) | 09-07..10-11 | live (and hit by this audit, §3 R5) |
| autostash | 15 (14/1/0) | 09-16..10-10 | live |
| mirror stale / drvfs | 15 (10/2/3) | 09-08..10-02 | gone since the mirror |
| blanket stage | 9 (5/0/4) | 09-12..10-02 | solved (hook) |
| unstaged / dirty tree | 9 (7/2/0) | 09-20..10-11 | **rising: 7 of 9 since 10-02** |
| land.sh | 8 (6/2/0) | 10-09..10-11 | **new class, 3 days old** |
| scratch clone | 7 (4/3/0) | 10-09..10-11 | **new class** |
| reset --hard | 7 (5/2/0) | 09-08..10-11 | low |
| ledger lint / NOT_APPEND | 6 (2/4/0) | 10-02..10-11 | **new class** |
| duplicate / patch-equivalent | 5 (5/0/0) | 09-25..10-11 | new class |
| disk full / space | 2 (0/2/0) | 10-06, 10-11 | new class |

**Dated post-migration incidents (≥2026-10-02), read from source:**

| date | incident | source |
|---|---|---|
| 10-04 | `./publish` autostashes and fails "multiple branches" when peers' files are dirty | `handoffs/FOUNDRY_REBOOT_HANDOFF_202610040745.md` |
| 10-04 | `pull --rebase` refuses on dirty tree; `--autostash` hook-blocked; workaround via publish | `handoffs/FOUNDRY_HANDOFF_202610040201.md` |
| 10-05/06 | crash left `.git/rebase-merge`; autostash saved as `refs/stash-saves/crash-autostash-20261005`, branch `crash-backup-20261005` still owed deletion | `handoffs/FOUNDRY_HANDOFF_202610061232.md`, `…1623.md` |
| 10-06 | /tmp (18 GB tmpfs) filled by old scratchpads → every agent ENOSPC | `lessons/20261006T055636Z-BENCH-tmp-18-gb-tmpfs-shared-by.md` |
| 10-07 | publish autostash leaves conflict markers in a dirty clone | `handoffs/FOUNDRY_REBOOT_HANDOFF_202610071234.md` |
| 10-07 | park WIP as patch outside repo, `checkout --`, rebase, reapply (manual dance) | `handoffs/FOUNDRY_HANDOFF_202610070107.md` |
| 10-07 | cloning the repo into a scratchpad (RAM) | `lessons/20261007T054859Z-BENCH-never-git-clone-repo-into-scratchpad.md` |
| 10-09 | OLD land.sh replayed the SHARED HEAD → could publish another agent's half-done commits; hardened | `lessons/20261009T100707Z-FOUNDRY-land-sh-old-replayed-shared-head.md` |
| 10-09 | ~45 helper landings by plumbing; clone drifts behind, `pull` dies on untracked collisions → `reconcile_clone.py` written | `handoffs/FOUNDRY_HANDOFF_202610091006.md`, `…1641.md` |
| 10-10 | ~560 phantom "modified" files in foundry from land.sh lag; MSB3030 false reds from scratch clones | `handoffs/FOUNDRY_HANDOFF_202610101111.md`, `…0040.md` |
| 10-10 | `./publish` autostash stranded **53 files** (incl. served sheet HTML, owner decisions) in `stash@{0}` | `lessons/20261010T164936Z-BENCH-publish-runs-git-pull-rebase-autostash.md` |
| 10-10 | pre-push ledger_lint judges LOCAL HEAD → temp-index push from a behind clone refused NOT_APPEND | `handoffs/BENCH_REBOOT_HANDOFF_202610102057.md` |
| 10-10 | zsh `"$c:refs/heads/main"` applies `:r` modifier, mangles refspec | same |
| 10-10 | landing via scratch clone (because served sheets keep seat dirty) → seat BEHIND → stale-tree reds; same ledger commit pushed twice → duplicate events | `lessons/20261010T235838Z-BENCH-landing-commits-through-scratch-clone-because.md`, `handoffs/BENCH_REBOOT_HANDOFF_202610102358.md` |
| 10-11 | 18 stray agent clones filled **276 GB**; fresh clone ~14 GB with selftest stages | `lessons/20261011T052223Z-FOUNDRY-fresh-clones-14gb-delete-when-pushed.md` |
| 10-11 | deleting a scratch clone lost untracked item prose (PACK_ANIMALS_RESTORE_EMPTY_SADDLES) | `lessons/20261011T125554Z-FOUNDRY-before-deleting-scratch-clone-check-untracked.md` |
| 10-11 | land.sh defaults LAND_REPO=foundry; refuses BENCH shas | `lessons/20261011T070420Z-BENCH-land-sh-defaults-land-repo-home.md` |
| 10-11 | land.sh commits leave bench "ahead/behind" with patch-equivalent duplicates; realign ritual | `handoffs/BENCH_HANDOFF_202610111523.md`; live now (ahead 1, behind 1) |
| 10-11 | (this audit) `block_blanket_git_stage.py` refused a python heredoc because a regex *string* contained `git add .` | observed at 2026-10-11 by this auditor |

**Verdict:** the 10-02 migration killed four whole classes (worktree, index.lock, blanket stage, mirror/drvfs). It replaced
them with ONE cascade that produced ~17 dated incidents in 9 days, all downstream of a single cause (R1).

## 3. Root causes

**R1 — Live-written files are TRACKED inside the seat clone (the cascade's origin).** Review-sheet servers rewrite
`Transient/biome_ffar/*_sheet_*.html` (decisions saved into the page) and append `*.serve.log`; `pulse_core.py:268-288` even
reads those serve logs to find live sheet URLs. Result: bench is never clean (48 modified now), so → `pull --rebase` refuses
("unstaged changes") → `./publish` autostashes → stash re-apply conflicts and strands work (53 files, 10-10) → agents route around
via scratch clones (276 GB, lost untracked prose) or `land.sh` (plumbing) → seat clone drifts ahead/behind with patch-equivalent
duplicates → phantom reds (NOT_APPEND, "lost" bridge tool, MSB3030, ~560 phantom modified) → `reconcile_clone.py` and a manual
realign ritual. Every new incident class since 10-02 is on this chain. Also: Transient is **46% of all commits since 10-04
(1,341 of 2,895)**, 206 commits touched `Transient/biome_ffar/` alone, and 20,957 tracked Transient files occupy **4,957 MB**.

**R2 — `git pull --rebase` is the wrong sync primitive for a dirty tree.** It refuses on ANY unstaged change, even ones that
don't overlap incoming commits. `git merge --ff-only` / `git reset --keep origin/main` only refuse when a dirty file is one the
update would change — which for Transient sheets is almost never. `block_shared_tree_merge.py:53` already names `reset --keep`
as safe; no tool uses it.

**R3 — `land.sh` publishes without telling the local branch.** It pushes `N` but leaves `HEAD` at `C` (sha mode) or unmoved
(`-m` mode) and does not update `refs/remotes/origin/main` past the fetch. Drift is guaranteed by design, then paid for by R2.

**R4 — Policy contradicts tooling.** The hook blocks `--autostash` typed by an agent (`block_shared_tree_merge.py:158`) while
`publish.py:107` runs `--autostash` internally where no hook can see it. GIT_WORKFLOW says "in a dirty clone, never ./publish",
but the bench clone is always dirty (R1), so `./publish` is effectively banned in BENCH yet still the documented primary path.

**R5 — Hook false positives / stale text.** `block_blanket_git_stage.py` scans the raw command string, so a heredoc containing
the text `git add .` is refused (hit by this audit); its refusal message still says "Four threads share this working tree AND
this index" (line 179) — false since 10-02. Compound-command refusals drop the whole call, including the write (18 files mention it).

**R6 — Pre-push lint judges the local HEAD, not the pushed sha** (`infrastructure/githooks/pre-push` → ledger lint), so a
correct temp-index push from a behind clone is refused NOT_APPEND (10-10).

**R7 — Repo weight makes every clone expensive.** bench `.git`: **101,515 loose objects (4.4 GiB) + 155 packs (5.6 GiB)** ≈ 10 GiB,
never gc'd; foundry: 1,183 loose, 5 packs, 6.4 GiB. Fresh clones measured 7–14 GB (lessons). Tracked Transient bulk (R1) is
the main contributor that keeps growing.

**R8 — Wrong default in land.sh** (`LAND_REPO=foundry`) — a silent cross-seat hazard in `-m` mode.

## 4. Git fixes, ranked

| # | fix | kind | target | why | risk if wrong |
|---|---|---|---|---|---|
| G1 | **Move live-written review state out of git**: sheet servers write `.serve.log` and decision state to `~/.seat-tmp/<SEAT>/sheets/` (or `D:\Luke\dev\_rmscratch\sheets\`), and gitignore `Transient/**/*.serve.log` and `Transient/**/img/` now; the HTML stays a generated, committed-once artifact, decisions live in a sidecar `*.decisions.json` committed by the enact step only | tooling | `src/RimMandrake/Utils/art/refresh_sheets.py`, the sheet server, `pulse_core.py:268-288`, `.gitignore` | kills R1, the root of the whole cascade | owner decisions saved only in a served HTML could be lost if the sidecar move is buggy — migrate with a byte-compare |
| G2 | **`seat sync` command** (`src/RimMandrake/Utils/seat_sync.py`, replaces `reconcile_clone.py` + the manual realign): fetch; if every local commit is patch-equivalent (`git cherry` all `-`) → `git reset --keep origin/main`; else `git rebase` only when clean, otherwise `git merge --ff-only` is tried and a named-path report printed; never stash, never --hard | tooling | new file; delete `reconcile_clone.py` and the GIT_WORKFLOW realign bullet | one verb for the one recurring operation; `--keep` refuses rather than touches a dirty file | a non-equivalent local commit misclassified; mitigated by refusing unless cherry is all `-` |
| G3 | **land.sh: realign after landing** — after push, `git update-ref refs/remotes/origin/main N`, then if `C` was HEAD and every later commit is landed, `git reset --keep N` (sha mode); in `-m` mode, `git reset --keep N` when HEAD == old origin. Default `LAND_REPO` to `git rev-parse --show-toplevel` of cwd, refuse when unset and cwd not a clone | tooling | `src/RimMandrake/Utils/land.sh`; then make `~/.seat-tmp/land.sh` a symlink to it | fixes R3 + R8; drift becomes impossible | `reset --keep` aborts on overlap — harmless, prints the path |
| G4 | **publish.py: drop `--autostash`**; when the tree is dirty, fall through to `land.sh -m` with the same paths (it already has a temp-index mode) then `seat sync` | tooling | `src/RimMandrake/Utils/publish.py:107` | removes R4's contradiction; one landing verb works in a dirty clone | publish's retry loop semantics change; selftest owed |
| G5 | pre-push ledger lint judges the **pushed sha's tree** (`$local_sha` from stdin) not HEAD | tooling | `infrastructure/githooks/pre-push` | fixes R6 | lint could miss a HEAD-only shard defect — none known |
| G6 | `block_blanket_git_stage.py`: tokenize with `shlex` and skip heredoc bodies / quoted strings; replace the "Four threads" text with the one-writer-per-clone wording | tooling | `.claude/hooks/block_blanket_git_stage.py:169-190` | R5; stale text is a "deleted, not annotated" violation | a quoted `git add .` passed to `bash -c` escapes — keep matching `bash -c` args |
| G7 | `git gc` (or `git repack -ad && git prune`) in bench; a weekly `git maintenance` timer per clone | tooling (one-time + timer) | `/home/mandrake/rm/bench` | 101k loose objects slow every status/log; likely reclaims several GiB (UNMEASURED until run) | none (objects reachable kept); run when no window is mid-git |
| G8 | Stop committing bulk sheet images and logs: `git rm --cached` is not needed for history, just ignore going forward; consider whether `Transient/` should be tracked at all (owner ruled 2026-09-01 it is) | policy | `.gitignore` | 46% of commits, 4.9 GB tracked | owner can't review from another machine — keep the HTML tracked, drop only img/ and logs |
| G9 | Scratch clones: `scratch_clone.py` should be the only way, default `--filter=blob:none --no-checkout` + sparse paths, register in a manifest, and `scratch_clone.py gc` deletes pushed+clean ones (checks untracked too) | tooling | `src/RimMandrake/Utils/scratch_clone.py` | 276 GB event; lost untracked prose | deleting a clone with unique untracked work — gc must refuse on any `??` outside ignore |
| G10 | Clear the leftovers: 2 autostash entries in bench, `backup/bench-pre-realign-20261011`, foundry's `crash-backup-20261005` + `refs/stash-saves/crash-autostash-20261005` | one-time (owner nod) | both clones | stash entries are where work goes to die | dropping a stash that holds unlanded work — inspect with `git stash show --stat` first |

**Policy simplifications.** After G1–G4: one landing verb (`./publish`, which picks rebase or temp-index itself), one sync verb
(`seat sync`), no stash ever. GIT_WORKFLOW.md's last two sections ("Landing when pull --rebase is refused", the realign bullet)
then DELETE, as do the lessons they summarise (MERGE into the git skill below).

**What belongs in a git skill.** The global `git-efficiency` skill exists. Propose a project skill `rm-git` (or a section in
GIT_WORKFLOW.md, which is already read-on-demand) holding: the two verbs; "proof of publication is `merge-base --is-ancestor`";
`reset --keep` vs `--hard`; why `pull --rebase` refuses on any dirty file; zsh `:r` refspec trap; keep file writes and commits in
separate Bash calls; scratch-clone delete checklist (unpushed AND untracked). PROMOTE to `git-efficiency` (global): `reset --keep`
as the safe sync primitive, `merge --ff-only` vs `pull --rebase` on a dirty tree, `git cherry` for patch-equivalence, zsh refspec
modifier trap, hooks that scan raw command strings false-positive on heredocs.

## 5. Disk: measurements now

Measured 2026-10-11 ~09:00 PDT with `df`, `du` (timeout 115 s) and Windows-side `powershell Get-ChildItem | Measure-Object`
(`du` over drvfs timed out at 100 s on `_rmbuild` and `_rmscratch`, so those two were measured from Windows instead).

**Filesystems**

| mount | size | used | free | use% | note |
|---|---|---|---|---|---|
| `/` (WSL ext4, `/dev/sdd`) | 1007 G | **541 G** | 415 G | 57% | the one that has filled before |
| `/tmp` (tmpfs) | 18 G | 443 M | 18 G | 3% | filled 10-06 (ENOSPC) |
| `C:\` (`/mnt/c`) | 3.7 T | 1.6 T | 2.1 T | 44% | |
| `D:\` (`/mnt/d`) | 3.7 T | 1.9 T | 1.8 T | 51% | |

**The WSL disk image:** `C:\Users\Mandrake\AppData\Local\wsl\{dbc3dd4c-b999-497e-bf84-00c27e4b0562}\ext4.vhdx` = **908.1 GB**
on C: while ext4 inside holds 541 GB. A vhdx never shrinks by itself, so **~367 GB of C: is held by space WSL already freed**
(the high-water mark from the 276 GB clone event). Its cap is the 1007 G ext4 size: the vhdx is already at 90% of the
size where ext4 itself fills.

**Where the 541 GB on `/` is** (accounts for ~all of it)

| path | size | what |
|---|---|---|
| `/home/mandrake/.seat-tmp` | **382 G** | see breakdown below |
| `/home/mandrake/rm/bench` | 18 G | seat clone (`.git` ≈10 GiB: 101,515 loose objects 4.4 GiB + 155 packs 5.6 GiB) |
| `/home/mandrake/rm/foundry_old_20261011` | 17 G | yesterday's foundry clone kept aside |
| `/home/mandrake/rm/foundry` | 14 G | seat clone (6.4 GiB packed) |
| `/home/mandrake/rm/stv` | 7.2 G | a clone: 89 local commits, all 89 landed upstream |
| `/home/mandrake/rm/scratch` | 7.1 G | almost all `scratch/BENCH/push_oldticks` (clean, 0 local commits); plus 46 `enact_v2_*` dirs ~1 MB each |
| `/home/mandrake/rm/store.git` / `mirror.git` | 6.3 G / 6.0 G | shared object store / mirror bare repo (by design) |
| `/home/mandrake/ComfyUI` | 27 G | local imagegen — the track is PARKED (memory `local-imagegen-track-parked.md`) |
| `/home/mandrake/.venvs` | 27 G | python venvs (not broken down) |
| `/home/mandrake/.cache` | 21 G | `uv` 13 G, `pip` 2.8 G, `huggingface` 2.3 G, `esphome` 1.9 G, `ms-playwright` 0.7 G |
| `/home/mandrake/.claude` | 7.8 G | transcripts 6.7 GiB in 4,438 `.jsonl`; only 0.18 GiB older than 30 d (retention is working) |
| `/home/mandrake/wt_p3` | 4.1 G | old worktree-era dir (worktrees OFF since 10-02) — UNMEASURED whether it holds unlanded work |
| `/home/mandrake/.local` | 2.7 G | |

**`/home/mandrake/.seat-tmp` (382 G) breakdown**

| path | size | state (measured: local commits not on any remote ref; patch-id vs origin/main since 10-01) |
|---|---|---|
| `FOUNDRY/claude-1000/` (session scratchpads) | 50 G | two sessions 29 G + 22 G |
| `BENCH/claude-1000/` | 33 G | this session's own scratchpad 25 G (`pushclone`, `land_final`, `hoseport` …), one at 7 G |
| `FOUNDRY/ledger_sync_*/repo` ×5 | ~70 G (14 G each, 4 measured + 1) | all created 10-11, 0 local commits, clean — **a tool leak**: `ledger_sync.py:170` `tempfile.mkdtemp(prefix="ledger_sync_")`, never removed |
| `FOUNDRY/scratch_land`, `pubclone`, `rebase_clone` | 14 G + 7.4 G + 6.9 G | 0 local commits, clean |
| `BENCH/gssland`, `BENCH/scratch_rot` | 7.1 G + 7.1 G | 0 local, clean |
| 17 top-level `*_clone`, `clone2-4`, `clone_di`, `graffiti_rebuild` (all 10-09) | ~185 G (6.9–14 G each) | every local commit landed (patch-id); **dirty tracked files remain in 9 of them** (clone3 15, clone2 7, clone_di 3, …) and `sitting3_clone` has **26 untracked** — the exact shape that lost item prose on 10-11 |
| `foundry_tree_backup_20261009_0653` | 2.0 G | backup |
| `yayo_dd` | 0.8 G | |

**Windows side**

| path | size | files |
|---|---|---|
| `D:\Luke\dev\_rmscratch` | **29.1 GB** | 114,273 — `edge_gate` 10.4 G, `codex` 6.7 G, `mc_r5` 5.3 G, four `saves_backup_*` 4.3 G, `pulse\s1..s5.bmp` 5×23.7 MB |
| `D:\Luke\dev\_rmbuild` | 6.7 GB | 256,171 — 227 per-mod staging dirs incl. `*FuzzSelfTest` |
| `D:\Luke\dev\_artpipe` | 0.97 GB | `_artsrc` 882 MB / 5,314 files, `done` 11,812 files |
| RimWorld appdata `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios` | **19.0 GB** | `Screenshots` **9.3 G**, `DefDump` 4.4 G, `Saves` **3.7 G / 238 files**, `Saves_backup_northstar_20261002204546` 0.9 G, `Saves_archive_2026-09-09` 0.5 G |
| `Player.log` / `Player-prev.log` | 1.5 MB / 3.4 MB | plus 6 hand-named old logs (largest `Player-crashed-animaltype.log` 21.7 MB, 2026-09-01) |
| repo `Transient/` (bench) | 5.1 GiB / 23,407 files | 4,957 MB of it **tracked** (20,957 files); `Transient/modcheck` 1.7 G; files 7–14 d old: 3.6 GB |

## 6. Disk growth sources

Ranked by bytes added per week (from the measurements above; rates are inferences from dates, marked so).

| # | source | evidence | rotation today |
|---|---|---|---|
| D1 | **Agent scratch clones** (`~/.seat-tmp/*_clone`, `FOUNDRY/*`, `BENCH/*`, `rm/scratch/*`) | ~300 G alive; 276 G event 10-11; 7–14 G per clone | **none** — deleted by hand after incidents |
| D2 | **`ledger_sync.py` temp clones** | 5 × 14 G created on one day (10-11) | **none** (mkdtemp, no cleanup) — a bug |
| D3 | **Session scratchpads** `~/.seat-tmp/<SEAT>/claude-1000/<session>` | 83 G across two seats; single sessions 22–29 G (they hold clones) | none; Claude Code does not clean them |
| D4 | **Tracked `Transient/`** → every clone and `.git` | 4.96 GB tracked, 46% of commits since 10-04; each new clone pays it; `.git` bench 10 GiB | the ~14-day shelf life is advisory (`rimflow sweep --transient` lists, never deletes); git keeps every version forever |
| D5 | **bench `.git` loose objects** | 101,515 loose / 155 packs, never gc'd (foundry: 1,183 / 5) | none; `gc.auto` evidently not keeping up |
| D6 | **RimWorld Screenshots** | 9.3 GB | none |
| D7 | **`_rmscratch`** (edge_gate, codex staging, mc_r5, save backups, 23.7 MB BMPs) | 29.1 GB | none; `codex` staging per job never removed |
| D8 | **RimWorld DefDump** | 4.4 GB | overwritten per dump? UNMEASURED |
| D9 | **Saves + backups** | 3.7 G + 0.9 G + 0.5 G in appdata, + 4.3 G in `_rmscratch\saves_backup_*` | "saves stay until he says delete" (owner rule) — keepers by design; the backup copies are not |
| D10 | `_rmbuild` staging | 6.7 GB / 256 k files | none (each winbuild restages) |
| D11 | Transcripts | 6.7 GiB | Claude Code's 30-day cleanup is working (only 0.18 GiB >30 d) — **KEEP** |
| D12 | Logs named in the brief | `registry.jsonl` 4.3 MB / 27,528 lines, `throughput.jsonl` 7.3 MB / 8,103 lines, `bridge_calls.jsonl` 9.4 MB (+ `.1` 20 MB: **already rotates**), serve logs 31 files 0.5 MB total, northstar proof JSON 230 files 99.6 MB (GSS 94.8 MB, 221 tracked) | small; northstar proofs are the only one in git and the only one growing by ~100 MB/fortnight — worth a retention rule |

**Not a problem today:** C: and D: (44% / 51%), /tmp (3%), transcripts, artpipe logs, serve logs, Player.log (rotates via
the game's own `Player-prev.log`).

## 7. Disk watch, retention, one-time cleanup

### 7a. Disk watch — extend `memwatch.py`, do not add a timer

`rm-memwatch.timer` already runs every minute (`src/RimMandrake/Utils/memwatch.py --no-host`), watches tmpfs mounts, rotates its
samples at 20 MB and toasts. `scratch_clone.py sample` (`rm-objstore.timer`, hourly) already records `disk_free_bytes`. Add a
disk section to memwatch rather than a fourth timer:

| metric | how | warn / critical | why that threshold |
|---|---|---|---|
| `/` free | `os.statvfs` | < 150 G / < 60 G | one runaway fan-out of 10 clones = 140 G |
| `/tmp`, `/dev/shm` used | already watched | 70% / 90% | the 10-06 ENOSPC |
| vhdx size vs ext4 used | `powershell Get-Item …ext4.vhdx` hourly (not per minute — powershell steals focus per memwatch's own `--no-host` note; run it from the hourly objstore sampler) | gap > 200 G → advise compaction | it never shrinks |
| C:, D: free | statvfs on `/mnt/c`, `/mnt/d` | < 200 G | |
| count + bytes of git clones outside the two seat clones | walk `~/.seat-tmp`, `~/rm/scratch` for `.git` dirs, depth ≤4 | > 4 clones or > 60 G | the leading indicator; D1+D2+D3 were all clones |
| bench/foundry loose-object count | `git count-objects -v` (hourly) | > 20,000 | D5 |
| top-5 dirs by growth since yesterday | daily du of `~/.seat-tmp/*`, `_rmscratch/*` written to a samples jsonl | report only | finds the next D2 |

Reports go where memwatch already reports (toast + its samples jsonl), surfaced as one RimPulse line (`pulse_core.py` already
reads state files) and in the 06:00/17:30 `rm-pulse-digest` digest. This also seeds the telemetry time series the owner asked for:
one row per sample in `~/.seat-tmp/disk_samples.jsonl`, rotated at 20 MB like memwatch's.

### 7b. Rotation / retention per source

| source | policy | enforcer |
|---|---|---|
| scratch clones (D1) | `scratch_clone.py` is the only way to make one; it records them in a manifest; `scratch_clone.py gc` deletes a clone that is (a) older than 24 h, (b) 0 commits not patch-equivalent to origin/main, (c) **0 modified and 0 untracked** files — else lists it | daily timer + memwatch alert |
| `ledger_sync.py` temp clones (D2) | `try/finally: shutil.rmtree` unless `--keep` | code fix, `src/RimMandrake/Utils/ledger_sync.py:170` |
| session scratchpads (D3) | delete scratchpads of sessions whose transcript mtime is > 3 d old and that hold no `.git` with unlanded work | same gc |
| Transient (D4) | ignore `Transient/**/img/`, `*.serve.log`, `*.bmp`; keep HTML/MD; `rimflow sweep --transient` gains `--apply` for > 14 d (git is provenance) | `.gitignore` + sweep |
| `.git` loose objects (D5) | `git maintenance start` in both clones (or a weekly `git gc --auto`) | one command per clone |
| RimWorld Screenshots (D6) | > 30 d moved to `D:\Luke\dev\_rmscratch\screenshots_archive\` or deleted | owner choice (Q3) |
| `_rmscratch` (D7) | `codex\<job>` removed by `gpt_consult.py` / `codex_image.py` after copy-back; everything else > 14 d listed weekly | code fix + weekly list |
| Saves (D9) | keepers untouched (owner rule); `saves_backup_*` copies older than 14 d listed for deletion | weekly list |
| northstar proof JSON (D12) | keep the latest proof per suite + any cited by a ledger close; move older to `_rmscratch` | owner choice (Q4) |

### 7c. One-time cleanup candidates (NOT deleted — sizes measured, safety measured where possible)

| candidate | size | safety evidence | action |
|---|---|---|---|
| vhdx compaction (`wsl --shutdown` then `Optimize-VHD` or `diskpart compact vdisk`) | **~367 GB on C:** | none lost; needs WSL down → every seat and timer stops | owner (Q1) |
| `~/.seat-tmp/FOUNDRY/ledger_sync_*` ×5 | ~70 G | 0 local commits, 0 dirty each | DELETE |
| 17 `~/.seat-tmp/*_clone` / `clone*` / `graffiti_rebuild` | ~185 G | all local commits landed (patch-id); **but 9 have modified files and `sitting3_clone` has 26 untracked** — diff those against origin first | DELETE after per-clone check |
| `FOUNDRY/scratch_land`, `pubclone`, `rebase_clone`, `BENCH/gssland`, `BENCH/scratch_rot`, `rm/scratch/BENCH/push_oldticks` | ~49 G | 0 local, 0 dirty | DELETE |
| `/home/mandrake/rm/stv` | 7.2 G | 89/89 landed; 2 modified files | DELETE after diffing 2 files |
| `/home/mandrake/rm/foundry_old_20261011` | 17 G | **1 UNLANDED commit** ("Ledger: CANON_MATERIALS_BUILD_1 offline pass note"), 46 modified, 224 untracked | KEEP until FOUNDRY rescues the commit and untracked files |
| session scratchpads in `FOUNDRY/claude-1000` (29 G, 22 G) and `BENCH/claude-1000` (25 G this session, 7 G) | 83 G | they contain clones; check each as above | DELETE after their sessions end |
| `/home/mandrake/ComfyUI` | 27 G | track PARKED by owner 2026-09-05 | owner (Q2) |
| `~/.cache/uv` + `pip` | 15.8 G | caches, regenerable (`uv cache clean`, `pip cache purge`) | DELETE |
| `/home/mandrake/wt_p3` | 4.1 G | worktree era; unlanded state UNMEASURED | check, then DELETE |
| bench `git gc` | likely several GiB of the 10 GiB `.git` (UNMEASURED until run) | lossless | do it |
| `D:\Luke\dev\_rmscratch\edge_gate` / `mc_r5` / `codex` | 10.4 + 5.3 + 6.7 GB | contents not inspected | list, then owner/FOUNDRY decides |
| RimWorld `Screenshots` | 9.3 GB | may hold owner F10 shots? (memory says his F10 shots go to Steam userdata, so these are likely bridge captures — UNMEASURED) | owner (Q3) |
| `Saves_backup_northstar_20261002204546`, `Saves_archive_2026-09-09`, `_rmscratch\saves_backup_*` ×4 | 0.9 + 0.5 + 4.3 GB | backups of saves, not the keepers | owner (keepers rule) |
| bench `stash@{0}`, `stash@{1}` (autostash), `backup/bench-pre-realign-20261011` | tiny | inspect `git stash show --stat` first | DELETE after inspection |

Total reclaimable on `/` without touching anything owner-ruled: roughly **380–400 G** (clones + scratchpads + caches), which then
only becomes free C: space after a vhdx compaction.

## Top 10 actions, ranked by value

| # | action | target | kind | value / risk |
|---|---|---|---|---|
| 1 | Move live-written review-sheet state (serve logs, img/, decision writes) out of the tracked tree; gitignore `Transient/**/img/`, `*.serve.log` | sheet server, `refresh_sheets.py`, `pulse_core.py:268-288`, `.gitignore` | tooling | removes the root of ~17 incidents in 9 days / owner decisions must migrate byte-safe |
| 2 | `seat sync` built on `git reset --keep origin/main` (+ cherry check); delete `reconcile_clone.py` and the manual realign ritual in GIT_WORKFLOW | new `src/RimMandrake/Utils/seat_sync.py` | tooling + DELETE | one verb; `--keep` refuses rather than clobbers |
| 3 | land.sh realigns the local branch after landing and defaults `LAND_REPO` to the cwd clone | `src/RimMandrake/Utils/land.sh` (+ symlink `~/.seat-tmp/land.sh`) | tooling | ends drift and the cross-seat default / low |
| 4 | Fix `ledger_sync.py` temp-clone leak; add `scratch_clone.py gc` (refuses on modified/untracked) on a daily timer | `ledger_sync.py:170`, `scratch_clone.py` | tooling | ~70 G/day leak closed; gc prevents the 276 G repeat |
| 5 | Disk section in memwatch + hourly vhdx/clone-count sample, surfaced in RimPulse and the digest | `memwatch.py`, `scratch_clone.py sample`, `pulse_core.py` | tooling | first warning before ENOSPC; starts the disk time series |
| 6 | One-time: delete landed-and-clean clones + ledger_sync leftovers (~300 G), after per-clone dirty-file check | `~/.seat-tmp/*`, `~/rm/scratch/BENCH/push_oldticks` | cleanup | big win / lose untracked prose if the check is skipped |
| 7 | Compact the vhdx | `C:\Users\Mandrake\AppData\Local\wsl\{dbc3…}\ext4.vhdx` | owner action | ~367 GB C: back / full WSL stop |
| 8 | publish.py: drop `--autostash`, fall through to temp-index landing in a dirty tree | `src/RimMandrake/Utils/publish.py:107` | tooling | ends the stash-stranding class; removes hook/tool contradiction |
| 9 | Pre-push ledger lint judges the pushed sha; blanket-stage hook stops matching heredoc text and drops "Four threads" | `infrastructure/githooks/pre-push`, `.claude/hooks/block_blanket_git_stage.py` | tooling + DELETE stale text | removes two false-refusal classes |
| 10 | `git maintenance start` / `git gc` in bench (101k loose objects) | `/home/mandrake/rm/bench` | one-time + timer | faster git, smaller clones / none |

## Questions only the owner can answer

1. **Compacting the WSL disk (~367 GB back on C:) needs every seat, timer and the artpipe daemon stopped for ~10–30 min.** When?
   (a) tonight at handoff · (b) next reboot you call anyway · (c) not needed — C: has 2.1 TB free, skip it · (d) schedule it monthly.
2. **`/home/mandrake/ComfyUI` (27 GB) belongs to the local-imagegen track you parked on 2026-09-05.** (a) delete it · (b) move it to
   D: · (c) keep it as is.
3. **RimWorld's `Screenshots` folder is 9.3 GB (bridge captures, by our reading).** (a) delete anything older than 30 days ·
   (b) move older ones to D: · (c) keep everything.
4. **Northstar proof JSONs are committed to git (GSS alone 94.8 MB, 221 files) and grow ~100 MB a fortnight.** (a) keep only the
   latest per suite in git, older ones on D: · (b) stop committing them, keep them on D: only · (c) keep committing all of them.
5. **Should review-sheet images and serve logs stop being committed (they make up most of `Transient/biome_ffar`'s 1,936 dirty
   files)?** You ruled 2026-09-01 that Transient is tracked so you can review from another machine. (a) keep sheet HTML tracked,
   stop tracking images and logs · (b) stop tracking review sheets entirely, serve them only · (c) keep tracking everything.
