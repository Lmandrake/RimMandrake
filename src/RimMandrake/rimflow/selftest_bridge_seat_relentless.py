#!/usr/bin/env python3
"""RELENTLESS_SEAT_UNTANGLE_FROM_BENCH: Relentless and the Conductor's window both run as seat BENCH, so a bridge hold by
one read as "ours" to the other. Relentless now holds the bridge as RELENTLESS. The driver lock is OFF for the seat rows
below on purpose: they prove the SEAT check tells the two apart with no process-keyed lock behind it. Runs the real
cli on a throwaway ledger, shared file and lock; touches nothing real."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
RIM = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, RIM)
REPO = os.path.dirname(os.path.dirname(RIM))
CLI = os.path.join(HERE, "cli.py")
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


class Rig:
    def __init__(self):
        self.tmp = tempfile.mkdtemp(prefix="rf_seat_")
        os.makedirs(os.path.join(self.tmp, "items"))
        self.base = {k: v for k, v in os.environ.items() if k not in (
            "RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "CLAUDECODE", "RIMFLOW_RAN_BY", "RM_DRIVER_PID",
            "RIMFLOW_BRIDGE_SEAT", "RELENTLESS_SUPERVISOR", "RM_HOST_GUARD_GEN")}
        self.base.update(RIMFLOW_LEDGER=os.path.join(self.tmp, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(self.tmp, "items"),
                         RIMFLOW_SHARED_BRIDGE=os.path.join(self.tmp, "shared.json"), RIMFLOW_PROBE="no-reading",
                         RIMFLOW_DISPATCH_LOCK=os.path.join(self.tmp, "dispatch.lock"),
                         RIMFLOW_BRIDGE_LOCK=os.path.join(self.tmp, "bridge.lock"),
                         RIMFLOW_OWNER_ACT_STAMP=os.path.join(self.tmp, "act.json"),
                         RIMFLOW_DRIVER_LOCK="")

    def env(self, who, **more):
        e = dict(self.base, RIMFLOW_SEAT="BENCH")
        if who == "relentless":
            e.update(RIMFLOW_BRIDGE_SEAT="RELENTLESS", RIMFLOW_BRIDGE_SEAT_IN_TEST="1")
        elif who != "conductor":
            e.update(RIMFLOW_SEAT=who, RIMFLOW_BRIDGE_SEAT="RELENTLESS", RIMFLOW_BRIDGE_SEAT_IN_TEST="1")
        e.update(more)
        return e

    def rf(self, who, *a, **more):
        r = subprocess.run([sys.executable, CLI, *a], env=self.env(who, **more), capture_output=True, text=True,
                           timeout=120, cwd=self.tmp)
        return r.returncode, r.stdout + r.stderr

    def py(self, who, code, **more):
        r = subprocess.run([sys.executable, "-c", "import sys; sys.path[:0] = [%r, %r]\n%s" % (RIM, HERE, code)],
                           env=self.env(who, **more), capture_output=True, text=True, timeout=120, cwd=self.tmp)
        return (r.stdout + r.stderr).strip()

    def holder(self):
        return self.py("conductor", "import os; from rimflow import model as m; m.EVENTS = os.environ['RIMFLOW_LEDGER']; print(m.replay(m.read()).bridge_holder)")

    def gate(self, who):
        return self.py(who, "from rimflow import model as m; r = m.bridge_gate(m.ambient_window_seat()); "
                            "print('PASS' if r is None else 'REFUSE ' + r)")


def seat_rows(g):
    # ---- the owner's joint session (the Conductor's BENCH) holds it: not Relentless's
    rc, out = g.rf("conductor", "bridge", "take", "--for", "joint session with the owner")
    check(rc == 0 and g.holder() == "BENCH", "the Conductor's take holds as BENCH: %s" % g.holder())
    rc, out = g.rf("relentless", "bridge", "idle", "--for", "relentless staging X")
    check(rc == 1 and "NOT TAKEABLE" in out and "BENCH" in out, "idle from Relentless reads his hold as someone else's: %s" % out[:90])
    rc, out = g.rf("relentless", "bridge", "take", "--idle-ok", "--for", "relentless staging X")
    check(rc != 0 and g.holder() == "BENCH", "a delegated take from Relentless is refused: %s" % out[:90])
    rc, out = g.rf("relentless", "bridge", "take", "--for", "relentless staging X")
    check(rc != 0 and g.holder() == "BENCH", "a plain take from Relentless is refused too")
    rc, out = g.rf("relentless", "bridge", "release", "--mine")
    check(rc == 0 and g.holder() == "BENCH", "release --mine after a staging leaves his hold: %s" % out[:90])
    check(g.gate("relentless").startswith("REFUSE"), "a game tool under Relentless is refused on his hold")
    check(g.gate("conductor") == "PASS", "a game tool in his window passes on his hold")
    rc, out = g.rf("conductor", "bridge", "release", "--mine")
    check(rc == 0 and g.holder() == "None", "his own release --mine still frees it")

    # ---- Relentless holds it: the Conductor sees a stranger, so nothing of his reads it as his
    rc, out = g.rf("relentless", "bridge", "idle", "--for", "relentless staging X")
    check(rc == 0 and "TAKEABLE" in out, "a free bridge is takeable by Relentless")
    rc, out = g.rf("relentless", "bridge", "take", "--idle-ok", "--for", "relentless staging X")
    check(rc == 0 and g.holder() == "RELENTLESS", "Relentless's take holds as RELENTLESS: %s %s" % (g.holder(), out[:80]))
    rows = [json.loads(x) for x in open(os.path.join(g.tmp, "events", "RELENTLESS.jsonl"), encoding="utf-8")]
    check(len(rows) == 1 and rows[0]["event"] == "bridge" and rows[0]["seat"] == "RELENTLESS", "the take is in its own shard")
    check(g.gate("relentless") == "PASS", "a game tool under Relentless passes on its own hold")
    check(g.gate("conductor").startswith("REFUSE"), "a game tool in his window no longer passes on Relentless's hold")
    rc, out = g.rf("conductor", "bridge", "idle", "--for", "what the Conductor wants")
    check(rc == 1 and "RELENTLESS" in out, "idle from the Conductor names Relentless: %s" % out[:90])
    rc, out = g.rf("conductor", "bridge", "release", "--mine")
    check(rc == 0 and g.holder() == "RELENTLESS", "the Conductor's release --mine leaves Relentless's hold")
    reading = g.py("conductor", "from rimflow import seat_restart as S; print(json.dumps(S.bridge_reading('BENCH')))".replace(
        "from rimflow", "import json; from rimflow"))
    check('"RELENTLESS"' in reading and '"BENCH"' not in reading.replace('"holders"', ""),
          "a Relentless hold is not a BENCH hold to a window's restart (the 16 min of 2026-11-03): %s" % reading[:90])
    rc, out = g.rf("conductor", "bridge", "take", "--for", "what the Conductor wants")
    check(rc != 0 and g.holder() == "RELENTLESS", "a plain Conductor take waits on a live Relentless hold")
    rc, out = g.rf("conductor", "bridge", "take", "--force", "--for", "the owner wants the game")
    check(rc == 0 and g.holder() == "BENCH", "--force still cuts across it: %s" % out[:90])
    last = [json.loads(x) for x in open(os.path.join(g.tmp, "events", "BENCH.jsonl"), encoding="utf-8")][-1]
    check("RELENTLESS" in (last.get("override") or ""), "and the cut is on the event: %s" % last.get("override"))
    g.rf("conductor", "bridge", "release", "--mine")


def lock_rows(g):
    lock = os.path.join(g.tmp, "DRIVER_LOCK.json")
    sleeper = subprocess.Popen(["sleep", "300"])
    try:
        more = {"RIMFLOW_DRIVER_LOCK": lock, "RM_DRIVER_PID": str(sleeper.pid)}
        rc, out = g.rf("relentless", "bridge", "take", "--idle-ok", "--for", "relentless staging Y", **more)
        seat = json.load(open(lock, encoding="utf-8")).get("seat") if rc == 0 else None
        check(rc == 0 and seat == "RELENTLESS", "the driver lock names RELENTLESS: %s %s" % (seat, out[:90]))
        code = "from rimflow import seat_restart as S, model; import json; print(json.dumps(S.bridge_reading('BENCH')))"
        g.base["RIMFLOW_SHARED_BRIDGE"], keep = os.path.join(g.tmp, "none.json"), g.base["RIMFLOW_SHARED_BRIDGE"]
        reading = g.py("conductor", code, RIMFLOW_DRIVER_LOCK=lock)
        g.base["RIMFLOW_SHARED_BRIDGE"] = keep
        check('"RELENTLESS"' in reading and '"BENCH"' not in reading, "restart reads the lock as Relentless's: %s" % reading[:90])
        rc, out = g.rf("relentless", "bridge", "release", "--mine", **more)
        check(rc == 0 and g.holder() == "None" and not os.path.exists(lock), "release frees ledger hold and lock: %s" % out[:90])
    finally:
        sleeper.kill()
        sleeper.wait()


# Run in a child under the rig's env: the real restart decision, recheck and kill step of a Conductor goodbye, on whatever
# the rig's shared file and driver lock really say. Only the window (transcript, session, helpers, ledger) is simulated.
RESTART_PROBE = """
import json
import selftest_seat_restart as F
SR = F.SR
SR.UNFILED = lambda t: None
T0 = F.T0
sch, st = F.bsched(), F.fresh()
tx = F._tx_file("quiet", [{"type": "assistant", "timestamp": SR._iso(T0 - 900),
                           "message": {"role": "assistant", "stop_reason": "end_turn", "content": [{"type": "text", "text": "bye"}]}}])
