"""RIMMANDRAKE_PRUNE_FLOWWORKS_DRAWBRIDGE_TO_HIS_NOV_THIRD_RULINGS: the gate frame, the hauling lines and the far bank of a
drawbridge (his rulings of 2026-11-03), solved in art_source/Drawbridge/frame_geometry.py and drawn by RM_DrawbridgeArt through
DrawbridgeFrameMath (Source/RM_DrawbridgeMath.cs). Offline, no dotnet. Over both materials, all 4 directions, widths 1 to 4, leaf
lengths 1 to the material's longest, both winch sides:
  - FRAME: two posts outside lanes 0 and width-1, one lintel from post to post, and a doorway with no frame or line pixel in it;
  - NEAR LINES, at the hold: each starts on the drawn tip edge, runs straight over the lintel and ends at the winch (taut);
  - FAR BANK, at the hold: no line piece at all (so none past its anchor square); lowered, the hitch stays on its anchor square;
  - MATERIAL: timber and steel take one path (the geometry takes no material; the anchor print asks nothing of the tier first);
  - NO POP: the lowered deck of a drawbridge prints the raised leaf's own picture (same file, same slice, same columns).
Can-fail: --canfail NAME plants one fault and must FAIL: near_slack, steel_far_taut, black_doorway, pop, post_in_lane.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_drawbridge_frame.py [--canfail NAME | --canfail all]
"""
from __future__ import annotations

import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "art_source", "Drawbridge"))
MATH = os.path.join(HERE, "Source", "RM_DrawbridgeMath.cs")
ART = os.path.join(HERE, "Source", "Pits", "Drawbridge", "RM_DrawbridgeArt.cs")
DECK = os.path.join(HERE, "Source", "Pits", "Suspension", "Building_SuspensionDeck.cs")
CTRL = os.path.join(HERE, "Source", "Pits", "Drawbridge", "RM_DrawbridgeControl.cs")
MAXLEAF = {"Timber": 4, "Steel": 8}
FAULTS = ["near_slack", "steel_far_taut", "black_doorway", "pop", "post_in_lane"]
# C# constant -> frame_geometry name
CONSTS = {"Plane": "PLANE", "PostV": "POST_V", "PostW": "POST_W", "PostH": "POST_H", "OpenH": "OPEN_H", "SheaveZ": "SHEAVE_Z",
          "MoorU": "MOOR_U", "DrumZ": "DRUM_Z", "HitchDeg": "HITCH_DEG"}


def body(src, sig):
    a = src.find(sig)
    if a < 0:
        return ""
    i = src.index("{", a)
    d = 0
    for j in range(i, len(src)):
        d += (src[j] == "{") - (src[j] == "}")
        if d == 0:
            return src[a:j + 1]
    return ""


def seg_hits(p, q, box):
    """does the segment enter the open rectangle (Liang-Barsky)"""
    x0, z0, x1, z1 = box
    t0, t1 = 0.0, 1.0
    for d, lo, hi in ((q[0] - p[0], x0 - p[0], x1 - p[0]), (q[1] - p[1], z0 - p[1], z1 - p[1])):
        if abs(d) < 1e-12:
            if lo >= 0 or hi <= 0:
                return False
            continue
        a, b = sorted((lo / d, hi / d))
        t0, t1 = max(t0, a), min(t1, b)
    return t1 - t0 > 1e-9


def on_segment(p, a, b):
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    cross = abs((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) / max(d, 1e-9)
    along = ((p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])) / max(d * d, 1e-9)
    return cross < 1e-6 and -1e-6 <= along <= 1 + 1e-6


