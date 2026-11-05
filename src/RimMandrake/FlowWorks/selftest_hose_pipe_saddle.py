#!/usr/bin/env python3
"""HOSE_SADDLE_FIX_STOPS_SHORT_OF_PIPE: a hose end lying BESIDE a pipe couples on a saddle clamped on the pipe.

Naive judge, live 2026-10-23: a hose "coupled to universal pipe" from the north ended on the cell edge, ~0.5 cell short of
the pipe's centre line, mid-air, with no saddle (DrawEnds put every port coupling at pts[n-1] + side * 0.5; the pipe-side
fitting was a flange hidden under that coupling; HoseJointProbe measured the same cell edge, so it passed the bug).

Linux-only (no dotnet): re-measures the saddle art's spigot reach in all four looks against LiquidJoinRule.SaddleSpigotReach,
checks HoseSaddleBeside's face and turn by turning the canvas spigot in Python, and checks the draw and the probe both use
the rule (and the old cell-edge face is gone). The C# twin is LiquidJoin_hose_saddle_beside_pipe_reaches_spigot.

    python3 src/RimMandrake/FlowWorks/selftest_hose_pipe_saddle.py      # exit 1 on any FAIL
"""
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
JOINS_TEX = os.path.join(HERE, "Textures", "RimMandrake", "FlowWorks", "Joins")
LOOKS = ("Modern", "Scrapper", "Industrial", "Futuristic")

rows = []


def check(name, ok, detail=""):
    rows.append((name, bool(ok)))
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, (" -- " + detail) if detail else ""))


def read(*parts):
    with open(os.path.join(SRC, *parts), encoding="utf-8-sig") as f:
        return f.read()


def body(src, signature):
    """The text of the method whose declaration contains `signature`, up to the next member declaration."""
    i = src.find(signature)
    if i < 0:
        return ""
    j = re.search(r"\n        (?:public|internal|private|protected)[^\n]*\(", src[i + len(signature):])
    return src[i:i + len(signature) + (j.start() if j else len(src))]


def spigot_reach(path):
    """Cells from the canvas centre to the lowest opaque row (the spigot tip; the canvas spans one cell)."""
    from PIL import Image
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    bb = im.split()[3].point(lambda a: 255 if a > 128 else 0).getbbox()
    if bb is None:
        return None, None
    return (bb[3] - h / 2.0) / h, bb


rule = read("Machinery", "LiquidJoinRule.cs")
m = re.search(r"public const double SaddleSpigotReach = ([0-9.]+);", rule)
check("rule_constant_present", m is not None, "LiquidJoinRule.SaddleSpigotReach")
REACH = float(m.group(1)) if m else float("nan")

# 1. the constant is the art's spigot, in every look (sanity: the instrument sees a real sprite, not an empty canvas)
for look in LOOKS:
    p = os.path.join(JOINS_TEX, look, "Saddle.png")
    if not os.path.exists(p):
        check("art_%s_saddle_exists" % look, False, p)
        continue
    r, bb = spigot_reach(p)
    seen = bb is not None and (bb[3] - bb[1]) > 20 and (bb[2] - bb[0]) > 10
    check("art_%s_saddle_visible" % look, seen, "bbox %s" % (bb,))
    check("art_%s_spigot_reach" % look, r is not None and abs(r - REACH) <= 0.03,
          "measured %.3f cell vs rule %.3f" % (r if r is not None else float("nan"), REACH))

