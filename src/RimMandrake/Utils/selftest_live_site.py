#!/usr/bin/env python3
"""selftest_live_site.py - live_site.py's pure parts and its --menu-dwell sequence against a fake bridge
(WORLD_NULLTEX_FLOOD_HUNT_STACKLESS_SO_FAR). No game: the fake records calls and answers like the bridge."""
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import live_site as L  # noqa: E402

FAILS = []


def check(label, ok):
    print(("PASS " if ok else "FAIL ") + label)
    if not ok:
        FAILS.append(label)


class FakeRB:
    def __init__(self, log, ticks=500, menu_ok=True):
        self.log, self.ticks, self.menu_ok = log, ticks, menu_ok
        self.state = {"programState": "Playing"}

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def call(self, tool, params=None):
        self.log.append(tool)
        if tool == "jawa/map_info":
            return {"tile": 7, "mapBiome": "TemperateForest", "sizeX": 50, "sizeZ": 50}
        if tool == "jawa/time_clock":
            return {"ticksGame": self.ticks}
        if tool == "rimworld/go_to_main_menu" and self.menu_ok:
            FakeRB.shared["programState"] = "Entry"
        if tool == "rimworld/start_debug_game_ready":
            FakeRB.shared["programState"] = "Playing"
        if tool == "rimworld/get_ui_state":
            return {"programState": FakeRB.shared["programState"]}
        if tool == "rimbridge/get_bridge_status":
            return {"state": {"automationReady": True, "currentMapId": 1, "longEventPending": False,
                              "programState": FakeRB.shared["programState"]}}
        return {"success": True}


def run(argv, **kw):
    log = []
    FakeRB.shared = {"programState": "Playing"}
    L.connect = lambda timeout: FakeRB(log, **kw)
    clock = [0.0]       # a fake clock: every sleep advances it, so a wait that never succeeds ends at once
    L.time = types.SimpleNamespace(time=lambda: clock[0], sleep=lambda s: clock.__setitem__(0, clock[0] + s))
    guard = types.ModuleType("bridge_concurrency_guard")
    guard.refuse_if_foreign_activity = lambda what, **k: None
    sys.modules["bridge_concurrency_guard"] = guard
    return L.main(argv), log


# need_regen (pure)
check("need_regen ok when biome matches", L.need_regen({"mapBiome": "X"}, "X", [])[0] == "ok")
check("need_regen regen when biome differs", L.need_regen({"mapBiome": "Y"}, "X", [])[0] == "regen")
check("need_regen no when only --not-biome matches", L.need_regen({"mapBiome": "Y"}, None, ["Y"])[0] == "no")

# --menu-dwell: first contact is a jawa/ call, then menu, then a quicktest back, READY
rc, log = run(["--menu-dwell", "5"])
check("menu-dwell READY", rc == L.READY)
check("menu-dwell first call is jawa/ (arms companion probes)", log and log[0].startswith("jawa/"))
check("menu-dwell goes to menu before the quicktest",
      "rimworld/go_to_main_menu" in log and "rimworld/start_debug_game_ready" in log
      and log.index("rimworld/go_to_main_menu") < log.index("rimworld/start_debug_game_ready"))
check("menu-dwell waits for Entry between them",
      "rimworld/get_ui_state" in log[log.index("rimworld/go_to_main_menu"):log.index("rimworld/start_debug_game_ready")])

# a colony past --max-ticks is never left
rc, log = run(["--menu-dwell", "5"], ticks=10 ** 6)
check("menu-dwell refuses a colony past --max-ticks", rc == L.NOT_READY and "rimworld/go_to_main_menu" not in log)

# a menu that never comes is NOT READY, never READY, and no quicktest is started over a live map
rc, log = run(["--menu-dwell", "5"], menu_ok=False)
check("menu never reached -> NOT READY, no quicktest", rc == L.NOT_READY and "rimworld/start_debug_game_ready" not in log)

# argument exclusivity
for argv in (["--menu-dwell", "5", "--save", "x"], ["--menu-dwell", "0"], []):
    try:
        L.main(argv)
        check("argparse refuses %s" % argv, False)
    except SystemExit as e:
        check("argparse refuses %s" % argv, e.code == 2)

print("SELFTEST " + ("PASS" if not FAILS else "FAIL: %d" % len(FAILS)))
sys.exit(1 if FAILS else 0)
