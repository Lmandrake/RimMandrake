> HISTORY: retired era, see design/RimMandrake/retired_eras_index_2026-11-18.md. This file's mentions of Relentless, Artisan, Whittle, FOUNDRY, RimPulse or rimflow v3 are history (that machinery no longer runs); the rest is as current as its own status says.

# Stale sweep of retired-era leftovers, Archmagi and SteveDesktop (2026-11-25)

Item `RIMMANDRAKE_CLEAN_STALE_LOCKS_AND_LEFTOVERS_OF_RETIRED_ERAS`. The owner, 1:13 AM PST 2026-11-25: "Please find
anything that says Artisan, Whittle, or Relentless and look for lock files and other old, stale items on both Steve
Desktop and Archmagi. We need to clean all this old junk out!!!"

Each thing was classed by its current state, not by its name: LIVE (something reads or writes it now), STALE (nothing
does, or its owner is gone), COULD NOT LOOK. Moved files are under `D:\ClaudeWork\backups\stale_sweep_2026-11-25\`
(`archmagi\MANIFEST.tsv` lists each moved path with its size, date and first line; `archmagi\DELETED.tsv` lists the
deleted markers). Working lists of this sweep: `D:\ClaudeWork\scratch\stale_sweep_2026-11-25\`.

Code fixed in this run:

- `c21b8b8769`: every detached launch left `<pool>/clones/<ITEM>.det.lock` behind (915 on Archmagi, 12 on
  SteveDesktop, none with a clone beside it). A return now removes the lock file with the clone (`drop_clone_lock`),
  and `clone_lock` re-checks the inode so a removal never gives two holders. Page:
  `design/specs/2026-11-25-clone-lock-file-returned/boundary.md`.
- `60404d5641`: `install_wt_seat_profiles.py` lists FOUNDRY as a retired seat, so `--apply` removes its tile.

## Archmagi

| thing | class | evidence | act |
|---|---|---|---|
| `D:\ClaudeWork\rimmandrake\testq\archmagi.stop` ("Claude Whittle FWLIVE loops hold the Archmagi game", 2026-11-11) | STALE | no Whittle process, no enabled Whittle unit or timer; it closed the Archmagi lane | moved to backups `archmagi\testq\`. The lane stays off by its first gate: `archmagi_gate()` reads `off (TESTQ_ARCHMAGI=1 not set)` (not set by this run) |
| `testq\YIELDED_TO_CLAUDE_WHITTLE.txt` (2026-11-11 resume note) | STALE | names the same retired loops; `fill.stop` it names was already gone | moved to backups |
| `testq\paused.json` (owner 2026-11-25 12:38 AM PST, SteveDesktop lane) | LIVE | his pause, until 2026-12-02 | left |
| systemd slice `app-whittle\x2dclaude.slice` | STALE | 0 tasks, 0 units, active since 2026-11-11; transient, no unit file | stopped; `daemon-reload`; 0 Whittle units listed after |
| 13 masked era units (`rm-relentless*`, `rm-artisan-now.*`, `rm-whittle-now.*`, `whittle-claude@.service`, `rm-pulse.service`) | LIVE | the masks are kept on purpose; `retired_loops_check.py` alarms on an unmask | left |
| 913 orphan `.det.lock` files in `~/rm/relentless/clones` | STALE | no clone beside each; none held (non-blocking flock) | removed with `drop_clone_lock`; cause fixed in `c21b8b8769` |
| 23 `.cleanse-<Mod>.lock` files in the pool (2026-11-17) | LIVE | `designer_cleanse.mod_lock` flock targets; a file that exists holds nothing | left |
| `~/rm/relentless-seeds` (11 GB, 133,179 files, last write 2026-11-06) | STALE | no code reads it; its 3 census clones were at origin/main (2 staged seed-case edits, not work) | tarred to backups `archmagi\home_rm\relentless-seeds.tar` (count matches), removed |
| `~/rm/relentless/release` (88 MB, 3 release clones at `55e59d9f27`), `relentless/live` (6.7 MB), `relentless/tmp4vj6r3_q` | STALE | no code reads them; no unlanded commits | tarred to `archmagi\home_rm\relentless_release_live_tmp.tar`, removed |
| `~/rm/scratch/FOUNDRY`, `~/rm/roles/{Conductor,Operations,artpiped}/whittle` (8.2 MB each, 2026-11-18/19) | STALE | retired seat; Whittle run folders that nothing reads | in the same tar, removed |
| 19 era-named dirs in `~/.seat-tmp` (`foundry_reconcile_*`, `foundry_tree_backup_*`, `*ARTISAN*.DET`, `*RALPH*.DET`, `*RELENTLESS*.DET`) | STALE | temp dirs of finished runs; no git clone; no process names them | tarred to `archmagi\home_rm\seat-tmp_era.tar`, removed |
| `D:\ClaudeWork\rimmandrake\relentless` (7.4 GB, 297 run folders, last write 2026-11-06) | STALE | no live code reads it (old evidence records and a selftest comment cite paths in it) | moved to backups `archmagi\ClaudeWork\rimmandrake\relentless` |
| 95 more era-named items on `D:\ClaudeWork` (depth 3): `relentless_progress`, `rimpulse_redesign`, `tmp_base_clone` (a Whittle tree copy), `arena\ralph_c`, `arena\foundry_vet`, `modset_swaps\relentless`, `ops\relentless_pool_jam`, the era files of `conductor\`, `switching_plan\`, `compare_builders\`, `traps\`, `proof_tiers\`, `final\`, `stragglers\`, `logs\foundry-tree-finish-20261102`, the `scratch\pulse*` files, `screenshots\pulse_check.*` | STALE | each a log, review or work folder of a retired era; no code reads it | moved to backups (`MANIFEST.tsv`, 96 rows MOVED with the line above) |
| `ralph_graffiti\STOP`, `ralph_gss\STOP`, `ralph_pyrelands\STOP` (Artisan loop off switches, 2026-11-08/11) | STALE | no `rm-ralph*` unit exists | moved to backups |
| 16 `samp_*.stop` (live rounds of 2026-10-26), 2 `v3.lock` (rimflow v3, 2026-10-31), 2 pid files (`modcheck.pid`, `ctl.pid`) | STALE | empty markers; both pids dead | deleted (`DELETED.tsv`) |
| `D:\ClaudeWork\rimmandrake\ralph_graffiti`, `ralph_gss`, `ralph_pyrelands`, `ralph_sim` | LIVE | output paths of `Graffiti/stage_colony.py`, `GimmeSomeSlack/northstar/colony_scene.py`, `Pyrelands/play.py`, `Utils/sim/loop_sim.py` | left; rename list |
| `D:\ClaudeWork\rimmandrake\relentless_agent` | LIVE | `seed_trust.py` reads `relentless_agent/seeds` | left; rename list |
| `~/rm/relentless/{clones,store,books,transcripts}`, `~/rm/pulse-deploy` | LIVE | the pool, the run store, `checker_box.py`, `run_store.Effects.transcripts`; units run from `pulse-deploy` | left; rename list |
| 0-byte flock files of live tools (`testq\*.lock`, `ops_watch\*.lock`, `dispatcher\tick.lock`, `~/rm/*.lock`) and older ones (`~/rm/relentless/store/tick.lock`, `wake.lock`, `metronome\shadow\*.lock`, `artpipe\registry.jsonl.lock`) | LIVE / harmless | a flock file that exists holds nothing; a removal can race an opener | left (one line, no ticket) |
| `scratch\augur_steve_runs_1795569864\{artisan,whittle}`, `conductor\relentless_now_removal_20261124`, `waitalive\...remove-relentless-now-page...`, `evidence\RIMMANDRAKE_STOP_RELENTLESS_...` | LIVE | a study of 2026-11-24, a backup and a run record of yesterday, a ticket's evidence | left |
| Windows Terminal tiles "AGENT FOUNDRY" and scheme "Seat FOUNDRY" | STALE | they opened a window into `/home/mandrake/rm/foundry`, which is gone | removed (settings backed up to `archmagi\windows_terminal\settings.json`); installer fixed in `60404d5641` |
| Typora window on `D:\ClaudeWork\rimmandrake\conductor\WHITTLE_NOW.md` (pid 1916989, 13 days) | STALE, left | the file is already deleted; the window is the owner's desktop | left for him to close |
| Windows scheduled tasks | LIVE | 3 RimMandrake tasks (Heartbeat, Telemetry, TPS Observer); no era name | left |
| cron, tmux | LIVE / none | no crontab; no tmux server | nothing |
| `~/dev` era-named paths: `MandrakeWorkflows/{artisan,whittle,relentless}`, `skills/{artisan*,whittle,relentless-pipeline}` | LIVE | kept on purpose for other projects (owner 2026-11-18, `retired_eras_index_2026-11-18.md`) | left |
| record `rm-detached-bench-rimmandrake-build-load-crossing-act-rebi-1795575036` reads `dead` on Archmagi | LIVE | a SteveDesktop run; SteveDesktop reads it `finished` (the Archmagi copy is a stale mirror) | left; see SteveDesktop |

Counts [measured, by table row]: LIVE 13, STALE 16 (one left: the Typora window), COULD NOT LOOK 0.

## SteveDesktop

Read over `ssh mandrake@stevedesktop-wsl` in six light calls; no repo-wide git, no tests, no publish there. The lane's
pause and `max_live` were not touched.

| thing | class | evidence | act |
|---|---|---|---|
| `whittle-claude@.service` mask | LIVE | kept on purpose (the only era unit there) | left |
| era units, timers, processes, cron, tmux | none / LIVE | no era unit, timer or process; tmux `seat-runner`, `seat-server` are the live seat | nothing |
| 12 orphan `.det.lock` files in `~/rm/relentless/clones` | STALE | no clone beside each; none held (`flock -n`) | removed; cause fixed in `c21b8b8769` |
| 9 `.det.lock` files with a clone, 3 warm clones, live runs (deviation record, clone-pool monitor) | LIVE | their clones stand; two runs active | left |
| `RIMMANDRAKE_BUILD_LOAD_CROSSING_ACT_REBINDS_ALIASES.det` (clone of a run that finished) | LIVE | `return_all` gives it back after its grace; a hand return runs `./sync` and `./publish` on the slow disk | left |
| `~/rm/scratch/CLAUDE_STEVEDESKTOP_OFFLINE2/mm_fresh` (7.1 GB) and `~/rm/scratch/UNKNOWN/merge-descent` (16 GB), 2026-11-11 | STALE | seats of the Claude Whittle workers; both HEADs on `origin/main`, no unpushed commit, no stash; one file-mode change (saved as `stevedesktop\mm_fresh_dirty.patch`) | removed at idle disk priority |
| `~/rm/scratch/CLAUDE-OFFLINE1`, `CLAUDE-OFFLINE3` | STALE | empty dirs of the same seats | removed |
| `/mnt/d/RimTest/testq{,.b}/start.lock` | LIVE | written today by the lane | left |
| `/mnt/d/RimTest/testq/deploy_memo.on` | LIVE | the switch of `infrastructure/stevedesktop/deploy_memo.py` | left |
| `~/rm/relentless/store` | LIVE | the run store, journal written today | left; rename list |
| Windows scheduled tasks, Windows Terminal profiles | LIVE | one task "Claude Fleet"; no era tile | left |

Counts [measured, by table row]: LIVE 9, STALE 3, COULD NOT LOOK 0.

## Lines for the rename list (nothing renamed in this run)

- `D:\ClaudeWork\rimmandrake\ralph_{graffiti,gss,pyrelands,sim}`: live output paths named for the Artisan loops.
- `D:\ClaudeWork\rimmandrake\relentless_agent\seeds`: read by `seed_trust.py` (`RM_SEEDS_PRIVATE`).
- `run_rules.json` `never_through` names `relentless_progress`, now moved away: the entry guards nothing.
- `~/rm/relentless/{clones,store,books,transcripts}` on both machines, and `~/rm/pulse-deploy` on Archmagi (already
  in `retired_eras_index_2026-11-18.md`).
- `<agent storage>/modset_swaps/<holder>`: the holder `relentless` is retired (its folder moved to backups).

## Second pass (after the removals)

`rimflow seat ready`: CONDUCTOR is ready. `./pipe show`: control rev 205, ALL ON, `family:relentless OFF`. `game_lock.py
query all`: ArchBig and ArchSmall held by live BENCH runs (holders alive). `detached_helper.py status`: three Archmagi
runs and one SteveDesktop run live, none disturbed. `archmagi.stop` and `~/rm/relentless-seeds` gone; 0 Whittle units.
The Archmagi pool holds 23 `.cleanse-*` locks and 18 `.det.lock` files: 14 beside a clone, and 4 new orphans from runs
that ended after the sweep. Not measured: whether their return step ran from a checkout that did not yet hold
`c21b8b8769` (the dispatch clone holds it at 2:30 AM PST). A recount of orphan `.det.lock` files a day later decides it.
