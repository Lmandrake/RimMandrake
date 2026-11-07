#!/usr/bin/env python3
"""selftest_flyer_tier_two.py - every tier-2 set is a locked flip-book (FLYER_TIER_TWO_REBUILD_KEPT_NEW_WINGS).

Offline, read-only. The gate itself is flyer_gate.py; this names the members so one command proves them:
  1. each set has a DEF_SETS row in flyer_gate.py;
  2. each set exits 0 from `flyer_gate.py flipbook <Set>`;
  3. `flyer_gate.py audit --strict` exits 0.
Exit 0 = all pass, 1 = a check failed (a gate's UNMEASURED exit 2 is a fail here: the set is not proven).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import flyer_gate as G  # noqa: E402

SETS = ("Shyrack", "Urusai", "Dustflutter", "Sivvern", "Soorrak", "Sparkleech", "Vrisk", "Zellik", "Strill")
GATE = str(HERE / "flyer_gate.py")


def main() -> int:
    bad = 0
    rows = {s for sets in G.DEF_SETS.values() for s in sets}
    for s in SETS:
        if s not in rows:
            print(f"FAIL {s}: no DEF_SETS row")
            bad += 1
        rc = subprocess.run([sys.executable, GATE, "flipbook", s], capture_output=True, text=True).returncode
        print(f"{'PASS' if rc == 0 else 'FAIL'} flipbook {s}: exit {rc}")
        bad += rc != 0
    rc = subprocess.run([sys.executable, GATE, "audit", "--strict"], capture_output=True, text=True).returncode
    print(f"{'PASS' if rc == 0 else 'FAIL'} audit --strict: exit {rc}")
    bad += rc != 0
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
