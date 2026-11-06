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
        if tool == "jawa/running_mods":
            return {"packageIds": list(FakeRB.running)}
        if tool == "rimworld/load_game":
            FakeRB.loads.append(dict(params or {}))
            if FakeRB.missing and not (params or {}).get("ignoreModCompatibility"):
                return {"success": False, "code": "save.missing_mods", "message": "6 mod(s) not active"}
            FakeRB.shared["programState"] = "Playing"
            return {"success": True}
        if tool == "rimworld/get_game_info":     # await_lifecycle's map check (READYWAITS_MIGRATE_REMAINING_52_COPIES)
            return {"mapCount": 1 if FakeRB.shared["programState"] == "Playing" else 0}
        if tool == "rimbridge/get_bridge_status":
            return {"state": {"automationReady": True, "currentMapId": 1, "longEventPending": False,
                              "programState": FakeRB.shared["programState"]}}
        return {"success": True}


def run(argv, running=("ludeon.rimworld", "7f.alienworlds"), **kw):
    log = []
    FakeRB.running = running
    FakeRB.shared = {"programState": "Playing"}
    FakeRB.missing = kw.pop("missing", False)
    FakeRB.loads = []
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

# --needs/--without (GENERATOR_MODS_PROVE_INERT_AFTER_CREATION): a wrong RUNNING list ends on `reload needed:`, loads nothing
import io, contextlib  # noqa: E401,E402
import live_def_check  # noqa: E402
live_def_check.aliases = lambda *a: {}
out = io.StringIO()
with contextlib.redirect_stdout(out):
    rc, log = run(["--needs", "7f.alienworlds", "--without", "oblitus.mylittleplanet", "--save", "S"],
                  running=("ludeon.rimworld", "7f.alienworlds", "oblitus.mylittleplanet"))
last = [x for x in out.getvalue().splitlines() if x.strip()][-1]
check("wrong list -> NOT READY, last line `reload needed:`, no load_game",
      rc == L.NOT_READY and last.startswith("reload needed:") and "oblitus.mylittleplanet" in last
      and "rimworld/load_game" not in log)
with contextlib.redirect_stdout(io.StringIO()):
    rc, log = run(["--needs", "7f.alienworlds.tidallylocked", "--save", "S"])
check("a missing --needs id -> reload needed, no load", rc == L.NOT_READY and "rimworld/load_game" not in log)
with contextlib.redirect_stdout(io.StringIO()):
    rc, log = run(["--needs", "7f.alienworlds", "--without", "oblitus.mylittleplanet", "--save", "S"])
check("right list -> the save loads, READY", rc == L.READY and log[0] == "jawa/running_mods" and "rimworld/load_game" in log)
gap = L.load_gap([], ["x.y"], None, {})
check("an unread running list is NOT READY, never `reload needed`", gap and not gap[-1].startswith("reload needed"))
check("load_gap: a fitting list is None", L.load_gap(["a.b"], ["c.d"], {"a.b"}, {}) is None)

# --ignore-missing-mods (GENERATOR_MODS_PROVE_INERT_AFTER_CREATION): the save records MLP/SF the experiment runs without
with contextlib.redirect_stdout(io.StringIO()):
    rc, log = run(["--without", "oblitus.mylittleplanet", "--save", "S"], missing=True)
check("a save recording absent mods, plain load -> NOT READY (the bridge pre-check)", rc == L.NOT_READY)
with contextlib.redirect_stdout(io.StringIO()):
    rc, log = run(["--without", "oblitus.mylittleplanet", "--save", "S", "--ignore-missing-mods"], missing=True)
check("--ignore-missing-mods -> load_game carries ignoreModCompatibility, READY",
      rc == L.READY and FakeRB.loads and FakeRB.loads[-1].get("ignoreModCompatibility") is True)
with contextlib.redirect_stdout(io.StringIO()):
    rc, log = run(["--without", "oblitus.mylittleplanet", "--save", "S", "--ignore-missing-mods"],
                  running=("ludeon.rimworld", "oblitus.mylittleplanet"), missing=True)
check("--ignore-missing-mods still checks the running list first", rc == L.NOT_READY and not FakeRB.loads)

# --restage-with (ATMOSBASE_PROOF_FIX_UNLIT_LEAVES_DARK_LAMP): a refused fixture is re-made on the running list, then loaded
staged = []


def _stager(path, save):
    staged.append((path, save))
    FakeRB.missing = False      # the re-made save records the running list
    return 0


L.run_stager = _stager
with contextlib.redirect_stdout(io.StringIO()):
    rc, log = run(["--save", "rm_proof_atmosphere", "--restage-with", "AtmosphericBase"], missing=True)
check("--restage-with: refused load -> stager on that save, second load READY",
      rc == L.READY and len(staged) == 1 and staged[0][1] == "rm_proof_atmosphere"
      and staged[0][0].endswith(os.path.join("AtmosphericBase", "stage_proof_site.py")) and len(FakeRB.loads) == 2)
staged.clear()
with contextlib.redirect_stdout(io.StringIO()):
    rc, log = run(["--save", "rm_proof_atmosphere", "--restage-with", "AtmosphericBase"])
check("--restage-with: a loadable fixture is not re-made", rc == L.READY and not staged and len(FakeRB.loads) == 1)
L.run_stager = lambda path, save: 2
with contextlib.redirect_stdout(io.StringIO()):
    rc, log = run(["--save", "rm_proof_atmosphere", "--restage-with", "AtmosphericBase"], missing=True)
check("--restage-with: a stager that cannot make the site -> NOT READY, no second load",
      rc == L.NOT_READY and len(FakeRB.loads) == 1)

# argument exclusivity
for argv in (["--save", "ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3", "--restage-with", "AtmosphericBase"],
             ["--save", "rm_proof_atmosphere", "--restage-with", "NoSuchMod"], ["--biome", "X", "--ignore-missing-mods"]):
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            L.main(argv)
        check("argparse refuses %s" % argv, False)
    except SystemExit as e:
        check("argparse refuses %s" % argv, e.code == 2)
for argv in (["--menu-dwell", "5", "--save", "x"], ["--menu-dwell", "0"], []):
    try:
        L.main(argv)
        check("argparse refuses %s" % argv, False)
    except SystemExit as e:
        check("argparse refuses %s" % argv, e.code == 2)

print("SELFTEST " + ("PASS" if not FAILS else "FAIL: %d" % len(FAILS)))
sys.exit(1 if FAILS else 0)
