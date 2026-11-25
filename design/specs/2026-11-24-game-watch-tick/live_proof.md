# Live proof: the game watcher reads each state, and the tick stops a broken game

Item `RIMMANDRAKE_BUILD_GAME_WATCHER_NAMES_THE_BROKEN_STATE`. Page: `boundary.md` beside this file.

Run on ArchSmall, 2026-11-24 5:08 PM to 5:17 PM PST (2026-11-25 01:08Z to 01:17Z).
Companion: `build.py --apply --instance ArchSmall` from commit `8824ac45f886`, which holds the `lastTickMono` fix
`7165eca30a` (one writer of the tick count). The game was relaunched after the deploy (pid 49164).
Raw files of this run are under the agent storage root, `scratch/gwatch/` (not kept in the repo).

## The states, read live by `game_watcher.py ArchSmall`

| state | heartbeat time (UTC) | detail |
|---|---|---|
| menu | 2026-11-25T01:11:44.303Z | `798 frames completed, phase frame-rest`, scene `menu` |
| loading | 2026-11-25T01:13:04.583Z | `load evidence 0.3s (main thread silent 0.3s)`, during `live_site.py --game` (quicktest map) |
| paused | 2026-11-25T01:13:14.699Z | `paused at tick 1` |
| ticking | 2026-11-25T01:14:24.865Z | `recent progress, tick 636`; `lastTickMono` 176.75 against `mono` 176.762 |
| frames_stopped | 2026-11-25T01:16:05.159Z | `main thread silent 70.6s in update`, after `jawa/tps_test_block seconds=120` |
| process_gone | about 01:17Z (no heartbeat) | `no process in the measured list`, after the stop |

Before the fix `7165eca30a`, a ticking game read `could_not_look` (found live on ArchBig, 2026-11-24). On this
companion it reads `ticking`.

One sample at 2026-11-25T01:13:09.689Z, between `loading` and `paused`, read `could_not_look` (`no pause or recent
tick progress at tick 0`): the map was up and the clock had not yet ticked or paused. `could_not_look` refuses nothing
and is never read as `ticking`, so this is correct. The 25 one-second samples read menu 4, loading 2,
could_not_look 2, paused 17.

## The stop, by `game_watch_tick.tick()`

The main thread was blocked with `jawa/tps_test_block seconds=120` at 5:14:53 PM PST. At 75 s, one tick ran with
`STOP_AGE_S` patched to 65 (the real bound is 1080 s), with `RM_GAME_WATCH_DIR` and `RM_OPS_WATCH_DIR` on scratch
folders. Tick exit 0. ArchBig, in the same tick, read `menu` and was left alone.

The `stops.jsonl` row:

```
{"age_s": 75.6, "at": 1795569370.0140202, "evidence": ".../instances/b/JawaBench/tps/hb_f1b4403890824e8d9ad455fd46ec3644.json: main thread silent 75.6s in update", "game": "ArchSmall", "log": ".../gwatch/tickdir/ArchSmall_1795569370_Player.log", "log_error": null, "outcome": "stopped", "pid": 49164, "signal_error": null, "state": "frames_stopped", "text": "STOPPED ArchSmall pid 49164: frames_stopped (.../hb_f1b4403890824e8d9ad455fd46ec3644.json: main thread silent 90.6s in update)\nSUCCESS: The process with PID 49164 has been terminated."}
```

The told row (route `game_watcher.stopped` → role Conductor, `alarm_routes.json`):

```
{"class": null, "kind": "game_watcher.stopped", "told_at": "2026-11-25T01:16:10Z", "why": "ArchSmall stopped by the game watcher: frames_stopped for 76 s (STOPPED ArchSmall pid 49164: ...). Evidence: .../tickdir/stops.jsonl"}
```

`game_instance.stop(broken=True)` confirmed the state again (silent 90.6 s at the confirm) before `taskkill /F`. The
Player.log of the stopped game was kept beside `stops.jsonl`. The bridge call that held the block ended with
`ConnectionResetError`, because the process was gone.

## Not run live

- A stop of ArchBig. The stop path is the same code; only `_keep_log` reads ArchBig's own Player.log path
  (`a_player_log`). ArchBig read `menu` live in the same tick.
- `stuck_load` and `frame_exceptions`. The selftest `selftest_game_watcher.py` covers both on planted heartbeats.
