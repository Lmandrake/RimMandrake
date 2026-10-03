#!/usr/bin/env python3
"""Offline selftest for belt_watchdog.py, belt_heartbeat.py and focus_heal.py -- no game, no bridge, no Windows.

Fixtures are the real outputs of 2026-10-03's hang classes, copied inline (Transient/ files expire in ~14 days):
rerun13's instant focus death, rerun12's bridge timeout, load 7's QuestNode_TradeRequest loop, load 5's per-frame
RealFoW exception, and a one-time load burst that must NOT read as a loop.
"""
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import belt_heartbeat  # noqa: E402
import belt_watchdog as w  # noqa: E402
import focus_heal  # noqa: E402

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, ("  -- %s" % detail) if detail and not ok else ""))


RERUN13 = """== situational_rerun
UNMEASURED situational_rerun -- RuntimeError: could not bring RimWorld forward; foreground is 'Noah Floersch - Green Flash Sunset'. Bridge calls that touch the game will time out until it is focused.
  results: \\\\wsl.localhost\\Ubuntu\\home\\mandrake\\rm\\foundry\\Transient\\modcheck\\live_queue_results.jsonl
"""
RERUN12_TAIL = """  ok   every recorded surprise has its evidence on disk
UNMEASURED situational_rerun -- RimBridgeError: timed out after 30.0s waiting for the bridge; RimWorld may be in a long event or the call may be frame-bound
  results: \\\\wsl.localhost\\Ubuntu\\home\\mandrake\\rm\\foundry\\Transient\\modcheck\\live_queue_results.jsonl
"""
IN_PROGRESS = """== situational_rerun
  -- Bacta
[bacta] 15:34:29 site_ready_scar FAIL RimBridgeError: timed out after 30.0s waiting for the bridge
"""
QUEST_BLOCK = """Exception test running QuestNode_TradeRequest_RandomOfferDuration: System.NullReferenceException: Object reference not set to an instance of an object
[Ref 18389293] Duplicate stacktrace, see ref for original

Slate vars:
map=Map-1-PlayerHome
points=%d
siteTile=111545,0
"""
QUEST_LOOP = "".join(QUEST_BLOCK % (1000 + i) for i in range(60))
FOW_LOOP = "".join("Exception in RimWorldRealFoW.MapComponentSeenFog.Update: System.IndexOutOfRangeException: Index "
                   "was outside the bounds of the array.\nRimWorldRealFoW.MapComponentSeenFog:MapComponentUpdate ()\n"
                   "  at Verse.MapComponentUtility.MapComponentUpdate\n" for _ in range(40))
LOAD_BURST = ("".join("Exception spawning loaded thing Granite%d: System.NullReferenceException: Object reference\n" % i
                      for i in range(200)) + "".join("Loaded map component %d\n" % i for i in range(400)))


def t_analysers():
    ro = w.run_output_state(RERUN13)
    check("rerun13 output reads FINISHED UNMEASURED", ro["finished"] and ro["status"] == "UNMEASURED", ro)
    check("rerun13 cause maps to the focus remedy", "focus" in w.cause_remedy(ro["cause"]), w.cause_remedy(ro["cause"]))
    ro12 = w.run_output_state(RERUN12_TAIL)
    check("rerun12 cause maps to the starved-bridge remedy", "starved" in w.cause_remedy(ro12["cause"]))
    check("an in-progress output is not finished", not w.run_output_state(IN_PROGRESS)["finished"])
    q = w.exception_loop(QUEST_LOOP)
    check("QuestNode_TradeRequest loop detected", q and q["loop"] and q["count"] >= 60, q)
    check("QuestNode loop gets the kill+relaunch remedy", q and "quest test-run" in q["remedy"], q)
    f = w.exception_loop(FOW_LOOP)
    check("RealFoW per-frame loop detected", f and f["loop"], f)
    check("RealFoW remedy names mlie.nwnrealfogofwar", f and "nwnrealfogofwar" in f["remedy"], f)
    b = w.exception_loop(LOAD_BURST)
    check("a load-time burst followed by normal lines is NOT a loop", b and not b["loop"], b)
    check("no error lines -> None", w.exception_loop("all fine\nloaded\n") is None)
    win = [{"type": "LudeonTK.EditWindow_Log"}, {"type": "Verse.ImmediateWindow"},
           {"type": "RimWorld.Dialog_NamePlayerFactionAndSettlement", "forcePause": True},
           {"type": "Verse.Dialog_ModSettings"}]
    check("naming + ModSettings dialogs are flagged, debug windows are not",
          w.bad_windows(win) == ["Dialog_NamePlayerFactionAndSettlement", "Dialog_ModSettings"], w.bad_windows(win))
    v, cause, rem = w.compose([w.Sig("a", w.OK, "x"), w.Sig("b", w.STALLED, "slow", "r1"),
                               w.Sig("c", w.DEAD, "gone", "r2")])
    check("compose takes the worst signal", v == "DEAD" and "gone" in cause and rem == "r2", (v, cause, rem))
    check("compose all-OK is HEALTHY", w.compose([w.Sig("a", w.OK, "x")])[0] == "HEALTHY")


