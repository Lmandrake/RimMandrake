#!/usr/bin/env python3
"""Selftest of control.py, the one control store and `pipe` (item RIMMANDRAKE_BUILD_PIPELINE_CONTROL_ONE_LINERS_NO_BUILD_PROCESS;
spec design/specs/2026-11-18-pipeline-control-surface/03-merged.md; acceptance tests from 02-gpt.md findings 2, 3, 4, 7,
8, 14, 15, 16, 17, 23). Temp stores, fixtures and harmless `rm-probe-` units only: never the live store, never a live mod.

  verbs      every write prints at most 3 lines; every verb's p95 is under 1 s (measured, printed); stable exit codes for
             refused (2), could not look (3) and failed (4)
  race       both pause orderings (pause lands between admit and start: REFUSED, released, never "running"; pause after
             start: the run is reported live), in the store and with a real systemd-run unit
  look       two callers racing for one look: exactly one reserves; duplicate settle and duplicate void change nothing;
             a grant adds one; a dead holder's reservation is released as a system fault; the fault alarm counts runs
  unread     missing, corrupt, locked and permission-denied stores: nothing launches (the runner is never called) and
             `pipe show` prints CONTROL UNREADABLE: <cause>, exit 3, never "nothing is off"
  crash      a launcher dying after admit and before systemd-run leaves no run and no charge (reconcile); one dying after
             the unit starts leaves exactly one run, no charge, and a retry of the same unit is refused as DUPLICATE
  clones     `pipe show` from two different code trees over one store prints the same bytes
  void       a void never moves a stage, and `pipe show` flags "stage advanced on a voided run"
  scope      `on all` does not lift a per-mod owner hold; the owner hold's import, his words kept; a lift binds at once
  stop       --kill: a unit that ignores SIGTERM and its child that does the same are dead within 1 s, the run killed and
             its trials released; --write-now: the stop order reaches a running stub agent through its hook within one
             tool call, it writes its handoff note and ends, its trial released; the hook is silent with no order and
             its lookup is under 50 ms; the deadline escalates to --kill
  sites      every systemd-run call site in src/RimMandrake goes through launch_unit, and a mutant launcher turns it red
"""
import contextlib
import io
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FAILS = []
UNRUN = []
TMP = tempfile.mkdtemp(prefix="selftest-control-")
DB = os.path.join(TMP, "c.db")
os.environ["RM_CONTROL_DB"] = DB
os.environ["RM_CONTROL_MODS"] = "Graffiti,Cauldron,Pyrelands"
os.environ["RM_CONTROL_TICK_UNIT"] = ""
os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(TMP, "md")
os.environ["RM_CONTROL_CONCEPTS"] = os.path.join(TMP, "concepts")
os.makedirs(os.environ["RM_MATURATION_DISPATCH_DIR"])
os.makedirs(os.environ["RM_CONTROL_CONCEPTS"])
import control as C  # noqa: E402
import probe_result as P  # noqa: E402

PY = sys.executable
TOOL = os.path.join(HERE, "control.py")


def check(ok, msg, got=None):
    print("%s %s%s" % ("ok  " if ok else "FAIL", msg, "" if ok or got is None else "  (got %r)" % (got,)))
    if not ok:
        FAILS.append(msg)


def pipe(*args, env=None):
    t0 = time.monotonic()
    r = subprocess.run([PY, TOOL] + list(args), capture_output=True, text=True, timeout=60,
                       env=dict(os.environ, **(env or {})))
    return r.returncode, (r.stdout or "") + (r.stderr or ""), time.monotonic() - t0


def fresh():
    for x in os.listdir(TMP):
        if x.startswith("c.db"):
            os.unlink(os.path.join(TMP, x))
    C.init(DB)


def spec(unit, **kw):
    return dict({"family": "probe", "unit": unit}, **kw)


def systemd_ok():
    try:
        r = subprocess.run(["systemctl", "--user", "is-system-running"], capture_output=True, text=True, timeout=5)
        return r.stdout.strip() in ("running", "degraded")
    except (OSError, subprocess.SubprocessError):
        return False


def unit_state(u):
    r = subprocess.run(["systemctl", "--user", "show", "-p", "ActiveState", "--value", u], capture_output=True,
                       text=True, timeout=5)
    return r.stdout.strip()


def wait_for(pred, t=10.0, step=0.05):
    end = time.monotonic() + t
    while time.monotonic() < end:
        if pred():
            return True
        time.sleep(step)
    return pred()


# ---------------------------------------------------------------- verbs, lines, times, exit codes

def p95_of(ts):
    ts = sorted(ts)
    return ts[int(0.95 * (len(ts) - 1))]


def slow_verbs(times, limit):
    """-> the verbs whose OWN p95 is at or over `limit` seconds.

    LIMIT: 1 s. Danger it guards: a verb that reaches git, a clone, a test door or a sleep takes seconds on EVERY
    call, and then the Conductor and every tick wait on it (boundary.md, promise verbs-answer-in-a-second;
    planted fault: `main()` sleeps 1.1 s, RED). Evidence it can happen: that planted fault, and one publish refused
    at 1.134 s on a busy machine (2026-11-19), which passed on rerun. So a verb whose call is over the limit is timed
    again, up to 4 more times (`t_verbs`), and its fastest call counts: a broken verb is slow every time, a busy
    machine stalls only some calls. (Load average 40 on 2026-11-19 stalled two calls in a row, 2.5 s.)"""
    return sorted(v for v, ts in times.items() if p95_of(ts) >= limit)


def t_verbs():
    fresh()
    times = {}
    for v, args, want in (
            ("off", ["off", "Graffiti", "--why", "test off"], 0),
            ("show", ["show"], 0),
            ("show-mod", ["show", "Graffiti"], 0),
            ("why", ["why", "Graffiti"], 0),
            ("log", ["log", "-n", "5"], 0),
            ("on", ["on", "Graffiti", "--why", "test on"], 0),
            ("off-all", ["off", "all", "--why", "test all"], 0),
            ("on-all", ["on", "all", "--why", "test all on"], 0),
            ("off-stage", ["off", "stage:blind_challenge", "--why", "t"], 0),
            ("off-item", ["off", "item:RIMMANDRAKE_X_Y_Z_W", "--why", "t"], 0),
            ("off-family", ["off", "family:testq", "--why", "t"], 0),
            ("void", ["void", "rm-probe-v1", "--why", "test void"], 0),
            ("grant", ["grant", "Graffiti", "look", "+1", "--why", "t", "--owner-said", "give it one more"], 0)):
        ts = []
        for _ in range(5 if v in ("show", "why", "log") else 1):
            rc, out, el = pipe(*args)
            for _ in range(4):  # a busy-machine stall (load 40 measured): time it again, keep the fastest call
                if el < 1.0 or v == "grant":
                    break
                el = min(el, pipe(*args)[2])
            ts.append(el)
        times[v] = ts
        lines = [x for x in out.splitlines() if x.strip()]
        check(rc == want, "pipe %s exits %d" % (" ".join(args[:2]), want), (rc, out[-300:]))
        if v in ("off", "on", "off-all", "on-all", "off-stage", "off-item", "off-family", "void", "grant"):
            check(len(lines) <= 3, "pipe %s prints at most 3 lines" % v, lines)
    allt = sorted(x for ts in times.values() for x in ts)
    worst = max(times, key=lambda v: p95_of(times[v]))
    print("     measured: %d pipe calls (fresh python each), worst verb p95 %.0f ms (%s), max %.0f ms" % (
        len(allt), p95_of(times[worst]) * 1000, worst, allt[-1] * 1000))
    check(not slow_verbs(times, 1.0), "every pipe verb's p95 is under 1 s",
          {v: round(p95_of(times[v]), 3) for v in slow_verbs(times, 1.0)})
    # round-two claim 9: the check is per verb (a pooled p95 passed one verb at 1.5 s among fast ones)
    check(slow_verbs(dict({"slow": [1.5]}, **{"v%d" % i: [0.2] * 5 for i in range(8)}), 1.0) == ["slow"],
          "claim r2-9: one slow verb among fast ones fails the p95 check")
    check(allt[-1] < 2.0, "every pipe verb is under 2 s", allt[-1])
    rc, out, _ = pipe("off", "Grafiti", "--why", "typo")
    check(rc == 2 and "Graffiti" in out, "a wrong mod is refused (2) with the nearest name", (rc, out))
    rc, out, _ = pipe("off", "Graffiti")
    check(rc == 2, "a write without --why is refused (2)", (rc, out))
    rc, out, _ = pipe("grant", "Graffiti", "look", "+1", "--why", "no words")
    check(rc == 2 and "his" in out, "a granted look without his words is refused (2)", (rc, out))
    rc, out, _ = pipe("stop", "Graffiti", "--write-now", "--kill", "--why", "two modes")
    check(rc == 2, "two stop modes are refused (2)", (rc, out))
    rc, out, _ = pipe("show", env={"RM_CONTROL_DB": os.path.join(TMP, "absent.db")})
    check(rc == 3 and out.startswith("CONTROL UNREADABLE:"), "an absent store: show says CONTROL UNREADABLE, exit 3",
          (rc, out))
    with open(os.path.join(os.environ["RM_MATURATION_DISPATCH_DIR"], "reading.json"), "w") as f:
        json.dump({"at_pac": "2026-11-18 1:05 PM PST", "mods": {"Graffiti": {"decision": "owner_hold",
                                                                             "stage": "blind_challenge"}}}, f)
    out = "\n".join(C.show())
    check("tick: owner_hold" in out and "blind_challenge" in out, "show reads the tick's reading (mods by name)", out)
    check("owner_hold" in C.why("Graffiti"), "why reads the tick's row for the mod")
    os.unlink(os.path.join(os.environ["RM_MATURATION_DISPATCH_DIR"], "reading.json"))
    # in-process: the verbs themselves, without python start
    t0 = time.monotonic()
    for _ in range(20):
        C.show()
        C.why("Graffiti")
    per = (time.monotonic() - t0) / 40
    print("     measured: show/why in-process %.1f ms each" % (per * 1000))
    check(per < 0.2, "show and why take under 200 ms in-process", per)


# ---------------------------------------------------------------- switches and scope precedence

def t_scope():
    fresh()
    C.switch("mod:Graffiti", True, "his hold", layer="owner", said="stop Graffiti")
    r = C.switch("all", False, "lift all")
    check(not r["had"], "on all with no all-switch lifts nothing")
    C.switch("all", True, "pause all")
    C.switch("all", False, "resume all")
    check(C.blocked(spec("u1", mod="Graffiti")) and "HELD BY OWNER" in C.blocked(spec("u1", mod="Graffiti")),
          "`on all` does not lift a per-mod owner hold", C.blocked(spec("u1", mod="Graffiti")))
    rc, out, _ = pipe("on", "Graffiti", "--why", "try")
    check(rc == 0 and "HELD BY OWNER" in out, "`pipe on <Mod>` under his hold says it is still held", out)
    check(C.blocked(spec("u2", mod="Cauldron")) is None, "another mod is not blocked")
    C.switch("stage:in_game", True, "no live")
    check(C.blocked(spec("u3", mod="Cauldron", stage="in_game")), "a stage switch blocks that stage")
    check(C.blocked(spec("u4", mod="Cauldron", stage="designer")) is None, "a stage switch blocks no other stage")
    C.switch("item:RIMMANDRAKE_A_B_C_D", True, "item off")
    check(C.blocked(spec("u5", item="RIMMANDRAKE_A_B_C_D")), "an item switch blocks that item")
    C.switch("family:testq", True, "family off")
    check(C.blocked({"family": "testq", "unit": "u6"}), "a family switch blocks that family")
    r1 = C.switch("mod:Cauldron", True, "x", idem="k1")
    r2 = C.switch("mod:Cauldron", True, "x", idem="k1")
    check(r2["replayed"] and r2["act"]["id"] == r1["act"]["id"], "a retried act with its idempotency key changes "
                                                                   "nothing")
    try:
        C.switch("mod:Cauldron", True, "x", layer="owner")
        check(False, "an owner hold without his words is refused")
    except C.Refused:
        check(True, "an owner hold without his words is refused")
    until = time.time() + 2
    C.switch("mod:Pyrelands", True, "until", until=until)
    check(C.blocked(spec("u7", mod="Pyrelands")), "an --until switch blocks before its time")
    check(C.blocked(spec("u7", mod="Pyrelands"), now=until + 1) is None, "and not after it")


# ---------------------------------------------------------------- the pause race, both orderings

def t_race():
    fresh()
    a = C.admit(spec("rm-probe-r1", mod="Graffiti", resources=[{"resource": C.LOOK, "win": "w", "base": 1}]))
    check(a["ok"], "admit reserves")
    check(C.account("Graffiti", C.LOOK, "w", 1)["held"] == 1, "the look is held after admit")
    r = C.switch("all", True, "pause between admit and start")
    check(r["cancelled"] == ["rm-probe-r1"], "pipe off cancels the unstarted run in the same transaction", r)
    code, line = C.condition(a["run"])
    check(code == 1 and "REFUSED" in line, "its unit's condition then refuses it", (code, line))
    check(C.run_state(a["run"])["state"] == "cancelled", "the run reads cancelled, never running")
    check(C.account("Graffiti", C.LOOK, "w", 1)["held"] == 0, "its reservation is released")
    C.switch("all", False, "resume")
    b = C.admit(spec("rm-probe-r2", mod="Graffiti"))
    code, _ = C.condition(b["run"])
    check(code == 0, "a run whose condition passed before the pause starts")
    C.switch("all", True, "pause after start")
    check(C.run_state(b["run"])["state"] == "started", "a pause after start leaves the started run reported live")
    rc, out, _ = pipe("off", "all", "--why", "again")
    check("1 run(s) live" in out and "pipe stop" in out, "pipe off names the live run and the three stop commands", out)
    if not systemd_ok():
        UNRUN.append("race with a real unit: no user systemd here")
        return
    fresh()
    mark = os.path.join(TMP, "race-mark")

    def runner_pausing(argv, **kw):     # the pause lands after admit, before systemd-run starts the unit
        C.switch("all", True, "pause inside the launch")
        return subprocess.run(argv, **kw)
    res = C.launch_unit(["--user", "--quiet", "--collect",
                         "--", "/bin/sh", "-c", "touch " + mark], spec("rm-probe-race-a"), runner=runner_pausing,
                        capture_output=True, text=True, timeout=30)
    time.sleep(0.3)
    check(res.refused and res.returncode == C.LAUNCH_REFUSED_RC, "real unit, pause before start: the launcher gets "
                                                                   "REFUSED, never rc 0", (res.returncode, res.stderr))
    check(not os.path.exists(mark), "real unit, pause before start: its payload never ran")
    C.switch("all", False, "resume")
    res = C.launch_unit(["--user", "--quiet", "--collect",
                         "--", "/bin/sh", "-c", "touch %s; sleep 2" % mark], spec("rm-probe-race-b"), capture_output=True,
                        text=True, timeout=30)
    check(res.returncode == 0 and not res.refused, "real unit, no pause: it starts", (res.returncode, res.stderr))
    wait_for(lambda: os.path.exists(mark), 5)
    C.switch("all", True, "pause after start")
    check(os.path.exists(mark) and C.run_state("rm-probe-race-b")["state"] == "started",
          "real unit, pause after start: its payload ran and it reads started (live)")
    wait_for(lambda: C.run_state("rm-probe-race-b")["state"] == "ended", 10)
    check(C.run_state("rm-probe-race-b")["state"] == "ended", "its ExecStopPost records it ended")


# ---------------------------------------------------------------- one look, two callers; settle and void once

