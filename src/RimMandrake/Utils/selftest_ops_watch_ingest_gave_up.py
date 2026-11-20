#!/usr/bin/env python3
"""selftest_ops_watch_ingest_gave_up.py — a testq done record whose ingest gave up with an error rings an alarm
(RIMMANDRAKE_RENAME_INGEST_REPAIR_ITEMS_MINT_REFUSES_THEM).

The incident: from 2026-11-05 testq ingest could not spawn a harness repair (the mint rule refused its name). After
MAX_TRIES the record was stamped `ingested` with the refusal in `error`, and nothing read it: 10 repairs were lost over
10 days without a sign.

Proves, on the real ops_watch.c_testing and ops_watch_rules.json:
  1. a record with `ingested.error` counts, a clean `ingested` and a still-pending record do not; the alarm text names
     the job;
  2. no done record reads MEASURED 0, not UNMEASURED or absent;
  3. an unreadable record in the window makes the count an ESTIMATE (a floor), never a clean MEASURED;
  4. the rule exists, is an alarm, and fires above 0.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TMP = Path(tempfile.mkdtemp(prefix="selftest_ingest_gave_up_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["TESTQ_QUEUE"] = str(TMP / "qhome")
os.environ["RM_DATA_ROOT"] = str(TMP / "data")
os.environ["RM_TESTING_METRICS_DIR"] = str(TMP / "metrics")
(TMP / "ops").mkdir()
(TMP / "qhome" / "done").mkdir(parents=True)
import ops_watch as OW  # noqa: E402

FAILS = []
KEY = "testing.ingest_gave_up_7d"


def ok(cond, what, detail=None):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  %r" % (detail,)))
    if not cond:
        FAILS.append(what)


def rec(jid, fin, **extra):
    return (fin, dict({"job": {"id": jid, "mod": "GimmeSomeSlack"},
                       "result": {"attempt": jid + "-a1", "outcome": "INVALID", "started": "2026-11-15T13:00:00Z"}},
                      **extra))


RULES = json.load(open(HERE / "ops_watch_rules.json", encoding="utf-8"))
now = 1795200000.0
lost = rec("J1", now - 3600, ingested={"error": "repair HARNESS_REPAIR_CAUSE_13905C1C not filed: ...", "at": "x"})
fine = rec("J2", now - 3600, ingested={"verified": ["X"], "at": "x"})
pend = rec("J3", now - 3600, ingest_pending={"tries": 2, "error": "repair ... not filed"})

out = OW.c_testing(now, RULES, {"steve_jobs": [lost, fine, pend], "steve_jobs_bad": [], "closes": {}})
p = out.get(KEY) or {}
ok(p.get("m") == "MEASURED" and p.get("v") == 1, "1. one gave-up record counts; clean and pending do not", p)
ok("J1" in json.dumps(p.get("x") or {}), "1. the alarm text names the job", p)

out = OW.c_testing(now, RULES, {"steve_jobs": [], "steve_jobs_bad": [], "closes": {}})
p = out.get(KEY) or {}
ok(p.get("m") == "MEASURED" and p.get("v") == 0, "2. no record reads MEASURED 0", p)

out = OW.c_testing(now, RULES, {"steve_jobs": [lost], "steve_jobs_bad": ["J9.json"], "closes": {}})
p = out.get(KEY) or {}
ok(p.get("m") == "ESTIMATE" and p.get("v") == 1, "3. an unreadable record makes the count a floor (ESTIMATE)", p)

rule = [r for r in RULES["targets"] if isinstance(r, dict) and r.get("key") == KEY]
ok(len(rule) == 1 and rule[0].get("alarm") is True and rule[0].get("op") == ">" and rule[0].get("value") == 0,
   "4. one alarm rule fires above 0", rule)

print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
sys.exit(1 if FAILS else 0)
