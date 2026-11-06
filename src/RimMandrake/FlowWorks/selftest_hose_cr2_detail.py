"""HOSE_CARRY_DIAGNOSE_LAYOK_HIDES_IN_DETAIL: validation_hose's CR2 row (the carried trail follows the walk).

Run J20261104T093122Z-d73263 (sha 97650a6a26) FAILED CR2 with the trail visibly following (count 2->4, trailLast [86,68]
= pawnPos [86,68]); the failing clause was layOk, which the row's detail did not record. Ruled HARNESS: a carried hose has
no lay by design (PickUp nulls it; HOSE_PROOFS_FIX_STALE_LAYOK_AFTER_PEEK swapped the clause for draw mode "carry").
This pins both halves offline: the detail records layOk and drawMode, and the verdict judges the measured case right.

  python3 src/RimMandrake/FlowWorks/selftest_hose_cr2_detail.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.join(HERE, "northstar")):
    if p not in sys.path:
        sys.path.insert(0, p)

import validation_hose as VH  # noqa: E402

FAILS = []


def check(cond, msg):
    print("%s  %s" % ("PASS" if cond else "FAIL", msg))
    if not cond:
        FAILS.append(msg)


def hose(count, last, pos, mode, lay_ok=False):
    return {"carry": "Carrying", "carrier": {"id": 7, "pos": pos}, "trail": {"count": count, "last": last},
            "layOk": lay_ok, "draw": {"mode": mode}, "pending": "CarryTo", "state": "Carrying"}


def main():
    a = hose(2, [84, 68], [84, 68], "carry")
    b = hose(4, [86, 68], [86, 68], "carry")          # the d73263 reading
    v = VH._carry_view(b)
    check("layOk" in v and v["layOk"] is False, "CR2 detail records layOk (false on a carried hose)")
    check(v.get("drawMode") == "carry", "CR2 detail records the draw mode")
    check(VH.cr2_ok(a, b) is True, "the measured d73263 case (count 2->4, last = pawn cell, layOk false, carry draw) PASSES")
    check(VH.cr2_ok(a, hose(4, [86, 68], [86, 68], "lay")) is False, "no carry draw FAILS")
    check(VH.cr2_ok(a, hose(4, [86, 68], [86, 68], "none")) is False, "nothing drawn FAILS")
    check(VH.cr2_ok(a, hose(2, [86, 68], [86, 68], "carry")) is False, "a trail that did not grow FAILS")
    check(VH.cr2_ok(a, hose(4, [80, 68], [86, 68], "carry")) is False, "a trail whose last cell lags the pawn FAILS")
    check(VH.cr2_ok(a, hose(4, [85, 68], [86, 68], "carry")) is True, "last = the cell he just left PASSES")
    src = open(os.path.join(HERE, "validation_hose.py"), encoding="utf-8").read()
    check('"CR2_trail_follows_walk", "PASS" if cr2_ok(a, b)' in src, "run_carry's CR2 row uses cr2_ok")
    print("RESULT: %s (%d failed)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
