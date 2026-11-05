"""LIQUID_PUMP_REDRAW_PLAN_VIEW_HUB gate: is each pump look oblique, with its four ports still registered?

  oblique : the band just above the body's south silhouette (the wall) is darker than the band just below its north
            silhouette (the top face's far rim): ratio <= WALL_RATIO, read on columns clear of the port strips.
            Plan-view medallions measure 0.98-1.06 (no wall); the oblique redraws 0.54-0.64.
  ports   : in the outer 0.12 cell of each side, the opaque connector is centred on the edge centre within 0.02 cell,
            and its outermost opaque pixel lies within 0.10 cell of the edge (selftest_hose_fittings' GAP_TOL).
Usage: check_oblique.py [--dir D]   D holds <Look>.png; default = the installed textures. Exit 0 = all pass.
"""
import os
import sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.normpath(os.path.join(HERE, "..", "..", "Textures"))
INSTALLED = {
    "Scrapper": os.path.join(TEX, "Things/Building/FlowWorks/Machinery/RM_LiquidPump.png"),
    "Industrial": os.path.join(TEX, "RimMandrake/FlowWorks/Pump/Industrial/RM_LiquidPump.png"),
    "Modern": os.path.join(TEX, "RimMandrake/FlowWorks/Pump/Modern/RM_LiquidPump.png"),
    "Futuristic": os.path.join(TEX, "RimMandrake/FlowWorks/Pump/Futuristic/RM_LiquidPump.png"),
}
WALL_RATIO = 0.80
REG_TOL, FACE_TOL, BAND = 0.02, 0.10, 0.12


def wall_ratio(a):
    n = a.shape[0]
    L, solid = a[..., :3].mean(-1), a[..., 3] > 200
    s = n / 512.0
    cols = [x for x in range(n) if 95 * s <= abs(x - (n - 1) / 2.0) <= 130 * s]
    south, north = [], []
    for x in cols:
        r = np.where(solid[:, x])[0]
        if len(r) < 120 * s:
            return None
        yt, yb = r.min(), r.max()
        south.append(L[yb - int(50 * s):yb - int(5 * s), x].mean())
        north.append(L[yt + int(5 * s):yt + int(50 * s), x].mean())
    return float(np.mean(south) / np.mean(north))


def ports(a):
    """[(side, centre offset cell, face gap cell)] for north/east/south/west (image north = row 0)."""
    n = a.shape[0]
    out = []
    for side, k in (("north", 0), ("east", 1), ("south", 2), ("west", 3)):
        r = np.rot90(a[..., 3] > 128, k)                 # rotate so this side is the top edge
        band = r[:int(BAND * n)]
        cols = np.where(band.any(0))[0]
        rows = np.where(band.any(1))[0]
        if not len(cols):
            out.append((side, None, None))
            continue
        out.append((side, ((cols.min() + cols.max() + 1) / 2.0 - n / 2.0) / n, rows.min() / float(n)))
    return out


def main():
    d = sys.argv[sys.argv.index("--dir") + 1] if "--dir" in sys.argv else None
    fails = 0
    for look, p in INSTALLED.items():
        p = os.path.join(d, look + ".png") if d else p
        a = np.array(Image.open(p).convert("RGBA")).astype(np.float64)
        wr = wall_ratio(a)
        ok = wr is not None and wr <= WALL_RATIO
        fails += not ok
        print("%-4s %-10s oblique: south-wall/north-rim brightness %s (<= %.2f)" % ("ok" if ok else "FAIL", look,
              "unmeasured" if wr is None else "%.2f" % wr, WALL_RATIO))
        for side, off, gap in ports(a):
            ok = off is not None and abs(off) <= REG_TOL and gap <= FACE_TOL
            fails += not ok
            print("%-4s %-10s port %-5s centre off edge centre %s cell (<= %.2f), face gap %s cell (<= %.2f)" % (
                "ok" if ok else "FAIL", look, side, "none" if off is None else "%+.3f" % off, REG_TOL,
                "none" if gap is None else "%.3f" % gap, FACE_TOL))
    print("check_oblique: %d failure(s)" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
