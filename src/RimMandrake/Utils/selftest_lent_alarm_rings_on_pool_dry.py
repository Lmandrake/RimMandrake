#!/usr/bin/env python3
"""selftest_lent_alarm_rings_on_pool_dry.py: a lent account rings no alarm for the plan's own drain; the pool running dry
still rings (RIMMANDRAKE_REAIM_LOAN_RUNWAY_ALARM_WAKES_OPS_AT_EVERY_RESET).

The RUNWAY_LOW target on accounts.*.loan_runway crossed at every reset of the lent seat (35 crossings 2026-11-03..11-26,
each an Operations run; the run of 2026-11-26 01:27Z read 0.24 MEASURED, the account plan NORMAL, no fleet stop in 24 h).
The drain to the leave line is the plan's own work, and a live run that finishes past that line is the plan's account_end.
The danger, the pool dry when the lent window ends, is accounts.fleet_stop_h (FLEET_STOP_NEAR), which runs the account
plan forward through the lent window's expiry. This test runs the SHIPPED rules (ops_watch.load_rules, so a rules file
that the loader refuses fails here, not silently on the live watch) through the real target_state and andon.
"""
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ["RM_OPS_WATCH_DIR"] = tempfile.mkdtemp(prefix="selftest_lent_alarm_")    # no copy of the live rules is read
import ops_watch as OW  # noqa: E402

NOW = 1795700000.0
FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(name)


rules = OW.load_rules()
check("the shipped rules load clean (no last-good fallback)", "_load_error" not in rules, rules.get("_load_error"))
check("no rule row rings on accounts.*.loan_runway", not any(
    t.get("key") == "accounts.*.loan_runway" and t.get("alarm") for t in rules.get("targets", [])))
check("FLEET_STOP_NEAR still rings on accounts.fleet_stop_h", any(
    t.get("key") == "accounts.fleet_stop_h" and t.get("alarm") and t in OW.good_targets(rules)
    for t in rules.get("targets", [])))


def alarms(points):
    st = OW.target_state(points, rules)
    flags = OW.andon(points, {}, {}, {"targets": rules["targets"]}, NOW)
    return sorted(a for a, v in st.items() if v), sorted(f["key"] for f in flags if f.get("rule") == "target")


def lent(loan_v, why):
    return {"accounts.steven.loan_runway": OW.M(loan_v, "x the time to the end of the loan", why=why),
            "accounts.steven.runway": dict(OW.M(0.4, "x the time to reset"), judged_by="accounts.steven.loan_runway"),
            "accounts.steven.week_left_pct": OW.M(85.0, "% of the weekly quota left")}


# 2026-11-26 01:27Z: the fleet on steven, 37 points of loan left, 44.7 h of window, 3.45 %/h -> 0.24; no stop in 24 h
day = {**lent(0.24, "open loan"), "accounts.fleet_stop_h": OW.M(24.0, "h until the plan has no account")}
st, fl = alarms(day)
check("the reading of 2026-11-26 (loan 0.24, no fleet stop) rings nothing", not st and not fl, (st, fl))
# a live run finishing past the leave line: this machine still on the closed loan
st, fl = alarms({**lent(0.0, "this machine is on a closed loan"), "accounts.fleet_stop_h": OW.M(24.0, "h")})
check("a run finishing on the closed loan, no fleet stop, rings nothing", not st and not fl, (st, fl))
# the real danger: the plan runs out of accounts inside 4 h
st, fl = alarms({**lent(0.24, "open loan"), "accounts.fleet_stop_h": OW.M(2.5, "h")})
check("the pool running dry inside 4 h rings FLEET_STOP_NEAR", st == ["FLEET_STOP_NEAR:accounts.fleet_stop_h"]
      and fl == ["accounts.fleet_stop_h"], (st, fl))

# an alarm OPEN when its row is retired: target_state gives it no reading (crossed None), which holds it OPEN forever.
# It leaves with its row; an alarm whose row stands holds as before.
import json  # noqa: E402
# the live shape: an accounts alarm is Operations' own (is_token_key), with no ledger item
st0 = {"RUNWAY_LOW:accounts.steven.loan_runway": {"state": "OPEN", "item": None, "for": "Operations", "since": "x"},
       "RUNWAY_LOW:accounts.lukas.runway": {"state": "OPEN", "item": None, "for": "Operations", "since": "x"}}
(OW.ops_dir()).mkdir(parents=True, exist_ok=True)
(OW.ops_dir() / "alarms.json").write_text(json.dumps(st0))
out = OW.run_alarms({"accounts.steven.loan_runway": OW.M(0.24, "x")}, rules, NOW,
                    set(), lambda todo, conf: {})
check("an OPEN alarm whose target row is retired leaves with its row", "RUNWAY_LOW:accounts.steven.loan_runway" not in out,
      out.get("RUNWAY_LOW:accounts.steven.loan_runway"))
check("an OPEN alarm whose row stands, with no reading, still holds OPEN",
      (out.get("RUNWAY_LOW:accounts.lukas.runway") or {}).get("state") == "OPEN", out.get("RUNWAY_LOW:accounts.lukas.runway"))
logged = [json.loads(x) for x in (OW.ops_dir() / "alarms_log.jsonl").read_text().splitlines()] \
    if (OW.ops_dir() / "alarms_log.jsonl").exists() else []
check("its leaving is logged", any(r.get("event") == "target_removed" and r.get("aid") ==
                                   "RUNWAY_LOW:accounts.steven.loan_runway" for r in logged), logged)

print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
sys.exit(1 if FAILS else 0)
