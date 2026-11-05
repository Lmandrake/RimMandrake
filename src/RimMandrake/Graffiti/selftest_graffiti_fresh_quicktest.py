#!/usr/bin/env python3
"""A2's "FRESH quicktest map started by the proof itself" must be fresh (GRAFFITI_NORTHSTAR_GREEN_FULL_1, test pilot gen 17).

Live, 2026-11-03: both A2 runs on 913a1f28 (/home/mandrake/rm/relentless/live/GRAFFITI_NORTHSTAR_GREEN_FULL_1-A2-
20261103T175503Z.log and -20261103T181104Z.log) printed "[1 map] hasCurrentGame: True mapCount: 2 -> OK" and were then
REFUSED at pre-flight "site:map_size: both axes must be >= 150, got 120x120". Player.log shows no new game at either run
(new games only at 17:19Z and 17:42Z); the current map was mapId 1, a 120x120 RM_GelatinousSlime colony on tile 3 that
another session made with jawa/world_tile_map_generate (TILEGEN_SILENT_REUSE_1). Experiment E2 (the pilot, same params as
the script): on a game already Playing, rimworld/start_debug_game_ready waits for the entry scene, "blockingReason": "A
game is already loaded.", and after 280 s returns "success": false, "Timed out waiting for RimWorld entry scene
readiness." prove_quicktest_world.py never reads that answer: it checks only programState Playing, hasCurrentGame and
mapCount >= 1, which the OLD game satisfies, and exits 0. northstar_full.py trusts that exit as "a FRESH quicktest".
HARNESS, deterministic whenever the game is already Playing when A2 starts.

RULED OUT (gen 17): the quicktest itself makes a 120x120 map (T2): the quicktest home was map 0, RM_TheRot; the 120x120
map was a foreign one left current. RULED OUT: Graffiti's code makes that map: no world_tile_map_generate or map size in
src/RimMandrake/Graffiti/*.py or the driver; the map predates both runs.

This drives the REAL prove_quicktest_world.py against a fake bridge. S1 replays E2 (old game, start refused): the script
must exit non-zero. S2 is a control, a real fresh start (success true, one map, tick 1): it must exit 0, so the probe can
go green. S3: a start that answers success but leaves a second map loaded is not a fresh single-map quicktest.
"""
import io
import json
import os
import runpy
import sys
import types
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SCRIPT = os.path.join(ROOT, "src", "RimMandrake", "bridgetools", "prove_quicktest_world.py")

PLAYING = {"programState": "Playing", "hasCurrentGame": True, "paused": True, "tick": 1}
E2_START = {"success": False, "message": "Timed out waiting for RimWorld entry scene readiness.",
            "state": dict(PLAYING, currentMapId="Map_1"),
            "entry": {"success": False, "satisfied": False, "targetReadiness": "entryScene",
                      "blockingReason": "A game is already loaded.", "elapsedMs": 280041}}
FRESH_START = {"success": True, "message": "RimWorld map data is available and is paused for automation.",
               "state": dict(PLAYING, currentMapId="Map_0")}


def _fake_rb(answers, log, state):
    """A stateful fake: go_to_main_menu puts the game at Entry; a start that answers success puts it back at Playing."""
    class RimBridge:
        def __init__(self, **kw):
            pass

        def connect(self):
            pass

        def call(self, tool, params):
            log.append(tool)
            if tool == "rimworld/get_ui_state":
                a = dict(state)
            elif tool == "rimworld/go_to_main_menu":
                if state.get("menu_works", True):
                    state.update(programState="Entry", hasCurrentGame=False)
                a = {"success": True}
            else:
                a = answers.get(tool, {"success": False, "message": "fake: no answer for %s" % tool})
                if tool == "rimworld/start_debug_game_ready" and a.get("success") is True:
                    state.update(PLAYING)
            return {"content": [{"text": json.dumps(a)}]}
    m = types.ModuleType("rimbridge_client")
    m.RimBridge = RimBridge
    m.resolve_endpoint = lambda: ("127.0.0.1", 0, "x")
    return m


def run_script(start, map_count, ticks=1, menu_works=True, at_menu=False):
    answers = {"rimworld/start_debug_game_ready": start,
               "rimworld/get_game_info": {"status": "game_loaded", "ticksGame": ticks, "mapCount": map_count,
                                          "state": PLAYING}}
    state = dict(PLAYING, menu_works=menu_works) if not at_menu else {"programState": "Entry", "hasCurrentGame": False}
    log, out = [], io.StringIO()
    saved_mod, saved_sleep = sys.modules.get("rimbridge_client"), __import__("time").sleep
    sys.modules["rimbridge_client"] = _fake_rb(answers, log, state)
    __import__("time").sleep = lambda s: None
    code = 0
    try:
        with contextlib.redirect_stdout(out):
            runpy.run_path(SCRIPT, run_name="__main__")
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    finally:
        __import__("time").sleep = saved_sleep
        if saved_mod is None:
            sys.modules.pop("rimbridge_client", None)
        else:
            sys.modules["rimbridge_client"] = saved_mod
    return code, out.getvalue(), log


def main():
    fails = []
    code, out, log = run_script(E2_START, map_count=2)
    if "rimworld/start_debug_game_ready" not in log:
        fails.append("S1 probe blind: the script never called start_debug_game_ready")
    if code == 0:
        fails.append("S1 (live E2: game already Playing, start_debug_game_ready success:false 'A game is already "
                     "loaded.', mapCount 2) exited 0: the old game passes as a FRESH quicktest; last line: %s"
                     % (out.strip().splitlines() or ["?"])[-1][:160])
    code, out, _ = run_script(FRESH_START, map_count=1)
    if code != 0:
        fails.append("S2 control (fresh start, success true, one map) exited %s: the probe cannot go green; %s"
                     % (code, (out.strip().splitlines() or ["?"])[-1][:160]))
    code, out, _ = run_script(FRESH_START, map_count=2)
    if code == 0:
        fails.append("S3 (start success but two maps loaded) exited 0: a leftover foreign map passes as fresh")
    # S4: a staged test map (tick 1, Playing) is LEFT for the main menu before the start, so a proof staged on a map can be
    # fresh at all (live 2026-11-04 16:44Z: A2 and F2 'NOT FRESH (start refused: A game is already loaded.)')
    code, out, log = run_script(FRESH_START, map_count=1)
    if "rimworld/go_to_main_menu" not in log or (log.index("rimworld/go_to_main_menu")
                                                > log.index("rimworld/start_debug_game_ready")):
        fails.append("S4 a Playing test game was not left for the main menu before the start: %s" % log)
    # S5: a colony past two in-game days is never left: refused before any go_to_main_menu
    code, out, log = run_script(FRESH_START, map_count=1, ticks=500000)
    if code == 0 or "rimworld/go_to_main_menu" in log:
        fails.append("S5 a game at tick 500000 (a colony) was left or passed: exit %s, calls %s" % (code, log))
    # S6: the menu is never reached -> not fresh, no start
    code, out, log = run_script(FRESH_START, map_count=1, menu_works=False)
    if code == 0 or "rimworld/start_debug_game_ready" in log:
        fails.append("S6 menu never reached yet exit %s, calls %s" % (code, log))
    # S7: already at the main menu: start straight away, green
    code, out, log = run_script(FRESH_START, map_count=1, at_menu=True)
    if code != 0 or "rimworld/go_to_main_menu" in log:
        fails.append("S7 at the menu: exit %s, calls %s" % (code, log))
    for f in fails:
        print("FAIL " + f)
    print("selftest_graffiti_fresh_quicktest: %s" % ("PASS" if not fails else "FAIL (%d)" % len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