def t_look():
    fresh()
    got = []
    barrier = threading.Barrier(8)

    def one(i):
        barrier.wait()
        ok, _ = C.reserve("Graffiti", C.LOOK, "judge-%d" % i, win="w1", base=1, pid=os.getpid())
        got.append(ok)
    ts = [threading.Thread(target=one, args=(i,)) for i in range(8)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    check(got.count(True) == 1, "eight callers race for one look: exactly one reserves", got)
    procs = [subprocess.Popen([PY, "-c", "import sys; sys.path.insert(0, %r); import control as C, os; "
                                         "ok, _ = C.reserve('Cauldron', C.LOOK, 'p%%d' %% os.getpid(), win='w2', "
                                         "base=1, pid=1); print(ok)" % HERE],
                              stdout=subprocess.PIPE, text=True) for _ in range(6)]
    outs = [p.communicate()[0].strip() for p in procs]
    check(outs.count("True") == 1, "six processes race for one look: exactly one reserves", outs)
    winner = [r for r in C._q("SELECT * FROM reservations WHERE mod='Graffiti'")][0]["run"]
    n1 = C.settle(winner, True, "verdict not_covered")
    n2 = C.settle(winner, True, "again")
    a = C.account("Graffiti", C.LOOK, "w1", 1)
    check(n1 == 1 and n2 == 0 and a["charged"] == 1 and a["available"] == 0, "settle charges once; a second settle "
                                                                              "changes nothing", (n1, n2, a))
    v1 = C.void(winner, "system fault after all")
    v2 = C.void(winner, "again")
    a = C.account("Graffiti", C.LOOK, "w1", 1)
    check(not v1["replayed"] and v2["replayed"] and a["charged"] == 0 and a["available"] == 1 and a["voided"] == 1,
          "void gives the look back once; a second void changes nothing", a)
    check(C.settle(winner, True, "late") == 0 and C.account("Graffiti", C.LOOK, "w1", 1)["charged"] == 0,
          "a voided run is never charged afterwards")
    ok, _ = C.reserve("Graffiti", C.LOOK, "judge-next", win="w1", base=1, pid=os.getpid())
    check(ok, "the given-back look can be reserved again")
    ok2, why = C.reserve("Graffiti", C.LOOK, "judge-next2", win="w1", base=1, pid=os.getpid())
    check(not ok2 and "none available" in why, "and not twice", why)
    C.grant("Graffiti", C.LOOK, 1, "his exception", win="w1", owner_said="one more")
    ok3, _ = C.reserve("Graffiti", C.LOOK, "judge-next2", win="w1", base=1, pid=os.getpid())
    check(ok3, "a grant adds one")
    ok4, _ = C.reserve("Pyrelands", C.LOOK, "dead-holder", win="w3", base=1, pid=2 ** 22 + 7)
    ok5, _ = C.reserve("Pyrelands", C.LOOK, "live-holder", win="w3", base=1, pid=os.getpid())
    check(ok4 and ok5, "a reservation whose holder died is released (fail_system) before the next reserve")
    check(C.faults("Pyrelands") == 1, "and counted once on the system-fault meter", C.faults("Pyrelands"))
    for i in range(3):
        C.reserve("Cauldron", "x", "f%d" % i, base=9, pid=os.getpid())
        C.settle("f%d" % i, False, "no result file")
    check(C.faults("Cauldron") == 3, "every fail_system settlement counts on the meter (runs, not rows)")
    check(C.account("Cauldron", "x", "", 9)["charged"] == 0, "and charges nothing")


# ---------------------------------------------------------------- unreadable stores fail closed

def t_unreadable():
    called = []

    def runner(argv, **kw):
        called.append(argv)
        return subprocess.CompletedProcess(argv, 0, "", "")
    cases = []
    absent = os.path.join(TMP, "absent2.db")
    cases.append(("missing", absent, None))
    bad = os.path.join(TMP, "corrupt.db")
    with open(bad, "wb") as f:
        f.write(b"this is not a database" * 100)
    cases.append(("corrupt", bad, None))
    perm = os.path.join(TMP, "perm.db")
    C.init(perm)
    os.chmod(perm, 0)
    cases.append(("permission", perm, None))
    locked = os.path.join(TMP, "locked.db")
    C.init(locked)
    holder = sqlite3.connect(locked, isolation_level=None)
    holder.execute("BEGIN EXCLUSIVE")
    cases.append(("locked", locked, holder))
    schema = os.path.join(TMP, "schema.db")
    C.init(schema)
    s = sqlite3.connect(schema, isolation_level=None)
    s.execute("UPDATE meta SET v='99' WHERE k='schema'")
    s.close()
    cases.append(("wrong schema", schema, None))
    for name, p, _h in cases:
        called.clear()
        res = C.launch_unit(["--user", "--", "true"],
                            spec("rm-probe-u-" + name.replace(" ", "")), runner=runner, p=p)
        check(res.refused and res.unreadable and not called, "%s store: nothing launches (the runner is never called)"
              % name, (res.returncode, res.stderr, called))
        rc, out, el = pipe("show", env={"RM_CONTROL_DB": p})
        if name == "locked":    # WAL: the last committed state is still read, and the lock is said first
            check(rc == 0 and out.startswith("STORE LOCKED:"), "locked store: pipe show says STORE LOCKED first and "
                                                                "shows the last committed state", (rc, out[:200]))
        else:
            check(rc == 3 and out.startswith("CONTROL UNREADABLE:") and "nothing is off" not in out,
                  "%s store: pipe show prints CONTROL UNREADABLE: <cause>, exit 3" % name, (rc, out[:200]))
        code, line = C.condition("run_x", p=p)
        check(code == 2, "%s store: a unit's condition skips it" % name, (code, line))
    holder.execute("ROLLBACK")
    holder.close()
    os.chmod(perm, 0o600)


# ---------------------------------------------------------------- crash before and after the unit starts

def t_crash():
    fresh()
    child = ("import sys, os; sys.path.insert(0, %r); import control as C; "
             "a = C.admit({'family': 'probe', 'unit': 'rm-probe-crash1', 'mod': 'Graffiti', "
             "'resources': [{'resource': C.LOOK, 'win': 'wc', 'base': 1}]}); os._exit(0)" % HERE)
    subprocess.run([PY, "-c", child], timeout=30)
    check(C.account("Graffiti", C.LOOK, "wc", 1)["held"] == 1, "a launcher that died after admit left its intent "
                                                                 "admitted and held")
    gone = C.reconcile(min_age_s=0, unit_loaded=lambda u: False)
    a = C.account("Graffiti", C.LOOK, "wc", 1)
    check(gone == ["rm-probe-crash1"] and a["held"] == 0 and a["charged"] == 0, "reconcile abandons it: no run, no "
                                                                                 "charge", (gone, a))
    code, _ = C.condition("run_rm-probe-crash1")
    check(code == 1, "an abandoned run's unit, if it ever starts, is refused (fenced)")
    check(C.reconcile(min_age_s=0, unit_loaded=lambda u: None) == [], "a blind systemd read abandons nothing")
    if not systemd_ok():
        UNRUN.append("crash after start with a real unit: no user systemd here")
        return
    child2 = ("import sys, os, subprocess; sys.path.insert(0, %r); import control as C\n"
              "def run(argv, **kw):\n    r = subprocess.run(argv, **kw); os._exit(0)\n"
              "C.launch_unit(['--user', '--quiet', '--collect', '--', '/bin/sleep',"
              " '1'], {'family': 'probe', 'unit': 'rm-probe-crash2', 'mod': 'Graffiti', 'resources': [{'resource': "
              "C.LOOK, 'win': 'wc2', 'base': 1}]}, runner=run, capture_output=True, text=True, timeout=30)" % HERE)
    subprocess.run([PY, "-c", child2], timeout=60)
    wait_for(lambda: (C.run_state("rm-probe-crash2") or {}).get("state") == "ended", 10)
    rows = C._q("SELECT * FROM runs WHERE unit='rm-probe-crash2'")
    a = C.account("Graffiti", C.LOOK, "wc2", 1)
    check(len(rows) == 1 and rows[0]["state"] == "ended", "a launcher that died after the unit started: exactly one "
                                                          "run, recorded ended by its unit", rows)
    check(a["charged"] == 0 and a["held"] == 0, "and no charge (it never settled: released)", a)
    res = C.launch_unit(["--user", "--", "true"], spec("rm-probe-crash2"),
                        runner=lambda *x, **k: (_ for _ in ()).throw(AssertionError("ran")))
    check(res.refused and "DUPLICATE" in res.stderr, "a retry under the same unit is refused as DUPLICATE, never run",
          res.stderr)


# ---------------------------------------------------------------- two clones read one status

def t_clones():
    fresh()
    C.switch("mod:Graffiti", True, "his hold", layer="owner", said="stop Graffiti")
    C.switch("stage:in_game", True, "no live today")
    outs = []
    for n in ("a", "b"):
        d = os.path.join(TMP, "clone-" + n, "src", "RimMandrake", "rimflow")
        os.makedirs(d)
        shutil.copy(TOOL, d)
        for sib in ("probe_result.py", "mod_next.py"):     # a clone holds control.py's siblings
            shutil.copy(os.path.join(os.path.dirname(TOOL), sib), d)
        r = subprocess.run([PY, os.path.join(d, "control.py"), "show"], capture_output=True, text=True, timeout=30)
        outs.append((r.returncode, r.stdout))
    check(outs[0] == outs[1] and outs[0][0] == 0 and "HELD BY OWNER" in outs[0][1],
          "pipe show from two clones over one store prints the same bytes", outs)


# ---------------------------------------------------------------- a void never moves a stage

def t_void_stage():
    fresh()
    d = os.path.join(os.environ["RM_CONTROL_CONCEPTS"], "Graffiti")
    os.makedirs(d, exist_ok=True)
    st = {"stage": "in_game", "history": [{"at": "2026-11-18T18:00:00Z", "from": "blind_challenge", "to": "in_game",
                                           "run": "rm-detached-bench-graffiti-judge-1"}]}
    with open(os.path.join(d, "stage.json"), "w", encoding="utf-8") as f:
        json.dump(st, f)
    before = open(os.path.join(d, "stage.json"), "rb").read()
    rc, out, _ = pipe("void", "rm-detached-bench-graffiti-judge-1", "--why", "killed by us", "--mod", "Graffiti")
    check(rc == 0 and "no stage moved" in out, "pipe void says no stage moved", out)
    check(open(os.path.join(d, "stage.json"), "rb").read() == before, "the stage record is untouched by a void")
    rc, out, _ = pipe("show", "Graffiti")
    check("stage advanced on a voided run" in out, "pipe show flags the stage advanced on a voided run", out)


# ---------------------------------------------------------------- the owner hold: import, lift, mirror

def t_owner_import():
    fresh()
    hf = os.path.join(TMP, "holds.json")
    with open(hf, "w", encoding="utf-8") as f:
        json.dump({"holds": [{"mod": "Graffiti", "date": "2026-11-18", "said": "stop Graffiti now"},
                             {"mod": "Cauldron", "date": "2026-11-16", "said": "stop the new biome mods work",
                              "design_allowed": {"said": "design only", "date": "2026-11-17"}}]}, f)
    lines = C.import_live(DB, hold_file=hf, concepts=[("Graffiti", TMP, {"coverage_release_granted": {
        "at": "2026-11-17T18:45:12Z"}})], voids_file=os.path.join(TMP, "novoids.jsonl"))
    check(any("look Graffiti window grant:2026-11-17T18:45:12Z" in x for x in lines), "a grant still waiting on its fixes "
                                                                               "imports as an opening balance", lines)
    rev1 = C._q("SELECT v FROM meta WHERE k='rev'", one=True)["v"]
    lines2 = C.import_live(DB, hold_file=hf, concepts=[], voids_file=os.path.join(TMP, "novoids.jsonl"))
    check(C._q("SELECT v FROM meta WHERE k='rev'", one=True)["v"] == rev1, "a second import writes no act (revision "
                                                                           "unchanged)")
    holds = C.mod_holds()
    check(set(holds) == {"Graffiti", "Cauldron"} and holds["Graffiti"]["said"] == "stop Graffiti now",
          "the import holds every mod of the file with his words", holds)
    check(holds["Cauldron"].get("design_allowed", {}).get("said") == "design only", "his design-only words travel")
    check(all("already" in x or "OFF" in x or "voids" in x or "nothing to import" in x for x in lines2),
          "a second import changes nothing", lines2)
    check(C.blocked({"family": "relentless", "unit": "x"}) is not None, "the retired Relentless family is OFF")
    import mod_owner_hold as OH
    os.environ.pop("RM_OWNER_HOLD_FILE", None)
    real_path = OH.PATH
    OH.PATH = hf
    try:
        got = OH.load()
        check(set(got) >= {"Graffiti", "Cauldron"}, "mod_owner_hold.load reads his holds (file and store)", got)
        C.lift_owner("Graffiti", "go on Graffiti", date="2026-11-18", held_said="stop Graffiti now")
        got = OH.load()
        check("Graffiti" not in got and "Cauldron" in got, "a store lift binds at once though the file still holds "
                                                           "the row (the mirror waits for its publish)", list(got))
        OH.lift("Cauldron", "go on Cauldron")
        check("Cauldron" not in OH.load() and "Cauldron" not in OH.load_file(hf), "mod_owner_hold.py lift lifts "
                                                                                   "store and file")
        C.switch("mod:Pyrelands", True, "pipe off")
        check(OH.load()["Pyrelands"].get("control"), "`pipe off <Mod>` reads as a hold to every hold reader")
        os.environ["RM_CONTROL_DB"] = os.path.join(TMP, "gone.db")
        try:
            OH.load()
            check(False, "an unreadable store makes mod_owner_hold.load raise Unreadable")
        except OH.Unreadable:
            check(True, "an unreadable store makes mod_owner_hold.load raise Unreadable")
        finally:
            os.environ["RM_CONTROL_DB"] = DB
    finally:
        OH.PATH = real_path


# ---------------------------------------------------------------- stopping: kill, write-now, the hook

# The trap ignores SIGTERM, so only `pipe stop --kill` ends it. Danger guarded by its 300 s end: a run of this test killed
# before that step left rm-probe-kill1 running for 80 min (2026-11-21), and every later run of this test, on any clone,
# failed to start its fixture under the same unit name. 300 s outlasts the kill step (under 3 s) by far.
TRAP = """#!/bin/bash
trap '' TERM
( trap '' TERM; exec -a rm-probe-child sleep 300 ) &
echo $! > "$1"
for _ in $(seq 1500); do sleep 0.2; done
"""

STUB = r"""
import os, subprocess, sys, time
tool, db, note, calls = sys.argv[1:5]
n = 0
while n < 600:
    n += 1
    time.sleep(0.1)          # one simulated tool call
    t = time.time()          # when this call's hook began (one appended line per call: "<start> <rc>")
    r = subprocess.run([sys.executable, tool, "hook", "--db", db], capture_output=True, text=True)
    fd = os.open(calls, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
    os.write(fd, ("%.6f %d\n" % (t, r.returncode)).encode())
    os.close(fd)
    if r.returncode == 2:
        with open(note, "w") as f:
            f.write("HANDOFF after %d tool calls: %s" % (n, r.stderr))
        sys.exit(0)
"""


def hook_calls(path):
    """-> [(start, rc)] of the stub's complete call lines (a line still being written is skipped)."""
    try:
        with open(path, encoding="ascii") as f:
            return [(float(a), int(b)) for a, b in (ln.split() for ln in f.read().split("\n")[:-1] if ln.strip())]
    except (OSError, ValueError):
        return []


def t_stop():
    # the hook alone: silent with no order, quick
    fresh()
    os.environ["RM_ROLE_UNIT"] = "rm-probe-nobody"
    t0 = time.perf_counter()
    for _ in range(50):
        code, text = C.hook(DB)
    per = (time.perf_counter() - t0) / 50
    os.environ.pop("RM_ROLE_UNIT")
    print("     measured: hook lookup %.2f ms (in-process)" % (per * 1000))
    check(code == 0 and text == "", "the hook is silent when there is no stop order")
    check(per < 0.05, "the hook's lookup is under 50 ms", per)
    t0 = time.monotonic()
    r = subprocess.run([PY, TOOL, "hook", "--db", DB], capture_output=True, text=True,
                       env=dict(os.environ, RM_ROLE_UNIT="rm-probe-nobody"))
    print("     measured: hook as a process %.0f ms" % ((time.monotonic() - t0) * 1000))
    check(r.returncode == 0 and not r.stdout and not r.stderr, "the hook process is silent with no order")
    s = json.loads(C.claude_settings(DB))
    check(s["hooks"]["PostToolUse"][0]["hooks"][0]["command"].endswith("hook --db " + DB),
          "the run's --settings carries the PostToolUse hook")
    if not systemd_ok():
        UNRUN.append("stop --kill / --write-now with real units: no user systemd here")
        return
    trap = os.path.join(TMP, "trap.sh")
    with open(trap, "w") as f:
        f.write(TRAP)
    os.chmod(trap, 0o755)
    pidf = os.path.join(TMP, "child.pid")
    res = C.launch_unit(["--user", "--quiet", "--collect", "--", trap, pidf],
                        spec("rm-probe-kill1", mod="Graffiti", resources=[{"resource": C.LOOK, "win": "wk",
                                                                           "base": 1}]),
                        capture_output=True, text=True, timeout=30)
    check(res.returncode == 0, "the trap fixture starts", res.stderr)
    wait_for(lambda: os.path.exists(pidf) and open(pidf).read().strip(), 5)
    child = int(open(pidf).read().strip())
    main = int(subprocess.run(["systemctl", "--user", "show", "-p", "MainPID", "--value", "rm-probe-kill1"],
                              capture_output=True, text=True).stdout.strip() or 0)
    subprocess.run(["systemctl", "--user", "kill", "--signal=SIGTERM", "--kill-whom=all", "rm-probe-kill1"])
    time.sleep(0.3)
    check(C._alive(child) and C._alive(main), "the fixture and its child ignore SIGTERM")
    t0 = time.monotonic()
    rc, out, el = pipe("stop", "Graffiti", "--kill", "--why", "force kill test")
    lines = [x for x in out.splitlines() if x.strip()]
    print("     measured: pipe stop --kill %.0f ms; %s" % (el * 1000, lines[0][:160] if lines else "-"))
    check(rc == 0 and "dead in" in out and len(lines) <= 3, "pipe stop --kill says dead with its ms (3 lines)", out)
    check(not C._alive(child) and not C._alive(main), "the unit and its child are dead")
    check(el < 3.0 and time.monotonic() - t0 < 3.0, "within the command (well under 3 s with python start)", el)
    check(C.run_state("rm-probe-kill1")["state"] == "killed", "the run reads killed")
    a = C.account("Graffiti", C.LOOK, "wk", 1)
    check(a["held"] == 0 and a["charged"] == 0, "its trial is released", a)
    check(C.blocked(spec("rm-probe-next", mod="Graffiti")) is not None, "new launches on the scope are blocked")
    # --write-now through the hook into a running stub agent
    C.switch("mod:Graffiti", False, "on again")
    stub = os.path.join(TMP, "stub.py")
    with open(stub, "w") as f:
        f.write(STUB)
    note, calls = os.path.join(TMP, "note.txt"), os.path.join(TMP, "calls.txt")
    res = C.launch_unit(["--user", "--quiet", "--collect",
                         "--setenv", "RM_ROLE_UNIT=rm-probe-stub1", "--", PY, stub, TOOL, DB, note, calls],
                        spec("rm-probe-stub1", mod="Graffiti", item="RIMMANDRAKE_PROBE_STOP_CHANNEL_STUB",
                             resources=[{"resource": C.LOOK, "win": "ws", "base": 1}]),
                        capture_output=True, text=True, timeout=30)
    check(res.returncode == 0, "the stub agent starts", res.stderr)
    wait_for(lambda: hook_calls(calls), 5)
    r = C.stop("Graffiti", "write_now", "write-now test", deadline_s=60, escalator=lambda *a: "no timer in test")
    t_order = time.time()   # the order is committed by now: every hook call that starts later must receive it
    check(r["units"] and r["units"][0]["unit"] == "rm-probe-stub1", "the stop order names the live unit", r["units"])
    wait_for(lambda: os.path.exists(note), 10)
    txt = open(note).read() if os.path.exists(note) else ""
    check("STOP ORDER, write now" in txt and "RIMMANDRAKE_PROBE_STOP_CHANNEL_STUB" in txt,
          "the running agent receives the write-now order through its hook, with its item", txt[:200])
    # counted from the order's commit, not from when the test last read a count (the test's own time is not the
    # channel's: RIMMANDRAKE_FIX_STOP_TEST_RACE_EMPTY_READ_COUNTED_ZERO)
    hc = hook_calls(calls)
    missed = [x for x in hc if x[0] >= t_order and x[1] != 2]
    check(hc and hc[-1][1] == 2 and not missed, "the first tool call after the order receives it (%d later call(s) "
          "missed it)" % len(missed), hc[-4:])
    wait_for(lambda: C.run_state("rm-probe-stub1")["state"] == "ended", 10)
    check(C.run_state("rm-probe-stub1")["state"] == "ended", "the unit ended after writing")
    srow = C._q("SELECT * FROM stops WHERE unit='rm-probe-stub1'", one=True)
    check(srow["state"] == "done" and srow["seen_at"], "the stop order reads seen, then done", srow)
    a = C.account("Graffiti", C.LOOK, "ws", 1)
    check(a["held"] == 0 and a["charged"] == 0, "its trial is released", a)
    # the deadline: an agent that ignores the order is killed
    C.switch("mod:Graffiti", False, "on again")
    res = C.launch_unit(["--user", "--quiet", "--collect", "--", "/bin/sleep",
                         "300"], spec("rm-probe-deaf1", mod="Graffiti"), capture_output=True, text=True, timeout=30)
    r = C.stop("Graffiti", "write_now", "deadline test", deadline_s=1)
    check("escalates to --kill" in r["units"][0]["said"] and "timer" in r["units"][0]["said"],
          "--write-now schedules its escalation", r["units"][0]["said"])
    wait_for(lambda: C.run_state("rm-probe-deaf1")["state"] == "killed", 15)
    check(C.run_state("rm-probe-deaf1")["state"] == "killed" and unit_state("rm-probe-deaf1") in ("inactive", "failed",
                                                                                                   ""),
          "past its deadline the order escalates to --kill", C.run_state("rm-probe-deaf1"))
    esc = C._q("SELECT * FROM acts WHERE kind='escalate'", one=True)
    check(esc and "escalated to --kill" in esc["why"], "and says so in an act")
    # emergency: kill by unit name while the store is unreadable
    res = subprocess.run(["systemd-run", "--user", "--quiet", "--collect", "--unit", "rm-probe-emerg1", "/bin/sleep",
                          "300"], capture_output=True, text=True)
    rc, out, _ = pipe("stop", "rm-probe-emerg1", "--kill", "--why", "store down", env={"RM_CONTROL_DB": os.path.join(
        TMP, "nostore.db")})
    check(rc == 0 and "dead in" in out and "STORE UNREADABLE" in out, "pipe stop <unit> --kill works with the store "
                                                                       "unreadable, and says so", out)


def t_stop_review_fixes():
    """Codex review, 2026-11-18: a kill with a survivor is never recorded killed (its clone kept); a stopped run is
    voided in the dispatch books too; `pipe init` in a test process never creates the live store."""
    fresh()
    a = C.admit(spec("rm-detached-probe-survivor-1", mod="Graffiti"))
    C.condition(a["run"])
    reaped = []
    r = C.stop("Graffiti", "kill", "survivor test", killer=lambda us: [
        {"unit": u, "dead": False, "ms": 1000, "survivors": [4242], "said": "SURVIVED: pids [4242]"} for u in us],
        reaper=lambda *x: reaped.append(x) or "reaped")
    check(not r["units"][0]["ok"] and C.run_state(a["run"])["state"] == "started" and not reaped,
          "a kill that leaves a survivor is not recorded killed and its clone is not returned", r["units"])
    vf = os.path.join(TMP, "voids-test.jsonl")
    os.environ["RM_RUN_VOIDS_FILE"] = vf
    try:
        C.switch("mod:Graffiti", False, "on")
        b = C.admit(spec("rm-probe-books-1", mod="Graffiti"))
        C.condition(b["run"])
        C.stop("Graffiti", "at_easy_spot", "books test", escalator=lambda *x: "-")
        import run_void as RV
        check("rm-probe-books-1" in RV.active(vf), "a stopped run is voided in the dispatch books too (voids.jsonl)")
    finally:
        os.environ.pop("RM_RUN_VOIDS_FILE", None)
    env = {k: v for k, v in os.environ.items() if k != "RM_CONTROL_DB"}
    env["RM_UNDER_SELFTEST"] = "1"
    r2 = subprocess.run([PY, TOOL, "init"], capture_output=True, text=True, env=env, timeout=30)
    check(r2.returncode == 0 and C.DEFAULT_DB not in r2.stdout and "rm-control-selftest" in r2.stdout,
          "pipe init in a test process makes a test store, never the live one", r2.stdout)


def t_kill_bookkeeping():
    """A killed detached run: its record is finished/killed at once and its clone is not held, so a relaunch needs no
    hand step (the Conductor measured 2026-11-18 11:30 AM PST that a bare SIGKILL left both)."""
    import detached_helper as DH
    st = os.path.join(TMP, "dstate")
    os.makedirs(os.path.join(st, "detached"), exist_ok=True)
    os.environ["RM_DISPATCHER_STATE"] = st
    clone = os.path.join(TMP, "pool", "clones", "RIMMANDRAKE_PROBE_KILL_BOOKKEEPING.det")
    os.makedirs(clone, exist_ok=True)
    unit = "rm-detached-bench-probe-kill-bookkeeping-1"
    rec = {"unit": unit, "seat": "BENCH", "item": "RIMMANDRAKE_PROBE_KILL_BOOKKEEPING", "clone": clone,
           "model": "opus", "at": time.time() - 60, "state": st, "status": "running", "clone_how": "given " + clone,
           "out": os.path.join(st, "detached", unit + ".out.json"), "err": os.path.join(st, "detached", unit + ".err")}
    DH.write_record(rec, st)
    held = DH.clone_holders(clone, now=time.time(), root=st)
    check(held and not held[0][1], "base: a killed run's record left running holds its clone hard (the measured "
                                   "defect)", held)
    msg = DH.mark_killed(unit, "killed by pipe stop --kill (test)")
    r2 = DH.read_record(unit, st)
    check(r2["status"] == "finished" and str(r2["result"]).startswith("killed") and r2.get("finish_owed"),
          "mark_killed records it finished/killed with its finish owed", (msg, r2.get("status"), r2.get("result")))
    held = DH.clone_holders(clone, now=time.time(), root=st)
    check(not [h for h in held if not h[1]], "the clone is no longer held hard: a relaunch waits for the return at most",
          held)
    os.environ.pop("RM_DISPATCHER_STATE", None)


def t_coverage_look():
    """The owner-granted coverage look through coverage_judge: reserved before the judge runs, one of two racing judges
    gets it, a run with no valid verdict releases it (fail_system, metered), a valid one charges it, a grant adds one."""
    fresh()
    import coverage_judge as CJ
    d = os.path.join(TMP, "looks", "ModLook")
    os.makedirs(d)
    win = "grant:2026-11-17T18:45:12Z"
    with open(os.path.join(d, "stage.json"), "w") as f:
        json.dump({"mod": "ModLook", "stage": "designer", "coverage_rounds": [],
                   "coverage_releases": [{"at": "2026-11-18T10:00:00Z", "rounds_at": 0, "judges_at": [],
                                          "granted_at": win[6:]}]}, f)
    a, b = CJ.reserve_look(d, "rm-coverage-judge-a"), CJ.reserve_look(d, "rm-coverage-judge-b")
    check(a["ok"] and not b["ok"] and "none available" in b["why"], "two judges for one granted look: one reserves",
          (a, b))
    CJ.settle_look(a, None, "no answer file")
    acc = C.account("ModLook", C.LOOK, win, 1)
    check(acc["held"] == 0 and acc["charged"] == 0 and C.faults("ModLook") == 1, "a judge with no valid verdict "
                                                                                 "releases the look as a system fault",
          acc)
    c = CJ.reserve_look(d, "rm-coverage-judge-c")
    CJ.settle_look(c, {"verdict": "not_covered", "error": None}, "ok")
    check(C._q("SELECT state FROM reservations WHERE run='rm-coverage-judge-c'", one=True)["state"] == "charged",
          "a valid verdict charges the look at settlement")
    check(C.look_window({"coverage_release_granted": {"at": win[6:]}}) == win, "a grant still waiting on its fixes keys "
                                                                           "the same window as its release")
    C.grant("ModLook", C.LOOK, 1, "his exception", win=win, owner_said="one more")
    check(CJ.look_balance(CJ.DS.load_state(d), d)["lim"] == 2, "a pipe grant adds one to the look's limit")
    e1, e2 = CJ.reserve_look(d, "rm-coverage-judge-e"), CJ.reserve_look(d, "rm-coverage-judge-f")
    check(e1["ok"] and not e2["ok"], "a grant of one adds exactly one look, never two (it is counted once)", (e1, e2))
    CJ.settle_look(e1, {"verdict": "covered", "error": None}, "ok")
    g = CJ.reserve_look(d, "rm-coverage-judge-g")
    check(not g["ok"], "a look charged on a covered verdict stays spent though no refusal round shows it", g)


# ---------------------------------------------------------------- every launch site is routed; a mutant is caught

def t_sites():
    sites = C.call_sites()
    bad = [s for s in sites if not s["routed"]]
    check({"rimflow/control.py", "rimflow/detached_helper.py"} <= {s["file"] for s in sites},
          "the census sees the systemd-run literals left (control.py's own, a run's return step)", sites)
    check(not bad, "every systemd-run call site goes through control.launch_unit",
          ["%s:%s:%d %s" % (s["file"], s["func"], s["line"], s["why"]) for s in bad])
    root = os.path.join(TMP, "mutant", "rimflow")
    os.makedirs(root)
    with open(os.path.join(root, "sneaky.py"), "w") as f:
        f.write("import subprocess\n\ndef go():\n    subprocess.run(['systemd-run', '--user', '--unit', 'x', 'true'])\n")
    m = C.call_sites(os.path.dirname(root))
    check([s for s in m if not s["routed"] and s["func"] == "go"], "a mutant launcher that bypasses launch_unit "
                                                                    "turns the census red", m)
    # round-two claim 8: only launch_unit writes `systemd-run`, so a literal is unrouted even beside or inside a call
    with open(os.path.join(root, "mixed.py"), "w") as f:
        f.write("import subprocess\nimport control as C\n\ndef go2():\n"
                "    C.launch_unit(['systemd-run', '--user', '--unit', 'rm-probe-a', 'true'], {'family': 'probe'})\n"
                "    argv = ['systemd-run', '--user', '--unit', 'rm-probe-b', 'true']\n"
                "    subprocess.run(argv)\n"
                "    subprocess.Popen(['systemd-run', '--user', '--unit', 'rm-probe-c', 'true'])\n\n"
                "def go3():\n    C.launch_unit(['true'], {'family': 'probe'})\n"
                "    return ['systemd-run', '--user', 'x']\n")
    m = {(s["func"], s["line"]): s for s in C.call_sites(os.path.dirname(root)) if s["file"] == "rimflow/mixed.py"}
    check(len(m) == 4 and not any(v["routed"] for v in m.values()),
          "claim r2-8: every systemd-run literal outside control.py is unrouted, the one handed to launch_unit too",
          {k: (v["routed"], v["why"]) for k, v in m.items()})
    os.unlink(os.path.join(root, "mixed.py"))
    with open(os.path.join(root, "detached_helper.py"), "w") as f:
        f.write("def launch_argv(rec):\n    return ['systemd-run', '--user', 'x']\n\n"
                "def bad(runner):\n    runner(launch_argv({}))\n")
    m = C.call_sites(os.path.dirname(root))
    check([s for s in m if not s["routed"] and s["func"] == "launch_argv"], "a builder called outside launch_unit "
                                                                            "turns it red", m)


def t_void_books_by_run_id():
    """RIMMANDRAKE_BOOK_PIPE_VOID_BY_UNIT_NOT_RUN_ID (Codex review 2026-11-18): `pipe void <run id>` gives back the
    store's reservations by id or unit, and the dispatch books must learn the UNIT (their runs are units), with the
    Conductor's route recorded beside it."""
    fresh()
    import types
    import run_void as RV
    vf = os.path.join(TMP, "voids-byid.jsonl")
    os.environ["RM_RUN_VOIDS_FILE"] = vf
    try:
        C.switch("mod:Graffiti", False, "on")
        a = C.admit(spec("rm-probe-books-2", mod="Graffiti"))
        o = types.SimpleNamespace(run=a["run"], why="books by id", mod=None, owner_said=None,
                                  per_ruling="CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM", idem=None)
        C.cmd_void(o)
        act = RV.active(vf)
        rows = [json.loads(x) for x in open(vf, encoding="utf-8")] if os.path.exists(vf) else []
        check(a["run"] != "rm-probe-books-2" and "rm-probe-books-2" in act and a["run"] not in act,
              "pipe void <run id> books the run's unit in voids.jsonl, not its id", sorted(act))
        check(any(r.get("per_ruling") == "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM" for r in rows),
              "the dispatch books record the Conductor's route", rows)
    finally:
        os.environ.pop("RM_RUN_VOIDS_FILE", None)


def t_hooks_in_run_clone():
    """RIMMANDRAKE_POINT_CONTROL_HOOKS_AT_RUN_CLONE_LAUNCHER_DELETED: a continuation is launched from the PREVIOUS run's
    clone, which its return then deletes, so a hook path taken from the launcher's own control.py is dead for the whole
    new run (stop channel, start check and end receipt; measured 2026-11-18 on a live unit). The hooks name the RUN's
    clone's control.py when it has one, and the launcher's only when it has none."""
    fresh()
    import types
    rc = os.path.join(TMP, "runclone")     # its rimflow is this one, by a link: the hook really runs from it
    mine = os.path.join(rc, "src", "RimMandrake", "rimflow", "control.py")
    os.makedirs(os.path.dirname(os.path.dirname(mine)))
    os.symlink(HERE, os.path.dirname(mine))
    cmd = json.loads(C.claude_settings(DB, clone=rc))["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
    check(mine in cmd and cmd.endswith("hook --db " + DB), "the PostToolUse hook runs the run clone's control.py", cmd)
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30,
                       env=dict(os.environ, RM_ROLE_UNIT="rm-probe-nobody"))
    check(r.returncode == 0 and not r.stdout and not r.stderr, "that hook command runs, silent with no stop order",
          (r.returncode, r.stdout[-200:], r.stderr[-200:]))
    bare = json.loads(C.claude_settings(DB, clone=os.path.join(TMP, "noclone")))["hooks"]["PostToolUse"][0]
    check(os.path.abspath(C.__file__) in bare["hooks"][0]["command"],
          "a clone without control.py falls back to the launcher's own", bare)
    got = []

    def runner(argv, **k):
        got.append(list(argv))
        return types.SimpleNamespace(returncode=0, stdout="", stderr="", args=argv)
    C.launch_unit(["--user", "--", "true"], spec("rm-probe-hookclone"),
                  runner=runner, p=DB, clone=rc)
    props = [a for a in (got[0] if got else []) if a.startswith(("ExecCondition=", "ExecStopPost="))]
    check(len(props) == 2 and all(mine in a for a in props), "the unit's start check and end receipt run the run "
          "clone's control.py", props)
    import detached_helper as DH
    import role_launch as RL
    for name, f, arg in (("detached_helper", DH._control_settings, {"clone": rc}),
                         ("role_launch", RL._control_settings, {"clone": rc})):
        try:
            s = f(arg)
        except TypeError as e:
            s = "TypeError: %s" % e
        check(mine in s, "%s's run carries its own clone's hook" % name, s[:160])
    for name, mod in (("detached_helper", DH), ("role_launch", RL)):
        src = open(mod.__file__, encoding="utf-8").read()
        call = src[src.index("C.launch_unit(launch_argv("):][:400]
        want = 'clone=%s.get("clone")' % ("rec" if name == "detached_helper" else "role")
        check(want in call, "%s passes its run's clone to launch_unit (%s)" % (name, want), call[:200])
    # the stop order's escalation timer: written by whoever ran `pipe stop` (a helper in a pool clone, often), fired
    # at the deadline: it falls through to a seat clone's control.py when the writer's clone is gone
    got = []
    os.environ["RM_WRAPUP_SEAT_CLONES"] = rc        # the seat clone of this test: the link above
    try:
        C.schedule_escalation("rm-probe-esc", 60, DB,
                              runner=lambda argv, **k: got.append(list(argv)) or types.SimpleNamespace(returncode=0))
    finally:
        os.environ.pop("RM_WRAPUP_SEAT_CLONES")
    argv = got[0] if got else []
    i = argv.index("--timer-property=AccuracySec=1s") + 1 if "--timer-property=AccuracySec=1s" in argv else len(argv)
    own = os.path.abspath(C.__file__)
    tail = argv[i:]
    seat = os.path.join(os.path.realpath(rc), "src", "RimMandrake", "rimflow", "control.py")
    check(own in tail and seat in tail[tail.index(own) + 1:] if own in tail else False,
          "the escalation timer names a seat clone's control.py after the writer's own", tail[:6])
    gone = os.path.join(TMP, "gone", "control.py")
    if own in tail:
        # a hook prints nothing (its line goes to the journal): exit 0 against this store is escalate having run;
        # the resolver with no script left exits 1 and names the candidates
        r = subprocess.run([gone if x == own else x for x in tail], capture_output=True, text=True, timeout=30)
        check(r.returncode == 0 and not r.stderr, "with the writer's clone gone the timer still runs escalate",
              (r.returncode, r.stderr[-200:]))
        r = subprocess.run([x for x in tail if x not in (own, seat)][:3] + [gone] +
                           tail[tail.index("--"):], capture_output=True, text=True, timeout=30)
        check(r.returncode != 0 and "no stop-step script" in r.stderr, "control: with no control.py left it fails "
              "loudly, naming the candidates", (r.returncode, r.stderr[-200:]))

def t_review_claims_eight():
    """The eight Codex claims on control.py (RIMMANDRAKE_SPLIT_CONTROL_STORE_REVIEW_CLAIMS_EIGHT_UNTRIED), each a red
    case on the base it was filed against; claim 4 did not reproduce and is kept as a guard with a real unit."""
    fresh()
    real_sc, real_alarm = C._systemctl, C._fault_alarm
    # 1. a failed `systemctl show` is "could not look", never "nothing was running"
    C._systemctl = lambda args, timeout=10: (1, "Failed to connect to bus: No such file or directory")
    try:
        res = C.kill_units(["rm-probe-claim1"], wait_s=0)
    finally:
        C._systemctl = real_sc
    check(res[0]["dead"] is None and "nothing was running" not in res[0]["said"] and "UNVERIFIED" in res[0]["said"],
          "claim 1: a failed cgroup read is death UNVERIFIED, never nothing was running", res)
    # 2. an emergency kill (store unreadable) still finds the run's claude scope by its name
    calls = []
    C._systemctl = lambda args, timeout=10: (0, "claude-seat-BENCH-rm-role-probe-claim2.scope loaded active running x\n"
                                             if args[0] == "list-units" else "")
    try:
        r = C.stop("rm-role-probe-claim2", "kill", "claim 2", p=os.path.join(TMP, "nostore.db"),
                   killer=lambda us: calls.append(list(us)) or [
                       {"unit": u, "dead": True, "ms": 1, "survivors": [], "said": "1 process(es) killed"} for u in us])
    finally:
        C._systemctl = real_sc
    check(calls and "claude-seat-BENCH-rm-role-probe-claim2.scope" in calls[0] and not r["store"],
          "claim 2: an emergency kill with the store unreadable kills the run's claude scope too", calls)
    C._systemctl = lambda args, timeout=10: (1, "Failed to connect to bus") if args[0] == "list-units" else (0, "")
    try:
        r = C.stop("rm-role-probe-claim2b", "kill", "claim 2b", p=os.path.join(TMP, "nostore.db"),
                   killer=lambda us: [{"unit": u, "dead": None, "ms": 1, "survivors": [],
                                       "said": "nothing was running in it"} for u in us])
    finally:
        C._systemctl = real_sc
    check(not r["units"][0]["ok"] and "UNVERIFIED" in r["units"][0]["said"],
          "claim 2: a claude scope that cannot be listed leaves the kill UNVERIFIED, never ok", r["units"])
    # 3. a unit-targeted stop fences an admitted (unstarted) run: its later start check refuses it
    fresh()
    a = C.admit(spec("rm-probe-claim3", mod="Graffiti", resources=[{"resource": C.LOOK, "win": "w3", "base": 1}]))
    C.stop("rm-probe-claim3", "kill", "claim 3", killer=lambda us: [
        {"unit": u, "dead": None, "ms": 1, "survivors": [], "said": "nothing was running in it"} for u in us],
        reaper=lambda *x: "-")
    code, line = C.condition(a["run"])
    check(code == 1 and C.account("Graffiti", C.LOOK, "w3", 1)["held"] == 0,
          "claim 3: after `pipe stop <unit> --kill` an admitted run's unit is refused at start, its trial released",
          (code, line))
    # 5. a failed launch with a reservation can be admitted again under its name
    fresh()
    sp = spec("rm-probe-claim5", mod="Graffiti", resources=[{"resource": C.LOOK, "win": "w5", "base": 2}])
    a = C.admit(sp)
    C._mark(a["run"], "fail_launch", "claim 5", fault=True)
    try:
        b = C.admit(sp)
        got = b["ok"]
    except C.Unreadable as e:
        got = "Unreadable: %s" % e
    check(got is True and C.account("Graffiti", C.LOOK, "w5", 2)["held"] == 1,
          "claim 5: a fail_launch run with a released reservation is re-admitted (not an unreadable store)", got)
    # 6. escalate acts only on an order whose deadline has passed, and names that order
    fresh()
    a = C.admit(spec("rm-probe-claim6", mod="Graffiti"))
    C.condition(a["run"])
    t0 = time.time()
    C.stop("rm-probe-claim6", "write_now", "claim 6 first", deadline_s=60, now=t0, escalator=lambda *x: "-")
    C.stop("rm-probe-claim6", "at_easy_spot", "claim 6 second", now=t0 + 1, escalator=lambda *x: "-")
    killed = []
    kill_ok = lambda us: killed.append(us) or [{"unit": u, "dead": True, "ms": 1, "survivors": [], "said": "killed"}
                                               for u in us]
    early = C.escalate("rm-probe-claim6", now=t0 + 10, killer=kill_ok, reaper=lambda *x: "-")
    check(not killed and "ESCALATED" not in early, "claim 6: an escalation before any order's deadline kills nothing",
          early)
    C.escalate("rm-probe-claim6", now=t0 + 61, killer=kill_ok, reaper=lambda *x: "-")
    rows = {r["why"]: r["state"] for r in C._q("SELECT why, state FROM stops WHERE unit='rm-probe-claim6'")}
    check(killed and rows.get("claim 6 first") == "escalated" and rows.get("claim 6 second") != "escalated",
          "claim 6: the escalation names the order whose deadline passed, not the newest", rows)
    # 7. every fault-metered release sounds the fault alarm (_mark fault=True, _reap)
    fresh()
    alarms = []

    def spy(run, p=None):   # through its own connection, as the real alarm reads: only a committed fault counts
        if C._q("SELECT COUNT(*) n FROM faults WHERE run=?", (run,), p, one=True)["n"]:
            alarms.append(run)
    C._fault_alarm = spy
    try:
        a = C.admit(spec("rm-probe-claim7", mod="Graffiti", resources=[{"resource": C.LOOK, "win": "w7", "base": 3}]))
        C._mark(a["run"], "fail_launch", "claim 7", fault=True)
        check(a["run"] in alarms, "claim 7: _mark(fault=True) sounds the fault alarm", alarms)
        dead = subprocess.Popen([PY, "-c", "pass"])
        dead.wait()
        C.reserve("Graffiti", C.LOOK, "run_claim7_holder", win="w7", base=3, pid=dead.pid)
        C.reserve("Graffiti", C.LOOK, "run_claim7_next", win="w7", base=3)
        check("run_claim7_holder" in alarms, "claim 7: _reap (a dead holder's look released) sounds the fault alarm",
              alarms)
        C.switch("mod:Graffiti", False, "on")
        b = C.admit(spec("rm-probe-claim7-stop", mod="Graffiti", resources=[{"resource": C.LOOK, "win": "w7b",
                                                                            "base": 1}]))
        C.condition(b["run"])
        C.stop("rm-probe-claim7-stop", "at_easy_spot", "claim 7 stop", escalator=lambda *x: "-")
        check(b["run"] in alarms, "claim 7: a stop that releases a live run's trial as a fault sounds the alarm", alarms)
    finally:
        C._fault_alarm = real_alarm
    # 8. a unit skipped at its start check (store unreadable) and then ended is not left admitted
    fresh()
    a = C.admit(spec("rm-probe-claim8", mod="Graffiti", resources=[{"resource": C.LOOK, "win": "w8", "base": 1}]))
    code, _ = C.condition(a["run"], p=os.path.join(TMP, "nostore.db"))
    C.ended(a["run"], "success/exited/0")
    C.ended(a["run"], "success/exited/0")
    st = C.run_state(a["run"])["state"]
    nf = C._q("SELECT COUNT(*) n FROM faults WHERE run=?", (a["run"],), one=True)["n"]
    check(code == 2 and st == "refused" and C.account("Graffiti", C.LOOK, "w8", 1)["held"] == 0 and nf == 1,
          "claim 8: a unit skipped unreadable then ended reads refused, its trial released as one fault (twice ended: "
          "still one)", (code, st, nf))
    # a unit-targeted cooperative stop of a run that had not started: cancelled, and no order or timer is left for it
    fresh()
    a = C.admit(spec("rm-probe-claim3b", mod="Graffiti"))
    timers = []
    r = C.stop("rm-probe-claim3b", "write_now", "claim 3b", deadline_s=60, escalator=lambda *x: timers.append(x) or "-")
    left = C._q("SELECT * FROM stops WHERE unit='rm-probe-claim3b' AND state IN ('pending','seen')")
    check(r["cancelled"] == ["rm-probe-claim3b"] and not left and not timers,
          "a write-now stop of an unstarted run cancels it and leaves no order or escalation timer", (r, left, timers))
    # a run recorded killed finishes its earlier stop orders (an escalation timer then finds nothing to do)
    fresh()
    a = C.admit(spec("rm-probe-claim6b", mod="Graffiti"))
    C.condition(a["run"])
    C.stop("rm-probe-claim6b", "write_now", "claim 6b order", deadline_s=60, escalator=lambda *x: "-")
    C.stop("rm-probe-claim6b", "kill", "claim 6b kill", killer=kill_ok, reaper=lambda *x: "-")
    left = C._q("SELECT * FROM stops WHERE unit='rm-probe-claim6b' AND state IN ('pending','seen')")
    check(C.run_state(a["run"])["state"] == "killed" and not left,
          "a run recorded killed leaves no pending stop order behind", left)
    # 4 (not reproduced; kept as a guard): re-admitting an ambiguous admission while its old unit is still queued:
    # systemd refuses the second transient unit under that name, so the new admission is fail_launch and the old unit's
    # start check refuses it; the old payload never runs on the new admission
    if not systemd_ok():
        UNRUN.append("claim 4 guard with a queued real unit: no user systemd here")
        return
    fresh()
    u = "rm-probe-claim4-%d" % os.getpid()
    marker = os.path.join(TMP, "claim4.ran")
    argv = ["--user", "--quiet", "--collect", "--on-active=2",
            "--timer-property=AccuracySec=1s", "--", "/usr/bin/touch", marker]   # the default accuracy is a minute
    r1 = C.launch_unit(argv, spec(u, mod="Graffiti"), capture_output=True, text=True, timeout=30)
    r2 = C.launch_unit(argv, spec(u, mod="Cauldron"), capture_output=True, text=True, timeout=30)
    fired = wait_for(lambda: unit_state(u + ".timer") in ("inactive", "failed", ""), 10)
    done = wait_for(lambda: unit_state(u) in ("inactive", "failed", ""), 10)
    row = C.run_state(u)
    check(r1.returncode == 0 and r2.returncode != 0 and fired and done and not os.path.exists(marker)
          and row["state"] == "fail_launch" and not row["started_at"],
          "claim 4 guard: the old queued unit's payload never runs on the re-admission",
          (r1.returncode, r2.returncode, fired, done, os.path.exists(marker), dict(row)))


def t_review_claims_round_two():
    """Codex's round-two claims on control.py (RIMMANDRAKE_SPLIT_CONTROL_REVIEW_ROUND_TWO_NINE_UNTRIED), each red on base
    19d3e29026 (D:\\ClaudeWork\\scratch\\control_claims_round2_20261118\\probe_base.log). Claims 8 and 9 sit in t_sites and
    t_verbs. Children: RIMMANDRAKE_FENCE_LAUNCH_IDENTITY_ONE_ID_TWO_PAYLOADS (1, 2),
    RIMMANDRAKE_HARDEN_EMERGENCY_KILL_LOCK_FORK_AND_END_RACE (3, 4, 5), RIMMANDRAKE_KEEP_STOP_DEADLINES_TWO_TIMERS_ONE_NAME
    (6, 7)."""
    dead = lambda us: [{"unit": u, "dead": True, "ms": 1, "survivors": [], "said": "1 process(es) killed"} for u in us]
    # 1. two admissions of one unit in one process: the first one's unit never starts on the second's admission
    fresh()
    a = C.admit(spec("rm-probe-r2c1", mod="Graffiti"))
    b = C.admit(spec("rm-probe-r2c1", mod="Cauldron"))
    C.switch("mod:Graffiti", True, "round two claim 1")
    code, line = C.condition(a["run"])
    check(b["ok"] and a["run"] != b["run"] and code == 1,
          "claim r2-1: a re-admission gets its own run id; the replaced admission's unit is refused at start",
          (a["run"], b["run"], code, line))
    check(C.condition(b["run"])[0] == 0, "claim r2-1: the re-admission's own unit starts on its own admission")
    fresh()
    s = spec("rm-probe-r2c1b", mod="Graffiti", resources=[{"resource": C.LOOK, "win": "w", "base": 9}])
    for _ in range(3):
        r = C.admit(s)
        C._mark(r["run"], "fail_launch", "round two claim 1b", fault=True)
    check(C.faults("Graffiti") == 3, "claim r2-1: three failed launches under one name meter three faults",
          C.faults("Graffiti"))
    check(C.account("Graffiti", C.LOOK, "w", 9)["held"] == 0, "claim r2-1: no failed attempt keeps its reservation held")
    # 2. the unit launched is the unit admitted
    fresh()
    seen = []

    def runner(argv, **kw):
        seen.append(list(argv))
        return subprocess.CompletedProcess(argv, 0, "", "")
    C.launch_unit(["--user", "--", "/bin/true"], spec("rm-probe-r2c2"), runner=runner)
    sent = seen[0] if seen else []
    check(sent[sent.index("--") - 6:sent.index("--") - 4] == ["--unit", "rm-probe-r2c2"] if "--" in sent else False,
          "claim r2-2: the spec's unit is the last --unit among systemd-run's options", sent)
    seen.clear()
    r = C.launch_unit(["systemd-run", "--user", "--unit", "rm-probe-r2c2-other", "/bin/true"], spec("rm-probe-r2c2b"),
                      runner=runner)
    check(not seen and r.refused and r.returncode == C.LAUNCH_REFUSED_RC and "launch-through-one-door" in r.stderr,
          "launch-through-one-door: a systemd-run line of the caller's own is refused by name, never run",
          (seen, r.stderr))
    r = C.launch_unit(["--user", "/bin/true"], spec("rm-probe-r2c2c"), runner=runner)
    check(not seen and r.refused and "--" in r.stderr, "launch-through-one-door: a launch with no `--` before its "
                                                       "payload is refused by name, never run", (seen, r.stderr))
    r = C.launch_unit(["--user", "--", "/bin/true"], spec("rm-probe-dollar"), runner=runner,
                      p=os.path.join(TMP, "${HOME}", "control.db"))
    check(not seen and r.refused and "plain-paths" in r.stderr, "plain-paths: a store path with $ is refused by name "
                                                                "before admission, never run", (seen, r.stderr))
    # 3. an emergency kill on a locked store kills at once and records the kill when the store frees
    fresh()
    a = C.admit(spec("rm-probe-r2c3", mod="Graffiti"))
    C.condition(a["run"])
    locked = threading.Event()

    def holder():   # another writer holds the store for 1.2 s
        hold = C.connect(DB)
        hold.execute("BEGIN IMMEDIATE")
        locked.set()
        time.sleep(1.2)
        hold.execute("ROLLBACK")
        hold.close()
    th = threading.Thread(target=holder)
    killed_at = []
    th.start()
    locked.wait(5)
    t0 = time.monotonic()
    try:
        r = C.stop("rm-probe-r2c3", "kill", "round two claim 3",
                   killer=lambda us: killed_at.append(time.monotonic() - t0) or dead(us), reaper=lambda *x: "-")
    finally:
        th.join()
    st = C.run_state(a["run"])["state"]
    check(killed_at and killed_at[0] < 1.0, "claim r2-3: a unit kill on a locked store kills within 1 s", killed_at)
    check(st == "killed" and r["units"][0]["ok"], "claim r2-3: the kill is recorded once the store frees", (st, r))
    # 4. a process that entered the cgroup after the snapshot, when systemctl's kill failed: killed or a survivor
    p1 = subprocess.Popen(["sleep", "300"])
    p2 = subprocess.Popen(["sleep", "300"])
    real_cg, real_sc, real_procs = C._cgroup_pids, C._systemctl, getattr(C, "_procs", None)
    C._cgroup_pids = lambda u: (P.value([p1.pid]), "probe.slice/rm-probe-r2c4.service")
    C._procs = lambda cg: P.value([x for x in (p1.pid, p2.pid) if C._alive(x)])
    C._systemctl = lambda args, timeout=10: (1, "Failed to kill unit: timeout") if args[0] == "kill" else (0, "")
    try:
        res = C.kill_units(["rm-probe-r2c4"], wait_s=0.5)
    finally:
        C._cgroup_pids, C._systemctl = real_cg, real_sc
        if real_procs is None:
            del C._procs
        else:
            C._procs = real_procs
    time.sleep(0.05)
    alive2 = p2.poll() is None
    for x in (p1, p2):
        x.kill()
        x.wait(5)
    check(not (res[0]["dead"] is True and alive2),
          "claim r2-4: a late cgroup member after a failed systemctl kill is killed or named, never 'dead'",
          (res, alive2))
    # 5. an end receipt landing while the kill verifies: still killed
    fresh()
    a = C.admit(spec("rm-probe-r2c5", mod="Graffiti"))
    C.condition(a["run"])
    C.stop("rm-probe-r2c5", "kill", "round two claim 5", killer=lambda us: C.ended(a["run"], "signal/KILL/9") and dead(us),
           reaper=lambda *x: "-")
    check(C.run_state(a["run"])["state"] == "killed", "claim r2-5: an end receipt during the kill's verify reads killed",
          C.run_state(a["run"])["state"])
    a = C.admit(spec("rm-probe-r2c5b", mod="Graffiti"))
    C.condition(a["run"])
    C.stop("rm-probe-r2c5b", "kill", "nothing running", killer=lambda us: C.ended(a["run"], "success/exited/0") and [
        {"unit": u, "dead": None, "ms": 1, "survivors": [], "said": "nothing was running in it"} for u in us],
        reaper=lambda *x: "-")
    check(C.run_state(a["run"])["state"] == "ended", "claim r2-5: a run that ended on its own (nothing killed) stays ended",
          C.run_state(a["run"])["state"])
    # 6. two deadlines on one unit: two timers; a timer not set reads not ok
    fresh()
    a = C.admit(spec("rm-probe-r2c6", mod="Graffiti"))
    C.condition(a["run"])
    loaded = []

    def trunner(argv, **kw):
        n = argv[argv.index("--unit") + 1]
        if n in loaded:
            return subprocess.CompletedProcess(argv, 1, "", "Unit %s.timer already exists." % n)
        loaded.append(n)
        return subprocess.CompletedProcess(argv, 0, "", "")
    esc = lambda *x: C.schedule_escalation(*x, runner=trunner)
    C.stop("rm-probe-r2c6", "write_now", "one hour", deadline_s=3600, escalator=esc)
    C.stop("rm-probe-r2c6", "write_now", "five s", deadline_s=5, escalator=esc)
    check(len(set(loaded)) == 2, "claim r2-6: two deadlines on one unit set two escalation timers", loaded)
    r = C.stop("rm-probe-r2c6", "write_now", "not set", deadline_s=5,
               escalator=lambda *x: "escalation timer NOT set (exit 1: probe)")
    check(not r["units"][0]["ok"], "claim r2-6: a stop whose escalation timer was not set is not ok", r["units"])
    # 7. pipe stop --idem: a replay writes nothing
    fresh()
    a = C.admit(spec("rm-probe-r2c7", mod="Graffiti"))
    C.condition(a["run"])
    real_esc = C.schedule_escalation
    C.schedule_escalation = lambda *x, **k: "-"
    outs = []
    try:
        for _ in range(2):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = C.main(["stop", "rm-probe-r2c7", "--write-now", "--why", "round two claim 7", "--idem", "k-r2c7"])
            outs.append((rc, buf.getvalue()))
    finally:
        C.schedule_escalation = real_esc
    n = C._q("SELECT COUNT(*) n FROM stops WHERE unit='rm-probe-r2c7'", one=True)["n"]
    m = C._q("SELECT COUNT(*) n FROM acts WHERE kind='stop'", one=True)["n"]
    check(n == 1 and m == 1 and outs[1][0] == 0 and "already" in outs[1][1],
          "claim r2-7: a second pipe stop with the same --idem writes no order and no act, and says so", (n, m, outs))


def t_review_claims_round_three():
    """Codex's round-three claims on the round-two fix (RIMMANDRAKE_SPLIT_CONTROL_REVIEW_ROUND_THREE_ELEVEN_UNTRIED),
    each red on origin/main 0117263ccf (D:\\ClaudeWork\\scratch\\control_claims_round2_20261118\\probe3_base.log).
    Children: RIMMANDRAKE_KEEP_FIRST_ADMISSION_ON_REFUSED_REPLACEMENT_ID_REUSE (1, 6),
    RIMMANDRAKE_BOOK_LOCKED_KILLS_BY_RUN_TIMERS_REAP_TWICE (2, 3, 4, 5, 8, 9),
    RIMMANDRAKE_TRACE_CENSUS_ALIASES_HALF_SECOND_READ_AS_ZERO (7, 10, 11)."""
    dead = lambda us: [{"unit": u, "dead": True, "ms": 1, "survivors": [], "said": "1 process(es) killed"} for u in us]
    noreap = lambda *x: "-"

    def started(unit, **kw):
        a = C.admit(spec(unit, **kw))
        C.condition(a["run"])
        return a

    def lock_for(sec):
        ev = threading.Event()

        def holder():
            h = C.connect(DB)
            h.execute("BEGIN IMMEDIATE")
            ev.set()
            time.sleep(sec)
            h.execute("ROLLBACK")
            h.close()
        th = threading.Thread(target=holder)
        th.start()
        ev.wait(5)
        return th
    # 1. a re-admission refused on a resource keeps the first admission; a replacement frees the old held look
    fresh()
    a = C.admit(spec("rm-probe-r3c1"))
    b = C.admit(spec("rm-probe-r3c1", mod="Graffiti", resources=[{"resource": C.LOOK, "win": "w", "base": 0}]))
    c = C.admit(spec("rm-probe-r3c1"))
    check(not b["ok"] and c["ok"] and c["run"] != a["run"] and C.condition(a["run"])[0] == 1,
          "claim r3-1: a refused re-admission leaves the first in place; the next replacement still gets its own id",
          (a["run"], b, c))
    fresh()
    s1 = spec("rm-probe-r3c1b", mod="Graffiti", resources=[{"resource": C.LOOK, "win": "w", "base": 1}])
    a = C.admit(s1)
    b = C.admit(s1)
    check(b["ok"] and C.account("Graffiti", C.LOOK, "w", 1)["held"] == 1 and C.condition(a["run"])[0] == 1,
          "claim r3-1: a replacement takes the last look its own first try held, releases that try's, and fences it",
          (b, C.account("Graffiti", C.LOOK, "w", 1)))
    # 6. a payload's own --unit is the payload's; the spec's unit goes into systemd-run's options
    fresh()
    seen = []
    runner = lambda argv, **kw: seen.append(list(argv)) or subprocess.CompletedProcess(argv, 0, "", "")
    r = C.launch_unit(["--user", "--", "/bin/echo", "--unit", "payload"], spec("rm-probe-r3c6"), runner=runner)
    sent = seen[0] if seen else []
    cmd = sent.index("/bin/echo") if "/bin/echo" in sent else -1
    check(not r.refused and "rm-probe-r3c6" in sent and 0 < sent.index("rm-probe-r3c6") < cmd
          and sent[cmd:] == ["/bin/echo", "--unit", "payload"],
          "claim r3-6: a payload --unit is not systemd-run's; the spec's unit goes before the command", sent)
    # 2. a locked emergency kill whose run ended first books that run (void, killed), not a stand-in
    fresh()
    a = started("rm-probe-r3c2", mod="Graffiti", resources=[{"resource": C.LOOK, "win": "w", "base": 1}])
    th = lock_for(1.0)
    try:
        C.stop("rm-probe-r3c2", "kill", "claim r3-2", killer=lambda us: C.ended(a["run"], "signal/KILL/9") and dead(us),
               reaper=noreap)
    finally:
        th.join()
    v = C._q("SELECT COUNT(*) n FROM voids WHERE run=?", (a["run"],), one=True)["n"]
    check(v == 1 and C.run_state(a["run"])["state"] == "killed",
          "claim r3-2: a locked kill whose end receipt landed first still voids and records that run killed",
          (v, C.run_state(a["run"])["state"]))
    # 3. an --idem replay on a locked store changes nothing and kills nothing
    fresh()
    started("rm-probe-r3c3")
    calls = []
    k = lambda us: calls.append(us) or dead(us)
    C.stop("rm-probe-r3c3", "kill", "first", killer=k, reaper=noreap, idem="k3")
    th = lock_for(1.0)
    try:
        r = C.stop("rm-probe-r3c3", "kill", "replay", killer=k, reaper=noreap, idem="k3")
    finally:
        th.join()
    check(len(calls) == 1 and r["replayed"], "claim r3-3: a locked --idem replay kills nothing and says replayed",
          (len(calls), r))
    # 4. an unreadable final reread (or a kill that used the whole budget) is UNVERIFIED, never dead
    gone = subprocess.Popen(["true"])
    gone.wait()
    real = (C._cgroup_pids, C._systemctl, C._procs)

    def slow_fail(args, timeout=10):
        if args[0] == "kill":
            time.sleep(0.3)
            return 1, "Failed to kill unit: timeout"
        return 0, ""
    C._cgroup_pids = lambda u: (P.value([gone.pid]), "probe.slice/rm-probe-r3c4.service")
    C._procs = lambda cg: P.could_not_look("stand-in: cgroup.procs unreadable")
    C._systemctl = slow_fail
    try:
        res = C.kill_units(["rm-probe-r3c4"], wait_s=0.1)
        live = subprocess.Popen(["sleep", "300"])
        C._procs = lambda cg: P.value([live.pid])    # a member that survives SIGKILL is named, not just "not dead"
        C._systemctl = lambda args, timeout=10: (1, "Failed") if args[0] == "kill" else (0, "")
        real_kill = os.kill
        os.kill = lambda pid, sig: None if pid == live.pid else real_kill(pid, sig)
        try:
            res2 = C.kill_units(["rm-probe-r3c4b"], wait_s=0.2)
        finally:
            os.kill = real_kill
            live.kill()
            live.wait(5)
    finally:
        C._cgroup_pids, C._systemctl, C._procs = real
    check(res[0]["dead"] is None and "UNVERIFIED" in res[0]["said"],
          "claim r3-4: an unreadable final cgroup reread is death UNVERIFIED", res)
    check(res2[0]["dead"] is False and live.pid in res2[0]["survivors"],
          "claim r3-4: a late member that does not die is named a survivor", res2)
    # 8. the fallback read covers descendant cgroups; an unreadable descendant is UNVERIFIED
    root = os.path.join(TMP, "cgfs")
    os.makedirs(os.path.join(root, "u.service", "child"))
    with open(os.path.join(root, "u.service", "cgroup.procs"), "w") as f:
        f.write("")
    with open(os.path.join(root, "u.service", "child", "cgroup.procs"), "w") as f:
        f.write("4242\n")
    real_root = C.CGROUP_ROOT
    C.CGROUP_ROOT = root
    try:
        got = C._procs("/u.service")
        os.makedirs(os.path.join(root, "u.service", "child2"))     # a cgroup with no readable cgroup.procs
        got2 = C._procs("/u.service")
    finally:
        C.CGROUP_ROOT = real_root
    check(list(got) == [4242] and got2.kind == "could_not_look", "claim r3-8: the cgroup read walks descendants; an "
          "unreadable one is could-not-look",
          (got, got2))
    # 5. two due escalation timers, or two concurrent kills, reap one detached run once
    for how in ("escalate", "stop"):
        fresh()
        u = "rm-detached-probe-r3c5-%s" % how
        started(u)
        t0 = time.time()
        reaps = []
        slow = lambda us: time.sleep(0.3) or dead(us)
        rp = lambda *x: reaps.append(1) or "-"
        if how == "escalate":
            C.stop(u, "write_now", "one", deadline_s=5, now=t0, escalator=noreap)
            C.stop(u, "write_now", "two", deadline_s=5, now=t0, escalator=noreap)
            ths = [threading.Thread(target=C.escalate, args=(u,), kwargs={"now": t0 + 10, "killer": slow, "reaper": rp})
                   for _ in range(2)]
        else:
            ths = [threading.Thread(target=C.stop, args=(u, "kill", "x%d" % i), kwargs={"killer": slow, "reaper": rp})
                   for i in range(2)]
        [x.start() for x in ths]
        [x.join() for x in ths]
        check(len(reaps) == 1, "claim r3-5: two concurrent %s kills of one detached run reap it once" % how, len(reaps))
    # 9. a failed escalation keeps the order deliverable and the escalate verb fails
    fresh()
    started("rm-probe-r3c9")
    t0 = time.time()
    C.stop("rm-probe-r3c9", "write_now", "order", deadline_s=5, now=t0, escalator=noreap)
    bad = lambda us: [{"unit": u, "dead": False, "ms": 1, "survivors": [1], "said": "SURVIVED: pids [1]"} for u in us]
    line = C.escalate("rm-probe-r3c9", now=t0 + 10, killer=bad, reaper=noreap)
    code, text = C.hook(unit="rm-probe-r3c9")
    check(line.startswith("ESCALATION FAILED") and code == 2 and "STOP ORDER" in text,
          "claim r3-9: after a failed escalation the hook still delivers the stop order", (line, code, text[:60]))
    # 10. hook commands survive a path with a space
    import shlex
    d = os.path.join(TMP, "with space")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "c.db")
    parts = shlex.split(C.hook_cmd("condition", "run_x", p))
    hk = json.loads(C.claude_settings(p))["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
    check(parts[-1] == p and shlex.split(hk)[-1] == p, "claim r3-10: a db path with a space stays one argument",
          (parts, hk))
    # 11. a deadline under 1 s is refused, never silently none
    for v in ("0.5s", "0", "-3m"):
        try:
            C.parse_dur(v)
            got = "accepted"
        except C.Refused:
            got = "refused"
        check(got == "refused", "claim r3-11: --deadline %s is refused" % v, got)
    check(C.parse_dur("90s") == 90 and C.parse_dur("5m") == 300, "a whole deadline still parses")
    # 7. the census: a builder called beside launch_unit, an alias run directly, two literals on one line
    root = os.path.join(TMP, "mutant3", "rimflow")
    os.makedirs(root)
    with open(os.path.join(root, "detached_helper.py"), "w") as f:
        f.write("import control as C\n\ndef launch_argv(rec):\n    return ['systemd-run', '--user', 'x']\n\n"
                "def mixed(runner):\n    C.launch_unit(['true'], {'family': 'probe'})\n    runner(launch_argv({}))\n\n"
                "def good(spec):\n    C.launch_unit(launch_argv({}), spec)\n")
    with open(os.path.join(root, "alias.py"), "w") as f:
        f.write("import subprocess\nimport control as C\n\ndef go(spec):\n"
                "    argv = ['systemd-run', '--user', 'true']\n    C.launch_unit(argv, spec)\n    alias = argv\n"
                "    subprocess.run(alias)\n\n"
                "def only_alias(spec):\n    argv = ['systemd-run', '--user', 'true']\n    alias = argv\n"
                "    C.launch_unit(alias, spec)\n\n"
                "def same_line(spec):\n    C.launch_unit(['systemd-run', 'a'], spec); subprocess.run(['systemd-run', 'b'])\n")
    m = C.call_sites(os.path.dirname(root))
    check(len(m) == 5 and not any(s_["routed"] for s_ in m), "claim r3-7: a builder's literal, an alias and two "
          "literals on one line are each unrouted", [(s_["func"], s_["line"], s_["routed"]) for s_ in m])

def t_accounts():
    """Slice 2 (RIMMANDRAKE_TYPE_EVERY_CONSUMABLE_AS_ACCOUNT_OLD_COUNTERS_GO): the consumable counts and limits are
    typed accounts in this store. `set` is an adjustment at a revision (critique 8); `undo` is a compensating act,
    refused with the later acts it would break (critique 16); pipeline_control's readers read this store."""
    fresh()
    # the item's acceptance command
    C.set_account("Graffiti", "blind_cycles_visit", 0, "t")
    r = C.undo(C.log(1)[0].split()[0], "t")
    check(r["ok"], "acceptance: set_account then undo of its act", r)
    # critique 8: set while another run completes (the adjustment is at a revision: later runs still count)
    fresh()
    C.set_account("Graffiti", "blind_cycles_total", 0, "back to zero", measured=2)
    check(C.used("Graffiti", "blind_cycles_total", 2) == 0, "set 0 at measured 2 reads 0")
    check(C.used("Graffiti", "blind_cycles_total", 3) == 1, "critique 8: a run completing after the set still counts",
          C.used("Graffiti", "blind_cycles_total", 3))
    check(C.used("Graffiti", "blind_cycles_total", C.UNM) == C.UNM, "an UNMEASURED count stays UNMEASURED")
    check(C.used("Cauldron", "blind_cycles_total", 4) == 4, "another mod's account is its own")
    check("Graffiti" in C.subjects("blind_cycles_total") and "Cauldron" not in C.subjects("blind_cycles_total")
          and C.subjects("no_such_account") == set(), "subjects() lists the accounts holding a live adjustment only")
    # critique 8: void a run from a previous visit: its window is given back, the current one is untouched
    C.grant("Graffiti", C.LOOK, 0, "open w1", win="w1")
    ok, _ = C.reserve("Graffiti", C.LOOK, "run_prev_visit", win="w1", base=1)
    C.settle("run_prev_visit", True, "a covered verdict")
    C.void("run_prev_visit", "a system fault after all")
    check(C.account("Graffiti", C.LOOK, "w1", 1)["available"] == 1 and C.account("Graffiti", C.LOOK, "w2", 1)[
        "available"] == 1, "critique 8: voiding a previous visit's run gives back that window only")
    # critique 16: set -> set -> undo first is refused (with the later act named) and keeps the later set
    fresh()
    a1 = C.set_account("Graffiti", "coverage_runs", 5, "first", measured=0)
    a2 = C.set_account("Graffiti", "coverage_runs", 2, "second", measured=0)
    r = C.undo(a1["act"]["id"], "undo first")
    check(not r["ok"] and a2["act"]["id"] in r["why"] and C.used("Graffiti", "coverage_runs", 0) == 2,
          "critique 16: set -> set -> undo first is refused naming the later set, which stands", r)
    r = C.undo(a2["act"]["id"], "undo second")
    check(r["ok"] and C.used("Graffiti", "coverage_runs", 0) == 5, "undoing the latest set puts back the one before",
          (r, C.used("Graffiti", "coverage_runs", 0)))
    r = C.undo(a2["act"]["id"], "again")
    check(not r["ok"] and "already undone" in r["why"], "critique 16: a repeated undo is refused", r)
    # adds commute: undoing an earlier add keeps a later add
    fresh()
    b1 = C.set_account("Graffiti", "coverage_malformed", 1, "add one", verb="add", measured=0)
    C.set_account("Graffiti", "coverage_malformed", 2, "add two", verb="add", measured=0)
    r = C.undo(b1["act"]["id"], "undo the first add")
    check(r["ok"] and C.used("Graffiti", "coverage_malformed", 0) == 2, "undoing an earlier add keeps a later add",
          C.used("Graffiti", "coverage_malformed", 0))
    # limits: set -> set -> undo first refused; undo second restores the first; `default` clears it
    l1 = C.set_limit("Graffiti", "blind_cycles_total", 5, "five")
    l2 = C.set_limit("Graffiti", "blind_cycles_total", 2, "two")
    check(C.limit("Graffiti", "blind_cycles_total", 3) == 2, "the latest limit binds")
    check(not C.undo(l1["act"]["id"], "x")["ok"], "an earlier limit under a later one is not undone")
    C.undo(l2["act"]["id"], "back to five")
    check(C.limit("Graffiti", "blind_cycles_total", 3) == 5, "undoing the later limit restores the earlier")
    C.set_limit("Graffiti", "blind_cycles_total", None, "default")
    check(C.limit("Graffiti", "blind_cycles_total", 3) == 3, "limit default reads the pipeline's own setting")
    # critique 16: grant -> consume -> undo grant shows the deficit
    fresh()
    g = C.grant("Graffiti", C.LOOK, 1, "one more look", win="w", owner_said="give it one more", base=1)
    for run in ("run_g1", "run_g2"):
        C.reserve("Graffiti", C.LOOK, run, win="w", base=1)
        C.settle(run, True, "a covered verdict")
    r = C.undo(g["act"]["id"], "the grant was a mistake", base=1)
    check(r["ok"] and r["after"]["available"] == -1 and "deficit" in r["line"],
          "critique 16: grant -> consume -> undo grant shows the deficit", r)
    # undo after the stage advanced: the grant's own window is compensated, the new window is untouched
    check(C.account("Graffiti", C.LOOK, "w_next", 1)["available"] == 1, "critique 16: undo after advancement leaves "
                                                                        "the new window untouched")
    # an off act is undone by identity; an act a later one replaced is refused
    o1 = C.switch("mod:Graffiti", True, "off one")
    C.switch("mod:Graffiti", True, "off two")
    check(not C.undo(o1["act"]["id"], "x")["ok"], "an off a later off replaced is not undone")
    # the readers: pipeline_control reads this store, fails closed on an unreadable one
    import pipeline_control as PC
    fresh()
    C.set_account("Graffiti", "granted_look", 0, "spent", measured=1)
    C.set_limit("Graffiti", "coverage_runs", 7, "seven")
    check(PC.used("Graffiti", "granted_look", 1) == 0 and PC.limit("Graffiti", "coverage_runs", 3) == 7,
          "pipeline_control.used/limit read the control store", (PC.used("Graffiti", "granted_look", 1),
                                                                   PC.limit("Graffiti", "coverage_runs", 3)))
    old = os.environ["RM_CONTROL_DB"]
    os.environ["RM_CONTROL_DB"] = os.path.join(TMP, "absent-acc.db")
    try:
        PC.used("Graffiti", "granted_look", 1)
        got = "no raise"
    except PC.Unreadable as e:
        got = "Unreadable: %s" % e
    finally:
        os.environ["RM_CONTROL_DB"] = old
    check(got.startswith("Unreadable"), "an unreadable control store fails pipeline_control's readers closed", got)
    # opening balances from the old journal, imported once
    pcd = os.path.join(TMP, "pc-old")
    os.makedirs(pcd, exist_ok=True)
    with open(os.path.join(pcd, "control.jsonl"), "w") as f:
        for i, (sec, name, after) in enumerate((("counts", "Cauldron/coverage_runs", -1),
                                               ("limits", "Cauldron/coverage_runs", 9))):
            f.write(json.dumps({"id": "pc_old%d" % i, "verb": "set", "sec": sec, "name": name, "before": None,
                                "after": after, "why": "old", "who": "t", "at": "x", "at_pacific": "x", "ts": 1}) + "\n")
    for _ in range(2):
        C.import_accounts(pcd)
    check(C.used("Cauldron", "coverage_runs", 3) == 2 and C.limit("Cauldron", "coverage_runs", 4) == 9,
          "the old journal's counts and limits are imported as opening balances, once",
          (C.used("Cauldron", "coverage_runs", 3), C.limit("Cauldron", "coverage_runs", 4)))
    rc, out, _ = pipe("set", "Graffiti", "coverage_runs", "4", "--why", "cli set")
    check(rc in (0, 2), "pipe set still answers (0 done or 2 refused for an unknown mod)", (rc, out))
    # slice review 7 and 8 (RIMMANDRAKE_FIX_SLICE_REVIEW_TWENTY_FINDINGS_QUEUE_FIRST): a typed look count binds at
    # admission as it reads, and an undone grant reports the balance admission reads (base 1)
    fresh()
    C.reserve("Graffiti", C.LOOK, "sr7-a", "w", base=1, used=0)
    C.settle("sr7-a", True, "a refusing verdict")
    C.set_account("Graffiti", C.LOOK, 0, "give the look back", measured=1, verb="set")
    u = C.used("Graffiti", C.LOOK, 1)
    ok, why = C.reserve("Graffiti", C.LOOK, "sr7-b", "w", base=1, used=u)
    check(u == 0 and ok, "slice review 7: a look given back by pipe set is reserved, not refused on its old charge",
          (u, ok, why))
    fresh()
    C.reserve("Graffiti", C.LOOK, "sr8-a", "w", base=1, used=0)
    C.settle("sr8-a", True, "a refusing verdict")
    g = C.grant("Graffiti", C.LOOK, 1, "one more", win="w", per_ruling="probe", base=1)
    line = PC.do_undo(g["act"]["id"], "undo the grant")[0]
    check("available 0" in line and "deficit" not in line,
          "slice review 8: undoing a look grant reports available 0 on its base-1 account", line)


def t_queue():
    """Slice 3 (RIMMANDRAKE_ADD_PIPE_QUEUE_VERBS_QUEUE_VIEW_PRINTS_MEGABYTES): `pipe queue` keeps order and membership
    apart (critique 23) in this store, and the tick's advancing list reads it."""
    fresh()
    ship = ["Pyrelands", "Graffiti", "Cauldron"]
    check(C.queue_apply(ship) == ship, "no queue act: the shipped advancing order, unchanged")
    C.queue_act("top", "Cauldron", "first", mods=ship)
    check(C.queue_apply(ship) == ["Cauldron", "Pyrelands", "Graffiti"], "queue top moves a mod first",
          C.queue_apply(ship))
    C.queue_act("bottom", "Pyrelands", "last", mods=ship)
    check(C.queue_apply(ship) == ["Cauldron", "Graffiti", "Pyrelands"], "queue bottom moves a mod last",
          C.queue_apply(ship))
    C.queue_act("move", "Pyrelands", "second", n=2, mods=ship)
    check(C.queue_apply(ship) == ["Cauldron", "Pyrelands", "Graffiti"], "queue move puts a mod at a position",
          C.queue_apply(ship))
    C.queue_act("drop", "Pyrelands", "out of the queue", mods=ship)
    check(C.queue_apply(ship) == ["Cauldron", "Graffiti"], "queue drop takes a mod out (membership)", C.queue_apply(ship))
    C.queue_act("add", "Pyrelands", "back in", mods=ship)
    check(C.queue_apply(ship) == ["Cauldron", "Pyrelands", "Graffiti"],
          "queue add puts it back where its order said (membership and order are separate)", C.queue_apply(ship))
    r = C.queue_act("top", "Cauldron", "retried", mods=ship, idem="q-retry")
    r2 = C.queue_act("top", "Cauldron", "retried", mods=ship, idem="q-retry")
    check(r2["replayed"] and r2["act"]["id"] == r["act"]["id"], "a retried queue act with one key changes nothing")
    try:
        C.queue_act("move", "Graffiti", "bad", n=0, mods=ship)
        got = "accepted"
    except C.Refused:
        got = "refused"
    check(got == "refused", "a position under 1 is refused", got)
    rc, out, _ = pipe("queue", "top", "Graffiti", "--why", "cli")
    check(rc == 0 and len([x for x in out.splitlines() if x.strip()]) <= 3 and "Graffiti" in out,
          "pipe queue top answers in at most 3 lines", (rc, out))
    rc, out, _ = pipe("queue")
    check(rc == 0 and out.splitlines()[0].startswith("queue"), "pipe queue lists the order", (rc, out))
    rc, out, _ = pipe("queue", "top", "Grafiti", "--why", "typo")
    check(rc == 2 and "Graffiti" in out, "a wrong mod is refused with the nearest name", (rc, out))
    # the tick reads it: maturation_dispatch's advancing list goes through queue_apply
    import maturation_dispatch as MD
    import inspect
    src = inspect.getsource(MD)
    check("queue_apply(" in src, "the tick's advancing list reads the store's queue (maturation_dispatch)")
    # an unreadable store: queue_apply raises (the tick keeps the shipped order and admits nothing on it)
    old = os.environ["RM_CONTROL_DB"]
    os.environ["RM_CONTROL_DB"] = os.path.join(TMP, "absent-q.db")
    try:
        C.queue_apply(ship)
        got = "no raise"
    except C.Unreadable:
        got = "Unreadable"
    finally:
        os.environ["RM_CONTROL_DB"] = old
    check(got == "Unreadable", "an unreadable store's queue read is Unreadable, never the shipped order as fact", got)
    # the compact `rimflow queue` default: running or touched today, at most 25, each cut to what to do
    import types
    sys.path.insert(0, os.path.dirname(HERE)) if os.path.dirname(HERE) not in sys.path else None
    from rimflow import cli as RC
    now = time.time()
    today = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
    old_ts = "2020-01-01T00:00:00Z"
    ev = [{"ts": today}, {"ts": old_ts}]
    items = {"RUN_%d" % i: types.SimpleNamespace(state="doing", history=[1]) for i in range(30)}
    items.update({"OLD_ONE": types.SimpleNamespace(state="ready", history=[1]),
                  "NEW_ONE": types.SimpleNamespace(state="ready", history=[0])})
    w = types.SimpleNamespace(items=items)
    body = "".join("## %s title\nstate:    x\nsummary:  %s\n\n" % (k, "y" * 2000) for k in ["NEW_ONE", "OLD_ONE"] +
                   ["RUN_%d" % i for i in range(30)])
    text = "# HEAD\nas-of: now\n\n# NEXT\n" + body
    out = RC.compact_queue(text, w, ev, "rimflow queue BENCH --full", now=now)
    check("## NEW_ONE" in out and "## OLD_ONE" not in out and out.count("## ") == 25 and "y" * 50 not in out
          and "--full" in out.splitlines()[-1] and "# NEXT" in out and len(out) < 4000,
          "the compact queue view: running or touched today, at most 25, no prose, says --full",
          (out.count("## "), len(out), out[-200:]))
    import pipeline_control as PC     # slice review 18: the retained `pipeline_control.py show` reads this store's queue
    fresh()
    ship = C.shipped_advancing()
    C.queue_act("top", ship[-1], "queue probe", mods=ship)
    q = [x for x in PC.do_show(PC.Ctx()) if x.startswith("queue")]
    check(q and "store" in q[0] and q[0].split(": ", 1)[1].startswith(ship[-1]),
          "slice review 18: pipeline_control.py show prints the store's queue, not the old journal's", q)


def t_review_round_four_p1():
    """Codex's review of the round-three fix (RIMMANDRAKE_SPLIT_CONTROL_REVIEW_ROUND_FOUR_FIFTEEN_UNTRIED): its three P1s
    and two could-not-look-read-as-none findings, each red on 16ded1e1fb; the other ten are on that item."""
    dead = lambda us: [{"unit": u, "dead": True, "ms": 1, "survivors": [], "said": "1 process(es) killed"} for u in us]
    none_running = lambda us: [{"unit": u, "dead": None, "ms": 1, "survivors": [], "said": "nothing was running in it"}
                               for u in us]
    # P1 #1: a second, later kill of a run already killed does not reap it again
    fresh()
    a = C.admit(spec("rm-detached-probe-r4c1"))
    C.condition(a["run"])
    reaps = []
    rp = lambda *x: reaps.append(1) or "-"
    C.stop("rm-detached-probe-r4c1", "kill", "first", killer=dead, reaper=rp)
    C.stop("rm-detached-probe-r4c1", "kill", "second", killer=none_running, reaper=rp)
    check(len(reaps) == 1, "claim r4-1: a later kill of a run already killed does not reap it again", len(reaps))
    # P1 #2: `<unit>.service` names the same run (its claude scope included)
    fresh()
    a = C.admit(spec("rm-role-probe-r4c2", extra_units=["claude-seat-BENCH-rm-role-probe-r4c2.scope"]))
    C.condition(a["run"])
    killed = []
    C.stop("rm-role-probe-r4c2.service", "kill", "suffixed", killer=lambda us: killed.append(list(us)) or dead(us),
           reaper=lambda *x: "-")
    check(killed and killed[0][0] == "rm-role-probe-r4c2" and "claude-seat-BENCH-rm-role-probe-r4c2.scope" in killed[0]
          and C.run_state(a["run"])["state"] == "killed",
          "claim r4-2: stop <unit>.service finds the run and its claude scope", (killed, C.run_state(a["run"])["state"]))
    # #12: pipe off cannot read the live runs: says UNVERIFIED, never "no run is live"
    fresh()
    real_q = C._q

    def q(sql, args=(), p=None, one=False):
        if "state='started'" in sql:
            raise C.Unreadable("probe: locked")
        return real_q(sql, args, p, one)
    C._q = q
    try:
        rc, buf = None, io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = C.main(["off", "Graffiti", "--why", "claim r4-12"])
    finally:
        C._q = real_q
    out = buf.getvalue()
    check(rc == 0 and "UNVERIFIED" in out and "no run is live" not in out,
          "claim r4-12: an off that cannot read the live runs says so", out)
    # #11: doctor with a failed integrity check is not OK
    real_read = C.read

    class Fake:
        def __init__(self, c):
            self.c = c

        def execute(self, sql, *a):
            if "quick_check" in sql:
                return types_ns(fetchone=lambda: ("*** in database main ***\nPage 3: btreeInitPage() returns error",))
            return self.c.execute(sql, *a)

        def close(self):
            self.c.close()
    import types
    types_ns = lambda **k: types.SimpleNamespace(**k)
    C.read = lambda p=None, timeout=1.5: Fake(real_read(p, timeout))
    try:
        code, lines = C.doctor()
    finally:
        C.read = real_read
    check(code == C.UNREADABLE and "fix:" in " ".join(lines), "claim r4-11: doctor fails on a quick_check that is not ok",
          (code, lines))


def t_slice4():
    """Slice 4 (RIMMANDRAKE_FORECAST_ON_SHARED_PLANNER_DROPIN_MIRROR_DEADMAN): `pipe next` runs the dispatch tree's own
    forecast; export_acts writes the store's acts as JSONL; a prefix drop-in gates a unit on the store-written permit
    (proved on a private rm-probe- prefix only: the live prefixes' install is the Conductor's, UNRUN here)."""
    fresh()
    C.switch("mod:Graffiti", True, "slice 4 export")
    out = os.path.join(TMP, "export", "acts.jsonl")
    n = C.export_acts(out)
    with open(out) as f:
        rows = [json.loads(x) for x in f]
    check(n == 1 and rows[0]["kind"] == "off" and rows[0]["scope"] == "mod:Graffiti",
          "export_acts writes every act as one JSON line", (n, rows))
    check(C.export_acts(out) == 1, "a second export rewrites the same file, no duplicates")
    tree, argv = C.forecast_cmd("30m")
    check(argv[-3:] == ["next", "--within", "30m"] and os.path.isfile(argv[1]) and tree,
          "pipe next runs maturation_dispatch next from the dispatch tree (or this one, named)", (tree, argv))
    try:
        C.forecast_cmd("soon")
        got = "accepted"
    except C.Refused:
        got = "refused"
    check(got == "refused", "pipe next refuses a window it cannot read", got)
    permit = os.path.join(TMP, "permit")
    txt = C.dropin_text(permit)
    check("ConditionPathExists=%s" % permit in txt and "[Unit]" in txt, "the drop-in gates on the permit file", txt)
    fresh()
    C.permit_sync(permit)
    check(os.path.exists(permit), "permit_sync writes the permit while nothing blocks all")
    C.switch("all", True, "slice 4 all off")
    C.permit_sync(permit)
    check(not os.path.exists(permit), "pipe off all removes the permit")
    C.switch("all", False, "slice 4 on")
    C.permit_sync(permit, p=os.path.join(TMP, "absent-permit.db"))
    check(not os.path.exists(permit), "an unreadable store leaves no permit (closed)")
    if not systemd_ok():
        UNRUN.append("slice 4 drop-in on a real probe unit: no user systemd here")
        return
    prefix = "rm-probe-r4dropin%d-" % os.getpid()
    unit = prefix + "x"
    marker = os.path.join(TMP, "dropin.ran")
    d = C.install_dropin(prefix, permit)
    try:
        r1 = subprocess.run(["systemd-run", "--user", "--quiet", "--collect", "--unit", unit, "/usr/bin/touch", marker],
                            capture_output=True, text=True, timeout=30)
        wait_for(lambda: unit_state(unit) in ("inactive", "failed", ""), 10)
        ran_closed = os.path.exists(marker)
        C.permit_sync(permit)
        r2 = subprocess.run(["systemd-run", "--user", "--quiet", "--collect", "--unit", unit + "2", "/usr/bin/touch",
                             marker], capture_output=True, text=True, timeout=30)
        wait_for(lambda: os.path.exists(marker), 10)
        ran_open = os.path.exists(marker)
    finally:
        C.remove_dropin(prefix)
    check(r1.returncode == 0 and not ran_closed and ran_open and not os.path.isdir(d),
          "a probe-prefix unit is skipped with no permit and runs with one; the drop-in is removed after",
          (r1.returncode, r1.stderr[-200:], ran_closed, ran_open, os.path.isdir(d)))


def t_permit_never_ghosts():
    """Promise permit-never-ghosts (RIMMANDRAKE_FORECAST_ON_SHARED_PLANNER_DROPIN_MIRROR_DEADMAN): the permit follows
    every `all` switch, the CLI's or a caller's, and a timed all-off that expires by itself is caught at the next
    admitted launch, so a drop-in-gated unit is never skipped while its run sits `admitted` (a ghost)."""
    fresh()
    permit = C.permit_path(DB)
    open(permit, "w").close()
    now = time.time()
    C.switch("all", True, "permit probe: timed", until=now + 60, now=now)
    check(not os.path.exists(permit), "a Python-level switch on all removes the permit (no CLI needed)")
    C.switch("all", False, "permit probe: on")
    check(os.path.exists(permit), "a Python-level switch back on writes the permit")
    C.switch("all", True, "permit probe: timed again", until=time.time() + 1)
    time.sleep(1.2)
    ran = []
    C.launch_unit(["--", "true"], spec("rm-probe-permit-a"),
                  runner=lambda a, **k: ran.append(a) or subprocess.CompletedProcess(a, 0, "", ""))
    check(ran and os.path.exists(permit), "after a timed all-off expires, the next admitted launch re-writes the permit",
          (ran, os.path.exists(permit)))
    fresh()     # slice review 13: `pipe stop all` and an undone `off all` move the permit too
    C.permit_sync(p=DB)
    C.stop("all", "at_easy_spot", "permit probe: stop all")
    check(not os.path.exists(permit), "slice review 13: pipe stop all removes the permit")
    fresh()
    C.permit_sync(p=DB)
    r = C.switch("all", True, "permit probe: off all")
    C.undo(r["act"]["id"], "permit probe: undo the off")
    check(os.path.exists(permit), "slice review 13: undoing off all writes the permit back")
    if not systemd_ok():
        UNRUN.append("permit ghost probe on a real probe unit: no user systemd here")
        return
    os.unlink(permit)       # the state a timed all-off left behind before the fix
    prefix = "rm-probe-r4ghost%d-" % os.getpid()
    unit = prefix + "a"
    marker = os.path.join(TMP, "ghost.ran")
    d = C.install_dropin(prefix, permit)
    try:
        r = C.launch_unit(["--user", "--quiet", "--collect", "--", "/usr/bin/touch", marker], spec(unit),
                          capture_output=True, text=True, timeout=30)
        wait_for(lambda: os.path.exists(marker), 10)
        st = C.run_state(r.run, DB) if getattr(r, "run", None) else None
    finally:
        C.remove_dropin(prefix)
    check(os.path.exists(marker) and st and st["state"] != "admitted" and not os.path.isdir(d),
          "an admitted launch on a gated prefix runs (the permit is written at admission), never a ghost",
          (os.path.exists(marker), st and st["state"], r.returncode, getattr(r, "why", None)))


def t_slices_review():
    """Codex's review of slices 2-4 (RIMMANDRAKE_FIX_SLICE_REVIEW_TWENTY_FINDINGS_QUEUE_FIRST), findings 1-6, each red
    on 1b79ae76b0; 7-20 are filed on that item."""
    ship = ["A", "B", "C"]
    fresh()
    C.queue_act("drop", "B", "out", mods=ship)
    C.queue_act("top", "B", "move a dropped one", mods=ship)
    check(C.queue_apply(ship) == ["A", "C"], "slice review 1: moving a dropped mod keeps it out", C.queue_apply(ship))
    fresh()
    C.queue_act("add", "D", "a new member", mods=ship)
    check(C.queue_apply(ship) == ["A", "B", "C", "D"], "slice review 2: adding a member keeps the others' order",
          C.queue_apply(ship))
    C.queue_act("drop", "D", "out again", mods=ship)
    c = C.read()
    try:
        full = C._queue_order(C._queue_rows(c), ship, members_only=False)
    finally:
        c.close()
    check("D" in full and "D" not in C.queue_apply(ship), "slice review 3: a dropped unshipped mod stays listed", full)
    o = types_ns(op="add", mod="all", n=None, why="x", owner_said=None, per_ruling=None, idem=None)
    try:
        C.cmd_queue(o)
        got = "accepted"
    except C.Refused:
        got = "refused"
    check(got == "refused", "slice review 4: pipe queue add all is refused (a mod only)", got)
    o = types_ns(mod="all", resource="look", n="+1", why="x", owner_said=None, per_ruling="probe", idem=None)
    try:
        C.cmd_grant(o)
        got = "accepted"
    except C.Refused:
        got = "refused"
    check(got == "refused", "slice review 20: pipe grant all look is refused (a mod only)", got)
    real_root = C.DISPATCH_ROOT
    d = os.path.join(TMP, "dispatch_tree", "src", "RimMandrake", "rimflow")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "maturation_dispatch.json"), "w") as f:
        json.dump({"advancing": ["X", "Y", "Z"]}, f)
    C.DISPATCH_ROOT = os.path.join(TMP, "dispatch_tree")
    try:
        base = C.shipped_advancing()
    finally:
        C.DISPATCH_ROOT = real_root
    check(base == ["X", "Y", "Z"], "slice review 5: queue verbs edit the live tick tree's shipped list", base)
    fresh()
    C.set_account("Graffiti", "coverage_runs", -5, "forgive", verb="add", measured=1)
    r = C.set_account("Graffiti", "coverage_runs", 1, "one more", verb="add", measured=1)
    check(C.used("Graffiti", "coverage_runs", 1) == 1 and r["after"] == 1,
          "slice review 6: add -5 at 1 reads 0, then add +1 reads 1 (no hidden debt)",
          C.used("Graffiti", "coverage_runs", 1))


