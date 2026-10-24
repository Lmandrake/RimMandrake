#!/usr/bin/env python3
"""selftest_hose_explore.py -- HOSE_EXPLORER_WIDEN_SEEDS_LONG_LEAD: the offline hose explorer's "no fit" means no fit.

hose_geometry_explore.py decides, offline, which reel lays the C# hose solver must serve. Its sweep verdicts are only
worth anything if the search behind them is saturated; these checks pin the three defects `saturate` exposed:
  1. a free end inside the reel's turning circle (free "N 0 3") fits at the full 2.2 lead with the ordinary search,
     because solve_free now seeds hooks (Dubins words under FREE_ARRIVALS arrival headings); can-fail: with no hook
     seeds (the old seed set) the same search finds nothing at 0.6 or 2.2;
  2. only the reel a hose LEAVES is exempt from its lead (Hose.own): a lay whose lead runs along a second reel's face
     fails at 2.2 with "lead-out touches", as it fails at 0.6 (fitting stays monotone in the lead); can-fail: under the
     old shared name ("reel" for both reels) the 2.2 lay passes while the 0.6 one fails;
  3. a mate case that runs out of wall-clock budget is "unsaturated", never "none at 0.6"; can-fail: without the
     budget flag the same row classifies "none at 0.6";
  4. the too-close proofs: mate_proof proves a mate whose lead runs into the other reel (sweep case m193), with the
     player-facing prefix; the start-inside test catches a curve start inside an inflated box.
"""
import math
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hose_geometry_explore as H  # noqa: E402

fails = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        fails.append(msg)


def free_n03(arrivals):
    saved = H.FREE_ARRIVALS
    H.FREE_ARRIVALS = arrivals
    try:
        P0, th0 = H.reel_mouth(0, 0, "N")
        P1 = np.array([0.5, 3.5])
        obs = [H.Box(0, 0, 2, 2, "reel")]
        ref = max(H.dubins_min(P0, th0, P1, th0), math.hypot(*(P1 - P0)))
        return [H.solve_free(P0, th0, ld, P1, obs, ref)[0] for ld in (H.LEAD_MIN, H.LEAD_OUT)]
    finally:
        H.FREE_ARRIVALS = saved


def lead_along_reel(name_b):
    P0, th0 = H.reel_mouth(0, 0, "E")
    P1 = np.array([8.0, P0[1]])
    obs = [H.Box(0, 0, 2, 2, "reel"), H.Box(2, P0[1], 4, P0[1] + 2, name_b)]
    return [H.solve_free(P0, th0, ld, P1, obs, 6.0)[:2] for ld in (H.LEAD_MIN, H.LEAD_OUT)]


def main():
    H._DEADLINE[0] = float("inf")
    # 1
    new, old = free_n03(8), free_n03(0)
    check(new == [True, True], "free N 0 3 (end inside the turning circle) fits at 0.6 and 2.2 with hook seeds: %s" % new)
    check(old == [False, False], "can-fail: without hook seeds the same search finds nothing: %s" % old)
    # 2
    r_new, r_old = lead_along_reel("reel B"), lead_along_reel("reel")
    check(not r_new[0][0] and not r_new[1][0] and "lead-out touches reel B" in r_new[1][1],
          "a lead along a second reel's face fails at 0.6 and at 2.2 (%s / %s)" % (r_new[0][1], r_new[1][1]))
    check(not r_old[0][0] and r_old[1][0], "can-fail: a shared reel name exempts the 2.2 lead only (%s / %s)" % (r_old[0][1], r_old[1][1]))
    # 3
    case = dict(key="t", reelA=(0, 0, "E"), reelB=(8, 0, "W"), endA=(5.5, 1.5), endB=(5.5, 2.5), slack=1.0)
    saved = H.CASE_BUDGET
    H.CASE_BUDGET = -1.0
    try:
        r = H.run_mate(case)
    finally:
        H.CASE_BUDGET = saved
        H._DEADLINE[0] = float("inf")
    check(H.classify(r) == "unsaturated", "a mate case out of budget classifies unsaturated (%s)" % r.get("why"))
    r.pop("budget_spent", None)
    check(H.classify(r) == "none at 0.6", "can-fail: the same row without the budget flag reads none at 0.6")
    # 4
    m193 = dict(key="m193", reelA=(0, 0, "S"), reelB=(-1, -2, "W"), endA=(2.5, -1.5), endB=(1.5, -1.5), slack=1.0)
    pr = H.mate_proof(m193)
    check(bool(pr) and pr.startswith("too close for the hose to bend"), "m193 is proved too close: %s" % pr)
    t = time.time()
    r = H.run_mate(m193)
    check(r.get("proved") and r["lead"] is None and time.time() - t < 5, "run_mate returns the proof without searching")
    box = H.Box(0, 0, 2, 2, "wall")
    check(H.blocked_ahead(np.array([2.05, 1.0]), 0.0, np.array([6.0, 1.0]), [box]) is not None,
          "a curve start 0.05 from a box face is blocked (inside the 0.123 inflation)")
    check(H.blocked_ahead(np.array([2.2, 1.0]), 0.0, np.array([6.0, 1.0]), [box]) is None,
          "sanity: a start 0.2 clear of the face (box behind it) is not blocked")
    print("%d failure(s)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
