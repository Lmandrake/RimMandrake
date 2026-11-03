#!/usr/bin/env python3
# selftest-timeout: 600   (stages and builds the FlowWorks C# SelfTest, then runs only the shore-search cases)
"""selftest_swim_shore_reach.py — TIRED_SWIMMER_FIX_UNREACHABLE_SHORE (GPT FA_core_sim_4.1).

WHY: a tired swimmer's shore search (RM_Swim.NearestFooting) accepted a dry ledge beside it that was too high to climb,
ordered an impossible Goto and could pick it again until it drowned. The search now crosses only steps the pawn can climb
(RM_PitTrapMath.StepAllowed, ramp and ladder joins) through the Verse-free RM_SwimMath.NearestReachableFooting.

The proof is three C# Case()s in Source/SelfTest/SwimChecks.cs, run through selftest_flowworks_stock.py --only:
a too-high ledge beside the swimmer loses to a farther ramp (can-fail: a walk-only flood picks the ledge), a 4000-grid
sweep against an independent BFS, and the production source shape. This wrapper fails unless all three report ok.

    python3 src/RimMandrake/FlowWorks/selftest_swim_shore_reach.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

STOCK = Path(__file__).resolve().parents[1] / "Utils" / "selftest_flowworks_stock.py"
CASES = ("Swim_shore_search_skips_unclimbable_ledge",
         "Swim_shore_search_sweep_answer_is_climbable_and_nearest",
         "Swim_shore_search_production_uses_climb_rule")


def main() -> int:
    r = subprocess.run([sys.executable, str(STOCK), "--only", "Swim_shore_*"], capture_output=True, text=True,
                       timeout=580)
    out = r.stdout + r.stderr
    ok = [c for c in CASES if re.search(r"^ok\s+" + re.escape(c) + r"\s*$", out, re.M)]
    for c in CASES:
        print(("PASS " if c in ok else "FAIL ") + c)
    if r.returncode != 0 or len(ok) != len(CASES):
        print(out[-3000:])
        print(f"FAIL: stock rc={r.returncode}, {len(ok)}/{len(CASES)} shore cases ok")
        return 1
    print(f"PASS: {len(ok)}/{len(CASES)} shore cases ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
