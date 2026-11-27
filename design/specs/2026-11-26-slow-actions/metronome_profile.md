# The two metronome units, profiled whole (2026-11-27, 11:20 AM to 11:30 AM PST, Archmagi)

Item: `RIMMANDRAKE_PROFILE_METRONOME_UNIT_WHOLE_FOUR_CPU_SECONDS` (row 8 of `one_page.md`, same folder). Units:
`rm-metronome.service` (the beat: remember, raise, ring, dispatch, chores) and `rm-metronome-sense.service` (the sense
phase, apart). Both run on Archmagi (14 cores) every 60 s after the last run ends. The load average read 26 to 52 during
every profile here. All wall figures are loaded-machine figures.

## Answer

- The metronome program itself costs about 0.4 s of each run [measured]: Python start, `load_table` (0.19 s with the
  start; it parses `ops_watch.py` with `ast` to find the family list) and the state writes on `/mnt/d`. The rest of each run (about
  95%) is the child commands of the phases.
- The 0.26 s of `one_page.md` was a duplicate exit, not a pass [measured ~90%]: beats.jsonl holds one sense line with
  `exit: duplicate` in 7 days, at 2026-11-26 8:01:21 PM, inside that helper's timing window. A duplicate exit is the
  program start and `load_table`, which is about 0.26 s.
- Three costs repeat in almost every run, and they make most of the time:
  1. **Small-file reads on `/mnt/d` (the Windows drive through 9p).** A `stat` costs about 5 ms and an `open` about
     10 ms under this load. Three collectors (steve, queues, disk) read hundreds to thousands of files or folders each pass (table below).
  2. **The whole ledger is read and replayed again by each reader**, about 93,000 events, 2.3 to 4.9 s each time under
     profile. One sense pass replays it once or twice (flow, roles, process and wrapup each read it alone). Every
     dispatch tick replays it once (4.9 s of an 8.1 s tick under profile).
  3. **Each sense pass reads 8 days of all 20 ops_watch series** (about 73 MB of JSON lines on `/mnt/d`) to carry the other
     families' last points and to build the history for the flags: 2.0 to 3.0 s of every pass under profile, about
     2.2 s per pass live (the phase's seconds less its collectors' seconds).
- Wall time follows the load of the machine. At 11:23 AM the live `queues,wrapup` pass took 47 s; its 7-day median is
  6.9 s. The reads on `/mnt/d` wait most when the machine is loaded (`one_page.md` row 10).

## The units, 4 days, all after sense ran apart (2026-11-23 11:20 AM to 2026-11-27 11:20 AM)

Source: the user journal's `Consumed … CPU time over … wall clock time` lines, and beats.jsonl. Script:
`metronome_week.py` (`DAYS=4`; `DAYS=7` gives the week of `one_page.md`, which mixes in the old in-beat sense).

| unit | runs | wall median / p90 s | CPU median / p90 s | wall h | CPU h |
|---|---|---|---|---|---|
| rm-metronome (beat) | 5,037 | 5.0 / 17.7 | 2.02 / 6.37 | 11.7 | 5.58 |
| rm-metronome-sense | 5,144 | 5.0 / 13.6 | 2.78 / 9.04 | 10.2 | 6.28 |

| phase (child command) | runs | median / p90 s | wall h | cause, from the profile of one run |
|---|---|---|---|---|
| sense (`ops_watch.py run --compose`, 2 families) | 5,144 | 4.64 / 12.97 | 9.65 | collectors 6.48 h (next table); the other 3.17 h (2.2 s a pass) is the read of every series, `history`, `andon` and the status writes |
| dispatch (`dispatcher.py tick --apply`, every 2 beats) | 2,524 | 5.38 / 18.53 | 6.85 | dry tick 6.6 s plain, 8.1 to 10.2 s under profile: `incident_step` reads and replays the ledger (`role_launch.read_ledger`, 4.9 s of 8.1) |
| raise (`restart_reconcile.py run`) | 5,047 | 0.98 / 2.73 | 2.01 | 1.5 s: `read_journal` 1.0 s; 51 seat files on `/mnt/d` 0.4 s. 3 kills at the 60 s hang guard on 2026-11-26 10 AM, none since |
| remember (`ops_memory.py build`) | 5,047 | 1.10 / 2.26 | 1.95 | 2.0 s: real work, step and MAD of 189 readings (`find_step`, `mad` 41,555 calls) and one VictoriaMetrics export (0.44 s) |
| ring (`dispatcher.py status`) | 5,046 | 0.15 / 0.30 | 0.26 | imports only |
| chores | 0 | | 0 | no command |
| outside the phases | | about 0.4 s a run | 0.63 (beat), 0.55 (sense) | the metronome program, above |

