#!/usr/bin/env python3
"""selftest_gss_playtest_runner.py - check recipes, shared journal verdicts and automatic resume offline."""
import os
import re
import sys
from contextlib import redirect_stderr
from functools import partial
from io import StringIO
from unittest.mock import patch

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
    n += _resume_deadline(G, pend, end)
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
    r = G.resume_loop(lambda *_: {"ready": True}, lambda *_: next(outs), limit_s=300, clock=ck, sleep=ck.sleep)
    assert r["recs"] is done and r["tries"] == 3, r
    n += 1
    # bounded: a game that never reloads ends with the last NOT_RELOADED record (honest INVALID, never a pass)
    ck = _Clock()
    r = G.resume_loop(lambda *_: {"ready": True}, lambda *_: notre, limit_s=30, clock=ck, sleep=ck.sleep)
    assert r["recs"] is notre and ck.t >= 30, r
    n += 1
    assert G.not_reloaded(notre) and not G.not_reloaded(done) and not G.not_reloaded(None)
    n += 1
    return n


def _resume_deadline(G, pend, end):
    """Drive the CLI's automatic resume with a fake bridge and clock."""
    first = [{"type": "run_start"}, dict(pend, evidence={"resumeRecipe": "save_reload_b",
                                                       "saveName": "test", "ticksAtSave": 1000}), end]
    ready = {"mapCount": 1, "ticksGame": 1001, "programState": "Playing"}
    limit = 60

    def run(load_wait, replies, slow_start=False, poll=None):
        ck = _Clock()
        starts = []

        class Bridge:
            timeout = 120.0

            def _set_call_timeout(self, seconds):
                self.timeout = seconds

            def call(self, tool, params):
                if tool == "rimworld/load_game_ready":
                    return {"success": True}
                if tool == "rimworld/get_game_info":
                    return next(replies)
                assert tool == G.TOOLS["start"], tool
                starts.append(ck())
                if slow_start:
                    ck.sleep(self.timeout)
                    raise TimeoutError("bridge did not answer")
                if poll is not None:
                    return {"success": True, "runId": "r2", "scenarios": ["save_reload_b"], "tickMode": "batch"}
                return {"success": False, "message": "no current map"}

        def run_once(session, calls, args, recipe, resume=None, *rest):
            return real_run_once(session, calls, args, recipe, resume, *rest) if resume else first

        real_run_once = G.run_once
        bridge = Bridge()
        argv = ["--recipe", "save_reload"]
        if load_wait is not None:
            argv += ["--load-wait", str(load_wait)]
        if poll is not None:
            argv += ["--poll", str(poll)]
        with (patch.object(G.P, "_connect", return_value=bridge),
              patch.object(G, "run_once", run_once),
              patch.object(G.time, "sleep", ck.sleep),
              patch.object(G, "resume_loop", partial(G.resume_loop, clock=ck, sleep=ck.sleep)),
              patch.object(G, "wait_for_map", partial(G.wait_for_map, clock=ck, sleep=ck.sleep))):
            rc = G.main(argv)
        assert rc == 1 and bridge.timeout == 120.0
        return ck(), starts

    # The first start races the load. The retry sees empty, missing and invalid map data.
    unready = [None, {}, {"mapCount": 1, "ticksGame": "invalid"}]
    elapsed, starts = run(limit, iter([ready] * 3 + unready * 30))
    assert elapsed <= limit, "resume used %.1f s with a %d s budget" % (elapsed, limit)
    assert elapsed == limit and starts == [2.0], (elapsed, starts)
    # A start that blocks consumes only the time remaining after the map polls.
    elapsed, starts = run(limit, iter([ready] * 3), slow_start=True)
    assert elapsed == limit and starts == [2.0], (elapsed, starts)
    # B can start before the deadline but its status poll must fit in the same budget.
    assert run(limit, iter([ready] * 3), poll=90) == (60.0, [2.0])
    # Fractional budgets clip poll and retry sleeps. A zero budget skips the callbacks.
    assert run(0.5, iter([{"mapCount": "invalid", "ticksGame": 1001}])) == (0.5, [])
    assert run(2.5, iter([ready] * 3)) == (2.5, [2.0])
    assert run(0, iter([])) == (0.0, [])

    # The flag is optional. Explicit malformed values must fail before connecting.
    assert run(None, iter([None] * 600)) == (600.0, [])
    for value in ("", "invalid", "nan", "inf", "-1"):
        with patch.object(G.P, "_connect") as connect, redirect_stderr(StringIO()):
            try:
                G.main(["--load-wait", value])
                raise AssertionError("invalid --load-wait accepted: %r" % value)
            except SystemExit as ex:
                assert ex.code == 2 and not connect.called, value
    return 12


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
