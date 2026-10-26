#!/usr/bin/env python3
"""selftest_steve_worker.py - the durable SteveDesktop worker (worker.py) on a throwaway TESTQ_HOME with mock phases.

No game, no ssh, no pull: the deploy/load/down/run commands are replaced by a small mock, the driver lock is a temp
file, and the attempt detaches as a plain new session (TESTQ_NO_SYSTEMD=1). Proves DONE with attested deploy hashes
and NOT_RUN accounting, duplicate delivery, --retry, hang -> one restart -> DONE, hang twice -> INVALID/HANG, no sheet
-> INVALID/HARNESS, guard held -> REFUSED, busy -> 75, stop -> INTERRUPTED, a dead attempt finalized, and
SOURCE_SHA_MISSING.
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
sys.path.insert(0, os.path.join(RUNNER, "src", "RimMandrake", "Utils", "testq"))
import schema as S  # noqa: E402

FAILS = []
MOCK = r'''
import json, os, sys, time
mode = os.environ.get("MOCK_MODE", "pass")
sheet_dir = os.environ["TESTQ_SHEET_DIR"]
mark = os.path.join(os.environ["TESTQ_HOME"], "mock_hung_once")
if mode == "hang" or (mode == "hang-once" and not os.path.exists(mark)):
    open(mark, "w").close()
    time.sleep(60)
if mode == "crash":
    print("Traceback: boom"); sys.exit(3)
name = "Mock_%d" % int(time.time() * 1000)
summary = {"chains": [{"name": "c1", "components": [{"name": "r1", "verdict": "PASS", "detail": "ok"},
                                                    {"name": "r2", "verdict": "FAIL", "detail": "bad"}]}]}
json.dump({"mod": "Mock", "summary": summary}, open(os.path.join(sheet_dir, name + ".json"), "w"))
open(os.path.join(sheet_dir, name + ".html"), "w").write("<html/>")
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
                   TESTQ_CMD_RUN="%s %s run" % (sys.executable, mock), RIMFLOW_DRIVER_LOCK=lock,
                   RM_HOST="stevedesktop", RM_GAME_USERDATA=tmp, RIMFLOW_LEDGER=os.path.join(tmp, "ev.jsonl"))
        head = subprocess.run(["git", "-C", RUNNER, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()

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
        check(verdicts == {"r1": "PASS", "r2": "FAIL", "r9": "NOT_RUN"}, "requested row absent -> NOT_RUN: %s" % verdicts)
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

        # 4. no sheet
        rc, o = w(["start"], job(), MOCK_MODE="crash")
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "INVALID" and res.get("cause") == "HARNESS", "no sheet -> INVALID/HARNESS")

        # 5. the guard is held by someone else
        sys.path.insert(0, os.path.join(RUNNER, "src", "RimMandrake", "rimflow"))
        import driver_lock as D
        other = {"pid": 4242, "start": 7.0, "boot_id": None, "platform": "wsl", "host": "archmagi-elsewhere"}
        D.acquire(lock, "BENCH", "interactive session", other)
        rc, o = w(["start"], job())
        res = wait_result(o.get("attempt", "x"))
        check(res.get("outcome") == "REFUSED" and res.get("cause") == "GUARD_HELD", "guard held -> REFUSED/GUARD_HELD: "
              + str(res.get("note")))
        D.release(lock, "BENCH", other)

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
        rc, o = w(["result", "--attempt", "../../etc"])
        check(rc != 0, "a path as an attempt id is refused")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
