#!/usr/bin/env python3
"""selftest_conductor_log_guard.py -- a test's fake alarm cannot reach the real Conductor log, by any writer
(SELFTEST_ALARM_FIX_ESCAPES_INTO_REAL_LOG). Nothing here touches the real log: the "real" path is a temp file, swapped into
the guard's LIVE, so a broken guard fails this test instead of ringing the alarm it exists to stop."""
import json
import os
import subprocess
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
RIMFLOW = HERE.parent / "rimflow"
sys.path[:0] = [str(HERE), str(RIMFLOW), str(HERE / "testq")]
TMP = Path(tempfile.mkdtemp())
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["RM_DISPATCHER_STATE"] = str(TMP / "dispatcher")
(TMP / "ops").mkdir()
import conductor_log_guard as G  # noqa: E402
import ops_watch as OW  # noqa: E402

FAILS = []
REAL_LIVE = G.LIVE
FAKE_LIVE = TMP / "real_log_stand_in.md"
OTHER = TMP / "a_tests_own_log.md"


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -- %s" % (detail,)))
    if not cond:
        FAILS.append(name)


# ---- the guard cannot go blind: every rules file names the path it protects
ops_rules = json.loads((HERE / "ops_watch_rules.json").read_text(encoding="utf-8"))
paths = {t["conductor_log"] for t in ops_rules["targets"] if t.get("conductor_log")}
check("ops_watch_rules: at least one target owes the Conductor a line", paths)
paths.add(json.loads((RIMFLOW / "relentless_rules.json").read_text(encoding="utf-8"))["staffing"]["conductor_log"])
paths.add(json.loads((RIMFLOW / "dispatcher_schedule.json").read_text(encoding="utf-8"))["no_handoff"]["conductor_log"])
check("every rules file's Conductor log is the path the guard protects", paths == {REAL_LIVE}, paths)


# ---- who is a test process: read in a child of each shape, which writes nothing
def child(name, under):
    script = TMP / name
    script.write_text("import sys\nsys.path.insert(0, %r)\nimport conductor_log_guard as G\n"
                      "try:\n    G.refuse_if_test(%r)\nexcept G.TestWroteLiveLog:\n    sys.exit(7)\n" % (str(RIMFLOW), REAL_LIVE), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != G.UNDER_SELFTEST}
    if under:
        env[G.UNDER_SELFTEST] = "1"
    return subprocess.run([sys.executable, str(script)], env=env, capture_output=True, text=True, timeout=60).returncode


check("production: an ordinary program may write the real log", child("ops_watch_like.py", False) == 0)
check("a selftest run by hand is a test process", child("selftest_by_hand.py", False) == 7)
check("anything under run_selftests is a test process, whatever its name", child("ops_watch_like.py", True) == 7)


# ---- run_selftests really marks its children: a fixture repo through the real runner
def runner_marks_children():
    root = TMP / "fixture_repo"
    (root / "src").mkdir(parents=True)
    said = TMP / "said.txt"
    (root / "src" / "selftest_probe.py").write_text(
        "import os, pathlib\npathlib.Path(%r).write_text(os.environ.get(%r, 'unset'))\n" % (str(said), G.UNDER_SELFTEST), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != G.UNDER_SELFTEST}
    env.update(RM_SELFTEST_REPO_ROOT=str(root), RM_SELFTEST_STATE_DIR=str(TMP / "state"), RM_SELFTEST_LOCK=str(TMP / "lock"),
               RM_SELFTEST_CACHE_DIR=str(TMP / "cache"), RM_SELFTEST_SKIP_DISK_GUARD="1", RM_SELFTEST_NO_HARNESS="1")
    env.pop("RM_SELFTEST_NESTED", None)
    r = subprocess.run([sys.executable, str(HERE / "run_selftests.py"), "--only", "src/selftest_probe.py"],
                       cwd=root, env=env, capture_output=True, text=True, timeout=120)
    return said.read_text() if said.exists() else "probe never ran: rc %s %s" % (r.returncode, (r.stdout + r.stderr)[-300:])


