"""selftest_proof_all.py -- offline fake-bridge checks of proof_all.py's durability (PROOF_ALL_DURABLE_RESULTS_1).

    python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_proof_all.py

No bridge, no game: the one shared socket is a stub, and every block body is replaced by a canned one. Each rule is
paired with a control that differs in that one thing, so a rule that stops firing turns this red:
  1. a final-block exception (log_budget raises)      -> the result JSON exists, keeps every earlier row, carries a
                                                         FAIL row for the block, and is NOT certifiable
  2. a BaseException escaping the final block         -> the per-block checkpoint already wrote the earlier rows,
     (KeyboardInterrupt, as a killed run)                marked partial + incomplete + certifiable False
  3. control: the same run with nothing raising       -> final checkpoint is mode live, certifiable True
  4. Proof.want(): --only core still runs preflight   -> control: "aerial" is skipped
  5. p3_probes_and_site: a weather_set reply with NO `success` field is a FAIL; control: explicit success true passes
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


def run_session(boom, only, base):
    out = os.path.join(base, "r.json")
    P = PA.Proof(args(only))
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
    # the matrix block needs the design spec; run only the cheap blocks (preflight is forced in by want())
    ONLY = ["core", "save_load", "aerial"]
    d = os.path.join(tmp, "a")
    os.makedirs(d)
    P, mid, fin, raised = run_session(RuntimeError("boom-final"), ONLY, d)
    ids = [r["id"] for r in fin["rows"]]
    check("1 exception in final block: earlier rows kept", "P1_fresh_map" in ids and "M1_conduit_transparent" in ids and "SL1_x" in ids, str(ids))
    check("1 exception in final block: FAIL row for the block", any(r["id"] == "LOG_BUDGET_block" and r["status"] == "FAIL" for r in fin["rows"]))
    check("1 exception in final block: not certifiable", fin["certifiable"] is False and fin["mode"] == "partial")

    d = os.path.join(tmp, "b")
    os.makedirs(d)
    P, mid, fin, raised = run_session(KeyboardInterrupt(), ONLY, d)
    check("2 BaseException escapes: checkpoint written before final", mid is not None and any(r["id"] == "SL1_x" for r in mid["rows"]), str(mid and [r["id"] for r in mid["rows"]]))
    check("2 BaseException escapes: marked incomplete, not certifiable", mid is not None and mid["certifiable"] is False and mid["mode"] == "partial" and "incomplete" in mid)
    check("2 BaseException escapes: run_raised recorded", "KeyboardInterrupt" in (fin.get("run_raised") or "") and fin["certifiable"] is False)

    d = os.path.join(tmp, "c")
    os.makedirs(d)
    P, mid, fin, raised = run_session(None, ONLY, d)
    check("3 control: clean --only run is partial, not certifiable (an --only run is never a proof)", fin["mode"] == "partial" and fin["certifiable"] is False)
    check("3 control: clean run has the Z row and no incomplete marker", any(r["id"] == "Z_log_budget" for r in fin["rows"]) and "incomplete" not in fin)

P = PA.Proof(args(["core"]))
check("4 --only core still wants preflight", P.want("preflight") and P.want("core"))
check("4 control: --only core does not want aerial", not P.want("aerial"))
check("4 control: no --only wants everything", PA.Proof(args(None)).want("aerial"))


def p3(weather_reply):
    P = PA.Proof(args(None))
    P.map_info = {"longitude": None}

    def call(tool, **kw):
        if tool == "jawa/weather_set":
            return weather_reply
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": []}
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



def z(control_msgs, session_errs):
    """Z over canned log entries: control_msgs are the control window's errors, session_errs the session's."""
    P = PA.Proof(args(None))
    P.log_base = 0
    P.control = {PA._err_key({"Message": m}) for m in control_msgs}
    P.B.call = lambda tool, **kw: {"logs": [dict(e, Sequence=i + 1, Level="Error") for i, e in enumerate(session_errs)]}
    P.log_budget()
    return [r for r in P.rows if r["id"] == "Z_log_budget"][0]


ld = "Could not get load ID. pathRelToParent=/sourcePrecept, parent=guy762_JawaHood219"
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

print("\n%s" % ("ALL PASS" if not FAILS else "FAILED: %s" % FAILS))
sys.exit(1 if FAILS else 0)