def types_ns(**k):
    import types
    return types.SimpleNamespace(**k)


# ---------------------------------------------------------------- promises of the boundary page, by name
# design/specs/2026-11-18-pipeline-control-surface/boundary.md: a test here carries its promise's name.

def t_his_hold_refuses_launch():
    """Promise his-hold-refuses-launch: a new hold after a lift holds again, even on the same day with other words
    (round-four claim 10: the import's key had no words, so the new hold was read as already imported)."""
    fresh()
    hf = os.path.join(TMP, "holds_again.json")
    nov = os.path.join(TMP, "novoids.jsonl")

    def write(said):
        with open(hf, "w", encoding="utf-8") as f:
            json.dump({"holds": [{"mod": "Graffiti", "date": "2026-11-18", "said": said}]}, f)
    write("stop Graffiti")
    C.import_live(DB, hold_file=hf, concepts=[], voids_file=nov)
    check("HELD BY OWNER" in (C.blocked(spec("h1", mod="Graffiti")) or ""), "his hold refuses the launch")
    rev1 = C._q("SELECT v FROM meta WHERE k='rev'", one=True)["v"]
    C.import_live(DB, hold_file=hf, concepts=[], voids_file=nov)
    check(C._q("SELECT v FROM meta WHERE k='rev'", one=True)["v"] == rev1, "the same hold imported twice writes nothing")
    C.lift_owner("Graffiti", "go on", date="2026-11-18", held_said="stop Graffiti")
    check(C.blocked(spec("h2", mod="Graffiti")) is None, "his lift opens it at once")
    C.import_live(DB, hold_file=hf, concepts=[], voids_file=nov)
    check(C.blocked(spec("h3", mod="Graffiti")) is None, "a stale file row of the lifted hold does not hold again")
    write("no, stop it again")
    C.import_live(DB, hold_file=hf, concepts=[], voids_file=nov)
    b = C.blocked(spec("h4", mod="Graffiti")) or ""
    check("no, stop it again" in b, "a new hold the same day, with other words, holds again with his new words", b)


