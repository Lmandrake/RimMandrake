#!/usr/bin/env python3
"""scene_runner.py - drive jawa/run_scenes, the shared in-game scene runner (RIMMANDRAKE_BUILD_SHARED_SCENE_RUNNER_FIRST_SLICE).

    python.exe src\\RimMandrake\\Utils\\scene_runner.py --type RimMandrake.ExplosiveKnockback.RM_KnockbackScenes
        [--scenes a,b] [--ticks N] [--frame-budget-ms 40] [--out evidence.json]

ONE bridge call runs the whole suite in game (each scene on its own plot: stage, ticks in process, the runner's outside
reads, the scene's judge; contract in src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchSceneRunnerCore.cs).
Around that call the game is saved to a unique file first and reloaded after, also when the run raises (owner 2026-11-17,
"Just save the test in a file and reload"; modcheck/scene_snapshot.py), so no scene cleans its plot by hand.

Needs python.exe (the bridge binds Windows loopback), a SCRATCH map, the bridge held, the JawaBench companion with
jawa/run_scenes, and the mod's PROOF build (RM_PROOFS). Prints one row table, the time split and the bridge-call count.

Exit codes, one per cause (never collapsed): 0 every row PASS · 1 a row FAILED · 2 a row UNMEASURED, or no rows (EMPTY) ·
3 PROOF BUILD REQUIRED (the suite type is not loaded) · 4 the run could not be made (the save failed, the bridge refused
or dropped the call; nothing was judged) · 5 the scene-begin save could not be reloaded (the map is NOT back where it began;
the rows are printed but the game needs a hand reload of the named save).

A suite with no row read from outside the mod gets SUITE_OUTSIDE_READ UNMEASURED (live_test_speed_assessment §3 (c):
a judge that reads only the mod's own state shares its blind spots).
"""
import argparse
import datetime
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "modcheck"))

TOOL = "jawa/run_scenes"
PASS, FAIL, UNMEASURED = "PASS", "FAIL", "UNMEASURED"
EXIT = {"PASS": 0, "FAIL": 1, "UNMEASURED": 2, "EMPTY": 2, "PROOF_BUILD": 3, "NO_RUN": 4, "RESTORE": 5}
PROOF_BUILD_MSG = ("PROOF BUILD REQUIRED: %s is not loaded (the mod is inactive or runs its RELEASE build). Build its proof build "
                   "(python3 src/RimMandrake/Utils/winbuild.py <Mod> -- -p:RmProofs=true), deploy it, run this, then put the "
                   "release build back.")


class CountingCall(object):
    """call(tool, **kw) over a bridge `send(tool, params) -> reply`, counting every call by tool (the before/after measure)."""

    def __init__(self, send):
        self.send, self.calls = send, {}

    def __call__(self, tool, **kw):
        self.calls[tool] = self.calls.get(tool, 0) + 1
        return self.send(tool, kw)

    @property
    def total(self):
        return sum(self.calls.values())


def unwrap(reply):
    """The tool's own object out of a bridge reply: {"result": {...tool payload...}} (whatever transport fields, such as its
    own "success", the envelope carries) or the payload itself; None when it is not a dict."""
    if isinstance(reply, dict) and "rows" not in reply and isinstance(reply.get("result"), dict):
        inner = reply["result"]
        if "rows" in inner or "success" in inner or "message" in inner:
            reply = inner
    return reply if isinstance(reply, dict) else None


def _text(v):
    return isinstance(v, str) and v.strip() != ""


def valid_row(r):
    """A row the table can carry: scene and check named, status PASS / FAIL / UNMEASURED, an UNMEASURED row with its cause."""
    return (isinstance(r, dict) and _text(r.get("scene")) and _text(r.get("check"))
            and r.get("status") in (PASS, FAIL, UNMEASURED) and (r.get("status") != UNMEASURED or _text(r.get("cause"))))


def valid_rows(rows):
    """The rows when they are an explicit list of valid rows, else None. An explicit [] stays [] (EMPTY); a missing, null
    or malformed rows field, or any malformed row, is None (the run could not be read: NO_RUN, never a verdict)."""
    if not isinstance(rows, list) or not all(valid_row(r) for r in rows):
        return None
    return rows


