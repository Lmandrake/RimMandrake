#!/usr/bin/env python3
"""Selftest of the per-machine tree-check line (treecheck_slots.py, publish.py door_checks).
Page: design/specs/2026-11-24-treecheck-slots/boundary.md. One test per promise, named as the promise.

    python3 selftest_treecheck_slots.py              the promises (exit 0 all green, 1 a red)
    python3 selftest_treecheck_slots.py --mutants    plant each fault in a copy of treecheck_slots.py and require a red
                                                     (exit 0 every plant caught, 1 a plant got past, 2 the harness broke)
TREECHECK_SLOTS_UNDER_TEST=<file> runs the promises against that copy of the module (the --mutants harness sets it).
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
UNDER = os.environ.get("TREECHECK_SLOTS_UNDER_TEST") or os.path.join(HERE, "treecheck_slots.py")


def load_slots():
    spec = importlib.util.spec_from_file_location("treecheck_slots", UNDER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["treecheck_slots"] = m
    spec.loader.exec_module(m)
    return m


TS = load_slots()
assert os.path.realpath(TS.__file__) == os.path.realpath(UNDER), "imported %s, not %s" % (TS.__file__, UNDER)
BASE = tempfile.mkdtemp(prefix="tcslots-", dir=os.path.expanduser("~/.cache"))
os.environ["PUBLISH_RM_ROOT"] = BASE
os.environ.pop(TS.HELD_ENV, None)
import publish as P  # noqa: E402  (after treecheck_slots is in sys.modules: publish uses the module under test)
import time_budget  # noqa: E402
P.RM_ROOT = BASE
__import__("atexit").register(shutil.rmtree, BASE, True)
FAILS = []

# one waiter or holder in its own process: take a slot, log in/out with times, hold it for HOLD seconds
DRIVER = r'''
import importlib.util, os, sys, time
spec = importlib.util.spec_from_file_location("treecheck_slots", sys.argv[1]); m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
root, n, name, hold, log = sys.argv[2], int(sys.argv[3]), sys.argv[4], float(sys.argv[5]), sys.argv[6]
def w(s):
    with open(log, "a") as f:
        f.write("%s %s %.6f\n" % (s, name, time.time()))
w("asked")
with m.Gate(root, n=n, say_s=0.5, poll_s=0.05) as g:
    g.take("tree checks")
    w("in"); time.sleep(hold); w("out")
'''


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what, flush=True)
    if not ok:
        FAILS.append(what)


def drive(root, n, name, hold, log, **kw):
    return subprocess.Popen([sys.executable, "-c", DRIVER, UNDER, root, str(n), name, str(hold), log],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, **kw)


def events(log):
    out = []
    if os.path.isfile(log):
        for ln in open(log):
            k, name, t = ln.split()
            out.append((float(t), k, name))
    # an end and the next start in one clock tick: the end sorts first (the next start came after the drop)
    return sorted(out, key=lambda e: (e[0], e[1] not in ("out", "end")))


def max_overlap(evs):
    cur = top = 0
    for _t, k, _n in evs:
        if k in ("in", "start"):
            cur += 1
            top = max(top, cur)
        elif k in ("out", "end"):
            cur -= 1
    return top


def g(*a, cwd):
    subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True)


PROBE = r'''
import os, sys, time
log = os.environ["TCSLOTS_PROBE_LOG"]
def w(k):
    with open(log, "a") as f:
        f.write("%s %s %.6f\n" % (k, "%d:%s" % (os.getpid(), os.environ.get("RM_TREECHECK_SLOT_HELD", "-")), time.time()))
w("start"); time.sleep(float(sys.argv[1]) if len(sys.argv) > 1 else 1.5); w("end")
print("probe green")
'''


def door_repo(tmp, pipeline=False):
    """A git work tree whose door runs one probe check (and, with pipeline=True, one pipeline test, also the probe)."""
    repo = os.path.join(tmp, "repo")
    os.makedirs(os.path.join(repo, os.path.dirname(P.TREE_CHECKS)))
    open(os.path.join(repo, "probe.py"), "w").write(PROBE)
    json.dump({"timeout_s": 120, "skip_when_only": ["ledger/*.jsonl"], "checks": [{"test": "probe.py", "fix": "f"}]},
              open(os.path.join(repo, P.TREE_CHECKS), "w"))
    if pipeline:
        json.dump({"timeout_s": 120, "pipeline_files": ["pipe/*.py"],
                   "tests": [{"test": "probe.py", "inputs": ["pipe/*.py"]}]},
                  open(os.path.join(repo, P.PIPELINE_TESTS), "w"))
    os.makedirs(os.path.join(repo, "pipe"))
    open(os.path.join(repo, "pipe", "a.py"), "w").write("x = 1\n")
    g("init", "-q", "-b", "main", repo, cwd=tmp)
    for k, v in (("user.name", "t"), ("user.email", "t@example.invalid"), ("core.hooksPath", "/dev/null")):
        g("config", k, v, cwd=repo)
    g("add", "-A", cwd=repo)
    g("commit", "-q", "-m", "base", cwd=repo)
    return repo


# ---- the promises ----------------------------------------------------------------------------------------------

DOOR = r'''
import importlib.util, os, sys
spec = importlib.util.spec_from_file_location("treecheck_slots", sys.argv[1]); m = importlib.util.module_from_spec(spec)
sys.modules["treecheck_slots"] = m; spec.loader.exec_module(m)
sys.path.insert(0, sys.argv[2])
import publish as P
try:
    (getattr(P, "door_checks", None) or (lambda t, c: (P.tree_checks(t, c), P.pipeline_checks(t, c))))(sys.argv[3], ["src/x.py"])
    print("DOOR GREEN")
except P.Refuse as e:
    print("DOOR RED %s" % e)
'''


def t_at_most_the_limit_run_at_once(tmp):
    """Four publishes reach the door at once with the limit at 2: at most 2 probes overlap, and all four go green."""
    repo = door_repo(tmp)
    log = os.path.join(tmp, "probe.log")
    env = dict(os.environ, TCSLOTS_PROBE_LOG=log, PUBLISH_RM_ROOT=BASE, RM_TREECHECK_SLOTS="2")
    env.pop(TS.HELD_ENV, None)
    ps = [subprocess.Popen([sys.executable, "-c", DOOR, UNDER, HERE, repo], env=env, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, text=True) for _ in range(4)]
    outs = [p.communicate(timeout=time_budget.CALL_S)[0] for p in ps]
    evs = events(log)
    starts = sum(1 for e in evs if e[1] == "start")
    check(starts == 4, "at-most-the-limit-run-at-once: the probe ran once per publish (%d of 4)" % starts)
    check(sum("DOOR GREEN" in o for o in outs) == 4, "at-most-the-limit-run-at-once: all four publishes went green (%s)"
          % [o.strip().splitlines()[-1:] for o in outs])
    top = max_overlap(evs)
    check(top <= 2 and starts == 4, "at-most-the-limit-run-at-once: at most 2 probes ran at once (%d)" % top)


def t_waiters_go_first_come_first_served(tmp):
    root, log = os.path.join(tmp, "gate"), os.path.join(tmp, "fifo.log")
    holder = drive(root, 1, "H", 1.5, log)
    time.sleep(0.5)
    ws = []
    for name in ("W1", "W2", "W3", "W4"):
        ws.append(drive(root, 1, name, 0.2, log))
        time.sleep(0.25)
    for p in [holder] + ws:
        p.communicate(timeout=time_budget.CALL_S)
    order = [n for _t, k, n in events(log) if k == "in"]
    check(order == ["H", "W1", "W2", "W3", "W4"], "waiters-go-first-come-first-served: order %s" % order)
    check(max_overlap(events(log)) == 1, "waiters-go-first-come-first-served: one at a time with the limit at 1")


def t_a_dead_holder_frees_its_slot(tmp):
    root, log = os.path.join(tmp, "gate"), os.path.join(tmp, "dead.log")
    holder = drive(root, 1, "H", 60, log)
    deadline = time.time() + 20
    while not any(k == "in" for _t, k, _n in events(log)) and time.time() < deadline:
        time.sleep(0.05)
    dead_waiter = drive(root, 1, "D", 0.2, log)       # a waiter that dies in the line
    time.sleep(0.4)
    w = drive(root, 1, "W", 0.2, log)
    time.sleep(0.4)
    dead_waiter.send_signal(signal.SIGKILL)
    dead_waiter.communicate()
    killed_at = time.time()
    holder.send_signal(signal.SIGKILL)
    holder.communicate()
    try:
        # budget: danger=a waiter that never gets the slot (the dead-holder-never-freed plant) holds the test with no end;
        # budget: evidence=the plant; longest=0.01s (the waiter took the slot 0.01 s after the kill, 2026-11-24), 1000x
        w.communicate(timeout=10)
        done = True
    except subprocess.TimeoutExpired:
        w.kill()
        w.communicate()
        done = False
    ins = [(t, n) for t, k, n in events(log) if k == "in" and n == "W"]
    check(done and ins and ins[0][0] - killed_at < 3.0,
          "a-dead-holder-frees-its-slot: the waiter behind a killed holder and a killed waiter took the slot (%s)"
          % ("%.2f s after the kill" % (ins[0][0] - killed_at) if ins else "never"))
    left = [n for n in os.listdir(os.path.join(root, "queue"))] if os.path.isdir(os.path.join(root, "queue")) else []
    check(left == [], "a-dead-holder-frees-its-slot: the dead waiter's ticket left the line (%s)" % left)


def t_a_waiter_shows_progress(tmp):
    root, log = os.path.join(tmp, "gate"), os.path.join(tmp, "say.log")
    holder = drive(root, 1, "H", 2.0, log)
    time.sleep(0.4)
    w = drive(root, 1, "W", 0.1, log)
    holder.communicate(timeout=time_budget.CALL_S)
    out = w.communicate(timeout=time_budget.CALL_S)[0]
    lines = [ln for ln in out.splitlines() if "waiting" in ln and "for a tree-check slot" in ln]
    check(len(lines) >= 2 and "0 ahead, 1 running (pid %d)" % holder.pid in lines[0],
          "a-waiter-shows-progress: %d waiting lines, the first %r" % (len(lines), lines[:1]))


def t_one_publish_holds_one_slot_across_both_checks(tmp):
    repo = door_repo(tmp, pipeline=True)
    log = os.path.join(tmp, "both.log")
    os.environ["TCSLOTS_PROBE_LOG"] = log
    takes = []
    real = TS.Gate.take

    def counted(self, what="tree checks"):
        had = self.fd
        real(self, what)
        if had is None and self.fd is not None:
            takes.append(what)
    TS.Gate.take = counted
    try:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            err = None
            try:
                P.door_checks(repo, ["pipe/a.py"]) if hasattr(P, "door_checks") else (
                    P.tree_checks(repo, ["pipe/a.py"]), P.pipeline_checks(repo, ["pipe/a.py"]))
            except P.Refuse as e:
                err = str(e)
    finally:
        TS.Gate.take = real
        os.environ.pop("TCSLOTS_PROBE_LOG", None)
    held = [n.split(":")[1] for _t, k, n in events(log) if k == "start"]
    check(err is None and len(held) == 2, "one-publish-holds-one-slot-across-both-checks: both checks ran (%s, %s)"
          % (held, err))
    check(len(takes) == 1 and held and len(set(held)) == 1 and held[0] == str(os.getpid()),
          "one-publish-holds-one-slot-across-both-checks: one slot taken (%s), held by this publish in both (%s)"
          % (takes, held))
    check(not os.environ.get(TS.HELD_ENV), "one-publish-holds-one-slot-across-both-checks: the slot is dropped after")


def t_a_check_under_a_held_slot_never_waits_again(tmp):
    root, log = os.path.join(tmp, "gate"), os.path.join(tmp, "nest.log")
    holder = drive(root, 1, "H", 3.0, log)
    time.sleep(0.4)
    env = dict(os.environ, **{TS.HELD_ENV: str(holder.pid)})
    t0 = time.time()
    child = drive(root, 1, "C", 0.0, log, env=env)
    child.communicate(timeout=time_budget.CALL_S)
    took = time.time() - t0
    holder.communicate(timeout=time_budget.CALL_S)
    check(took < 2.0, "a-check-under-a-held-slot-never-waits-again: a child of a holder passed in %.2f s" % took)


def t_a_publish_with_no_door_checks_takes_no_slot(tmp):
    repo = door_repo(tmp, pipeline=True)
    takes = []
    real = TS.Gate.take
    TS.Gate.take = lambda self, what="tree checks": takes.append(what)
    try:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            P.door_checks(repo, ["ledger/BENCH.jsonl"]) if hasattr(P, "door_checks") else None
    finally:
        TS.Gate.take = real
    check(hasattr(P, "door_checks") and takes == [],
          "a-publish-with-no-door-checks-takes-no-slot: a ledger-only change asked for %s" % takes)


def main():
    for t in (t_at_most_the_limit_run_at_once, t_waiters_go_first_come_first_served, t_a_dead_holder_frees_its_slot,
              t_a_waiter_shows_progress, t_one_publish_holds_one_slot_across_both_checks,
              t_a_check_under_a_held_slot_never_waits_again, t_a_publish_with_no_door_checks_takes_no_slot):
        tmp = tempfile.mkdtemp(prefix=t.__name__[2:20] + "-", dir=BASE)
        try:
            t(tmp)
        except Exception as e:                       # a crash of one test is a red of that promise, named
            check(False, "%s crashed: %r" % (t.__name__[2:].replace("_", "-"), e))
        os.environ["PUBLISH_RM_ROOT"] = BASE
    print("%s: %d red" % ("RED" if FAILS else "GREEN", len(FAILS)))
    return 1 if FAILS else 0


# ---- the plants (--mutants) --------------------------------------------------------------------------------------

PLANTS = [
    ("gate-ignored", "at-most-the-limit-run-at-once",
     '        if self.fd is not None or os.environ.get(HELD_ENV):\n            return\n',
     '        return\n'),
    ("dead-holder-never-freed", "a-dead-holder-frees-its-slot",     # a slot is a file that exists, not a held lock
     '                        fd = _try_lock(p, keep=True)\n',
     '                        fd = HELD if os.path.exists(p + ".held") else _try_lock(p, keep=True)\n'
     '                        if fd != HELD:\n                            open(p + ".held", "w").close()\n'
     '                            self.mpath = p + ".held"\n'),
    ("no-waiting-line", "a-waiter-shows-progress",
     '                    self.say("waiting %d s', '                    0 and self.say("waiting %d s'),
    ("held-env-ignored", "a-check-under-a-held-slot-never-waits-again",
     'if self.fd is not None or os.environ.get(HELD_ENV):', 'if self.fd is not None:'),
]
UNPLANT_DROP = ('            os.close(self.fd)                            # closing releases the flock\n',
                '            os.close(self.fd)\n            os.unlink(self.mpath)\n')


def mutants():
    src = open(os.path.join(HERE, "treecheck_slots.py")).read()
    tmp = tempfile.mkdtemp(prefix="tcmut-", dir=BASE)
    env = dict(os.environ)
    env.pop(TS.HELD_ENV, None)

    def run_copy(text, label):
        p = os.path.join(tmp, label, "treecheck_slots.py")
        os.makedirs(os.path.dirname(p))
        open(p, "w").write(text)
        r = subprocess.run([sys.executable, os.path.abspath(__file__)], env=dict(env, TREECHECK_SLOTS_UNDER_TEST=p),
                           capture_output=True, text=True, timeout=time_budget.CALL_S)
        return r.returncode, r.stdout + r.stderr
    rc, o = run_copy(src, "control")
    if rc != 0:
        print("HARNESS BROKEN: the unmutated copy is red:\n" + o)
        return 2
    print("ok   control: the unmutated copy is green")
    missed = []
    for name, promise, old, new in PLANTS:
        if old not in src:
            print("HARNESS BROKEN: plant %s no longer applies" % name)
            return 2
        text = src.replace(old, new, 1)
        if name == "dead-holder-never-freed":
            text = text.replace(*UNPLANT_DROP)
        rc, o = run_copy(text, name)
        red = [ln for ln in o.splitlines() if ln.startswith("FAIL ") and promise in ln]
        print(("ok   " if red else "MISS ") + "plant %s: %s" % (name, red[0] if red else "no red on " + promise))
        if not red:
            missed.append(name)
    print("%s: %d of %d plants caught" % ("GREEN" if not missed else "RED", len(PLANTS) - len(missed), len(PLANTS)))
    return 1 if missed else 0


if __name__ == "__main__":
    sys.exit(mutants() if "--mutants" in sys.argv else main())
