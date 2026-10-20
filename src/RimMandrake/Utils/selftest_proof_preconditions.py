"""Selftest of the precondition harness (PROOF_VERDICTS_REPAIR_SAME_BUG_EVERY_ROUND): no row can read PASS or FAIL over a
site or harness failure, and a real mod fault still reads FAIL.

    python3 src/RimMandrake/Utils/selftest_proof_preconditions.py

A  the mechanism (validation_core.guard/scope/require + modcheck/preconditions.py), on a toy proof whose read has the bug
   shape every review kept finding (an unread reply reads 0 and scores FAIL): each call kind refused, answered with no dict,
   a staging that did not take (build short, no pawn, not drafted, roof not written), a dead probe channel, a refused probe;
   `_answer`, require, adopt, quiet, sibling scopes, and no scope at all (the old behaviour, for every other harness user).
B  the modcheck Suite opt-in (Suite.preconditions): a refused bridge_call withholds a component's PASS/FAIL and files no
   finding; a real failed expectation is still FAIL with a finding; opted out, nothing changes.
C  the migrated scripts, swept with a fake bridge that refuses / no-ops each call kind they make:
   - FlowWorks proof_hose realflow, suspension_bridge_proof (--mock) and the Contagion suite (selftest_contagion's Fake):
     a refusal may only WITHHOLD a verdict -- no row reads a PASS/FAIL that the healthy run did not;
   - named staging calls the old per-call guards never covered withhold the rows that stand on them (these fail on the code
     before this item: it scored them FAIL or PASS);
   - can-fail: the healthy realflow fake moves nothing and its bars still read FAIL (MOD); the healthy suspension mock PASSes.
"""
import contextlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, ".."))
NORTHSTAR = os.path.join(SRC, "FlowWorks", "northstar")
for p in (HERE, os.path.join(HERE, "modcheck"), NORTHSTAR, os.path.join(SRC, "FlowWorks"), os.path.join(SRC, "Contagion")):
    if p not in sys.path:
        sys.path.insert(0, p)

FAILS = []
CHECKS = [0]


def check(name, cond, detail=""):
    CHECKS[0] += 1
    if cond:
        print("ok   " + name)
    else:
        FAILS.append(name)
        print("FAIL %s %s" % (name, str(detail)[:400]))


def quiet_out():
    return contextlib.redirect_stdout(io.StringIO())


# ============================================================================ A. the mechanism, on a toy proof
class ToyBridge(object):
    """A healthy game whose tank moves `units`; `fault` = (kind, target) breaks one call kind."""

    def __init__(self, units=500, fault=None):
        self.units, self.fault = units, fault or (None, None)

    def call(self, tool, **kw):
        kind, target = self.fault
        if target == tool and kind == "refuse":
            return {"success": False, "message": "refused (selftest)"}
        if target == tool and kind == "nondict":
            return "garbage"
        if target == tool and kind == "raise":
            raise RuntimeError("socket closed (selftest)")
        if tool == "jawa/build_batch":
            asked = len(kw["ops"].split(";"))
            return {"success": True, "survived": asked - 1 if (kind, target) == ("noop", tool) else asked}
        if tool == "jawa/spawn_pawn":
            return {"success": True, "pawns": [] if (kind, target) == ("noop", tool) else [{"id": 41}]}
        if tool == "jawa/set_draft":
            return {"success": True, "drafted": not ((kind, target) == ("noop", tool)) and kw.get("drafted")}
        if tool == "jawa/set_roof_batch":
            return {"success": True, "cellsChanged": 25, "cellsFailedVerify": 3 if (kind, target) == ("noop", tool) else 0}
        return {"success": True}

    def hp(self, cmd, wait_s=20.0):
        kind, target = self.fault
        if target == "probe" and kind == "dead":
            return {"success": False, "error": "hose probe timed out (no frame serviced it)"}
        if target == "probe" and kind == "refuse":
            return {"success": False, "error": "no tank at 1,1"}
        if target == "probe" and kind == "garbled":
            return {"success": False, "raw": "<<not json>>"}
        return {"success": True, "units": self.units}


TOY_CALLS = ("jawa/build_batch", "jawa/spawn_pawn", "jawa/set_draft", "jawa/set_roof_batch", "rimworld/step_game_ticks")


