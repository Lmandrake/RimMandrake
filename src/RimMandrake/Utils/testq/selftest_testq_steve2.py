#!/usr/bin/env python3
"""selftest_testq_steve2.py - the SteveDesktop lane drives Steve1 and Steve2 at once, offline.

Page: design/specs/2026-11-23-steve-two-games-lane/boundary.md. One test per promise, each named after it.
Everything runs on temp files: the queue, two worker homes (Steve1's and Steve2's), two driver locks, and a fake ssh
that runs the remote command locally, so the REAL worker.py runs both attempts. The run phase is a mock modcheck that
sleeps MOCK_SLEEP seconds, so two attempts can be seen alive at the same time.
"""
import glob
import json
import os
import shlex
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TESTQ = os.path.join(HERE, "testq.py")
STEVE_DIR = os.path.join(REPO, "infrastructure", "stevedesktop")
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "bridgetools"))
import companion_identity as CI  # noqa: E402

FAILS = []
FAKE_SSH = r'''
import os, subprocess, sys
env = dict(os.environ, RM_HOST="stevedesktop", RIMFLOW_DRIVER_LOCK=os.environ["STEVE_DRIVER_LOCK"])
sys.exit(subprocess.run(["bash", "-c", sys.argv[-1]], env=env).returncode)
'''
MOCK = r'''
import json, os, sys, time
time.sleep(float(os.environ.get("MOCK_SLEEP") or 0))
name = "Mock_%d_%d" % (int(time.time() * 1000000), os.getpid())
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
        for d in ("queue", "home_a", "home_b", "sheets", "ledger", "mods"):
            os.makedirs(p(d))
        open(p("fake_ssh.py"), "w").write(FAKE_SSH)
        open(p("mock.py"), "w").write(MOCK)
        open(p("ledger", "events.jsonl"), "w").close()
        self.env = {k: v for k, v in os.environ.items()
                    if k not in ("RM_HOST_GUARD_GEN", "RIMFLOW_SEAT", "TESTQ_UNIT", "RM_GAME_INSTANCE")
                    and not k.startswith(("TESTQ_", "GABP_"))}
        mock = "%s %s" % (sys.executable, p("mock.py"))
        self.env.update(
            TESTQ_QUEUE=p("queue"), TESTQ_SSH="%s %s" % (sys.executable, p("fake_ssh.py")), TESTQ_REMOTE_RUNNER=REPO,
            TESTQ_REMOTE_RUNNER_B=REPO, STEVE_DRIVER_LOCK=p("LOCK_A.json"), TESTQ_HOME=p("home_a"),
            TESTQ_STEVE2_PREFIX="export TESTQ_HOME=%s TESTQ_WORKER_HOST=stevedesktop.b RIMFLOW_DRIVER_LOCK=%s && " % (
                p("home_b"), p("LOCK_B.json")),
            TESTQ_SHEET_DIR=p("sheets"), TESTQ_MODS_DIR=p("mods"), TESTQ_SKIP_PULL="1", TESTQ_NO_SYSTEMD="1",
            TESTQ_CMD_DEPLOY="true", TESTQ_CMD_LOAD="true", TESTQ_CMD_DOWN="true", TESTQ_CMD_RUN=mock,
            TESTQ_CMD_STATUS="echo 'running pid=4242'", TESTQ_CMD_PROBE="true", TESTQ_CMD_MAPS="true",
            TESTQ_CMD_RESETREPAIR="true", TESTQ_CMD_DUMP="true", TESTQ_CMD_BRIDGE="true",
            RIMFLOW_LEDGER=p("ledger", "events.jsonl"), RM_HOST="archmagi", RM_GAME_USERDATA=self.tmp,
            TESTQ_LEDGER_EVENTS=p("ledger"), MOCK_SLEEP="4")
        sha = subprocess.run(["git", "-C", REPO, "merge-base", "HEAD", "origin/main"], capture_output=True,
                             text=True).stdout.strip()
        self.sha = sha
        CI.write_fixture(p("BridgeTools", "JawaBench", CI.DLL_NAME), CI.srchash_at(REPO, sha))

    def p(self, *parts):
        return os.path.join(self.tmp, *parts)

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
                           timeout=240)
        return r.returncode, r.stdout + r.stderr

    def py(self, code, **extra):
        """Run CODE (its last printed line is JSON) in a fresh interpreter under this rig's env -> that value."""
        code = "import sys, json; sys.path.insert(0, %r); sys.path.insert(0, %r)\n%s" % (HERE, STEVE_DIR, code)
        r = subprocess.run([sys.executable, "-c", code], env=self.envx(extra), capture_output=True, text=True,
                           timeout=120, cwd=HERE)
        try:
            return json.loads(r.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return {"raw": (r.stdout + r.stderr)[-600:]}

    def job(self, mod="Mock", priority=50):
        """A distinct job each call (submit answers an identical request with the job it already has)."""
        self.n = getattr(self, "n", 0) + 1
        rc, o = self.tq("submit", mod, "--purpose", "commission", "--by", "BENCH", "--sha", self.sha, "--rows",
                        "r%d" % self.n,
                        "--priority", str(priority), "--no-sha-check")
        try:
            return json.loads(o.strip().splitlines()[-1])["job"]
        except (ValueError, IndexError, KeyError):
            raise RuntimeError("submit failed: %s" % o[-400:])

    def where(self, jid):
        for st in ("pending", "running", "done", "cancelled"):
            if os.path.exists(self.p("queue", st, jid + ".json")):
                return st

    def rec(self, jid):
        return json.load(open(self.p("queue", self.where(jid), jid + ".json")))

    def alive(self, home):
        """Attempt ids in HOME with a heartbeat (state.json) and no result yet."""
        return [os.path.basename(os.path.dirname(f)) for f in glob.glob(self.p(home, "attempts", "*", "state.json"))
                if not os.path.exists(os.path.join(os.path.dirname(f), "result.json"))]

    def drain(self, limit=90):
        """Tick until nothing is running or pending."""
        t = time.time()
        while time.time() - t < limit:
            self.tq("tick")
            if not glob.glob(self.p("queue", "running", "*.json")) and not glob.glob(self.p("queue", "pending", "*.json")):
                return True
            time.sleep(1)
        return False

    def reset(self):
        self.drain()
        for st in ("pending", "running", "done", "cancelled"):
            for f in glob.glob(self.p("queue", st, "*.json")):
                os.remove(f)
        for f in ("paused.json", "stevedesktop.b_paused.json", "steve2.on", "steve2.stop", "train.json",
                  "stevedesktop.b_train.json"):
            if os.path.exists(self.p("queue", f)):
                os.remove(self.p("queue", f))


def T_NOW():     # a pause with no end ends by the default hours (lane_stop.py): these stand now
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def t_steve2_off_by_default(r):
    r.tq("list")
    subprocess.run(["rm", "-rf", r.p("home_b")])      # an earlier test's drain (with steve2.on) may have made it
    os.makedirs(r.p("home_b"))
    a, b = r.job(), r.job()
    r.tq("tick")
    run = [x for x in (a, b) if r.where(x) == "running"]
    check(len(run) == 1 and r.rec(run[0]).get("host") in (None, "stevedesktop"),
          "steve2-off-by-default: no steve2.on -> one job admitted, to Steve1 (%s)" % [r.where(a), r.where(b)])
    check(not os.path.isdir(r.p("home_b", "attempts")),
          "steve2-off-by-default: Steve2's worker home was never touched")

    r.reset()


def t_two_jobs_run_at_once_one_per_game(r):
    open(r.p("queue", "steve2.on"), "w").close()
    a, b = r.job(), r.job()
    r.tq("tick")
    hosts = sorted((r.rec(x).get("host") or "stevedesktop") for x in (a, b) if r.where(x) == "running")
    check(hosts == ["stevedesktop", "stevedesktop.b"],
          "two-jobs-run-at-once-one-per-game: one tick admits one job per game (%s; states %s)" % (
              hosts, [r.where(a), r.where(b)]))
    time.sleep(1.5)
    al, bl = r.alive("home_a"), r.alive("home_b")
    check(len(al) == 1 and len(bl) == 1,
          "two-jobs-run-at-once-one-per-game: both attempts alive at the same time (Steve1 %s, Steve2 %s)" % (al, bl))
    r.drain()
    done = {x: r.rec(x) for x in (a, b) if r.where(x) == "done"}
    dh = sorted((d.get("host") or "stevedesktop") for d in done.values())
    rh = sorted(d["result"].get("host") for d in done.values())
    check(dh == ["stevedesktop", "stevedesktop.b"] and rh == ["stevedesktop", "stevedesktop.b"],
          "two-jobs-run-at-once-one-per-game: each result lands in done/ with its own host (record %s, result %s)" % (
              dh, rh))
    r.reset()


def t_steve2_respects_the_machine_pause_and_its_own(r):
    open(r.p("queue", "steve2.on"), "w").close()
    json.dump({"since": T_NOW(), "reason": "test machine pause"}, open(r.p("queue", "paused.json"), "w"))
    a = r.job()
    r.tq("tick")
    check(r.where(a) == "pending", "steve2-respects-the-machine-pause-and-its-own: machine pause -> Steve2 admits "
                                   "nothing (%s)" % r.where(a))
    os.remove(r.p("queue", "paused.json"))
    json.dump({"since": T_NOW(), "reason": "test steve2 pause"},
              open(r.p("queue", "stevedesktop.b_paused.json"), "w"))
    b = r.job()
    r.tq("tick")
    hosts = [(r.rec(x).get("host") or "stevedesktop") for x in (a, b) if r.where(x) == "running"]
    check(hosts == ["stevedesktop"] and [r.where(a), r.where(b)].count("pending") == 1,
          "steve2-respects-the-machine-pause-and-its-own: Steve2's own pause stops Steve2 only (%s)" % hosts)
    rc, o = r.tq("resume", "--lane", "stevedesktop.b", "--reason", "test")
    check(rc == 0 and not os.path.exists(r.p("queue", "stevedesktop.b_paused.json")),
          "steve2-respects-the-machine-pause-and-its-own: resume --lane stevedesktop.b lifts it (rc %s: %s)" % (
              rc, o.strip()[-120:]))
    r.reset()


def t_steve2_stop_file_wins(r):
    open(r.p("queue", "steve2.on"), "w").close()
    a, b = r.job(), r.job()
    r.tq("tick")
    on_b = [x for x in (a, b) if r.where(x) == "running" and r.rec(x).get("host") == "stevedesktop.b"]
    open(r.p("queue", "steve2.stop"), "w").close()
    c = r.job()
    r.tq("tick")
    check(not (r.where(c) == "running" and r.rec(c).get("host") == "stevedesktop.b"),
          "steve2-stop-file-wins: no new admission to Steve2 under steve2.stop")
    r.drain()
    check(len(on_b) == 1 and r.where(on_b[0]) == "done",
          "steve2-stop-file-wins: the job already on Steve2 is still reconciled to done/ (%s)" % (
              [r.where(x) for x in on_b]))
    r.reset()


def t_steve2_command_carries_its_game(r):
    got = r.py("import testq; print(json.dumps([testq.remote_cmd(['status'], testq.STEVE2), "
               "testq.remote_cmd(['status'], testq.STEVE)]))", TESTQ_STEVE2_PREFIX=None, TESTQ_REMOTE_RUNNER_B=None,
               TESTQ_STEVE2_HOME=None, TESTQ_REMOTE_RUNNER=None)
    b, a = (got if isinstance(got, list) else ["", ""])
    check(b.startswith("cd ~/rm/runner_b && ") and "game_instance.py env b) && eval" in b
          and "TESTQ_HOME=/mnt/d/RimTest/testq.b" in b and "TESTQ_WORKER_HOST=stevedesktop.b" in b
          and "TESTQ_COMPANION_INBOX=/mnt/d/RimTest/testq/companion" in b and b.index("&& python3") > b.index("eval"),
          "steve2-command-carries-its-game: Steve2's command: %s" % b[:300])
    check(a.startswith("cd ~/rm/runner && python3 ") and "game_instance" not in a,
          "steve2-command-carries-its-game: Steve1's command is unchanged: %s" % a[:200])


def plant_running(r, host, jid="J_PLANT", mod="Mock", by="BENCH"):
    job = {"schema": "testq.job/1", "id": jid, "mod": mod, "requested_by": by, "lane": "stevedesktop",
           "priority": 20, "profile": "minimal", "submitted": "2026-11-23T00:00:00Z", "selector": {"chains": ["c1"]}}
    rec = {"job": job, "attempt": jid + ".a1", "sent": "2026-11-23T00:00:00Z", "attempts": [jid + ".a1"]}
    if host != "stevedesktop":
        rec["host"] = host
    json.dump(rec, open(r.p("queue", "running", jid + ".json"), "w"))


def t_filler_fills_an_idle_game(r):
    r.tq("list")
    plant_running(r, "stevedesktop")
    v_off = r.py("import testq; print(json.dumps(testq.fill_plan('Mock', 4, 200)['verdict']))")
    open(r.p("queue", "steve2.on"), "w").close()
    v_on = r.py("import testq; print(json.dumps(testq.fill_plan('Mock', 4, 200)['verdict']))")
    plant_running(r, "stevedesktop.b", jid="J_PLANT2")
    v_both = r.py("import testq; print(json.dumps(testq.fill_plan('Mock', 4, 200)['verdict']))")
    check(v_off == "busy" and v_on not in ("busy", None) and not isinstance(v_on, dict) and v_both == "busy",
          "filler-fills-an-idle-game: Steve1 busy, Steve2 off -> busy (%s); Steve2 on and idle -> not busy (%s); "
          "both running -> busy (%s)" % (v_off, v_on, v_both))
    os.remove(r.p("queue", "running", "J_PLANT.json"))
    open(r.p("queue", "steve2.stop"), "w").close()
    draining = r.py("import testq, gaps\n"
                    "gaps.owed_items = lambda world=None: {}\n"
                    "def plan(chains):\n"
                    "    gaps.probe = lambda mod, items, since: {'chains': chains, 'item_chains': {'X_OWES_L1': chains}}\n"
                    "    p = testq.fill_plan('Mock', 4, 200)\n"
                    "    return [p['verdict'], p.get('pick'), p['text']]\n"
                    "print(json.dumps([plan(['c1']), plan(['c1', 'c2'])]))")
    check(isinstance(draining, list) and draining[0][:2] == ["exhausted", []],
          "filler-fills-an-idle-game: Steve2 draining c1, only c1 offered -> exhausted (%s)" % (draining,))
    check(isinstance(draining, list) and draining[1][:2] == ["pick", ["c2"]],
          "filler-fills-an-idle-game: Steve2 draining c1 under steve2.stop, Steve1 idle -> pick c2 (%s)" % (draining,))
    for f in glob.glob(r.p("queue", "running", "*.json")):
        os.remove(f)
    r.reset()


def t_visit_feed_one_mod_per_game(r):
    r.tq("list")
    code = "import testq, visit_feed; print(json.dumps(visit_feed.in_flight(testq)))"
    plant_running(r, "stevedesktop", jid="J_V1", mod="FlowWorks", by="BENCH.visit")
    off = r.py(code)
    open(r.p("queue", "steve2.on"), "w").close()
    on = r.py(code)
    plant_running(r, "stevedesktop.b", jid="J_V2", mod="Pyrelands", by="BENCH.visit")
    both = r.py(code)
    check(isinstance(off, list) and off[0] is not None, "visit-feed-one-mod-per-game: one game live, a visit job "
                                                        "running -> busy (%s)" % (off,))
    check(isinstance(on, list) and on[0] is None and on[1] == ["FlowWorks"],
          "visit-feed-one-mod-per-game: two games live, one visit job running -> free, FlowWorks excluded (%s)" % (on,))
    check(isinstance(both, list) and both[0] is not None,
          "visit-feed-one-mod-per-game: two visit jobs running on two games -> busy (%s)" % (both,))
    for f in glob.glob(r.p("queue", "running", "*.json")):
        os.remove(f)
    json.dump({"schema": "testq.job/1", "id": "J_VP", "mod": "Pyrelands", "requested_by": "BENCH.visit",
               "lane": "stevedesktop", "priority": 60, "profile": "minimal", "submitted": "2026-11-23T00:00:00Z",
               "selector": {"chains": ["c1"]}}, open(r.p("queue", "pending", "J_VP.json"), "w"))
    pend = r.py(code)
    check(isinstance(pend, list) and pend[0] is not None,
          "visit-feed-one-mod-per-game: a visit job pending -> busy (%s)" % (pend,))
    os.remove(r.p("queue", "pending", "J_VP.json"))
    r.reset()


def t_steve2_results_are_steve_results(r):
    r.tq("list")
    json.dump([{"id": "W_TEST", "start": "2026-11-23T01:00:00Z", "end": "2026-11-23T02:00:00Z"}],
              open(r.p("queue", "fault_windows.json"), "w"))
    rec = {"job": {"id": "J_X", "mod": "Mock", "profile": "minimal"}, "sent": "2026-11-23T01:10:00Z",
           "finished": "2026-11-23T01:20:00Z", "host": "stevedesktop.b",
           "result": {"host": "stevedesktop.b", "started": "2026-11-23T01:10:00Z", "finished": "2026-11-23T01:20:00Z"}}
    got = r.py("import fault_monitor as FM, ingest\nrec = %r\n"
               "g = FM.gate(rec, FM.load()[0], {'clean_through_s': 0})\nw, why = ingest.env_window(rec)\n"
               "print(json.dumps([g[0], (w or {}).get('id'), ingest.config_for('stevedesktop.b', 'X', 'minimal'), "
               "ingest.config_for('stevedesktop', 'X', 'minimal'), ingest.config_for('archmagi', 'X', 'full-list')]))"
               % rec)
    check(isinstance(got, list) and got[0] == "quarantine" and got[1] == "W_TEST",
          "steve2-results-are-steve-results: an in-window Steve2 result is quarantined and ingest sees the window (%s)"
          % (got,))
    check(isinstance(got, list) and got[2:] == ["steve-minimal", "steve-minimal", "archmagi-full-list"],
          "steve2-results-are-steve-results: ingest config steve-<profile> for both Steve games (%s)" % (got,))
    os.remove(r.p("queue", "fault_windows.json"))


def t_fault_drain_waits_for_both_workers(r):
    r.tq("list")
    code = ("import testq as T, fault_monitor as FM\n"
            "def fake(args, stdin=None, timeout=180, host=T.STEVE):\n"
            "    return 0, {'busy': host == T.STEVE2}\n"
            "T.remote = fake\nprint(json.dumps(FM.worker_busy()))")
    off = r.py(code)
    open(r.p("queue", "steve2.on"), "w").close()
    on = r.py(code)
    check(off is False and on is True, "fault-drain-waits-for-both-workers: Steve2 busy -> worker_busy False with "
                                       "Steve2 off (%s), True with it on (%s)" % (off, on))
    r.reset()


def t_steve2_worker_is_a_steve_lane(r):
    code = ("os = __import__('os'); import worker as W\n"
            "print(json.dumps([W.STEVE_LANE, W.staged_companion(), sorted(k for k in W.kept_env_keys("
            "{'GABP_SERVER_PORT': '5175', 'GABP_TOKEN': 't', 'RM_GAME_INSTANCE': 'b', 'OTHER': 'x'}))]))")
    b = r.py(code, TESTQ_WORKER_HOST="stevedesktop.b", TESTQ_COMPANION_INBOX="/x/companion", TESTQ_HOME=r.p("home_w"))
    a = r.py(code, TESTQ_WORKER_HOST="archmagi", TESTQ_HOME=r.p("home_a"))
    check(isinstance(b, list) and b[0] is True and b[1] == "/x/companion/" + CI.DLL_NAME
          and b[2] == ["GABP_SERVER_PORT", "GABP_TOKEN", "RM_GAME_INSTANCE"],
          "steve2-worker-is-a-steve-lane: Steve2's worker is a Steve lane, reads TESTQ_COMPANION_INBOX, keeps GABP_ (%s)"
          % (b,))
    check(isinstance(a, list) and a[0] is False and a[1] == os.path.join(r.p("home_a"), "companion", CI.DLL_NAME),
          "steve2-worker-is-a-steve-lane: the archmagi worker is not, and reads its own home's inbox (%s)" % (a,))

    stopped = shlex.quote(r.p("recycle_down"))
    load = ("if [ -f %s ]; then echo 'started Steve2, pid 4242, bridge on port 5175 after 90 s'; "
            "else echo 'already running (pid 1234)'; echo 'running pid=1234 age_s=29000'; fi" % stopped)
    recycled = r.py("import os, worker as W\n"
                    "W.ensure_dirs()\n"
                    "job = W.S.make_job('Mock', {'rows': ['r1']}, 'commission', 'BENCH', %r)\n"
                    "aid = job['id'] + '.a1'\nd = W.p('attempts', aid)\nos.makedirs(d)\n"
                    "W.S.dump(job, os.path.join(d, 'job.json'))\n"
                    "a = W.Attempt(aid)\na.run()\n"
                    "print(json.dumps([a.res['outcome'], a.res['cause'], a.game_pid, "
                    "a.res.get('recycled_kept_game'), a.res.get('counts', {}).get('PASS', 0), "
                    "a.res['note'].partition(': ')[0]]))"
                    % r.sha,
                    TESTQ_WORKER_HOST="stevedesktop.b", TESTQ_HOME=r.p("home_w"), RM_HOST="stevedesktop",
                    RM_GAME_INSTANCE="b", RIMFLOW_DRIVER_LOCK=r.p("LOCK_B.json"), MOCK_SLEEP="0",
                    TESTQ_CMD_LOAD=load, TESTQ_CMD_DOWN="touch " + stopped)
    check(isinstance(recycled, list) and recycled[:3] == ["DONE", None, "4242"]
          and "h old" in (recycled[3] or "") and recycled[4] == 1,
          "steve2-worker-is-a-steve-lane: an old Steve2 restarts with its fresh PID and runs rows (%s)" % (recycled,))


def t_steve2_reads_its_own_install(r):
    """J20261124T001426Z-9581b9: Steve2's worker checked and installed the companion in Steve1's Steam install, said FRESH,
    and the game loaded the old one."""
    code = ("import worker as W\na = W.Attempt.__new__(W.Attempt)\n"
            "print(json.dumps([a.mods_dir(), a.companion_dir()]))")
    steam = dict(TESTQ_MODS_DIR=None, TESTQ_COMPANION_DIR=None, RM_STEAMAPPS="/steam")
    b = r.py(code, TESTQ_WORKER_HOST="stevedesktop.b", RM_GAME_INSTANCE="b", RM_GAME_USERDATA="/inst/b", **steam)
    a = r.py(code, TESTQ_WORKER_HOST="stevedesktop", RM_GAME_INSTANCE=None, RM_GAME_USERDATA=None, **steam)
    blind = r.py(code, TESTQ_WORKER_HOST="stevedesktop.b", RM_GAME_INSTANCE="b", RM_GAME_USERDATA=None, **steam)
    check(b == ["/inst/b/game/Mods", "/inst/b/game/BridgeTools/JawaBench"],
          "steve2-reads-its-own-install: Steve2's Mods and companion are its own install's (%s)" % (b,))
    check(a == ["/steam/common/RimWorld/Mods", "/steam/common/RimWorld/BridgeTools/JawaBench"],
          "steve2-reads-its-own-install: Steve1's are Steam's, unchanged (%s)" % (a,))
    check(isinstance(blind, list) and not any(x.startswith("/steam") for x in blind),
          "steve2-reads-its-own-install: Steve2 with no data folder named never answers Steve1's install (%s)" % (blind,))


def t_site_saves_reach_steve2(r):
    """sync_test_mods.site_saves copies each registered save into every target Saves folder it is given, and the tick
    asks for Steve2's folder too while Steve2 is switched on."""
    code = ("import sync_test_mods as M\npushed = []\n"
            "M.remote_saves = lambda: '/a/Saves'\nM.remote_sha = lambda path: ''\n"
            "M.push_file = lambda src, d: pushed.append(d)\n"
            "M.remote_sha = (lambda f: (lambda path: f.get(path, '')))(dict())\n"
            "import os, tempfile, json as J\nt = tempfile.mkdtemp(); sv = os.path.join(t, 'S'); os.makedirs(sv)\n"
            "open(os.path.join(sv, 'Site_one.rws'), 'w').write('x')\nreg = os.path.join(t, 'reg.json')\n"
            "J.dump({'one': {'save': 'Site_one'}}, open(reg, 'w'))\n"
            "rc = M.site_saves(True, registry=reg, saves=sv, extra=['/b/Saves'])\n"
            "print(json.dumps(sorted(pushed)))")
    got = r.py(code)
    check(got == ["/a/Saves", "/b/Saves"], "site-saves-reach-steve2: one registered save is pushed to Steve1's and "
                                           "Steve2's Saves (%s)" % (got,))
    argv_off = r.py("import testq; print(json.dumps(testq.site_stage_argv()))")
    open(r.p("queue", "steve2.on"), "w").close()
    argv_on = r.py("import testq; print(json.dumps(testq.site_stage_argv()))")
    check(isinstance(argv_off, list) and "--also-saves" not in argv_off and isinstance(argv_on, list)
          and argv_on[argv_on.index("--also-saves") + 1] == "/mnt/d/ClaudeWork/rimmandrake/instances/b/Saves",
          "site-saves-reach-steve2: the tick's copy names Steve2's Saves only while Steve2 is on (%s / %s)" % (
              argv_off, argv_on))
    r.reset()


def t_a_tick_with_both_games_busy_writes_the_reading(r):
    r.tq("list")
    for f in ("steve_both_busy.json", "steve_games.json"):
        if os.path.exists(r.p("queue", f)):
            os.remove(r.p("queue", f))
    r.job()
    r.tq("tick")
    gv = r.py("import testq; print(json.dumps(testq.read_json(testq.q('steve_games.json'))))")
    check(not os.path.exists(r.p("queue", "steve_both_busy.json")) and isinstance(gv, dict)
          and gv.get("both_busy") is False and (gv.get("games") or {}).get("Steve2", {}).get("state") == "off"
          and (gv.get("games") or {}).get("Steve1", {}).get("state") == "busy",
          "a-tick-with-both-games-busy-writes-the-reading: Steve1 busy, Steve2 off -> no steve_both_busy.json, and "
          "steve_games.json says so (%s)" % (gv,))
    open(r.p("queue", "steve2.on"), "w").close()
    r.job()
    r.tq("tick")
    rd = r.py("import testq; print(json.dumps(testq.read_json(testq.q('steve_both_busy.json'))))")
    gv = r.py("import testq; print(json.dumps(testq.read_json(testq.q('steve_games.json'))))")
    check(isinstance(rd, dict) and sorted(rd.get("jobs", {})) == ["Steve1", "Steve2"] and isinstance(gv, dict)
          and gv.get("both_busy") is True,
          "a-tick-with-both-games-busy-writes-the-reading: both busy -> steve_both_busy.json names both jobs (%s)" % (rd,))
    r.reset()


def t_a_proof_that_crashes_is_unmeasured_not_fail(r):
    tb = ("Traceback (most recent call last):\n  File \"x.py\", line 33, in <module>\n    import numpy as np\n"
          "ModuleNotFoundError: No module named 'numpy'\n")
    cases = [[0, "all PASS"], [1, "ROT_click_RM_X FAIL: a picture cell did not select it"], [1, tb],
             [1, "rows:\n" + tb + "ROT_click_RM_X FAIL: 3 cells missed\n"], [2, "UNMEASURED HARNESS"], [None, ""],
             [1, tb.replace("ModuleNotFoundError: No module named 'numpy'", "PermissionError: [WinError 5] Access is "
                            "denied: '/mnt/d/ClaudeWork'") + "[bridge split] 33.9 s wall: load 0.8 / ticks 0.0\n"]]
    got = r.py("import worker as W\nprint(json.dumps([W.proof_verdict(rc, t)[0] for rc, t in %r]))" % (cases,))
    check(got == ["PASS", "FAIL", "UNMEASURED", "FAIL", "UNMEASURED", "UNMEASURED", "UNMEASURED"],
          "a-proof-that-crashes-is-unmeasured-not-fail: exit 1 ending in a traceback (exit lines after it allowed) reads "
          "UNMEASURED, a FAIL line "
          "after a quoted traceback stays FAIL (%s)" % (got,))


def main():
    tmp = tempfile.mkdtemp(prefix="testq_steve2_")
    r = Rig(tmp)
    for t in (t_steve2_reads_its_own_install, t_site_saves_reach_steve2, t_steve2_command_carries_its_game, t_steve2_worker_is_a_steve_lane, t_steve2_results_are_steve_results,
              t_fault_drain_waits_for_both_workers, t_filler_fills_an_idle_game, t_visit_feed_one_mod_per_game,
              t_steve2_off_by_default, t_two_jobs_run_at_once_one_per_game,
              t_steve2_respects_the_machine_pause_and_its_own, t_steve2_stop_file_wins,
              t_a_tick_with_both_games_busy_writes_the_reading, t_a_proof_that_crashes_is_unmeasured_not_fail):
        try:
            t(r)
        except Exception as e:  # noqa: BLE001 - a crashing test is a failed promise, named
            check(False, "%s crashed: %s: %s" % (t.__name__, type(e).__name__, str(e)[:300]))
    subprocess.run(["rm", "-rf", tmp])
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
