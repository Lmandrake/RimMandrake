#!/usr/bin/env python3
"""Selftest of preflight_backtest.apply_audit (RIMMANDRAKE_BACKTEST_PREFLIGHT_OVER_REAL_PAST_TICKETS, criterion A2): a
reader's audit of the table's audit_sample is folded in by the tool, never by hand. audited = rows read, false = rows
whose named fact was false at pickup, and A3 (proposed_for_ticket_4) is recomputed by proposals(). Pure: temp files."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import preflight_backtest as PB  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def row(cid, fires_total, refusing=True):
    return {"id": cid, "group": cid[0], "fires": {"open": fires_total} if fires_total else {}, "fires_total": fires_total,
            "incremental": 0, "incremental_tokens_upper_bound": 0, "refusing": refusing, "audited": 0, "false": None}


def table(n_sample=1):
    items = ["ITEM_%02d" % i for i in range(n_sample)]
    return {"checks": [row("B1", n_sample), row("B4", 0), row("E12", 3), row("C10", 5, refusing=False)],
            "audit_sample": {"B1": [{"item": i, "commit": None, "as_of": "today", "evidence": ["x"]} for i in items],
                             "E12": [{"item": "E_ONE", "commit": "abc", "as_of": "as it was", "evidence": ["y"]}]}}


def audit(rows, reader="Codex (gpt_consult)"):
    return {"reader": reader, "at": "2026-11-18T22:00:00Z", "checks": {"B1": rows}}


t = PB.apply_audit(table(), audit([{"item": "ITEM_00", "verdict": "fact_true", "why": "untracked at pickup"}]))
b1 = next(r for r in t["checks"] if r["id"] == "B1")
check(b1["audited"] == 1 and b1["false"] == 0, "one sample read, its fact true at pickup: audited 1, false 0 (%r)" % b1)
p = {r["id"]: r for r in t["proposed_for_ticket_4"]}
check(p["B1"]["audited"] == 1 and p["B1"]["status"].startswith("stays WARN: 1 audited of the 30 needed"),
      "A3 is recomputed from the audit: B1 stays WARN, 1 of 30 (%r)" % p["B1"]["status"])
check(p["E12"]["status"].startswith("enforce in ticket 4") and "C10" not in p,
      "the owner's checks keep their ruling, a non-refusing check is not proposed")
check(next(r for r in t["checks"] if r["id"] == "B4")["audited"] == 0
      and next(r for r in t["checks"] if r["id"] == "B4")["false"] is None,
      "a check the audit does not name keeps audited 0 and false null (unread, never zero false)")
check(t["audit"]["reader"] == "Codex (gpt_consult)" and t["audit"]["read"] == {"B1": 1},
      "the table names who read it and how many per check: %r" % t.get("audit"))

t2 = PB.apply_audit(t, audit([{"item": "ITEM_00", "verdict": "fact_false", "why": "it was tracked"}]))
b1 = next(r for r in t2["checks"] if r["id"] == "B1")
check(b1["audited"] == 1 and b1["false"] == 1, "re-applying replaces the counts, never adds to them (%r)" % b1)

t30 = PB.apply_audit(table(30), audit([{"item": "ITEM_%02d" % i, "verdict": "fact_true", "why": "w"} for i in range(30)]))
check({r["id"]: r for r in t30["proposed_for_ticket_4"]}["B1"]["status"] == "cleared: may refuse in ticket 4",
      "30 read, none false: cleared for ticket 4")

for bad, what in (([{"item": "NOT_SAMPLED", "verdict": "fact_true", "why": "w"}], "an item not in the sample"),
                  ([{"item": "ITEM_00", "verdict": "probably", "why": "w"}], "a verdict outside fact_true/fact_false"),
                  ([{"item": "ITEM_00", "verdict": "fact_true", "why": " "}], "a verdict with no reason"),
                  ([{"item": "ITEM_00", "verdict": "fact_true", "why": "a"}, {"item": "ITEM_00", "verdict": "fact_true",
                                                                               "why": "b"}], "the same sample read twice")):
    try:
        PB.apply_audit(table(), audit(bad))
        check(False, "refused: %s" % what)
    except ValueError:
        check(True, "refused: %s" % what)
try:
    PB.apply_audit(table(), audit([{"item": "ITEM_00", "verdict": "fact_true", "why": "w"}], reader=""))
    check(False, "refused: an audit naming no reader")
except ValueError:
    check(True, "refused: an audit naming no reader")

with tempfile.TemporaryDirectory() as d:
    tp, ap_ = os.path.join(d, "2026-01-01.json"), os.path.join(d, "2026-01-01.audit.json")
    json.dump(table(), open(tp, "w"))
    json.dump(audit([{"item": "ITEM_00", "verdict": "fact_true", "why": "w"}]), open(ap_, "w"))
    r = subprocess.run([sys.executable, os.path.join(HERE, "preflight_backtest.py"), "--apply-audit", ap_, "--table", tp],
                       capture_output=True, text=True, timeout=60)
    got = json.load(open(tp))
    check(r.returncode == 0 and next(x for x in got["checks"] if x["id"] == "B1")["audited"] == 1
          and "B1 audited 1, false 0" in r.stdout, "the CLI folds the audit into the table in place: %s" % (
              r.stdout.strip() or r.stderr.strip()[-200:]))
    json.dump(audit([{"item": "NOT_SAMPLED", "verdict": "fact_true", "why": "w"}]), open(ap_, "w"))
    before = open(tp).read()
    r = subprocess.run([sys.executable, os.path.join(HERE, "preflight_backtest.py"), "--apply-audit", ap_, "--table", tp],
                       capture_output=True, text=True, timeout=60)
    check(r.returncode != 0 and open(tp).read() == before, "a refused audit exits non-zero and leaves the table untouched")

print("PASS" if not FAILS else "FAILED %d" % len(FAILS))
sys.exit(1 if FAILS else 0)
