#!/usr/bin/env python3
"""selftest_closeout_drain_real_chain.py — one goodbye with four helpers alive, end to end, loses nothing.

CLOSEOUT_DRAIN_PROVE_REAL_RESTART_LIVE (PLAN step 2 live proof, design/RimMandrake/parallel_review_2026-10-31/PLAN.md).
selftest_seat_restart.py D1-D10 prove each step with every reader faked. This runs the whole chain once with the
readers REAL: a real OS process is the window (its sessions/<pid>.json carries its kernel birth tick), four real helper
processes write their own subagent transcripts and ledger lines, the shard lives in a real git clone with a bare origin
and a `publish` that commits by explicit path and pushes, and the Dispatcher's own decide()/execute() with
SR.default_obs() SIGTERMs the window. Faked only: the Claude session listing (`claude agents --json`, built from the
session file instead), the shared bridge (read as free) and the fleet fallback launcher (cannot run). Nothing outside
a temp dir is written. Read outside it, as the live wake does: dispatcher_schedule.json (the live BENCH entries, so a
retune of their thresholds can move this test), the Designer's pending turns and the process tree (claude_ancestor).

  R1  request --fresh --now after his goodbye, 4 helpers alive: DEFERRED naming all 4, exit 0, request recorded
  R2  drain_of: the window's session drains (next and the spawn hook refuse); another session does not
  R3  ticks while any helper lives: held, never killed; the hold names the helper still running
  R4  every helper ended, its ledger line in the clone but not on origin: held for the unpublished shard
  R5  the window publishes the shard: the next tick SIGTERMs exactly that process, and it is dead
  R6  nothing lost: every helper's ledger line is on origin/main, every helper transcript ends on its final message
  R7  wake lists all 4 drained helpers with their transcript paths
"""
import argparse  # noqa: F401
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_closeout_chain_")
HOME = os.path.join(TMP, "claude")
os.environ.update({"RM_DISPATCHER_STATE": os.path.join(TMP, "state"), "TESTQ_QUEUE": os.path.join(TMP, "testq"),
                   "RM_SEAT_LOG_DIR": os.path.join(TMP, "seat_log"), "CLAUDE_CONFIG_DIR": HOME,
                   "RM_RESTART_NOW_DIR": os.path.join(TMP, "restart-now"), "SEAT_RESTART_NO_TICK": "1",
                   "RM_SEAT_RESTART_SCHEDULE": os.path.join(TMP, "sched.json"),
                   "RM_SCRATCH_ROOT": os.path.join(TMP, "scratch"),        # seat_clones: no real scratch clone read
                   "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"})  # no signing or hooks of the user's
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import dispatcher as D  # noqa: E402
import seat_restart as SR  # noqa: E402

FAILS = []
SEAT = "BENCH"
SID = "sid-goodbye-window"
CLONE = os.path.join(TMP, "clone")
ORIGIN = os.path.join(TMP, "origin.git")
SHARD = "infrastructure/state/ledger/events/%s.jsonl" % SEAT
HELPERS = [("agent-real%d" % i, "real job %d" % i) for i in range(4)]
PROCS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(t)) + ".000Z"


def git(*a):
    r = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=CLONE, capture_output=True,
                       text=True, timeout=60)
    if r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr.strip()))
    return r.stdout


PUBLISH = """#!/bin/sh
# the sandbox ./publish: commit the named paths by explicit path, push to origin main
set -e
[ "$1" = "-m" ] && { msg="$2"; shift 2; }
git -c user.name=t -c user.email=t@t add -- "$@"
git -c user.name=t -c user.email=t@t commit -q -m "${msg:-publish}" -- "$@"
git push -q origin HEAD:main
"""


def setup_repo():
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", ORIGIN], check=True, timeout=60)
    subprocess.run(["git", "clone", "-q", ORIGIN, CLONE], check=True, timeout=60, capture_output=True)
    os.makedirs(os.path.join(CLONE, os.path.dirname(SHARD)))
    with open(os.path.join(CLONE, SHARD), "w") as f:
        f.write(json.dumps({"event": "note", "id": "SEED", "seat": SEAT, "ts": iso(time.time() - 7200)}) + "\n")
    with open(os.path.join(CLONE, "publish"), "w") as f:
        f.write(PUBLISH)
    os.chmod(os.path.join(CLONE, "publish"), 0o755)
    git("checkout", "-q", "-b", "main")
    git("add", SHARD, "publish")
    git("commit", "-q", "-m", "seed")
    git("push", "-q", "origin", "HEAD:main")
    git("fetch", "-q", "origin")


