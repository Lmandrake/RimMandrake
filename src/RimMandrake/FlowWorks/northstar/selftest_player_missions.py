"""Selftest for player_missions.py: whitelist, friction, timing, deadline, events, verify, dry-run PASS/FAIL.

    python3 src/RimMandrake/FlowWorks/northstar/selftest_player_missions.py

Offline only (the dry-run fake). Every check that could pass vacuously has a paired negative.
"""
import contextlib
import copy
import io
import json
import os
import pickle
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import player_missions as pm  # noqa: E402

FAILS = []
N = [0]


def ok(cond, what):
    N[0] += 1
    if not cond:
        FAILS.append(what)
        print("FAIL", what)


def run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = pm.main(argv)
    return rc, buf.getvalue()


def refused(spec, tool, args, **kw):
    try:
        pm.check_action(spec, tool, args, **kw)
        return None
    except pm.Refused as r:
        return str(r)


def test_whitelist(spec):
    for tool in spec["refused"]:
        ok(refused(spec, tool, {}) is not None, "refused list blocks %s" % tool)
    ok(refused(spec, "jawa/teleport_pawn", {}) is not None, "pattern blocks an unknown teleport tool")
    ok("not on the player whitelist" in (refused(spec, "jawa/totally_new", {}) or ""), "unknown tool refused")
    ok("unknown parameter" in (refused(spec, "rimworld/click_cell", {"x": 1, "z": 2, "banana": 3}) or ""),
       "unknown param refused (the bridge would drop it silently)")
    ok(refused(spec, "rimworld/click_cell", {"x": 1, "z": 2}) is None, "a plain whitelisted call passes")
    sent = pm.check_action(spec, "jawa/flowworks_body_report", {"x": 1, "z": 1, "classify": True})
    ok(sent["classify"] is False, "body_report classify forced false")
    sent = pm.check_action(spec, "rimworld/apply_architect_designator", {"designatorId": "d", "x": 1, "z": 1})
    ok(sent["keepSelected"] is False, "designator never left armed")
    ok(refused(spec, "rimworld/step_game_ticks", {"ticks": 2001}) is not None, "tick cap enforced")
    ok(refused(spec, "rimworld/step_game_ticks", {"ticks": 2000}) is None, "tick cap is inclusive")
    ok(refused(spec, "rimworld/execute_gizmo", {"gizmoId": "g1"}, gizmo_label="DEV: Deepen") is not None,
       "dev gizmo label refused")
    ok(refused(spec, "rimworld/execute_gizmo", {"gizmoId": "g1"}, gizmo_label="Ladder raised") is None,
       "player gizmo label allowed")
    ok(refused(spec, "rimworld/execute_context_menu_option", {"label": "Dev: instant dig"}) is not None,
       "dev menu option label refused")
    for t in spec["whitelist"]:
        for pat in spec["refused_patterns"]:
            ok(pat not in t.lower(), "whitelisted %s does not trip pattern %s" % (t, pat))


def test_friction(spec):
    f, _ = pm.friction_flags("rimworld/apply_architect_designator", {}, {"success": False}, False, [])
    ok("failed_placement" in f and "unclear_refusal" in f, "silent failed placement -> failed_placement+unclear")
    f, _ = pm.friction_flags("rimworld/apply_architect_designator", {}, {"success": False, "message": "rock"}, False, [])
    ok("unclear_refusal" not in f, "a refusal WITH a reason is not unclear")
    prior = [{"kind": "act", "tool": "rimworld/apply_architect_designator", "args_norm": pm._norm({"x": 1})}]
    f, _ = pm.friction_flags("rimworld/apply_architect_designator", {"x": 1}, {"success": True}, True, prior)
    ok("repeated_attempt" in f, "same designation twice -> repeated_attempt")
    prior = [{"kind": "act", "tool": "rimworld/step_game_ticks", "args_norm": pm._norm({"ticks": 9})}]
    f, _ = pm.friction_flags("rimworld/step_game_ticks", {"ticks": 9}, {"success": True}, True, prior)
    ok("repeated_attempt" not in f, "repeated time steps are not friction")


