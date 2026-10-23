#!/usr/bin/env python3
"""selftest for joint_check.judge (offline, no game): a clean answer passes; a gap, a non-port end, a shared nozzle, an
undrawn pose, a silent probe and reels-with-no-joints never read as PASS."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import joint_check as J  # noqa: E402

fails = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        fails.append(msg)


def ans(*joints, reels=2):
    return {"success": True, "cmd": "joints", "tolerance": 0.05, "reels": reels, "joints": list(joints)}


def j(kind, ok, gap=0.0):
    return {"reel": 1, "at": [3, 4], "rot": 1, "look": "Scrapper", "kind": kind, "ok": ok, "gap": gap, "where": "[1,2]", "note": "n"}


check(J.judge(ans(j("reel_end", True), j("free_port_end", True, 0.01), j("feed_under_reel", True)))[0] == "PASS", "clean joints pass")
check(J.judge(ans(j("reel_end", True), j("free_port_end", False, 0.38)))[0] == "FAIL", "a 0.38-cell flange gap fails")
check(J.judge(ans(j("feed_nozzle_shared", False)))[0] == "FAIL", "two hoses from one nozzle fails")
check(J.judge(ans(j("feed_port_end", False)))[0] == "FAIL", "an end at no port fails")
check(J.judge(ans(j("reel_end", True), j("pose", None)))[0] == "UNMEASURED", "an undrawn laid hose is UNMEASURED, not a pass")
check(J.judge({"success": False, "error": "timeout"})[0] == "UNMEASURED", "a silent probe is UNMEASURED")
check(J.judge(ans(reels=3))[0] == "UNMEASURED", "reels on the map but no joints measured is UNMEASURED")
check(J.judge(ans(reels=0))[0] == "PASS", "a map with no reels passes (nothing to join)")
v, lines = J.judge(ans(j("free_port_end", False, 0.38)))
check(any("0.380" in ln and "free_port_end" in ln for ln in lines), "a FAIL line names the joint kind and its gap")
# JOINT_CHECK_WIDEN_PIPE_STUBS_UNSEEN: pipe ends and hose-over-hose crossings
check(J.pipe_ends([(0, 0), (1, 0), (2, 0)]) == [(0, 0), (2, 0)] and J.pipe_ends([(5, 5)]) == [(5, 5)]
      and J.pipe_ends([(0, 0), (1, 0), (1, 1), (0, 1)]) == [], "pipe_ends: run ends, a lone pipe, a closed ring has none")
tank = {(3, 0)}
part = lambda c: c in tank                                           # noqa: E731
run = [(0, 0), (1, 0), (2, 0)]
st = {tuple(x["at"]): x for x in J.stub_joints(run, [], [], [], part)}
check(st[(2, 0)]["ok"] is True and st[(0, 0)]["ok"] is False, "a pipe end beside a tank passes; the far end at nothing FAILs")
st = {tuple(x["at"]): x for x in J.stub_joints(run, [(-1, 0)], [], [], part)}
check(st[(0, 0)]["ok"] is True and st[(0, 0)]["where"] == "pipe pole", "a pipe end at a pipe pole passes")
st = {tuple(x["at"]): x for x in J.stub_joints(run, [], [(-2, 0, 2, 2)], [], part)}
check(st[(0, 0)]["ok"] is True and st[(0, 0)]["where"] == "hose reel", "a pipe end beside a reel's footprint passes")
st = {tuple(x["at"]): x for x in J.stub_joints(run, [], [(-3, 1, 2, 2)], [], part)}
check(st[(0, 0)]["ok"] is False, "a reel touching the pipe end only at a corner is no port (FAIL)")
st = {tuple(x["at"]): x for x in J.stub_joints(run, [], [], [(0, 0)], part)}
check(st[(0, 0)]["ok"] is True and st[(0, 0)]["where"] == "hose end", "a hose's free end on the pipe end passes")
st = {tuple(x["at"]): x for x in J.stub_joints([(0, 0), (1, 0)], [], [], [], lambda c: True if c == (2, 1) else None)}
check(st[(0, 0)]["ok"] is None and st[(1, 0)]["ok"] is True, "an unanswered role read is UNMEASURED; a diagonal tank passes")
st = {tuple(x["at"]): x for x in J.stub_joints([(0, 0), (1, 0)], [], [], [], lambda c: False)}
check(all(x["ok"] is False for x in st.values()), "nothing with a role anywhere: both ends FAIL")
h = lambda i, cells, reel, **kw: dict({"id": i, "laid": True, "centreCells": cells, "reel": reel, "footprint": [reel[0], reel[1], 2, 2]}, **kw)  # noqa: E731
cx = J.crossing_joints([h(1, [[5, 0], [5, 1], [5, 2]], [0, 0]), h(2, [[4, 1], [5, 1], [6, 1]], [9, 9])])
check(len(cx) == 1 and cx[0]["ok"] is False and cx[0]["at"] == [5, 1] and cx[0]["kind"] == "hose_crossing", "two laid hoses sharing a cell: one FAIL")
cx = J.crossing_joints([h(1, [[5, 0], [6, 0]], [0, 0], relayTo=[6, 0]), h(2, [[6, 0], [7, 0]], [6, 0])])
check(cx == [], "a relay pair meeting at the relay reel is no crossing")
cx = J.crossing_joints([h(1, [[5, 0]], [0, 0]), h(2, [[5, 0]], [9, 9], laid=False)])
check(cx == [], "a stored (not laid) hose never crosses")
a2 = ans(j("reel_end", True))
a2["extra"] = [J._joint("pipe_stub", (0, 0), False, "-", "stub")]
check(J.judge(a2)[0] == "FAIL", "a pipe stub in extra turns the map FAIL")
a3 = ans(reels=3)
a3["extra"] = [J._joint("pipe_stub", (0, 0), True, "pipe pole", "ok")]
check(J.judge(a3)[0] == "UNMEASURED", "extra joints never mask a probe that measured no reel joint")


class FakeB(object):
    """list_things answers a 3-pipe run (one end beside a tank at (3,0)) and a pole; the census holds one stored reel."""
    def call(self, tool, kw):
        if tool == "jawa/list_things":
            if "RM_LiquidTap" in kw.get("defName", ""):
                return {"success": True, "countMatched": 1, "things": [{"def": "RM_LiquidTap", "x": 50, "z": 50}]}
            things = [{"def": "RM_UniversalPipe", "x": x, "z": 0} for x in range(3)] + [{"def": "RM_PipePole", "x": 9, "z": 9}]
            return {"success": True, "countMatched": len(things), "things": things}
        return {"success": False}


def fprobe(cmd):
    if cmd == "census":
        return {"success": True, "hoses": [{"id": 1, "laid": False, "reel": [20, 20], "footprint": [20, 20, 2, 2]}]}
    if cmd == "net:3,0":
        return {"success": True, "origin": "RM_LiquidTank"}
    return {"success": False, "error": "no liquid machine or tank there"}


ex = {tuple(x["at"]): x["ok"] for x in J.extra_joints(FakeB(), fprobe)}
check(ex == {(2, 0): True, (0, 0): False}, "extra_joints live wiring: the tank end passes, the bare end FAILs (%s)" % ex)
ex = J.extra_joints(FakeB(), lambda cmd: {"success": False, "error": "probe timeout"})
check(len(ex) == 1 and ex[0]["ok"] is None, "an unreadable census is UNMEASURED, never a pass")
# JOINT_CHECK_FIX_TAPS_LOOK_LIKE_NOTHING: bleed wells and sprinkler heads (a head stands ON its pipe cell) are ports
st = {tuple(x["at"]): x for x in J.stub_joints(run, [], [], [], lambda c: False, [(-1, 1)])}
check(st[(0, 0)]["ok"] is True and st[(0, 0)]["where"] == "-1,1" and st[(2, 0)]["ok"] is False, "a bleed well on the end's diagonal is a port")
st = {tuple(x["at"]): x for x in J.stub_joints(run, [], [], [], lambda c: False, [(1, 0)])}
check(st[(0, 0)]["ok"] is True and st[(2, 0)]["ok"] is True, "a head standing on a pipe cell is a port for the ends beside it")
check(set(J.PORT_DEF_PREFIXES) >= {"RM_LiquidTap", "RM_SprinklerHead", "RM_LiquidDrill"} and "RM_SprinklerHead_Scrapper" in J._defs_with(J.PORT_DEF_PREFIXES),
      "port defs are read from Defs (variants included)")
# replay of the 2026-10-23 live failures from the scenarios that laid them (map R = c01 at origin (96,35), map C = c07 at (12,112))
sc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenarios")
sys.path.insert(0, os.path.dirname(sc))
sys.path.insert(0, sc)


def replay(modname, ox, oz):
    import importlib
    b = importlib.import_module("scenarios." + modname).SETUP["build"]
    pipes = [(x + ox, z + oz) for d, x, z, *_ in b if d == "RM_UniversalPipe"]
    ports = [(x + ox, z + oz) for d, x, z, *_ in b if d.startswith(J.PORT_DEF_PREFIXES)]
    return {tuple(r["at"]): r["ok"] for r in J.stub_joints(pipes, [], [], [], lambda c: None if False else False, ports)}


try:
    r = replay("c01_thirsty_terraces", 96, 35)
    check(all(r.get(c) is True for c in ((134, 47), (134, 53), (134, 59), (134, 65))), "replay map R: the four sprinkler-row ends PASS")
    check((142, 45) not in r, "replay map R: the 142,45 tail is no longer laid")
except Exception as e:  # noqa: BLE001
    check(False, "replay c01 failed: %r" % e)
try:
    r = replay("c07_bathhouse_tower", 12, 112)
    check(r.get((25, 130)) is True, "replay map C: the pipe end by the bleed wells (25,130) PASSes")
except Exception as e:  # noqa: BLE001
    check(False, "replay c07 failed: %r" % e)
try:
    import importlib
    b = importlib.import_module("scenarios.c05_fuel_depot").SETUP
    pipes = [(x + 112, z + 12) for d, x, z, *_ in b["build"] if d == "RM_UniversalPipe"]
    tanks = {(x + 112 + i, z + 12 + j) for d, x, z, *_ in b["build"] if "Tank" in d for i in (0, 1) for j in (0, 1)}
    st = {tuple(r["at"]): r["ok"] for r in J.stub_joints(pipes, [], [], [], lambda c: c in tanks)}
    check((131, 41) not in st and st.get((125, 41)) is True, "replay map C: C5 without the adapter mod no longer lays the 131,41 tail; the run ends on its tank")
except Exception as e:  # noqa: BLE001
    check(False, "replay c05 failed: %r" % e)
print("joint_check selftest: %d failure(s)" % len(fails))
sys.exit(1 if fails else 0)