## The sense families, live

Source: each series record's own `collector_s`, 4 days (`metronome_families.py`, `DAYS=4`). Causes: cProfile of one
`ops_watch.py run --compose --family A --family B` against a copy of the live store on `/mnt/d`, with no alarms filed
(`metronome_profile_run.sh`). Profiled seconds are higher than the medians, because the profile adds cost and the load
was high.

| family | median / p90 s | h in 4 days | share | cause, from the profile |
|---|---|---|---|---|
| disk | 5.63 / 12.44 | 0.99 | 15% | the clone pool reading (`scratch_clone.scratch_stranded`): 25 `git` child commands, 8.8 s; `scratch_reap.is_clone` globs, 5.0 s, 60 k folder reads |
| flow | 2.90 / 4.81 | 0.91 | 14% | the ledger read and replay, 3.4 s of 9.7 s. Flow runs twice as often as the others: a pass that measures testing adds it (`COMPOSE_NEEDS_FLOW`), and so does a pass that finds the alarm family `flow` unread past its bound |
| steve | 3.86 / 9.95 | 0.72 | 11% | `done_jobs`: it stats all 1,580 files of `testq/done` (2,655 `stat`, 13 s) and reads the ones of the last day (575 reads, 14.5 s). The folder grows: no step removes old records |
| process | 1.16 / 3.33 | 0.65 | 10% | the ledger read (`model.read_clone`), 2.3 s of 2.5 s |
| queues | 2.72 / 9.60 | 0.64 | 10% | `signin_health.last_telling` reads 1,022 files, 15 s; `newest_progress_mtime` 5.2 s |
| tps | 2.82 / 5.72 | 0.49 | 8% | `game_health` 2.4 s and the `tps_record.py` child 1.4 s |
| evidence | 2.46 / 5.66 | 0.45 | 7% | `close_evidence.tamper_findings`, 4.75 s |
| tokentalk | 1.59 / 2.93 | 0.41 | 6% | `c_tokentalk`, 2.9 s (not split further) |
| wrapup | 2.45 / 4.79 | 0.39 | 6% | `wrapup.standing`: the ledger read 2.8 s, `doing_claims` 5.5 s |
| roles | 2.12 / 3.61 | 0.34 | 5% | the ledger read 2.85 s; `role_use.read` 2.2 s |
| testing | 1.06 / 2.95 | 0.21 | 3% | `c_testing` own loop 6.2 s under profile (not split further) |
| codex | 0.68 / 2.06 | 0.15 | 2% | |
| the other 8 | under 0.13 | 0.14 together | 2% | |

## What would remove the most (no ticket filed here; `RIMMANDRAKE_ORDER_TEN_SLOW_ACTION_FIXES_PAGE_FILED_NONE` orders them)

| fix | size | removes, about | proves |
|---|---|---|---|
| One ledger replay, shared: cache the replayed model on disk, keyed on the shard sizes and times, and read it in dispatch, flow, process, wrapup and roles | M | most of 2.3 to 4.9 s, 2 to 3 times a minute: the largest single cost of both units | a dispatch tick and a flow pass, before and after |
| A sense pass that is not the alarm pass reads only the last record of each other family (a tail read), not 8 days of all 20. Its flags use that history today: first find what reads a non-alarm pass's flags | S to M | about 2 s of every pass (3.2 h in 4 days) | the `run` profile of a cheap pass (maturation, pager: 3.9 s, 2.6 s of it `read_series`) |
| `done_jobs`: list `testq/done` once and keep an index by file time, or move records older than the window to an archive folder; `last_telling`: the same for its 1,022 files | S | most of steve's and queues' seconds | the two profiles above |
| The disk family's clone pool reading: reuse the result while the pool's folders are unchanged | S | most of disk's 5.6 s | the disk profile |
| The metronome start: keep the `ast` parse of `ops_watch.py` (it stopped a hand-copied list that drifted once), and cache its result on the file's size and time | S | under 0.14 s a run [guess ~70%] | `met_load` 0.19 s against `py_bare` 0.05 s |

The row-10 question of `one_page.md` stays open: the loaded machine makes every `/mnt/d` read slower, and the units
are only part of that load.

## Raw files

Profiles and outputs: `D:\ClaudeWork\rimmandrake\scratch\metprof\` on Archmagi (scratch). The scripts beside this page
make every table again: `metronome_week.py`, `metronome_families.py`, `metronome_profile_run.sh`,
`metronome_prof_top.py`, `metronome_prof_callees.py`.
