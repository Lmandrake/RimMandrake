#!/usr/bin/env python3
"""STILLSAND_ROOF_COVER_EXPOSURE_1 live proof A2: run the Stillsand sun chain up to
sun_roof_cover_above_55deg (its two prerequisite rows run first) and exit 0 only if that row PASSes.

The row (validation.py) roofs a 6x6 pad, steps past the shade grid's next 2000-tick rebuild, then needs the
roofed cell at shade >= 0.99 and exposure <= the sand glare floor (0.35 from the BiomeDef), and the open cell
above it, at a pinned sun >= 55 deg. Reads the run's own results JSON (Transient/modcheck/Stillsand_*.json,
written by modcheck runner.write_sheet), never the console.

Exit: 0 PASS, 1 FAIL / UNMEASURED / row missing, 2 no results JSON written by this run.
"""
import glob
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ROW = "sun_roof_cover_above_55deg"


def main():
    start = time.time()
    rc = subprocess.call([sys.executable, "-m", "modcheck.cli", "run", "Stillsand", "--rows", ROW,
                          "--item", "STILLSAND_ROOF_COVER_EXPOSURE_1"],
                         cwd=os.path.join(ROOT, "src", "RimMandrake", "Utils"), stdin=subprocess.DEVNULL)
    fresh = [p for p in glob.glob(os.path.join(ROOT, "Transient", "modcheck", "Stillsand_*.json"))
             if os.path.getmtime(p) >= start]
    if not fresh:
        print("NO RESULTS: modcheck exited %d and wrote no Stillsand results JSON" % rc)
        return 2
    path = max(fresh, key=os.path.getmtime)
    summary = json.load(open(path, encoding="utf-8"))["summary"]
    for ch in summary.get("chains") or []:
        for c in ch.get("components") or []:
            if c.get("name") == ROW:
                print("%s: %s -- %s (%s)" % (ROW, c.get("verdict"), c.get("detail"), path))
                return 0 if c.get("verdict") == "PASS" else 1
    print("%s missing from %s" % (ROW, path))
    return 1


if __name__ == "__main__":
    sys.exit(main())
