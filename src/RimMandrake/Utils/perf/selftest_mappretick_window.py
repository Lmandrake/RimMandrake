#!/usr/bin/env python3
"""Offline selftest of mappretick_window.verdict (MAPPRETICK_DIAGNOSE_FULL_LIST_STALL). No bridge, no game."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mappretick_window as W

FAILS = []


def check(name, got, want):
    if got != want:
        FAILS.append("%s: got %r want %r" % (name, got, want))


def prof(pre_max, kids=None, calls=12000, as_dict=False):
    ms = [{"method": W.PRETICK, "calls": calls, "meanUs": "250.1 us",
           "maxUs": pre_max if not isinstance(pre_max, float) else "%.1f us" % pre_max}]
    for name, mx in (kids or {}).items():
        ms.append({"method": name, "calls": calls, "meanUs": "50 us", "maxUs": mx})
    if as_dict:
        return {"methods": {m.pop("method"): m for m in ms}}
    return {"methods": ms}


PF = "Verse.PathFinder:PathFinderTick"
WP = "RimWorld.WildPlantSpawner:WildPlantSpawnerTick"
FIVE = ["ludeon.rimworld", "Ludeon.RimWorld.Royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
        "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey"]
ok = dict(ticks=10000, mods=321, map_size=325, biome="RUT_TheRot", tile=96532, dlcs=FIVE)

# us() parses every rendering the profiler uses
check("us str", W.us("8507.6 us"), 8507.6)
check("us num", W.us(412.0), 412.0)
check("us unavailable", W.us("unavailable: no calls timed"), None)
check("us none", W.us(None), None)
check("us bool", W.us(True), None)

# 2026-10-27 bisect reading: MapPreTick max 8.5 ms -> NOT_REPRODUCED
check("bisect Bcur", W.verdict(prof(8507.6, {PF: "3482.4 us", WP: "4421.3 us"}), **ok)[:2], (0, "NOT_REPRODUCED"))
# boundary: exactly 10.5 ms is not a spike; 10.6 is
check("edge 10.5", W.verdict(prof(10500.0), **ok)[:2], (0, "NOT_REPRODUCED"))
check("edge 10.6 no kids", W.verdict(prof(10600.0), **ok)[:2], (1, "UNNAMED"))
# round-10 spike, 414 ms, PathFinderTick 390 ms -> NAMED PathFinderTick
code, word, text = W.verdict(prof(414000.0, {PF: "390000 us", WP: "2000 us"}), **ok)
check("spike named", (code, word), (0, "NAMED"))
check("spike names pathfinder", "PathFinderTick" in text, True)
# dict-shaped profile is read the same way
check("dict shape", W.verdict(prof(414000.0, {PF: "390000 us"}, as_dict=True), **ok)[:2], (0, "NAMED"))
# share boundary: a child at exactly half names it, just under does not
check("half", W.verdict(prof(400000.0, {PF: "200000 us"}), **ok)[:2], (0, "NAMED"))
check("under half", W.verdict(prof(400000.0, {PF: "199999 us"}), **ok)[:2], (1, "UNNAMED"))
# a child that is not in CHILDREN never names the spike
check("foreign child", W.verdict(prof(400000.0, {"Verse.Foo:Bar": "399000 us"}), **ok)[:2], (1, "UNNAMED"))
# a timed-but-zero-call child is ignored
p = prof(400000.0, {PF: "390000 us"}); p["methods"][1]["calls"] = 0
check("zero-call child", W.verdict(p, **ok)[:2], (1, "UNNAMED"))
# BLIND: MapPreTick never timed / absent / no ticks
check("blind no calls", W.verdict(prof("unavailable: no calls timed", calls=0), **ok)[:2], (1, "BLIND"))
check("blind absent", W.verdict({"methods": []}, **ok)[:2], (1, "BLIND"))
check("blind none profile", W.verdict(None, **ok)[:2], (1, "BLIND"))
check("blind no ticks", W.verdict(prof(1000.0), ticks=0, mods=321, map_size=325, biome="RUT_TheRot", tile=96532, dlcs=FIVE)[:2], (1, "BLIND"))
# wrong scene: a minimal list or a small map proves nothing about the full-list 325 stall
check("minimal list", W.verdict(prof(1000.0), ticks=100, mods=13, map_size=325, biome="RUT_TheRot", tile=96532, dlcs=FIVE)[:2], (1, "WRONG_LIST"))
check("mods unknown", W.verdict(prof(1000.0), ticks=100, mods=None, map_size=325, biome="RUT_TheRot", tile=96532, dlcs=FIVE)[:2], (1, "WRONG_LIST"))
check("small map", W.verdict(prof(1000.0), ticks=100, mods=321, map_size=250, biome="RUT_TheRot", tile=96532, dlcs=FIVE)[:2], (1, "WRONG_MAP"))
# wrong scene, pinned: the round-10 map is RUT_TheRot at tile 96532; any other wide map proves nothing
sc = dict(ticks=100, mods=321, map_size=325, dlcs=FIVE)
check("other biome", W.verdict(prof(1000.0), biome="RUT_Basin", tile=96532, **sc)[:2], (1, "WRONG_MAP"))
check("biome unknown", W.verdict(prof(1000.0), biome=None, tile=96532, **sc)[:2], (1, "WRONG_MAP"))
check("other tile", W.verdict(prof(1000.0), biome="RUT_TheRot", tile=96533, **sc)[:2], (1, "WRONG_MAP"))
check("tile unknown", W.verdict(prof(1000.0), biome="RUT_TheRot", tile=None, **sc)[:2], (1, "WRONG_MAP"))
check("other scene spike", W.verdict(prof(414000.0, {PF: "390000 us"}), biome="RUT_Basin", tile=1, **sc)[:2], (1, "WRONG_MAP"))
check("pinned scene", W.verdict(prof(1000.0), biome="RUT_TheRot", tile=96532, **sc)[:2], (0, "NOT_REPRODUCED"))
check("pin constants", (W.BIOME, W.TILE), ("RUT_TheRot", 96532))
# "all five DLC": a 300+ list missing any one expansion, or an unread list, is WRONG_LIST (even with a named spike)
for d in W.DLCS:
    less = [x for x in FIVE if x.lower() != d]
    check("missing " + d, W.verdict(prof(1000.0), **dict(ok, dlcs=less))[:2], (1, "WRONG_LIST"))
    check("missing %s spike" % d, W.verdict(prof(414000.0, {PF: "390000 us"}), **dict(ok, dlcs=less))[:2], (1, "WRONG_LIST"))
check("dlcs unread", W.verdict(prof(1000.0), **dict(ok, dlcs=None))[:2], (1, "WRONG_LIST"))
check("dlcs empty", W.verdict(prof(1000.0), **dict(ok, dlcs=[]))[:2], (1, "WRONG_LIST"))
check("core only", W.verdict(prof(1000.0), **dict(ok, dlcs=["ludeon.rimworld"]))[:2], (1, "WRONG_LIST"))
check("case-insensitive five", W.verdict(prof(1000.0), **dict(ok, dlcs=[x.upper() for x in FIVE]))[:2], (0, "NOT_REPRODUCED"))
check("dlc constants", sorted(W.DLCS), sorted("ludeon.rimworld." + x for x in
                                              ("royalty", "ideology", "biotech", "anomaly", "odyssey")))
try:
    W.verdict(prof(1000.0), 100, 321, 325, "RUT_TheRot", 96532)
    FAILS.append("dlcs is optional: a caller can skip the expansion check")
except TypeError:
    pass

# every child name is 'Ns.Type:Method' (the profiler's allowlist grammar) and the list fits its 32-method cap
check("child grammar", all(n.count(":") == 1 and "." in n.split(":")[0] for n in W.CHILDREN), True)
check("cap 32", len(W.CHILDREN) + 2 <= 32, True)

# TEST_ENV_FIX_TRIBAL_VISIT_STOPS_SETUP: the staged map is quieted, and read back, before any tick advance.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rimdrive.fake import FakeWorld, pawn_row
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modcheck"))
import quiet_site


def tribal_world():
    w = FakeWorld(pawns=[pawn_row("Col1"),
                         pawn_row("Tribal1", kind="Tribal_Warrior", faction="TribeRough", is_player=False, hostile=True),
                         pawn_row("Visitor1", kind="Tribal_Trader", faction="TribeCivil", is_player=False)])
    w.queue = [{"defName": "TraderCaravanArrival", "fireTick": 8358}, {"defName": "StrangerInBlackJoin", "fireTick": 9000}]
    return w


w = tribal_world()
qs = W.quiet_stage(w)
check("storyteller off", w.debug["enableStoryteller"], False)
check("random mental states off", w.debug["enableRandomMentalStates"], False)
check("threat scale 0", w.difficulty["threatScale"], 0.0)
check("big threats off", w.difficulty["allowBigThreats"], False)
check("incident queue empty", w.queue, [])
alive = sorted(pid for pid, r in w.pawns.items() if not r.get("dead") and r.get("spawned", True))
check("hostile removed, visitor and colonist kept", alive, ["Col1", "Visitor1"])
check("receipt names every control", [c["name"] for c in qs.receipt()["controls"]], list(W.QUIET_CONTROLS))
check("wild spawner left running (a timed child)", "wild_spawner_off" in W.QUIET_CONTROLS, False)
qs.restore()
check("restore turns the storyteller back on", w.debug["enableStoryteller"], True)
# negative control: a game that ignores the setting is refused, never trusted
w = tribal_world()
w.modes.add("settings_lie")
try:
    W.quiet_stage(w)
    FAILS.append("settings_lie: quiet_stage accepted a storyteller that read back ON")
except (quiet_site.QuietSiteUnclean, quiet_site.H.HelperUnverified):
    pass


# a failure AFTER the storyteller went off (the hostile will not go) is refused AND undone
class StubbornWorld(FakeWorld):
    def _t_jawa_pawn_force_incapacitate(self, **_):
        return {"success": True}


w = StubbornWorld(pawns=tribal_world().pawns.values())
try:
    W.quiet_stage(w)
    FAILS.append("stubborn hostile: quiet_stage accepted a hostile that stayed")
except quiet_site.QuietSiteUnclean:
    pass
check("refused stage is undone: storyteller", w.debug["enableStoryteller"], True)
check("refused stage is undone: threat scale", w.difficulty["threatScale"], 1.0)


# the live adapter: RimBridge.call(tool, dict) -> call(tool, **params)
class DictBridge(object):
    def __init__(self, world):
        self.w = world

    def call(self, tool, params=None):
        return self.w.call(tool, **(params or {}))


w = tribal_world()
qs = W.quiet_stage(W.KwSession(DictBridge(w)))
check("KwSession: storyteller off", w.debug["enableStoryteller"], False)
check("KwSession: queue empty", w.queue, [])
check("restore_quiet ok", W.restore_quiet(qs), None)
check("restore_quiet: storyteller back on", w.debug["enableStoryteller"], True)


class Boom(object):
    def restore(self):
        raise RuntimeError("bridge gone")


check("restore_quiet never raises", (W.restore_quiet(Boom()) or "").startswith("restore failed: RuntimeError"), True)
# order: the live path quiets the map before it raises the speed for the window
src = open(W.__file__).read()
live = src[src.index("def _live("):]
check("quiet before speed", live.index("quiet_stage(") < live.index('{"speed": a.speed}'), True)
check("quiet restored in a finally after the window",
      live.index('{"speed": a.speed}') < live.index("finally:") < live.index("restore_quiet(qs)"), True)

if FAILS:
    print("\n".join("FAIL " + f for f in FAILS))
    print("selftest_mappretick_window: %d FAIL" % len(FAILS))
    sys.exit(1)
print("selftest_mappretick_window: PASS")
