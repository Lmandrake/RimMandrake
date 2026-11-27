# Slow actions: what each costs in 7 days, and why (2026-11-26, 7:55 PM PST)

Item: `RIMMANDRAKE_TIME_SLOW_ACTIONS_DEPLOY_CHECK_TOOK_TWO_MINUTES`. Owner's card, 2026-11-26: time every common action,
fix each slow one by its cause. Measurements and commands: `evidence.md` (same folder). The window is
2026-11-19 7:40 PM to 2026-11-26 7:40 PM PST. Cost = runs × usual duration, in wall hours. The machine has 14 cores; its
load average read 22 to 52 during all timings here, so every wall figure is a loaded-machine figure.

## What was fixed in this run

| action | before | after | what changed |
|---|---|---|---|
| deploy plan of one mod (Gimme Some Slack, ArchSmall) | 147 s, 181 s, 191 s (load 24 to 42) | 64 s, 83 s, 84 s, 106 s (load 36 to 52) | `deploy_index.py`: the Windows-drive files are not opened again when size and time match; the def guard skips folders that hold no defs. Game-side file opens: 5,185 to 0. Folder listings: 7,147 to 3,277. |

Two to three times faster, not ten: the rest is `stat` and folder listing on the Windows drive (row 1 below).
The index cannot catch an edit that keeps both size and modified time (`touch -r`, `cp -p`), bit rot, or a file that
the listing misses. `deploy_custom_mods.py --full-read` reads every file and rewrites the index. Page:
`design/specs/2026-11-26-deploy-index/boundary.md`.

## The ranking (wall hours in 7 days = runs × usual duration)

| # | action | runs | usual (median / p90) | total | cause (named, with its evidence in `evidence.md`) |
|---|---|---|---|---|---|
| 1 | helper run (detached) | 892 | 32 min / 130 min | 833 h | A model call and the work between calls. The split is UNMEASURED for the 7 days: no record keeps it. One run timed by parts: this one (see evidence §3). In-game runs are 141 h of it. |
| 2 | pipeline tick (`rm-maturation-dispatch`) | 7,602 | 47 s / 119 s | 136 h | Repeated work. One run: 51 s wall, 31 s user CPU, 8,706 file opens, 11.9 M dict reads, `last_words` called 716 times. Wall is 1.9× CPU: the load of the machine. |
| 3 | scratch reap (`rm-scratch-reap`) | 160 | 9 min / 57 min | 61 h | Reads of many files: one dry run, 639 s, 2.44 M `lstat` calls (176 s), and 309 s waiting for child commands (which ones: UNMEASURED). |
| 4 | publish (`./publish`) | ≥94 waits, ≥371 check runs | wait 7 min / 39 min; checks 4.7 min / 9.7 min | ≥57 h | A wait in a line (19.9 h) and the real work of the checks (31.3 h pipeline checks, 6.2 h tree checks). One run of mine: 1,811 s = 1,084 s in the line + 596 s pipeline checks + 26 s tree checks. Counts are lower bounds. |
| 5 | metronome beat and sense | 13,445 | 9 s / 25 s | 37 h | The child commands of the phases, about 95% of each run; the metronome program itself about 0.4 s. Three repeated costs: small-file reads on `/mnt/d`, the ledger replayed again by each reader (2.3 to 4.9 s each time), and every sense pass reading 8 days of all 20 series. The 0.26 s timed alone was a duplicate exit, not a pass. Full split: `metronome_profile.md`. |
| 6 | status page (`rm-maturation-page`) | 3,273 | 32 s / 57 s | 33 h | Repeated work. One run 43 s: 12.4 s encoding 285 PNG images and 11.5 M dict reads; the whole page is built again every minute. |
| 7 | ticket lane tick (`list_dispatch.py`) | 516 | 169 s / 425 s | 32 h | Repeated work. One run 218 s: 193 s is 48 item outcome checks run one after the other (`list_effect.run`). |
| 8 | ticket outcome checks (`rm-list-effect`) | 368 | 125 s / 341 s | 17 h | The same cause as row 7: the same checks run again by a second timer. |
| 9 | codebase page (`rm-codebase-now`) | 670 | 14 s / 273 s | 17 h | Reads of many files and real work. One run 110 s: 19.6 k `stat`, 34 k opens, 91 k AST relation calls. |
| 10 | stream collect (`rm-streams-collect`) | 672 | 47 s / 120 s | 12 h | Repeated work. One run 127 s, 82 s user CPU: `subject_aliases` called 3.1 M times, 3.1 M `stat` calls. |
| - | deploy plan of one mod | by walk, stage and cert runs | 147 to 191 s before, 64 to 106 s now | UNMEASURED count | Reads of many files on the Windows drive (fixed in part, above). |

