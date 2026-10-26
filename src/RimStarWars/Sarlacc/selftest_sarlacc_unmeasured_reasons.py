#!/usr/bin/env python3
"""selftest_sarlacc_unmeasured_reasons.py -- SARLACC_UNMEASURED_FIX_BORROWED_REASON: every row that validation.py
DECLARES unmeasured (the incident and changed-return rows no bridge tool can drive) must carry its OWN reason, not the
first declared row's. Drives the production chains through modcheck's real TestContext on an inert fake bridge.
A control proves the latch still holds: a real FAIL before a declared row still makes that row UNMEASURED upstream.
Offline; no game.

    python3 src/RimStarWars/Sarlacc/selftest_sarlacc_unmeasured_reasons.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation as V  # noqa: E402
from modcheck.suite import TestContext  # noqa: E402

FAILS = []
# a phrase from each declared row's own reason in validation.py
OWN = {
    "swimmer_road_longshade_only": "RSW_SwimmerRoad fires only",
    "swimmer_seep_stillsand_only": "RSW_SwimmerSeepRoot fires only",
    "rooting_evacuates_the_patch": "pawns standing on the patch",
    "take_signs_leave_sand_and_message": "disturbed-sand decal",
    "changed_return_granted_to_a_survivor": "spat free",
    "anchored_mouth_tithe_strike": "mtbStrikeDays",
}


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


class Inert(object):
    def call(self, tool, **p):
        return {"success": True}

    def track(self, *a, **k):
        pass


def run(chain):
    t = TestContext(Inert())
    dict(V.suite.chains)[chain](t)
    return t


def main():
    if V.suite is None:
        check("modcheck importable", False)
        return 1
    rows = {}
    for chain in ("incidents", "changed_return"):
        for c in run(chain).components:
            rows[c.name] = c
    check("sanity: every declared row ran", sorted(rows) == sorted(OWN), repr(sorted(rows)))
    for name, phrase in sorted(OWN.items()):
        c = rows.get(name)
        check("%s is UNMEASURED" % name, c is not None and c.verdict == "UNMEASURED", repr(c and c.verdict))
        check("%s carries its own reason" % name, c is not None and phrase in str(c.detail),
              repr(c and str(c.detail)[:160]))
    # control: a real upstream failure still latches the declared rows (no reason leaks back to 'measured')
    t = TestContext(Inert())
    t.upstream_failed, t.upstream_reason = True, "planted upstream FAIL"
    dict(V.suite.chains)["incidents"](t)
    check("control: after an upstream FAIL every row is UNMEASURED with the upstream reason",
          t.components and all(c.verdict == "UNMEASURED" and "planted upstream FAIL" in str(c.detail) for c in t.components),
          repr([(c.name, c.verdict, str(c.detail)[:60]) for c in t.components]))
    print("sarlacc unmeasured reasons: %d failure(s) -> %s" % (len(FAILS), "OK" if not FAILS else "FAILED"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