SR.transcript_for = lambda sf, cfg: tx
o = F.obs(sessions=[F.bsess()], request=F.breq(), tx={"last_user_at": None})
o["seat_restart"]["bridge"] = SR.bridge_reading
F.run(sch, st, o, T0 + 1)
acts = F.run(sch, st, o, T0 + 700)
holds = [a["why"] for a in acts if a["do"] == "restart_hold"]
state = F.bstate(st)               # read now: the kill step below moves it on
recheck = SR.recheck_at_kill("BENCH", sch, dict(st["seat_restart"]["BENCH"]), F.bsess(), paused=lambda: None,
                             work=lambda s_, ts: [], shard=lambda s_: None)
kills = []
fired = None
if state != "claimed":     # held at the decision: the kill step gets its own claim, so its recheck is what is read
    st2 = F.fresh()
    o2 = F.obs(sessions=[F.bsess()], request=F.breq(), tx={"last_user_at": None})
    F.run(sch, st2, o2, T0 + 1)
    k = [a for a in F.run(sch, st2, o2, T0 + 700) if a["do"] == "restart_kill"]
else:
    st2, k = st, [a for a in acts if a["do"] == "restart_kill"]
if k:
    fx = {"session_file": lambda pid: {"pid": pid, "sessionId": "sid-old", "name": "CONDUCTOR", "status": "idle"},
          "kill": lambda pid, start=None: kills.append(pid) or "SIGTERM", "write_killed": lambda s_, r: None, "start": lambda pid: 77,
          "recheck": lambda seat, sch_, rs_, sf: SR.recheck_at_kill(seat, sch_, rs_, sf, paused=lambda: None,
                                                                    work=lambda s_, ts: [], shard=lambda s_: None)}
    fired = bool(SR.execute(k[0], sch, st2, True, T0 + 701, fx) is not None and kills)
