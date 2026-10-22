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
  5c. p3: the whole map is unfogged after the sweep (no later rock clear can flood a pocket); fog left FAILs P3
  5d. p2c: the map is swept before the control's save and its 600-tick advance; a map that will not calm FAILs P2c
  5e. hostiles the calm's own unfog releases are swept again (p2c and P3); a map that keeps releasing FAILs SITE
  6. log_budget control-noise and thrower attribution  7. a dead log journal makes Z UNMEASURED
  8. LogTap counts entries lost between polls
  9. d4_save (S12d in-session, 2026-10-22): the style block's SHARED UNMEASURED placeholder is REPLACED by the second
     save's verdict (one S12d row, block save_load; the S7 re-read is evidence, not a row); controls: a failed save/load
     reads UNMEASURED naming why, never PASS; an aborted session keeps the placeholder; a FAIL verdict stays FAIL
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
    return argparse.Namespace(only=only, no_shots=True, no_fresh_map=True, full_matrix=False, spec=None, skip_offline=False, save_name=None)


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
    P.d4_save = lambda: None


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


def fake_map(weather_reply, triggers=(), sticky=False, hostiles=(), calls=None, fog_left=0, released=(), keeps_releasing=False):
    """A fake map's bridge call. triggers: fog-trigger things present; sticky: they survive destroy_batch; hostiles: hostile
    pawns still listed after every sweep; fog_left: cells still fogged after set_fog unfogAll; released: hostiles the
    unfog brings onto the map (r7), swept by the next destroy_bulk unless keeps_releasing. calls collects (tool, kw)."""
    armed = [dict(t) for t in triggers]
    freed = []

    def call(tool, **kw):
        if calls is not None:
            calls.append(tool if not kw.get("action") else "%s:%s" % (tool, kw["action"]))
        if tool == "jawa/set_fog":
            freed[:] = list(released)
            return {"success": True, "action": kw.get("action"), "foggedCellsBefore": 9000, "foggedCellsNow": fog_left}
        if tool == "jawa/destroy_bulk" and not keeps_releasing:
            del freed[:]
        if tool == "jawa/weather_set":
            return weather_reply
        if tool == "jawa/list_pawns":
            if kw.get("faction") == "hostile":
                return {"success": True, "pawns": [{"id": h} for h in list(hostiles) + freed]}
            return {"success": True, "pawns": []}
        if tool == "jawa/list_things":
            if kw.get("defName"):
                return {"success": True, "things": list(armed), "countMatched": len(armed), "isCompleteList": True}
            return {"success": True, "things": []}
        if tool == "jawa/destroy_batch" and kw.get("categories") == "Ethereal" and not sticky:
            del armed[:]
        return {"success": True}
    return call


def p3_released(released, keeps_releasing=False):
    """P3 over a fake map whose unfog releases hostiles (r7); returns the P3 row's status."""
    P = PA.Proof(args(None))
    P.map_info = {"longitude": None}
    P.B.call = fake_map({"success": True}, released=released, keeps_releasing=keeps_releasing)
    P.B.probe = lambda c, *a, **k: {"success": True}
    P.B.ap = lambda c, *a, **k: {"success": True}
    P.B.hp = lambda c, *a, **k: {"success": True, "pawns": []}
    P.p3_probes_and_site(None)
    return [r for r in P.rows if r["id"] == "P3_probes_site_pinned_region_empty"][0]["status"]


def p3(weather_reply, triggers=(), sticky=False, hostiles=(), calls=None, fog_left=0):
    """P3 over a fake map (fake_map); returns the P3 row's status."""
    P = PA.Proof(args(None))
    P.map_info = {"longitude": None}
    P.B.call = fake_map(weather_reply, triggers, sticky, hostiles, calls, fog_left)
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
# TESTENV_FOGGED_MECH_HARDEN_WOKE_ON_REVEAL residual (r6 map 3): the whole map is unfogged after the sweep, before the pin
check("5c the map is unfogged after the non-colonist sweep and before the noon pin",
      "jawa/set_fog:unfogAll" in order
      and order.index("jawa/destroy_bulk") < order.index("jawa/set_fog:unfogAll") < order.index("jawa/time_clock"), order)
check("5c can-fail: fog left after the unfog FAILs P3", p3({"success": True}, fog_left=12) == "FAIL")
order_h = []
p3({"success": True}, hostiles=["Mech_Militor3042"], calls=order_h)
check("5c can-fail: the unfog is refused while a hostile is listed (it would wake him)", "jawa/set_fog:unfogAll" not in order_h, order_h)
check("5b can-fail: triggers that survive the disarm FAIL P3", p3({"success": True}, triggers=TRIG, sticky=True) == "FAIL")
check("5b can-fail: a hostile pawn left after the sweeps FAILs P3", p3({"success": True}, hostiles=["Mech_Militor3042"]) == "FAIL")


def p2c(hostiles=(), fog_left=0, released=(), keeps_releasing=False):
    """p2c_control_noise over a fake map -> (tool order, P)."""
    P = PA.Proof(args(None))
    order = []
    base = fake_map({"success": True}, hostiles=hostiles, calls=order, fog_left=fog_left, released=released,
                    keeps_releasing=keeps_releasing)

    def call(tool, **kw):
        if tool == "rimbridge/list_logs":
            order.append(tool)
            return {"success": True, "logs": []}
        return base(tool, **kw)
    P.B.call = call
    P.B.ticks = lambda n: order.append("ticks:%d" % n)
    saved = (PA.V._wait_saved, PA.V._wait_playing)
    PA.V._wait_saved = lambda name, *a, **k: True
    PA.V._wait_playing = lambda B, *a, **k: (True, 1)
    try:
        P.p2c_control_noise()
    finally:
        PA.V._wait_saved, PA.V._wait_playing = saved
    return order, P