def t_gather(tmp):
    hb = os.path.join(tmp, "hb")
    trans = os.path.join(tmp, "Transient")
    os.makedirs(trans)
    log = os.path.join(tmp, "Player.log")
    with open(log, "w") as f:
        f.write("ok\n")
    ro = os.path.join(trans, "belt_rerun13_x.txt")
    with open(ro, "w") as f:
        f.write(RERUN13)
    with open(os.path.join(trans, "belt_bridge_log_x.md"), "w") as f:
        f.write("- x\n")
    game = {"game": {"pid": 1, "cpu": 10.0, "responding": True, "age": 3000}, "py": [], "fg": "RimWorld by Ludeon"}
    br = {"ok": True, "connect_ms": 5, "state": {"programState": "Playing"}, "main_ms": 30, "windows": []}
    kw = dict(bridge=True, player_log=log, win=game, br=br, hb_dir=hb, transient=trans,
              results=os.path.join(tmp, "none.jsonl"), runners=[])
    sigs = w.gather(**kw)
    v = w.compose(sigs)[0]
    check("rerun13 fixture, no runner process -> DEAD (the run is over, stop polling)", v == "DEAD",
          w.report(sigs))
    with open(ro, "w") as f:
        f.write(IN_PROGRESS)
    sigs = w.gather(**dict(kw, runners=[]))
    check("output with no verdict and NO runner -> DEAD (killed run)", w.compose(sigs)[0] == "DEAD", w.report(sigs))
    sigs = w.gather(**dict(kw, runners=["win:9 situational_rerun.py"]))
    check("same output WITH a runner, all else fine -> HEALTHY", w.compose(sigs)[0] == "HEALTHY", w.report(sigs))
    sigs = w.gather(**dict(kw, runners=["win:9 x"], win=dict(game, fg="Noah Floersch - Green Flash Sunset")))
    check("unfocused game during a run -> STALLED with the focus remedy",
          w.compose(sigs)[0] == "STALLED" and "game_focus" in w.compose(sigs)[2], w.report(sigs))
    sigs = w.gather(**dict(kw, runners=["win:9 x"], br=dict(br, windows=[{"type": "Verse.Dialog_ModSettings"}])))
    check("ModSettings open during a run -> WEDGED", w.compose(sigs)[0] == "WEDGED", w.report(sigs))
    sigs = w.gather(**dict(kw, win=dict(game, game=None)))
    check("no game process -> DEAD", w.compose(sigs)[0] == "DEAD")
    with open(log, "w") as f:
        f.write(QUEST_LOOP)
    old = time.time() - 900
    os.utime(log, (old, old))
    sigs = w.gather(**dict(kw, runners=["win:9 x"]))
    pl = [s for s in sigs if s.name == "player_log"][0]
    check("frozen log ending in the QuestNode loop -> WEDGED", pl.level == w.WEDGED and "frozen" in pl.detail,
          pl.line())
    with open(log, "w") as f:
        f.write("ok\n")
    sigs = w.gather(**dict(kw, runners=["win:9 x"], br=dict(br, main_error="timed out after 8.0s")))
    check("bridge pings but main thread times out -> STALLED", any(
        s.name == "bridge" and s.level == w.STALLED for s in sigs), w.report(sigs))
    # 'Not Responding' that persists across two watchdog calls >240 s apart -> WEDGED
    nr = dict(game, game=dict(game["game"], responding=False))
    w.gather(**dict(kw, runners=["win:9 x"], win=nr, now=time.time() - 300))
    sigs = w.gather(**dict(kw, runners=["win:9 x"], win=dict(nr, game=dict(nr["game"], cpu=310.0))))
    g = [s for s in sigs if s.name == "game"][0]
    check("Not Responding for 5 min at a full core -> WEDGED (tight loop)", g.level == w.WEDGED and "tight loop"
          in g.detail, g.line())
    # heartbeat files
    os.makedirs(hb, exist_ok=True)
    now = time.time()
    with open(os.path.join(hb, "heartbeat_situational_rerun.json"), "w") as f:
        json.dump({"job": "situational_rerun", "ts": now - 600, "step": "suite Bacta", "finished": False}, f)
    sigs = w.gather(**dict(kw, runners=[]))
    h = [s for s in sigs if s.name == "heartbeat"][0]
    check("stale heartbeat with no runner -> DEAD", h.level == w.DEAD, h.line())
    with open(os.path.join(hb, "heartbeat_situational_rerun.json"), "w") as f:
        json.dump({"job": "situational_rerun", "ts": now - 5, "step": "suite Bacta", "step_started": now - 2000,
                   "step_budget_s": 1500, "finished": False}, f)
    sigs = w.gather(**dict(kw, runners=["win:9 x"]))
    h = [s for s in sigs if s.name == "heartbeat"][0]
    check("fresh beat but step over budget -> WEDGED", h.level == w.WEDGED and "BUDGET" in h.detail, h.line())


