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
    for mod, fns in ((PA.VA, ("run_live",)), (PA.VH, ("run_live", "run_maze", "run_relay", "run_carry")),
                     (PA.VS, ("run_live",)), (PA.VSH, ("run_live",))):
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

print("\n%s" % ("ALL PASS" if not FAILS else "FAILED: %s" % FAILS))
sys.exit(1 if FAILS else 0)