def run(fault=None):
    import frame_geometry as G
    fails = []

    def check(ok, msg):
        if not ok:
            fails.append(msg)

    src = open(MATH, encoding="utf-8").read()
    fm = body(src, "public static class DrawbridgeFrameMath")
    check(bool(fm), "DrawbridgeFrameMath is not in RM_DrawbridgeMath.cs (no frame, no hauling line)")
    for c, g in CONSTS.items():
        m = re.search(r"public const double " + c + r" = (-?[0-9.]+);", fm)
        check(m is not None and abs(float(m.group(1)) - getattr(G, g)) < 1e-9, "constant %s differs from frame_geometry.%s" % (c, g))
    flat = re.sub(r"\s+", " ", fm)
    for frag in ("X = fx * u + sx * v, Z = fz * u + sz * v + up",
                 "Leaf(fx, fz, sx, sz, length, sgn * width / 2.0, deg)",
                 "At(fx, fz, sx, sz, Plane, sgn * (width / 2.0 + PostV), SheaveZ)",
                 "At(fx, fz, sx, sz, length + MoorU, sgn * (width / 2.0 - 0.1), 0)",
                 "double k = 1.0 - deg / HitchDeg; if (k <= 0)"):
        check(frag in flat, "C# formula not found (mirror drifted): " + frag)

    for mat, longest in MAXLEAF.items():
        for d in "NSEW":
            fx, fz = G.F[d]
            hold = G.HOLD[d]
            for w in range(1, 5):
                post_v = 0.0 - G.POST_W if fault == "post_in_lane" else G.POST_V
                # FRAME: the posts stand outside the lanes
                check(post_v - G.POST_W / 2 >= -0.02, "%s w%d: a post stands inside a lane" % (d, w))
                box = G.interior(d, w)
                if box:
                    x0, z0, x1, z1 = box
                    check(x1 - x0 >= w - 0.05, "%s w%d: the doorway is narrower than its lanes" % (d, w))
                    check(z1 - z0 >= 0.8, "%s w%d: the doorway is too low to read" % (d, w))
                    for c in G.posts(d, w):
                        px0, px1 = c[0] - G.POST_W / 2, c[0] + G.POST_W / 2
                        check(px1 <= x0 + 1e-9 or px0 >= x1 - 1e-9, "%s w%d: a post covers the doorway" % (d, w))
                    check(z0 + G.POST_H - G.LINTEL_T >= z1 - 1e-9 or G.POST_H - G.LINTEL_T >= G.OPEN_H, "%s w%d: the lintel hangs in the doorway" % (d, w))
                for L in range(1, longest + 1):
                    tip = [G.leaf_pt(d, L, s * w / 2, hold) for s in (-1, 1)]
                    for ws in (-1, 1):
                        drum = G.xy(d, -0.5, ws * (w / 2 + 0.5), G.DRUM_Z)
                        for s in (-1, 1):
                            p = G.near_line(d, w, L, s, hold, ws, drum)
                            if fault == "near_slack":
                                p = [p[0], (p[0][0], p[0][1] - 0.6)] + p[1:-1]
                            where = "%s %s w%d L%d winch%+d line%+d" % (mat, d, w, L, ws, s)
                            check(on_segment(p[0], *tip), where + ": does not start on the drawn tip edge")
                            check(math.dist(p[-1], drum) < 1e-9, where + ": does not end at the winch")
                            check(len(p) == (3 if s == ws else 4), where + ": not one taut run over the lintel")
                            check(math.dist(p[1], G.sheave(d, w, s)) < 1e-9, where + ": does not go over the lintel")
                            if box:
                                for a, b in zip(p, p[1:]):
                                    check(not seg_hits(a, b, box), where + ": crosses the doorway")
                    for s in (-1, 1):
                        far = G.hitch(d, w, L, s, hold)
                        if fault == "steel_far_taut" and mat == "Steel":
                            far = [G.moor(d, w, L, s), G.xy(d, L - 1.0, s * w / 2)]
                        check(far is None, "%s %s w%d L%d: a far line is still drawn at the hold" % (mat, d, w, L))
                        low = G.hitch(d, w, L, s, 0)
                        for q in low or []:
                            u = fx * q[0] + fz * (q[1] - (0.12 if d in "NS" else 0)) if d in "NS" else fx * q[0]
                            check(u >= L - 0.13, "%s %s w%d L%d: the lowered hitch leaves its anchor square" % (mat, d, w, L))

    art = open(ART, encoding="utf-8").read()
    deck = open(DECK, encoding="utf-8").read()
    ctrl = open(CTRL, encoding="utf-8").read()
    pr = body(deck[deck.find("public class Building_SuspensionAnchor"):], "public override void Print(SectionLayer layer)")
    i, j = pr.find("RM_DrawbridgeArt.PrintDrawbridgeEnd(layer, this)"), pr.find("AnchorPrintFor")
    check(0 <= i < j, "a drawbridge's anchor does not print its frame or mooring first (a steel one prints the suspension tower)")
    end = body(art, "public static bool PrintDrawbridgeEnd(")
    check(bool(end) and "Steel" not in end and "Timber" not in end, "the drawbridge end branches on its material")
    pf = body(art, "private static void PrintFrame(")
    if fault == "black_doorway":
        pf = pf.replace("PrintRect(layer, art.PostLeft", "PrintRect(layer, art.Pad, left, 1f, 1f, 0f); PrintRect(layer, art.PostLeft")
    face = pf[:pf.find("return;")]   # the face-on frame: what it prints, and nothing else
    check(re.findall(r"PrintRect\(layer, art\.(\w+)", face) == ["Beam", "PostLeft", "PostRight"] and "PrintPlane" not in face,
          "the face-on frame prints something besides its two posts and its lintel: the doorway is not clear")
    dl = body(art, "public static void DrawLines(")
    check(bool(dl) and "DrawbridgeFrameMath.NearLine(" in dl and "DrawbridgeFrameMath.Hitch(" in dl, "no code draws the hauling lines")
    check("DrawLines(map, r, l);" in body(art, "public static void DrawLeaves("), "the hauling lines are not drawn each frame")
    dp = body(deck, "public override void Print(SectionLayer layer)")
    pd = body(art, "public static bool PrintLeafDeck(")
    i, j = dp.find("RM_DrawbridgeArt.PrintLeafDeck(layer, this, Record)"), dp.find("RM_SuspensionDeckLink.Print")
    if fault == "pop":
        i = -1
    check(0 <= i < j, "the lowered drawbridge deck does not print the raised leaf's picture (it changes picture at the first tick)")
    check("LeafDeckMat(" in pd and "LeafDeckMat(" in body(deck, "public override Material FadeMaterial(out float angle)"),
          "the faded deck square draws another picture than the printed one")
    up = body(art, "public static void DrawLeafUp(")
    check("LeafU0" in body(art, "public static Mesh LeafSlice(int slice)") and "LeafU0" in body(art, "public static Material LeafDeckMat("),
          "the lowered and the raised leaf cut different columns of the picture")
    check("DrawbridgeLeafPose.SliceFor" in up and "DrawbridgeLeafPose.SliceFor" in body(art, "public static Material LeafDeckMat("),
          "the lowered and the raised leaf show different slices")
    gate = body(art, "public static bool DrawGate(")
    check("GatePanel" in gate, "the door squares still draw one framed door picture per lane")
    check("OpenPct)" in body(ctrl, "protected override void DrawAt(Vector3 drawLoc, bool flip = false)") or "OpenPct)" in ctrl, "the gate panel does not follow the door")
    return fails


def main(argv):
    if "--canfail" in argv:
        name = argv[argv.index("--canfail") + 1]
        rc = 0
        for f in FAULTS if name == "all" else [name]:
            r = run(f)
            print("can-fail %s: %s" % (f, "OK (%d, first: %s)" % (len(r), r[0]) if r else "BROKEN (passed on the planted fault)"))
            rc = rc or (0 if r else 1)
        return rc
    r = run()
    print("FAIL (%d): %s" % (len(r), "; ".join(r[:8])) if r else "PASS drawbridge frame, lines and far bank")
    return 1 if r else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
