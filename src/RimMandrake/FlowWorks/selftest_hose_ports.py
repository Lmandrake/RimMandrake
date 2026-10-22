#!/usr/bin/env python3
"""HOSE_ENDS_FIX_MISSES_THE_PORTS -- the hose's attachment points match the INSTALLED art (offline, no game).

Owner, live walk 2026-10-21 on C5 Fuel Depot: "Hose attached to tank and reel broken. No longer following old logic of
attaching at attachment points (or graphics no longer support that)". Cause: the reel nozzle was a hand constant
(u 9/256 at drawSize 2.8) that two art installs (2e22f30e3c, 2c27b49569) and a drawSize change (2.8 -> 2.15) left
behind; nothing compared the C# to the pixels. This test does:

  1. reel: Source/Hose/ReelIntakeGeometry.cs is exactly what reel_intake_geometry.py measures from today's 8 reel
     textures at the defs' one drawSize (its --check), and HoseMath reads the nozzle from that table (no constant).
  2. tank: TankPortGeometry.PortDz (HoseMath.cs) matches each look's RM_LiquidTank.png west/east flange row within
     0.03 cell, and the flange really sits at the canvas edge (the footprint edge at drawSize 2).

Any art reinstall that moves a port turns this red until the table is regenerated / re-measured.
"""
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(HERE, "Source", "Hose")
GEN = os.path.join(REPO, "src", "RimMandrake", "Utils", "mockups", "messy_conduit", "reel_intake_geometry.py")
TANK_TEX = os.path.join(HERE, "Textures", "RimMandrake", "FlowWorks", "Tank")
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
TANK_DRAW = 2.0

fails = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        fails.append(msg)


def reel():
    r = subprocess.run([sys.executable, GEN, "--check"], capture_output=True, text=True, timeout=120)
    check(r.returncode == 0, "reel: ReelIntakeGeometry.cs matches the installed reel art -- " + (r.stdout.strip() or r.stderr.strip())[-200:])
    hm = open(os.path.join(SRC, "HoseMath.cs")).read()
    m = re.search(r"internal V2 NozzleTip\b[\s\S]{0,400}?\n        \}", hm)
    body = m.group(0) if m else ""
    check("ReelIntakeGeometry.OutletTip(" in body, "reel: HoseReelRect.NozzleTip reads the measured table (ReelIntakeGeometry.OutletTip)")
    check(not re.search(r"9\.0 / 256|ReelDrawSize = 2\.8", hm), "reel: no hand-measured nozzle constant (u 9/256, drawSize 2.8) left in HoseMath.cs")


def tank():
    hm = open(os.path.join(SRC, "HoseMath.cs")).read()
    m = re.search(r"PortDz = \{([^}]*)\}", hm)
    check(m is not None, "tank: TankPortGeometry.PortDz exists in HoseMath.cs")
    if not m:
        return
    table = [float(x) for x in m.group(1).split(",")]
    check(len(table) == len(LOOKS), "tank: one PortDz per look (%d)" % len(table))
    for i, look in enumerate(LOOKS):
        a = np.array(Image.open(os.path.join(TANK_TEX, look, "RM_LiquidTank.png")).convert("RGBA"))[..., 3] > 128
        h, w = a.shape
        rows = [v for v in range(h) if a[v].any()]
        left = {v: np.nonzero(a[v])[0][0] for v in rows}
        right = {v: np.nonzero(a[v])[0][-1] for v in rows}
        lm, rm = min(left.values()), max(right.values())
        lrows = [v for v in rows if left[v] <= lm + 4]
        rrows = [v for v in rows if right[v] >= rm - 4]
        for side, edge_ok, rr in (("west", lm <= 4, lrows), ("east", rm >= w - 5, rrows)):
            dz = (0.5 - (rr[0] + rr[-1]) / 2.0 / h) * TANK_DRAW
            check(edge_ok, "tank: %s %s flange reaches the footprint edge" % (look, side))
            if i < len(table):
                check(abs(dz - table[i]) <= 0.03, "tank: %s %s flange at dz %.3f, table %.3f (<= 0.03)" % (look, side, dz, table[i]))


def main():
    reel()
    tank()
    print("%s: %d failure(s)" % (os.path.basename(__file__), len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
