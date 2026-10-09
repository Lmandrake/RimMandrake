#!/usr/bin/env python3
"""modcheck floor triage against the REAL deployed mod tree -- a live-install check.

    python3 src/RimMandrake/Utils/modcheck/selftest_deployed_floor.py

`modcheck floor --all` (DETERMINISM_ASSESSMENT.md SS6, C4), against the REAL repo and deployed mods -- a
positive-count assertion only, never a threshold on the counts themselves (SS6's own instruction). The dangerous
failure mode is a glob that quietly matches nothing and reports a clean empty table, not any specific count changing
as walks/mods are added or fixed. Split out of modcheck/selftest.py 2026-10-08 (selftest audit item 8).
"""
# selftest-tier: deployed
# Runs only under `run_selftests.py --tier deployed` (or --tier all / --only): after a deploy or a game update.
# selftest-timeout: 600
# Reason (measured 2026-10-07): floor.triage over the REAL mod tree on the drvfs mount - 112 components_declared
# calls, ~17k stat + 26k lstat (patch_targets mod_index/location_index/check_mod) - ~110 s wall (~27 s CPU, rest is
# drvfs IO), which under the parallel pool brushes the 240 s default. The check is deliberately against live data.
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
for p in (_HERE, _UTILS):
    if p not in sys.path:
        sys.path.insert(0, p)

import floor  # noqa: E402
import runner  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print("  ok   %s" % name)
    else:
        print("  FAIL %s  %s" % (name, detail))
        FAILURES.append(name)


def main():
    rows, footer = floor.triage(runner.ROOT)
    check("floor.triage: at least one walk read", len(rows) >= 1, len(rows))
    check("floor.triage: at least one mod indexed with a resolvable subject",
          any(r["subject_ok"] for r in rows), len(rows))
    check("floor.triage: footer renders a non-empty summary line", bool(footer))
    print("\nSELFTEST %s -- deployed floor triage" % ("FAILED" if FAILURES else "OK"))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