print(json.dumps({"reading": SR.bridge_reading("BENCH"), "state": state, "dos": [a["do"] for a in acts], "holds": holds,
                  "recheck": recheck, "killed": fired, "claimed_for_kill": bool(k)}))
"""


def restart_probe(g, **more):
    out = g.py("conductor", RESTART_PROBE, TMPDIR=g.tmp, **more)
    try:
        return json.loads(out.splitlines()[-1])
    except (IndexError, ValueError):
        return {"crash": out[-600:]}


def restart_hold_rows(g):
    """The item's own words, 2026-11-03: a Relentless bridge hold never holds a Conductor restart; 16 min 13 s of restart_hold
    'bridge/driver lock held by BENCH'. Each row reads the hold check itself, not only the holders list it is fed."""
    free = restart_probe(g)
    check(free.get("reading", {}).get("holders") == [] and free.get("state") == "claimed" and "restart_kill" in free.get("dos", [])
          and not free.get("holds") and free.get("recheck") == [] and free.get("killed") is True,
          "control: a free bridge goes through decide, recheck and the kill step: %s" % free)

    def relentless_clears(p, how):
        check(p.get("reading", {}).get("holders") and "RELENTLESS" in p["reading"]["holders"] and "BENCH" not in p["reading"]["holders"],
              "%s: the restart really reads Relentless: %s" % (how, p.get("reading") or p))
        check(p.get("state") == "claimed" and "restart_kill" in p.get("dos", []) and not p.get("holds"),
              "%s holds no Conductor restart at the decision (_pending): %s %s" % (how, p.get("dos"), p.get("holds")))
        check(p.get("recheck") == [], "%s holds no Conductor restart at the kill (recheck_at_kill): %s" % (how, p.get("recheck")))
        check(p.get("killed") is True, "%s: the kill step fires: %s" % (how, p.get("killed")))

    def bench_holds(p, how):
        check(p.get("reading", {}).get("holders") and "BENCH" in p["reading"]["holders"], "%s: the restart really reads BENCH: %s" % (how, p.get("reading") or p))
        check(p.get("state") == "pending" and "restart_kill" not in p.get("dos", [])
              and any("bridge/driver lock held by BENCH" in h for h in p.get("holds", [])),
              "%s still holds at the decision (_pending): %s %s" % (how, p.get("dos"), p.get("holds")))
        check(p.get("recheck") == ["bridge held by BENCH"], "%s still holds at the kill (recheck_at_kill): %s" % (how, p.get("recheck")))
        check(p.get("killed") is False, "%s: the kill step does not fire: %s" % (how, p.get("killed")))

    rc, out = g.rf("relentless", "bridge", "take", "--idle-ok", "--for", "relentless proving a graffiti")
    check(rc == 0 and g.holder() == "RELENTLESS", "Relentless holds through the real cli: %s" % out[:90])
    relentless_clears(restart_probe(g), "a Relentless hold in the shared file")
    g.rf("relentless", "bridge", "release", "--mine")
    rc, out = g.rf("conductor", "bridge", "take", "--idle-ok", "--for", "the Conductor driving")
    check(rc == 0 and g.holder() == "BENCH", "the Conductor holds through the real cli: %s" % out[:90])
    bench_holds(restart_probe(g), "the Conductor's own hold in the shared file")
    g.rf("conductor", "bridge", "release", "--mine")
    lock = os.path.join(g.tmp, "DRIVER_LOCK_RESTART.json")
    keep = g.base["RIMFLOW_SHARED_BRIDGE"]
    sleeper = subprocess.Popen(["sleep", "300"])
    try:
        for who, rule, how in (("relentless", relentless_clears, "a Relentless driver lock alone"),
                               ("conductor", bench_holds, "the Conductor's driver lock alone")):
            more = {"RIMFLOW_DRIVER_LOCK": lock, "RM_DRIVER_PID": str(sleeper.pid)}
            rc, out = g.rf(who, "bridge", "take", "--idle-ok", "--for", "restart row", **more)
            check(rc == 0 and os.path.exists(lock), "%s: taken: %s" % (how, out[:90]))
            g.base["RIMFLOW_SHARED_BRIDGE"] = os.path.join(g.tmp, "none.json")   # the lock is the only thing to read
            try:
                rule(restart_probe(g, RIMFLOW_DRIVER_LOCK=lock), how)
            finally:
                g.base["RIMFLOW_SHARED_BRIDGE"] = keep
            g.rf(who, "bridge", "release", "--mine", **more)
    finally:
        sleeper.kill()
        sleeper.wait()


def holder_is_not_a_seat(g):
    rc, out = g.rf("RELENTLESS", "note", "X_Y", "--text", "x")
    check(rc != 0 and "RELENTLESS" in out, "nobody runs as RELENTLESS: %s" % out[:80])
    r = subprocess.run([sys.executable, CLI, "file", "SEAT_TEST_THING", "--for", "RELENTLESS", "--kind", "task", "--title", "x",
                        "--needs", "offline", "--why", "t"], env=g.env("conductor"), capture_output=True, text=True, timeout=120)
    check(r.returncode != 0, "nobody files for RELENTLESS")
    code = ("from rimflow import model as m\n"
            "try:\n  m._check_seat({'seat': 'RELENTLESS', 'event': 'note'}); print('ALLOWED')\n"
            "except m.SchemaError: print('REFUSED')\n"
            "m._check_seat({'seat': 'RELENTLESS', 'event': 'bridge'}); print('BRIDGE OK')")
    check(g.py("conductor", code).split() == ["REFUSED", "BRIDGE", "OK"], "the schema takes a holder on `bridge` events only")


def identity_rows(g):
    code = "from rimflow import model as m; print(m.bridge_identity(%r))"
    check(g.py("relentless", code % "BENCH") == "RELENTLESS", "BENCH under Relentless is RELENTLESS")
    check(g.py("conductor", code % "BENCH") == "BENCH", "BENCH without the variable is BENCH")
    check(g.py("OWNER", code % "OWNER") == "OWNER", "OWNER is never renamed, whatever process runs ./bridge")
    check(g.py("RUNNER", code % "RUNNER") == "RUNNER", "RUNNER is never renamed")
    check(g.py("relentless", code % "BENCH", RIMFLOW_BRIDGE_SEAT="NONSENSE") == "BENCH", "a name that is no holder renames nothing")
    e = dict(g.env("relentless"))
    e.pop("RIMFLOW_BRIDGE_SEAT_IN_TEST")
    r = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r)\n%s" % (RIM, code % "BENCH")],
                       env=e, capture_output=True, text=True)
    check(r.stdout.strip() == "BENCH", "a selftest run by a Relentless worker keeps its BENCH fixtures")


def wiring_rows():
    """Each door Relentless opens the bridge through carries the name; a door without it silently holds as BENCH again."""
    os.environ.pop("RIMFLOW_LEDGER", None)
    os.environ.pop("RIMFLOW_BRIDGE_SEAT", None)     # a worker running this suite inherits the name: each door must say it itself
    os.environ.pop("WSLENV", None)
    import relentless
    import relentless_live
    from rimflow import model
    check(relentless.BRIDGE_HOLDER in model.BRIDGE_HOLDERS, "relentless names a holder the ledger accepts")
    done = types.SimpleNamespace(returncode=0, stdout="", stderr="")
    with mock.patch.object(subprocess, "run", return_value=done) as run:
        relentless.Effects.rimflow(types.SimpleNamespace(r={"seat": "BENCH"}, books="/nowhere"), "bridge", "who")
    check(run.call_args.kwargs["env"].get("RIMFLOW_BRIDGE_SEAT") == "RELENTLESS", "the supervisor's rimflow says RELENTLESS")
    with mock.patch.object(subprocess, "run", return_value=done) as run:
        relentless_live.Fx.rimflow(types.SimpleNamespace(seat="BENCH", books="/nowhere"), "bridge", "who")
    check(run.call_args.kwargs["env"].get("RIMFLOW_BRIDGE_SEAT") == "RELENTLESS", "the live tier's rimflow says RELENTLESS")

    rl = types.SimpleNamespace(launch_argv=lambda *a: ["systemd-run", "--", "claude", "--output-format", "json"])
    d = tempfile.mkdtemp(prefix="rf_seat_w_")
    try:
        fx = types.SimpleNamespace(RL=rl, r={"seat": "BENCH", "model": "opus"})
        run_ = {"unit": "u", "out": os.path.join(d, "o"), "err": os.path.join(d, "e")}
        with mock.patch.object(subprocess, "run", return_value=done) as run, \
                mock.patch.object(relentless.run_tmp, "prepare", return_value=d), \
                mock.patch.object(relentless.run_tmp, "env", return_value={"TMPDIR": d}), \
                mock.patch.object(relentless.relentless_usage, "note_clone"):
            relentless.Effects.launch(fx, {"item": "I"}, run_, "prompt", "rm-builder", "/clone", 60, {})
        argv = run.call_args.args[0]
        at = argv.index("RIMFLOW_BRIDGE_SEAT=RELENTLESS") if "RIMFLOW_BRIDGE_SEAT=RELENTLESS" in argv else -1
        check(0 < at < argv.index("--") and argv[at - 1] == "--setenv", "a worker's unit says RELENTLESS, before the `--`")
        at = argv.index("WSLENV=RIMFLOW_BRIDGE_SEAT") if "WSLENV=RIMFLOW_BRIDGE_SEAT" in argv else -1
        check(0 < at < argv.index("--") and argv[at - 1] == "--setenv", "and hands the name to a python.exe child")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    log = os.path.join(tempfile.mkdtemp(prefix="rf_seat_p_"), "proof.log")
    rc = relentless_live.Fx.run_proof(types.SimpleNamespace(books=tempfile.gettempdir()), "printenv RIMFLOW_BRIDGE_SEAT", log, 30)
    check(rc == 0 and "RELENTLESS" in open(log, encoding="utf-8").read(), "a live proof the supervisor runs says RELENTLESS")
    import relentless_game
    with mock.patch.object(subprocess, "Popen") as popen:
        d2 = tempfile.mkdtemp(prefix="rf_seat_r_")
        relentless_game.GameFx.prove_launch(types.SimpleNamespace(base=d2, books="/nowhere"), "I")
    check(popen.call_args.kwargs["env"].get("RIMFLOW_BRIDGE_SEAT") == "RELENTLESS", "the live round the supervisor starts says RELENTLESS")

    shard = relentless.SHARD % "RELENTLESS"
    calls = []

    def fake_run(a, **k):
        calls.append(a)
        return done
    git = lambda *a, **k: types.SimpleNamespace(stdout=" M %s\n" % shard if "status" in a else "0\n", returncode=0, stderr="")
    fx = types.SimpleNamespace(r={"seat": "BENCH"}, books="/nowhere", git=git, prose_moves=lambda: [])
    with mock.patch.object(subprocess, "run", side_effect=fake_run):
        relentless.Effects.flush(fx)
    check(any(shard in a for a in calls), "flush publishes the holder's shard: %s" % calls[:1])


def p_b1_says(g, who, seat, mirror):
    """preflight_flowworks.p_b1, the FlowWorks seat check prep_site.py refuses on, against the real mirror the cli wrote."""
    return g.py(who, "import sys, types; sys.path.insert(0, %r); import preflight_flowworks as P\n"
                     "s = types.SimpleNamespace(tools=['t']); paths = types.SimpleNamespace(bridge_file=%r, run=None)\n"
                     "r = P.p_b1(s, paths, None, %r); print(r.status if hasattr(r, 'status') else r)"
                     % (os.path.join(RIM, "FlowWorks", "northstar"), mirror, seat)).split("\n")[-1]


def lease_says(g, who, mirror):
    """preflight_bridge's lease row."""
    return g.py(who, "import sys; sys.path.insert(0, %r); import preflight_bridge as P; P.BRIDGE_FILE = %r\n"
                     "r = P.c_bridge_lease({'seat': 'BENCH', 'live': True}); print(r.status if hasattr(r, 'status') else r[0], r.reason if hasattr(r, 'reason') else r[1])" % (os.path.join(RIM, "Utils"), mirror))