def t_void_never_moves_a_stage():
    """Promise void-never-moves-a-stage: `pipe show` flags the voided run and no other (round-four claim 13: a run was
    matched by substring, so voiding a judge flagged a stage its `-reader` run advanced)."""
    fresh()
    d = os.path.join(os.environ["RM_CONTROL_CONCEPTS"], "Graffiti")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "stage.json"), "w", encoding="utf-8") as f:
        json.dump({"history": [{"to": "in_game", "run": "rm-coverage-judge-17-reader"}]}, f)
    C.void("rm-coverage-judge-17", "voided by us", mod="Graffiti")
    c = C.read()
    try:
        check(C._stage_advanced_on_voided(c) == [], "a run whose name only begins with the voided run's is not flagged",
              C._stage_advanced_on_voided(c))
        with open(os.path.join(d, "stage.json"), "w", encoding="utf-8") as f:
            json.dump({"history": [{"to": "in_game", "run": "rm-coverage-judge-17"}]}, f)
        check(len(C._stage_advanced_on_voided(c)) == 1, "the voided run itself is flagged, once",
              C._stage_advanced_on_voided(c))
    finally:
        c.close()


def t_reused_name_runs_again():
    """Promise reused-name-runs-again: a launcher that reuses one unit name for every run (the stop-resume sweep, the
    testq wake) says so (`reuse_name`) and is admitted again once the earlier run is over. Any other name that ran is
    refused as DUPLICATE (a left-open run is continued once), and a live one is refused either way."""
    fresh()
    fake = lambda a, **k: subprocess.CompletedProcess(a, 0, "", "")
    argv = ["--user", "--quiet", "--collect", "--", "true"]
    r = C.launch_unit(argv, spec("rm-probe-again", reuse_name=True), runner=fake)
    C.condition(r.run)
    live = C.launch_unit(argv, spec("rm-probe-again", reuse_name=True), runner=fake)
    check(live.refused and "DUPLICATE" in live.stderr, "a reused name whose run is live is refused", live.stderr)
    C.ended(r.run, "success/exited/0")
    r2 = C.launch_unit(argv, spec("rm-probe-again", reuse_name=True), runner=fake)
    check(not getattr(r2, "refused", False) and r2.returncode == 0, "a reused name whose run ended is admitted again",
          getattr(r2, "why", None))
    C.condition(r2.run)
    C.ended(r2.run, "success/exited/0")
    once = ["--user", "--", "true"]
    r3 = C.launch_unit(once, spec("rm-probe-once"), runner=fake)
    C.condition(r3.run)
    C.ended(r3.run, "success/exited/0")
    r4 = C.launch_unit(once, spec("rm-probe-once"), runner=fake)
    check(r4.refused and "DUPLICATE" in r4.stderr, "a name that ran, not marked reused, is still refused", r4.stderr)
    for f, site in (("stop_resume.py", "SWEEP_UNIT"), (os.path.join("..", "Utils", "testq", "steward.py"), "WAKE_UNIT")):
        with open(os.path.join(HERE, f), encoding="utf-8") as fh:
            src = fh.read()
        check('"unit": %s, "reuse_name": True' % site in src, "%s launches %s with reuse_name" % (f, site))


