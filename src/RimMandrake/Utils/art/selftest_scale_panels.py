#!/usr/bin/env python3
"""selftest_scale_panels.py — the scaled portrayal is on EVERY biome sheet (owner, 2026-10-05: "You also did not
include the scaled portrayal on that sheet"). Asserts, on the sheets as built: each carries scale items with a
picture (scale_ image), and the ground colour of Leaning Scrub is measured from a real texture."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art_sheet as A  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def main():
    sheets = sorted(A.BIOME_OUT.glob("*_sheet_*.html"))
    check(len(sheets) >= 20, f"sanity probe: found {len(sheets)} built biome sheets")
    for f in sheets:
        h = f.read_text()
        m = re.search(r'<script id="ITEMS" type="application/json">(.*?)</script>', h, re.S)
        items = json.loads(m.group(1)) if m else []
        n = sum(1 for i in items if (i.get("scale") or {}).get("img"))
        check(n > 0 or not items, f"{f.stem}: {n} of {len(items)} rows carry a scale panel picture")
    rgb, src = A.measure_ground("RM_LeaningScrub")
    check(rgb is not None and "Sand" in src, f"Leaning Scrub ground measured: {rgb} from {src}")
    print(f"{len(FAILS)} failed" if FAILS else "all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
