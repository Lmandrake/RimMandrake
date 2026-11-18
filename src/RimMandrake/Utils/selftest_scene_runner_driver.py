#!/usr/bin/env python3
"""Selftest: scene_runner.py, the python half of the shared in-game scene runner (RIMMANDRAKE_BUILD_SHARED_SCENE_RUNNER_FIRST_SLICE).

A fake bridge records every call; the REAL modcheck/scene_snapshot.py runs with fake save/load. Proves:
  D1  a passing suite is ONE jawa/run_scenes call, saved before it and reloaded after it, exit 0
  D2  FAIL, D3 UNMEASURED and D5 EMPTY (success with no rows) are three different outcomes and exits
  D4  a suite with no row read from outside the mod gets SUITE_OUTSIDE_READ UNMEASURED
  D6  "Type not found" is PROOF BUILD REQUIRED (exit 3), never a table of FAILs
  D7  a refused run and D8 a dropped call are NO_RUN (exit 4), and the map is still reloaded
  D9  a failed reload is RESTORE (exit 5) even when every row passed; the rows are kept
  D10 a failed save stages nothing: run_scenes is never called
  D11 a {"result": {...}} reply is unwrapped; D12 also when the envelope carries its own "success" (a nested FAIL stays FAIL)
  D13 success with rows missing, null or malformed is NO_RUN (unreadable), never EMPTY and never a crash
  D14 a restore that raises after a None reply is RESTORE, never "the save failed"
  D15 no bridge at all is NO_RUN (exit 4); D16 a relative --out path is written
  W   the wiring: the tool, its CAMPAIGN refusal, the EK suite and its csproj lines, RM_PROOFS fences
No game, no bridge.  Run: python3 src/RimMandrake/Utils/selftest_scene_runner_driver.py
"""
import functools
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "modcheck"))
import scene_runner as SR       # noqa: E402
import scene_snapshot as SS     # noqa: E402

RESULTS = []


def check(cid, ok, why):
    RESULTS.append((cid, bool(ok), why))
    print("%s %s %s" % ("PASS" if ok else "FAIL", cid, why))


def row(scene, chk, status, source="scene"):
    return {"scene": scene, "check": chk, "status": status, "measured": "1", "expected": ">= 1", "source": source, "cause": None}


GOOD = [row("storeroom_bomb_pit", "OUTSIDE haulables -3,-5,7,2", "PASS", "outside"), row("storeroom_bomb_pit", "VERDICT", "PASS"),
        row("storeroom_bomb_pit_control", "VERDICT", "PASS")]


def harness(reply=None, raises=None, save_fails=False, load_ok=True, load_raises=None):
    events = []

    def send(tool, kw):
        events.append(("call", tool))
        if raises:
            raise raises
        return reply

    def save(call, name):
        events.append(("save", name))
        if save_fails:
            raise RuntimeError("no .rws appeared")
        return {"ok": True}

    def load(call, name):
        events.append(("load", name))
        if load_raises:
            raise load_raises
        return {"verified": load_ok, "problems": [] if load_ok else ["no Playing map"]}

    call = SR.CountingCall(send)
    snap = functools.partial(SS.scene_snapshot, save=save, load=load)
    rep = SR.run(call, "RimMandrake.ExplosiveKnockback.RM_KnockbackScenes", snapshot=snap)
    return rep, events, call


def ok_reply(rows):
    return {"success": True, "overall": SR.overall(rows), "rows": rows, "scenes": [], "suiteBegin": "ran", "problems": []}