Actions with one figure each, from records: C# build `Time Elapsed 00:03:26` (32 lines in transcripts; the same mod
repeated); game start 39 s and save load 4 s on a game that is up (walk stage record, 2026-11-26); a walk READY in 151 s
with the game up, 534 s with a map rebuild; a full-list cold load many minutes (`CLAUDE.md`); `./sync --dry-run` 3.1 s;
`rimflow show` 4.1 s; the five status commands 0.1 to 3.7 s (brief); a selftest of 13 checks 0.2 s; the Conductor's
window run median 167 s over 64 runs, 6.4 h; wake of the Conductor window UNMEASURED (no start record apart from the run).

## Fixes left (rows; no ticket is filed for a row)

| row | fix | size | proves |
|---|---|---|---|
| 1 | Deploy plan: list and `stat` the game copy with folder-relative calls (a `stat` by absolute path cost 8 to 10 ms, 1.5 ms relative to the folder, 3.7 ms by `dir_fd`; `scandir(fd)` listing 2× faster), or list it once from the Windows side. Add a retry for ENOMEM to the listing (today a folder that fails is skipped without a word). | M (a day) | plan time of Gimme Some Slack; planted ENOMEM |
| 2 | Ticket lane: run the 48 outcome checks once per tick for both timers, and in parallel; keep a result until a file that the check reads has changed. | M | a tick of 218 s → under 30 s |
| 3 | Pipeline tick: compute `last_words` once per tick, not 716 times; stop reading 8.7 k files per tick. | S to M | profile of one tick |
| 4 | Status page: encode only the images that changed; share the read with the tick. | S | profile of one page |
| 5 | Stream collect: memoize `subject_aliases` (3.1 M calls). | S | profile of one run |
| 6 | Scratch reap: stop at a folder's own time, not at each file (2.44 M `lstat`); find the child commands that it waits for. | M | dry run of 639 s |
| 7 | Publish line: slot wait median 7 min and p90 39 min with 2 slots on 14 cores at load 22+. The slot count guards a named danger (`2026-11-24-treecheck-slots`); measure the danger before a change. Pipeline checks re-run 145 of 231 tests per publish. | L | needs the page's own measurement |
| 8 | Metronome: done (`metronome_profile.md`); its five fixes are on that page. | | |
| 9 | Helper runs: record model seconds and tool seconds per run (today UNMEASURED); then the 833 h can be split. | S | any run's record |
| 10 | Load: `vmstat` read 60 to 70% CPU busy, 2.5 GB swap in use, 0.5 to 1.4 GB/s disk reads while the rm timers used about 10% of the core-hours. Find the other users before adding any slot. | M | UNMEASURED who |

## What this page cannot say

- Publish counts are lower bounds (the same line quoted twice in one transcript counts once).
- The 7-day figures for timers are systemd's own `wall clock time` lines. Their wall time includes waiting for CPU.
- The cause of row 1 and its split are UNMEASURED or measured on one run only. Row 5 is split in `metronome_profile.md`.