def toy_proof(V, B, rows, answer_tick=False):
    """The bug shape: stage, read, and score the read -- an unread reply reads 0."""
    B = V.guard(B)
    with V.scope("toy"):
        B.call("jawa/build_batch", ops="RM_LiquidTank:1,1;RM_LiquidPump:4,1")
        pid = ((B.call("jawa/spawn_pawn", kindDef="Colonist", x=1, z=1, count=1).get("pawns") or [{}])[0]).get("id")
        B.call("jawa/set_draft", pawnId=pid, drafted=True)
        B.call("jawa/set_roof_batch", ops="None:0,0,5,5")
        B.call("rimworld/step_game_ticks", ticks=60, _answer=answer_tick)
        units = B.hp("tank:1,1").get("units") or 0
        V.row(rows, "TOY_tank_filled", "PASS" if units > 0 else "FAIL", "MOD", {"units": units})
    return {r["id"]: r for r in rows}


def part_a():
    import validation_core as V
    with quiet_out():
        ok = toy_proof(V, ToyBridge(units=500), [])["TOY_tank_filled"]
        bad = toy_proof(V, ToyBridge(units=0), [])["TOY_tank_filled"]
    check("A healthy toy: the mod moved liquid -> PASS", ok["status"] == "PASS", ok)
    check("A can-fail: every precondition held, the mod moved nothing -> FAIL (MOD)", bad["status"] == "FAIL" and bad["class"] == "MOD", bad)
    cases = [(k, t) for t in TOY_CALLS for k in ("refuse", "nondict")]
    cases += [("noop", t) for t in TOY_CALLS[:4]] + [("dead", "probe"), ("refuse", "probe"), ("garbled", "probe")]
    for kind, target in cases:
        for units in (500, 0):
            with quiet_out():
                r = toy_proof(V, ToyBridge(units=units, fault=(kind, target)), [])["TOY_tank_filled"]
            check("A %s %s (mod %s): UNMEASURED, never PASS/FAIL" % (kind, target, "ok" if units else "broken"),
                  r["status"] == "UNMEASURED" and r["detail"].get("unmeasuredBecause") and r["class"] in ("SITE", "HARNESS"), r)
    # a call that raises is recorded before it propagates (the block's own handler reports the exception)
    rows = []
    try:
        with quiet_out():
            toy_proof(V, ToyBridge(fault=("raise", "jawa/spawn_pawn")), rows)
        raised = False
    except RuntimeError:
        raised = True
    check("A a call that raises still raises (the block handler records it), no row scored", raised and not rows, rows)
    with quiet_out():
        r = toy_proof(V, ToyBridge(units=0, fault=("refuse", "rimworld/step_game_ticks")), [], answer_tick=True)["TOY_tank_filled"]
    check("A _answer=True: a refusal that IS the measured answer withholds nothing (FAIL stands)", r["status"] == "FAIL", r)
    # require, adopt, quiet, sibling scopes, no scope
    rows = []
    with quiet_out():
        with V.scope("s"):
            V.require(False, "fixture present", "no fixture (selftest)")
            V.row(rows, "R_req", "PASS", "MOD", {})
        with V.scope("stage") as stg:
            V.require(False, "staged", "did not take")
        with V.scope("sibling"):
            V.row(rows, "R_sibling", "FAIL", "MOD", {})
        with V.scope("dependent"):
            V.adopt(stg)
            V.row(rows, "R_adopted", "FAIL", "MOD", {})
        with V.scope("q"):
            with V.quiet():
                V.require(False, "housekeeping", "ignored")
                V.guard(ToyBridge(fault=("refuse", "jawa/destroy_batch"))).call("jawa/destroy_batch", rects="0,0,1,1")
            V.row(rows, "R_quiet", "FAIL", "MOD", {})
        with V.scope("outer"):
            with V.scope("inner"):
                V.require(False, "inner staging", "x")
            V.row(rows, "R_after_inner", "PASS", "MOD", {})
            V.require(False, "outer staging", "x")
            with V.scope("inner2"):
                V.row(rows, "R_under_outer_fault", "PASS", "MOD", {})
        V.guard(ToyBridge(fault=("refuse", "jawa/build_batch"))).call("jawa/build_batch", ops="A:1,1")
        V.row(rows, "R_no_scope", "FAIL", "MOD", {})
    st = {r["id"]: (r["status"], r["class"]) for r in rows}
    check("A require() that does not hold -> UNMEASURED SITE", st["R_req"] == ("UNMEASURED", "SITE"), st)
    check("A a fault dies with its scope: a sibling scope's FAIL stands", st["R_sibling"] == ("FAIL", "MOD"), st)
    check("A adopt(): a closed staging scope's fault withholds the row that depends on it", st["R_adopted"][0] == "UNMEASURED", st)
    check("A quiet(): housekeeping with its own gate records nothing", st["R_quiet"] == ("FAIL", "MOD"), st)
    check("A an inner scope's fault does not reach the outer scope's later rows", st["R_after_inner"] == ("PASS", "MOD"), st)
    check("A an outer scope's fault reaches rows in scopes nested inside it", st["R_under_outer_fault"][0] == "UNMEASURED", st)
    check("A no scope open: the old behaviour exactly (other harness users)", st["R_no_scope"] == ("FAIL", "MOD"), st)
    check("A PRE holds no frame after the run", not V.PRE.frames, V.PRE.frames)


