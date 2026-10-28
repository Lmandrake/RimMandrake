#!/usr/bin/env python3
"""Selftest for account_pick.pick: a lent account the machine is ON, off-limits, with no other account fit, is HELD
(never KEEP, which would keep releasing work on it). python3 src/RimMandrake/rimflow/selftest_account_pick.py"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import account_pick as AP  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


NOW = time.time()
RULE = {"enabled": True, "act": "recommend", "hold": ["role_launch", "ring", "recover"],
        "switch_when": {"runway_lt": 0.8, "week_left_pct_lt": 10},
        "target_min": {"runway_ge": 1.2, "week_left_pct_ge": 20, "m": ["MEASURED"]},
        "rank": "soonest_reset", "lent_min_draw_pct": 10}
LENT = {"lent_accounts": {"borrowed": {}}}


def status(accts):
    pts = {}
    for a, (rw, wl) in accts.items():
        pts["accounts.%s.runway" % a] = {"m": "MEASURED", "v": rw}
        pts["accounts.%s.week_left_pct" % a] = {"m": "MEASURED", "v": wl}
        pts["accounts.%s.hours_to_reset" % a] = {"m": "MEASURED", "v": 30}
    return {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(NOW - 60)), "alarms": {}, "points": pts}


def main():
    off = lambda view, rules, now: (0.0, "off-limits")      # noqa: E731
    ok = lambda view, rules, now: (50.0, "fine")            # noqa: E731
    st = status({"borrowed": (2.0, 50), "mine": (0.2, 5)})
    p = AP.pick(RULE, st, "borrowed", LENT, off, NOW)
    check(p["state"] == "HOLD" and p["hold"], "lent current, off-limits, no other fit -> HOLD + hold (not KEEP)")
    p = AP.pick(RULE, status({"borrowed": (2.0, 50), "mine": (3.0, 60)}), "borrowed", LENT, off, NOW)
    check(p["state"] == "SWITCH" and p["to"] == "mine", "lent current, off-limits, an owned account fit -> SWITCH")
    p = AP.pick(RULE, st, "borrowed", LENT, ok, NOW)
    check(p["state"] == "KEEP" and not p["hold"], "lent current within its allowance -> KEEP")
    p = AP.pick(RULE, status({"mine": (0.2, 5)}), "mine", LENT, off, NOW)
    check(p["state"] == "KEEP" and not p["hold"], "owned current under the line, none fit -> KEEP (bands pace it)")
    # review night: a zero allowance is off-limits whatever lent_min_draw_pct says (0 or omitted must not open it)
    r0 = dict(RULE, lent_min_draw_pct=0)
    p = AP.pick(r0, st, "borrowed", LENT, off, NOW)
    check(p["state"] == "HOLD" and p["hold"], "min draw 0: lent current at allowance 0, none fit -> HOLD, not KEEP")
    p = AP.pick(r0, status({"borrowed": (2.0, 50), "mine": (0.2, 5)}), "mine", LENT, off, NOW)
    check(p["state"] == "KEEP" and p["to"] is None, "min draw 0: an off-limits lent account is never a SWITCH target")
    print("\n%s" % ("FAILED %d" % len(FAILS) if FAILS else "all passed"))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
