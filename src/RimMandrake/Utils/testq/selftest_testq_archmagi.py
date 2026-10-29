#!/usr/bin/env python3
"""selftest_testq_archmagi.py - the testq Archmagi backfill (TESTQ_ARCHMAGI_LANE_BUILD_BACKFILL), offline.

Everything runs on temp files: the queue, the worker home, the driver lock (RIMFLOW_DRIVER_LOCK), the shared bridge
file (RIMFLOW_SHARED_BRIDGE), the BRIDGE mirror (beside a throwaway RIMFLOW_LEDGER), the bridge call log
(TESTQ_BRIDGE_LOG) and the game pid (TESTQ_ARCHMAGI_PID). SteveDesktop is a fake ssh that is down unless a test
brings it up. Proves:
  gate: off unless TESTQ_ARCHMAGI=1; a stop file, a pause, a back-off, another host, no runner clone, a shared
        bridge holder, a HELD mirror, a held driver lock, a bridge used < 600 s ago, and a missing call log each
        close it; all clear opens it.
  candidates: lane archmagi only; lane any only while SteveDesktop is down or busy; never lane stevedesktop;
        full-list profile only by default; a job Archmagi refused to deploy is skipped.
  tick: disabled -> nothing runs and nothing is logged about archmagi; enabled and open -> the real worker runs the
        job locally and its result lands in done/ with host archmagi (result host archmagi); the driver lock is held
        while it runs; drift -> REFUSED/DEPLOY, the job back in pending and skipped; no game -> REFUSED/LOAD, back to
        pending and a back-off; a bridge holder appearing mid-run stops the attempt and the job goes back; the Steve
        filler does not count an archmagi job as Steve's work.
  phases: archmagi_phases.py load / down / status / deploy refuse rather than launch, stop or deploy.
  worker: a REFUSED line from a deploy / load phase ends the attempt REFUSED/DEPLOY / REFUSED/LOAD.
  ingest: an archmagi result verifies under config archmagi-<profile>.
"""
import glob
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
PHASES = os.path.join(HERE, "archmagi_phases.py")
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "bridgetools"))
import companion_identity as CI  # noqa: E402

FAILS = []
FAKE_SSH = r'''
import os, subprocess, sys
if os.path.exists(os.environ["FAKE_SSH_DOWN"]):
    sys.stderr.write("ssh: connect to host: No route to host\n"); sys.exit(255)
env = dict(os.environ, RM_HOST="stevedesktop", RIMFLOW_DRIVER_LOCK=os.environ["STEVE_DRIVER_LOCK"])  # another machine
sys.exit(subprocess.run(["bash", "-c", sys.argv[-1]], env=env).returncode)
'''
MOCK = r'''
import json, os, sys, time
time.sleep(float(os.environ.get("MOCK_SLEEP") or 0))
name = "Mock_%d" % int(time.time() * 1000000)
summary = {"chains": [{"name": "c1", "components": [{"name": "r1", "verdict": "PASS", "detail": "ok"}]}]}
json.dump({"mod": "Mock", "summary": summary}, open(os.path.join(os.environ["TESTQ_SHEET_DIR"], name + ".json"), "w"))
print("sheet Transient/modcheck/%s.html" % name)
'''


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