def t_end_receipt_outlives_its_clone():
    """Promise ended-run-is-recorded-ended (RIMMANDRAKE_END_GHOST_RUNS_STORE_SAYS_STARTED_SYSTEMD_GONE): a unit's end
    receipt named one control.py, in a clone that was gone by the time it ran (the run's own, returned before the
    receipt; or the launcher's, when the run's clone did not exist yet at launch), so 4 runs stayed `started` for good
    (measured 2026-11-19). The start check and end receipt fall through to a seat clone's control.py."""
    import shlex
    import types
    seat = os.path.join(TMP, "seatclone")
    os.makedirs(os.path.join(seat, "src", "RimMandrake"))
    os.symlink(HERE, os.path.join(seat, "src", "RimMandrake", "rimflow"))
    real = C.__file__
    for case in ("its own clone, returned before the receipt", "a clone that did not exist at launch"):
        fresh()
        rc = os.path.join(TMP, "goneclone")
        shutil.rmtree(rc, ignore_errors=True)
        if case.startswith("its own"):
            os.makedirs(os.path.join(rc, "src", "RimMandrake"))
            os.symlink(HERE, os.path.join(rc, "src", "RimMandrake", "rimflow"))
        got = []
        os.environ["RM_WRAPUP_SEAT_CLONES"] = seat
        C.__file__ = os.path.join(TMP, "deadlauncher", "control.py")    # the launcher's clone, returned too
        try:
            C.launch_unit(["--user", "--", "true"], spec("rm-probe-ghost"), p=DB, clone=rc,
                          runner=lambda a, **k: got.append(list(a)) or types.SimpleNamespace(returncode=0, stdout="",
                                                                                             stderr="", args=a))
        finally:
            C.__file__ = real
            os.environ.pop("RM_WRAPUP_SEAT_CLONES")
        shutil.rmtree(rc, ignore_errors=True)
        props = {a.split("=", 1)[0]: a.split("=", 1)[1] for a in (got[0] if got else []) if a.startswith("Exec")}
        rid = "run_rm-probe-ghost"
        for prop, want in (("ExecCondition", "started"), ("ExecStopPost", "ended")):
            r = subprocess.run(shlex.split(props.get(prop, "false").lstrip("-")), capture_output=True, text=True,
                               timeout=30)
            st = (C.run_state(rid, DB) or {}).get("state")
            check(st == want, "%s: with %s gone, the unit's %s still records it %s" % (case, rc, prop, want),
                  (st, r.returncode, r.stderr[-200:]))
    # a ghost left from before the fix: reconcile (`pipe doctor`) ends a started run whose unit systemd reads gone,
    # its pending stop order done; a run whose unit cannot be read is left started and named unreadable
    fresh()
    fake = lambda a, **k: subprocess.CompletedProcess(a, 0, "", "")
    runs = {}
    for u in ("rm-probe-ghost-gone", "rm-probe-ghost-blind", "rm-probe-ghost-live"):
        runs[u] = C.launch_unit(["--user", "--", "true"], spec(u), runner=fake, p=DB).run
        C.condition(runs[u], p=DB)
    C.stop("rm-probe-ghost-gone", "at_easy_spot", "order", p=DB)
    seen = {"rm-probe-ghost-gone": False, "rm-probe-ghost-blind": None, "rm-probe-ghost-live": True}
    later = time.time() + 3600
    try:
        g = C.ghosts(DB, later, unit_loaded=seen.get)
    except AttributeError as e:
        g = {"gone": [], "unreadable": [], "err": str(e)}
    check([r["unit"] for r in g["gone"]] == ["rm-probe-ghost-gone"] and
          [r["unit"] for r in g["unreadable"]] == ["rm-probe-ghost-blind"],
          "ghosts: gone and unreadable are told apart, a live unit is neither", g)
    out = C.reconcile(DB, later, unit_loaded=seen.get)
    st = {u: C.run_state(r, DB)["state"] for u, r in runs.items()}
    stops = [x["state"] for x in C._q("SELECT state FROM stops", (), DB)]
    check(out == ["rm-probe-ghost-gone"] and st == {"rm-probe-ghost-gone": "ended", "rm-probe-ghost-blind": "started",
                                                   "rm-probe-ghost-live": "started"} and stops == ["done"],
          "reconcile ends only the gone run, and its stop order is done", (out, st, stops))