# ============================================================================ B. the modcheck Suite opt-in
class SuiteSession(object):
    def __init__(self, refuse=()):
        self.refuse = set(refuse)

    def call(self, tool, **kw):
        if tool in self.refuse:
            return {"success": False, "message": "refused (selftest)"}
        if tool == "jawa/read_value":
            return {"success": True, "value": kw.get("want")}
        return {"success": True}


def part_b():
    from suite import Suite, TestContext, ExpectationFailed

    def make(opt):
        s = Suite("PreconditionsSelftest")
        s.preconditions = opt

        @s.chain("toy")
        def toy(t):
            t.bridge_call("jawa/spawn_batch", ops="Steel:1,1")          # chain staging: taints every component after it
            with t.component("reads_value"):
                v = (t.bridge_call("jawa/read_value", want=7) or {}).get("value")
                if v != 7:
                    raise ExpectationFailed("read %r, want 7" % (v,))
            with t.component("mod_fault"):
                t.bridge_call("jawa/read_value", want=1)
                raise ExpectationFailed("the mod did the wrong thing (selftest)")
        return s

    def run(opt, refuse=()):
        s, findings = make(opt), []
        t = TestContext(SuiteSession(refuse), anchor=(10, 10), on_finding=findings.append)
        for _, fn in s.chains:
            fn(t)
        return {c.name: c.verdict for c in t.components}, findings

    v, f = run(True)
    check("B healthy: PASS, and a real mod fault is FAIL with a finding", v == {"reads_value": "PASS", "mod_fault": "FAIL"} and len(f) == 1, (v, f))
    v, f = run(True, refuse=("jawa/spawn_batch",))
    check("B a refused chain staging call: no component PASS or FAIL, no finding",
          v == {"reads_value": "UNMEASURED", "mod_fault": "UNMEASURED"} and not f, (v, [c.detail for c in f]))
    v, f = run(True, refuse=("jawa/read_value",))
    check("B a refused read inside a component: UNMEASURED, no finding", v.get("reads_value") == "UNMEASURED" and not f, (v, f))
    v, f = run(False, refuse=("jawa/read_value",))
    check("B opted out (every other suite): the old behaviour, a refused read is FAIL", v.get("reads_value") == "FAIL", v)


# ============================================================================ C1. proof_hose realflow
class RFFake(object):
    """A healthy flowworks map that moves nothing (so the bars FAIL: can-fail), with one call kind broken."""

    def __init__(self, refuse=None, noop=None):
        self.refuse, self.noop, self.kinds, self.tick, self.last_end, self.hoses = refuse, noop, [], 0, None, []

    def call(self, tool, **kw):
        if tool not in self.kinds:
            self.kinds.append(tool)
        if tool == self.refuse:
            return {"success": False, "message": "refused (selftest)"}
        if tool == "jawa/build_batch":
            asked = len([o for o in kw.get("ops", "").split(";") if o])
            return {"success": True, "survived": 0 if self.noop == tool else asked}
        if tool == "jawa/destroy_batch":
            return {"success": True, "destroyed": 0 if self.noop == tool and kw.get("categories") == "Building" else 1}
        if tool == "jawa/list_things":
            return {"success": True, "things": [{"id": 7}] if kw.get("defName") == "Battery" else []}
        if tool == "jawa/comp_read":
            return {"success": True, "values": {"heldUnits": 0}}
        if tool == "rimworld/list_selected_gizmos":
            return {"success": True, "gizmos": [{"label": "Job: Empty", "gizmoId": 1}]}
        return {"success": True}

    def hp(self, cmd, wait_s=20.0):
        k = "probe:" + cmd.split(":")[0]
        if k not in self.kinds:
            self.kinds.append(k)
        if k == self.refuse:
            return {"success": False, "error": "refused (selftest)"}
        if k == self.noop:
            return {"success": False, "error": "hose probe timed out (no frame serviced it)"}
        if cmd.startswith("lay:"):
            x0, z0, x1, z1 = (int(v) for v in cmd[4:].split(","))
            self.last_end = [x1 + 1, z1]
            self.hoses.append({"reel": [x0, z0], "id": 900 + len(self.hoses), "state": "Flat", "carry": "Laid"})
            return {"success": True}
        if cmd.startswith("tank:"):
            return {"success": True, "units": 500}
        if cmd.startswith("pump:"):
            return {"success": True, "powered": True}
        if cmd.startswith("settrail:"):
            return {"success": True, "carry": "Dropped"}
        if cmd.startswith("net:"):
            return {"success": True, "tanks": [{"tank": self.last_end}] if self.last_end else []}
        if cmd == "census":
            return {"success": True, "tick": self.tick, "hoses": list(self.hoses)}
        if cmd == "colonists":
            return {"success": True, "pawns": []}
        return {"success": True}

    def probe(self, cmd, wait_s=20.0):
        return {}

    def probe_of(self, t, cmd, wait_s=20.0, poll_s=0.3):
        return {}

    def ticks(self, n):
        self.tick += n
        return {"success": True}


