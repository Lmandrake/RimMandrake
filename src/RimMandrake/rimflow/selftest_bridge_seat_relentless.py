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
    finally:
        shutil.rmtree(d, ignore_errors=True)

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


def main():
    g = Rig()
    try:
        seat_rows(g)
        lock_rows(g)
        holder_is_not_a_seat(g)
        identity_rows(g)
        wiring_rows()
    finally:
        shutil.rmtree(g.tmp, ignore_errors=True)
    print("FAILED %d" % len(FAILS) if FAILS else "OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