# The seven promises whose renamed test let a deliberate break pass (RIMMANDRAKE_HARDEN_PROMISE_TESTS_SEVEN_BREAKS_SLIPPED_PAST;
# acceptance/control_promise_breaks_accept.py): each now has a test of its own that checks the promise itself.

def _dead(us):
    return [{"unit": u, "dead": True, "ms": 1, "survivors": [], "said": "1 process(es) killed"} for u in us]


def t_stop_reaches_the_agent():
    """A writing stop order is shown to the running agent after its next tool call, from the run's own clone: the
    PostToolUse hook exits 2 (the only exit whose text Claude Code shows the agent) with the order and its item."""
    fresh()
    u = "rm-probe-reach1"
    a = C.admit(spec(u, mod="Graffiti", item="RIMMANDRAKE_PROBE_STOP_REACHES_AGENT"))
    C.condition(a["run"])
    C.stop(u, "write_now", "reach test", deadline_s=60, escalator=lambda *x: "-")
    code, text = C.hook(DB, unit=u)
    check(code == 2 and "STOP ORDER, write now" in text and "RIMMANDRAKE_PROBE_STOP_REACHES_AGENT" in text,
          "the hook hands a write-now order to the agent: exit 2, the order and its item", (code, text[:120]))
    check(C._q("SELECT state FROM stops WHERE unit=?", (u,), one=True)["state"] == "seen", "the order reads seen")
    rc = os.path.join(TMP, "reachclone")    # the run's own clone: its rimflow is this one, by a link
    os.makedirs(os.path.join(rc, "src", "RimMandrake"), exist_ok=True)
    if not os.path.exists(os.path.join(rc, "src", "RimMandrake", "rimflow")):
        os.symlink(HERE, os.path.join(rc, "src", "RimMandrake", "rimflow"))
    cmd = json.loads(C.claude_settings(DB, clone=rc))["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, env=dict(os.environ, RM_ROLE_UNIT=u))
    check(os.path.join(rc, "src", "RimMandrake", "rimflow", "control.py") in cmd and r.returncode == 2 and
          "STOP ORDER, write now" in r.stderr, "the run clone's hook command exits 2 with the order on stderr",
          (cmd[-80:], r.returncode, r.stderr[:120]))
    u2 = "rm-probe-reach2"
    b = C.admit(spec(u2, mod="Graffiti"))
    C.condition(b["run"])
    C.stop(u2, "at_easy_spot", "reach test easy", escalator=lambda *x: "-")
    code, text = C.hook(DB, unit=u2)
    check(code == 2 and "STOP ORDER, at the next easy spot" in text, "an at-easy-spot order reaches it too: exit 2",
          (code, text[:120]))


def t_kill_verified_dead():
    """--kill reports "killed" only after every process is seen gone; a survivor is reported and nothing is recorded
    killed. The survivor is made by the real kill_units over a stand-in cgroup whose process is read as alive."""
    fresh()
    child = subprocess.Popen(["/bin/sleep", "30"])
    real = (C._cgroup_pids, C._systemctl, C._alive)
    C._cgroup_pids = lambda unit: (P.value([child.pid]), "/probe-kill-verified")
    C._systemctl = lambda args, timeout=10: (0, "")
    try:
        for alive, want in ((lambda pid: True, "survivor"), (real[2], "dead")):
            fresh()
            u = "rm-detached-probe-killverified-%s" % want
            a = C.admit(spec(u, mod="Graffiti"))
            C.condition(a["run"])
            reaped = []
            C._alive = alive
            r = C.stop(u, "kill", "kill verified test", killer=lambda us: C.kill_units(us, wait_s=0.05),
                       reaper=lambda *x: reaped.append(x) or "reaped")
            row = r["units"][0]
            state = C.run_state(a["run"])["state"]
            if want == "survivor":
                check(not row["ok"] and "SURVIVED" in row["said"] and state == "started" and not reaped,
                      "a survivor is reported, its run is not recorded killed and nothing is reaped",
                      (row, state, reaped))
            else:
                check(row["ok"] and row["dead"] and state == "killed" and reaped,
                      "with every process gone the run reads killed", (row, state))
    finally:
        C._cgroup_pids, C._systemctl, C._alive = real
        child.kill()
        child.wait()


def t_killed_run_needs_no_hand_step():
    """A killed detached run's record is closed and its clone returned by `pipe stop --kill` itself: control.py's own
    kill path (no reaper passed) marks the record finished/killed and starts the `<unit>-return` unit that runs
    finish and the clone's return. That unit's systemd-run is caught here, never started."""
    import detached_helper as DH
    fresh()
    st = os.path.join(TMP, "dstate-nohand")
    os.makedirs(os.path.join(st, "detached"), exist_ok=True)
    unit = "rm-detached-bench-probe-no-hand-step-1"
    clone = os.path.join(TMP, "pool", "clones", "RIMMANDRAKE_PROBE_NO_HAND_STEP.det")
    os.makedirs(clone, exist_ok=True)
    DH.write_record({"unit": unit, "seat": "BENCH", "item": "RIMMANDRAKE_PROBE_NO_HAND_STEP", "clone": clone,
                     "model": "opus", "at": time.time() - 60, "state": st, "status": "running",
                     "clone_how": "given " + clone, "out": os.path.join(st, "detached", unit + ".out.json"),
                     "err": os.path.join(st, "detached", unit + ".err")}, st)
    a = C.admit(spec(unit, family="detached", mod="Graffiti"))
    C.condition(a["run"])
    started, real_run = [], subprocess.run

    def run(argv, *k, **kw):
        if argv and argv[0] in ("systemd-run", "systemctl"):
            started.append(list(argv))
            return subprocess.CompletedProcess(argv, 0, "", "")
        return real_run(argv, *k, **kw)
    os.environ["RM_DISPATCHER_STATE"] = st
    subprocess.run = run
    try:
        r = C.stop(unit, "kill", "no hand step test", killer=_dead)
    finally:
        subprocess.run = real_run
        os.environ.pop("RM_DISPATCHER_STATE", None)
    rec = DH.read_record(unit, st) or {}
    check(C.run_state(a["run"])["state"] == "killed" and rec.get("status") == "finished" and
          str(rec.get("result")).startswith("killed"), "the kill itself closes the detached record (finished, killed)",
          (C.run_state(a["run"])["state"], rec.get("status"), r["units"][0].get("bookkeeping")))
    ret = [x for x in started if x[0] == "systemd-run" and unit + "-return" in x]
    check(ret and ret[0][-2:] == ["reap", unit], "and starts the unit that returns its clone (control.py reap)",
          started)


def t_stopped_run_spends_no_trial():
    """A stopped or voided run charges nothing, in the store and in the dispatch books: every stop mode releases the
    run's held trial and voids one already charged; a void gives a charged look back."""
    fresh()
    vf = os.path.join(TMP, "voids-spend.jsonl")
    os.environ["RM_RUN_VOIDS_FILE"] = vf
    try:
        import run_void as RV
        for mode in C.STOP_MODES:
            for charged in (False, True):
                u = "rm-probe-spend-%s-%s" % (mode.replace("_", ""), "charged" if charged else "held")
                w = "w-" + u
                a = C.admit(spec(u, mod="Graffiti", resources=[{"resource": C.LOOK, "win": w, "base": 1}]))
                C.condition(a["run"])
                if charged:
                    C.settle(a["run"], True, "a verdict before the stop")
                pre = C.account("Graffiti", C.LOOK, w, 1)
                C.stop(u, mode, "spend test", deadline_s=60 if mode == "write_now" else None,
                       escalator=lambda *x: "-", killer=_dead, reaper=lambda *x: "-")
                acc = C.account("Graffiti", C.LOOK, w, 1)
                check((pre["held"], pre["charged"]) == ((0, 1) if charged else (1, 0)) and acc["held"] == 0 and
                      acc["charged"] == 0 and acc["available"] == 1,
                      "pipe stop --%s: a run whose trial was %s charges nothing" % (
                          mode.replace("_", "-"), "charged" if charged else "held"), (pre, acc))
                check(u in RV.active(vf), "pipe stop --%s: the run is void in the dispatch books" % mode.replace(
                    "_", "-"))
        a = C.admit(spec("rm-probe-spend-void", mod="Graffiti", resources=[{"resource": C.LOOK, "win": "wv",
                                                                           "base": 1}]))
        C.condition(a["run"])
        C.settle(a["run"], True, "a verdict")
        C.void(a["run"], "a system fault after all")
        acc = C.account("Graffiti", C.LOOK, "wv", 1)
        check(acc["charged"] == 0 and acc["available"] == 1, "a voided run charges nothing", acc)
    finally:
        os.environ.pop("RM_RUN_VOIDS_FILE", None)


def t_probe_never_lies():
    """A failed `systemctl` call and an unreadable cgroup.procs read as "could not look", never as "nothing there"."""
    real_sc, real_root = C._systemctl, C.CGROUP_ROOT
    detail = "Failed to connect to bus: " + "x" * 150 + " No such file or directory"
    C._systemctl = lambda args, timeout=10: (1, detail)
    try:
        pids, why = C._cgroup_pids("rm-probe-blind1")
        res = C.kill_units(["rm-probe-blind1"], wait_s=0)
    finally:
        C._systemctl = real_sc
    check(pids.kind == "could_not_look" and "systemctl show failed" in pids.cause and why == "",
          "a failed systemctl show reads could not look, not empty", (pids, why))
    check(pids.cause == "systemctl show failed (rc 1): " + detail, "the failed probe keeps the whole cause", pids)
    check(res[0]["dead"] is None and "UNVERIFIED" in res[0]["said"] and "nothing was running" not in res[0]["said"],
          "and the kill says death UNVERIFIED, never nothing was running", res)
    root = os.path.join(TMP, "cgroot")
    os.makedirs(os.path.join(root, "probe.slice", "rm-probe-blind2.service"), exist_ok=True)
    os.makedirs(os.path.join(root, "probe.slice", "empty.service"), exist_ok=True)
    with open(os.path.join(root, "probe.slice", "empty.service", "cgroup.procs"), "w") as f:
        f.write("")
    C.CGROUP_ROOT = root
    try:
        blind = C._procs("/probe.slice/rm-probe-blind2.service")
        empty = C._procs("/probe.slice/empty.service")
        gone = C._procs("/probe.slice/gone.service")
    finally:
        C.CGROUP_ROOT = real_root
    check((blind.kind, empty.kind, gone.kind) == ("could_not_look", "empty", "empty"), "a cgroup without a readable"
          " cgroup.procs reads could not look;"
          " an empty one and a gone one read empty", (blind, empty, gone))
    fresh()     # slice review 17: a store whose write lock is held is not reported healthy by `pipe doctor`
    h = sqlite3.connect(DB, isolation_level=None)
    h.execute("BEGIN IMMEDIATE")
    try:
        code, lines = C.doctor()
    finally:
        h.execute("ROLLBACK")
        h.close()
    check(code == C.UNREADABLE and "locked" in lines[0], "slice review 17: pipe doctor on a write-locked store says "
          "locked, never ok", (code, lines[:1]))


def t_same_command_twice():
    """A void, a settlement or a keyed command sent twice has the effect of once (the import's twice is
    t_owner_import's): the keyed ones by their --idem key, from Python and from the `pipe` command line."""
    fresh()
    n = lambda kind: len(C._q("SELECT id FROM acts WHERE kind=?", (kind,)))
    r1 = C.switch("mod:Cauldron", True, "twice off", idem="k-off")
    r2 = C.switch("mod:Cauldron", True, "twice off", idem="k-off")
    check(n("off") == 1 and r2["replayed"] and r2["act"]["id"] == r1["act"]["id"], "an off sent twice is one act",
          (n("off"), r2.get("replayed")))
    C.grant("Graffiti", C.LOOK, 1, "twice grant", win="wg", idem="k-grant")
    C.grant("Graffiti", C.LOOK, 1, "twice grant", win="wg", idem="k-grant")
    check(C.account("Graffiti", C.LOOK, "wg", 1)["available"] == 2 and n("grant") == 1,
          "a grant of +1 sent twice adds one", C.account("Graffiti", C.LOOK, "wg", 1))
    C.set_account("Graffiti", "blind_cycles_total", 1, "twice add", measured=0, verb="add", idem="k-add")
    C.set_account("Graffiti", "blind_cycles_total", 1, "twice add", measured=0, verb="add", idem="k-add")
    check(C.used("Graffiti", "blind_cycles_total", 0) == 1, "an add of 1 sent twice adds one",
          C.used("Graffiti", "blind_cycles_total", 0))
    a = C.admit(spec("rm-probe-twice1", mod="Graffiti"))
    C.condition(a["run"])
    C.stop("rm-probe-twice1", "at_easy_spot", "twice stop", escalator=lambda *x: "-", idem="k-stop")
    r = C.stop("rm-probe-twice1", "at_easy_spot", "twice stop", escalator=lambda *x: "-", idem="k-stop")
    check(r["replayed"] and len(C._q("SELECT id FROM stops WHERE unit='rm-probe-twice1'")) == 1,
          "a stop sent twice writes one order", r)
    outs = [pipe("off", "Pyrelands", "--why", "twice cli", "--idem", "k-cli") for _ in range(2)]
    check([o[0] for o in outs] == [0, 0] and len(C._q("SELECT id FROM acts WHERE idem='k-cli'")) == 1,
          "pipe off --idem sent twice from the command line is one act", [o[1][-120:] for o in outs])
    C.grant("Graffiti", C.LOOK, 0, "open wt", win="wt")
    C.reserve("Graffiti", C.LOOK, "run_twice_look", win="wt", base=1)
    C.settle("run_twice_look", True, "verdict")
    C.settle("run_twice_look", True, "verdict again")
    check(C.account("Graffiti", C.LOOK, "wt", 1)["charged"] == 1, "a settlement sent twice charges once")
    C.void("run_twice_look", "void")
    C.void("run_twice_look", "void again")
    acc = C.account("Graffiti", C.LOOK, "wt", 1)
    check(acc["charged"] == 0 and acc["available"] == 1, "a void sent twice gives back once", acc)


def t_every_change_is_an_act():
    """Each change is one record: who, when (Pacific), why, before, after. A write prints at most 3 lines; `pipe undo`
    reverses an act or refuses naming the later acts in its way. `before` is the state the change replaced: the OFF
    row a second off overwrote (its why and act), the account before a grant, the limit before a new limit."""
    fresh()
    act = lambda aid: C._q("SELECT * FROM acts WHERE id=?", (aid,), one=True)
    o1 = C.switch("mod:Graffiti", True, "first off")["act"]
    o2 = C.switch("mod:Graffiti", True, "second off")["act"]
    on = C.switch("mod:Graffiti", False, "on again")["act"]
    g = C.grant("Graffiti", C.LOOK, 2, "two looks", win="wa", base=1)["act"]
    l1 = C.set_limit("Graffiti", "blind_cycles_total", 5, "limit five")["act"]
    l2 = C.set_limit("Graffiti", "blind_cycles_total", 7, "limit seven")["act"]
    s = C.set_account("Graffiti", "blind_cycles_total", 0, "back to zero", measured=2)["act"]
    rows = [act(x["id"]) for x in (o1, o2, on, g, l1, l2, s)]
    check(len(C._q("SELECT id FROM acts")) == 7, "seven changes are seven acts", len(C._q("SELECT id FROM acts")))
    check(all(r["who"] == C.who() and r["at_pacific"] == C.pac(r["ts"]) and r["why"] for r in rows),
          "every act records who, when in Pacific, and why", [(r["who"], r["at_pacific"], r["why"]) for r in rows])
    b = [json.loads(r["before"]) for r in rows]
    check(b[0] is None and (b[1] or {}).get("why") == "first off" and (b[1] or {}).get("act") == o1["id"] and
          (b[2] or {}).get("why") == "second off", "an off's and an on's before is the switch row they replaced", b[:3])
    check((b[3] or {}).get("available") == 1 and b[4] == {"limit": None} and b[5] == {"limit": 5} and
          b[6] == {"used": 2, "measured": 2}, "a grant's, a limit's and a set's before is the state they changed",
          b[3:])
    af = [json.loads(r["after"]) for r in rows]
    check(af[1].get("why") == "second off" and af[3] == {"grant": 2} and af[5] == {"limit": 7},
          "and their after is what they wrote", af)
    rc, out, _ = pipe("off", "Cauldron", "--why", "three lines")
    lines = [x for x in out.splitlines() if x.strip()]
    last = C._q("SELECT * FROM acts ORDER BY rev DESC LIMIT 1", one=True)
    check(rc == 0 and len(lines) <= 3 and last["id"] in out and last["why"] == "three lines",
          "a write prints at most 3 lines, naming its act", lines)
    u = C.undo(l1["id"], "undo the first limit")
    check(not u["ok"] and l2["id"] in u["why"], "undo refuses an act with a later act in its way, naming it", u)
    check(C.undo(l2["id"], "undo the second")["ok"] and C.undo(l1["id"], "then the first")["ok"] and
          C.limit("Graffiti", "blind_cycles_total", 9) == 9, "latest first, both undo back to the default")


def t_before_is_read():
    """`pipe log` prints each act's before beside its after; `pipe undo` of an OFF laid over an earlier OFF puts that
    earlier OFF back (its why and act), not ON; a lone OFF undoes to ON; a limit undoes by a compensating act."""
    fresh()
    o1 = C.switch("mod:Graffiti", True, "first off: the earlier reason")["act"]
    o2 = C.switch("mod:Graffiti", True, "second off laid over it")["act"]
    lines = C.log(5)
    mine = [x for x in lines if x.startswith(o2["id"])]
    check(len(mine) == 1 and o1["id"] in mine[0] and "first off" in mine[0] and "second off" in mine[0],
          "pipe log prints an act's before (the OFF it replaced) beside its after", lines)
    u = C.undo(o2["id"], "undo the second off")
    sw = C._q("SELECT * FROM switches WHERE scope='mod:Graffiti' AND layer='control'", one=True)
    check(u["ok"] and sw is not None and sw["act"] == o1["id"] and sw["why"].startswith("first off"),
          "undo of an off over an earlier off restores that earlier off from its before", (u, sw and dict(sw)))
    check("first off" in (u["line"] or "") and o1["id"] in (u["line"] or ""), "and its line names what it put back",
          u["line"])
    u1 = C.undo(o1["id"], "undo the restored first off")
    check(u1["ok"] and C._q("SELECT * FROM switches WHERE scope='mod:Graffiti' AND layer='control'", one=True) is None,
          "undo of the restored lone off leaves the scope ON", u1)
    l1 = C.set_limit("Graffiti", "blind_cycles_total", 5, "limit five")["act"]
    C.set_account("Graffiti", "blind_cycles_total", 3, "count three", measured=0)
    ul = C.undo(l1["id"], "undo the limit")
    check(ul["ok"] and C.limit("Graffiti", "blind_cycles_total", 9) == 9 and
          sum(r["delta"] or 0 for r in C._q("SELECT * FROM adjustments WHERE kind='count' AND state='live'")) == 3,
          "a limit undoes by a compensating act: the count set after it still counts", ul)


# Each remaining promise's name, bound to the test its "Tested by" line names (the most specific one where it names
# several); src/RimMandrake/Utils/boundary_check.py reads these. main() runs each function once, whatever its names.
t_off_blocks_starts = t_race
t_one_admission_point = t_sites
t_three_named_stops = t_stop
t_kill_works_without_the_store = t_review_claims_round_two
t_look_charged_only_on_a_verdict = t_coverage_look
t_void_gives_back_once = t_look
t_unreadable_store_launches_nothing = t_unreadable
t_binds_at_once_from_any_clone = t_clones
t_verbs_answer_in_a_second = t_verbs
t_queue_order_is_the_stores = t_queue
t_counts_and_limits_are_adjustments = t_accounts
t_a_test_never_touches_the_live_store = t_stop_review_fixes
t_ended_run_is_recorded_ended = t_end_receipt_outlives_its_clone


# ---------------------------------------------------------------- a test makes no live effect

LEAK_CHILD = r"""
import os, sys
sys.path.insert(0, %(here)r)
import control as C
r = C.launch_unit(["--user", "--", "/bin/true"], {"family": %(family)r, "unit": "rm-probe-leak-%%d" %% os.getpid()})
print("REFUSED" if r.refused else "RAN", r.why if r.refused else "")
"""


def _fake_systemd_run(name):
    """A PATH whose systemd-run is a stand-in that only leaves a mark: the real subprocess.run runs it, nothing starts.
    -> (the PATH, the mark's path)."""
    d = os.path.join(TMP, "fake-bin-" + name)
    os.makedirs(d, exist_ok=True)
    mark = os.path.join(d, "ran")
    if os.path.exists(mark):
        os.unlink(mark)
    exe = os.path.join(d, "systemd-run")
    with open(exe, "w", encoding="utf-8") as f:
        f.write("#!/bin/sh\necho ran > %s\n" % mark)
    os.chmod(exe, 0o755)
    return d + os.pathsep + os.environ.get("PATH", ""), mark


def _leak_child(family):
    """A child of this selftest with NO test mark in its environment and no selftest name: the shape of 2026-11-21's
    leak (a selftest's helper reached the real launcher). -> (what the child said, whether systemd-run was reached)."""
    path, mark = _fake_systemd_run("child-" + family)
    env = {k: v for k, v in os.environ.items() if k not in ("RM_UNDER_SELFTEST", "RM_OWNER_HOLD_FILE", "RM_DISPATCHER_STATE")}
    r = subprocess.run([PY, "-c", LEAK_CHILD % {"here": HERE, "family": family}], capture_output=True, text=True,
                       timeout=60, env=dict(env, PATH=path))
    return (r.stdout or "").strip() + (r.stderr or "")[-300:], os.path.exists(mark)


def t_a_test_process_starts_no_real_unit():
    """Replays the leak of 2026-11-21 (selftest_maturation_autonomy's fixture mod A got two real runs): a launch with
    no runner of its own, from a test process or any child of one, is refused before systemd-run; a probe-family unit
    (a drill's throwaway), a launch that passes runner=, and a test that replaced subprocess.run still go through."""
    fresh()
    path, mark = _fake_systemd_run("in")
    old = os.environ.get("PATH", "")
    os.environ["PATH"] = path
    try:
        r = C.launch_unit(["--user", "--", "/bin/true"], {"family": "detached", "unit": "rm-probe-leak-in"})
        reached = os.path.exists(mark)
        own = C.launch_unit(["--user", "--", "/bin/true"], {"family": "detached", "unit": "rm-probe-leak-own"},
                            runner=lambda argv, **kw: subprocess.CompletedProcess(argv, 0, "", ""))
        real = subprocess.run
        subprocess.run = lambda argv, **kw: subprocess.CompletedProcess(argv, 0, "", "")
        try:
            patched = C.launch_unit(["--user", "--", "/bin/true"], {"family": "detached", "unit": "rm-probe-leak-patched"})
        finally:
            subprocess.run = real
    finally:
        os.environ["PATH"] = old
    check(r.refused and "test process" in (r.why or "") and not reached,
          "in a selftest, a pipeline-family launch with no runner of its own is refused before systemd-run",
          (r.refused, getattr(r, "why", None), reached))
    check(not own.refused and not patched.refused,
          "a launch that passes runner=, or runs under a replaced subprocess.run, is the test's own act and goes through",
          (getattr(own, "why", None), getattr(patched, "why", None)))
    out, reached = _leak_child("detached")
    check(out.startswith("REFUSED") and "test process" in out and not reached,
          "a child of a selftest, with no mark in its environment, starts no real pipeline unit", (out, reached))
    out, reached = _leak_child("probe")
    check(out.startswith("RAN") and reached, "a probe-family unit (a drill's throwaway) still launches from a test", (out, reached))


def t_a_test_process_never_writes_the_real_ledger():
    """A test process that appends with the ledger of this checkout in use is refused before any byte is written; a
    ledger of the test's own (a path, RIMFLOW_LEDGER, a rebound model.EVENTS) takes the same event."""
    import model as M
    ev = {"seat": "BENCH", "event": "note", "id": "SELFTEST_LIVE_EFFECT_PROBE", "text": "t", "why": "selftest"}
    wrote, real = [], M._append_locked
    M._append_locked = lambda path, blob: wrote.append(path) or 0
    try:
        try:
            M.append(dict(ev))
            raised = None
        except Exception as e:      # noqa: BLE001
            raised = e
        own = os.path.join(TMP, "own-ledger", "events", "BENCH.jsonl")
        try:
            M.append(dict(ev), own)
            own_err = None
        except Exception as e:      # noqa: BLE001
            own_err = e
    finally:
        M._append_locked = real
    check(type(raised).__name__ == "TestLiveEffect" and not [w for w in wrote if w != own],
          "a selftest's append to this checkout's own ledger is refused before the write", (raised, wrote))
    check(own_err is None and own in wrote, "an append to a ledger of the test's own is written", (own_err, wrote))


# ---------------------------------------------------------------- his hold: the store writes, the file mirrors it

OHTOOL = os.path.join(HERE, "mod_owner_hold.py")


def ohcli(*args):
    r = subprocess.run([PY, OHTOOL] + list(args), capture_output=True, text=True, timeout=60, env=dict(os.environ))
    return r.returncode, (r.stdout or "") + (r.stderr or "")


@contextlib.contextmanager
def hold_fixture(rows, name="mirror"):
    """A fresh store, a hold file of `rows` named by RM_OWNER_HOLD_FILE, alarms in a folder of the test's own."""
    fresh()
    d = os.path.join(TMP, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "alarms"))
    hf = os.path.join(d, "mod_owner_hold.json")
    with open(hf, "w", encoding="utf-8") as f:
        json.dump({"_doc": "kept as written", "holds": rows}, f, indent=2)
    saved = {k: os.environ.get(k) for k in ("RM_OWNER_HOLD_FILE", "RM_REFUSAL_DIR")}
    os.environ["RM_OWNER_HOLD_FILE"], os.environ["RM_REFUSAL_DIR"] = hf, os.path.join(d, "alarms")
    try:
        yield hf
    finally:
        os.chmod(d, 0o755)
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def file_holds(hf):
    with open(hf, encoding="utf-8") as f:
        return {h["mod"]: h for h in json.load(f)["holds"]}


