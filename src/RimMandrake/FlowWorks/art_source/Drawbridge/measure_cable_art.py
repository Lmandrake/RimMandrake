"""DRAWBRIDGE_CABLES_FIX_STOP_SHORT: measure, from the PNGs' alpha alone, where every suspension-anchor picture's two
ropes run, where each rope meets its bollard (the attachment point) and where the painted rope stops; and, for the raised
leaf's edge views, the leaf body's columns and the top row of the hook's eye (the painted stiff rope stub runs outside those
columns and above that row).

Independent of the C# under test: it reads pixels, never the code. Writes anchor_cable_art.json beside this file, which the
offline SelfTest (DrawbridgeChecks.cs, "Drawbridge_Cables_*") reads to grade RM_DrawbridgeCableMath, and which
selftest_flowworks_drawbridge_art.py re-measures to prove the fixture is current.

Frame: every anchor picture is turned so its ropes run toward +x ("along"); along/lateral are fractions of the 1-cell
picture (along 0 = back edge, 1 = the edge facing the deck; lateral 0 = the cell's centre line, + = left of the rope's
direction). Pixel picture rows run down, so lateral = (128 - y) / 256 in the east-facing frame.

    python3 src/RimMandrake/FlowWorks/art_source/Drawbridge/measure_cable_art.py [--check] [--tex <Textures root>]
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "..", "..", "Textures")
OUT = os.path.join(HERE, "anchor_cable_art.json")
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
MATS = ["Timber", "Steel", "Heavy"]
BASE_MATS = ["Rope", "Timber", "Steel", "Heavy"]
LEAF_EDGES = ["Edge_Scrapper", "Edge_Industrial", "Edge_Modern", "Edge_Futuristic", "Timber_Edge", "Steel_Edge"]
ALPHA = 40


def runs(col):
    out, start = [], None
    for i, v in enumerate(list(col) + [False]):
        if v and start is None:
            start = i
        elif not v and start is not None:
            out.append((start, i - 1))
            start = None
    return out


def measure_axis(a):
    """a: alpha mask, ropes running toward +x. Two ropes; per rope its centre row, thickness, the last painted column and
    the attachment column (walking back from the tip, the first column where the silhouette around the rope is wider
    than 1.6 rope thicknesses: the bollard's hardware)."""
    h, w = a.shape
    end = int(np.where(a.any(0))[0].max())
    tip = runs(a[:, end - 3])
    if len(tip) != 2:
        raise SystemExit("expected two ropes at the tip, got %r" % (tip,))
    ropes = []
    for r0, r1 in tip:
        c = (r0 + r1) / 2.0
        thick = r1 - r0 + 1
        x = end - 3
        while x > 0:
            lo = max(0, int(c) - 3 * thick)
            band = a[lo: int(c) + 3 * thick + 1, x]
            mid = int(c) - lo
            near = [r for r in runs(band) if r[0] - 1 <= mid <= r[1] + 1]
            width = max((r[1] - r[0] + 1 for r in near), default=0)
            if width == 0 or width > thick * 1.6:
                break
            x -= 1
        attach = x + 1
        ropes.append({
            "lateral": round((h / 2.0 - (c + 0.5)) / h, 5),
            "thick": round(thick / float(h), 5),
            "attach": round(attach / float(w), 5),
            "end": round((end + 1) / float(w), 5),
        })
    return ropes


def turned(a, facing):
    """Turn a picture so its ropes run toward +x: north (ropes up) and the base single (drawn north-up) turn clockwise."""
    if facing in ("north", "single"):
        return np.rot90(a, -1)
    if facing == "south":
        return np.rot90(a, 1)
    return a


def mask(path):
    return np.array(Image.open(path).convert("RGBA"))[:, :, 3] > ALPHA


def measure(tex):
    res = {"anchors": {}, "leafEdges": {}}
    sb = os.path.join(tex, "RimMandrake", "FlowWorks", "SuspensionBridge")
    for look in LOOKS:
        for m in MATS:
            for f in ("east", "north", "south"):
                p = os.path.join(sb, look, "RM_SuspensionAnchor_%s_%s.png" % (m, f))
                if os.path.exists(p):
                    res["anchors"]["%s/%s/%s" % (look, m, f)] = measure_axis(turned(mask(p), f))
    for m in BASE_MATS:
        p = os.path.join(tex, "Things", "Building", "FlowWorks", "SuspensionBridge", "RM_SuspensionAnchor_%s.png" % m)
        if os.path.exists(p):
            res["anchors"]["base/%s/single" % m] = measure_axis(turned(mask(p), "single"))
    for e in LEAF_EDGES:
        p = os.path.join(tex, "Things", "Building", "FlowWorks", "Drawbridge", "RM_DrawbridgeLeafUp_%s.png" % e)
        if not os.path.exists(p):
            continue
        a = mask(p)
        h, w = a.shape
        cols = np.where(a[int(h * 0.2): int(h * 0.9)].any(0))[0]
        b0, b1 = int(cols.min()), int(cols.max())
        top = a[: int(h * 0.12)]
        outside = top.copy()
        outside[:, b0: b1 + 1] = False
        ys, xs = np.where(outside)
        # the hook's eye: the first row whose silhouette inside the body columns is at least half the body wide (the stub
        # crossing the body columns above it is a rope's width, growing a pixel or two a row)
        need = (b1 - b0 + 1) * 0.5
        eye = next(r for r in range(h) if a[r, b0: b1 + 1].sum() >= need)
        res["leafEdges"][e] = {
            "body": [round(b0 / float(w), 5), round((b1 + 1) / float(w), 5)],
            "eyeTop": round(eye / float(h), 5),
            "stubPixelsOutsideBody": int(outside.sum()),
            "stubCols": [round(int(xs.min()) / float(w), 5), round((int(xs.max()) + 1) / float(w), 5)] if len(xs) else None,
        }
    if not res["anchors"] or not res["leafEdges"]:
        raise SystemExit("measured nothing under %s" % tex)
    return res


def main():
    tex = TEX
    if "--tex" in sys.argv:
        tex = sys.argv[sys.argv.index("--tex") + 1]
    res = measure(tex)
    text = json.dumps(res, indent=1, sort_keys=True) + "\n"
    if "--check" in sys.argv:
        with open(OUT) as f:
            if f.read() != text:
                print("STALE: %s differs from a fresh measurement of the PNGs" % OUT)
                return 1
        print("OK anchor_cable_art.json matches the PNGs (%d anchors, %d leaf edges)" % (len(res["anchors"]), len(res["leafEdges"])))
        return 0
    with open(OUT, "w") as f:
        f.write(text)
    print("wrote %s (%d anchors, %d leaf edges)" % (OUT, len(res["anchors"]), len(res["leafEdges"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
