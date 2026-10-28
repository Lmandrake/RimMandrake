#!/usr/bin/env python3
"""Selftest for account_failover.decide: switch only on a fresh MEASURED reading at or under the threshold, once."""
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import account_failover as A  # noqa: E402

M = lambda l, src="MEASURED", st=False: {"source": src, "week_pct_left": l, "stale": st}  # noqa: E731
now = time.time()
CASES = [({"system": M(16), "lukas": M(7, "ESTIMATE")}, False, "above threshold"),
         ({"system": M(2), "lukas": M(7, "ESTIMATE")}, True, "at threshold"),
         ({"system": M(1.5, "ESTIMATE")}, False, "an ESTIMATE never switches"),
         ({"system": M(1, st=True)}, False, "a stale reading never switches"),
         ({"system": M(2), "lukas": M(1)}, False, "target as low: no gain"),
         ({"system": M(None)}, False, "unreadable")]
fails = 0
for acc, want, name in CASES:
    got, why = A.decide(acc, now, False)
    ok = got == want
    fails += not ok
    print("%s  %s: %s" % ("ok  " if ok else "FAIL", name, why))
got, _ = A.decide({"system": M(1)}, now, True)
fails += got
print("%s  marker present: never twice" % ("ok  " if not got else "FAIL"))
got, _ = A.decide({"system": M(1)}, time.mktime(time.strptime("2026-10-29", "%Y-%m-%d")), False)
fails += got
print("%s  past the deadline: no switch" % ("ok  " if not got else "FAIL"))
print("%d failure(s)" % fails)
sys.exit(1 if fails else 0)
