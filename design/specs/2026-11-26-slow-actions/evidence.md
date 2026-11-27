# Evidence for `one_page.md` (2026-11-26, about 8 PM PST)

Raw files of this run are in `D:\ClaudeWork\rimmandrake\scratch\slowact\` (profiles `*.prof`, plan outputs) and are
scratch. The two scripts that made the 7-day tables are beside this file (`evidence_stats.py`, `evidence_wall.py`).

## 1. Part 1: the deploy plan of Gimme Some Slack on ArchSmall (`--mod GimmeSomeSlack --instance ArchSmall`, plan only)

cProfile, same command, same folders; load average read just before each run.

| run | wall | load | game-side opens | scandir calls | note |
|---|---|---|---|---|---|
| before, profile | 147 s | 24 | 5,185 (34 s) | 7,147 (37 s) | def guard 133 s of it; byte compare 8.6 s |
| before, plain | 191 s | 42 | | | |
| before, profile | 181 s | 33 to 42 | 5,185 (35 s) | 7,147 (52 s) | |
| after, cold index | 136 s, 139 s | 40, 50 | 4,815 reads (index written) | | first run writes 2,472 rows |
| after, warm | 126 s, 75 s, 83 s, 106 s | 32 to 52 | 0 | | plain runs |
| after, profile (index only) | 84 s | 40 | 0 | 7,147 (29 s) | |
| after, profile (index + prune) | 64 s | 36 | 0 | 3,277 (10 s) | `posix.stat` 6,351 calls, 32 s: the rest |

The plan text is identical before and after except the line `not enabled in ModsConfig`, which changed because ArchSmall's
list changed between the runs (another run's act). Game folders were not written (plan mode only).

Planted faults (offline, `selftest_deploy_index.py`, 13 checks): a new size, the same size with a new time, a deleted file
each report a difference. Mutants made the same checks red: a compare that always says "same" (4 red), an index that
ignores the time (2 red), a deploy that does not drop its entries (1 red), a parse kept without its stat (1 red), a size
mismatch sent to the index (1 red). Existing deploy selftests (compose_deleted, def_guard, deleted, exclude_dirs_shared,
git_paths, hold, locked_dll, prune, single_walk, deployed_biome_refs) pass.

Measured traps on the way (so the page's fixes are not guesses): on `/mnt/d` a `stat` by absolute path cost 8.2 to 10.3 ms,
by `dir_fd` 3.7 ms, after `chdir` 1.5 ms (300 files, load 35 to 48). `os.scandir` of the whole ArchSmall Mods tree (5,330
folders, 17,515 files): 36 s, 50 s by path; 18 s by `scandir(fd)` (then ENOMEM once at load 48); `find` listed the same
tree in 3 to 13 s, but `bfs` (the system `find`) printed ENOMEM for 100 folders and counted 15,588 files instead of
17,515 once: a count from it is a confident wrong number under load.

## 2. The 7-day tables

- Units: `journalctl --user --since "7 days ago" -g "over .* wall clock time"` (55,113 lines, 2026-11-19 7:40 PM to
  2026-11-26 7:40 PM): each rm-* service run writes `Consumed X CPU time over Y wall clock time`. Parsed by
  `evidence_wall.py`. All rm-* service runs: 230 CPU hours of the 2,352 core-hours of the week (9.8%), 1,392 wall hours.
- Helper runs: `D:\ClaudeWork\rimmandrake\dispatcher\detached\*.finish.log` mtime minus the launch epoch in the unit name:
  892 runs, 833 h, median 31.7 min, p90 130 min. `control.db` `runs` table (1,526 rows) by family: detached in_game 116
  runs 141 h, offline_build 41 runs 32.5 h, blind_challenge 18 runs 13.5 h; cert_rerun 32 runs 8.5 h.
- Pipeline tick steps (`dispatcher/tick_steps.jsonl`, 4,173 ticks in 7 days): mean total 8.8 s (decide 3.6, execute 4.3);
  the unit's wall median is 46.8 s, so 38 s per run is outside the steps it records (start-up and the work after them).
- Publish: transcripts under `~/.claude/projects` modified in the last 7 days, the lines `publish: took a tree-check slot
  after N s`, `pipeline checks: ... in N s`, `tree checks: N green in N s`, unique per transcript: 94 waits (median 441 s,
  p90 2,315 s, 19.9 h), 371 pipeline-check runs (283 s, 584 s, 31.3 h), 911 tree-check runs (22 s, 39 s, 6.2 h). No publish
  writes its own timing file: UNMEASURED beyond these lower bounds (row for a timing line is not filed; a helper's
  stdout is the only record).

## 3. Parts of single real runs

| action | wall | parts |
|---|---|---|
| publish (this run, 7:05 to 7:35 PM) | 1,811 s | 1,084 s waiting for a slot (2 running ahead), 26 s tree checks (two trees), 596 s pipeline checks (144 green, 1 flaky), the rest the commit and push |
| `maturation_dispatch.py tick` (no apply) | 51 s | user 31 s, sys 2 s; 8,706 opens 5.1 s; 11.9 M dict reads 4.3 s; 716 `last_words` calls 2.2 s |
| `list_dispatch.py tick` (no apply) | 219 s | 193.6 s in `poll` = 48 `list_effect.run` calls (child processes); `replay` of the ledger 6 s; user 112 s, sys 70 s |
| `maturation_now.py` (status page) | 43 s | 12.4 s PNG encode (285 calls); 11.5 M dict reads 2.9 s; 5,437 opens 3.4 s |
| `codebase_now.py` | 110 s | 19.6 k `stat` 10.4 s; 34 k opens 9.1 s; `cs_mask` 6.7 s; 91.7 k `calls` 4.5 s; `poll` 6.9 s |
| `scratch_reap.py` (dry run) | 639 s | 309 s `epoll` waits on child commands (164); 2.44 M `lstat` 176 s; user 123 s, sys 130 s |
| `streams.py collect` | 127 s | user 82 s; 3.16 M `stat` 8 s; 6.3 M `__init__` 6.4 s; `subject_aliases` 3.1 M calls 5.7 s |
| `metronome.py apart --phase sense` | 0.26 s | the unit's median is 4.8 s wall and 4.4 s CPU: not the same work (UNMEASURED) |
| `seat_sync.py --dry-run` | 3.1 s | |
| `rimflow show <ID>` | 4.1 s | |
| this helper run, 6:22 to about 8:00 PM | ~98 min | publish 30 min; the six profiles above 20 min; deploy plan timings about 25 min; the rest (about 20 min) is model turns and edits: [guess ~60%], no record splits it |

The machine during the work (`vmstat 1 6`, 7:46 PM): user 38 to 51%, system 17 to 30%, idle 23 to 35%, 6 to 15 runnable
tasks, 2.5 GB swap in use, disk reads 0.5 to 1.4 GB/s, load average 22 to 52 on 14 cores.
