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
            ts.append(el)
        times[v] = ts
        lines = [x for x in out.splitlines() if x.strip()]
        check(rc == want, "pipe %s exits %d" % (" ".join(args[:2]), want), (rc, out[-300:]))
        if v in ("off", "on", "off-all", "on-all", "off-stage", "off-item", "off-family", "void", "grant"):
            check(len(lines) <= 3, "pipe %s prints at most 3 lines" % v, lines)
    allt = sorted(x for ts in times.values() for x in ts)
    p95 = allt[int(0.95 * (len(allt) - 1))]
    print("     measured: %d pipe calls (fresh python each), p95 %.0f ms, max %.0f ms" % (len(allt), p95 * 1000,
                                                                                       allt[-1] * 1000))
    check(p95 < 1.0, "every pipe verb's p95 is under 1 s", p95)
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
    res = C.launch_unit(["systemd-run", "--user", "--quiet", "--collect", "--unit", "rm-probe-race-a",
                         "/bin/sh", "-c", "touch " + mark], spec("rm-probe-race-a"), runner=runner_pausing,
                        capture_output=True, text=True, timeout=30)
    time.sleep(0.3)
    check(res.refused and res.returncode == C.LAUNCH_REFUSED_RC, "real unit, pause before start: the launcher gets "
                                                                   "REFUSED, never rc 0", (res.returncode, res.stderr))
    check(not os.path.exists(mark), "real unit, pause before start: its payload never ran")
    C.switch("all", False, "resume")
    res = C.launch_unit(["systemd-run", "--user", "--quiet", "--collect", "--unit", "rm-probe-race-b",
                         "/bin/sh", "-c", "touch %s; sleep 2" % mark], spec("rm-probe-race-b"), capture_output=True,
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
        res = C.launch_unit(["systemd-run", "--user", "--unit", "rm-probe-u-" + name.replace(" ", ""), "true"],
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
              "C.launch_unit(['systemd-run', '--user', '--quiet', '--collect', '--unit', 'rm-probe-crash2', '/bin/sleep',"
              " '1'], {'family': 'probe', 'unit': 'rm-probe-crash2', 'mod': 'Graffiti', 'resources': [{'resource': "
              "C.LOOK, 'win': 'wc2', 'base': 1}]}, runner=run, capture_output=True, text=True, timeout=30)" % HERE)
    subprocess.run([PY, "-c", child2], timeout=60)
    wait_for(lambda: (C.run_state("rm-probe-crash2") or {}).get("state") == "ended", 10)
    rows = C._q("SELECT * FROM runs WHERE unit='rm-probe-crash2'")
    a = C.account("Graffiti", C.LOOK, "wc2", 1)
    check(len(rows) == 1 and rows[0]["state"] == "ended", "a launcher that died after the unit started: exactly one "
                                                          "run, recorded ended by its unit", rows)
    check(a["charged"] == 0 and a["held"] == 0, "and no charge (it never settled: released)", a)
    res = C.launch_unit(["systemd-run", "--user", "--unit", "rm-probe-crash2", "true"], spec("rm-probe-crash2"),
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
    check(any("look Graffiti window 2026-11-17T18:45:12Z" in x for x in lines), "a grant still waiting on its fixes "
                                                                               "imports as an opening balance", lines)
    lines2 = C.import_live(DB, hold_file=hf, concepts=[], voids_file=os.path.join(TMP, "novoids.jsonl"))
    holds = C.mod_holds()
    check(set(holds) == {"Graffiti", "Cauldron"} and holds["Graffiti"]["said"] == "stop Graffiti now",
          "the import holds every mod of the file with his words", holds)
    check(holds["Cauldron"].get("design_allowed", {}).get("said") == "design only", "his design-only words travel")
    check(all("already" in x or "OFF" in x or "voids" in x for x in lines2), "a second import changes nothing", lines2)
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

TRAP = """#!/bin/bash
trap '' TERM
( trap '' TERM; exec -a rm-probe-child sleep 1000 ) &
echo $! > "$1"
while true; do sleep 0.2; done
"""

STUB = r"""
import os, subprocess, sys, time
tool, db, note, calls = sys.argv[1:5]
n = 0
while n < 600:
    n += 1
    time.sleep(0.1)          # one simulated tool call
    r = subprocess.run([sys.executable, tool, "hook", "--db", db], capture_output=True, text=True)
    if r.returncode == 2:
        with open(note, "w") as f:
            f.write("HANDOFF after %d tool calls: %s" % (n, r.stderr))
        sys.exit(0)
    with open(calls, "w") as f:
        f.write(str(n))
"""


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
    res = C.launch_unit(["systemd-run", "--user", "--quiet", "--collect", "--unit", "rm-probe-kill1", trap, pidf],
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
    res = C.launch_unit(["systemd-run", "--user", "--quiet", "--collect", "--unit", "rm-probe-stub1",
                         "--setenv", "RM_ROLE_UNIT=rm-probe-stub1", PY, stub, TOOL, DB, note, calls],
                        spec("rm-probe-stub1", mod="Graffiti", item="RIMMANDRAKE_PROBE_STOP_CHANNEL_STUB",
                             resources=[{"resource": C.LOOK, "win": "ws", "base": 1}]),
                        capture_output=True, text=True, timeout=30)
    check(res.returncode == 0, "the stub agent starts", res.stderr)
    wait_for(lambda: os.path.exists(calls), 5)
    before = int(open(calls).read() or 0)
    r = C.stop("Graffiti", "write_now", "write-now test", deadline_s=60, escalator=lambda *a: "no timer in test")
    check(r["units"] and r["units"][0]["unit"] == "rm-probe-stub1", "the stop order names the live unit", r["units"])
    wait_for(lambda: os.path.exists(note), 10)
    txt = open(note).read() if os.path.exists(note) else ""
    seen_after = int(txt.split("after ")[1].split(" ")[0]) - before if "after " in txt else 99
    check("STOP ORDER, write now" in txt and "RIMMANDRAKE_PROBE_STOP_CHANNEL_STUB" in txt,
          "the running agent receives the write-now order through its hook, with its item", txt[:200])
    check(seen_after <= 2, "within one tool call of the order (counted %d)" % seen_after)
    wait_for(lambda: C.run_state("rm-probe-stub1")["state"] == "ended", 10)
    check(C.run_state("rm-probe-stub1")["state"] == "ended", "the unit ended after writing")
    srow = C._q("SELECT * FROM stops WHERE unit='rm-probe-stub1'", one=True)
    check(srow["state"] == "done" and srow["seen_at"], "the stop order reads seen, then done", srow)
    a = C.account("Graffiti", C.LOOK, "ws", 1)
    check(a["held"] == 0 and a["charged"] == 0, "its trial is released", a)
    # the deadline: an agent that ignores the order is killed
    C.switch("mod:Graffiti", False, "on again")
    res = C.launch_unit(["systemd-run", "--user", "--quiet", "--collect", "--unit", "rm-probe-deaf1", "/bin/sleep",
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
    win = "2026-11-17T18:45:12Z"
    with open(os.path.join(d, "stage.json"), "w") as f:
        json.dump({"mod": "ModLook", "stage": "designer", "coverage_rounds": [],
                   "coverage_releases": [{"at": "2026-11-18T10:00:00Z", "rounds_at": 0, "judges_at": [],
                                          "granted_at": win}]}, f)
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
    check(C.look_window({"coverage_release_granted": {"at": win}}) == win, "a grant still waiting on its fixes keys "
                                                                           "the same window as its release")
    C.grant("ModLook", C.LOOK, 1, "his exception", win=win, owner_said="one more")
    check(CJ.look_balance(CJ.DS.load_state(d), d)["lim"] == 2, "a pipe grant adds one to the look's limit")


# ---------------------------------------------------------------- every launch site is routed; a mutant is caught

def t_sites():
    sites = C.call_sites()
    bad = [s for s in sites if not s["routed"]]
    check(len(sites) >= 18, "the census sees every systemd-run site (%d)" % len(sites), len(sites))
    check(not bad, "every systemd-run call site goes through control.launch_unit",
          ["%s:%s:%d %s" % (s["file"], s["func"], s["line"], s["why"]) for s in bad])
    root = os.path.join(TMP, "mutant", "rimflow")
    os.makedirs(root)
    with open(os.path.join(root, "sneaky.py"), "w") as f:
        f.write("import subprocess\n\ndef go():\n    subprocess.run(['systemd-run', '--user', '--unit', 'x', 'true'])\n")
    m = C.call_sites(os.path.dirname(root))
    check([s for s in m if not s["routed"] and s["func"] == "go"], "a mutant launcher that bypasses launch_unit "
                                                                    "turns the census red", m)
    with open(os.path.join(root, "detached_helper.py"), "w") as f:
        f.write("def launch_argv(rec):\n    return ['systemd-run', '--user', 'x']\n\n"
                "def bad(runner):\n    runner(launch_argv({}))\n")
    m = C.call_sites(os.path.dirname(root))
    check([s for s in m if not s["routed"] and s["func"] == "launch_argv"], "a builder called outside launch_unit "
                                                                            "turns it red", m)


def main():
    for t in (t_verbs, t_scope, t_race, t_look, t_unreadable, t_crash, t_clones, t_void_stage, t_owner_import, t_stop,
              t_kill_bookkeeping, t_coverage_look, t_sites):
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