def test_loop(spec, tmp):
    runs = os.path.join(tmp, "runs")
    T = [1000.0]
    real_wall = pm.CLOCK.wall
    pm.CLOCK.wall = staticmethod(lambda: T[0])
    try:
        rc, out = run(["--runs", runs, "start", "canal", "--dry-run"])
        ok(rc == 0 and "FIXTURE: 4 ops" in out, "dry-run start + fixture")
        T[0] += 7.0
        rc, out = run(["--runs", runs, "act", "rimworld/apply_architect_designator",
                       json.dumps({"designatorId": "Designator_DigCanal_fake", "x": 50, "z": 58, "width": 17,
                                   "height": 1}), "--intent", "row"])
        ok(rc == 0, "designate row")
        rd = pm.current_run_in(runs)
        rows = pm.read_actions(rd)
        ok(abs(rows[-1]["think_s"] - 7.0) < 1e-6, "think_s = gap since mission start (7 s)")
        # game left running while the agent thinks: advance the fake's clock by hand
        p = os.path.join(rd, "fake.pickle")
        st = pickle.load(open(p, "rb"))
        st["ticks"] += 444
        pickle.dump(st, open(p, "wb"))
        T[0] += 3.0
        run(["--runs", runs, "act", "rimworld/apply_architect_designator",
             json.dumps({"designatorId": "Designator_DigCanal_fake", "x": 65, "z": 52, "width": 1, "height": 16})])
        rows = pm.read_actions(rd)
        ok(abs(rows[-1]["think_s"] - 3.0) < 1e-6, "think_s = gap since previous action (3 s)")
        ok(rows[-1]["ticks_during_think"] == 444, "ticks that passed during the think gap are counted")
        T[0] += 1.0
        rc, out = run(["--runs", runs, "act", "jawa/flowworks_excavation_drive", json.dumps({"x": 1, "z": 1})])
        ok(rc == 2 and "REFUSED" in out, "dev shortcut refused at the CLI")
        ok(pm.read_actions(rd)[-1].get("refused"), "refusal is logged")
        # inject a storyteller event at +1000 ticks and check it fires once
        r = pm.read_run(rd)
        r["events"] = [{"at_ticks": 1000, "tool": "jawa/weather_set", "args": {"weather": "Clear"}}]
        pm.write_run(rd, r)
        for _ in range(6):
            T[0] += 2.0
            run(["--runs", runs, "act", "rimworld/step_game_ticks", json.dumps({"ticks": 2000})])
        ev = [x for x in pm.read_actions(rd) if x["kind"] == "event"]
        ok(len(ev) == 1 and ev[0]["tool"] == "jawa/weather_set", "event fires exactly once when its tick passes")
        T[0] += 1.0
        run(["--runs", runs, "observe", "--shot"])
        run(["--runs", runs, "note", "unclear_feedback", "selftest"])
        rc, out = run(["--runs", runs, "report", "--json"])
        rep = json.loads(out)
        ok(rep["verdict"] == "PASS", "dry-run canal reaches PASS by digging (got %s)" % rep["verdict"])
        t = rep["timing"]
        ok(t["screenshots"] == 1, "screenshot counted")
        ok(t["refused"] == 1, "refused counted")
        ok(t["ticks_by_actions"] == 12000, "ticks by actions summed (got %s)" % t["ticks_by_actions"])
        ok(t["ticks_during_think"] == 444, "ticks during think summed")
        ok(abs(t["think_s"] - (7 + 3 + 1 + 12 + 1 + 0)) < 1e-6, "think total = sum of gaps (got %s)" % t["think_s"])
        kinds = [f for fr in rep["friction"] for f in fr["flags"]]
        ok("refused_by_driver" in kinds and "unclear_feedback" in kinds, "friction log carries both sources")

        # negative: a run that never designates FAILs, then TIMEOUTs past the action budget
        runs2 = os.path.join(tmp, "runs2")
        run(["--runs", runs2, "start", "canal", "--dry-run"])
        rd2 = pm.current_run_in(runs2)
        r = pm.read_run(rd2)
        r["deadline"]["actions"] = 3
        pm.write_run(rd2, r)
        rc, out = run(["--runs", runs2, "report", "--json"])
        ok(json.loads(out)["verdict"] == "FAIL", "no digging -> FAIL")
        for _ in range(3):
            run(["--runs", runs2, "act", "rimworld/step_game_ticks", json.dumps({"ticks": 100})])
        rc, out = run(["--runs", runs2, "act", "rimworld/step_game_ticks", json.dumps({"ticks": 100})])
        ok(rc == 3 and "DEADLINE" in out, "action budget ends the mission")
        rc, out = run(["--runs", runs2, "act", "rimworld/step_game_ticks", json.dumps({"ticks": 100})])
        ok(rc == 3, "no actions after the deadline")
        rc, out = run(["--runs", runs2, "report", "--json"])
        ok(json.loads(out)["verdict"] == "TIMEOUT", "FAIL past the deadline reads TIMEOUT")
        # a goal met only AFTER the game-time deadline is TIMEOUT, never PASS
        runs5 = os.path.join(tmp, "runs5")
        run(["--runs", runs5, "start", "canal", "--dry-run"])
        run(["--runs", runs5, "act", "rimworld/apply_architect_designator",
             json.dumps({"designatorId": "Designator_DigCanal_fake", "x": 50, "z": 58, "width": 17, "height": 1})])
        run(["--runs", runs5, "act", "rimworld/apply_architect_designator",
             json.dumps({"designatorId": "Designator_DigCanal_fake", "x": 65, "z": 52, "width": 1, "height": 16})])
        for _ in range(6):
            run(["--runs", runs5, "act", "rimworld/step_game_ticks", json.dumps({"ticks": 2000})])
        rd5 = pm.current_run_in(runs5)
        p5 = os.path.join(rd5, "fake.pickle")
        st5 = pickle.load(open(p5, "rb"))
        st5["ticks"] += spec["missions"]["canal"]["deadline"]["ticks"] + 1000
        pickle.dump(st5, open(p5, "wb"))
        rc, out = run(["--runs", runs5, "report", "--json"])
        rep5 = json.loads(out)
        ok(rep5["verdict"] == "TIMEOUT" and "game-time deadline" in (rep5["deadline"] or ""),
           "goal met past the tick deadline is TIMEOUT, not PASS (got %s)" % rep5["verdict"])
        # wall deadline
        runs3 = os.path.join(tmp, "runs3")
        run(["--runs", runs3, "start", "canal", "--dry-run"])
        T[0] += spec["missions"]["canal"]["deadline"]["wall_s"] + 1
        rc, out = run(["--runs", runs3, "act", "rimworld/get_game_info", "{}"])
        ok(rc == 3, "wall deadline ends the mission")
        # an action the fake cannot model is a transport limitation, not game friction
        runs4 = os.path.join(tmp, "runs4")
        run(["--runs", runs4, "start", "canal", "--dry-run"])
        run(["--runs", runs4, "act", "rimworld/open_main_tab", json.dumps({"mainTabId": "Work"})])
        last = pm.read_actions(pm.current_run_in(runs4))[-1]
        ok(last.get("transport_limitation") is True, "unmodelled tool flagged transport_limitation")
    finally:
        pm.CLOCK.wall = real_wall