class Rig:
    def __init__(self, tmp):
        self.tmp = tmp
        p = self.p
        for d in ("queue", "steve_home", "arch_home", "sheets", "ledger", "mods"):
            os.makedirs(p(d))
        open(p("fake_ssh.py"), "w").write(FAKE_SSH)
        open(p("mock.py"), "w").write(MOCK)
        open(p("down"), "w").close()                     # SteveDesktop down unless a test removes it
        open(p("ledger", "events.jsonl"), "w").close()
        self.log_old()
        self.env = {k: v for k, v in os.environ.items()
                    if k not in ("RM_HOST_GUARD_GEN", "RIMFLOW_SEAT", "TESTQ_UNIT") and not k.startswith("TESTQ_")}
        mock = "%s %s" % (sys.executable, p("mock.py"))
        self.env.update(
            TESTQ_QUEUE=p("queue"), TESTQ_SSH="%s %s" % (sys.executable, p("fake_ssh.py")), TESTQ_REMOTE_RUNNER=REPO,
            FAKE_SSH_DOWN=p("down"), STEVE_DRIVER_LOCK=p("STEVE_DRIVER_LOCK.json"), TESTQ_HOME=p("steve_home"), TESTQ_SHEET_DIR=p("sheets"),
            TESTQ_MODS_DIR=p("mods"), TESTQ_SKIP_PULL="1", TESTQ_NO_SYSTEMD="1",
            TESTQ_CMD_DEPLOY="true", TESTQ_CMD_LOAD="true", TESTQ_CMD_DOWN="true", TESTQ_CMD_RUN=mock,
            TESTQ_CMD_STATUS="echo 'running pid=4242'",
            RIMFLOW_DRIVER_LOCK=p("DRIVER_LOCK.json"), RIMFLOW_SHARED_BRIDGE=p("BRIDGE_SHARED.json"),
            RIMFLOW_LEDGER=p("ledger", "events.jsonl"), RM_HOST="archmagi", RM_GAME_USERDATA=self.tmp,
            TESTQ_ARCHMAGI="1", TESTQ_ARCHMAGI_RUNNER=REPO, TESTQ_ARCHMAGI_HOME=p("arch_home"),
            TESTQ_ARCHMAGI_MODS_DIR=p("mods"), TESTQ_ARCHMAGI_CMD_RUN=mock, TESTQ_ARCHMAGI_CMD_DEPLOY="true",
            TESTQ_ARCHMAGI_PID="4242", TESTQ_BRIDGE_LOG=p("bridge_calls.jsonl"))
        # both lanes' deploy phase refuses a companion not built from the job's sources; the default place is the
        # Mods folder's sibling BridgeTools/JawaBench, so one fixture serves both workers (they share p("mods"))
        sha = subprocess.run(["git", "-C", REPO, "merge-base", "HEAD", "origin/main"], capture_output=True,
                             text=True).stdout.strip()
        CI.write_fixture(p("BridgeTools", "JawaBench", CI.DLL_NAME), CI.srchash_at(REPO, sha))

    def p(self, *parts):
        return os.path.join(self.tmp, *parts)

    def log_old(self, age=3600):
        f = self.p("bridge_calls.jsonl")
        open(f, "a").close()
        os.utime(f, (time.time() - age, time.time() - age))

    def call(self, expr, **extra):
        """Evaluate EXPR inside testq.py under this rig's env (a subprocess, so the module reads it fresh)."""
        code = "import sys, json; sys.path.insert(0, %r); import testq; print(json.dumps(%s))" % (HERE, expr)
        r = subprocess.run([sys.executable, "-c", code], env=self.envx(extra), capture_output=True, text=True,
                           timeout=60, cwd=HERE)
        try:
            return json.loads(r.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return {"raw": r.stdout + r.stderr}

    def envx(self, extra):
        e = dict(self.env)
        for k, v in extra.items():
            if v is None:
                e.pop(k, None)
            else:
                e[k] = v
        return e

    def tq(self, *args, **extra):
        r = subprocess.run([sys.executable, TESTQ] + list(args), env=self.envx(extra), capture_output=True, text=True,
                           timeout=180)
        return r.returncode, r.stdout + r.stderr

    def job(self, _name, lane="archmagi", profile="full-list", priority=50):
        """Submit a real job (testq submit validates it) -> its id. _NAME only labels the test's intent."""
        if not hasattr(self, "sha"):
            self.sha = subprocess.run(["git", "-C", REPO, "merge-base", "HEAD", "origin/main"], capture_output=True,
                                      text=True).stdout.strip()
        rc, o = self.tq("submit", "Mock", "--purpose", "commission", "--by", "BENCH", "--sha", self.sha, "--rows",
                        "r1", "--lane", lane, "--profile", profile, "--priority", str(priority))
        try:
            return json.loads(o.strip().splitlines()[-1])["job"]
        except (ValueError, IndexError, KeyError):
            raise RuntimeError("submit failed: %s" % o[-300:])

    def state(self, jid):
        for st in ("pending", "running", "done", "cancelled"):
            if os.path.exists(self.p("queue", st, jid + ".json")):
                return st

    def rec(self, jid):
        return json.load(open(self.p("queue", self.state(jid), jid + ".json")))

    def wait_result(self, home, aid, limit=60):
        t = time.time()
        while time.time() - t < limit:
            if os.path.exists(self.p(home, "attempts", aid, "result.json")):
                return json.load(open(self.p(home, "attempts", aid, "result.json")))
            time.sleep(0.3)
        return None

    def qlog(self):
        try:
            return open(self.p("queue", "tick.log")).read()
        except OSError:
            return ""

    def clear(self):
        for st in ("pending", "running", "done", "cancelled"):
            for f in glob.glob(self.p("queue", st, "*.json")):
                os.remove(f)
        for f in ("archmagi_state.json", "archmagi_paused.json", "archmagi.stop"):
            if os.path.exists(self.p("queue", f)):
                os.remove(self.p("queue", f))


def t_gate(r):
    r.tq("list")                                     # creates the queue dirs
    g = r.call("testq.archmagi_gate()")
    check(g[0] is True, "all gates clear -> open: %s" % g)
    g = r.call("testq.archmagi_gate()", TESTQ_ARCHMAGI=None)
    check(g[0] is False and "off" in g[1], "TESTQ_ARCHMAGI unset -> closed: %s" % g[1])
    g = r.call("testq.archmagi_gate()", RM_HOST="stevedesktop")
    check(g[0] is False and "not archmagi" in g[1], "another machine -> closed: %s" % g[1])
    g = r.call("testq.archmagi_gate()", TESTQ_ARCHMAGI_RUNNER=r.p("nowhere"))
    check(g[0] is False and "no runner clone" in g[1], "no runner clone -> closed: %s" % g[1])
    g = r.call("testq.archmagi_gate()", TESTQ_SKIP_PULL=None)
    check(g[0] is False and "own" in g[1], "an agent's clone as the runner (pulls live) -> closed: %s" % g[1])
    open(r.p("queue", "archmagi.stop"), "w").close()
    g = r.call("testq.archmagi_gate()")
    check(g[0] is False and "stopped" in g[1], "archmagi.stop -> closed: %s" % g[1])
    os.remove(r.p("queue", "archmagi.stop"))
    json.dump({"since": "x", "job": "J", "outcome": "INVALID", "cause": "CANARY"},
              open(r.p("queue", "archmagi_paused.json"), "w"))
    g = r.call("testq.archmagi_gate()")
    check(g[0] is False and "paused" in g[1], "archmagi pause -> closed: %s" % g[1])
    rc, o = r.tq("resume", "--lane", "archmagi", "--reason", "test")
    check(not os.path.exists(r.p("queue", "archmagi_paused.json")), "resume --lane archmagi lifts it")
    json.dump({"backoff_until": time.time() + 900, "backoff_why": "no game"}, open(r.p("queue", "archmagi_state.json"),
                                                                                  "w"))
    g = r.call("testq.archmagi_gate()")
    check(g[0] is False and "backing off" in g[1], "back-off -> closed: %s" % g[1])
    os.remove(r.p("queue", "archmagi_state.json"))
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 7200))
    json.dump({"holder": "FOUNDRY", "since": now, "touched": now, "purpose": "proof"},
              open(r.p("BRIDGE_SHARED.json"), "w"))
    g = r.call("testq.archmagi_gate()")
    check(g[0] is False and "FOUNDRY" in g[1], "a shared bridge holder (even a 2 h old one) -> closed: %s" % g[1])
    os.remove(r.p("BRIDGE_SHARED.json"))
    open(r.p("ledger", "BRIDGE"), "w").write("HELD BENCH since x\n")
    g = r.call("testq.archmagi_gate()")
    check(g[0] is False and "BENCH" in g[1] and "mirror" in g[1], "a HELD BRIDGE mirror -> closed: %s" % g[1])
    open(r.p("ledger", "BRIDGE"), "w").write("FREE\n")
    g = r.call("testq.archmagi_gate()")
    check(g[0] is True, "a FREE BRIDGE mirror -> open: %s" % g)
    hold = subprocess.Popen([sys.executable, os.path.join(REPO, "src", "RimMandrake", "rimflow", "host_guard.py"),
                             "run", "--seat", "BENCH", "--for", "test", "--", "sleep", "20"],
                            env=r.envx({}), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        t = time.time()
        while time.time() - t < 15 and r.call("testq._rimflow()[1].status()").get("state") != "HELD":
            time.sleep(0.3)
        g = r.call("testq.archmagi_gate()")
        check(g[0] is False and "driver lock HELD" in g[1], "a held driver lock -> closed: %s" % g[1])
    finally:
        hold.terminate()
        hold.wait(timeout=30)
    g = r.call("testq.archmagi_gate()")
    check(g[0] is True or "driver lock" not in g[1], "a STALE driver lock (its holder died) does not close it: %s" % g)
    r.log_old(age=60)
    g = r.call("testq.archmagi_gate()")
    check(g[0] is False and "silence" in g[1], "the bridge used 60 s ago -> closed: %s" % g[1])
    g = r.call("testq.archmagi_gate()", TESTQ_ARCHMAGI_SILENT_S="30")
    check(g[0] is True, "TESTQ_ARCHMAGI_SILENT_S=30 accepts 60 s of silence: %s" % g)
    os.remove(r.p("bridge_calls.jsonl"))
    g = r.call("testq.archmagi_gate()")
    check(g[0] is False and "cannot show" in g[1], "no bridge call log -> closed (silence unproven): %s" % g[1])
    r.log_old()


def t_candidates(r):
    r.clear()
    a = r.job("JA", lane="archmagi")
    y = r.job("JY", lane="any", priority=80)
    s = r.job("JS", lane="stevedesktop", priority=90)
    t = r.job("JT", lane="archmagi", profile="targeted", priority=95)
    ids = lambda c: [j["id"] for j in c]       # noqa: E731
    c = ids(r.call("testq.archmagi_candidates(True, False)"))
    check(c == [a], "Steve up and idle: only lane archmagi, full-list: %s" % c)
    c = ids(r.call("testq.archmagi_candidates(False, False)"))
    check(c == [y, a], "Steve down: lane any re-routed too, by priority: %s" % c)
    c = ids(r.call("testq.archmagi_candidates(True, True)"))
    check(c == [y, a], "Steve busy: lane any re-routed too: %s" % c)
    check(s not in c and t not in c, "never lane stevedesktop; never targeted by default")
    c = ids(r.call("testq.archmagi_candidates(True, False)", TESTQ_ARCHMAGI_PROFILES="targeted,full-list"))
    check(c == [t, a], "TESTQ_ARCHMAGI_PROFILES widens the profiles: %s" % c)
    json.dump({"skip": {a: {"why": "drift"}}}, open(r.p("queue", "archmagi_state.json"), "w"))
    c = ids(r.call("testq.archmagi_candidates(True, False)"))
    check(c == [], "a job Archmagi refused to deploy is skipped: %s" % c)


def admitted(r, jid):
    rec = r.rec(jid)
    return rec.get("attempt"), rec.get("host")


def t_tick(r):
    r.clear()
    j = r.job("J1")
    mark = len(r.qlog())
    r.tq("tick", TESTQ_ARCHMAGI=None)
    check(r.state(j) == "pending", "disabled: an archmagi job stays pending")
    check("archmagi" not in r.qlog()[mark:], "disabled: nothing is logged about archmagi: %s" % r.qlog()[mark:])
    rc, o = r.tq("tick")
    aid, host = admitted(r, j)
    check(r.state(j) == "running" and host == "archmagi", "enabled and open: admitted on archmagi (%s) %s" % (aid, o[-200:]))
    res = r.wait_result("arch_home", aid)
    check(res and res["outcome"] == "DONE" and res.get("host") == "archmagi",
          "the local worker ran it: %s" % str(res and (res["outcome"], res["cause"], res.get("host"), res.get("note"))))
    r.tq("tick")
    check(r.state(j) == "done" and r.rec(j).get("host") == "archmagi", "the result lands in done/ marked archmagi")

    # the driver lock is held for the attempt's life; the filler does not count it as Steve's
    r.clear()
    j = r.job("J2")
    r.tq("tick", MOCK_SLEEP="6")
    aid, _h = admitted(r, j)
    t = time.time()
    lock = {}
    while time.time() - t < 10 and lock.get("state") != "HELD":     # the attempt starts detached
        lock = r.call("testq._rimflow()[1].status()")
        time.sleep(0.3)
    check(lock.get("state") == "HELD" and lock.get("seat") == "RUNNER", "the attempt holds the driver lock: %s" %
          {k: lock.get(k) for k in ("state", "seat")})
    g = r.call("testq.archmagi_gate()")
    check(g[0] is False, "while it runs the gate is closed (driver lock): %s" % g[1])
    busy = r.call("len(testq.steve_running())")
    check(busy == 0, "an archmagi job is not Steve's running work (the filler still fills)")
    r.wait_result("arch_home", aid)
    r.tq("tick", TESTQ_ARCHMAGI=None)
    check(r.state(j) == "done", "J2 finished (switched off mid-run: what it started is still reconciled)")

    # drift: REFUSED/DEPLOY -> back to pending, skipped by archmagi from then on
    r.clear()
    j = r.job("J3")
    r.tq("tick", TESTQ_ARCHMAGI_CMD_DEPLOY="echo 'REFUSED: drift found for Mock'; exit 3; :")
    aid, _h = admitted(r, j)
    res = r.wait_result("arch_home", aid)
    check(res and (res["outcome"], res["cause"]) == ("REFUSED", "DEPLOY"), "drift -> REFUSED/DEPLOY: %s" %
          str(res and (res["outcome"], res["cause"], res.get("note"))))
    r.tq("tick")
    st = json.load(open(r.p("queue", "archmagi_state.json")))
    check(r.state(j) == "pending" and j in (st.get("skip") or {}), "the job is back in pending and skipped on archmagi")
    r.tq("tick")
    check(r.state(j) == "pending", "and archmagi does not take it again")

    # no game: REFUSED/LOAD -> back to pending, lane backs off
    r.clear()
    j = r.job("J4")
    r.tq("tick", TESTQ_ARCHMAGI_PID="")
    aid, _h = admitted(r, j)
    res = r.wait_result("arch_home", aid)
    check(res and (res["outcome"], res["cause"]) == ("REFUSED", "LOAD"), "no game running -> REFUSED/LOAD: %s" %
          str(res and (res["outcome"], res["cause"], res.get("note"))))
    r.tq("tick", TESTQ_ARCHMAGI_PID="")
    st = json.load(open(r.p("queue", "archmagi_state.json")))
    check(r.state(j) == "pending" and st.get("backoff_until", 0) > time.time() + 1000,
          "back to pending and the lane backs off ~30 min")
    g = r.call("testq.archmagi_gate()")
    check(g[0] is False and "backing off" in g[1], "the gate reports the back-off")

    # a window takes the bridge mid-run: the attempt is stopped and the job goes back
    r.clear()
    j = r.job("J5")
    r.tq("tick", MOCK_SLEEP="30")
    aid, _h = admitted(r, j)
    time.sleep(2)
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump({"holder": "FOUNDRY", "since": now, "touched": now, "purpose": "forced take"},
              open(r.p("BRIDGE_SHARED.json"), "w"))
    r.tq("tick")
    check(r.rec(j).get("yield"), "a bridge holder mid-run marks the job yielded")
    res = r.wait_result("arch_home", aid, limit=40)
    check(res and res["outcome"] == "INTERRUPTED", "the attempt was stopped: %s" % (res and res["outcome"]))
    r.tq("tick")
    check(r.state(j) == "pending", "the yielded job is back in pending")
    check(r.state(j) == "pending" and not glob.glob(r.p("queue", "running", "*.json")),
          "and nothing is admitted while the window holds the bridge")
    os.remove(r.p("BRIDGE_SHARED.json"))


def t_steve_and_any(r):
    """SteveDesktop up and idle takes the lane-any job; archmagi only takes its own."""
    r.clear()
    os.remove(r.p("down"))
    if os.path.exists(r.p("queue", "ssh_state.json")):
        os.remove(r.p("queue", "ssh_state.json"))      # no 300 s wait for the next probe
    try:
        y = r.job("JY2", lane="any", priority=80)
        a = r.job("JA2", lane="archmagi", priority=10)
        r.tq("tick")
        check(r.state(y) == "running" and r.rec(y).get("host") in (None, "stevedesktop"),
              "Steve up: the lane-any job goes to SteveDesktop")
        check(r.state(a) == "running" and r.rec(a).get("host") == "archmagi",
              "the archmagi job runs on archmagi at the same time")
        for jid, home in ((y, "steve_home"), (a, "arch_home")):
            r.wait_result(home, r.rec(jid)["attempt"])
        r.tq("tick")
        check(r.state(y) == "done" and r.state(a) == "done", "both finish, each from its own worker")
    finally:
        open(r.p("down"), "w").close()


def t_keep_modlist(r):
    """TESTQ_ARCHMAGI_FIX_OWNER_MODLIST_SWAP: the lane never lets modcheck swap/compose/restore ModsConfig."""
    code = ("import sys, json, subprocess; sys.path.insert(0, %r); import testq\n"
            "seen = {}\n"
            "class R: returncode = 0; stdout = '{}'; stderr = ''\n"
            "def fake(cmd, **kw): seen.update(kw['env']); return R()\n"
            "testq.subprocess.run = fake\n"
            "testq.archmagi_worker(['status'])\n"
            "print(json.dumps([seen.get('MODCHECK_KEEP_MODLIST'), seen.get('WSLENV')]))" % HERE)
    p = subprocess.run([sys.executable, "-c", code], env=r.envx({}), capture_output=True, text=True, timeout=60, cwd=HERE)
    try:
        keep, wsl = json.loads(p.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        keep, wsl = None, p.stdout + p.stderr
    check(keep == "1" and "MODCHECK_KEEP_MODLIST" in (wsl or ""), "archmagi worker env keeps the modlist and exports it via WSLENV: %s %s" % (keep, wsl))
    code = ("import sys, os; sys.path.insert(0, %r); import runner\n"
            "calls = []\n"
            "runner.swap_to_test_list = lambda *a: calls.append('swap')\n"
            "runner.restore_full = lambda: calls.append('restore')\n"
            "runner.compose_test_list = lambda *a: calls.append('compose')\n"
            "runner.run([])\n"
            "os.environ['MODCHECK_KEEP_MODLIST'] = '1'\n"
            "runner.run([])\n"
            "print(calls)" % os.path.join(REPO, "src", "RimMandrake", "Utils", "modcheck"))
    p = subprocess.run([sys.executable, "-c", code], env=r.envx({}), capture_output=True, text=True, timeout=60,
                       cwd=os.path.join(REPO, "src", "RimMandrake", "Utils", "modcheck"))
    check(p.stdout.strip().endswith("['swap', 'compose', 'restore']"),
          "runner.run swaps+restores without the flag and does neither with it: %s" % (p.stdout + p.stderr)[-300:])


def t_phases(r):
    def ph(*args, **env):
        e = dict(os.environ, **env)
        p = subprocess.run([sys.executable, PHASES] + list(args), env=e, capture_output=True, text=True, timeout=120,
                           cwd=REPO)
        return p.returncode, p.stdout
    rc, o = ph("load", TESTQ_ARCHMAGI_PID="777")
    check(rc == 0 and "already running (pid 777)" in o, "phases load: a running game is used, never relaunched")
    rc, o = ph("load", TESTQ_ARCHMAGI_PID="")
    check(rc == 3 and o.startswith("REFUSED:"), "phases load: no game -> REFUSED, never launches")
    rc, o = ph("down", TESTQ_ARCHMAGI_PID="777")
    check(rc == 3 and o.startswith("REFUSED:"), "phases down: never stops the owner's game")
    rc, o = ph("status", TESTQ_ARCHMAGI_PID="777")
    check(rc == 0 and "running pid=777" in o, "phases status: running pid")
    rc, o = ph("status", TESTQ_ARCHMAGI_PID="")
    check(rc == 3 and o.startswith("stopped"), "phases status: stopped")
    rc, o = ph("deploy", "RM_NoSuchMod_Selftest")
    check(rc == 3 and o.startswith("REFUSED:"), "phases deploy: a plan that is not clean -> REFUSED, never --apply")


def t_ingest_label():
    sys.path.insert(0, HERE)
    import ingest
    calls = []
    real = ingest.rimflow
    ingest.rimflow = lambda *a: (calls.append(a), (1, "no"))[1]
    try:
        ingest.ingest_group({"profile": "full-list", "mod": "Mock", "source_sha": "0" * 40, "id": "J"},
                            {"host": "archmagi", "runner_sha": "1" * 40}, "ITEM", {"rows": []}, "J.a1")
    finally:
        ingest.rimflow = real
    cfg = calls and calls[0][calls[0].index("--config") + 1]
    check(cfg == "archmagi-full-list", "ingest verifies an archmagi result under config archmagi-<profile>: %s" % cfg)


def main():
    tmp = tempfile.mkdtemp(prefix="rf_testq_arch_")
    try:
        r = Rig(tmp)
        for t in (t_gate, t_candidates, t_tick, t_steve_and_any, t_keep_modlist, t_phases):
            try:
                t(r)
            except Exception as ex:     # noqa: BLE001 - reported; the next test still runs
                check(False, "%s raised %s: %s" % (t.__name__, type(ex).__name__, ex))
        t_ingest_label()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