def wsl_says(g, who):
    """Pyrelands' gate-A and gate-C rows, through a run_wsl that drops the caller's variables as wsl.exe does."""
    return g.py(who, """import os, subprocess, sys
sys.path.insert(0, %r)
import preflight_pyrelands as P
class Env:
    def run_wsl(self, cmd, timeout=None):
        e = {k: v for k, v in os.environ.items() if k not in ('RIMFLOW_SEAT', 'AGENT_SEAT', 'RIMFLOW_BRIDGE_SEAT')}
        r = subprocess.run(cmd, env=e, capture_output=True, text=True, timeout=timeout, cwd=%r)
        return r.returncode, r.stdout + r.stderr
print(P.a1_bridge_lock(Env()).status)
""" % (os.path.join(RIM, "Pyrelands"), REPO))


def spelled_says(g, who, holder):
    """What Pyrelands hands wsl.exe, and whether gate C sees a hold that its release did not free."""
    return g.py(who, """import sys
sys.path.insert(0, %r)
import preflight_pyrelands as P
class Env:
    cmds = []
    def run_wsl(self, cmd, timeout=None):
        self.cmds.append(cmd)
        return 0, 'bridge held by %s since x'
e = Env()
print(P.a1_bridge_lock(e).status, P.c_bridge_released(e).status, all('RIMFLOW_BRIDGE_SEAT=RELENTLESS' in c for c in e.cmds))
""" % (os.path.join(RIM, "Pyrelands"), holder))


