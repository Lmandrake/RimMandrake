#!/usr/bin/env python3
"""selftest_gizka_validation_chains.py -- GIZKA_VALIDATION_FIX_LOST_REASON_DONOR_PICK: two harness faults in
validation.py, driven through modcheck's real TestContext on a fake bridge (no game):
  * harmony_wiring: hook 1 UNMEASURED, hook 2 a real FAIL -> every row after the FAIL must be UNMEASURED WITH a reason
    (the old _comp cleared upstream_reason to None, so the rows after a later FAIL carried no reason at all);
  * donor_patch: with both the donor `Gizka` and the port `RSW_Gizka` loaded, only RSW_Gizka is patched to 15
    (RSW_GizkaDonorPatches.xml; the donor block was deleted), so the row must read RSW_Gizka and PASS, not FAIL on the
    donor's untouched 100; with only the donor loaded it is UNMEASURED, never a FAIL.
Offline.

    python3 src/RimStarWars/GizkaStowaway/selftest_gizka_validation_chains.py
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
    def __init__(self, loaded=("RSW_Gizka",), mv=None):
        self.loaded, self.mv, self.hook_n = set(loaded), mv or {}, 0

    def track(self, *a, **k):
        pass

    def call(self, tool, **p):
        if tool == "jawa/harmony_patches":
            self.hook_n += 1
            if self.hook_n == 1:
                return {"success": False, "message": "no such method"}
            return {"success": True, "methods": [{"prefixes": [{"owner": "someone.else"}]}]}
        if tool == "jawa/get_defs":
            d = p.get("defs", "")
            if d.startswith("PawnKindDef/"):
                return {"success": True, "foundCount": 1 if d.split("/", 1)[1] in self.loaded else 0}
            if d.startswith("ThingDef/") and p.get("fields") == "statBases":
                k = d.split("/", 1)[1]
                return {"success": True, "defs": [{"fields": {"statBases": [{"stat": "MarketValue", "value": self.mv[k]}]}}]}
        return {"success": True}


def run(chain, bridge):
    t = TestContext(bridge)
    dict(V.suite.chains)[chain](t)
    return t.components


def main():
    if V.suite is None:
        check("modcheck importable", False)
        return 1
    rows = run("harmony_wiring", Fake())
    verdicts = [c.verdict for c in rows]
    check("sanity: hook 1 UNMEASURED, hook 2 FAIL", verdicts[:2] == ["UNMEASURED", "FAIL"] and len(rows) >= 3, repr(verdicts))
    after = rows[2:]
    check("rows after the FAIL are UNMEASURED", after and all(c.verdict == "UNMEASURED" for c in after), repr(verdicts))
    check("rows after the FAIL carry a reason", after and all(c.detail for c in after),
          repr([(c.name, c.detail) for c in after][:3]))

    both = run("donor_patch", Fake(loaded=("Gizka", "RSW_Gizka"), mv={"Gizka": 100.0, "RSW_Gizka": 15.0}))
    check("donor and port loaded: the patched RSW_Gizka is read -> PASS", [c.verdict for c in both] == ["PASS"],
          repr([(c.verdict, str(c.detail)[:120]) for c in both]))
    port = run("donor_patch", Fake(loaded=("RSW_Gizka",), mv={"RSW_Gizka": 100.0}))
    check("control: an unpatched RSW_Gizka still FAILs", [c.verdict for c in port] == ["FAIL"], repr([c.verdict for c in port]))
    donor = run("donor_patch", Fake(loaded=("Gizka",), mv={"Gizka": 100.0}))
    check("donor only: UNMEASURED, not FAIL (nothing patches the donor)", [c.verdict for c in donor] == ["UNMEASURED"],
          repr([(c.verdict, str(c.detail)[:120]) for c in donor]))
    print("gizka validation chains: %d failure(s) -> %s" % (len(FAILS), "OK" if not FAILS else "FAILED"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