def t_hold_file_mirrors_the_store():
    """Promise hold-file-mirrors-the-store: hold, lift and allow-design write the store first; the file is then
    rewritten from the store's rows; a file row the store lacks is learned into the store, never dropped."""
    import mod_owner_hold as OH
    with hold_fixture([{"mod": "Graffiti", "date": "2026-11-18", "said": "stop Graffiti now"},
                       {"mod": "Cauldron", "date": "2026-11-16", "said": "stop the new biome mods work"}]) as hf:
        rc, out = ohcli("hold", "Pyrelands", "--said", "hold Pyrelands too", "--date", "2026-11-19")
        st = {m: r for m, r in C.mod_holds().items() if r.get("store")}
        check(rc == 0 and st.get("Pyrelands", {}).get("said") == "hold Pyrelands too",
              "mod_owner_hold.py hold writes his hold into the store with his words", (rc, out, sorted(st)))
        check(set(st) == {"Graffiti", "Cauldron", "Pyrelands"}, "the file's rows the store lacked are learned into "
                                                                 "the store, never dropped", sorted(st))
        fh = file_holds(hf)
        check(list(fh) == ["Graffiti", "Cauldron", "Pyrelands"] and fh["Pyrelands"]["said"] == "hold Pyrelands too",
              "the file is rewritten from the store: his rows in their order, the new hold after them", list(fh))
        check(json.load(open(hf))["_doc"] == "kept as written", "the mirror keeps the file's _doc")
        rc, out = ohcli("allow-design", "Pyrelands", "--said", "design it", "--date", "2026-11-19")
        st = C.mod_holds()
        check(rc == 0 and st["Pyrelands"].get("design_allowed") == {"said": "design it", "date": "2026-11-19"}
              and file_holds(hf)["Pyrelands"].get("design_allowed") == {"said": "design it", "date": "2026-11-19"},
              "allow-design writes the store's row, then the mirror", (rc, out, st.get("Pyrelands")))
        rc, out = ohcli("lift", "Cauldron", "--said", "go on Cauldron")
        doc = json.load(open(hf))
        check(rc == 0 and "Cauldron" not in C.mod_holds() and "Cauldron" not in file_holds(hf)
              and any(x.get("mod") == "Cauldron" and x.get("lifted_said") == "go on Cauldron"
                      for x in doc.get("lifted") or []),
              "a lift leaves the store, then the mirror drops the row and keeps his lifting words", (rc, out))
        before = open(hf, "rb").read()
        OH.mirror()
        OH.mirror()
        check(open(hf, "rb").read() == before, "mirroring again changes no byte (the file is the store's copy)")
        check(OH.drift()[0], "pipe doctor's drift check reads the mirror in step", OH.drift())
        rc, out, _ = pipe("doctor")
        check("owner hold mirror: in step" in out, "pipe doctor says the mirror is in step", out)
        rows = json.load(open(hf))
        rows["holds"].append({"mod": "Stillsand", "date": "2026-11-19", "said": "hand-added"})
        json.dump(rows, open(hf, "w"))
        ok, lines = OH.drift()
        check(not ok and any("Stillsand" in x for x in lines), "a row the store lacks reads as drift, with its mod",
              lines)
        rc, out = ohcli("lift", "Graffiti", "--said", "go on Graffiti")
        check(rc == 0 and "Stillsand" in file_holds(hf) and C.mod_holds().get("Stillsand", {}).get("store"),
              "a lift of another mod keeps the hand-added row: the mirror learns it into the store first", (rc, out))
        rows = json.load(open(hf))
        rows["holds"].append({"mod": "LeaningScrub", "date": "2026-11-19", "said": "hand-added too"})
        json.dump(rows, open(hf, "w"))
        OH.mirror()
        check("LeaningScrub" in file_holds(hf) and C.mod_holds().get("LeaningScrub", {}).get("store")
              and OH.drift()[0], "a bare mirror learns a row the store lacks and keeps it in the file")


CLI = os.path.join(HERE, "cli.py")
LIFT_RULING = "RIMMANDRAKE_ENACT_CONDUCTOR_MAY_LIFT_HOLD_NOT_HIM_ALONE"     # the owner's card of 2026-11-19


@contextlib.contextmanager
def conductor_ledger(file_item=True):
    """The Conductor window (AGENT_SEAT BENCH, no RM_ROLE_UNIT) on a throwaway rimflow ledger, with the ruling's item
    filed on it (file_item=False: not filed, so its digest note cannot be written). -> the ledger folder."""
    d = tempfile.mkdtemp(prefix="conductor-ledger-", dir=TMP)
    env = {"RIMFLOW_LEDGER": os.path.join(d, "events.jsonl"), "RIMFLOW_ITEMS": os.path.join(d, "items"),
           "RIMFLOW_PROBE": "no-reading", "AGENT_SEAT": "BENCH", "RIMFLOW_SEAT": "BENCH"}
    saved = {k: os.environ.get(k) for k in list(env) + ["RM_ROLE_UNIT"]}
    os.environ.update(env)
    os.environ.pop("RM_ROLE_UNIT", None)
    try:
        if file_item:
            r = subprocess.run([PY, CLI, "file", LIFT_RULING, "--for", "BENCH", "--seat", "BENCH", "--title",
                                "fixture item. Acceptance test: none, a fixture", "--why", "fixture"],
                               capture_output=True, text=True, timeout=120)
            check(r.returncode == 0, "the fixture ledger files the ruling's item", r.stderr[-300:])
        yield d
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def ledger_notes(d):
    out = []
    for dp, _, fs in os.walk(d):
        for f in fs:
            if f.endswith(".jsonl"):
                for line in open(os.path.join(dp, f), encoding="utf-8"):
                    try:
                        ev = json.loads(line)
                    except ValueError:
                        continue
                    if ev.get("event") == "note" and ev.get("id") == LIFT_RULING:
                        out.append(ev)
    return out


CONDUCTOR_ARGS = ("--per-ruling", LIFT_RULING, "--why", "Pyrelands needs it now")


def t_his_hold_lifts_by_him_or_the_conductor():
    """Promise his-hold-lifts-by-him-or-the-conductor: only `mod_owner_hold.py lift <Mod>` lifts his hold, with his
    words (--said) or as the Conductor's lift (--per-ruling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_LIFT_HOLD_NOT_HIM_ALONE
    --why). `pipe on <Mod>`, `pipe on all`, `pipe undo` of the hold, a lift without words, with blank words, citing
    another ruling, with no reason or with both his words and the ruling, a hand edit deleting the file's row and
    `pipe init --import` of that edited file each leave it held."""
    import mod_owner_hold as OH
    with hold_fixture([], "lift_only") as hf, conductor_ledger():
        rc, out = ohcli("hold", "Graffiti", "--said", "stop Graffiti", "--date", "2026-11-19")
        act = C.mod_holds()["Graffiti"]["act"]

        def held(what):
            b = C.blocked(spec("lw-" + what.split()[0], mod="Graffiti")) or ""
            check("HELD BY OWNER" in b and "Graffiti" in OH.load(), "after %s Graffiti is still held by him" % what, b)
        check(rc == 0, "the hold is written", out)
        held("the hold")
        for args in (("on", "Graffiti"), ("on", "mod:Graffiti"), ("on", "all")):
            rc, out, _ = pipe(*args, "--why", "try to lift it")
            if args[1] != "all":
                check("still HELD BY OWNER" in out, "`pipe %s` says his hold stays" % " ".join(args), out)
            held("pipe " + " ".join(args))
        rc, out, _ = pipe("undo", act, "--why", "try to undo his hold")
        check(rc != 0, "`pipe undo` of his hold act is refused", (rc, out))
        held("pipe undo")
        rc, out = ohcli("lift", "Graffiti")
        check(rc != 0, "a lift without --said is refused", rc)
        held("lift-without-words")
        rc, out = ohcli("lift", "Graffiti", "--said", "  ")
        check(rc != 0, "a lift with blank words is refused", (rc, out))
        held("lift-with-blank-words")
        json.dump({"holds": []}, open(hf, "w"))
        held("hand-edit deleting the row")
        C.import_live(DB, hold_file=hf, concepts=[], voids_file=os.path.join(TMP, "novoids.jsonl"))
        held("import of the edited file")
        OH.mirror()
        check("Graffiti" in file_holds(hf), "the next mirror writes the deleted row back from the store")
        for bad, what in ((("--per-ruling", "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM", "--why", "go"), "another ruling"),
                          (("--per-ruling", LIFT_RULING), "the ruling with no reason"),
                          (("--per-ruling", LIFT_RULING, "--why", "  "), "the ruling with a blank reason"),
                          (("--said", "go on", *CONDUCTOR_ARGS), "his words and the ruling both")):
            rc, out = ohcli("lift", "Graffiti", *bad)
            check(rc != 0, "a lift citing %s is refused" % what, (rc, out))
            held("lift-citing-" + what.replace(" ", "-"))
        rc, out = ohcli("lift", "Graffiti", "--said", "go on Graffiti")
        check(rc == 0 and C.blocked(spec("lw-z", mod="Graffiti")) is None and "Graffiti" not in OH.load(),
              "`mod_owner_hold.py lift Graffiti --said` lifts it", (rc, out))
        ohcli("hold", "Cauldron", "--said", "stop Cauldron", "--date", "2026-11-19")
        rc, out = ohcli("lift", "Cauldron", *CONDUCTOR_ARGS)
        check(rc == 0 and C.blocked(spec("lw-c", mod="Cauldron")) is None and "Cauldron" not in OH.load(),
              "the Conductor's lift (`--per-ruling %s --why`) lifts it" % LIFT_RULING, (rc, out))
        check("READY" in out, "the Conductor's lift says the mod still waits for its readiness list", out)


