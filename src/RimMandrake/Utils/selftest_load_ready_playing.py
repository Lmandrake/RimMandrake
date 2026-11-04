#!/usr/bin/env python3
"""selftest_load_ready_playing.py - a rimworld/load_game_ready success is held by rimbridge_client until get_game_info
reads programState Playing, and comes back success False with stuckProgramState when it never does
(BRIDGE_LOAD_FIX_READY_WHILE_INITIALIZING). No socket: RimBridge._request is replaced per case.

The instance (live r8, 2026-10-26): the first load_game_ready after a cold launch answered success / game_loaded in 8 s
while programState stayed MapInitializing for >3 min (SmashTools DetachedMapComponentCache duplicate key in
Map.FinalizeLoading); the harness believed it and clockgate then refused every tick.
"""
import atexit
import json
import os
import shutil
import sys
import tempfile

_TMP = tempfile.mkdtemp(prefix="st_selftest_load_ready_playing_")
atexit.register(shutil.rmtree, _TMP, True)
os.environ["TMPDIR"] = tempfile.tempdir = _TMP
os.environ["RIMBRIDGE_EVIDENCE_LOG"] = os.path.join(_TMP, "bridge_calls.jsonl")
os.environ["RIMBRIDGE_SESSION_LOG"] = ""
os.environ["RIMFLOW_DRIVER_LOCK"] = os.path.join(_TMP, "no_driver_lock.json")   # a real holder must not redden this
os.environ.pop("RIMBRIDGE_CALL_DEADLINE", None)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rimbridge_client as C  # noqa: E402

C.LOAD_READY_POLL_S = 0.0
FAILS = []


def check(ok, msg):
    print("%-5s %s" % ("ok" if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


def run(load_reply, states, params=None, wait_s="0.2"):
    """One load_game_ready through RimBridge.call. `states`: successive get_game_info programStates (an Exception
    instance is raised instead; the last entry repeats). -> (reply, number of get_game_info polls)."""
    os.environ[C.LOAD_READY_WAIT_ENV] = wait_s
    b = C.RimBridge(token="t", timeout=30.0)
    polls = {"n": 0}

    def req(method, p=None):
        name = (p or {}).get("name")
        if name == "rimworld/get_game_info":
            i = min(polls["n"], len(states) - 1)
            polls["n"] += 1
            s = states[i]
            if isinstance(s, Exception):
                raise s
            return {"status": "game_loaded", "state": {"programState": s}}
        if name == C.LOAD_READY_TOOL:
            return json.loads(json.dumps(load_reply))
        raise AssertionError("unexpected call %s" % name)
    b._request = req
    r = b.call(C.LOAD_READY_TOOL, dict({"saveName": "BENCH_leaf_scenes_20261026"}, **(params or {})), check=False)
    for x in C.outstanding_indeterminate():
        C.reconcile_resolve(x["cid"], "not-applied", "selftest")
    return r, polls["n"]


def main():
    ok = {"success": True, "status": "game_loaded", "message": "game data is available and is paused for automation"}

    # 1. the r8 instance: success reply, the game never leaves MapInitializing
    r, n = run(ok, ["MapInitializing"])
    check(r.get("success") is False, "stuck MapInitializing -> success False (got %r)" % r.get("success"))
    check(r.get("stuckProgramState") == "MapInitializing", "stuckProgramState names MapInitializing (%r)"
          % r.get("stuckProgramState"))
    check(r.get("loadReplySuccess") is True and "MapInitializing" in str(r.get("error")),
          "the bridge's own success is kept and the error names the state")
    check(n >= 2, "it polled more than once before giving up (%d)" % n)

    # 2. a healthy load: a few MapInitializing reads, then Playing
    r, n = run(ok, ["MapInitializing", "MapInitializing", "Playing"], wait_s="30")
    check(r.get("success") is True and r.get("programStateAfter") == "Playing", "settles on Playing -> success True")
    check(n == 3, "stops polling at the first Playing (%d polls)" % n)

    # 3. the 2026-08-20 trap: success while nothing loaded (Entry)
    r, _ = run(ok, ["Entry"])
    check(r.get("success") is False and r.get("stuckProgramState") == "Entry", "success while at Entry -> refused")

    # 4. readiness asked for mid-load on purpose is passed through, unpolled
    r, n = run(ok, ["MapInitializing"], params={"readiness": "mapData"})
    check(r.get("success") is True and n == 0, "readiness=mapData passes through without a poll (%d)" % n)
    r, n = run(ok, ["Playing"], params={"readiness": "playable"})
    check(r.get("success") is True and n == 1, "readiness=playable is held for Playing (%d polls)" % n)

    # 5. a failure reply is left alone
    bad = {"success": False, "error": "Save 'x' does not exist."}
    r, n = run(bad, ["Playing"])
    check(r == bad and n == 0, "failure reply untouched and unpolled")

    # 6. a get_game_info that does not answer (busy main thread) is waited through
    r, _ = run(ok, [C.RimBridgeError("timed out waiting"), "Playing"], wait_s="30")
    check(r.get("success") is True, "a timed-out poll is retried, then Playing -> success True")
    r, _ = run(ok, [C.RimBridgeError("timed out waiting")])
    check(r.get("success") is False and "timed out" in str(r.get("error")), "never answering -> refused, cause named")

    # 7. an MCP content-wrapped reply keeps its shape
    wrapped = {"content": [{"type": "text", "text": json.dumps(ok)}]}
    r, _ = run(wrapped, ["MapInitializing"])
    inner = json.loads(r["content"][0]["text"]) if isinstance(r, dict) and r.get("content") else {}
    check(inner.get("success") is False and inner.get("stuckProgramState") == "MapInitializing",
          "wrapped reply rewritten inside content[0].text")

    print("\n%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