def schedule():
    """The LIVE BENCH entries of dispatcher_schedule.json, pointed at the sandbox clone and log."""
    with open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8") as f:
        live = json.load(f)
    seat = dict(live["seats"][SEAT], clone=CLONE)
    sr = dict(live["seat_restart"]["seats"][SEAT], seat_log=os.path.join(TMP, "conductor_log.md"))
    s = {"seats": {SEAT: seat}, "seat_restart": {"enabled": True, "dry": False, "seats": {SEAT: sr}},
         "ledger_notes": False, "publish": False}
    with open(os.environ["RM_SEAT_RESTART_SCHEDULE"], "w") as f:
        json.dump(s, f)
    return D.load_schedule(os.environ["RM_SEAT_RESTART_SCHEDULE"])


def append(path, rec):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def human(t, text):
    return {"type": "user", "timestamp": iso(t), "origin": {"kind": "human"}, "promptSource": "typed",
            "message": {"role": "user", "content": text}}


def assistant(t, stop, ctx=150_000):
    return {"type": "assistant", "timestamp": iso(t),
            "message": {"role": "assistant", "stop_reason": stop, "usage": {"input_tokens": ctx},
                        "content": [{"type": "text", "text": "ok"}] if stop == "end_turn" else
                        [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "x"}}]}}


def notice(t, hid):
    return {"type": "user", "timestamp": iso(t), "origin": {"kind": "task-notification"}, "promptSource": "system",
            "message": {"role": "user", "content": "<task-notification><task-id>%s</task-id>completed"
                                                   "</task-notification>" % hid}}


HELPER = r"""
import json, os, sys, time
tx, go, shard, hid = sys.argv[1:5]
def put(p, r):
    with open(p, "a") as f:
        f.write(json.dumps(r) + "\n")
def iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + ".000Z"
put(tx, {"type": "user", "timestamp": iso(), "message": {"role": "user", "content": "do " + hid}})
put(tx, {"type": "assistant", "timestamp": iso(), "message": {"role": "assistant", "stop_reason": "tool_use",
         "content": [{"type": "tool_use", "id": "h", "name": "Bash", "input": {}}]}})
open(tx + ".started", "w").close()
while not os.path.exists(go):
    time.sleep(0.05)
put(shard, {"event": "note", "id": "HELPER_RESULT_" + hid.upper().replace("-", "_"), "seat": "BENCH", "ts": iso(),
            "why": "result of " + hid})
put(tx, {"type": "assistant", "timestamp": iso(), "message": {"role": "assistant", "stop_reason": "end_turn",
         "content": [{"type": "text", "text": "FINAL " + hid}]}})
"""


def start_helpers(tx_main):
    sub = os.path.join(tx_main[:-len(".jsonl")], "subagents")
    os.makedirs(sub, exist_ok=True)
    for hid, desc in HELPERS:
        with open(os.path.join(sub, hid + ".meta.json"), "w") as f:
            json.dump({"description": desc}, f)
        p = subprocess.Popen([sys.executable, "-c", HELPER, os.path.join(sub, hid + ".jsonl"),
                              os.path.join(TMP, hid + ".go"), os.path.join(CLONE, SHARD), hid])
        PROCS.append(p)
    deadline = time.time() + 30
    while time.time() < deadline and not all(os.path.exists(os.path.join(sub, h + ".jsonl.started")) for h, _ in HELPERS):
        time.sleep(0.05)
    up = [h for h, _ in HELPERS if os.path.exists(os.path.join(sub, h + ".jsonl.started"))]
    check(len(up) == len(HELPERS), "setup: all 4 helper processes started and are mid-tool (%s)" % up)
    for h in up:
        os.remove(os.path.join(sub, h + ".jsonl.started"))
    return sub


def finish_helper(hid, proc):
    open(os.path.join(TMP, hid + ".go"), "w").close()
    proc.wait(timeout=30)