def main():
    rep, ev, call = harness(ok_reply(GOOD))
    kinds = [e[0] for e in ev]
    check("D1", rep["outcome"] == "PASS" and SR.EXIT[rep["outcome"]] == 0 and call.calls == {SR.TOOL: 1}
          and kinds == ["save", "call", "load"] and ev[0][1] == ev[2][1] and ev[0][1].startswith("scene_runner_pre_"),
          "outcome %s, calls %s, order %s" % (rep["outcome"], call.calls, kinds))
    rep, _, _ = harness(ok_reply(GOOD[:2] + [row("storeroom_bomb_pit_control", "VERDICT", "FAIL")]))
    check("D2", rep["outcome"] == "FAIL" and SR.EXIT["FAIL"] == 1, rep["outcome"])
    rep, _, _ = harness(ok_reply(GOOD[:2] + [row("storeroom_bomb_pit_control", "VERDICT", "UNMEASURED")]))
    check("D3", rep["outcome"] == "UNMEASURED" and SR.EXIT["UNMEASURED"] == 2, rep["outcome"])
    rep, _, _ = harness(ok_reply(GOOD[1:]))
    g = [r for r in rep["rows"] if r["check"] == "SUITE_OUTSIDE_READ"]
    check("D4", rep["outcome"] == "UNMEASURED" and len(g) == 1 and g[0]["status"] == "UNMEASURED" and g[0]["cause"],
          "outcome %s, guard rows %s" % (rep["outcome"], g))
    rep, _, _ = harness(ok_reply([]))
    check("D5", rep["outcome"] == "EMPTY" and not rep["rows"] and SR.EXIT["EMPTY"] == 2, "%s %s" % (rep["outcome"], rep["rows"]))
    rep, ev, _ = harness({"success": False, "message": "Type not found: RimMandrake.ExplosiveKnockback.RM_KnockbackScenes (mod inactive...)"})
    buf = io.StringIO()
    SR.render(rep, out=buf)
    check("D6", rep["outcome"] == "PROOF_BUILD" and SR.EXIT["PROOF_BUILD"] == 3 and "PROOF BUILD REQUIRED" in buf.getvalue()
          and "FAIL" not in [r.get("status") for r in rep["rows"]], rep["outcome"])
    rep, ev, _ = harness({"success": False, "message": "Unknown scene(s): nope", "details": {"known": ["a"]}})
    check("D7", rep["outcome"] == "NO_RUN" and SR.EXIT["NO_RUN"] == 4 and [e[0] for e in ev] == ["save", "call", "load"],
          "%s %s" % (rep["outcome"], ev))
    rep, ev, _ = harness(raises=ConnectionResetError("bridge dropped"))
    check("D8", rep["outcome"] == "NO_RUN" and "bridge dropped" in rep.get("error", "") and [e[0] for e in ev] == ["save", "call", "load"],
          "%s %s" % (rep["outcome"], ev))
    rep, ev, _ = harness(ok_reply(GOOD), load_ok=False)
    buf = io.StringIO()
    SR.render(rep, out=buf)
    check("D9", rep["outcome"] == "RESTORE" and SR.EXIT["RESTORE"] == 5 and len(rep["rows"]) == 3 and "SCENE RESTORE FAILED" in buf.getvalue(),
          "%s rows %d" % (rep["outcome"], len(rep["rows"])))
    rep, ev, call = harness(ok_reply(GOOD), save_fails=True)
    check("D10", rep["outcome"] == "NO_RUN" and call.calls.get(SR.TOOL, 0) == 0 and "save failed" in rep.get("error", ""),
          "%s %s %s" % (rep["outcome"], call.calls, rep.get("error")))
    rep, _, _ = harness({"result": ok_reply(GOOD)})
    check("D11", rep["outcome"] == "PASS" and len(rep["rows"]) == 3, rep["outcome"])
    rep, _, _ = harness({"success": True, "result": ok_reply(GOOD[:2] + [row("storeroom_bomb_pit_control", "VERDICT", "FAIL")])})
    check("D12", rep["outcome"] == "FAIL" and len(rep["rows"]) == 3, rep["outcome"])
    outs = []
    for bad in ({"success": True}, {"success": True, "rows": None}, {"success": True, "rows": ["bad"]},
                {"success": True, "rows": [{"scene": "s", "status": "PASS"}]}):
        try:
            r13, _, _ = harness(bad)
            outs.append(r13["outcome"])
        except Exception as ex:                          # noqa: BLE001 - a crash is the defect this case looks for
            outs.append("CRASH %s" % type(ex).__name__)
    check("D13", outs == ["NO_RUN"] * 4, str(outs))
    rep, _, _ = harness(None, load_raises=OSError("pipe closed"))
    check("D14", rep["outcome"] == "RESTORE" and "save failed" not in str(rep.get("error")), "%s %s" % (rep["outcome"], rep.get("error")))

    import contextlib
    import tempfile
    import types
    fake = types.ModuleType("rimbridge_client")

    def no_endpoint(*a, **k):
        raise ConnectionRefusedError("bridge port closed")
    fake.resolve_endpoint = no_endpoint
    fake.RimBridge = None
    real = sys.modules.get("rimbridge_client")
    sys.modules["rimbridge_client"] = fake
    try:
        with tempfile.TemporaryDirectory() as td:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = SR.main(["--type", "X.Y", "--out", os.path.join(td, "e.json")])
            check("D15", code == 4 and "could not reach the bridge" in buf.getvalue() and os.path.exists(os.path.join(td, "e.json")),
                  "exit %s: %s" % (code, buf.getvalue()[-200:]))
            cwd = os.getcwd()
            os.chdir(td)
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    SR.main(["--type", "X.Y", "--out", "evidence.json"])
                check("D16", os.path.exists(os.path.join(td, "evidence.json")), "relative --out evidence.json written")
            finally:
                os.chdir(cwd)
    finally:
        if real is not None:
            sys.modules["rimbridge_client"] = real
        else:
            sys.modules.pop("rimbridge_client", None)

    def rd(*p):
        return open(os.path.join(REPO, *p), encoding="utf-8").read()
    tools = rd("src", "RimMandrake", "bridgetools", "JawaBench.BridgeTools", "JawaBenchSceneRunnerTools.cs")
    safety = rd("src", "RimMandrake", "bridgetools", "JawaBench.BridgeTools", "JawaBenchSafetyCore.cs")
    check("W1", re.search(r'\[Tool\(\s*"jawa/run_scenes"', tools) is not None, "the tool is declared")
    check("W2", '["jawa/run_scenes"] = FTestOnly' in safety, "CAMPAIGN refuses jawa/run_scenes (test-only family)")
    ek = rd("src", "RimMandrake", "ExplosiveKnockback", "Source", "RM_KnockbackScenes.cs")
    attr = rd("src", "RimMandrake", "_Shared", "SceneRunner", "RMTestAttribute.cs")
    csproj = rd("src", "RimMandrake", "ExplosiveKnockback", "Source", "RimMandrake_ExplosiveKnockback.csproj")
    check("W3", ek.lstrip().startswith("#if RM_PROOFS") and attr.lstrip().startswith("#if RM_PROOFS")
          and ek.rstrip().endswith("#endif") and attr.rstrip().endswith("#endif"), "the suite and the attribute compile only under RM_PROOFS")
    check("W4", re.search(r'\[RMTest\("storeroom_bomb_pit", Ticks = 900, Outside = "haulables [-0-9,]+ >= 1"\)\]', ek) is not None
          and '[RMTest("storeroom_bomb_pit_control", Ticks = 900)]' in ek, "the EK suite declares the storeroom pair, the main lane with an Outside count")
    check("W5", 'Include="RM_KnockbackScenes.cs"' in csproj and "SceneRunner\\RMTestAttribute.cs" in csproj, "the EK csproj compiles both")
    check("W6", "class RMTestAttribute" in attr and "AllowMultiple = true" in attr and "JawaBenchSceneRunnerCore.AttributeName" not in attr
          and 'AttributeName = "RMTestAttribute"' in rd("src", "RimMandrake", "bridgetools", "JawaBench.BridgeTools", "JawaBenchSceneRunnerCore.cs"),
          "the runner matches the attribute's type name")
    bad = [c for c, ok, _ in RESULTS if not ok]
    print("scene-runner driver: %d/%d passed%s" % (len(RESULTS) - len(bad), len(RESULTS), (" FAILED " + ",".join(bad)) if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
