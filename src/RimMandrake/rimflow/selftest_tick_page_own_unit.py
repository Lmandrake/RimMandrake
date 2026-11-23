#!/usr/bin/env python3
"""selftest_tick_page_own_unit.py: the promises of design/specs/2026-11-23-tick-page-own-unit/boundary.md, one test of
each promise's name. Item RIMMANDRAKE_SLIM_TICK_MEMORY_PAGE_BUILD_HITS_ONE_GIG_TICK_TOOK_FIVE_MIN.

Every tick here runs on temp folders (state dir, dispatcher state, owner hold, conductor log, page output); a selftest
process reads and writes a control store of its own (control.db_path). main() checks that the ledger events are
byte-for-byte unchanged after the run.

  (default)   the three fast promises, a few seconds
  --real      also real-size-applying-tick-under-ceiling: about 2 min on Archmagi, in a systemd user scope
  TICK_PAGE_BASE_DIR=<dir holding a parent maturation_dispatch.py>   runs the same tests on that copy (watch it fail)
"""
import hashlib
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SYSTEMD = os.path.join(REPO, "src", "RimMandrake", "Utils", "systemd")
TMP = tempfile.mkdtemp(prefix="tick_page_own_unit_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(TMP, "mstate")
os.environ["RM_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor.md")
os.environ["RM_OWNER_HOLD_FILE"] = os.path.join(TMP, "mod_owner_hold.json")
os.environ["MATURATION_NOW_OUT"] = os.path.join(TMP, "page")       # a page child, if one runs, writes here
os.environ["RM_STAGE_LAND"] = "1"
for _d in ("state", "mstate", "root/design/concepts"):
    os.makedirs(os.path.join(TMP, _d), exist_ok=True)
sys.path.insert(0, HERE)
if os.environ.get("TICK_PAGE_BASE_DIR"):
    sys.path.insert(0, os.environ["TICK_PAGE_BASE_DIR"])
import maturation_dispatch as MD      # noqa: E402

ROOT = os.path.join(TMP, "root")
FAILS, SEEN = [], []
CEILING = "600M"        # well under the unit's 1G; a dry tick alone measured 344 MB, tick + page child about 670 MB
HANG_S = 1200           # hang guard, not a speed bar: the real-size tick measured about 100 s (2026-11-23)


def ok(name, cond, why=""):
    SEEN.append(name)
    print("%s  %s%s" % ("ok   " if cond else "FAIL ", name, "" if cond else ": %s" % (why,)))
    if not cond:
        FAILS.append(name)
    return cond


class Recorder:
    """Stands in for subprocess.run: a call that starts maturation_now.py is recorded and not run; others run."""

    def __init__(self):
        self.page_calls = []
        self.real = subprocess.run

    def __call__(self, argv, *a, **k):
        parts = argv if isinstance(argv, (list, tuple)) else [argv]
        if any("maturation_now.py" in str(x) for x in parts):
            self.page_calls.append(list(parts))
            return type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        return self.real(argv, *a, **k)

    def __enter__(self):
        subprocess.run = self
        return self

    def __exit__(self, *exc):
        subprocess.run = self.real


def fx(extra=None):
    f = {"autonomy": False, "facts": lambda: {}}
    f.update(extra or {})
    return f


# ---- the promises ---------------------------------------------------------------------------------------------------

def t_applying_tick_starts_no_page_builder():
    with Recorder() as rec:
        rd = MD.tick(ROOT, {"advancing": []}, True, fx=fx())
    ok("applying-tick-starts-no-page-builder: an applying tick called as the unit calls it starts no maturation_now.py",
       not rec.page_calls and "page" not in rd, {"page_calls": rec.page_calls, "page": rd.get("page")})
    seen = {}
    real_tick = MD.tick

    def spy(root, cfg, apply, fx=None, now=None, page=False):
        seen.update(apply=apply, page=page)
        return {"mods": {}, "idle_owed_max_min": 0, "idle_owed_mods": [], "idle_alarm_min": 0, "launched": []}
    MD.tick = spy
    try:
        with open(os.devnull, "w") as dn:
            out, sys.stdout = sys.stdout, dn
            try:
                MD.main(["--root", ROOT, "tick", "--apply"])
            finally:
                sys.stdout = out
    finally:
        MD.tick = real_tick
    ok("applying-tick-starts-no-page-builder: `tick --apply` (the unit's ExecStart) asks the tick for no page",
       seen.get("apply") is True and seen.get("page") is False, seen)


def t_hand_tick_page_still_builds():
    calls = []
    rd = MD.tick(ROOT, {"advancing": []}, True,
                 fx=fx({"page": lambda: (calls.append(1), type("R", (), {"returncode": 0})())[1]}), page=True)
    ok("hand-tick-page-still-builds: tick(apply, page=True) builds the page once", calls == [1]
       and rd.get("page") == "regenerated", {"calls": calls, "page": rd.get("page")})


def _unit(name):
    try:
        with open(os.path.join(SYSTEMD, name), encoding="utf-8") as f:
            return f.read().splitlines()
    except OSError:
        return None


def _limit_has_danger(lines, key):
    """The KEY= line exists and the comment block just above it names a danger (guards or hang guard)."""
    for i, ln in enumerate(lines):
        if ln.startswith(key + "="):
            j, block = i - 1, []
            while j >= 0 and lines[j].startswith("#"):
                block.append(lines[j].lower())
                j -= 1
            text = " ".join(block)
            return ("guard" in text) and ("measured" in text)
    return False


def t_page_has_its_own_unit():
    svc, tmr, disp = _unit("rm-maturation-page.service"), _unit("rm-maturation-page.timer"), _unit(
        "rm-maturation-dispatch.service")
    if not ok("page-has-its-own-unit: the shipped page service, timer and dispatch service are readable",
              svc is not None and tmr is not None and disp is not None, SYSTEMD):
        return
    ex = [ln for ln in svc if ln.startswith("ExecStart=")]
    ok("page-has-its-own-unit: the page service runs Utils/maturation_now.py from the dispatch clone",
       len(ex) == 1 and ex[0].endswith("/home/mandrake/rm/dispatch/src/RimMandrake/Utils/maturation_now.py")
       and "WorkingDirectory=/home/mandrake/rm/dispatch" in svc, ex)
    ok("page-has-its-own-unit: its timer fires a fixed time after each build ends",
       any(ln.startswith("OnUnitInactiveSec=") for ln in tmr), tmr)
    ok("page-has-its-own-unit: MemoryMax and TimeoutStartSec each sit under a comment naming the danger they guard "
       "and the measurement", _limit_has_danger(svc, "MemoryMax") and _limit_has_danger(svc, "TimeoutStartSec"))
    dex = [ln for ln in disp if ln.startswith("ExecStart=")]
    ok("page-has-its-own-unit: the dispatch unit's tick passes no --page",
       len(dex) == 1 and "maturation_dispatch.py tick" in dex[0] and "--page" not in dex[0], dex)


REAL_CHILD = r'''
import os, sys
sys.argv[0] = "selftest_tick_page_own_unit_real_child"     # a test process: its own control store
sys.path.insert(0, os.environ["SELFTEST_HERE"])
if os.environ.get("TICK_PAGE_BASE_DIR"):
    sys.path.insert(0, os.environ["TICK_PAGE_BASE_DIR"])
import maturation_dispatch as MD
MD.REPO = os.environ["SELFTEST_REPO"]      # a parent copy outside the tree still finds the real page builder
facts = MD.gather(os.environ["SELFTEST_REPO"], MD.load_cfg())     # the real read, held for the whole tick as _tick holds it
rd = MD.tick(os.environ["SELFTEST_ROOT"], {"advancing": []}, True, fx={"autonomy": False, "facts": lambda: {}})
print("REAL_CHILD_DONE mods=%d page=%s" % (len(facts), rd.get("page")))
'''


def t_real_size_applying_tick_under_ceiling():
    env = dict(os.environ, SELFTEST_HERE=HERE, SELFTEST_REPO=REPO, SELFTEST_ROOT=ROOT)
    unit = "selftest-tick-page-%d" % os.getpid()
    argv = ["systemd-run", "--user", "--scope", "--quiet", "--unit", unit, "-p", "MemoryMax=" + CEILING,
            "-p", "MemorySwapMax=0", sys.executable, "-c", REAL_CHILD]
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=HANG_S, env=env)
    except subprocess.TimeoutExpired:
        ok("real-size-applying-tick-under-ceiling: the tick ended inside the %d s hang guard" % HANG_S, False, "hung")
        return
    except OSError as e:
        ok("real-size-applying-tick-under-ceiling: systemd-run could be started", False, e)
        return
    out = (r.stdout or "") + (r.stderr or "")
    done = [ln for ln in out.splitlines() if ln.startswith("REAL_CHILD_DONE")]
    ok("real-size-applying-tick-under-ceiling: a real-size applying tick ends with exit 0 in a %s, no-swap cgroup"
       % CEILING, r.returncode == 0 and len(done) == 1,
       "rc %s (137 or a kill: over the ceiling); tail: %s" % (r.returncode, out.strip().splitlines()[-3:]))


def _ledger_digest():
    h = hashlib.sha256()
    d = os.path.join(REPO, "infrastructure", "state", "ledger", "events")
    for nm in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        p = os.path.join(d, nm)
        if os.path.isfile(p):
            with open(p, "rb") as f:
                h.update(nm.encode() + b"\0" + f.read())
    return h.hexdigest()


def main():
    before = _ledger_digest()
    t_applying_tick_starts_no_page_builder()
    t_hand_tick_page_still_builds()
    t_page_has_its_own_unit()
    if "--real" in sys.argv:
        t_real_size_applying_tick_under_ceiling()
    else:
        print("skip  real-size-applying-tick-under-ceiling: run with --real (about 2 min)")
    ok("the run left infrastructure/state/ledger/events/ unchanged", _ledger_digest() == before)
    print("%d of %d checks failed" % (len(FAILS), len(SEEN)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
