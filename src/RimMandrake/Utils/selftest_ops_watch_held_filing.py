#!/usr/bin/env python3
"""ops_watch files deferred alarms on light beats (ALARM_FILING_FIX_NO_ROOM_AT_INN). Alarms are composed on the beat
that measures COMPOSE_ALARM_FAMILY (8-15 s of the sense phase's 15), whose filer deferred nearly every filing: 8
nightly reds sat PENDING 12-17 passes. Every other compose pass now files what that pass deferred (file_held), inside
the beat's deadline, under the ownership fence; a real failure is left to the alarm pass. Fixture-only: stub
collectors, a stub filer, temp dirs."""
import json
import os
import sys
import tempfile as _tf
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
_TMP = Path(_tf.mkdtemp(prefix="selftest_ops_watch_held_filing_"))
os.environ["RM_OPS_WATCH_DIR"] = str(_TMP / "ops")
os.environ.pop("METRONOME_DEADLINE", None)
import ops_watch as OW  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(name)


OW.COLLECTORS = {f: (lambda fam: lambda now, rules, ctx: {"%s.stub" % fam: OW.M(1, "n")})(f) for f in OW.ORDER}
alarm_runs = []
OW.run_alarms = lambda *a, **k: (alarm_runs.append(1), OW._obj(OW.read_json(OW.ops_dir() / "alarms.json")))[1]
rules = OW.load_rules()
ops = _TMP / "ops"
ops.mkdir(parents=True, exist_ok=True)
AP = ops / "alarms.json"
LOG = ops / "alarms_log.jsonl"
t0 = time.time() - 600
OW.run(now=t0, rules=rules)        # seed every series
alarm_runs.clear()


def seed():
    AP.write_text(json.dumps({
        "NIGHTLY_RED:testing.red_aaaaaa": {"state": "PENDING", "name": "SELFTEST_FIX_HELD_AAAA", "title": "red a",
                                           "deferred_n": 14, "deferred_at": OW.iso(t0), "tries": 0},
        "NIGHTLY_RED:testing.red_bbbbbb": {"state": "PENDING", "name": "SELFTEST_FIX_FAILED_BBBB", "title": "red b",
                                           "error": "no receiver: x", "tries": 3, "last_try": OW.iso(t0)},
        "DISK:disk.full": {"state": "OPEN", "item": "OPS_DISK_FULL_CCCC", "name": "OPS_DISK_FULL_CCCC", "title": "c"},
        "NIGHTLY_RED:testing.red_dddddd": {"state": "PENDING", "name": "SELFTEST_FIX_REOPEN_DDDD", "title": "red d",
                                           "deferred_n": 2, "deferred_at": OW.iso(t0), "reopen": True,
                                           "conductor_log": None, "expedite": ["X"]},
    }))
    if LOG.exists():
        LOG.unlink()


calls = []


def filer_ok(todo, conf):
    dl = OW.beat_deadline()
    calls.append({"names": [a["name"] for a in todo], "todo": todo, "in_time": dl is not None and time.time() < dl})
    return dict({a["name"]: None for a in todo}, _publish="published")


# 1. a light compose pass (no flow) files what the alarm pass deferred, inside the beat deadline
seed()
os.environ["METRONOME_DEADLINE"] = "%.3f" % (time.time() + 15)
OW.run(now=t0 + 60, rules=rules, families=["companion"], compose=True, filer=filer_ok)
st = json.loads(AP.read_text())
a, b, d = (st["NIGHTLY_RED:testing.red_%s" % x] for x in ("aaaaaa", "bbbbbb", "dddddd"))
check("light pass: the alarm pass did not run", alarm_runs == [], alarm_runs)
check("light pass: one filing of the deferred alarms", len(calls) == 1
      and sorted(calls[0]["names"]) == ["SELFTEST_FIX_HELD_AAAA", "SELFTEST_FIX_REOPEN_DDDD"], calls)
check("light pass: it filed inside the beat's deadline", calls and calls[0]["in_time"], calls)
check("light pass: a deferred alarm is OPEN on its item", a.get("state") == "OPEN" and a.get("item") == "SELFTEST_FIX_HELD_AAAA", a)
check("light pass: its deferral stops (deferred_at gone, deferred_n unchanged)", "deferred_at" not in a
      and a.get("deferred_n") == 14, a)
check("light pass: a reopen stays a reopen and keeps its expedite",
      calls and [t for t in calls[0]["todo"] if t["name"] == "SELFTEST_FIX_REOPEN_DDDD"][0]["reopen"] is True
      and [t for t in calls[0]["todo"] if t["name"] == "SELFTEST_FIX_REOPEN_DDDD"][0]["expedite"] == ["X"], calls)