# TESTENV_CONTROL_NOISE_HARDEN_SPIDER_AT_ARM: the control's 600-tick advance runs on a swept map
o, P = p2c()
check("5d p2c sweeps (disarm, non-colonists, unfog) before the control save and its first tick",
      "rimworld/save_game" in o and "ticks:600" in o
      and o.index("jawa/destroy_bulk") < o.index("jawa/set_fog:unfogAll") < o.index("rimworld/save_game") < o.index("ticks:600"), o)
check("5d control: a calm map leaves no P2c row", not [r for r in P.rows if r["id"] == "P2c_control_save_load"])
o, P = p2c(hostiles=["Megaspider4410"])
check("5d can-fail: a map that will not calm FAILs P2c SITE and never advances the clock",
      [r["status"] for r in P.rows if r["id"] == "P2c_control_save_load"] == ["FAIL"] and not [x for x in o if x.startswith("ticks:")], o)
# TESTENV_FLESHBEAST_HARDEN_FREED_BY_UNFOG (r7): the calm's unfog releases fleshbeasts AFTER its own hostile check
BEASTS = ["Trispike3924", "Toughspike3925"]
o, P = p2c(released=BEASTS)
cn = P.res["control_noise_calm"]
check("5e p2c: hostiles the unfog released are swept again before the control save; no P2c row",
      not [r for r in P.rows if r["id"] == "P2c_control_save_load"] and cn["calm"]
      and cn["mapFog"]["releasedByUnfog"] == BEASTS and cn["mapFog"]["hostilesAfter"] == []
      and o.index("jawa/set_fog:unfogAll") < len(o) - 1 - o[::-1].index("jawa/destroy_bulk") < o.index("rimworld/save_game"), o)
o, P = p2c(released=BEASTS, keeps_releasing=True)
check("5e can-fail: a map whose unfog keeps releasing hostiles FAILs P2c SITE and never ticks",
      [r["status"] for r in P.rows if r["id"] == "P2c_control_save_load"] == ["FAIL"] and not [x for x in o if x.startswith("ticks:")], o)
check("5e can-fail: released hostiles left after P3's calm FAIL P3",
      p3_released(BEASTS, keeps_releasing=True) == "FAIL")
check("5e control: released hostiles swept by P3's calm leave P3 PASS", p3_released(BEASTS) == "PASS")


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

# 9. d4_save: S12d measured by a second save after SL3
def d4_case(save_rows, after_status, aborted=False):
    P = PA.Proof(args(None))
    P.out_path = os.devnull
    P.rows = [{"id": "S12d_D4_pending_queue_save", "status": "UNMEASURED", "class": "HARNESS", "detail": "SHARED", "block": "style"}]
    if aborted:
        P.res["aborted"] = "save did not land"
    calls = []
    saved = (PA.VS.s12d_stage, PA.VS._save_load, PA.VS.s12d_after_load)
    PA.VS.s12d_stage = lambda B: calls.append("stage") or True
    PA.VS._save_load = lambda B, rows, name, st, stage=False: calls.append(("save", name.endswith("_d4"), stage)) or rows.extend(save_rows)
    PA.VS.s12d_after_load = lambda B, rows, built: calls.append("after") or rows.append(
        {"id": "S12d_D4_pending_queue_save", "status": after_status, "class": "MOD", "detail": {}})
    P.B = type("B", (), {"ap": lambda self, c: {"anchors": []}, "call": lambda self, *a, **k: {}})()
    try:
        P.d4_save()
    finally:
        PA.VS.s12d_stage, PA.VS._save_load, PA.VS.s12d_after_load = saved
    return [r for r in P.rows if r["id"] == "S12d_D4_pending_queue_save"], P, calls


S7OK = [{"id": "S7_save_load_styles", "status": "PASS", "class": "MOD", "detail": {}}]
got, P, calls = d4_case(S7OK, "PASS")
check("9 d4_save: placeholder replaced by ONE PASS row in save_load", [(r["status"], r["block"]) for r in got] == [("PASS", "save_load")], str(got))
check("9 d4_save: staged, saved under a _d4 name with stage=True, then read", calls == ["stage", ("save", True, True), "after"], str(calls))
check("9 d4_save: S7 re-read kept as evidence, not a row", not any(r["id"] == "S7_save_load_styles" for r in P.rows) and P.res.get("d4_save_notes"))
got, P, calls = d4_case([{"id": "S7_save_load_styles", "status": "FAIL", "class": "SITE", "detail": {"state": "menu"}}], "PASS")
check("9 control: failed save/load -> UNMEASURED with why, after-load never read", [r["status"] for r in got] == ["UNMEASURED"] and "after" not in calls and got[0]["detail"].get("why"), str(got))
got, P, calls = d4_case(S7OK, "PASS", aborted=True)
check("9 control: aborted session keeps the SHARED placeholder, stages nothing", [(r["status"], r["block"]) for r in got] == [("UNMEASURED", "style")] and not calls, str((got, calls)))
got, P, calls = d4_case(S7OK, "FAIL")
check("9 control: a FAIL verdict stays FAIL", [r["status"] for r in got] == ["FAIL"], str(got))
check("9 declared: S12d is a declared save_load row", "S12d_D4_pending_queue_save" in PA.DECLARED_ROWS["save_load"] and "d4_save" in PA.BLOCKS)

print("\n%s" % ("ALL PASS" if not FAILS else "FAILED: %s" % FAILS))
sys.exit(1 if FAILS else 0)