def t_conductor_lift_only_from_its_window():
    """Promise conductor-lift-only-from-its-window: the Conductor's lift is refused, and the mod stays held, from a
    launched run (RM_ROLE_UNIT set: a detached helper, a role run), from another seat, and with no seat; from the
    Conductor window (seat BENCH, no RM_ROLE_UNIT) it lifts."""
    import mod_owner_hold as OH
    with hold_fixture([], "lift_window"), conductor_ledger() as d:
        ohcli("hold", "Graffiti", "--said", "stop Graffiti", "--date", "2026-11-19")
        for env, what in (({"RM_ROLE_UNIT": "rm-detached-bench-x-1"}, "a launched helper"),
                          ({"AGENT_SEAT": "OPERATIONS", "RIMFLOW_SEAT": "OPERATIONS"}, "another seat"),
                          ({"AGENT_SEAT": "", "RIMFLOW_SEAT": ""}, "no seat")):
            r = subprocess.run([PY, OHTOOL, "lift", "Graffiti", *CONDUCTOR_ARGS], capture_output=True, text=True,
                               timeout=120, env=dict(os.environ, **env))
            check(r.returncode != 0 and "Conductor window" in r.stderr and "Graffiti" in OH.load(),
                  "the Conductor's lift from %s is refused and Graffiti stays held" % what, (r.returncode, r.stderr))
        check(not ledger_notes(d), "a refused lift writes no digest note", ledger_notes(d))
        rc, out = ohcli("lift", "Graffiti", *CONDUCTOR_ARGS)
        check(rc == 0 and "Graffiti" not in OH.load(), "the Conductor window's lift lifts it", (rc, out))


def t_conductors_lift_is_its_own_act():
    """Promise conductors-lift-is-its-own-act: the Conductor's lift is recorded as the Conductor's act, never as his
    words: the store act carries per_ruling the ruling's item and no owner_said; the mirror's lifted row says
    lifted_by CONDUCTOR with its reason and no lifted_said; a BENCH ledger note whose why starts `delegated: scope:`
    (his daily digest's class scope) is written before it lifts, and a lift whose note cannot be written lifts nothing."""
    import mod_owner_hold as OH
    sys.path.insert(0, os.path.dirname(HERE))
    from contracts import blind as BL
    with hold_fixture([{"mod": "Graffiti", "date": "2026-11-18", "said": "stop Graffiti now"}], "lift_act") as hf:
        with conductor_ledger(file_item=False) as d:
            rc, out = ohcli("lift", "Graffiti", *CONDUCTOR_ARGS)
            check(rc != 0 and "digest note" in out and "Graffiti" in OH.load(),
                  "a Conductor lift whose digest note cannot be written lifts nothing", (rc, out))
        with conductor_ledger() as d:
            rc, out = ohcli("lift", "Graffiti", *CONDUCTOR_ARGS)
            check(rc == 0 and "Graffiti" not in OH.load(), "the Conductor's lift lifts it", (rc, out))
            acts = [a for a in C._q("SELECT * FROM acts WHERE kind='lift'") if a["scope"] == "mod:Graffiti"]
            check(len(acts) == 1 and acts[0]["per_ruling"] == LIFT_RULING and not acts[0]["owner_said"]
                  and acts[0]["why"].startswith("the Conductor lifted his hold"),
                  "the store act is the Conductor's: per_ruling the item, no owner_said", [dict(a) for a in acts])
            rows = [x for x in json.load(open(hf, encoding="utf-8")).get("lifted", []) if x.get("mod") == "Graffiti"]
            check(len(rows) == 1 and rows[0].get("lifted_by") == "CONDUCTOR" and "lifted_said" not in rows[0]
                  and rows[0].get("lifted_why") == "Pyrelands needs it now" and rows[0].get("said") == "stop Graffiti now",
                  "the mirror's lifted row says lifted_by CONDUCTOR, never his lifting words", rows)
            OH.mirror()
            rows2 = [x for x in json.load(open(hf, encoding="utf-8")).get("lifted", []) if x.get("mod") == "Graffiti"]
            check(rows2 == rows, "a second mirror keeps the one Conductor lift row", rows2)
            notes = ledger_notes(d)
            check(len(notes) == 1 and notes[0]["why"].startswith("delegated: scope:") and "Graffiti" in notes[0]["text"]
                  and BL.class_of(notes[0]["why"]) == "scope" and not notes[0].get("ownerSaid"),
                  "a BENCH note `delegated: scope:` reaches his digest as class scope", notes)


def t_mirror_failure_is_an_alarm():
    """Promise mirror-failure-is-an-alarm: a mirror that cannot be written raises the alarm control:owner_hold_mirror,
    exits 5 and lifts nothing: a new hold holds from the store, the file is left whole, and the other holds stay."""
    import mod_owner_hold as OH
    import refusal_contract as RC
    with hold_fixture([{"mod": "Graffiti", "date": "2026-11-18", "said": "stop Graffiti now"},
                       {"mod": "Cauldron", "date": "2026-11-16", "said": "stop the new biome mods work"}],
                      "mirror_fails") as hf:
        OH.mirror()
        before = open(hf, "rb").read()
        os.chmod(os.path.dirname(hf), 0o555)      # the mirror's folder cannot be written
        rc, out = ohcli("hold", "Stillsand", "--said", "hold Stillsand", "--date", "2026-11-19")
        alarms = RC.open_alarms()
        check(rc == 5 and "ALARM" in out, "a hold whose mirror cannot be written exits 5 and says ALARM", (rc, out))
        check(any(a.get("subject") == "control:owner_hold_mirror" for a in alarms),
              "the alarm control:owner_hold_mirror is raised", alarms)
        check("HELD BY OWNER" in (C.blocked(spec("mf1", mod="Stillsand")) or "") and "Stillsand" in OH.load(),
              "the new hold holds from the store though its mirror failed")
        check(open(hf, "rb").read() == before, "the failed mirror leaves the file whole")
        rc, out = ohcli("lift", "Graffiti", "--said", "go on Graffiti")
        check(rc == 5 and set(OH.load()) == {"Cauldron", "Stillsand"},
              "a lift whose mirror fails lifts only the mod he named: the rest stay held", (rc, out, sorted(OH.load())))
        os.chmod(os.path.dirname(hf), 0o755)
        rc, out = ohcli("mirror")
        check(rc == 0 and set(file_holds(hf)) == {"Cauldron", "Stillsand"} and OH.drift()[0],
              "`mod_owner_hold.py mirror` writes the file from the store once it can", (rc, out))
        check(not any(a.get("subject") == "control:owner_hold_mirror" for a in RC.open_alarms()),
              "a mirror written again clears its alarm")
        saved = os.environ["RM_CONTROL_DB"]
        os.environ["RM_CONTROL_DB"] = os.path.join(TMP, "gone-hold.db")
        try:
            rc, out = ohcli("hold", "FlowWorks", "--said", "hold it")
        finally:
            os.environ["RM_CONTROL_DB"] = saved
        check(rc == 3 and "COULD NOT LOOK" in out and "FlowWorks" not in file_holds(hf),
              "a hold on an unreadable store exits 3, could not look, and writes no mirror row", (rc, out))


def t_held_stays_held_across_the_mirror():
    """Promise held-stays-held-across-the-mirror: the shipped hold file, learned into an empty store and mirrored back,
    holds the same mods with the same words, dates and allowances, row for row, so the cutover changes no hold."""
    import mod_owner_hold as OH
    shipped = json.load(open(OH.PATH, encoding="utf-8"))
    with hold_fixture(shipped["holds"], "shipped") as hf:
        before = OH.load_file(hf)
        OH.mirror()
        after_store = {m: r for m, r in C.mod_holds().items() if r.get("store")}
        after = OH.load()
        check(sorted(after_store) == sorted(before) == sorted(after), "the store holds the shipped mods after the "
              "mirror, and every reader still reads them held", (sorted(before), sorted(after_store)))
        check(json.load(open(hf))["holds"] == shipped["holds"], "the mirrored rows equal the shipped rows exactly "
                                                                 "(words, dates, allowances, order)")
        check(all(after_store[m]["said"] == before[m]["said"] and after_store[m]["date"] == before[m]["date"]
                  and after_store[m].get("design_allowed") == before[m].get("design_allowed") for m in before),
              "each store row carries his words, date and design allowance")


def t_next_fits_a_screen():
    """next-fits-a-screen: `pipe next` without --full prints under 1,500 characters: each start with when and its rule,
    every waiting mod named on one line per reason; --full prints the tree's text whole (3,894-4,937 characters on the
    live tree, 2026-11-19)."""
    long_why = 'HELD BY OWNER 2026-11-16: "%s" (lift: python3 src/RimMandrake/rimflow/mod_owner_hold.py lift X)' % (
        "And stop the new biome mods work. " * 6)
    fc = {"at": 1000.0, "at_pac": "6:48 AM PST", "within_s": 1800.0, "step_s": 60,
          "launches": [{"mod": "StartMod%d" % i, "at": 1000.0 + 60 * i, "at_pac": "6:5%d AM PST" % i,
                        "launch": {"kind": "build", "model": "opus", "rule": "rule_%d" % i}} for i in range(3)],
          "blocked": [{"mod": "WaitMod%02d" % i, "decision": "owner_hold",
                       "why": long_why if i % 2 else "OFF by pipe (act ct_%06d at 4:40 PM): %s" % (i, "slow " * 40)}
                      for i in range(14)] + [{"mod": "SettleMod", "decision": "settle", "why": "x" * 400}],
          "unmeasured": ["Mod%d: UNMEASURED after its live run(s) %s end" % (i, "rm-detached-" + "y" * 90)
                         for i in range(3)],
          "roles": ["Designer: no scheduled slot (the role is disabled); %s" % ("z" * 300), "red_dispatch: UNMEASURED"]}
    text_full = "\n".join("line %d %s" % (i, "w" * 200) for i in range(25))

    class R:
        def __init__(self, out, rc=0):
            self.stdout, self.returncode, self.stderr = out, rc, ""

    def runner(argv, **kw):
        if argv[0] == "git":
            return R("abc1234\n")
        return R(json.dumps(fc) if argv[-1] == "--json" else text_full)
    code, lines = C.forecast("30m", runner=runner)
    out = "\n".join(lines)
    check(code == C.OK and len(out) < C.NEXT_BRIEF_MAX, "pipe next fits under 1,500 characters", (len(out), out))
    for x in fc["launches"]:
        check(any(x["mod"] in ln and x["at_pac"] in ln and x["launch"]["rule"] in ln and "WILL START" in ln
                  for ln in lines), "pipe next names each start, its time and its rule", (x["mod"], out))
    for b in fc["blocked"]:
        check(b["mod"] in out, "pipe next names every waiting mod", (b["mod"], out))
    waits = [ln for ln in lines if ln.startswith("waits,")]
    check(len(waits) <= len(fc["blocked"]) and len(waits) == 3, "one line per reason the mods wait (3 reasons here)",
          waits)
    code, lines = C.forecast("30m", runner=runner, full=True)
    check(code == C.OK and "\n".join(lines[1:]) == text_full, "pipe next --full prints the tree's text whole",
          len("\n".join(lines)))
    fc["launches"] = [dict(fc["launches"][0], mod="Many%d" % i) for i in range(9)]
    code, lines = C.forecast("30m", runner=runner)
    check(len("\n".join(lines)) < C.NEXT_BRIEF_MAX and "and 4 more start(s): pipe next --full" in lines,
          "past five starts, the rest are counted and pointed at --full", lines)
    code, lines = C.forecast("30m", runner=lambda a, **k: R("abc\n") if a[0] == "git" else R("not json"))
    check(code == C.FAILED and "cannot be read" in lines[-1], "unreadable forecast JSON is a failure named, never an "
          "empty forecast", lines)


def t_deadline_is_wall_clock():
    """deadline-is-wall-clock: a write-now order's escalation timer is due at the wall-clock deadline the order states
    (`--on-calendar`, in UTC, rounded up to the second), never after a monotonic count (`--on-active`): on this WSL2 VM
    a 2-minute `--on-active` timer fired 105 s late and a 30 s one 58.8 s late, because the wall clock jumps ahead of
    the monotonic one (the real-agent drill, 2026-11-19)."""
    fresh()
    got = []
    import types
    t0 = time.time()
    C.schedule_escalation("rm-probe-wall", 120, DB,
                          runner=lambda argv, **k: got.append(list(argv)) or types.SimpleNamespace(returncode=0))
    t1 = time.time()
    argv = got[0] if got else []
    cal = [x for x in argv if x.startswith("--on-calendar=")]
    check(not any(x.startswith("--on-active") for x in argv) and len(cal) == 1 and cal[0].endswith(" UTC"),
          "the escalation timer is a wall-clock (--on-calendar ... UTC) timer, not --on-active", argv[:8])
    if cal:
        import calendar
        due = calendar.timegm(time.strptime(cal[0][len("--on-calendar="):-len(" UTC")], "%Y-%m-%d %H:%M:%S"))
        check(t0 + 120 <= due <= t1 + 121, "the timer is due at the stated deadline, rounded up to the second",
              (due - t0, cal))
    r = C.stop("rm-probe-wall2", "write_now", "wall clock", deadline_s=120, escalator=lambda *x: "timer probe")
    check("escalates to --kill at" in r["units"][0]["said"] if r["units"] else True,
          "pipe stop still states the deadline it set", r)


def t_undo_disarms_escalation():
    """Undo withdraws a write-now order and disarms its timer, including when undo crosses timer creation."""
    from unittest.mock import patch

    def pipe_cli(*args):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = C.main(list(args))
        check(rc == 0, "pipe %s succeeds" % args[0], out.getvalue())

    def undo_latest():
        order = C._q("SELECT * FROM stops ORDER BY id DESC LIMIT 1", one=True)
        pipe_cli("undo", order["act"], "--why", "withdraw the stop")
        return order

    def arm(argv, **kw):
        if during_arm:
            undo_latest()
        armed.add(argv[argv.index("--unit") + 1] + ".timer")
        return subprocess.CompletedProcess(argv, 0, "", "")

    def disarm(args, timeout=10):
        assert args[0] == "stop", args
        armed.difference_update(args[1:])
        return 0, ""

    unit = "rm-probe-stop-undo"
    fresh()
    schedule = C.schedule_escalation
    armed = set()
    during_arm = False
    with patch.object(C, "schedule_escalation", lambda *args: schedule(*args, runner=arm)), \
            patch.object(C, "_systemctl", disarm):
        pipe_cli("stop", unit, "--write-now", "--deadline", "1h", "--why", "keep this order")
        keep = armed.copy()
        pipe_cli("stop", unit, "--write-now", "--why", "withdraw this order")
        check(len(keep) == 1 and len(armed) == 2, "write-now stops arm separate timers", armed)
        order = undo_latest()
        check(armed == keep, "pipe undo disarms the withdrawn stop's escalation timer", sorted(armed - keep))
        killed = []
        line = C.escalate(unit, now=order["deadline"] + 1, killer=lambda units: killed.extend(units) or [])
        check("nothing to do" in line and not killed, "escalation skips a withdrawn order at its deadline", line)
        during_arm = True
        pipe_cli("stop", unit, "--write-now", "--why", "undo during timer creation")
        check(armed == keep, "a timer armed concurrently with undo is disarmed", sorted(armed - keep))


def t_an_off_over_a_live_switch_names_the_one_it_replaces():
    """2026-11-23 4:02 AM PST: a helper's proof ran `pipe off family:list_dispatch` over the Conductor's live switch
    (ct_000112, machine load) and then `pipe on`; the output said only "OFF -> OFF", and the Conductor's switch was gone."""
    fresh()
    rc, out1, _ = pipe("off", "family:testq", "--why", "the first reason")
    rc, out, _ = pipe("off", "family:testq", "--why", "a second reason")
    check(rc == 0 and "REPLACES" in out and "the first reason" in out and "pipe on" in out,
          "an off over a live switch names the act and reason it replaces, and that `pipe on` lifts both", out)
    rc, out, _ = pipe("off", "family:stop_resume", "--why", "fresh")
    check(rc == 0 and "REPLACES" not in out, "an off on a scope that was on says nothing about a replacement", out)


def t_an_unseeded_mod_can_be_switched_off():
    """Promise an-unseeded-mod-can-be-switched-off (RIMMANDRAKE_HOLD_NEW_CONCEPT_DISABLED_DESIGNER_CHAINS): WreckedMachines
    was admitted with a shipping folder and no concept, and `pipe off WreckedMachines` read "no mod in the pipeline"."""
    fresh()
    env = {"RM_CONTROL_MOD_FOLDERS": "Wrecked,Other"}
    rc, out, _ = pipe("off", "Wrecked", "--why", "admitted, not seeded: no pass until he says go", env=env)
    check(rc == 0 and "mod:Wrecked ON -> OFF" in out, "`pipe off` takes a mod with a shipping folder, not seeded", out)
    check("OFF" in (C.blocked(spec("w1", mod="Wrecked")) or ""), "its OFF row refuses a launch naming the mod")
    import mod_owner_hold as OH
    check((OH.held("design/concepts/Wrecked") or {}).get("control") is True,
          "every hold reader sees it: mod_owner_hold.held on its concept path", OH.held("design/concepts/Wrecked"))
    rc, out, _ = pipe("on", "Wrecked", "--why", "readiness READY", env=env)
    check(rc == 0 and C.blocked(spec("w2", mod="Wrecked")) is None, "`pipe on` lifts it", out)
    rc, out, _ = pipe("off", "Nowhere", "--why", "x", env=env)
    check(rc != 0 and "no mod 'Nowhere'" in out, "a name with neither a concept nor a shipping folder is refused", out)
    for verb in (["queue", "top", "Wrecked"], ["grant", "Wrecked", "look", "+1", "--owner-said", "go"]):
        rc, out, _ = pipe(*(verb + ["--why", "x"]), env=env)
        check(rc != 0 and "no mod 'Wrecked'" in out, "`pipe %s` still refuses an unseeded mod" % verb[0], out)


def main():
    # its probe units have fixed names in the one user systemd: runs on one machine (sibling clones' ./publish) take
    # turns, or one run's unit is "already loaded" for the other (RIMMANDRAKE_SERIALIZE_CONTROL_SELFTEST_SIBLINGS_SHARE_UNIT_NAMES)
    import fcntl
    lock = open("/tmp/rm-selftest-control-%d.lock" % os.getuid(), "w")
    fcntl.flock(lock, fcntl.LOCK_EX)
    for t in (t_void_books_by_run_id, t_verbs, t_scope, t_race, t_look, t_unreadable, t_crash, t_clones, t_void_stage, t_owner_import, t_stop,
              t_stop_review_fixes, t_kill_bookkeeping, t_coverage_look, t_sites,
              t_hooks_in_run_clone, t_review_claims_eight, t_review_claims_round_two, t_review_claims_round_three,
              t_accounts, t_queue, t_review_round_four_p1,
              t_slice4, t_slices_review, t_his_hold_refuses_launch, t_void_never_moves_a_stage,
              t_reused_name_runs_again, t_end_receipt_outlives_its_clone,
              t_stop_reaches_the_agent, t_kill_verified_dead, t_killed_run_needs_no_hand_step,
              t_stopped_run_spends_no_trial, t_probe_never_lies, t_same_command_twice, t_every_change_is_an_act,
              t_permit_never_ghosts, t_before_is_read, t_hold_file_mirrors_the_store,
              t_his_hold_lifts_by_him_or_the_conductor, t_conductor_lift_only_from_its_window,
              t_conductors_lift_is_its_own_act, t_mirror_failure_is_an_alarm, t_held_stays_held_across_the_mirror,
              t_next_fits_a_screen, t_deadline_is_wall_clock, t_undo_disarms_escalation, t_an_unseeded_mod_can_be_switched_off,
              t_an_off_over_a_live_switch_names_the_one_it_replaces,
              t_a_test_process_starts_no_real_unit, t_a_test_process_never_writes_the_real_ledger):
        print("== %s" % t.__name__)
        try:
            t()
        except Exception as e:      # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    for u in UNRUN:
        print("UNRUN %s" % u)
    shutil.rmtree(TMP, ignore_errors=True)
    if FAILS:
        print("FAILED %d: %s" % (len(FAILS), "; ".join(FAILS[:8])))
        return 1
    if UNRUN:
        print("FAILED: %d part(s) UNRUN (a test that could not look is not a pass)" % len(UNRUN))
        return 1
    print("PASS selftest_control")
    return 0


if __name__ == "__main__":
    sys.exit(main())