def test_verify(spec):
    dump = pm.load_dump()
    src = pm.scan_source_tools()
    ok(len(src) > 50, "source scan sees the companion's [Tool]s (%d)" % len(src))   # sanity probe
    ok("jawa/flowworks_pit_report" in src and "x" in src["jawa/flowworks_pit_report"], "probe: a known tool+param")
    if dump is None:
        print("SKIP verify-vs-dump: Transient/bench_tools_dump.json absent (UNMEASURED, not passed)")
    else:
        rows, problems = pm.verify(spec, dump, src)
        ok(not problems, "every verified claim re-derives: %s" % problems)
    bad = copy.deepcopy(spec)
    bad["whitelist"]["rimworld/click_cell"]["params"].append("noSuchParam")
    bad["whitelist"]["jawa/invented_tool"] = {"cls": "read", "params": [], "verified": "source"}
    _, problems = pm.verify(bad, dump or {}, src)
    ok(any("click_cell" in p for p in problems) or dump is None, "verify catches a wrong param")
    ok(any("invented_tool" in p for p in problems), "verify catches an invented tool")


class TankStub(object):
    """Just enough bridge for the chain goal: tanks {id: (x, z, units)}, one colonist, a click -> selection."""

    def __init__(self, tanks, colonist=(30, 0), sem_names_id=True, things_key=True, complete_field=True):
        self.tanks, self.col, self.names, self.things_key = dict(tanks), colonist, sem_names_id, things_key
        self.complete_field = complete_field      # False = an older list_things reply without isCompleteList
        self.sel = None

    def call(self, tool, a):
        if tool == "rimworld/list_colonists":
            return {"colonists": [{"name": "Ada", "position": {"x": self.col[0], "z": self.col[1]}}]}
        if tool == "jawa/list_pawns":
            return {"pawns": [{"name": "Ada", "health": {"hediffs": []}}]}
        if tool == "jawa/list_things":
            if not self.things_key:
                return {"success": False}
            x, z, w, h = [int(v) for v in a.get("rect", "0,0,1000,1000").split(",")]   # no rect = whole map
            hit = [{"id": i, "position": {"x": t[0], "z": t[1]}} for i, t in self.tanks.items()
                   if x <= t[0] < x + w and z <= t[1] < z + h]
            lim = int(a.get("limit", 200))
            reply = {"things": hit[:lim]}
            if self.complete_field:
                reply.update(isCompleteList=len(hit) <= lim, truncated=max(0, len(hit) - lim))
            return reply
        if tool == "rimworld/click_cell":
            self.sel = next((i for i, t in self.tanks.items() if (t[0], t[1]) == (a["x"], a["z"])), None)
            return {"success": True}
        if tool == "rimworld/get_selection_semantics":
            if self.sel is None:
                return {"selection": []}
            u = self.tanks[self.sel][2]
            return {"selection": [{"thingId": self.sel if self.names else "RM_LiquidTank999999",
                                   "inspect": "Holding: Water (%g / 500 units)" % u}]}
        raise RuntimeError(tool)


