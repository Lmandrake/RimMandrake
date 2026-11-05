#!/usr/bin/env python3
"""selftest_steve_worker.py - the durable SteveDesktop worker (worker.py) on a throwaway TESTQ_HOME with mock phases.

No game, no ssh, no pull: the deploy/load/down/run commands are replaced by a small mock, the driver lock is a temp
file, and the attempt detaches as a plain new session (TESTQ_NO_SYSTEMD=1). Proves DONE with attested deploy hashes
and NOT_RUN accounting, duplicate delivery, --retry, hang -> one restart -> DONE, hang twice -> INVALID/HANG, no sheet
-> INVALID/HARNESS, a modcheck refusal -> BLOCKED_SELECTION, a fresh game start resolving only the bridge markers older
than it (a kept game with an older marker is restarted first, once per marker), a game gone or replaced after the run -> INVALID/GAME_DIED (also in
the canary; alive + red canary -> CANARY; a status that cannot tell keeps the verdict), guard held by another driver -> deferred busy 75, busy -> 75, stop -> INTERRUPTED, a dead attempt
finalized, SOURCE_SHA_MISSING, and the real deploy route: deploy_flags' flags pass deploy_custom_mods.py's checks.
Attempt.deploy() deploys the composed closure (TerminalBiomes carries LuminousPigment) and an unreadable closure ends
the job INVALID/DEPLOY (RELAPSE_STEVE_FIX_DIED_TWICE).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WORKER = os.path.join(HERE, "worker.py")
RUNNER = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC_TREE = RUNNER  # the real tree: mod folders for the deploy route stay read from here
# The worker runs at a git sha (rev-parse HEAD, source_sha checkouts). A bare export (a blind checker's tree) has no
# git: commit the trees the worker reads into a throwaway repo and run against that copy instead of crashing.
if subprocess.run(["git", "-C", RUNNER, "rev-parse", "--verify", "HEAD"], capture_output=True).returncode != 0:
    _copy = tempfile.mkdtemp(prefix="steve_worker_git_")
    for _rel in ("infrastructure/stevedesktop", "src/RimMandrake/bridgetools", "src/RimMandrake/Utils",
                 "src/RimMandrake/contracts", "src/RimMandrake/rimflow"):
        if os.path.isdir(os.path.join(RUNNER, _rel)):
            shutil.copytree(os.path.join(RUNNER, _rel), os.path.join(_copy, _rel),
                            ignore=shutil.ignore_patterns("__pycache__", ".git"))
    # case 14's deploy closure reads every mod's About.xml and the compose manifest (modcheck runner.src_mods_by_id)
    import glob as _glob
    for _p in sorted(_glob.glob(os.path.join(RUNNER, "src", "*", "*", "About"))
                     + _glob.glob(os.path.join(RUNNER, "src", "*", "*.compose.json"))):
        _dst = os.path.join(_copy, os.path.relpath(_p, RUNNER))
        if os.path.exists(_dst):
            continue
        if os.path.isdir(_p):
            shutil.copytree(_p, _dst)
        else:
            os.makedirs(os.path.dirname(_dst), exist_ok=True)
            shutil.copy2(_p, _dst)
    _g = ["git", "-C", _copy, "-c", "user.name=selftest", "-c", "user.email=selftest@invalid"]
    for _a in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "-m", "bare-export snapshot"]):
        subprocess.run(_g + _a, check=True, capture_output=True)
    print("no git checkout at %s: running against a committed snapshot %s" % (RUNNER, _copy))
    RUNNER, HERE = _copy, os.path.join(_copy, "infrastructure", "stevedesktop")
    WORKER = os.path.join(HERE, "worker.py")
sys.path.insert(0, os.path.join(RUNNER, "src", "RimMandrake", "Utils", "testq"))
sys.path.insert(0, os.path.join(RUNNER, "src", "RimMandrake", "bridgetools"))
import schema as S  # noqa: E402
import companion_identity as CI  # noqa: E402

FAILS = []
BRIDGE = r'''
import json, os, sys
path, args = sys.argv[1], sys.argv[2:]
m = json.load(open(path))
if "--resolve" in args:
    if os.environ.get("TESTQ_MOCK_RESOLVE_FAIL"):
        print("evidence row NOT written", file=sys.stderr); sys.exit(1)
    cid = args[args.index("--resolve") + 1]
    assert args[args.index("--as") + 1] == "not-applied" and args[args.index("--note") + 1].startswith("moot:")
    m.pop(cid)
    json.dump(m, open(path, "w"))
    print("reconciled %s as not-applied" % cid)
else:
    print("evidence log x; %d mutating call(s) with UNKNOWN outcome" % len(m))
    for cid, t in m.items():
        print("  %s  %s  jawa/time_clock  args 0  pid 1 cli.py  INDETERMINATE" % (cid, t))
'''
MOCK = r'''
import json, os, sys, time
mode = os.environ.get("MOCK_MODE", "pass")
sheet_dir = os.environ["TESTQ_SHEET_DIR"]
mark = os.path.join(os.environ["TESTQ_HOME"], "mock_hung_once")
if mode == "hang" or (mode == "hang-once" and not os.path.exists(mark)):
    open(mark, "w").close()
    time.sleep(60)
if mode == "refuse":
    print("REFUSED: every selected chain of Mock is offline (c0)"); sys.exit(2)
if mode == "crash":
    print("Traceback: boom"); sys.exit(3)
if mode == "no_game":
    print('{"status": "no_game", "message": "No game is currently loaded", "state": {"programState": "Entry"}}')
    print("hasCurrentGame: False mapCount: None -> NOT READY"); sys.exit(1)
stale_mark = os.path.join(os.environ["TESTQ_HOME"], "mock_stale_once")
if mode in ("stale", "stale-nokeep") or (mode == "stale-once" and not os.path.exists(stale_mark)):
    open(stale_mark, "w").close()
    print("[modcheck] Mock HARNESS UNMEASURED: the running load is not the composed list (restart the game on it): "
          "not loaded: rw.mod.simplestairs; loaded but not composed: adaptive.storage.framework")
    if mode != "stale-nokeep":
        print("STALE_LOAD: Mock: ModsConfig left on the composed list; restart the game on it and run again")
    sys.exit(1)
if mode == "fatal":
    print("Windows fatal exception: access violation\n\nThread 0x1: File gate.py line 9 in hash\n" + "x" * 800)
    print("[modcheck] long tail " * 40); sys.exit(5)
name = "Mock_%d" % int(time.time() * 1000)
summary = {"chains": [{"name": "c1", "components": [{"name": "r1", "verdict": "PASS", "detail": "ok"},
                                                    {"name": "r2", "verdict": "FAIL", "detail": "bad"}]}]}
if mode == "canary":
    print("[modcheck] vanilla canary RED: no mod row runs")
    summary = {"chains": [{"name": "c1", "components": [{"name": "r1", "verdict": "UNMEASURED",
                                                         "detail": "vanilla canary red: not a verdict on the mod"}]}]}
json.dump({"mod": "Mock", "summary": summary}, open(os.path.join(sheet_dir, name + ".json"), "w"))
open(os.path.join(sheet_dir, name + ".html"), "w").write("<html/>")
import subprocess
print("HEAD_AT_RUN", subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip())
if mode == "expect":
    print('EXPECTED_ROWS ["r1", "r2", "r_lost"]')
print("args:", " ".join(sys.argv[1:]))
print("[modcheck] sheet \\\\wsl.localhost\\Ubuntu\\x\\Transient\\modcheck\\%s.html" % name)
sys.exit(1)
'''


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    tmp = tempfile.mkdtemp(prefix="rf_steveworker_")
    try:
        home, sheets, mods = (os.path.join(tmp, d) for d in ("home", "sheets", "mods"))
        for d in (home, sheets, os.path.join(mods, "Mock", "1.6", "Assemblies"), os.path.join(mods, "Mock", "Defs")):
            os.makedirs(d)
        open(os.path.join(mods, "Mock", "1.6", "Assemblies", "Mock.dll"), "wb").write(b"MZ")
        open(os.path.join(mods, "Mock", "Defs", "a.xml"), "w").write("<Defs/>")
        mock = os.path.join(tmp, "mock_modcheck.py")
        open(mock, "w").write(MOCK)
        lock = os.path.join(tmp, "DRIVER_LOCK.json")
        env = {k: v for k, v in os.environ.items() if k not in ("RM_HOST_GUARD_GEN", "RIMFLOW_SEAT")}
        env.update(TESTQ_HOME=home, TESTQ_SHEET_DIR=sheets, TESTQ_MODS_DIR=mods, TESTQ_SKIP_PULL="1",
                   TESTQ_NO_SYSTEMD="1", TESTQ_CMD_DEPLOY="true", TESTQ_CMD_LOAD="true", TESTQ_CMD_DOWN="true",
                   TESTQ_CMD_PROBE="true", TESTQ_PROBE_GAP_S="0",  # the kept game answers unless a case says not
                   TESTQ_CMD_RUN="%s %s run" % (sys.executable, mock), RIMFLOW_DRIVER_LOCK=lock,
                   TESTQ_CMD_STATUS="echo 'running pid=4242 session=1'",  # never the real rw_game.sh status
                   RM_HOST="stevedesktop", RM_GAME_USERDATA=tmp, RIMFLOW_LEDGER=os.path.join(tmp, "ev.jsonl"))
        head = subprocess.run(["git", "-C", RUNNER, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        # the deploy phase refuses a companion not built from the job's sources (selftest_steve_worker_companion.py
        # covers that): here, one that is
        env["TESTQ_COMPANION_DIR"] = os.path.join(tmp, "BridgeTools", "JawaBench")
        CI.write_fixture(os.path.join(env["TESTQ_COMPANION_DIR"], CI.DLL_NAME), CI.srchash_at(RUNNER, head))

        def w(args, job=None, **extra):
            r = subprocess.run([sys.executable, WORKER] + args, input=json.dumps(job) if job else None,
                               env=dict(env, **extra), capture_output=True, text=True, timeout=60)
            try:
                return r.returncode, json.loads(r.stdout.strip().splitlines()[-1])
            except (ValueError, IndexError):
                return r.returncode, {"raw": r.stdout + r.stderr}

        def job(**kw):
            return S.make_job("Mock", {"rows": ["r1", "r2", "r9"]}, "commission", "BENCH", head, **kw)

        def wait_result(aid, limit=40):
            t = time.time()
            while time.time() - t < limit:
                path = os.path.join(home, "attempts", aid, "result.json")
                if os.path.exists(path):
                    return json.load(open(path))
                time.sleep(0.3)
            return {}

        # 1. a clean attempt
        j = job()
        rc, o = w(["start"], j)
        check(rc == 0 and o.get("state") == "started" and o["attempt"] == j["id"] + ".a1", "start detaches a1: %s" % o)
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "DONE" and res.get("modcheck_exit") == 1, "a FAIL row is still a DONE run: %s"
              % res.get("note"))
        verdicts = {r["row"]: r["verdict"] for r in res.get("rows", [])}
        check(verdicts == {"r1": "PASS", "r2": "FAIL", "r9": "NOT_RUN"},
              "requested row absent -> NOT_RUN: %s" % verdicts)
        dep = res.get("deployed", {}).get("mods", {}).get("Mock", {})
        check(dep.get("files") == 2 and len(dep.get("dll_sha256", "")) == 64, "deployed identity attested: %s" % dep)
        check(len(res.get("artifacts", [])) == 3 and "phase_s" in res and "run" in res["phase_s"],
              "artifacts hashed and phases timed")
        args = open(os.path.join(home, "attempts", o["attempt"], "modcheck.log")).read()
        check("--rows r1,r2,r9 --canary --validity --reuse off" in args, "modcheck got the job's arguments")
        check(not os.path.exists(os.path.join(home, "current")) and not os.path.exists(lock),
              "the attempt released current and the game guard")
        rc, o2 = w(["outbox"])
        check(o["attempt"] in o2.get("outbox", []), "the result waits in the outbox")
        w(["ack", "--attempt", o["attempt"]])
        check(w(["outbox"])[1].get("outbox") == [], "ack empties it")

        # 2. duplicate delivery and retry
        rc, o3 = w(["start"], j)
        check(o3.get("attempt") == o["attempt"] and o3.get("duplicate") and o3.get("state") == "finished",
              "a duplicate start returns the finished attempt, no second run: %s" % o3)
        rc, o4 = w(["start", "--retry"], j)
        check(o4.get("attempt") == j["id"] + ".a2", "--retry makes a2")
        wait_result(o4.get("attempt", "x"))

        # 3. a hang, a clean restart, a pass
        j = job()
        rc, o = w(["start"], j, MOCK_MODE="hang-once", TESTQ_RUN_TIMEOUT_S="2")
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "DONE" and res.get("retries") == 1, "hang -> restart -> DONE with retries=1: %s"
              % res.get("note"))
        os.remove(os.path.join(home, "mock_hung_once"))
        j = job()
        rc, o = w(["start"], j, MOCK_MODE="hang", TESTQ_RUN_TIMEOUT_S="2")
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "INVALID" and res.get("cause") == "HANG", "hang twice -> INVALID/HANG")

        # 3a. STEVE_LANE_UNSTICK_BRAKED_UNOWNED_8EB8: the game came up on FULL, modcheck refused the stale load and
        # left ModsConfig on its composed list; the worker restarts the game onto it once and runs again
        sdowns = os.path.join(tmp, "stale_downs")
        rc, o = w(["start"], job(), MOCK_MODE="stale-once", TESTQ_CMD_DOWN="echo down >> %s" % sdowns)
        res = wait_result(o.get("attempt", "x"))
        adir = os.path.join(home, "attempts", o.get("attempt", "x"))
        check(res.get("outcome") == "DONE" and res.get("retries") == 1 and res.get("harness_cause") == "stale_load"
              and "simplestairs" in (res.get("stale_load_bounced") or ""),
              "a stale load -> one restart onto the composed list -> DONE, the cause recorded: %s %s"
              % (res.get("outcome"), res.get("note")))
        check(os.path.exists(sdowns) and len(open(sdowns).readlines()) == 1
              and os.path.exists(os.path.join(adir, "modcheck.stale_load.log")),
              "the restart stopped the game once and kept the refused run's log")
        rc, o = w(["start"], job(), MOCK_MODE="stale", TESTQ_CMD_DOWN="echo down >> %s" % (sdowns + "_2"))
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "INVALID" and res.get("cause") == "HARNESS"
              and res.get("harness_cause") == "stale_load"
              and (res.get("note") or "").startswith("stale_load (after a restart"),
              "stale again after the restart -> INVALID/HARNESS, cause stale_load, unrepaired: %s" % res.get("note"))
        check(len(open(sdowns + "_2").readlines()) == 1, "only one restart is spent on a stale load")
        rc, o = w(["start"], job(), MOCK_MODE="stale-nokeep", TESTQ_CMD_DOWN="echo down >> %s" % (sdowns + "_3"))
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "INVALID" and res.get("harness_cause") == "stale_load"
              and not os.path.exists(sdowns + "_3") and "not left on the composed list" in (res.get("note") or ""),
              "a stale load with the list restored -> INVALID at once, no restart that cannot help: %s"
              % res.get("note"))

        # 3b. a killed game: its lost-reply bridge marker is moot once load starts a fresh game, and only then
        bridge = os.path.join(tmp, "mock_bridge.py")
        open(bridge, "w").write(BRIDGE)
        markers = os.path.join(tmp, "markers.json")
        old_cid, new_cid = "a88fdb7a88ea4064", "b99fdb7a88ea4065"

        def fresh_markers():
            json.dump({old_cid: "2000-01-01T00:00:00Z", new_cid: "2999-01-01T00:00:00Z"}, open(markers, "w"))
        fresh_markers()
        bx = dict(TESTQ_CMD_BRIDGE="%s %s %s" % (sys.executable, bridge, markers))
        rc, o = w(["start"], job(), TESTQ_CMD_LOAD="echo started pid 4242", **bx)
        res = wait_result(o.get("attempt", "x"))
        left = json.load(open(markers))
        check(res.get("outcome") == "DONE" and res.get("moot_markers") == [old_cid] and list(left) == [new_cid],
              "a fresh game resolves only the markers older than it: %s left %s" % (res.get("moot_markers"), left))
        # 3b'. STEVE_RIG_FIX_OUTOFBAND_DRIVER_MARKER: a KEPT game carrying a marker older than this load (2026-10-26:
        # a modcheck driver killed mid step_game_ticks) is restarted, then the fresh start resolves it moot; before
        # the fix the job ran on and its handshake was refused -> INVALID/HARNESS, three jobs in a row
        fresh_markers()
        flag, downs = os.path.join(tmp, "load_once"), os.path.join(tmp, "downs")
        # (the pid is computed: worker.log echoes the command line, and load reads that log's tail)
        flaky = ("if [ -f %s ]; then echo started pid $((4300+43)); else touch %s; echo 'already running (pid 4242)'; fi"
                 % (flag, flag))
        rc, o = w(["start"], job(), TESTQ_CMD_LOAD=flaky, TESTQ_CMD_DOWN="echo down >> %s" % downs,
                  TESTQ_CMD_STATUS="echo 'running pid=4343 session=1'", **bx)
        res = wait_result(o.get("attempt", "x"))
        left = json.load(open(markers))
        check(res.get("outcome") == "DONE" and res.get("bounced_for_markers") == [old_cid]
              and res.get("moot_markers") == [old_cid] and list(left) == [new_cid]
              and os.path.exists(downs) and len(open(downs).read().split()) == 1,
              "a kept game with a stale marker is restarted once and the marker resolved moot: %s %s %s bounced=%s "
              "moot=%s left=%s" % (res.get("outcome"), res.get("cause"), res.get("note"),
                                   res.get("bounced_for_markers"), res.get("moot_markers"), list(left)))
        json.dump({new_cid: "2999-01-01T00:00:00Z"}, open(markers, "w"))
        rc, o = w(["start"], job(), TESTQ_CMD_LOAD="echo 'already running (pid 4242)'", **bx)
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "DONE" and "bounced_for_markers" not in res and "moot_markers" not in res
              and list(json.load(open(markers))) == [new_cid],
              "a kept game with no marker older than the load is not restarted: %s" % res.get("note"))
        fresh_markers()
        rc, o = w(["start"], job(), TESTQ_CMD_LOAD="echo 'already running (pid 4242)'", **bx)
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "INVALID" and res.get("cause") == "LOAD" and len(json.load(open(markers))) == 2,
              "a restart that never yields a fresh game is INVALID/LOAD, markers kept: %s %s"
              % (res.get("cause"), res.get("note")))
        # 3b''. STEVEWORKER_FIX_MARKER_BOUNCE_EVERY_JOB: a marker the restart could NOT resolve (resolve fails, or the
        # client's marker delete silently gives up) must not cost every later job a game restart: one restart per
        # marker, then the next job fails fast (INVALID/HARNESS, nothing restarted) naming the marker to reconcile
        fresh_markers()
        # (the INVALID/LOAD case above restarted for old_cid and never got a fresh game, so it stays remembered and
        # would fail this job fast too: start from a reconciled slate)
        for f in (flag, downs, os.path.join(home, "marker_bounces.json")):
            if os.path.exists(f):
                os.remove(f)
        rc, o = w(["start"], job(), TESTQ_CMD_LOAD=flaky, TESTQ_CMD_DOWN="echo down >> %s" % downs,
                  TESTQ_CMD_STATUS="echo 'running pid=4343 session=1'", TESTQ_MOCK_RESOLVE_FAIL="1", **bx)
        res = wait_result(o.get("attempt", "x"))
        check(res.get("bounced_for_markers") == [old_cid] and "moot_markers" not in res
              and len(open(downs).read().split()) == 1, "an unresolvable marker: the first job restarts once: %s %s"
              % (res.get("bounced_for_markers"), res.get("note")))
        rc, o = w(["start"], job(), TESTQ_CMD_LOAD="echo 'already running (pid 4343)'",
                  TESTQ_CMD_DOWN="echo down >> %s" % downs, TESTQ_CMD_STATUS="echo 'running pid=4343 session=1'",
                  TESTQ_MOCK_RESOLVE_FAIL="1", **bx)
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "INVALID" and res.get("cause") == "HARNESS" and old_cid in (res.get("note") or "")
              and len(open(downs).read().split()) == 1,
              "the next job with the same marker does not restart the game again: %s %s downs=%d"
              % (res.get("cause"), res.get("note"), len(open(downs).read().split())))

        # 3c. the game dies mid-run (TESTQ_DEAD_GAME_RUN_FIX_READS_DONE): modcheck still writes a sheet of
        # UNMEASURED rows, but a game that is gone, or is another process, measured nothing -> INVALID/GAME_DIED
        load = dict(TESTQ_CMD_LOAD="echo started pid 4242")
        rc, o = w(["start"], job(), TESTQ_CMD_STATUS="echo stopped; exit 3", **load)
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "INVALID" and res.get("cause") == "GAME_DIED" and len(res.get("rows", [])) == 3,
              "a game gone after the run -> INVALID/GAME_DIED, rows kept as evidence: %s %s %s"
              % (res.get("outcome"), res.get("cause"), res.get("note")))
        rc, o = w(["start"], job(), TESTQ_CMD_STATUS="echo 'running pid=5151 session=1 started=x'", **load)
        res = wait_result(o.get("attempt", "x"))
        check(res.get("cause") == "GAME_DIED", "another game process after the run -> GAME_DIED: %s" % res.get("note"))
        rc, o = w(["start"], job(), TESTQ_CMD_STATUS="echo 'running pid=4242 session=1 started=x'",
                  TESTQ_CMD_LOAD="echo 'already running (pid 4242)'")
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "DONE", "the same game still running -> DONE: %s" % res.get("note"))
        rc, o = w(["start"], job(), TESTQ_CMD_STATUS="echo powershell broke; exit 1", **load)
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "DONE" and "liveness unknown" in (res.get("note") or ""),
              "a status that cannot tell keeps the verdict and says so: %s" % res.get("note"))

        # 3d. the kept game stopped answering (STEVE_LANE_FIX_WEDGED_KEPT_GAME, 10-30: 5 jobs on one hung game, 14 h dark)
        wdowns, wprobes, wlog = (os.path.join(tmp, n) for n in ("wedge_downs", "wedge_probes", "wedge_load"))
        kept = "echo 'already running (pid 4242)'"
        flaky = os.path.join(tmp, "wedge_load.sh")          # a file: the worker logs the command, and sh() tails that log
        open(flaky, "w").write("if [ -f %s ]; then echo 'started pid 4242'; else %s; fi\n" % (wdowns, kept))
        flaky = "bash " + flaky
        deaf = "echo x >> %s; echo 'bridge error: timed out after 30.0s' >&2; exit 1" % wprobes
        rc, o = w(["start"], job(), TESTQ_CMD_LOAD=flaky, TESTQ_CMD_DOWN="echo down >> %s" % wdowns,
                  TESTQ_CMD_PROBE=deaf, TESTQ_CMD_STATUS="echo 'running pid=4242 session=1'")
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "DONE" and "timed out" in (res.get("bounced_unresponsive") or "")
              and len(open(wdowns).read().split()) == 1 and len(open(wprobes).read().split()) == 2,
              "a kept game deaf to two probes is restarted once and the job runs: %s %s %s"
              % (res.get("outcome"), res.get("cause"), res.get("bounced_unresponsive")))
        os.remove(wdowns)
        rc, o = w(["start"], job(), TESTQ_CMD_LOAD=kept, TESTQ_CMD_DOWN="echo down >> %s; exit 1" % wdowns,
                  TESTQ_CMD_PROBE=deaf)
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "INVALID" and res.get("cause") == "LOAD" and not res.get("rows")
              and res.get("modcheck_exit") is None,
              "a wedged game that cannot be stopped -> INVALID/LOAD, no run: %s %s" % (res.get("cause"), res.get("note")))
        os.remove(wdowns)
        rc, o = w(["start"], job(), TESTQ_CMD_LOAD=kept, TESTQ_CMD_DOWN="echo down >> %s" % wdowns,
                  TESTQ_CMD_PROBE="exit 127")
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "DONE" and not os.path.exists(wdowns),
              "a probe that cannot run keeps the game: %s %s" % (res.get("outcome"), res.get("note")))
        answered = "if [ -f %s ]; then exit 0; else touch %s; exit 1; fi" % (wlog, wlog)
        rc, o = w(["start"], job(), TESTQ_CMD_LOAD=kept, TESTQ_CMD_DOWN="echo down >> %s" % wdowns,
                  TESTQ_CMD_PROBE=answered, TESTQ_CMD_STATUS="echo 'running pid=4242 session=1'")
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "DONE" and not os.path.exists(wdowns),
              "one missed probe (autosave) keeps the game: %s %s" % (res.get("outcome"), res.get("note")))

        # 3e. an overgrown kept game is recycled before the job (STEVE_GAME_FIX_UNBOUNDED_MAPS: 17 h, 27 maps, then deaf)
        rdowns = os.path.join(tmp, "recycle_downs")
        grown = os.path.join(tmp, "recycle_load.sh")
        ok_maps = "echo '{\"status\": \"Playing\", \"mapCount\": 3}'"
        def recycle(status_line, maps, down_rc=0):
            open(grown, "w").write("if [ -f %s ]; then echo 'started pid 4242'; else echo 'already running (pid 4242)'; "
                                   "echo '%s'; fi\n" % (rdowns, status_line))
            if os.path.exists(rdowns):
                os.remove(rdowns)
            rc, o = w(["start"], job(), TESTQ_CMD_LOAD="bash " + grown, TESTQ_CMD_PROBE="true", TESTQ_CMD_MAPS=maps,
                      TESTQ_CMD_DOWN="echo down >> %s; exit %d" % (rdowns, down_rc),
                      TESTQ_CMD_STATUS="echo 'running pid=4242 session=1'")
            return wait_result(o.get("attempt", "x"))
        young, old = "running pid=4242 session=1 age_s=600", "running pid=4242 session=1 age_s=28801"
        res = recycle(old, ok_maps)
        check(res.get("outcome") == "DONE" and "h old" in (res.get("recycled_kept_game") or "")
              and len(open(rdowns).read().split()) == 1, "a kept game past the age limit is restarted, the job runs: %s %s"
              % (res.get("outcome"), res.get("recycled_kept_game")))
        res = recycle(young, "echo '{\"mapCount\": 20}'")
        check(res.get("outcome") == "DONE" and "20 maps" in (res.get("recycled_kept_game") or "")
              and os.path.exists(rdowns), "a kept game at the map limit is restarted: %s" % res.get("recycled_kept_game"))
        res = recycle(young, ok_maps)
        check(res.get("outcome") == "DONE" and not os.path.exists(rdowns) and "recycled_kept_game" not in res
              and res.get("kept_game_maps") == 3, "a young small game is kept: %s %s" % (res.get("outcome"), res.get("note")))
        res = recycle(young, "echo 'bridge error' >&2; exit 1")
        check(res.get("outcome") == "DONE" and not os.path.exists(rdowns),
              "a map count that cannot be read keeps a young game: %s" % res.get("note"))
        res = recycle(old, "echo 'bridge error' >&2; exit 1")
        check(res.get("outcome") == "DONE" and os.path.exists(rdowns),
              "an unread map count does not excuse an old game: %s" % res.get("outcome"))
        res = recycle(old, ok_maps, down_rc=1)
        check(res.get("outcome") == "INVALID" and res.get("cause") == "LOAD" and res.get("modcheck_exit") is None,
              "an overgrown game that cannot be stopped -> INVALID/LOAD, no run: %s %s" % (res.get("cause"), res.get("note")))
        open(grown, "w").write("echo 'already running (pid 4242)'; echo '%s'\n" % old)
        os.remove(rdowns) if os.path.exists(rdowns) else None
        rc, o = w(["start"], job(), TESTQ_CMD_LOAD="bash " + grown, TESTQ_WORKER_HOST="archmagi",
                  TESTQ_CMD_DOWN="echo down >> %s" % rdowns, TESTQ_CMD_STATUS="echo 'running pid=4242 session=1'")
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "DONE" and not os.path.exists(rdowns) and "recycled_kept_game" not in res,
              "the archmagi lane's kept game is never recycled, however old: %s %s" % (res.get("outcome"), res.get("note")))

        # STEVE_WORKER_UNSTICK_WOUNDED_GAME_KEPT_UP: a live game that cannot hold a map is not handed to the next job
        ndowns = os.path.join(tmp, "no_game_downs")
        logdir = os.path.join(tmp, "gamelog")
        os.makedirs(logdir, exist_ok=True)
        game_log = os.path.join(logdir, "Player.log")

        def no_game_run(text, downs):
            """Stopping the mock game deletes Player.log, as a cold start does: a copy made after the stop finds nothing."""
            with open(game_log, "wb") as f:
                f.write(text)
            rc, o = w(["start"], job(), MOCK_MODE="no_game", TESTQ_CMD_STATUS="echo 'running pid=4242 session=1'",
                      TESTQ_CMD_DOWN="echo down >> %s; rm -f %s" % (downs, game_log), RM_GAME_LOGDIR=logdir, **load)
            return wait_result(o.get("attempt", "x")), os.path.join(home, "attempts", o.get("attempt", "x"), "Player.log")

        def kept_whole(path, text):
            """The kept file IS the game's log, byte for byte: everything else in it is the evidence the copy exists for."""
            if not os.path.exists(path):
                return False
            with open(path, "rb") as f:
                return f.read() == text

        fixture = (b"XML error noise Exception loading def\nSystem.BadImageFormatException: AlienRace.dll\n"
                   b"System.TypeLoadException: WorldGenStep\nlast line\n")
        res, kept = no_game_run(fixture, ndowns)
        note = res.get("note") or ""
        check(not os.path.exists(game_log), "the stop in this case really takes the game's log away: %s" % game_log)
        check(os.path.exists(kept) and "BadImageFormat" in open(kept).read() and "TypeLoadException" in open(kept).read(),
              "a no_game run keeps Player.log, whole, in the attempt BEFORE the stop takes it: %s" % note)
        check(kept_whole(kept, fixture), "the kept log is the game's log byte for byte, not a digest of it: %s" % kept)
        check("first fatal: System.BadImageFormatException" in note and "TypeLoadException" not in note,
              "of two fatal lines the note names the FIRST, and only it: %s" % note)
        check(res.get("outcome") == "INVALID" and res.get("cause") == "HARNESS", "no_game, game alive -> HARNESS: %s %s"
              % (res.get("cause"), res.get("note")))
        check(os.path.exists(ndowns) and len(open(ndowns).readlines()) == 1 and "cold-starts" in (res.get("note") or ""),
              "a no_game run stops the game once so the next job cold-starts: %s" % res.get("note"))
        fixture = b"Exception early\nException late\nend\n"
        res, kept = no_game_run(fixture, ndowns + "_generic")
        note = res.get("note") or ""
        check(kept_whole(kept, fixture), "a log with no fatal line is kept byte for byte too: %s" % kept)
        check(os.path.exists(kept) and "last exception: Exception late" in note and "first fatal" not in note,
              "no fatal line: the last exception is reported and labelled as that, never as the first fatal: %s" % note)
        fixture = b"a clean log\n"
        res, kept = no_game_run(fixture, ndowns + "_clean")
        check(kept_whole(kept, fixture), "a log with no exception is kept byte for byte too: %s" % kept)
        check(os.path.exists(kept) and "no exception in it" in (res.get("note") or ""),
              "a log with no exception is kept and says so: %s" % res.get("note"))
        fixture = b"native noise \xff\xfe\r\nSystem.BadImageFormatException: AlienRace.dll\r\nend, no newline"
        res, kept = no_game_run(fixture, ndowns + "_raw")
        check(kept_whole(kept, fixture), "CRLF, a bad UTF-8 byte and an unterminated last line survive the copy: %s" % kept)
        rc, o = w(["start"], job(), MOCK_MODE="no_game", TESTQ_CMD_STATUS="echo 'running pid=4242 session=1'",
                  TESTQ_CMD_DOWN="echo 'REFUSED: never stops the owner game'; exit 3", **load)
        res = wait_result(o.get("attempt", "x"))
        check(res.get("cause") == "HARNESS" and "game NOT stopped (never stops the owner game)" in (res.get("note") or ""),
              "a lane that may not stop the game says so in the note: %s" % res.get("note"))
        check("game log NOT kept" in (res.get("note") or ""), "a Player.log it cannot read is said, never fatal: %s"
              % res.get("note"))
        hdowns = os.path.join(tmp, "harness_downs")
        rc, o = w(["start"], job(), MOCK_MODE="crash", TESTQ_CMD_STATUS="echo 'running pid=4242 session=1'",
                  TESTQ_CMD_DOWN="echo down >> %s" % hdowns, **load)
        res = wait_result(o.get("attempt", "x"))
        check(res.get("cause") == "HARNESS" and not os.path.exists(hdowns),
              "a HARNESS death that names no lost game keeps the game: %s %s" % (res.get("cause"), res.get("note")))

        cdowns = os.path.join(tmp, "canary_downs")
        rc, o = w(["start"], job(), MOCK_MODE="canary", TESTQ_CMD_STATUS="echo 'running pid=4242 session=1'",
                  TESTQ_CMD_DOWN="echo down >> %s" % cdowns, **load)
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "INVALID" and res.get("cause") == "CANARY", "a red canary, game alive -> CANARY: %s"
              % res.get("cause"))
        # STEVE_LANE_FIX_DEAD_COLONY_CANARY_RED: the kept game with a dead colony voided every later job
        check(os.path.exists(cdowns) and len(open(cdowns).read().split()) == 1 and "cold-starts" in (res.get("note") or ""),
              "a red canary stops the game once so the next job cold-starts: downs=%s note=%s"
              % (len(open(cdowns).read().split()) if os.path.exists(cdowns) else 0, res.get("note")))
        rc, o = w(["start"], job(), MOCK_MODE="canary", TESTQ_CMD_STATUS="echo stopped; exit 3", **load)
        res = wait_result(o.get("attempt", "x"))
        check(res.get("cause") == "GAME_DIED", "a game killed in the canary is GAME_DIED, not a red canary: %s"
              % res.get("cause"))

        # 4. no sheet
        rc, o = w(["start"], job(), MOCK_MODE="crash")
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "INVALID" and res.get("cause") == "HARNESS", "no sheet -> INVALID/HARNESS")

        rc, o = w(["start"], job(), MOCK_MODE="fatal")
        res = wait_result(o.get("attempt", "x"))
        check(res.get("cause") == "HARNESS" and "Windows fatal exception: access violation" in (res.get("note") or ""),
              "a faulthandler stack far above the last 300 chars still reaches the note: %s" % (res.get("note") or "")[:120])

        rc, o = w(["start"], job(), MOCK_MODE="refuse")
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "INVALID" and res.get("cause") == "BLOCKED_SELECTION",
              "modcheck's REFUSED line -> INVALID/BLOCKED_SELECTION: %s" % res.get("note"))

        # 5. the guard is held by someone else
        sys.path.insert(0, os.path.join(RUNNER, "src", "RimMandrake", "rimflow"))
        import driver_lock as D
        other = {"pid": 4242, "start": 7.0, "boot_id": None, "platform": "wsl", "host": "archmagi-elsewhere"}
        D.acquire(lock, "BENCH", "interactive session", other)
        jg = job()
        rc, o = w(["start"], jg)
        check(rc == 75 and o.get("state") == "busy" and o.get("deferred") and "BENCH" in o.get("busy_with", "")
              and not os.path.exists(os.path.join(home, "jobs", jg["id"])),
              "guard held by a live non-testq driver -> deferred busy (75), no attempt made: %s %s" % (rc, o))
        D.release(lock, "BENCH", other)
        rc, o = w(["start"], jg)
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "DONE", "the deferred job runs once the guard is free: %s" % res.get("note"))

        # 6. busy, then stop
        ja = job()
        rc, oa = w(["start"], ja, MOCK_MODE="hang", TESTQ_RUN_TIMEOUT_S="50")
        time.sleep(1.5)
        rc, ob = w(["start"], job())
        check(rc == 75 and ob.get("state") == "busy" and ob.get("busy_with") == oa.get("attempt"),
              "a second job while one runs is refused busy (75): %s" % ob)
        rc, st = w(["status", "--job", ja["id"]])
        check(st.get("state") == "running" and st.get("phase") in ("run", "attest", "load", "deploy"),
              "status reports the running attempt and its phase: %s" % st)
        w(["stop", "--attempt", oa["attempt"]])
        res = wait_result(oa["attempt"], 30)
        check(res.get("outcome") == "INTERRUPTED", "stop -> INTERRUPTED: %s" % res.get("note"))
        check(not os.path.exists(lock), "a stopped attempt releases the guard")
        os.remove(os.path.join(home, "mock_hung_once"))

        # 7. a dead attempt (no heartbeat, no result) is finalized at the next start
        jd = job()
        aid = jd["id"] + ".a1"
        os.makedirs(os.path.join(home, "attempts", aid))
        S.dump(jd, os.path.join(home, "attempts", aid, "job.json"))
        st_path = os.path.join(home, "attempts", aid, "state.json")
        S.dump({"phase": "run"}, st_path)
        os.utime(st_path, (time.time() - 600, time.time() - 600))
        open(os.path.join(home, "current"), "w").write(aid + "\n")
        open(os.path.join(home, "jobs", jd["id"]), "w").write(aid + "\n")
        rc, o = w(["start"], job())
        dead = json.load(open(os.path.join(home, "attempts", aid, "result.json")))
        check(dead.get("outcome") == "INTERRUPTED" and dead.get("cause") == "CRASH" and o.get("state") == "started",
              "a dead attempt gets INTERRUPTED/CRASH and the next job starts")
        wait_result(o.get("attempt", "x"))

        # 8. source_sha not in the runner
        rc, o = w(["start"], S.make_job("Mock", {"rows": ["r1"]}, "fix", "BENCH", "deadbeef00"))
        check(o.get("outcome") == "REFUSED" and o.get("cause") == "SOURCE_SHA_MISSING", "unknown source_sha refused")
        # 9. bolt 2: a row the preview planned but the sheet lacks is NOT_RUN (no --rows needed)
        jx = S.make_job("Mock", {"chains": ["c1"]}, "commission", "BENCH", head)
        rc, o = w(["start"], jx, MOCK_MODE="expect")
        res = wait_result(o.get("attempt", "x"))
        vx = {r["row"]: r["verdict"] for r in res.get("rows", [])}
        check(vx == {"r1": "PASS", "r2": "FAIL", "r_lost": "NOT_RUN"}, "EXPECTED_ROWS absent from the sheet -> NOT_RUN: %s" % vx)

        # 14. RELAPSE_STEVE_FIX_DIED_TWICE: Attempt.deploy() is where the Steve lane deploys, and it must put the mods
        # of ours the composed list names in the game too. TerminalBiomes composes mandrake.rm.luminouspigment; a deploy
        # of only the mod left it undeployed and RimWorld dropped it (INVALID/HARNESS stale_load, 2026-11-04). The
        # recorder stands in for the deploy command, so the argv it sees IS what the worker deploys.
        rec, recpy = os.path.join(tmp, "deploy_argv.json"), os.path.join(tmp, "deploy_recorder.py")
        open(recpy, "w").write("import json, sys\njson.dump(sys.argv[1:], open(%r, 'w'))\n" % rec)
        rc, o = w(["start"], S.make_job("TerminalBiomes", {"rows": ["r1"]}, "commission", "BENCH", head),
                  TESTQ_CMD_DEPLOY="%s %s" % (sys.executable, recpy))
        res = wait_result(o.get("attempt", "x"))
        argv = json.load(open(rec)) if os.path.exists(rec) else None
        check(argv is not None and argv[:1] == ["TerminalBiomes"] and "LuminousPigment" in argv,
              "a TerminalBiomes job deploys its closure (LuminousPigment) with the mod: argv %s, %s %s"
              % (argv, res.get("outcome"), res.get("note")))

        # 10. bolt 1: the attempt runs at EXACTLY source_sha even when the clone's HEAD is newer; main comes back after
        scratch = os.path.join(tmp, "clone")
        os.makedirs(scratch)
        def g(*a):
            return subprocess.run(["git", "-C", scratch] + list(a), capture_output=True, text=True).stdout.strip()
        g("init", "-q", "-b", "main")
        csrc = os.path.join(scratch, *CI.SRC_REL.split("/"))       # companion sources, so its companion can be FRESH
        os.makedirs(csrc)
        open(os.path.join(csrc, "A.cs"), "w").write("class A {}\n")
        g("add", CI.SRC_REL)
        for n in ("one", "two"):
            open(os.path.join(scratch, n), "w").write(n)
            g("add", n)
            g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", n)
        first, second = g("rev-parse", "HEAD~1"), g("rev-parse", "HEAD")
        scomp = os.path.join(tmp, "scratch_companion")
        CI.write_fixture(os.path.join(scomp, CI.DLL_NAME), CI.srchash_at(scratch, first))
        env["TESTQ_COMPANION_DIR"] = scomp                         # every later start runs on the scratch clone
        # a slow checkout (post-checkout hook) widens the window between the attempt's last git call and its result:
        # the clone must be back on main BEFORE result.json appears, since the next start may follow at once
        hook = os.path.join(scratch, ".git", "hooks", "post-checkout")
        open(hook, "w").write("#!/bin/sh\nsleep 2\n")
        os.chmod(hook, 0o755)
        jp = S.make_job("Mock", {"rows": ["r1"]}, "commission", "BENCH", first[:12])
        rc, o = w(["start"], jp, TESTQ_CLONE=scratch)
        res = wait_result(o.get("attempt", "x"))
        log = open(os.path.join(home, "attempts", o["attempt"], "modcheck.log")).read()
        check("HEAD_AT_RUN " + first in log and res.get("runner_sha") == first,
              "the run saw source_sha, not the newer HEAD: runner_sha %s" % res.get("runner_sha"))
        check(g("rev-parse", "HEAD") == second and g("symbolic-ref", "--short", "HEAD") == "main"
              and not os.path.exists(os.path.join(home, "pinned_clone")), "the clone is back on main at the newer HEAD")
        # a crash that left the clone pinned is healed by the next start
        g("checkout", "-q", "--detach", first)
        open(os.path.join(home, "pinned_clone"), "w").write(first)
        jh = S.make_job("Mock", {"rows": ["r1"]}, "commission", "BENCH", second)
        rc, o = w(["start"], jh, TESTQ_CLONE=scratch)
        res = wait_result(o.get("attempt", "x"))
        check(res.get("runner_sha") == second and g("symbolic-ref", "--short", "HEAD") == "main",
              "a start heals a leftover pin before it runs: %s" % res.get("runner_sha"))

        # 11. STEVEWORKER_UNSTICK_DIRTY_CLONE_REFUSES_SYNC: a tracked file dirtied while pinned must not wedge the rig
        open(os.path.join(scratch, "one"), "w").write("three")     # main moves on: "one" now differs from the pin
        g("add", "one")
        g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "three")
        third = g("rev-parse", "HEAD")
        g("checkout", "-q", "--detach", second)
        open(os.path.join(home, "pinned_clone"), "w").write(second)
        open(os.path.join(scratch, "one"), "w").write("dirtied by an attempt")
        jd = S.make_job("Mock", {"rows": ["r1"]}, "commission", "BENCH", second)
        rc, o = w(["start"], jd, TESTQ_CLONE=scratch)
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "DONE" and res.get("runner_sha") == second, "a dirty pinned clone is healed, job runs: %s %s"
              % (o, res.get("note")))
        dd = os.path.join(home, "attempts", o.get("attempt", "x"))
        check("one" in (open(os.path.join(dd, "dirty_clone.txt")).read() if os.path.exists(os.path.join(dd, "dirty_clone.txt")) else "")
              and os.path.exists(os.path.join(dd, "dirty_clone.diff")), "the dirt is recorded in the attempt dir")
        check(open(os.path.join(scratch, "one")).read() == "three", "the tracked file was restored")
        # a seat clone (not 'runner', no TESTQ_CLONE) is never self-healed
        r = subprocess.run([sys.executable, "-I", "-c", "import sys;sys.path.insert(0,%r);import worker;print(worker.runner_clone_only())"
                            % os.path.dirname(WORKER)], env={k: v for k, v in env.items() if k != "TESTQ_CLONE"},
                           capture_output=True, text=True, timeout=60)
        check(r.stdout.strip() == "False", "dirty self-heal is off outside the runner clone: %r %s" % (r.stdout, r.stderr[-200:]))
        # 12. STEVEWORKER_HARDEN_OLD_PIN_RUNS_OLD_CODE: the attempt runs the main-checkout worker copy, and a
        # detached clone with NO marker (an old pinned attempt never wrote/removed it) is healed by the outer start
        check(os.path.exists(os.path.join(home, "outer", "worker.py")), "the attempt ran from a copy outside the clone")
        g("checkout", "-q", "--detach", first)
        if os.path.exists(os.path.join(home, "pinned_clone")):
            os.remove(os.path.join(home, "pinned_clone"))
        je = S.make_job("Mock", {"rows": ["r1"]}, "commission", "BENCH", second)
        rc, o = w(["start"], je, TESTQ_CLONE=scratch)
        res = wait_result(o.get("attempt", "x"))
        check(res.get("runner_sha") == second and g("symbolic-ref", "--short", "HEAD") == "main",
              "a detached clone without a marker is healed at the next start: %s" % res.get("runner_sha"))

        # 14b. a closure that cannot be read ends the job INVALID/DEPLOY before anything is deployed: a deploy that
        # guessed [] would drop the mod's dependencies silently, the defect itself. The scratch clone's modcheck
        # runner is broken at the job's source_sha, so the worker's closure read fails there.
        bad = os.path.join(scratch, "src", "RimMandrake", "Utils", "modcheck")
        os.makedirs(bad, exist_ok=True)
        open(os.path.join(bad, "runner.py"), "w").write("raise RuntimeError('selftest: a broken modcheck runner')\n")
        g("add", "src/RimMandrake/Utils/modcheck/runner.py")
        g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "broken runner")
        broken = g("rev-parse", "HEAD")
        if os.path.exists(rec):
            os.remove(rec)
        rc, o = w(["start"], S.make_job("Mock", {"rows": ["r1"]}, "commission", "BENCH", broken), TESTQ_CLONE=scratch,
                  TESTQ_CMD_DEPLOY="%s %s" % (sys.executable, recpy))
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "INVALID" and res.get("cause") == "DEPLOY" and "deploy closure" in (res.get("note") or "")
              and not os.path.exists(rec),
              "an unreadable deploy closure ends the job INVALID/DEPLOY, nothing deployed: %s/%s %s"
              % (res.get("outcome"), res.get("cause"), res.get("note")))

        # 13. TESTQ_FIX_COMPOSE_ROUTE_MOD_WITH: the real deploy route (TESTQ_CMD_DEPLOY mocks it everywhere above).
        # The flags deploy_flags builds from the REAL src tree must get past deploy_custom_mods.py's own argument
        # checks; `--mod FlowWorks --compose biomes` died there as argparse exit 2 on two booked Steve slots.
        deploy_py = os.path.join(SRC_TREE, "src", "RimMandrake", "Utils", "deploy_custom_mods.py")
        probe = ("import runpy,sys; sys.argv=[%r]+sys.argv[1:]; g=runpy.run_path(%r, run_name='dcm');"
                 "g['first_existing'].__globals__['first_existing']=lambda *a: sys.exit('PARSE_OK');"
                 "sys.exit(g['main']())") % (deploy_py, deploy_py)
        src = os.path.join(SRC_TREE, "src")
        for names, want in ((["FlowWorks", "RimMandrake.Biomes"], [("--compose", "biomes"), ("--with", "FlowWorks")]),
                            (["FlowWorks", "Pyrelands", "UtinniPatches"],
                             [("--compose", "biomes"), ("--with", "FlowWorks"), ("--with", "UtinniPatches")]),
                            (["FlowWorks", "UtinniPatches"], [("--mod", "FlowWorks"), ("--mod", "UtinniPatches")])):
            flags = S.deploy_flags(names, src)
            check(flags == want, "deploy route for %s: %s" % (names, flags))
            argv = [a for fv in flags for a in fv]
            r = subprocess.run([sys.executable, "-c", probe] + argv, capture_output=True, text=True, timeout=120,
                               cwd=SRC_TREE)
            check("PARSE_OK" in r.stderr and r.returncode == 1,
                  "deploy_custom_mods.py accepts %s: rc %s %s" % (" ".join(argv), r.returncode, r.stderr[-300:]))

        # keyed on the id check's own refusal: a bare rc != 0 also passed with the check deleted, since
        # cmd_result of a missing path answers "no result" with exit 1
        # status --job reads p("jobs", <id>) too; with only --attempt checked (wave 72 mutation) a path passed here
        for argv in (["result", "--attempt"], ["ack", "--attempt"], ["stop", "--attempt"], ["status", "--job"]):
            rc, o = w(argv + ["../../etc"])
            check(rc == 2 and "not a job or attempt id" in o.get("raw", ""),
                  "a path as an id is refused by %s: rc %s %s" % (" ".join(argv), rc, str(o)[-200:]))
        # start takes its id from the job JSON on stdin, not argv: cmd_start writes p("jobs", id) and attempts/<id>.aN,
        # so validate_job's id regex is the only thing between a path id and those writes (wave 75: with it stubbed
        # out every row above still passed)
        jbad = dict(job(), id="../../etc")
        rc, o = w(["start"], jbad)
        check(rc != 0 and "bad id" in o.get("raw", "") and not os.path.exists(os.path.join(tmp, "etc"))
              and not os.path.exists(os.path.join(home, "etc")),
              "a path as the job id on stdin is refused before anything is written: rc %s %s" % (rc, str(o)[-200:]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