def window_says(g, who, holder):
    """The queue's bridge window: is a needs=bridge item offered, and what does the refusal say."""
    return g.py(who, "import types; from rimflow import priority as p\n"
                     "w = types.SimpleNamespace(game='UP', bridge_holder=%r); it = types.SimpleNamespace(needs='bridge', id='I')\n"
                     "print(p.satisfiable(it, w, seat='BENCH'), '|', p.needs_reason(it, w, 'BENCH'))" % holder)


def holder_check_rows(g):
    """Every check that used to read the seat alone, against a hold of each kind. A door still reading the seat says
    Relentless's own hold is a stranger's, or (the defect this item names) the Conductor's hold is its own."""
    mirror = os.path.join(g.tmp, "BRIDGE")
    g.rf("conductor", "bridge", "release", "--mine")
    g.rf("relentless", "bridge", "release", "--mine")

    rc, out = g.rf("relentless", "bridge", "take", "--for", "RELENTLESS row: names BENCH in its purpose", "--force")
    check(rc == 0 and g.holder() == "RELENTLESS", "Relentless holds: %s" % out[:80])
    check(p_b1_says(g, "relentless", "BENCH", mirror) == "PASS", "p_b1 BENCH from Relentless passes on its own hold")
    check(p_b1_says(g, "relentless", "RELENTLESS", mirror) == "PASS", "p_b1 --seat RELENTLESS passes on its own hold")
    check(p_b1_says(g, "conductor", "BENCH", mirror) == "FAIL", "p_b1 from the Conductor refuses Relentless's hold, BENCH in the purpose or not")
    check("held by this seat" in lease_says(g, "relentless", mirror), "preflight_bridge's lease from Relentless reads its own hold as its own")
    check("another seat" in lease_says(g, "conductor", mirror), "preflight_bridge's lease from the Conductor reads Relentless's as another's")
    says = wsl_says(g, "relentless")
    check(says == "PASS", "Pyrelands gate A from Relentless passes on its own hold: %s" % says[:90])
    says = wsl_says(g, "conductor")
    check(says == "FAIL", "Pyrelands gate A from the Conductor refuses Relentless's hold: %s" % says[:90])
    says = window_says(g, "relentless", "RELENTLESS")
    check(says.startswith("True"), "a bridge item is offered to Relentless on its own hold: %s" % says[:90])
    check(window_says(g, "conductor", "RELENTLESS").startswith("False"), "and is not offered to the Conductor on it")
    check("RELENTLESS is holding" in window_says(g, "conductor", "RELENTLESS"), "whose reason names Relentless")
    code = "import sys; sys.path.insert(0, %r); import handoff; print(handoff.own_hold(%%r, 'BENCH'))" % os.path.join(RIM, "Utils")
    held = "driver lock: FREE\nbridge held by %s since x"
    check(g.py("relentless", code % (held % "RELENTLESS")) == "True", "handoff from Relentless sees its own hold")
    check(g.py("conductor", code % (held % "RELENTLESS")) == "False", "handoff from the Conductor does not")
    check(g.py("conductor", code % "bridge FREE") == "False", "handoff reads a free bridge as nobody's")
    code = "import sys; sys.path[:0] = [%r, %r]; import live_session as L; print(L.own_hold(%%r))" % (os.path.join(RIM, "Utils"), os.path.join(RIM, "Utils", "northstar_driver"))
    check(g.py("relentless", code % (held % "RELENTLESS")) == "True", "live_session from Relentless sees its own hold")
    check(g.py("relentless", code % (held % "BENCH")) == "False", "live_session from Relentless refuses the Conductor's")

    rc, out = g.rf("conductor", "bridge", "take", "--for", "the joint session", "--force")
    check(rc == 0 and g.holder() == "BENCH", "the Conductor holds: %s" % out[:80])
    check(p_b1_says(g, "relentless", "BENCH", mirror) == "FAIL", "p_b1 BENCH from Relentless refuses the owner's joint session (the defect)")
    check(p_b1_says(g, "relentless", "RELENTLESS", mirror) == "FAIL", "p_b1 --seat RELENTLESS refuses it too")
    check(p_b1_says(g, "conductor", "BENCH", mirror) == "PASS", "p_b1 from the Conductor passes on his hold")
    check("another seat" in lease_says(g, "relentless", mirror), "preflight_bridge's lease from Relentless reads his hold as another's")
    check("held by this seat" in lease_says(g, "conductor", mirror), "preflight_bridge's lease from the Conductor reads his as his")
    says = wsl_says(g, "relentless")
    check(says == "FAIL", "Pyrelands gate A from Relentless refuses his hold: %s" % says[:90])
    says = wsl_says(g, "conductor")
    check(says == "PASS", "Pyrelands gate A from the Conductor passes on his hold: %s" % says[:90])
    says = window_says(g, "relentless", "BENCH")
    check(says.startswith("False"), "a bridge item is NOT offered to Relentless on his hold: %s" % says[:90])
    check("BENCH is holding" in says, "and the reason names him: %s" % says[:90])
    check(window_says(g, "conductor", "BENCH").startswith("True"), "it is offered to the Conductor on his own")
    check(g.py("relentless", code % (held % "BENCH")) == "False", "live_session from Relentless still refuses it")
    code = "import sys; sys.path.insert(0, %r); import handoff; print(handoff.own_hold(%%r, 'BENCH'))" % os.path.join(RIM, "Utils")
    check(g.py("relentless", code % (held % "BENCH")) == "False", "handoff from Relentless does not call his hold its own")
    check(g.py("conductor", code % (held % "BENCH")) == "True", "handoff from the Conductor does")

    env = dict(g.base, RIMFLOW_SEAT="BENCH")
    env.pop("RIMFLOW_BRIDGE_SEAT", None)
    for script, argv in (("prep_site.py", ["--seat", "RELENTLESS", "--help"]),
                         ("preflight_flowworks.py", ["live", "--seat", "RELENTLESS", "--help"])):
        r = subprocess.run([sys.executable, os.path.join(RIM, "FlowWorks", "northstar", script), *argv], env=env,
                           capture_output=True, text=True, timeout=120, cwd=g.tmp)
        check(r.returncode == 0, "%s takes --seat RELENTLESS: %s" % (script, r.stderr[-120:]))

    # gate C's release, end to end under each name: Relentless releasing must free its own hold, not cross his
    g.rf("relentless", "bridge", "take", "--for", "gate C", "--force")
    rel = g.py("relentless", """import os, subprocess, sys
sys.path.insert(0, %r)
import preflight_pyrelands as P
class Env:
    def run_wsl(self, cmd, timeout=None):
        e = {k: v for k, v in os.environ.items() if k not in ('RIMFLOW_SEAT', 'AGENT_SEAT', 'RIMFLOW_BRIDGE_SEAT')}
        r = subprocess.run(cmd, env=e, capture_output=True, text=True, timeout=timeout, cwd=%r)
        return r.returncode, r.stdout + r.stderr
print(P.c_bridge_released(Env()).status)
""" % (os.path.join(RIM, "Pyrelands"), REPO))
    check(rel == "PASS" and g.holder() == "None", "Pyrelands gate C frees Relentless's own hold: %s %s" % (rel[:80], g.holder()))
    rows = [json.loads(x) for x in open(os.path.join(g.tmp, "events", "RELENTLESS.jsonl"), encoding="utf-8")]
    check(rows and rows[-1].get("state") == "released" and not rows[-1].get("override"), "and that release is Relentless's own, crossing nobody: %s" % (rows[-1:],))
    check(spelled_says(g, "relentless", "RELENTLESS") == "PASS FAIL True", "Pyrelands spells the name out for wsl.exe, and a hold its release left is a FAIL: %s" % spelled_says(g, "relentless", "RELENTLESS"))
    check(spelled_says(g, "conductor", "BENCH") == "PASS FAIL False", "the Conductor's stays bare: %s" % spelled_says(g, "conductor", "BENCH"))

    # the role-file branch of the ambient seat: a window with no seat variable, only its session role file
    role = os.path.join(g.tmp, ".claude", "session_roles")
    os.makedirs(role, exist_ok=True)
    with open(os.path.join(role, "sid"), "w", encoding="utf-8") as f:
        f.write("AGENT-BENCH\n")
    ambient = "from rimflow import model as m; m.ROOT = %r; print(m.ambient_window_seat())" % g.tmp
    check(g.py("relentless", ambient, RIMFLOW_SEAT="", AGENT_SEAT="", CLAUDE_SESSION_ID="sid") == "RELENTLESS", "a role-file seat under Relentless reads RELENTLESS")
    check(g.py("conductor", ambient, RIMFLOW_SEAT="", AGENT_SEAT="", CLAUDE_SESSION_ID="sid") == "BENCH", "and BENCH in his window")

    # host_guard's own door, the one `./game` and bridge tools reach without the cli's rename
    lock = os.path.join(g.tmp, "guard.lock")
    guard = ("import json; from rimflow import host_guard as h; r = h.acquire('BENCH', 'x', path=%r); "
             "print(r.get('ok'), json.load(open(%r)).get('seat') if r.get('ok') else r.get('why'))" % (lock, lock))
    says = g.py("relentless", guard, RM_DRIVER_PID="")
    check(says.endswith("True RELENTLESS"), "host_guard.acquire under Relentless writes RELENTLESS: %s" % says[-120:])

    # a shard of a holder: the ledger routes to it, and a torn one names the repair flag
    sh = "from rimflow import model as m; print(m.shard_path('RELENTLESS', %r).split('/')[-1])" % g.base["RIMFLOW_LEDGER"]
    check(g.py("conductor", sh) == "RELENTLESS.jsonl", "a holder has a shard")
    d = os.path.join(g.tmp, "torn", "events")
    os.makedirs(d)
    torn = os.path.join(d, "RELENTLESS.jsonl")
    with open(torn, "w", encoding="utf-8") as f:
        f.write('{"seat":\n{"seat": "RELENTLESS"}\n')
    says = g.py("conductor", "from rimflow import model as m\ntry:\n    m.read(%r)\nexcept m.LedgerError as e:\n    print(e)" % torn)
    check("--seat RELENTLESS" in says, "a torn holder shard names its repair flag: %s" % says[-120:])
    r = subprocess.run([sys.executable, os.path.join(RIM, "Utils", "repair_torn_ledger.py"), "--seat", "RELENTLESS", "--help"], env=dict(g.base),
                       capture_output=True, text=True, timeout=60, cwd=g.tmp)
    check(r.returncode == 0, "and the repair tool takes that flag: %s" % r.stderr[-90:])

    env_code = "import bridge_holder as B, json; e = B.process_env({'WSLENV': 'X/p'}); print(e['RIMFLOW_BRIDGE_SEAT'], e['WSLENV']); print(B.process_env(e)['WSLENV'])"
    check(g.py("conductor", "import sys; sys.path.insert(0, %r)\n%s" % (os.path.join(RIM, "Utils"), env_code)).split() ==
          ["RELENTLESS", "X/p:RIMFLOW_BRIDGE_SEAT", "X/p:RIMFLOW_BRIDGE_SEAT"], "process_env names the holder and passes it to python.exe, once")
    wsl = "import sys; sys.path.insert(0, %r); import bridge_holder as B; print(' '.join(B.rimflow_env(%%r)))" % os.path.join(RIM, "Utils")
    check(g.py("relentless", wsl % "BENCH") == "AGENT_SEAT=BENCH RIMFLOW_BRIDGE_SEAT=RELENTLESS", "a wsl.exe child of Relentless is spelled out")
    check(g.py("conductor", wsl % "RELENTLESS") == "AGENT_SEAT=BENCH RIMFLOW_BRIDGE_SEAT=RELENTLESS", "and --seat RELENTLESS says the same, BENCH as the ledger seat")
    check(g.py("conductor", wsl % "BENCH") == "AGENT_SEAT=BENCH", "the Conductor's stays bare")
    mirror_read = "import sys; sys.path.insert(0, %r); import bridge_holder as B; print(B.held_by(%%r))" % os.path.join(RIM, "Utils")
    for text, want in (("# head\nHELD    RELENTLESS    since x\nfor     BENCH work\n", "RELENTLESS"),
                       ("# head\nFREE    since x    (released by BENCH)\n", "None"),
                       ("BENCH holds the bridge (fake)\n", "BENCH"), ("", "None")):
        check(g.py("conductor", mirror_read % text) == want, "held_by(%r) is %s" % (text[:30], want))


def main():
    g = Rig()
    try:
        seat_rows(g)
        lock_rows(g)
        restart_hold_rows(g)
        holder_is_not_a_seat(g)
        identity_rows(g)
        holder_check_rows(g)
        wiring_rows()
    finally:
        shutil.rmtree(g.tmp, ignore_errors=True)
    print("FAILED %d" % len(FAILS) if FAILS else "OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
