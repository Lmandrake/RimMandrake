# Menu drop diagnosis (MAP_DROP_DIAGNOSE_MENU_MIDRUN_GHOST)

## Evidence (D:\Luke\dev\_rmscratch\bridge_calls.jsonl, times UTC; 17:37 PDT = 00:37Z)
- Proof run A = client pid 19368 (cli.py). At 00:37:41 it issued `rimworld/step_game_ticks` (long, ~33 s) and never got an end row.
- At 00:38:13, during that call, a SECOND client appeared: pid 34844 (`northstar_site.py`, the map B site build) made `jawa/static_call`, `get_ui_state`, then **`rimworld/go_to_main_menu`** (ok, 27 ms).
- From 00:38:14 every call of pid 19368 fails (step_game_ticks, map_info, window_list_close, set_current_map ...): "No current map". Those are the 17 harness FAILs.
- pid 34844 then ran `start_debug_game_ready` (IndeterminateError) and polled get_ui_state ~420 s: programState stayed Entry (pyre_site_build_B_fail1.log). That is the "map B stuck at menu".
- No game-over, exception or abandon precedes the drop; no go_to_main_menu from pid 19368 at all.

## Cause
Harness concurrency, not a game fault: two bridge clients drove one game. `fresh_quicktest_world` / `reload_fixture` in `src/RimMandrake/Pyrelands/northstar_site.py` (lines ~116 and ~570) call `rimworld/go_to_main_menu` whenever programState is Playing, with no check that another client is mid-run. Not the site builder's abandon (dbdfef28f7 only touches the quicktest colony map and is not in this call sequence).
Caveat: the Player.log of pass 7 was not archived (only pilot logs), so the game-side log line is unseen; the bridge call log is the evidence.

## Fix (NOT applied: lives in src/RimMandrake/Pyrelands/**, off limits tonight)
In `fresh_quicktest_world` and `reload_fixture`, before `go_to_main_menu`, refuse (SiteError) if bridge_calls.jsonl shows a start row from another pid within the last ~60 s (or an unended start), unless an explicit `--allow-concurrent`. Selftest: fake log with foreign pid recent -> refuses; own pid / old rows -> proceeds. Operationally: never launch a site build while a proof holds the game (rimflow bridge take).

## Short live check (confirms, ~2 min)
Start any long `step_game_ticks` from one client, then run `northstar_site.py` build from another: expect the first client to fail with "No current map" within seconds of the second's go_to_main_menu. After the guard: the second refuses before the call.
