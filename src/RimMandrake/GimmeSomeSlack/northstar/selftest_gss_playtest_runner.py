#!/usr/bin/env python3
"""selftest_gss_playtest_runner.py - the GSS launcher's pure logic: recipe expansion agrees with the C# catalogue,
and the shared verdict rule reads a GSS journal (PENDING save_reload, red-error FAIL) the way it reads FlowWorks'."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gss_playtest_runner as G  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CS = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "JawaBench.BridgeTools", "JawaBenchGssPlaytest.cs")


def main():
    n = 0
    assert G.expand("quick") == ["cords", "ui"]
    assert G.expand("full")[-1] == "save_reload" and "save_reload_b" not in G.expand("full")
    assert G.expand("cords, soak") == ["cords", "soak"]
    try:
        G.expand("hose_bend")   # moved to FlowWorks' runner with the hose
        raise AssertionError("moved scene accepted")
    except ValueError:
        pass
    try:
        G.expand("cord")
        raise AssertionError("typo accepted")
    except ValueError:
        pass
    n += 5
    # the C# catalogue and recipes match this file's (a drift would make the launcher refuse a valid scene or accept a bad one)
    src = open(CS, encoding="utf-8").read()
    known = re.search(r"GssKnown = \{([^}]*)\}", src).group(1)
    full = re.search(r"GssFull = \{([^}]*)\}", src).group(1)
    assert tuple(re.findall(r'"([a-z_]+)"', known)) == G.SCENES, known
    assert tuple(re.findall(r'"([a-z_]+)"', full)) == G.RECIPES["full"], full
    n += 2
    for tool in G.TOOLS.values():
        assert '"%s"' % tool in src, tool
    n += 1
    P = G.P
    end = {"type": "run_end", "completed": True, "scenariosPlanned": 2}
    pend = {"type": "scenario", "name": "save_reload", "status": "PENDING", "evidence": {"resumeRecipe": "save_reload_b"}, "runId": "r1"}
    ok = {"type": "scenario", "name": "cords", "status": "PASS", "expectedFailUntil": None}
    red = {"type": "scenario", "name": "ui", "status": "FAIL", "expectedFailUntil": None}
    assert P.verdict([{"type": "run_start"}, ok, pend, end]) == "INCOMPLETE"
    assert P.pending_resume([ok, pend])["runId"] == "r1"
    assert P.verdict([{"type": "run_start"}, ok, red, end]) == "FAIL"
    b = [{"type": "run_start"}, {"type": "scenario", "name": "save_reload_b", "status": "PASS", "expectedFailUntil": None},
         {"type": "run_end", "completed": True, "scenariosPlanned": 1}]
    assert P.combine([{"type": "run_start"}, ok, pend, end], b) == "PASS"
    n += 4
    n += _resume_wait(G)
    n += _save_reload_b_source(src)
    print("%d/%d passed" % (n, n))
    return 0


class _Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.t += s


def _resume_wait(G):
    """Visit 1 on the full list (STRANGE_WALK_RESUME_RACED_THE_LOAD): the old map, paused at the save's tick, passed the
    readiness poll before the load began. The wait now wants three on-map polls running, and the resume retries
    save_reload_b while the game says it is still the saved one (NOT_RELOADED) or refuses the start."""
    n = 0
    ts = 1000
    old = {"mapCount": 2, "ticksGame": 1000, "state": {"programState": "Playing"}}
    gone = {"mapCount": 0, "ticksGame": 0, "state": {"programState": "Entry"}}
    new = {"mapCount": 1, "ticksGame": 1001, "state": {"programState": "Playing"}}
    # one on-map poll (the old map or a flicker) is not enough; three running are
    seq = iter([old, gone, new, gone, new, new, new, new])
    ck = _Clock()
    w = G.wait_for_map(lambda: next(seq), ts, limit_s=60, clock=ck, sleep=ck.sleep)
    assert w["ready"] and w["polls"] == 7, w
    n += 1
    # a poll that raises (main thread busy finishing the load) breaks a run and is not fatal
    seq = iter([new, RuntimeError("busy"), new, new, new])

    def poll():
        x = next(seq)
        if isinstance(x, Exception):
            raise x
        return x
    ck = _Clock()
    w = G.wait_for_map(poll, ts, limit_s=60, clock=ck, sleep=ck.sleep)
    assert w["ready"] and w["polls"] == 5, w
    n += 1
    # a map past the save's tick is not the loaded save; the wait gives up at its limit
    ck = _Clock()
    w = G.wait_for_map(lambda: {"mapCount": 1, "ticksGame": 2000, "state": {"programState": "Playing"}}, ts, limit_s=10,
                       clock=ck, sleep=ck.sleep)
    assert not w["ready"] and ck.t >= 10, w
    n += 1
    # the resume: NOT_RELOADED (B ran on the saved game) and a refused start are retried; a real verdict ends it
    notre = [{"type": "scenario", "name": "save_reload_b", "status": "INVALID", "reason": "NOT_RELOADED: still the saved game"}]
    done = [{"type": "scenario", "name": "save_reload_b", "status": "FAIL", "reason": "2 line(s) changed"}]
    outs = iter([None, notre, done])
    ck = _Clock()
    r = G.resume_loop(lambda: {"ready": True}, lambda: next(outs), limit_s=300, clock=ck, sleep=ck.sleep)
    assert r["recs"] is done and r["tries"] == 3, r
    n += 1
    # bounded: a game that never reloads ends with the last NOT_RELOADED record (honest INVALID, never a pass)
    ck = _Clock()
    r = G.resume_loop(lambda: {"ready": True}, lambda: notre, limit_s=30, clock=ck, sleep=ck.sleep)
    assert r["recs"] is notre and ck.t >= 30, r
    n += 1
    assert G.not_reloaded(notre) and not G.not_reloaded(done) and not G.not_reloaded(None)
    n += 1
    return n


def _save_reload_b_source(src):
    """save_reload_b's two rules, read from the C# (the companion is built and run only live):
    - the owner struck the walk bar "same polylines after load" (2026-10-22, KNOWN_LIMITS C1): cords and hoses are
      compared without their polyline hashes, which are recorded (geomChanged), never failed;
    - it refuses to read the saved game itself (a B on the pre-load map compares the map with its own snapshot)."""
    n = 0
    b = src[src.index("GScnSaveReloadB(GCtx c)"):]
    b = b[:b.index("\n        }\n")]
    assert "s0.Select(GTopo)" in b and "l0.Select(GTopo)" in b, "B compares raw lines (polyline hash included)"
    assert 'c.ev["geomChanged"]' in b, "B no longer records polyline changes"
    n += 1
    assert "NOT_RELOADED" in b and "gSavedGame" in b and "ReferenceEquals" in b, "B reads the saved game itself"
    a = src[src.index("GScnSaveReloadA(GCtx c)"):]
    a = a[:a.index("\n        }\n")]
    assert "gSavedGame = new WeakReference(Current.Game)" in a, "A does not mark the saved game"
    n += 1
    # the ui scene: a check it could not read is listed NOT READ, never counted as a pass (visit 1: 23/23 read as all green)
    assert not re.search(r'Check\([^;]*skipped[^;]*,\s*true\s*,', src), "a skipped ui check is counted ok"
    assert 'c.ev["skipped"] = skipped' in src and "NOT READ" in src
    n += 1
    topo = src[src.index("string GTopo(string l)"):]
    topo = topo[:topo.index("\n\n")]
    assert '"cord "' in topo and "geom" in topo, topo
    n += 1
    return n


if __name__ == "__main__":
    sys.exit(main())
