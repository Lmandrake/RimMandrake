#!/usr/bin/env python3
"""selftest_ops_watch_retired_alarm_item.py -- OPS_WATCH_FIX_RETIRED_ALARM_ITEM: an alarm whose one fixed item was
dropped or superseded files a successor instead of failing "a retired item holds no promise" three times.

Real ops_watch.real_filer against a fake ingest module (a fake clone) that refuses `live` on a retired name as the
ledger does. Expect: the successor is spawned and raised, the filer reports the rename, run_alarms keeps the alarm
OPEN on the successor, and the next repeat reopens the successor (not the retired item)."""
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
TMP = Path(tempfile.mkdtemp(prefix="selftest_ops_retired_alarm_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["RM_DATA_ROOT"] = str(TMP / "data")
(TMP / "ops").mkdir()
ing_dir = TMP / "clone" / "src/RimMandrake/Utils/testq"
ing_dir.mkdir(parents=True)
(ing_dir / "ingest.py").write_text('''
CALLS = []
RETIRED = {"SCRATCH_DIRT_MEASURE_AT_END"}
def rimflow(*a):
    CALLS.append(a)
    if a[0] == "live":
        if a[1] in RETIRED:
            return 1, "%s is dropped: a retired item holds no promise" % a[1]
        return 0, "ok"
    return 0, "ok"
def publish(n, message=""):
    return "published"
''')
import ops_watch as OW  # noqa: E402

FAILS = []


def ok(c, w):
    print(("PASS " if c else "FAIL ") + w)
    if not c:
        FAILS.append(w)


conf = dict(OW.alarm_conf(OW.load_rules()))
conf["clone"] = str(TMP / "clone")
OW.alarm_receiver_problem = lambda c: None
(TMP / "data").mkdir(exist_ok=True)
OW.qhome = lambda: TMP
todo = [{"aid": "X:k", "name": "SCRATCH_DIRT_MEASURE_AT_END", "title": "t", "reopen": True, "expedite": None}]
res = OW.real_filer(todo, conf)
new = (res.get("_renamed") or {}).get("SCRATCH_DIRT_MEASURE_AT_END")
ok(bool(new) and new.startswith("SCRATCH_DIRT_MEASURE_AT_END_"), "retired fixed item: a successor name is filed (%s)" % new)
ok(res.get(new) is None, "the successor filed without error")
ok(todo[0]["name"] == new, "the todo row now names the successor, so run_alarms stores it")
todo2 = [{"aid": "X:k", "name": new, "title": "t", "reopen": True, "expedite": None}]
res2 = OW.real_filer(todo2, conf)
ok(res2.get(new) is None and not res2.get("_renamed"), "next repeat reopens the successor, no further rename")
print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
