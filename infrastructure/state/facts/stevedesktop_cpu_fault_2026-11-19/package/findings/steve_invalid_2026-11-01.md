# Steve lane INVALID streak of 2026-11-01 (OPS_STEVE_DIAGNOSE_INVALID_MBTX)

Alarm: `steve.invalid_streak` = 3. Three different causes, not one defect. All three were FlowWorks canary guard jobs on the
same four chains. The lane has been green since: the 9 jobs from 22:27Z to 23:18Z are DONE.

| job | finished | cause | what happened | status |
|---|---|---|---|---|
| `J20261101T183825Z-186d97` | 18:57Z | HARNESS | `ensure_playing_map`: quicktest world start failed, programState Entry for 371 s, `no_game`. No crash report. | Root cause UNKNOWN: the game log is gone. Fixed the loss, not the cause. |
| `J20261101T185825Z-fcf731` | 19:09Z | LOAD | Native crash at startup, report `Crash_2026-11-01_190900227`. | Not a mod fault as far as read; one-off so far. |
| `J20261101T215632Z-85a7de` | 22:03Z | DEPLOY | Companion stale: embedded `bd1be15b3c6b`, wanted `d3ad4023cbcb`, after `c9006e1f4e` moved its sources. | Fixed by hand; recurs (below). |

## 186d97: why the cause is unknown

The symptom matches 2026-10-31 pid 30296 (AlienRace `BadImageFormat`, then `WorldGenStep` `TypeLoadException`), but that
is a resemblance, not a finding. The attempt directory held no game log. Its Player.log rotated to Player-prev.log at the
next cold start and was overwritten by the one after, so nothing on SteveDesktop still holds it. The crash run's log and
the current log both contain no `BadImageFormat` or `TypeLoadException`.

The earlier fix did work on this real wounded game: the note reads "game stopped so the next job cold-starts"
(`STEVE_WORKER_UNSTICK_WOUNDED_GAME_KEPT_UP`, until now proven on a mock only).

Fix, this item: `Attempt.keep_game_log` in `infrastructure/stevedesktop/worker.py` copies Player.log into the attempt
directory before the game stops, and puts the fault in the note. The next occurrence is readable.

## fcf731: the crash

The log's last line is RimBridge's `attention.initialize` startup step. The top stack frame is Mono JIT code,
`System.Configuration.SectionGroupInfo:.ctor`, reached from `Lib.GAB.Transport.TcpTransport.StartAsync` through
`TcpListener` and `ConfigurationManager`. That is plain .NET socket setup, in no mod's code. The crash report's other
SteveDesktop neighbours (10-31 07:30, 07:35) have different stacks, so no single signature recurs. Cause not established. Cold starts on later
sources load and run DONE, so it is not a standing fault; the same sources were never re-run. If this stack recurs, it stops
being a one-off: search `Crashes/` for `SectionGroupInfo`.

## 85a7de: the stale companion

Nothing automatic stages a companion: a search of `src`, `infrastructure/stevedesktop` and the state JSON finds no caller of
`sync_test_mods.py` other than people. So any commit touching the companion sources fails every later job at deploy,
after about 344 s, until someone builds and stages by hand. Filed as `STEVE_COMPANION_WIRE_STAGE_HAND_CRANKED`.
