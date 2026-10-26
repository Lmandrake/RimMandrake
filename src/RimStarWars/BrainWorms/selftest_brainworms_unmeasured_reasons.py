#!/usr/bin/env python3
"""selftest_brainworms_unmeasured_reasons.py -- BRAINWORMS_VALIDATION_FIX_BORROWED_REASON: validation.py's UNMEASURED
rows must say their real reason. Through modcheck's real TestContext on a fake bridge (no game):
  * infection_state: when the row that infects the pawn is UNMEASURED (the hediff is hidden from pawn_get), the
    severity row that reads that pawn must say so, not report a symptom ("carry no severity field");
  * _comp: after a lifted UNMEASURED and a later plain FAIL, the rows after the FAIL must carry a reason (the old _comp
    set upstream_reason to None).
Offline.

    python3 src/RimStarWars/BrainWorms/selftest_brainworms_unmeasured_reasons.py
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


class Hidden(object):
    """The add succeeds, but pawn_get lists no hediff at all (an undiscovered hediff hidden from the snapshot)."""

    def __init__(self):
        self.n = 0

    def track(self, *a, **k):
        pass

    def call(self, tool, **p):
        if tool == "jawa/map_info":
            return {"success": True, "sizeX": 100, "sizeZ": 100}
        if tool == "jawa/spawn_pawn":
            self.n += 1
            return {"success": True, "pawns": [{"id": "P%d" % self.n}]}
        if tool == "jawa/pawn_get":
            return {"success": True, "pawn": {"id": p.get("pawn"), "hediffs": []}}
        return {"success": True}


class Inert(object):
    def track(self, *a, **k):
        pass

    def call(self, tool, **p):
        return {"success": True}


def main():
    if V.suite is None:
        check("modcheck importable", False)
        return 1
    t = TestContext(Hidden())
    t.wait_ticks = lambda n, **k: None
    t.clear_area = lambda size=40: None
    dict(V.suite.chains)["infection_state"](t)
    rows = dict((c.name, c) for c in t.components)
    first = rows.get("infected_pawn_carries_hediff_clean_control_does_not")
    second = rows.get("severity_advances_while_warm")
    check("sanity: the hidden hediff makes the infecting row UNMEASURED", first is not None and first.verdict == "UNMEASURED",
          repr(first and (first.verdict, first.detail)))
    check("the severity row is UNMEASURED", second is not None and second.verdict == "UNMEASURED", repr(second and second.verdict))
    check("the severity row names the real reason (the hidden hediff), not a symptom",
          second is not None and "lists no" in str(second.detail) and "no severity field" not in str(second.detail),
          repr(second and str(second.detail)[:200]))

    t = TestContext(Inert())
    with V._comp(t, "a_declared_row"):
        V._unmeasured(t, "declared")
    with V._comp(t, "b_real_fail"):
        V._fail("planted")
    with V._comp(t, "c_after_the_fail"):
        pass
    v = [(c.name, c.verdict, c.detail) for c in t.components]
    check("sanity: UNMEASURED, FAIL, then UNMEASURED", [x[1] for x in v] == ["UNMEASURED", "FAIL", "UNMEASURED"], repr(v))
    check("the row after the FAIL carries a reason", bool(v[-1][2]), repr(v[-1]))
    print("brainworms unmeasured reasons: %d failure(s) -> %s" % (len(FAILS), "OK" if not FAILS else "FAILED"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
