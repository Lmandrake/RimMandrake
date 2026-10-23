#!/usr/bin/env python3
"""Runs validation_hose_offline.py (HO5-HO9) inside run_selftests.py's sweep.

Why this wrapper exists (HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES, 2026-10-22): the hose's offline art rows moved from
Gimme Some Slack's validation.py into validation_hose_offline.py at the hose port (7cf08bf64e), and from then on only a
FlowWorks validation/proof run executed them -- run_selftests.py discovers selftest*.py only. HO9 (the drawn fittings meet
their nozzles/ports) would have refused 2e22f30e3c's coupling art on 2026-10-17 had anything run it before a commit.

    python3 src/RimMandrake/FlowWorks/selftest_hose_offline.py      # exit 1 on any FAIL
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validation_hose_offline as V  # noqa: E402

if __name__ == "__main__":
    rows = V.run_offline()
    bad = [r["id"] for r in rows if r["status"] != "PASS"]
    print("hose offline: %d/%d rows PASS%s" % (len(rows) - len(bad), len(rows), (" -- FAIL " + ", ".join(bad)) if bad else ""))
    sys.exit(1 if bad else 0)