def overall(rows):
    """Same rule as JawaBenchSceneRunnerCore.Overall: FAIL > UNMEASURED > PASS; no rows is EMPTY (neither)."""
    if not rows:
        return "EMPTY"
    st = [r.get("status") for r in rows]
    if FAIL in st:
        return FAIL
    if any(s != PASS for s in st):
        return UNMEASURED
    return PASS


def with_outside_guard(rows):
    """Append SUITE_OUTSIDE_READ UNMEASURED when no row came from outside the mod; rows unchanged otherwise."""
    if rows and not any(r.get("source") == "outside" for r in rows):
        rows = rows + [{"scene": "(suite)", "check": "SUITE_OUTSIDE_READ", "status": UNMEASURED, "measured": None,
                        "expected": ">= 1 outside row", "source": "driver",
                        "cause": "no row was read from outside the mod: give a scene an RMTest Outside count"}]
    return rows


def run(call, type_name, scenes="", ticks=0, frame_budget_ms=40.0, timeout_s=600, snapshot=None, clock=time.time):
    """-> report dict with 'outcome' (a key of EXIT) and everything printed. `call` is a CountingCall; `snapshot` the
    scene_snapshot context manager (injected by the selftest)."""
    if snapshot is None:
        from scene_snapshot import scene_snapshot as snapshot
    from scene_snapshot import SceneRestoreError
    rep = {"type": type_name, "scenes_asked": scenes, "rows": [], "split": {}, "snapshot": None}
    t0 = clock()
    reply = None
    phase = "save"                                       # save -> run -> restore: which one an exception came from
    try:
        with snapshot(call, "scene_runner_pre_") as snap:
            phase = "run"
            rep["snapshot"] = snap.name
            rep["split"]["save_s"] = round(clock() - t0, 2)
            t1 = clock()
            try:
                reply = call(TOOL, type=type_name, scenes=scenes, ticks=ticks, frameBudgetMs=frame_budget_ms,
                             timeoutMs=int(timeout_s * 1000))
            except Exception as ex:                      # noqa: BLE001 - a dropped call is "could not run", reported
                rep["error"] = "%s raised %s: %s" % (TOOL, type(ex).__name__, ex)
            rep["split"]["run_s"] = round(clock() - t1, 2)
            t2 = clock()
            phase = "restore"
        rep["split"]["reload_s"] = round(clock() - t2, 2)
        rep["restore"] = dict(snap.evidence.get("restore_load") or {})
    except SceneRestoreError as ex:
        rep["restore_error"] = str(ex)
    except Exception as ex:                              # noqa: BLE001 - classified by the phase it came from
        if phase == "save":
            rep["error"] = "the scene-begin save failed, nothing was staged: %s: %s" % (type(ex).__name__, ex)
        else:
            rep["restore_error"] = "%s during %s: %s" % (type(ex).__name__, phase, ex)
    rep["split"]["total_s"] = round(clock() - t0, 2)
    rep["bridge_calls"] = dict(call.calls, total=call.total)
    r = unwrap(reply)
    if r is not None:
        rep["scenes"] = r.get("scenes") or []
        rep["suite_begin"] = r.get("suiteBegin")
        rep["game_overall"] = r.get("overall")
        if r.get("success") is True:
            rows = valid_rows(r.get("rows"))
            if rows is None:
                rep["error"] = "the run answered success with unreadable rows (%s): nothing can be judged" % (
                    type(r.get("rows")).__name__ if not isinstance(r.get("rows"), list) else "a row without scene, check, a PASS/FAIL/UNMEASURED status or an UNMEASURED row's cause")
            else:
                rep["rows"] = with_outside_guard(list(rows))
        else:
            msg = str(r.get("message") or r)
            rep["error"] = msg
            rep["refusal"] = r.get("details")
            rep["proof_build_missing"] = "Type not found" in msg
    elif reply is not None and "error" not in rep:
        rep["error"] = "unreadable reply: %r" % (reply,)
    if rep.get("restore_error"):          # the map is not back: the loudest cause, whatever the run said
        rep["outcome"] = "RESTORE"
    elif rep.get("proof_build_missing"):
        rep["outcome"] = "PROOF_BUILD"
    else:
        if "error" in rep or r is None or r.get("success") is not True:
            rep["outcome"] = "NO_RUN"
        else:
            rep["outcome"] = overall(rep["rows"])
    return rep


