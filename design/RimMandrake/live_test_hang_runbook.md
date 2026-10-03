# Live-test hang runbook

Owner, 2026-10-03: *"Please engineer a system that is a bit more resistant to these kinds of hangs. We need to
get better at debugging."* Each class below cost minutes to hours on the 2026-10-03 belt night.

**First move, always:** `python3 src/RimMandrake/Utils/belt_watchdog.py`. It prints one line per signal and one
verdict (HEALTHY / STALLED / WEDGED / DEAD) with a remedy. Run it every ~5 min during a live run and before
calling a run "running" (doctrine: `infrastructure/agents/FOUNDRY.md` § Hangs and the watchdog).

## Symptom → cause → remedy

| # | Symptom (what the watchdog prints) | Cause | Remedy |
|---|---|---|---|
| 1 | `DEAD run_output … FINISHED … UNMEASURED … could not bring RimWorld forward` / `FOCUS_LOST`, exit 3 | Another window (media player, browser, a terminal) held the foreground; RimWorld does not render unfocused, so the run cannot proceed. rerun13 died in under 1 s and was polled for 5+ min as if running. | The run is OVER, so stop polling it. Turn on Options → Run in background (or `python3 src/RimMandrake/Utils/game_focus.py`), then relaunch. `focus_heal.py` already escalated (minimise the blocker, minimise/restore the game) before giving up. |
| 2 | `WEDGED player_log … frozen log ending in a loop: …QuestNode_TradeRequest…`, or `WEDGED game … 'Not Responding' for 4m+ at a full core` | A quest test-run exception loop (or another tight main-thread loop). Player.log freezes at the loop (load 7, 14:59), and the bridge main thread times out. | Kill RimWorld by PID and relaunch. The game does not recover. Read the loop's first exception and file it. |
| 3 | `WEDGED player_log … repeating every frame: …RealFoW… IndexOutOfRange` and `step_game_ticks` failing on every map | `mlie.nwnrealfogofwar` throws every Update after `bland_world` destroys ruins on a second map (load 5). | Close the game, remove `mlie.nwnrealfogofwar` from `ModsConfig.xml` (parse it, never hand-grep), and relaunch. |
| 4 | `WEDGED modals open: Dialog_ModSettings` / `Dialog_NamePlayerFactionAndSettlement` | A stale settings poke or `colony_found` left a modal open. `modal_open` surprises then taint every later chain. | Close it with `jawa/window_list_close action=close typeName=<it>`. Then rerun every suite recorded while it was open, because those results are tainted. The runner now closes both at job start and end. |
| 5a | `INFO bridge not answering, game up <25m: still cold-loading?`, which turns into `STALLED bridge not answering` after 25 min | A cold load stalled. A full-list load is about 15 min. | Read the Player.log tail for the last loaded thing and the first exception. Kill and relaunch with the offender out. |
| 5b | `STALLED belt_logs <file> written 20m+ ago` | A subagent went silent. It is either dead (a background agent dies at 600 s of silence) or wedged on a hang above. | Check its notification. Respawn it with a skeleton-first brief and an instruction to call the watchdog every 5 min. |
| 6 | `WEDGED heartbeat … BUDGET: step 'suite X' ran N s > budget`, exit 4 | One suite outran its wall-clock budget (`BELT_SUITE_BUDGET_S`, default 1500 s). | The runner recorded UNMEASURED(BUDGET) and exited by itself. Poke that suite alone, using the heartbeat step to find where it stopped. |
| 7 | `STALLED bridge … MAIN THREAD call failed` with `ping` OK | The main thread is starved (unfocused) or busy (a long event or loop). | Fix focus first. If the problem persists for more than 5 min and the game reads `BUSY` at about one core, treat it as class 2. |
| 8 | `WEDGED player_log` loop of `QuestNode_TradeRequest_RandomOfferDuration` NRE right after a bridge call, then a frozen log | `rimworld/search_debug_actions` expands every debug-menu node; expanding runs the quest generator's test loops on the main thread (MEASURED 2026-10-03: hung twice in Bacta `tank_scar`, and again on a plain poke; on the entry scene it NREs in `RitualSiegeWithSpecifics`) | Never call `search_debug_actions` / `execute_debug_action` from a suite. Use `jawa/pawn_health action=permanent` for permanent injuries; kill and relaunch the game. |


## What the signals mean

- **game**: the RimWorldWin64 process, its CPU use since the last watchdog call, and Windows' "Not Responding" flag. "Not Responding" is only escalated after 4 min of continuous persistence, and never during the first 25 min of a cold load.
- **player_log**: a loop is the same normalised error line ≥20 times in the tail and *still present at its end*. A burst during the load followed by normal lines is not a loop.
- **bridge**: the bridge is probed via `python.exe`, because WSL cannot reach it. `ping` answers off the main thread, so only a main-thread call (`rimworld/get_ui_state`) proves the game is turning over.
- **heartbeat / run_output / runner**: these three tell a slow run from a dead one or a finished one. A run is OVER when its output has a final `MEASURED`/`UNMEASURED` line, or its heartbeat says `finished`. It is DEAD when there is no verdict and no runner process.
