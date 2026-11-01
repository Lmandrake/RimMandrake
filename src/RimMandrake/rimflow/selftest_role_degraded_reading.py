#!/usr/bin/env python3
"""A degraded ops reading must not refuse the role that reports the problem (owner-authority brief 2026-11-01:
Operations slot 07:30 REFUSED 'accounts.system.runway is absent'). Planted state: a status.json whose account has no
runway point. A role with `degraded_reading_ok: true` launches on the most cautious reading with an alarm and a
DEGRADED line; the same role without the flag, and every other role, is still REFUSED. Pure: fake observers."""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
os.environ["TZ"] = "UTC"
time.tzset()
import role_launch as RL  # noqa: E402
import selftest_dispatcher as SD  # noqa: E402

FAILS = []


def check(ok, what):
    if not ok:
        FAILS.append(what)
        print("FAIL:", what)


def drive(role):
    t = SD.at_local("07:30")
    status = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t - 60)), "points": {}}
    acts = []
    RL.decide_roles({"roles": [role]}, {"roles": {}}, SD.robs(status), t, lambda **kw: acts.append(kw), set(), None)
    return acts


on = drive(SD.operations(degraded_reading_ok=True, token_aware=True))
launch = [a for a in on if a.get("do") == "role_launch"]
check(len(launch) == 1, "flagged Operations launches on a degraded reading: %r" % [a.get("do") for a in on])
check(any(a.get("do") == "alarm" and a.get("kind") == "role:Operations:ops" and "LAUNCHED on a degraded" in a["why"]
          and "accounts.acct.runway is absent" in a["why"] for a in on), "the degraded launch alarms with the cause")
check(launch and "DEGRADED READING: accounts.acct.runway is absent" in launch[0]["message"] if launch else False,
      "the launch message carries the DEGRADED line")
off = drive(SD.operations())
check(not [a for a in off if a.get("do") == "role_launch"], "unflagged Operations is still refused")
check(any("REFUSED: accounts.acct.runway is absent" in a.get("why", "") for a in off), "unflagged refusal text kept")
cond = drive(SD.conductor(quick_checks_local=["07:30"], degraded_reading_ok=False))
check(not [a for a in cond if a.get("do") == "role_launch"], "a role without the flag stays refused")

# OPERATIONS_FIX_RUNS_BLIND_WHEN_STALE: the stale / missing-or-unreadable status.json / unresolved account readings,
# Operations and the Conductor due at the same tick: Operations launches marked UNMEASURED and told to diagnose the
# watch first, the Conductor is refused.
t = SD.at_local("07:30")
for label, status, acct in (("stale", SD.ops_status(t, age_s=3600), "acct"), ("missing/unreadable", None, "acct"),
                            ("no account", SD.ops_status(t), None)):
    acts = []
    RL.decide_roles({"roles": [SD.operations(degraded_reading_ok=True, token_aware=True),
                               SD.conductor(quick_checks_local=["07:30"])]},
                    {"roles": {}}, SD.robs(status, account=acct), t, lambda **kw: acts.append(kw), set(), None)
    la = [a for a in acts if a.get("do") == "role_launch"]
    check([a["role"] for a in la] == ["Operations"], "%s: only Operations launches: %r" % (label, [a["role"] for a in la]))
    msg = la[0]["message"] if la else ""
    check("is UNMEASURED" in msg and "diagnose the watch first" in msg,
          "%s: the launch message marks the reading UNMEASURED and says diagnose the watch first" % label)
    check(any(a.get("do") == "alarm" and "Conductor" in a.get("why", "") and "REFUSED" in a["why"] for a in acts),
          "%s: the Conductor is refused with an alarm" % label)
if FAILS:
    print("%d FAILED" % len(FAILS))
    sys.exit(1)
print("OK role_degraded_reading")