check("light pass: a real failure is not retried there (the alarm pass keeps it)",
      b.get("state") == "PENDING" and b.get("tries") == 3 and b.get("error") == "no receiver: x", b)
check("light pass: an OPEN alarm is untouched", st["DISK:disk.full"]["item"] == "OPS_DISK_FULL_CCCC")
lines = [json.loads(x) for x in LOG.read_text().splitlines()] if LOG.exists() else []
check("light pass: the log says filed, from a held filing",
      sorted(r["aid"] for r in lines if r["event"] == "filed" and r.get("held")) ==
      ["NIGHTLY_RED:testing.red_aaaaaa", "NIGHTLY_RED:testing.red_dddddd"], lines)
status = json.loads((ops / "status.json").read_text())
check("light pass: the status carries the alarms it just filed",
      status["alarms"]["NIGHTLY_RED:testing.red_aaaaaa"]["state"] == "OPEN", status["alarms"].get("NIGHTLY_RED:testing.red_aaaaaa"))

# 2. nothing held: no filing at all
calls.clear()
OW.run(now=t0 + 120, rules=rules, families=["companion"], compose=True, filer=filer_ok)
check("nothing deferred: the light pass files nothing", calls == [], calls)

# 3. a light pass that runs out of time defers again: counted, still held for the next light beat
seed()
OW.run(now=t0 + 180, rules=rules, families=["companion"], compose=True,
       filer=lambda todo, conf: {x["name"]: OW.FILING_DEFERRED for x in todo})
a = json.loads(AP.read_text())["NIGHTLY_RED:testing.red_aaaaaa"]
check("deferred again: PENDING, deferred_n counted, still held", a["state"] == "PENDING" and a["deferred_n"] == 15
      and a.get("deferred_at") == OW.iso(t0 + 180) and not a.get("last_try"), a)

# 4. a held filing that fails for real hands the alarm back to the alarm pass
seed()
OW.run(now=t0 + 240, rules=rules, families=["companion"], compose=True,
       filer=lambda todo, conf: {x["name"]: "rimflow refused" for x in todo})
a = json.loads(AP.read_text())["NIGHTLY_RED:testing.red_aaaaaa"]
check("real failure: the error kept, a try counted, no longer held", a["state"] == "PENDING" and a.get("error") ==
      "rimflow refused" and a.get("tries") == 1 and "deferred_at" not in a, a)

# 5. without --file-alarms nothing is filed
seed()
calls.clear()
OW.run(now=t0 + 300, rules=rules, families=["companion"], compose=True)
check("no filer: nothing filed, the deferral stands", calls == [] and json.loads(AP.read_text())
      ["NIGHTLY_RED:testing.red_aaaaaa"].get("deferred_at"), calls)

# 6. the ownership fence: a fenced generation files nothing
seed()
calls.clear()
try:
    OW.run(now=t0 + 360, rules=rules, families=["companion"], compose=True, filer=filer_ok,
           still_owner=lambda what: "filing" not in what)
    fenced = False
except OW.Fenced:
    fenced = True
check("fence: a fenced pass raises Fenced and files nothing", fenced and calls == [], (fenced, calls))

# 7. the alarm pass's deferral marks the alarm held; its real try clears the mark
state = {"K:k.x": {"state": "PENDING", "name": "N_X_Y", "title": "t"}}
todo = [{"aid": "K:k.x", "name": "N_X_Y", "title": "t"}]
log = []
OW.settle_filing(state, todo, {"N_X_Y": OW.FILING_DEFERRED}, filer_ok, t0, log, set())
check("settle: a deferral stamps deferred_at", state["K:k.x"].get("deferred_at") == OW.iso(t0), state)
OW.settle_filing(state, todo, {"N_X_Y": "boom"}, filer_ok, t0 + 1, log, set())
check("settle: a real try clears deferred_at", "deferred_at" not in state["K:k.x"] and state["K:k.x"]["error"] == "boom", state)

# 8. the pass that measures flow still runs the alarms itself
OW.run(now=t0 + 420, rules=rules, families=["timers", "flow"], compose=True, filer=filer_ok)
check("alarm pass: still composes alarms on the flow beat", alarm_runs == [1], alarm_runs)

os.environ.pop("METRONOME_DEADLINE", None)
print("ALL PASS" if not FAILS else "FAILED: %s" % FAILS)
sys.exit(1 if FAILS else 0)