def test_chain_goal(spec):
    m = spec["missions"]["chain"]
    rects = pm.landmark_rects(m, (60, 60))      # site 44,48,32,24 ; far_bank 67,48,9,24
    run_ = {"goal_check": m["goal_check"], "rects": {k: list(v) for k, v in rects.items()}}
    def verdict(stub, baseline):
        r = dict(run_)
        if baseline != "absent":
            r["tank_baseline"] = baseline
        return pm.goal_check(stub, r)
    v, ev = verdict(TankStub({"RM_LiquidTank1": (50, 60, 40)}, colonist=(70, 60)), {})
    ok(v == "PASS" and ev["destTank"] == "RM_LiquidTank1", "new destination tank filled 40 -> PASS (%s)" % v)
    # the G6.5 defect: a filled tank OUTSIDE the destination rect used to pass the goal
    v, ev = verdict(TankStub({"RM_LiquidTank2": (5, 5, 400), "RM_LiquidTank1": (50, 60, 0)}, colonist=(70, 60)), {})
    ok(v == "FAIL" and all(t["id"] != "RM_LiquidTank2" for t in ev["destTanks"]),
       "a full tank elsewhere on the map does not pass the goal (%s)" % v)
    # ... and one that already held water before the mission: the delta, not the level, is the goal
    v, ev = verdict(TankStub({"RM_LiquidTank1": (50, 60, 400)}, colonist=(70, 60)), {"RM_LiquidTank1": 395.0})
    ok(v == "FAIL" and ev["destTanks"][0]["delta"] == 5.0, "pre-filled tank +5 < min_units -> FAIL (%s)" % v)
    v, _ = verdict(TankStub({"RM_LiquidTank1": (50, 60, 400)}, colonist=(70, 60)), {"RM_LiquidTank1": 380.0})
    ok(v == "PASS", "pre-filled tank +20 -> PASS (%s)" % v)
    # identity: a selection that names a DIFFERENT tank does not count as this tank's units
    v, ev = verdict(TankStub({"RM_LiquidTank1": (50, 60, 40)}, colonist=(70, 60), sem_names_id=False), {})
    ok(v == "UNMEASURED" and ev["destTanks"][0]["units"] is None, "units read off another tank -> UNMEASURED (%s)" % v)
    v, _ = verdict(TankStub({"RM_LiquidTank1": (50, 60, 40)}, colonist=(70, 60)), None)
    ok(v == "UNMEASURED", "unread start baseline -> UNMEASURED, never PASS (%s)" % v)
    v, _ = verdict(TankStub({"RM_LiquidTank1": (50, 60, 40)}, colonist=(70, 60), things_key=False), {})
    ok(v == "UNMEASURED", "list_things without things -> UNMEASURED (%s)" % v)
    v, _ = verdict(TankStub({}, colonist=(70, 60)), {})
    ok(v == "FAIL", "no destination tank built -> FAIL (%s)" % v)
    v, _ = verdict(TankStub({"RM_LiquidTank1": (50, 60, 40)}, colonist=(50, 60)), {})
    ok(v == "FAIL", "tank filled but nobody across -> FAIL (%s)" % v)
    # a run.json written before P14 has no baseline key: deltas from 0 would let a pre-filled tank pass
    v, ev = verdict(TankStub({"RM_LiquidTank1": (50, 60, 400)}, colonist=(70, 60)), "absent")
    ok(v == "UNMEASURED" and "no tank_baseline" in ev.get("why", ""),
       "a pre-fix run.json with no baseline key -> UNMEASURED, never PASS (%s)" % v)
    # truncated listing (limit 50): 51 tanks in the destination, the 51st never listed
    many = dict(("RM_LiquidTank%d" % (100 + i), (44 + i % 32, 48 + i // 32, 0)) for i in range(51))
    many["RM_LiquidTank100"] = (44, 48, 40)
    last = "RM_LiquidTank150"
    v, ev = verdict(TankStub(many, colonist=(70, 60)), {"RM_LiquidTank100": 0.0, last: 0.0})
    ok(v == "UNMEASURED" and last in ev.get("why", ""), "truncated page missing a tracked tank -> UNMEASURED (%s)" % v)
    v, ev = verdict(TankStub(many, colonist=(70, 60)), {"RM_LiquidTank100": 0.0})
    ok(v == "PASS" and ev["destListComplete"] is False, "truncated page, every tracked tank listed, delta met -> PASS (%s)" % v)
    flat = dict(many, RM_LiquidTank100=(44, 48, 0))
    v, ev = verdict(TankStub(flat, colonist=(70, 60)), {"RM_LiquidTank100": 0.0})
    ok(v == "UNMEASURED", "truncated page, no delta met -> UNMEASURED, an unlisted tank could hold it (%s)" % v)
    fifty = dict(list(many.items())[:50])
    v, _ = verdict(TankStub(fifty, colonist=(70, 60), complete_field=False), {"RM_LiquidTank101": 0.0, last: 0.0})
    ok(v == "UNMEASURED", "a full page on a reply without isCompleteList counts as truncated (%s)" % v)
    v, _ = verdict(TankStub(fifty, colonist=(70, 60)), {"RM_LiquidTank100": 0.0})
    ok(v == "PASS", "exactly 50 with isCompleteList true is complete -> PASS (%s)" % v)
    ok(pm.tank_baseline(TankStub(many), m["goal_check"], rects) is None,
       "a truncated start listing records no baseline (None)")
    b = pm.tank_baseline(TankStub({"RM_LiquidTank1": (50, 60, 7), "RM_LiquidTank2": (5, 5, 9)}), m["goal_check"], rects)
    ok(b == {"RM_LiquidTank1": 7.0}, "start baseline records only destination tanks, by id (%s)" % b)
    ok(pm.tank_baseline(TankStub({}), spec["missions"]["canal"]["goal_check"], rects) is None,
       "non-chain missions take no tank baseline")


def main():
    spec = pm.load_spec()
    pm.run_spec_cache.update(spec)
    tmp = tempfile.mkdtemp(prefix="pm_selftest_")
    try:
        test_whitelist(spec)
        test_friction(spec)
        test_loop(spec, tmp)
        test_verify(spec)
        test_chain_goal(spec)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s %d/%d" % ("FAIL" if FAILS else "PASS", N[0] - len(FAILS), N[0]))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
