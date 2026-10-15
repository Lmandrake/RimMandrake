"""selftest_proof_all.py -- offline fake-bridge checks of proof_all.py's durability (PROOF_ALL_DURABLE_RESULTS_1).

    python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_proof_all.py

No bridge, no game: the one shared socket is a stub, and every block body is replaced by a canned one. Each rule is
paired with a control that differs in that one thing, so a rule that stops firing turns this red:
  1. a final-block exception (log_budget raises)      -> the result JSON exists, keeps every earlier row, carries a
                                                         FAIL row for the block, and is NOT certifiable
  2. a BaseException escaping the final block         -> the per-block checkpoint already wrote the earlier rows,
     (KeyboardInterrupt, as a killed run)                marked partial + incomplete + certifiable False
  3. control: the same run with nothing raising       -> final checkpoint is mode live, certifiable True
     (1-3 run the whole block list except the matrix/determinism pair, which needs the design spec: want() is
     narrowed directly rather than via --only, because an --only run is never certifiable and would make the
     certifiable checks pass whatever the raise rules did)
  4. Proof.want(): --only core still runs preflight   -> control: "aerial" is skipped
  5. p3_probes_and_site: a weather_set reply with NO `success` field is a FAIL; control: explicit success true passes
  5b. p3: fog triggers are disarmed before the noon pin; triggers that survive, or a hostile pawn left, FAIL P3
  6. log_budget control-noise and thrower attribution  7. a dead log journal makes Z UNMEASURED
  8. LogTap counts entries lost between polls
"""
import argparse
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import proof_all as PA  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("PASS" if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


class FakeSocket(object):
    def call(self, *a, **k):
        return {"success": True}


PA._SOCKET[:] = [FakeSocket()]


def args(only=None):
    return argparse.Namespace(only=only, no_shots=True, no_fresh_map=True, full_matrix=False, spec=None, skip_offline=False)


def stub_blocks(P, boom=None):
    """Canned block bodies: preflight and core emit one PASS row each; log_budget raises `boom` or emits a row."""
    P.p1_fresh_map = lambda: P.row("preflight", "P1_fresh_map", "PASS", "SITE", {})
    P.p2_tier_and_startup_log = lambda: None
    P.p2c_control_noise = lambda: None
    P.p3_probes_and_site = lambda boards: None
    P.core = lambda: P.row("core", "M1_conduit_transparent", "PASS", "MOD", {})
    P.restore = lambda: None

    def lb():
        if boom is not None:
            raise boom
        P.row("session", "Z_log_budget", "PASS", "MOD", {})
    P.log_budget = lb
    P.save_load = lambda: P.row("save_load", "SL1_x", "PASS", "MOD", {})


def run_session(boom, base):
    out = os.path.join(base, "r.json")
    P = PA.Proof(args(None))
    P.want = lambda name: name not in ("matrix", "determinism")
    P.out_path = out
    stub_blocks(P, boom)
    empty = lambda ns=None: {"rows": []}  # noqa: E731
    for mod, fns in ((PA.VA, ("run_live",)), (PA.VS, ("run_live",))):
        for f in fns:
            setattr(mod, f, empty)
    raised = None
    try:
        try:
            P.run(None)
        except BaseException as ex:  # noqa: BLE001
            P.res["run_raised"] = repr(ex)
            raised = ex
            raise
        finally:
            mid = json.load(open(out)) if os.path.exists(out) else None
            P.checkpoint(final=True)
    except BaseException:  # noqa: BLE001
        pass
    return P, mid, json.load(open(out)), raised


with tempfile.TemporaryDirectory() as tmp:
    d = os.path.join(tmp, "a")
    os.makedirs(d)
    P, mid, fin, raised = run_session(RuntimeError("boom-final"), d)
    ids = [r["id"] for r in fin["rows"]]
    check("1 exception in final block: earlier rows kept", "P1_fresh_map" in ids and "M1_conduit_transparent" in ids and "SL1_x" in ids, str(ids))
    check("1 exception in final block: FAIL row for the block", any(r["id"] == "LOG_BUDGET_block" and r["status"] == "FAIL" for r in fin["rows"]))
    check("1 exception in final block: not certifiable", fin["certifiable"] is False, str((fin["mode"], fin["certifiable"])))

    d = os.path.join(tmp, "b")
    os.makedirs(d)
    P, mid, fin, raised = run_session(KeyboardInterrupt(), d)
    check("2 BaseException escapes: checkpoint written before final", mid is not None and any(r["id"] == "SL1_x" for r in mid["rows"]), str(mid and [r["id"] for r in mid["rows"]]))
    check("2 BaseException escapes: marked incomplete, not certifiable", mid is not None and mid["certifiable"] is False and mid["mode"] == "partial" and "incomplete" in mid)
    check("2 BaseException escapes: run_raised recorded", "KeyboardInterrupt" in (fin.get("run_raised") or "") and fin["certifiable"] is False)

    d = os.path.join(tmp, "c")
    os.makedirs(d)
    P, mid, fin, raised = run_session(None, d)
    check("3 control: clean run is live and certifiable", fin["mode"] == "live" and fin["certifiable"] is True, str((fin["mode"], fin["certifiable"])))
    check("3 control: clean run has the Z row and no incomplete marker", any(r["id"] == "Z_log_budget" for r in fin["rows"]) and "incomplete" not in fin)

P = PA.Proof(args(["core"]))
check("4 --only core still wants preflight", P.want("preflight") and P.want("core"))
check("4 control: --only core does not want aerial", not P.want("aerial"))
check("4 control: no --only wants everything", PA.Proof(args(None)).want("aerial"))


def p3(weather_reply, triggers=(), sticky=False, hostiles=(), calls=None):
    """P3 over a fake map. triggers: fog-trigger things present; sticky: they survive destroy_batch; hostiles: hostile pawns
    still listed after every sweep. calls (a list) collects the tool order."""
    P = PA.Proof(args(None))
    P.map_info = {"longitude": None}
    armed = [dict(t) for t in triggers]

    def call(tool, **kw):
        if calls is not None:
            calls.append(tool)
        if tool == "jawa/weather_set":
            return weather_reply
        if tool == "jawa/list_pawns":
            if kw.get("faction") == "hostile":
                return {"success": True, "pawns": [{"id": h} for h in hostiles]}
            return {"success": True, "pawns": []}
        if tool == "jawa/list_things":
            if kw.get("defName"):
                return {"success": True, "things": list(armed), "countMatched": len(armed), "isCompleteList": True}
            return {"success": True, "things": []}
        if tool == "jawa/destroy_batch" and kw.get("categories") == "Ethereal" and not sticky:
            del armed[:]
        return {"success": True}
    P.B.call = call
    P.B.probe = lambda c, *a, **k: {"success": True}
    P.B.ap = lambda c, *a, **k: {"success": True}
    P.B.hp = lambda c, *a, **k: {"success": True, "pawns": []}
    P.p3_probes_and_site(None)
    return [r for r in P.rows if r["id"] == "P3_probes_site_pinned_region_empty"][0]["status"]


check("5 weather_set with no `success` field fails P3", p3({}) == "FAIL")
check("5 control: explicit success true passes P3", p3({"success": True}) == "PASS")
check("5 control: explicit success false fails P3", p3({"success": False}) == "FAIL")
# TESTENV_FOGGED_MECH_HARDEN_WOKE_ON_REVEAL: fog triggers disarmed before the clock moves; armed or hostile maps refuse
TRIG = [{"id": "TriggerUnfogged1", "def": "TriggerUnfogged", "x": 30, "z": 40},
        {"id": "SignalAction_Ambush2", "def": "SignalAction_Ambush", "x": 30, "z": 40}]
order = []
check("5b triggers present and vanished: P3 PASS", p3({"success": True}, triggers=TRIG, calls=order) == "PASS")
check("5b the disarm runs before the noon pin and the non-colonist sweep",
      "jawa/destroy_batch" in order and order.index("jawa/destroy_batch") < order.index("jawa/destroy_bulk") < order.index("jawa/time_clock"),
      order)
check("5b can-fail: triggers that survive the disarm FAIL P3", p3({"success": True}, triggers=TRIG, sticky=True) == "FAIL")
check("5b can-fail: a hostile pawn left after the sweeps FAILs P3", p3({"success": True}, hostiles=["Mech_Militor3042"]) == "FAIL")


def z(control_msgs, session_errs, log_dead=False):
    """Z over canned log entries: control_msgs are the control window's errors, session_errs the session's. The journal
    echoes the log-cap sentinel warning (validation_core.log_alive) unless log_dead."""
    P = PA.Proof(args(None))
    P.log_base = 0
    P.control = {PA._err_key({"Message": m}) for m in control_msgs}
    sent = []

    def call(tool, **kw):
        if tool == "jawa/static_call":
            if kw.get("method") == "Warning" and not log_dead:
                sent.append(kw.get("args"))
            return {"success": True}
        return {"logs": [dict(e, Sequence=i + 1, Level="Error") for i, e in enumerate(session_errs)]
                + [{"Sequence": 9999, "Level": "Warning", "Message": m} for m in sent]}
    P.B.call = call
    P.log_budget()
    return [r for r in P.rows if r["id"] == "Z_log_budget"][0]


ld = "Could not get load ID. pathRelToParent=/sourcePrecept, parent=guy762_JawaHood219"
check("7 log cap: a dead journal (sentinel never seen) makes Z UNMEASURED, never PASS",
      z([], [], log_dead=True)["status"] == "UNMEASURED")
check("7 control: a live journal with no errors passes Z", z([], [])["status"] == "PASS")


def tap_lost(ring, steps):
    """LogTap over a fake 1,000-style ring of `ring` entries; `steps` = entries written between polls."""
    VC = PA._VC()
    log = []

    class FB(object):
        def call(self, tool, **kw):
            keep = log[-ring:]
            after = kw.get("afterSequence", 0)
            out = [e for e in keep if e["Sequence"] > after][::-1][:kw.get("limit", 50)]
            return {"logs": out}
    t = VC.LogTap(FB())
    for n in steps:
        for _ in range(n):
            log.append({"Sequence": len(log) + 1, "Level": "Warning" if len(log) % 7 == 0 else "Info", "Message": "x"})
        t.poll()
    return t.lost


check("8 journal tap: polls closer than the ring lose nothing", tap_lost(10, [5, 9, 3]) == 0)
check("8 journal tap: a gap longer than the ring is counted as lost", tap_lost(10, [5, 25]) == 15)


def tap_repeat():
    """A row repeated 3x carries its LATEST sequence and RepeatCount 3: seq 2..4 are covered, nothing is lost."""
    VC = PA._VC()
    rows = [{"Sequence": 1, "Level": "Info"}]

    class FB(object):
        def call(self, tool, **kw):
            return {"logs": [e for e in rows if e["Sequence"] > kw.get("afterSequence", 0)][::-1]}
    t = VC.LogTap(FB())
    rows.append({"Sequence": 4, "Level": "Error", "RepeatCount": 3})
    t.poll()
    rows.append({"Sequence": 9, "Level": "Error", "RepeatCount": 2})   # 5..7 really gone
    t.poll()
    return t.lost


check("8 journal tap: a repeated row's RepeatCount covers its sequences; a real hole is still lost", tap_repeat() == 3)
check("6 control noise (digits differ) is excluded", z([ld.replace("219", "727")], [{"Message": ld}])["status"] == "PASS")
check("6 control: an error NOT in the control window is charged", z([ld], [{"Message": "System.NullReferenceException: boom"}])["status"] == "FAIL")
check("6 control: an error naming GSS is charged even when the control had it",
      z(["NRE in RimMandrake.GimmeSomeSlack.Aerial"], [{"Message": "NRE in RimMandrake.GimmeSomeSlack.Aerial"}])["status"] == "FAIL")
check("6 control: the same message thrown from ANOTHER frame is charged",
      z(["NRE"], [{"Message": "NRE", "StackTrace": "  at Verse.Other.M () [0x0]"}])["status"] == "FAIL")
check("6 an NRE thrown in another mod's frame (not in the control) is that mod's",
      z([], [{"Message": "NRE", "StackTrace": "  at RimFridge.RimFridgeComponent.StartedOrLoadedGame () [0x0001a]"}])["status"] == "PASS")
check("6 control: an NRE thrown in a VANILLA frame is still charged",
      z([], [{"Message": "NRE", "StackTrace": "  at Verse.Thing.DoTick () [0x0001a]"}])["status"] == "FAIL")
check("6 control: a stackless error naming no source is still charged", z([], [{"Message": "Something odd"}])["status"] == "FAIL")
check("6 a def error with [Source: other mod] is that mod's", z([], [{"Message": "Failed to find X.\n[Source: RimFridge: Now with Shelves!]"}])["status"] == "PASS")
check("6 thrower reads the first stack frame", PA._thrower({"Message": "x", "StackTrace": "  at A.B.C () [0x0001a] in <x>:0"}) == "A.B.C ()")

# 7. M20 settings flips (GSS_SWITCHES_PROVE_TWENTY_UNFLIPPED): the real flips_block against a fake bridge whose behaviour
# follows the settings (faithful) and one that ignores them (broken) -> rows PASS on the first, FAIL on the second.
for _id in ("M20a_fallen_wire_shock_flip", "M20b_fallen_wire_knockback_flip", "M20c_fallen_wire_ignites_flip", "M20d_keep_wires_setting_roundtrip"):
    check("7 declared: %s" % _id, _id in PA.declared_rows())
import validation_aerial as _VA


class FakeB:
    def __init__(self, faithful):
        self.faithful, self.s, self.pawns, self.n, self.sweeps = faithful, {"fallenWireShock": "True", "fallenWireIgnites": "True", "fallenWireKnockback": "2", "keepWiresOnGravship": "True"}, {}, 0, 0

    def ticks(self, n):
        self._t = n
        for pw in self.pawns.values():
            if pw["age"] == 0 and n >= 20:
                shock = self.s["fallenWireShock"] == "True" if self.faithful else True
                kb = int(self.s["fallenWireKnockback"]) if self.faithful else 0
                pw["shocked"] = shock
                if shock and kb > 0:
                    pw["pos"] = [pw["pos"][0] + 1, pw["pos"][1]]
            pw["age"] += n
        self.sweeps += n // 250

    def ap(self, cmd):
        if cmd.startswith("set:"):
            k, v = cmd[4:].split("=")
            self.s[k] = v
            return {"success": True, "value": v}
        if cmd == "census":
            return {"success": True, "anchors": [], "_a": 1}
        return {"success": True, "cuts": 1}

    def call(self, tool, **kw):
        if tool == "jawa/spawn_pawn":
            self.n += 1
            self.pawns[self.n] = {"pos": [kw["x"], kw["z"]], "age": 0, "shocked": False}
            return {"pawns": [{"id": self.n}]}
        if tool == "jawa/list_pawns":
            return {"pawns": [{"id": i, "pos": list(pw["pos"]), "health": {"hediffs": [{"def": "RM_FallenWireShock"}] if pw["shocked"] else []}} for i, pw in self.pawns.items()]}
        if tool == "jawa/list_things":
            if kw.get("defName") == "Fire":
                on = (self.s["fallenWireIgnites"] == "True") if self.faithful else True
                return {"things": [{"id": 1}] if on and self.sweeps >= 2 else []}
            return {"things": [{"id": 5}]}
        return {"success": True}


_orig = _VA.anchors_by_pos
_VA.anchors_by_pos = lambda c: {_VA.F1: {"id": 1, "fallenLive": True, "fallen": [{"cutPartner": 2, "tip": [101.5, 135.5]}]}, _VA.F2: {"id": 2}}
_VA.time.sleep = lambda *_: None
for faithful in (True, False):
    rows = []
    _VA.flips_block(FakeB(faithful), rows, {})
    got = {r["id"]: r["status"] for r in rows}
    want = "PASS" if faithful else "FAIL"
    for _id in ("M20a_fallen_wire_shock_flip", "M20b_fallen_wire_knockback_flip", "M20c_fallen_wire_ignites_flip"):
        check("7 %s fake bridge: %s is %s" % ("faithful" if faithful else "broken", _id, want), got.get(_id) == want, str(got))
    if faithful:
        check("7 faithful: M20d wiring row PASS and settings restored", got.get("M20d_keep_wires_setting_roundtrip") == "PASS")
_VA.anchors_by_pos = _orig

print("\n%s" % ("ALL PASS" if not FAILS else "FAILED: %s" % FAILS))
sys.exit(1 if FAILS else 0)
