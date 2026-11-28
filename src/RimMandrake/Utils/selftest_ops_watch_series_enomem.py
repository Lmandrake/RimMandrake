#!/usr/bin/env python3
"""A failed read of a series file is "could not look", never an alarm (OPS_SCRATCH_OUTSIDE_READING_RESTORE_WLTC).

Instance: 2026-11-28T05:52:18Z, one 9p read of /mnt/d/.../series/disk.jsonl failed with ENOMEM and the compose pass
opened SCRATCH_OUTSIDE_BLIND ("could not read ... disk.jsonl: OSError: [Errno 12] Cannot allocate memory"). The same
read passed at once a moment later. Class: any carried family whose series read fails once.

Three cases, each for disk (disk.scratch_outside_blind) and seats (seats.blind), the two targets that st_suppressed
turns into a measured 1:
  good       the series reads: the carried target is a measured 0 and no alarm opens;
  one_fail   one ENOMEM, then good reads: the read is retried, the target is a measured 0, no alarm opens;
  always     every read fails ENOMEM: the target reads UNMEASURED with the cause, and no alarm opens.
`--against <rev>` replays the instance on ops_watch.py as it stood at that revision: `rimflow guard ... --instance
"--against 59aad62301^"` shows the guard red on the code that opened the false alarm; a bad revision exits 125.
Page: design/specs/2026-11-22-sense-families-cheap/boundary.md. Fixture-only: stub collectors, a temp store."""
import builtins
import errno
import json
import os
import sys
import tempfile as _tf
import time
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
_TMP = Path(_tf.mkdtemp(prefix="selftest_ops_watch_series_enomem_"))
os.environ["RM_OPS_WATCH_DIR"] = str(_TMP / "ops")
os.environ["RM_OPS_WATCH_LIVE_DIR"] = str(_TMP / "live_elsewhere")
os.environ.pop("METRONOME_DEADLINE", None)
if "--against" in sys.argv:     # replay the instance: ops_watch.py's code as it stood at <rev>, run as this tree's file
    import subprocess
    REV = sys.argv[sys.argv.index("--against") + 1]
    r = subprocess.run(["git", "show", "%s:src/RimMandrake/Utils/ops_watch.py" % REV], cwd=HERE, capture_output=True,
                       text=True)
    if r.returncode:    # a typo'd revision shows nothing about the instance: exit 125, which a guard reads as died
        print("COULD NOT LOOK: no ops_watch.py at %s: %s" % (REV, r.stderr.strip()))
        sys.exit(125)
    OW = types.ModuleType("ops_watch")
    OW.__file__ = str(HERE / "ops_watch.py")       # its HERE (rules, rimflow, ops_core) stays this tree
    sys.modules["ops_watch"] = OW
    exec(compile(r.stdout, "ops_watch.py@%s" % REV, "exec"), OW.__dict__)
    print("against %s: ops_watch.py from that revision" % REV)
else:
    import ops_watch as OW  # noqa: E402

FAILS = []
TARGETS = {"disk": ("disk.scratch_outside_blind", "SCRATCH_OUTSIDE_BLIND"), "seats": ("seats.blind", None)}


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(name)


def stub(fam):
    def c(now, rules, ctx):
        pts = {"%s.stub" % fam: OW.M(1, "n")}
        if fam in TARGETS:
            pts[TARGETS[fam][0]] = OW.M(0, "sources not seen", cause="none")
        return pts
    return c


class Flaky:
    """A real open file whose read() raises ENOMEM while the shared budget lasts (the budget counts down per read)."""
    def __init__(self, f, budget):
        self.f, self.budget = f, budget

    def read(self, *a):
        if self.budget["left"] != 0:
            self.budget["left"] -= 1
            raise OSError(errno.ENOMEM, "Cannot allocate memory")
        return self.f.read(*a)

    def __getattr__(self, k):
        return getattr(self.f, k)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.f.close()


OW.COLLECTORS = {f: stub(f) for f in OW.ORDER}
rules = OW.load_rules()
sleeps = []


def quiet_retry():
    """The retry's waits are recorded, not slept (the module that owns the retry, once ops_watch uses it)."""
    di = sys.modules.get("deploy_index")
    if di is not None:
        di.time = types.SimpleNamespace(sleep=sleeps.append, time=time.time)


def run_case(case, fails):
    """-> (status points, alarms filed, budgets left). fails: ENOMEM reads per bad series (-1 = every read)."""
    os.environ["RM_OPS_WATCH_DIR"] = str(_TMP / case)
    t = time.time() - 3600
    OW.run(now=t, rules=rules)                     # a whole pass: every family's series written, its target 0
    budgets = {str(OW.series_path(f)): {"left": fails} for f in TARGETS}
    real_open = builtins.open

    def flaky_open(p, *a, **k):
        f = real_open(p, *a, **k)
        b = budgets.get(str(p))
        return Flaky(f, b) if b is not None else f
    filed = []

    def filer(todo, conf):
        filed.extend(todo)
        return dict({a["name"]: None for a in todo}, _publish="published")
    quiet_retry()
    OW.open = flaky_open
    try:
        OW.run(now=t + 120, rules=rules, families=["flow"], compose=True, filer=filer)
    finally:
        del OW.open
    st = json.loads((_TMP / case / "status.json").read_text())
    return st["points"], filed, budgets


def alarms_on(filed, key):
    return [a.get("name") for a in filed if a.get("key") == key]


def t_good_read():
    pts, filed, _ = run_case("good", 0)
    for fam, (key, _tag) in TARGETS.items():
        p = pts.get(key) or {}
        check("good: %s carried as a measured 0" % key, p.get("m") == "MEASURED" and p.get("v") == 0, p)
        check("good: no %s alarm" % key, not alarms_on(filed, key), alarms_on(filed, key))


def t_one_failed_read_then_good():
    pts, filed, budgets = run_case("one_fail", 1)
    for fam, (key, _tag) in TARGETS.items():
        p = pts.get(key) or {}
        check("one_fail: %s carried as a measured 0" % key, p.get("m") == "MEASURED" and p.get("v") == 0, p)
        check("one_fail: no %s alarm" % key, not alarms_on(filed, key), alarms_on(filed, key))
        check("one_fail: no could-not-read fault is kept for %s" % fam, fam not in OW.SERIES_FAULTS, OW.SERIES_FAULTS)
    check("one_fail: the ENOMEM read was refused once and read again after a wait",
          all(b["left"] == 0 for b in budgets.values()) and bool(sleeps), (budgets, sleeps))


def t_always_failing_read():
    pts, filed, _ = run_case("always", -1)
    for fam, (key, _tag) in TARGETS.items():
        p = pts.get(key) or {}
        why = str(p.get("why"))
        check("always: %s reads UNMEASURED (could not look), not a measured 1" % key, p.get("m") == "UNMEASURED", p)
        check("always: %s names the cause (the file and ENOMEM)" % key,
              "could not read" in why and "Cannot allocate memory" in why and fam + ".jsonl" in why, why)
        check("always: no %s alarm" % key, not alarms_on(filed, key), alarms_on(filed, key))


def main():
    for t in (t_good_read, t_one_failed_read_then_good, t_always_failing_read):
        try:
            t()
        except (Exception, SystemExit) as e:  # noqa: BLE001  a test that raises is a red, named
            check("%s raised %s: %s" % (t.__name__, type(e).__name__, e), False)
    print("selftest_ops_watch_series_enomem: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
