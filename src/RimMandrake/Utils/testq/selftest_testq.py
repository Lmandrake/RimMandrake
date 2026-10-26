#!/usr/bin/env python3
"""selftest_testq.py - the queue and dispatch tick (testq.py) against the REAL worker (worker.py) behind a fake ssh.

The fake ssh runs the remote command locally (or exits 255 while a 'down' flag file exists); the worker runs on a
temp TESTQ_HOME with mock phases, as in infrastructure/stevedesktop/selftest_steve_worker.py. Proves: submit and
duplicate submit, priority order, owner_gate / not_before / archmagi held back, one job at a time across ticks,
result fetched and acked, ssh down -> no sends and a timed probe, cancel, supersede, a dead attempt finalized then
retried once (attempt id asked first), orphan results kept, show within 20 lines, a concurrent tick refused.
"""
import fcntl
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TESTQ = os.path.join(HERE, "testq.py")
sys.path.insert(0, HERE)
import schema as S  # noqa: E402

FAILS = []
FAKE_SSH = r'''
import os, subprocess, sys
if os.path.exists(os.environ["FAKE_SSH_DOWN"]):
    sys.stderr.write("ssh: connect to host: No route to host\n"); sys.exit(255)
with open(os.environ["FAKE_SSH_LOG"], "a") as f:
    f.write(sys.argv[-1] + "\n")
sys.exit(subprocess.run(["bash", "-c", sys.argv[-1]]).returncode)
'''
MOCK = r'''
import json, os, sys, time
name = "Mock_%d" % int(time.time() * 1000000)
summary = {"chains": [{"name": "c1", "components": [{"name": "r1", "verdict": "PASS", "detail": "ok"},
                                                    {"name": "r2", "verdict": "FAIL", "detail": "bad"}]}]}
json.dump({"mod": "Mock", "summary": summary}, open(os.path.join(os.environ["TESTQ_SHEET_DIR"], name + ".json"), "w"))
print("sheet Transient/modcheck/%s.html" % name)
'''


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    tmp = tempfile.mkdtemp(prefix="rf_testq_")
    try:
        queue, home, sheets = (os.path.join(tmp, d) for d in ("queue", "home", "sheets"))
        for d in (queue, home, sheets):
            os.makedirs(d)
        open(os.path.join(tmp, "fake_ssh.py"), "w").write(FAKE_SSH)
        open(os.path.join(tmp, "mock.py"), "w").write(MOCK)
        down, sshlog = os.path.join(tmp, "down"), os.path.join(tmp, "ssh.log")
        open(sshlog, "w").close()
        env = {k: v for k, v in os.environ.items() if k not in ("RM_HOST_GUARD_GEN", "RIMFLOW_SEAT", "TESTQ_UNIT")}
        env.update(TESTQ_QUEUE=queue, TESTQ_SSH="%s %s" % (sys.executable, os.path.join(tmp, "fake_ssh.py")),
                   TESTQ_REMOTE_RUNNER=REPO, FAKE_SSH_DOWN=down, FAKE_SSH_LOG=sshlog,
                   TESTQ_HOME=home, TESTQ_SHEET_DIR=sheets, TESTQ_MODS_DIR=os.path.join(tmp, "mods"),
                   TESTQ_SKIP_PULL="1", TESTQ_NO_SYSTEMD="1", TESTQ_CMD_DEPLOY="true", TESTQ_CMD_LOAD="true",
                   TESTQ_CMD_DOWN="true", TESTQ_CMD_RUN="%s %s" % (sys.executable, os.path.join(tmp, "mock.py")),
                   RIMFLOW_DRIVER_LOCK=os.path.join(tmp, "DRIVER_LOCK.json"), RM_HOST="stevedesktop",
                   RM_GAME_USERDATA=tmp)
        sha = subprocess.run(["git", "-C", REPO, "merge-base", "HEAD", "origin/main"], capture_output=True,
                             text=True).stdout.strip()

        def tq(*args, **extra):
            r = subprocess.run([sys.executable, TESTQ] + list(args), env=dict(env, **extra), capture_output=True,
                               text=True, timeout=120)
            return r.returncode, r.stdout

        def submit(*args):
            rc, o = tq("submit", "Mock", "--purpose", "commission", "--by", "BENCH", "--sha", sha, *args)
            try:
                return json.loads(o.strip().splitlines()[-1])
            except (ValueError, IndexError):
                return {"raw": o}

        def state(jid):
            for st in ("pending", "running", "done", "cancelled"):
                if os.path.exists(os.path.join(queue, st, jid + ".json")):
                    return st

        def wait_worker(aid, limit=40):
            t = time.time()
            while time.time() - t < limit:
                if os.path.exists(os.path.join(home, "attempts", aid, "result.json")):
                    return True
                time.sleep(0.3)
            return False

        def running_attempt(jid):
            return json.load(open(os.path.join(queue, "running", jid + ".json")))["attempt"]

        a = submit("--rows", "r1,r2")["job"]
        b = submit("--rows", "r1", "--priority", "90")["job"]
        g = submit("--rows", "r2", "--owner-gate", "owner must pick the list")["job"]
        nb = submit("--rows", "r2", "--not-before", "2099-01-01T00:00:00Z")["job"]
        arch = submit("--rows", "r2", "--lane", "archmagi")["job"]
        dup = submit("--rows", "r1,r2")
        check(dup.get("job") == a and dup.get("duplicate"), "an identical submit returns the pending job: %s" % dup)
        rc, o = tq("submit", "Mock", "--purpose", "fix", "--by", "BENCH", "--sha", "0123456789abcdef", "--rows", "r1")
        check(rc == 2 and "origin/main" in o, "an unpublished source_sha is refused at submit")
        rc, o = tq("submit", "Mock", "--purpose", "fix", "--by", "BENCH", "--sha", sha)
        check(rc == 2 and "selects nothing" in o, "an empty selection is refused at submit")

        tq("tick")
        check(state(b) == "running" and state(a) == "pending", "tick admits the highest priority job first")
        ab = running_attempt(b)
        tq("tick")
        check(state(a) == "pending", "a second tick while B runs admits nothing")
        check(wait_worker(ab), "the worker finished B")
        tq("tick")
        done_b = json.load(open(os.path.join(queue, "done", b + ".json")))
        check(done_b["result"]["outcome"] == "DONE" and done_b["result"]["counts"] == {"PASS": 1, "FAIL": 1},
              "B's result is fetched into done/: %s" % done_b["result"]["counts"])
        check(not os.path.exists(os.path.join(home, "outbox", ab + ".json")), "B's result is acked off the outbox")
        check(state(a) == "running", "the same tick admits A")
        check(all(state(j) == "pending" for j in (g, nb, arch)), "owner_gate, not_before and archmagi stay pending")

        # ssh drops while A runs
        aa = running_attempt(a)
        open(down, "w").close()
        tq("tick")
        ss = json.load(open(os.path.join(queue, "ssh_state.json")))
        check(ss.get("down_since") and "No route" in ss.get("last_error", ""), "ssh down is recorded")
        os.remove(down)
        n = len(open(sshlog).read().splitlines())
        tq("tick")
        check(len(open(sshlog).read().splitlines()) == n, "no ssh at all until the probe is due")
        check(wait_worker(aa), "A finished on the worker while ssh was down")
        tq("tick", TESTQ_PROBE_S="0")
        check(state(a) == "done" and not json.load(open(os.path.join(queue, "ssh_state.json"))).get("down_since"),
              "the due probe finds ssh back and collects A")

        # cancel and supersede
        tq("cancel", nb, "--reason", "not needed")
        check(state(nb) == "cancelled", "cancel moves a pending job to cancelled/")
        s = submit("--rows", "r1", "--supersedes", g, "--priority", "10")["job"]
        check(state(g) == "cancelled" and state(s) == "pending", "a superseding submit cancels the pending original")

        # a dead attempt: the worker finalizes it, then the dispatcher retries once
        tq("tick")
        check(state(s) == "running", "the superseding job is admitted")
        a1 = running_attempt(s)
        wait_worker(a1)
        os.remove(os.path.join(home, "attempts", a1, "result.json"))
        os.remove(os.path.join(home, "outbox", a1 + ".json"))
        st_path = os.path.join(home, "attempts", a1, "state.json")
        os.utime(st_path, (time.time() - 600, time.time() - 600))
        tq("tick")
        dead = json.load(open(os.path.join(home, "attempts", a1, "result.json")))
        check(dead["cause"] == "CRASH" and state(s) == "running", "a dead attempt is finalized INTERRUPTED/CRASH")
        tq("tick")
        a2 = running_attempt(s)
        check(a2 == s + ".a2", "one automatic retry after the attempt id was read: %s" % a2)
        wait_worker(a2)
        tq("tick")
        tq("tick")
        rec = json.load(open(os.path.join(queue, "done", s + ".json")))
        check(rec["attempts"] == [a1, a2] and rec["result"]["outcome"] == "DONE", "the retry's result closes the job")

        # an orphan result in the outbox
        orphan = S.make_job("Mock", {"rows": ["r1"]}, "commission", "BENCH", sha)
        r = subprocess.run([sys.executable, os.path.join(REPO, "infrastructure", "stevedesktop", "worker.py"), "start"],
                           input=json.dumps(orphan), env=env, capture_output=True, text=True, timeout=60)
        oa = json.loads(r.stdout.strip().splitlines()[-1])["attempt"]
        wait_worker(oa)
        tq("tick")
        check(os.path.exists(os.path.join(queue, "orphans", oa + ".json")) and
              not os.path.exists(os.path.join(home, "outbox", oa + ".json")), "an unknown job's result is kept and acked")

        rc, o = tq("show", b)
        check(rc == 0 and len(o.splitlines()) <= 20 and "DONE" in o, "show fits in 20 lines")
        rc, o = tq("list")
        check(len(o.splitlines()) == 6, "list shows every job once:\n%s" % o)
        with open(os.path.join(queue, "tick.lock"), "w") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            rc, o = tq("tick")
        check("already running" in o, "a tick while another runs exits at once")
        rc, o = tq("show", "../../x")
        check(rc == 2, "a path as a job id is refused")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