def t_heartbeat(tmp):
    belt_heartbeat.STATE_DIR = os.path.join(tmp, "hb2")
    p = belt_heartbeat.start("jobx", thread=False)
    belt_heartbeat.step("suite A", budget_s=10)
    rec = json.load(open(p))
    check("heartbeat written with step and budget", rec["step"] == "suite A" and rec["step_budget_s"] == 10, rec)
    check("over_budget None inside budget", belt_heartbeat.over_budget(rec, rec["step_started"] + 5) is None)
    check("over_budget names the step past budget", "suite A" in (belt_heartbeat.over_budget(
        rec, rec["step_started"] + 11) or ""))
    fired, exited = [], []
    belt_heartbeat._on_budget = fired.append
    belt_heartbeat._exit = exited.append
    try:
        belt_heartbeat._check_budget(now=time.time() + 60)
    finally:
        belt_heartbeat._exit = os._exit
    rec = json.load(open(p))
    check("budget breach calls on_budget, marks finished UNMEASURED, exits 4",
          fired and exited == [belt_heartbeat.EXIT_BUDGET] and rec["finished"] and rec["status"] == "UNMEASURED",
          (fired, exited, rec))
    belt_heartbeat.start("joby", thread=False)
    belt_heartbeat.stop(status="PASS")
    r = belt_heartbeat.read("joby")
    check("stop() leaves a finished record read() can see", r and r[0]["finished"] and r[0]["status"] == "PASS", r)


def t_focus():
    titles = iter(["Chrome", "Chrome", "Chrome", "RimWorld by Ludeon Studios"])
    calls = []
    steps = [("a", lambda: calls.append("a")), ("b", lambda: calls.append("b"))]
    att = focus_heal.escalate(steps, lambda: next(titles), rounds=2, sleep=lambda s: None)
    check("escalation keeps climbing until RimWorld is in front", calls == ["a", "b", "a"] and
          att[-1][1].startswith("RimWorld"), (calls, att))
    try:
        focus_heal.escalate(steps, lambda: "Noah Floersch - Green Flash Sunset", rounds=2, sleep=lambda s: None,
                            prior=[("gentle_retries", "x")])
        check("never-focusing raises FocusLost", False)
    except focus_heal.FocusLost as e:
        check("never-focusing raises FocusLost carrying every attempt (1 prior + 4)", len(e.attempts) == 5 and
              "FOCUS_LOST" in str(e) and isinstance(e, RuntimeError), e.attempts)

    def boom():
        raise RuntimeError("no RimWorldWin64 process")
    try:
        focus_heal.escalate([("x", boom)], lambda: "Chrome", sleep=lambda s: None)
        check("a fatal step stops the ladder", False)
    except focus_heal.FocusLost as e:
        check("a fatal step stops the ladder at once", len(e.attempts) == 1 and "FATAL" in e.attempts[0][1])
    check("EXIT_FOCUS_LOST and EXIT_BUDGET are distinct from 0/1/2",
          len({0, 1, 2, focus_heal.EXIT_FOCUS_LOST, belt_heartbeat.EXIT_BUDGET}) == 5)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        t_analysers()
        t_gather(tmp)
        t_heartbeat(tmp)
    t_focus()
    print("\n%d/%d passed" % (sum(RESULTS), len(RESULTS)))
    sys.exit(0 if all(RESULTS) else 1)
