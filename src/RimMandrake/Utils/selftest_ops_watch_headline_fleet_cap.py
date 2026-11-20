#!/usr/bin/env python3
"""The digest headline must not print the fleet-stop horizon cap as a stop.

accounts.fleet_stop_h reads the horizon (24) when the plan finds no stop inside it. The headline printed that as
"fleet stop in 24 h", which reads as "the fleet stops tomorrow" (Operations 19:30 run, 2026-11-19: 24.0 with why
"no stop inside 24 h at 3.50%/h"). A capped reading must say "no fleet stop inside 24 h"; a real stop keeps its hours.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import ops_watch as OW  # noqa: E402

RESULTS = []


def case(ok, what, detail=""):
    RESULTS.append(bool(ok))
    print("%s  %s%s" % ("PASS" if ok else "FAIL", what, "" if ok else "  -> %r" % (detail,)))


def pts(stop):
    p = {"accounts.fleet_burn_pct_h": {"m": "MEASURED", "v": 3.504, "x": {"live": "system"}}}
    if stop is None:
        p["accounts.fleet_stop_h"] = {"m": "MEASURED", "v": 24.0,
                                      "x": {"rate_pct_h": 3.504, "why": "no stop inside 24 h at 3.50%/h"}}
    else:
        p["accounts.fleet_stop_h"] = {"m": "MEASURED", "v": stop,
                                      "x": {"rate_pct_h": 3.504, "stop_at": "2026-11-20T12:00:00Z",
                                            "why": "the plan stops at 2026-11-20T12:00:00Z at 3.50%/h"}}
    return p


capped = OW.headline(pts(None), [], {})
case("no fleet stop inside 24 h at 3.5 %/h" in capped and "fleet stop in 24" not in capped,
     "capped horizon reads as no stop inside it", capped[:200])

real = OW.headline(pts(8.4), [], {})
case("fleet stop in 8.4 h at 3.5 %/h" in real, "a real stop keeps its hours", real[:200])

print("%d of %d" % (sum(RESULTS), len(RESULTS)))
sys.exit(0 if all(RESULTS) and len(RESULTS) == 2 else 1)