said = runner_marks_children()
check("run_selftests marks every child as a test process", said == "1", said)

# ---- every writer, in this (test) process: the stand-in real log stays absent, a test's own log still works
G.LIVE = str(FAKE_LIVE)


def stays_absent(name, write):
    FAKE_LIVE.unlink(missing_ok=True)
    try:
        write(str(FAKE_LIVE))
    except OSError:
        pass
    check("%s: a test's write to the real log is refused" % name, not FAKE_LIVE.exists())


def writes_elsewhere(name, write):
    OTHER.unlink(missing_ok=True)
    write(str(OTHER))
    check("%s: a test's own temp log is still written" % name, OTHER.exists() and OTHER.read_text(encoding="utf-8").strip())


def ops_watch_writer(path):
    """TE1's shape: the real rules, the real alarm step, an overdue alarm, the Conductor line left unredirected."""
    rules = json.loads((HERE / "ops_watch_rules.json").read_text(encoding="utf-8"))
    for t in rules["targets"]:
        if t.get("conductor_log"):
            t["conductor_log"] = path
    (TMP / "ops" / "alarms.json").unlink(missing_ok=True)
    pt = {"testing.nightly_reds_overdue": {"t": 0, "v": 1, "m": "MEASURED", "x": {"said": "src/x/selftest_b.py red"}}}
    OW.conductor_line_owed = lambda key, said: True     # the told ledger is its own test's; here the line is always owed
    OW.run_alarms(pt, rules, 1.0, set(), lambda todo, conf: {a["name"]: None for a in todo}, set())


import relentless as R  # noqa: E402
import dispatcher as D  # noqa: E402
import detached_helper as DH  # noqa: E402
import replay_watch as RW  # noqa: E402


def relentless_writer(method):
    def write(path):
        got = getattr(R.Effects, method)(types.SimpleNamespace(r={"staffing": {"conductor_log": path}}), "t")
        return got
    return write


def replay_writer(path):
    sched = TMP / "sched.json"
    sched.write_text(json.dumps({"no_handoff": {"conductor_log": path}}), encoding="utf-8")
    RW.World.conductor(types.SimpleNamespace(cfg={"schedule": str(sched)}), "line\n")


def steward_writer(path):
    import steward as S
    os.environ["TESTQ_CONDUCTOR_LOG"] = path
    S.conductor_raise("why", "first", 1.0)


def dispatcher_writer(path):
    os.environ.pop("RM_DISPATCHER_STATE", None)     # its older guard keys on this; the shared guard must stand alone
    try:
        D.conductor_log({"no_handoff": {"conductor_log": path}}, {"kind": "k", "why": "w", "seat": "BENCH"}, 1.0)
    finally:
        os.environ["RM_DISPATCHER_STATE"] = str(TMP / "dispatcher")


def detached_writer(path):
    os.environ.pop("RM_DISPATCHER_STATE", None)
    try:
        DH.conductor_line("t", 1.0, path=path)
    finally:
        os.environ["RM_DISPATCHER_STATE"] = str(TMP / "dispatcher")


WRITERS = [("ops_watch", ops_watch_writer), ("relentless jam", relentless_writer("conductor_alarm")),
           ("relentless attention", relentless_writer("conductor_attention")), ("replay_watch", replay_writer),
           ("steward", steward_writer), ("dispatcher", dispatcher_writer), ("detached_helper", detached_writer)]
for label, w in WRITERS:
    stays_absent(label, w)
    writes_elsewhere(label, w)

rows = (TMP / "ops" / "alarms_log.jsonl").read_text(encoding="utf-8").splitlines()
check("ops_watch: the refusal is on its alarm log, the alarm's filing untouched",
      any('"conductor_log_failed"' in r and "real Conductor log" in r for r in rows) and any('"filed"' in r for r in rows), rows[-4:])

print("conductor_log_guard: " + ("FAIL %d" % len(FAILS) if FAILS else "ok"))
sys.exit(1 if FAILS else 0)
