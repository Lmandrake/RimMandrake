#!/usr/bin/env python3
"""selftest_graffitiimperial_unmeasured_reason.py -- GRAFFITIIMPERIAL_VALIDATION_FIX_LOST_REASON: in framework_wiring an
UNMEASURED first row (modExtensions shape unreadable) is lifted so the independent rows run; when the next row then
FAILs (the Crown sibling does not resolve), the row after it must be UNMEASURED WITH a reason. The old _comp set
upstream_reason to None, so empire_faction_def_resolves read UNMEASURED with no reason at all. Drives the production
chain through modcheck's real TestContext on a fake bridge. Offline.

    python3 src/RimStarWars/GraffitiImperial/selftest_graffitiimperial_unmeasured_reason.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation as V  # noqa: E402
from modcheck.suite import TestContext  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


class Fake(object):
    def track(self, *a, **k):
        pass

    def call(self, tool, **p):
        d = p.get("defs", "")
        if tool == "jawa/get_defs" and d == "ThingDef/" + V.MARK:
            return {"success": True, "foundCount": 1, "defs": [{"fields": {"modExtensions": ["ModExtension_Graffiti"]}}]}
        if tool == "jawa/get_defs" and d == "ThingDef/" + V.SIBLING:
            return {"success": True, "foundCount": 0, "notFound": [d]}
        return {"success": True, "foundCount": 1}


def main():
    if V.suite is None:
        check("modcheck importable", False)
        return 1
    t = TestContext(Fake())
    dict(V.suite.chains)["framework_wiring"](t)
    v = [(c.name, c.verdict, c.detail) for c in t.components]
    check("sanity: UNMEASURED, FAIL, then a third row", [x[1] for x in v][:2] == ["UNMEASURED", "FAIL"] and len(v) == 3, repr(v))
    check("the row after the FAIL is UNMEASURED", len(v) == 3 and v[2][1] == "UNMEASURED", repr(v[-1:]))
    check("the row after the FAIL carries a reason", len(v) == 3 and bool(v[2][2]), repr(v[-1:]))
    print("graffitiimperial unmeasured reason: %d failure(s) -> %s" % (len(FAILS), "OK" if not FAILS else "FAILED"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