def rf_run(**kw):
    import proof_hose as PH
    fb = RFFake(**kw)
    with quiet_out():
        rows = PH._rf(fb)["rows"]
    return {r["id"]: r for r in rows}, fb


def sweep_same_or_withheld(label, healthy, broken):
    """A refusal may only WITHHOLD a verdict: every PASS/FAIL row of the broken run reads what the healthy run read."""
    changed = {k: (healthy.get(k), v) for k, v in broken.items() if v in ("PASS", "FAIL") and healthy.get(k) != v}
    check("C %s: no row reads a PASS/FAIL the healthy run did not" % label, not changed, changed)


def part_c1():
    healthy, fb = rf_run()
    hv = {k: r["status"] for k, r in healthy.items()}
    check("C1 can-fail: the healthy fake moves nothing and the carry bar is a measured FAIL (MOD)",
          healthy["NS_hose_carries_real_units"]["status"] == "FAIL" and healthy["NS_hose_carries_real_units"]["class"] == "MOD",
          healthy["NS_hose_carries_real_units"])
    kinds = list(fb.kinds)
    for k in kinds:
        if k == "jawa/get_defs":
            continue                                    # an existence probe (_answer): its row is UNMEASURED in every run
        rows, _ = rf_run(refuse=k)
        sweep_same_or_withheld("realflow refuse %s" % k, hv, {i: r["status"] for i, r in rows.items()})
    # named staging calls the per-call guards never covered (code before this item scored these rows FAIL)
    for kind, rids in (("jawa/flowworks_excavation_drive", ["NS_hose_carries_real_units", "NS_hose_tint_is_carried_liquid",
                                                            "NS_hose_far_end_pump", "NS_pipe_and_hose_one_net"]),
                       ("jawa/battery_set", ["NS_hose_carries_real_units", "NS_relay_chain_carries"]),
                       ("jawa/comp_read", ["NS_hose_carries_real_units", "NS_tank_feeds_hose"]),
                       ("probe:settrail", ["NS_hose_dropped_carries_nothing"]),
                       ("probe:census", ["NS_hose_carries_real_units", "NS_hose_port_removed_discovered"]),
                       ("rimworld/execute_gizmo", []),
                       ("probe:filltank", ["NS_tank_feeds_hose"])):
        rows, _ = rf_run(refuse=kind)
        bad = {r: rows[r]["status"] for r in rids if rows[r]["status"] != "UNMEASURED"}
        check("C1 refused %s withholds the rows staged on it" % kind, not bad, bad)
    for kind, rids in (("jawa/build_batch", ["NS_hose_carries_real_units", "NS_hose_port_removed_moves", "NS_tank_feeds_hose"]),
                       ("jawa/destroy_batch", ["NS_hose_plumps_only_from_powered_pump", "NS_hose_port_removed_discovered"]),
                       ("probe:tank", ["NS_hose_carries_real_units", "NS_hose_dropped_carries_nothing"])):
        rows, _ = rf_run(noop=kind)
        bad = {r: rows[r]["status"] for r in rids if rows[r]["status"] != "UNMEASURED"}
        check("C1 no-op/dead %s withholds the rows staged on it" % kind, not bad, bad)