def render(rep, out=None):
    out = out or sys.stdout                              # read at call time: a redirected stdout is honoured
    p = lambda s="": print(s, file=out)
    if rep["outcome"] == "PROOF_BUILD":
        p(PROOF_BUILD_MSG % rep["type"])
    if rep.get("error"):
        p("NO RUN: %s" % rep["error"])
        if rep.get("refusal"):
            p("  %s" % json.dumps(rep["refusal"])[:600])  # cut-ok: terminal display
    if rep["rows"]:
        p("%-28s %-34s %-10s %-14s %-10s %s" % ("SCENE", "CHECK", "STATUS", "MEASURED", "EXPECTED", "SOURCE / CAUSE"))
        for r in rep["rows"]:
            tail = r.get("source") or ""
            if r.get("cause"):
                tail += " / " + str(r["cause"])
            p("%-28s %-34s %-10s %-14s %-10s %s" % (str(r.get("scene"))[:28], str(r.get("check"))[:34], r.get("status"),
                                                    str(r.get("measured"))[:14], str(r.get("expected"))[:10], tail[:160]))  # cut-ok: terminal display
    for s in rep.get("scenes") or []:
        p("  %-26s origin %-8s ticks %s/%s in %s frames; stage %s ms, ticks %s ms, judge %s ms" % (
            s.get("scene"), s.get("origin"), s.get("ticksStepped"), s.get("ticksWanted"), s.get("frames"),
            s.get("stageMs"), s.get("tickMs"), s.get("judgeMs")))
    sp = rep["split"]
    p("time: save %s s, run %s s, reload %s s, total %s s; bridge calls %s" % (
        sp.get("save_s"), sp.get("run_s"), sp.get("reload_s"), sp.get("total_s"), rep["bridge_calls"]))
    if rep.get("restore_error"):
        p("SCENE RESTORE FAILED: %s (reload %s by hand)" % (rep["restore_error"], rep.get("snapshot")))
    if rep.get("game_overall") not in (None, rep["outcome"]) and rep["outcome"] in (PASS, FAIL, UNMEASURED, "EMPTY"):
        p("note: the game's own overall was %s; the driver's (with its guard rows) is %s" % (rep["game_overall"], rep["outcome"]))
    p("OUTCOME %s (exit %d)" % (rep["outcome"], EXIT[rep["outcome"]]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--type", required=True, help="the suite's full type name")
    ap.add_argument("--scenes", default="", help="comma list; empty = every scene of the suite")
    ap.add_argument("--ticks", type=int, default=0, help="ticks per scene; 0 = each scene's own")
    ap.add_argument("--frame-budget-ms", type=float, default=40.0)
    ap.add_argument("--timeout-s", type=float, default=600.0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    rep = None
    try:
        from rimbridge_client import RimBridge, resolve_endpoint
        host, port, token = resolve_endpoint()
        with RimBridge(host=host, port=port, token=token, timeout=a.timeout_s + 120) as b:
            call = CountingCall(lambda tool, kw: b.call(tool, kw, check=False))
            rep = run(call, a.type, a.scenes, a.ticks, a.frame_budget_ms, a.timeout_s)
    except Exception as ex:                              # noqa: BLE001 - no bridge is "could not run" (exit 4), never a FAIL
        if rep is None:
            rep = {"type": a.type, "rows": [], "split": {}, "bridge_calls": {}, "outcome": "NO_RUN",
                   "error": "could not reach the bridge: %s: %s" % (type(ex).__name__, ex)}
        else:
            rep["teardown_error"] = "%s: %s" % (type(ex).__name__, ex)
    out = a.out or os.path.join(os.environ.get("RM_SCRATCH", r"D:\ClaudeWork\rimmandrake"), "scene_runner",
                                "run_%s.json" % datetime.datetime.now().strftime("%Y%m%dT%H%M%S"))
    try:
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=1, default=str)
        rep["evidence"] = out
    except OSError as ex:
        print("evidence NOT written (%s): %s" % (out, ex), file=sys.stderr)
    render(rep)
    if rep.get("evidence"):
        print("evidence:", rep["evidence"])
    return EXIT[rep["outcome"]]


if __name__ == "__main__":
    sys.exit(main())
