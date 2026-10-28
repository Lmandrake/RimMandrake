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


def status(accts, hours=None):
    pts = {}
    for a, (rw, wl) in accts.items():
        pts["accounts.%s.runway" % a] = {"m": "MEASURED", "v": rw}
        pts["accounts.%s.week_left_pct" % a] = {"m": "MEASURED", "v": wl}
        pts["accounts.%s.hours_to_reset" % a] = {"m": "MEASURED", "v": (hours or {}).get(a, 30)}
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
    priority(ok, off)
    print("\n%s" % ("FAILED %d" % len(FAILS) if FAILS else "all passed"))
    sys.exit(1 if FAILS else 0)


def priority(ok, off):
    """ACCOUNTPICK_CORRECT_OWNER_PRIORITY: the target is the owner's fixed priority, read from the same file the
    switching plan reads (switching_plan.json `order`), never the soonest reset."""
    import json
    import tempfile
    d = tempfile.mkdtemp(prefix="st_ap_prio_")
    plan = os.path.join(d, "plan.json")
    with open(plan, "w") as f:
        json.dump({"order": ["steven", "system", "lukas"]}, f)
    rule = dict(RULE, priority_plan=plan)
    lent = {"lent_accounts": {"steven": {}}}
    accts = {"lukas": (0.2, 5), "system": (3.0, 90), "steven": (3.0, 90), "zeta": (3.0, 90)}
    hours = {"system": 150, "steven": 160, "zeta": 2, "lukas": 1}
    p = AP.pick(rule, status(accts, hours), "lukas", lent, ok, NOW)
    check(p["state"] == "SWITCH" and p["to"] == "steven",
          "priority: steven fit (lent, in allowance) is first in the owner's order, ahead of a sooner reset (%s)" % p["why"])
    p = AP.pick(rule, status(accts, hours), "lukas", lent, off, NOW)
    check(p["state"] == "SWITCH" and p["to"] == "system",
          "priority: steven off-limits -> system, not the unlisted account resetting soonest (%s)" % p["why"])
    p = AP.pick(rule, status({"lukas": (0.2, 5), "zeta": (3.0, 90), "other": (3.0, 90)}, {"zeta": 9, "other": 3}),
                "lukas", lent, off, NOW)
    check(p["to"] == "other", "priority: accounts outside the order fall back to the schedule's rank (%s)" % p["why"])
    p = AP.pick(dict(RULE, priority_plan=os.path.join(d, "missing.json")), status(accts, hours), "lukas", lent, ok, NOW)
    check(p["state"] == "UNMEASURED" and p["to"] is None,
          "priority: the plan unreadable -> no switch recommended, alarmed (fail closed) (%s)" % p["why"])
    p = AP.pick(rule, status({"system": (3.0, 90), "lukas": (3.0, 90)}), "system", lent, ok, NOW)
    check(p["state"] == "KEEP", "priority: not under the switch line -> KEEP (priority only picks a target)")
    real = AP.load_priority({})
    with open(os.path.join(AP.REPO, "src", "RimMandrake", "Utils", "switching_plan.json")) as f:
        want = json.load(f)["order"]
    check(real == want and real, "priority: the default is switching_plan.json's own order %s" % real)


if __name__ == "__main__":
    main()