# ============================================================================ C2. suspension_bridge_proof --mock
def part_c2():
    import suspension_bridge_proof as SBP
    d = tempfile.mkdtemp(prefix="sbp_pre_")
    ocall, ostat = SBP.FakeBridge.call, SBP.FakeBridge.static
    seen = []

    def mock(name, call=None, static=None):
        SBP.FakeBridge.call = call or ocall
        SBP.FakeBridge.static = static or ostat
        try:
            path = os.path.join(d, name + ".json")
            with quiet_out():
                SBP.main(["--mock", path])
        finally:
            SBP.FakeBridge.call, SBP.FakeBridge.static = ocall, ostat
        return {r["id"]: r["detail"].get("mock") for r in json.load(open(path, encoding="utf-8"))["rows"]}

    def logging_call(self, tool, **kw):
        k = tool if tool != "jawa/static_call" else "static:" + str(kw.get("method"))
        if k not in seen:
            seen.append(k)
        return ocall(self, tool, **kw)
    healthy = mock("healthy", call=logging_call)
    owed = {k for k, v in healthy.items() if v == "UNMEASURED"}
    check("C2 can-pass: the healthy mock PASSes every row that is not owed", all(v == "PASS" for k, v in healthy.items() if k not in owed),
          {k: v for k, v in healthy.items() if v != "PASS"})

    def refuser(kind, how):
        def call(self, tool, **kw):
            k = tool if tool != "jawa/static_call" else "static:" + str(kw.get("method"))
            if k != kind:
                return ocall(self, tool, **kw)
            if how == "refuse":
                return {"success": False, "message": "refused (selftest)"}
            if how == "argrefuse":
                return {"success": True, "result": "REFUSED: bad args (selftest)"}
            if tool == "jawa/spawn_pawn":
                return {"success": True, "pawns": []}
            if tool == "jawa/set_draft":
                return {"success": True, "drafted": False}
            return ocall(self, tool, **kw)
        return call
    for k in seen:
        sweep_same_or_withheld("suspension refuse %s" % k, healthy, mock("r_" + k.replace("/", "_"), call=refuser(k, "refuse")))
        if k.startswith("static:"):
            sweep_same_or_withheld("suspension REFUSED-args %s" % k, healthy, mock("a_" + k.replace("/", "_"), call=refuser(k, "argrefuse")))
    for k in ("jawa/spawn_pawn", "jawa/set_draft"):
        sweep_same_or_withheld("suspension no-op %s" % k, healthy, mock("n_" + k.replace("/", "_"), call=refuser(k, "noop")))
    # named staging calls the per-call guards never covered (code before this item scored these rows PASS)
    for kind, how, rids in (("jawa/flowworks_excavation_drive", "refuse", ["SB_drag_6_timber_builds", "SB_rails_off_some_fall",
                                                                           "GRATE_fire_burns_people_above", "JET_two_square_steel_accepted"]),
                            ("jawa/spawn_batch", "refuse", ["SB_path_crosses_on_deck", "SB_load_over_rating_whole_span_falls",
                                                            "GRATE_item_stays_on_deck"]),
                            ("jawa/spawn_pawn", "noop", ["SB_rails_off_some_fall", "UND_both_arrive", "JET_overload_drops_whole_at_root"]),
                            ("static:ProofRails", "argrefuse", ["SB_rails_off_some_fall", "SB_rails_on_nobody_falls"]),
                            ("static:ProofPutUnder", "refuse", ["UND_crush_below_and_wreck"])):
        got = mock("t_" + kind.replace("/", "_") + how, call=refuser(kind, how))
        bad = {r: got.get(r) for r in rids if got.get(r) != "UNMEASURED"}
        check("C2 %s %s withholds the rows staged on it" % (how, kind), not bad, bad)
    # review 2026-10-20: a ProofPutUnder that ANSWERED under=False (not a refusal) left DropUnder reading under=False: scored FAIL
    def put_under_false(self, m, a):
        if m == "ProofPutUnder":
            return "PUTUNDER under=False"
        if m == "ProofDropUnder":
            return "DROPUNDER under=False at=1,1 underDeck=False slid=0"
        return ostat(self, m, a)
    got = mock("putunder_false", static=put_under_false)
    check("C2 a put-under that did not take withholds UND_item_slides_to_open_floor", got.get("UND_item_slides_to_open_floor") == "UNMEASURED",
          got.get("UND_item_slides_to_open_floor"))
    # a refused pour must not withhold the item row staged beside it (scope leak)
    got = mock("pour_refused", call=refuser("static:ProofPour", "refuse"))
    check("C2 a refused ProofPour withholds the pour row only", got.get("GRATE_pour_drains_to_body") == "UNMEASURED"
          and got.get("GRATE_item_stays_on_deck") == "PASS", {k: got.get(k) for k in ("GRATE_pour_drains_to_body", "GRATE_item_stays_on_deck")})
    # can-fail through the harness: a real mod fault still FAILs
    got = mock("realfail", static=lambda self, m, a: ("KNOCK trials=20 fell=0 railed=False edge=True" if m == "ProofKnock" else ostat(self, m, a)))
    check("C2 can-fail: rails off, open edge, nobody falls -> FAIL", got.get("SB_rails_off_some_fall") == "FAIL", got.get("SB_rails_off_some_fall"))


