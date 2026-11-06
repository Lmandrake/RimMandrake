#!/usr/bin/env python3
"""selftest_conductor_log_guard.py -- a test's fake alarm cannot reach the real Conductor log, by any writer
(SELFTEST_ALARM_FIX_ESCAPES_INTO_REAL_LOG). Nothing here writes the real log: the "real" path is a temp file, swapped into
the guard's LIVE, so a broken guard fails this test instead of ringing the alarm it exists to stop. The last section READS
the real log (conductor_log_receipt.py): the fake lines are gone, or, behind a checker's wall, the removal's receipt holds."""
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


def relentless_writer(method):
    def write(path):
        got = getattr(R.Effects, method)(types.SimpleNamespace(r={"staffing": {"conductor_log": path}}), "t")
        return got
    return write


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
           ("relentless attention", relentless_writer("conductor_attention")), 
           ("steward", steward_writer), ("dispatcher", dispatcher_writer), ("detached_helper", detached_writer)]
for label, w in WRITERS:
    stays_absent(label, w)
    writes_elsewhere(label, w)

rows = (TMP / "ops" / "alarms_log.jsonl").read_text(encoding="utf-8").splitlines()
check("ops_watch: the refusal is on its alarm log, the alarm's filing untouched",
      any('"conductor_log_failed"' in r and "real Conductor log" in r for r in rows) and any('"filed"' in r for r in rows), rows[-4:])


# ---- the removal: the receipt tool on planted logs, then on the real log, read only. The contract's own `! grep -q` goes
# green on a log it could not read, so this is what fails when the log is dirty, lost or empty.
import conductor_log_receipt as CR  # noqa: E402

said = []
FIX = "- 2026-11-07T11:00:00Z ops_watch ALARM OPS_RED_OVERDUE_CHASE_AEUZ: Ops alarm NIGHTLY_RED_OVERDUE: src/x/selftest_b.py red\n"
REC = TMP / "receipt.json"
CASE = TMP / "conductor"
CASE.mkdir()
PLANT, BACK = CASE / "log.md", TMP / "backup.md"
BACK.write_text("# log\n\n" + FIX + "\n- real line\n\n" + FIX + "\n- last line\n", encoding="utf-8")
PLANT.write_text("# log\n\n- real line\n\n- last line\n- written later\n", encoding="utf-8")
check("record: writes when the log starts with the backup minus its fixtures",
      CR.record(PLANT, BACK, REC, said.append) == CR.OK and json.loads(REC.read_text())["removed_count"] == 2, said)
check("receipt tool: a clean visible log is clean", CR.check(PLANT, REC, said.append) == CR.OK, said)
check("receipt tool: it read the log and says so", "VISIBLE" in said[-1] and "0 fixture lines" in said[-1], said[-1:])

PLANT.write_text("# log\n\n- real line\n\n- something else went\n", encoding="utf-8")
said.clear()
check("record: refuses when more than the fixtures changed", CR.record(PLANT, BACK, TMP / "no.json", said.append) == CR.DIRTY, said)

PLANT.write_text("# log\n" + FIX, encoding="utf-8")
check("receipt tool: a fixture line in the log fails", CR.check(PLANT, REC, said.append) == CR.DIRTY)
PLANT.write_text("# log\n- bare mention src/x/selftest_b.py\n", encoding="utf-8")
check("receipt tool: any trace of the fixture path fails", CR.check(PLANT, REC, said.append) == CR.DIRTY)

(CASE / CR.SIBLING).write_text("{}", encoding="utf-8")
PLANT.write_text("  \n", encoding="utf-8")
check("receipt tool: an empty log in a visible folder is LOST", CR.check(PLANT, REC, said.append) == CR.LOST)
PLANT.unlink()
check("receipt tool: an absent log in a visible folder is LOST", CR.check(PLANT, REC, said.append) == CR.LOST)

(CASE / CR.SIBLING).unlink()
said.clear()
check("receipt tool: a masked folder rests on the receipt", CR.check(PLANT, REC, said.append) == CR.OK, said)
check("receipt tool: a masked folder says the log was NOT read", any("NOT VISIBLE" in s and "NOT read" in s for s in said), said)
for label, edit in (("count", lambda r: r.update(removed_count=9)), ("non-fixture line", lambda r: r["removed"].__setitem__(0, "- real line\n")),
                    ("dropped line", lambda r: r["removed"].pop()), ("same hashes", lambda r: r.update(after_sha256=r["before_sha256"])),
                    ("no shrink", lambda r: r.update(after_bytes=r["before_bytes"]))):
    bad = json.loads(REC.read_text())
    edit(bad)
    TAMPERED = TMP / "tampered.json"
    TAMPERED.write_text(json.dumps(bad), encoding="utf-8")
    check("receipt tool: a masked folder with a bad receipt fails (%s)" % label, CR.check(PLANT, TAMPERED, said.append) == CR.DIRTY)
check("receipt tool: a missing receipt fails", CR.check(PLANT, TMP / "absent.json", said.append) == CR.DIRTY)

said.clear()
code = CR.check(out=said.append)            # the REAL log where it can be seen, the committed receipt everywhere
print("\n".join("  real log: " + s for s in said))
check("the real log holds no fixture line, or is masked and the committed receipt holds", code == CR.OK, said)
real = json.loads(CR.RECEIPT.read_text(encoding="utf-8"))
check("committed receipt: the 18 lines gen 1 counted", real["removed_count"] == 18, real["removed_count"])

print("conductor_log_guard: " + ("FAIL %d" % len(FAILS) if FAILS else "ok"))
sys.exit(1 if FAILS else 0)