def tick(sch, st, now):
    """One Dispatcher pass over the seat_restart path: decide() on SR.default_obs (real readers), then execute()."""
    sf = SR.session_file(WINDOW.pid) or {}
    sessions = [dict(sf, status=sf.get("status"))] if sf and SR.proc_alive(WINDOW.pid, SR.reg_start(sf)) else []
    o = {"paused": None, "agents": {"state": "MEASURED", "sessions": sessions},
         "seat_restart": SR.default_obs(sch, D.seat_events_since)}
    acts = []

    def act(**kw):
        kw.setdefault("at", D.iso(now))
        acts.append(kw)
    SR.decide(sch, st, o, now, True, act)
    res = []
    for a in acts:
        if a["do"] in SR.DOES:
            res.append((a["do"], SR.execute(a, sch, st, True, now, {})))
    D.save(st, os.environ["RM_DISPATCHER_STATE"])      # the tick's own save: drain_of reads it from state.json
    return acts, res


def holds(acts, res):
    return " | ".join([a.get("why") or "" for a in acts if a["do"] == "restart_hold"] + [r for d, r in res if r])


def session_state(st):
    return ((st.get("seat_restart") or {}).get(SEAT) or {})


def main():
    global WINDOW
    setup_repo()
    sch = schedule()
    SR.REPO = CLONE                   # the window's clone: request reads and publishes its shard there
    SR.bridge_reading = lambda seat: {"state": "MEASURED", "holders": []}   # the shared bridge: free (not under test)
    SR.MACHINE = os.path.join(TMP, "no-machine.json")   # no fleet relaunch argv: the fallback launcher never starts
    SR.run_fallback = lambda argv: FAILS.append("the fleet fallback was run: %s" % argv) or "refused in the test"
    WINDOW = subprocess.Popen(["sleep", "900"])
    PROCS.append(WINDOW)
    born = SR.proc_start(WINDOW.pid)
    os.makedirs(os.path.join(HOME, "sessions"), exist_ok=True)
    sfp = os.path.join(HOME, "sessions", "%d.json" % WINDOW.pid)
    sfile = {"pid": WINDOW.pid, "sessionId": SID, "cwd": CLONE, "name": "CONDUCTOR", "kind": "interactive",
             "status": "busy", "procStart": str(born), "startedAt": int(time.time() * 1000)}
    SR._write_json(sfp, sfile)
    tx = SR.transcript_path(CLONE, SID)
    os.makedirs(os.path.dirname(tx), exist_ok=True)
    t = time.time()
    append(tx, human(t - 600, "land the four jobs"))
    append(tx, assistant(t - 590, "tool_use"))
    sub = start_helpers(tx)
    append(tx, assistant(t - 580, "end_turn"))
    append(tx, human(t - 60, "goodbye"))
    append(tx, assistant(t - 55, "tool_use"))        # the goodbye turn runs the close-out: the request itself

    # R1 -------------------------------------------------------------------------------------------------------------
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = SR.main(["request", "--seat", "CONDUCTOR", "--ticket", "GOODBYE", "--reason", "goodbye", "--fresh",
                      "--now", "--pid", str(WINDOW.pid), "--note", "goodbye with four helpers out"])
    out = out.getvalue()
    rq = SR._read_json(SR.request_path(SEAT)) or {}
    check(rc == 0 and "DEFERRED" in out and "REFUSED" not in out, "R1 request exits 0 and prints DEFERRED (rc %s: %s)"
          % (rc, out[-300:].replace("\n", " / ")))
    check(all(h in out and d in out for h, d in HELPERS), "R1 the DEFERRED line names all 4 helpers by id and job")
    check(rq.get("deferred") is True and sorted(h["id"] for h in rq.get("helpers") or []) == sorted(h for h, _ in HELPERS)
          and rq.get("session_id") == SID and rq.get("pid") == WINDOW.pid,
          "R1 the request is recorded: deferred, the 4 helpers, this window (%s)" % {k: rq.get(k) for k in (
              "deferred", "session_id", "pid", "helpers")})
    append(tx, assistant(time.time(), "end_turn"))   # the goodbye turn ends; the window goes idle, draining
    SR._write_json(sfp, dict(sfile, status="idle"))

    # R2 -------------------------------------------------------------------------------------------------------------
    check(bool(SR.drain_of(SEAT, SID)), "R2 the window's session is draining: %s" % SR.drain_of(SEAT, SID))
    check(SR.drain_of(SEAT, "sid-another-window") is None, "R2 another session is not drained by this request")

    # R3 -------------------------------------------------------------------------------------------------------------
    st = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}
    killed_early = []
    for i, (hid, _) in enumerate(HELPERS):
        acts, res = tick(sch, st, time.time())
        if any(d == "restart_kill" and r.startswith("killed") for d, r in res) or WINDOW.poll() is not None:
            killed_early.append(hid)
        still = [h for h, _ in HELPERS[i:]]
        why = holds(acts, res)
        named = [h for h, _ in HELPERS if h in why]
        check(named == still, "R3 %d helper(s) alive: held, naming exactly the live ones %s (%s)"
              % (len(still), still, why[:200]))
        check(SR.drain_of(SEAT, SID) is not None, "R3 still draining with %d alive" % len(still))
        finish_helper(hid, PROCS[1 + i])
        append(tx, notice(time.time(), hid))              # its notice reaches the window, which reads it
        append(tx, assistant(time.time(), "end_turn"))
    check(not killed_early and WINDOW.poll() is None, "R3 the window is never killed while a helper lives (%s)"
          % killed_early)

    # R4 -------------------------------------------------------------------------------------------------------------
    unpub = SR.unpublished_shard(SEAT, CLONE)
    check(bool(unpub) and "uncommitted" in unpub, "R4 the helpers' lines leave the shard unpublished (%s)" % unpub)
    acts, res = tick(sch, st, time.time())
    why = holds(acts, res)
    check(WINDOW.poll() is None and "unpublished" in why, "R4 all helpers done, shard unpublished: held (%s)" % why[:200])

    # R5 -------------------------------------------------------------------------------------------------------------
    pub = SR.publish_shard(SEAT, CLONE)               # the window's close-out: commit by explicit path, ./publish
    git("fetch", "-q", "origin")
    check(pub is None and SR.unpublished_shard(SEAT, CLONE) is None, "R5 the window published its shard (%s)" % pub)
    append(tx, assistant(time.time(), "end_turn"))
    time.sleep(1.2)
    acts, res = None, []
    for k in range(3):                                # a tick may claim, the next kills; a few at most
        acts, r = tick(sch, st, time.time())
        res += r
        if WINDOW.poll() is not None:
            break
    kills = [r for d, r in res if d == "restart_kill"]
    check(WINDOW.poll() is not None and any(r.startswith("killed pid %d" % WINDOW.pid) for r in kills),
          "R5 the shard on origin: the window process is SIGTERMed and dead (%s; state %s)"
          % (kills or holds(acts, res)[:200], session_state(st).get("state")))
    rec = SR._read_json(SR.killed_path(SEAT)) or {}
    check(rec.get("session_id") == SID and not rec.get("aborted")
          and sorted(rec.get("drained") or {}) == sorted(h for h, _ in HELPERS),
          "R5 the killed record names this window and carries the 4 drained helpers (%s)" % rec.get("drained"))

    # R6: reachability. What the helpers made is where the next window reads it ----------------------------------------
    on_origin = subprocess.run(["git", "show", "origin/main:" + SHARD], cwd=CLONE, capture_output=True, text=True,
                               timeout=60).stdout
    ids = [json.loads(x).get("id") for x in on_origin.splitlines() if x.strip()]
    want = ["HELPER_RESULT_" + h.upper().replace("-", "_") for h, _ in HELPERS]
    check(all(w in ids for w in want), "R6 every helper's ledger line is on origin/main (%d of %d)"
          % (sum(w in ids for w in want), len(want)))
    finals = []
    for hid, _ in HELPERS:
        with open(os.path.join(sub, hid + ".jsonl"), encoding="utf-8") as f:
            last = json.loads(f.read().splitlines()[-1])
        finals.append(((last.get("message") or {}).get("content") or [{}])[0].get("text") == "FINAL " + hid)
    check(all(finals), "R6 every helper transcript ends on its final message (%s)" % finals)

    # R7 -------------------------------------------------------------------------------------------------------------
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            SR.main(["wake", "--seat", "CONDUCTOR"])
        except Exception as e:  # noqa: BLE001 - a crash is a failed wake, reported below
            print("WAKE RAISED %r" % e)
    out = out.getvalue()
    block = out.split("== helpers the old window drained", 1)[-1] if "== helpers the old window drained" in out else ""
    check(block and all(os.path.join(sub, h + ".jsonl") in block and d in block for h, d in HELPERS),
          "R7 wake lists all 4 drained helpers with their transcripts (%s)"
          % (block[:400].replace("\n", " / ") or out[-400:].replace("\n", " / ")))
    check("WAKE RAISED" not in out, "R7 the wake ran to its end")


if __name__ == "__main__":
    WINDOW = None
    try:
        main()
    finally:
        for p in PROCS:
            if p.poll() is None:
                p.kill()
        shutil.rmtree(TMP, ignore_errors=True)
    print("\n%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    sys.exit(1 if FAILS else 0)