# ============================================================================ C3. the Contagion suite
def part_c3():
    import selftest_contagion as SC
    healthy = SC.run()
    hv = {k: v[0] for k, v in healthy.items()}
    check("C3 can-pass: the healthy Contagion fake PASSes every component", all(v == "PASS" for v in hv.values()),
          {k: v for k, v in hv.items() if v != "PASS"})
    ocall, tools = SC.Fake.call, []

    def logging_call(self, tool, **p):
        if tool not in tools:
            tools.append(tool)
        return ocall(self, tool, **p)
    SC.Fake.call = logging_call
    try:
        SC.run()
    finally:
        SC.Fake.call = ocall
    # a settings field the mod no longer declares IS a settings component's claim (`_answer`): its refusal is a measured FAIL
    claims = {"jawa/mod_settings_field"}
    for k in tools:
        if k in claims:
            continue

        def refusing(self, tool, _k=k, **p):
            if tool == _k:
                return {"success": False, "message": "refused (selftest)"}
            return ocall(self, tool, **p)
        SC.Fake.call = refusing
        try:
            got = SC.run()
        finally:
            SC.Fake.call = ocall
        crashed = {n: v for n, v in got.items() if v[0] == "CRASH"}
        check("C3 refuse %s: no chain crashes" % k, not crashed, crashed)
        sweep_same_or_withheld("Contagion refuse %s" % k, hv, {n: v[0] for n, v in got.items()})


# ============================================================================ D. proof_hose preport: one save's refused load must not withhold the other
def part_d():
    import proof_hose as PH
    import validation_core as V

    class PreFake(object):
        def __init__(self):
            self.log = []

        def call(self, tool, **kw):
            if tool == "rimworld/load_game" and kw.get("saveName") == "A":
                return {"success": False, "message": "no such save (selftest)"}
            return {"success": True, "logs": []}

        def hp(self, cmd, wait_s=20.0):
            return {"success": True, "pawns": [{"job": "RM_CarryHoseEnd"}]}

        def ticks(self, n):
            return {"success": True}

    ow = V._wait_playing
    V._wait_playing = lambda B, **k: (True, 1)
    try:
        import argparse
        P = PH.Proof(argparse.Namespace(only=None, preport_save="A,B"), bridge=PreFake())
        with quiet_out():
            with V.scope("preport"):
                P.preport()
    finally:
        V._wait_playing = ow
    st = {r["id"]: r["status"] for r in P.rows}
    check("D preport: a refused load of save 1 is UNMEASURED and save 2 still PASSes",
          st.get("PP1_preport_midcarry_save_loads") == "UNMEASURED" and st.get("PP2_preport_midretract_save_loads") == "PASS", st)
    P2 = PH.Proof(argparse.Namespace(only=None, preport_save=None), bridge=PreFake())
    with quiet_out():
        try:
            P2.block("zzz", lambda: (_ for _ in ()).throw(RuntimeError("harness boom (selftest)")))
        except Exception:
            pass
    rr = [r for r in P2.rows if r["id"] == "ZZZ_block"]
    check("D a raised block is UNMEASURED/HARNESS, never FAIL", rr and rr[0]["status"] == "UNMEASURED" and rr[0]["class"] == "HARNESS", rr)


def main():
    for part in (part_a, part_b, part_c1, part_c2, part_c3, part_d):
        try:
            part()
        except Exception as ex:  # noqa: BLE001 - a part that cannot run is a failure of this selftest, never a skip
            import traceback
            FAILS.append("%s raised %r" % (part.__name__, ex))
            print("FAIL %s raised %s" % (part.__name__, traceback.format_exc()[-1500:]))
    print("selftest_proof_preconditions: %d checks, %s" % (CHECKS[0], "PASS" if not FAILS else "FAIL (%d failing)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