# 2. HoseSaddleBeside: face -side * reach, angle turns the canvas spigot (0,-1) toward the hose (-side)
hb = body(rule, "public static void HoseSaddleBeside(")
check("rule_face_formula", "faceX = -sx * SaddleSpigotReach;" in hb and "faceZ = -sz * SaddleSpigotReach;" in hb)
am = re.search(r"angleDeg = sx == 0 \? \(sz == 1 \? (\d+) : (\d+)\) : \(sx == 1 \? (\d+) : (\d+)\);", hb)
check("rule_angle_formula_present", am is not None)
if am:
    s1, s_1, e1, e_1 = (int(g) for g in am.groups())
    for sx, sz in ((1, 0), (0, 1), (-1, 0), (0, -1)):
        a = (s1 if sz == 1 else s_1) if sx == 0 else (e1 if sx == 1 else e_1)
        r = math.radians(a)
        # Unity's y rotation turns clockwise seen from above: (0,-1) -> (-sin a, -cos a)
        sp = (-math.sin(r), -math.cos(r))
        check("rule_spigot_faces_hose_side_%d_%d" % (sx, sz), abs(sp[0] + sx) < 1e-9 and abs(sp[1] + sz) < 1e-9,
              "angle %d points (%.2f,%.2f), want (%d,%d)" % (a, sp[0], sp[1], -sx, -sz))
    # the item's geometry: a hose from the north (end on the cell above, side (0,-1)) of a pipe at (10,10)
    face_z = 10.5 + 1 * REACH
    old_face_z = 11.5 - 0.5
    check("north_hose_face_on_spigot_not_cell_edge", abs(face_z - 10.5) <= 0.2 and abs(old_face_z - 10.5) >= 0.45,
          "new face %.2f cell from the pipe line, old %.2f" % (face_z - 10.5, old_face_z - 10.5))

# 3. the pipe-side fitting beside a pipe is the turned saddle, not a flange
joins = read("Machinery", "RM_LiquidJoins.cs")
dh = body(joins, "public static void DrawHosePortFitting(")
check("draw_saddle_not_flange", 'Mat("Saddle", LookOf(port))' in dh and "LiquidJoinRule.Flange(" not in dh
      and "LiquidJoinRule.HoseSaddleBeside(sideX, sideZ, out _, out _, out double ang)" in dh
      and "Quaternion.Euler(0f, (float)ang, 0f)" in dh)

# 4. the hose: the coupling's face and the reach ribbon both go to the spigot
hoses = read("Hose", "RM_MapComponent_Hoses.cs")
ps = body(hoses, "internal static bool PipeSaddleFace(")
check("face_helper_uses_rule", "fe.PortKind != HosePortKind.Pipe" in ps and "LiquidJoinRule.HoseSaddleBeside(sx, sz, out double fx, out double fz, out _)" in ps
      and "fe.Port.Position.x + 0.5 + fx" in ps and "fe.Port.Position.z + 0.5 + fz" in ps)
check("drawends_face_on_saddle", "bool onSaddle = PipeSaddleFace(fe, out V2 saddleFace);" in hoses
      and "HoseMath.PortFitting(pts, onSaddle ? saddleFace : pts[n - 1] + dp * 0.5, dp," in hoses)
check("can_fail_old_cell_edge_face_gone", "HoseMath.PortFitting(pts, pts[n - 1] + dp * 0.5, dp," not in hoses)
check("drawends_reach_ribbon", "DrawPortStub(r, fe, hm, vis, y - 0.001f, pts[n - 1], onSaddle ? saddleFace : (V2?)null)" in hoses
      and "new[] { hoseEnd.X, hoseEnd.Z, saddleFace.Value.X, saddleFace.Value.Z }" in hoses)

# 5. the probe measures the spigot, not the cell edge
probe = read("Hose", "HoseJointProbe.cs")
check("probe_measures_spigot", "RM_MapComponent_Hoses.PipeSaddleFace(fe, out V2 saddleFace)" in probe
      and "- dp * RimMandrake.FlowWorks.Machinery.LiquidJoinRule.SaddleSpigotReach" in probe)

bad = [n for n, ok in rows if not ok]
print("hose pipe saddle: %d/%d rows PASS%s" % (len(rows) - len(bad), len(rows), (" -- FAIL " + ", ".join(bad)) if bad else ""))
sys.exit(1 if bad else 0)
