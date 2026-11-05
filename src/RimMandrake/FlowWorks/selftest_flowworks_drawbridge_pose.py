"""DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED: a raised drawbridge leaf is drawn as a rigid leaf turned about its hinge, never an
upright picture stretched to the leaf's full length up the screen (owner 2026-11-03: "The north-south bridge looks as though
it's down, yet it says it's up"; the old draw covered 100% of a north-running gap).

Offline, no dotnet: the constants are read from Source/RM_DrawbridgeMath.cs (DrawbridgeLeafPose) and the formulas are mirrored
here; each mirrored C# formula string is checked present (pair honesty). Swept over every direction, leaf length 1-14 and
rise 0..1:
  - the ruled holds (owner's build spec 2026-11-04): hinge on the north bank (leaf runs south) 55, south bank 85, east/west 75;
  - raised, at least 40% of the gap is open on screen in every direction and length (the leaf no longer reads lowered);
  - raised, the painted top shows (never edge-on, never the underside);
  - angle 0 draws exactly the flat deck footprint (no pop on the first tick), and the gap only opens as it rises;
  - true length constant: one picture slice per cell, root at the hinge, tip at the tip, middles repeat (no stretch);
  - every lane's draw matrix keeps the picture's handedness (no back face) in all four directions;
  - DrawLeafUp draws through the pose and slices; the old full-height stretch is gone.

Can-fail: --canfail replays the old draw (screen length = leaf length up the screen) and must FAIL.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_drawbridge_pose.py [--canfail]
"""
from __future__ import annotations

import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MATH = os.path.join(HERE, "Source", "RM_DrawbridgeMath.cs")
ART = os.path.join(HERE, "Source", "Pits", "Drawbridge", "RM_DrawbridgeArt.cs")
DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0)]


def body(src: str, sig: str) -> str:
    a = src.index(sig)
    i = src.index("{", a)
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return src[a:j + 1]
    raise ValueError("unbalanced " + sig)


def const(src: str, name: str) -> float:
    m = re.search(r"public const (?:double|int) " + name + r" = ([0-9.]+);", src)
    if not m:
        raise ValueError("missing constant " + name)
    return float(m.group(1))


def main(canfail: bool) -> int:
    fails: list[str] = []

    def check(ok: bool, msg: str) -> None:
        if not ok:
            fails.append(msg)

    src = open(MATH, encoding="utf-8").read()
    pose = body(src, "public static class DrawbridgeLeafPose")
    K = const(pose, "K")
    holds = {"S": const(pose, "HoldRunningSouth"), "N": const(pose, "HoldRunningNorth"), "EW": const(pose, "HoldEastWest")}
    slices = int(const(pose, "Slices"))
    check(K == 0.5, f"K {K} is not the v3 sheet's 0.5")
    check(holds == {"S": 55.0, "N": 85.0, "EW": 75.0}, f"holds {holds} are not the ruled 55/85/75")
    check(slices == 4, f"slices {slices}: the Face picture is 1 x 4 cells")
    # pair honesty: the mirrored formulas are the C#'s
    for frag in ("return dz < 0 ? HoldRunningSouth : dz > 0 ? HoldRunningNorth : HoldEastWest;",
                 "return HoldDegrees(dx, dz) * r;",
                 "x = dx * c;", "z = dz * c + K * s;",
                 "double along = dx * x + dz * z;",
                 "return System.Math.Max(0.0, 1.0 - along / length);",
                 "return 1 + (i - 1) % (Slices - 2);"):
        check(frag in pose, "C# formula not found (mirror drifted): " + frag)

    def hold(dx: int, dz: int) -> float:
        return holds["S"] if dz < 0 else holds["N"] if dz > 0 else holds["EW"]

    def cell(dx: int, dz: int, deg: float) -> tuple[float, float]:
        if canfail:   # the old draw: a picture the leaf's full length standing up the screen at any rise
            return (0.0, 1.0) if deg > 0 else (dx, dz)
        a = math.radians(deg)
        return dx * math.cos(a), dz * math.cos(a) + K * math.sin(a)

    def gap_open(dx: int, dz: int, length: int, deg: float) -> float:
        x, z = cell(dx, dz, deg)
        along = (dx * x + dz * z) * length
        return 1.0 if along <= 0 else max(0.0, 1.0 - along / length)

    def slice_for(i: int, length: int) -> int:
        return 0 if i <= 0 else slices - 1 if i >= length - 1 else 1 + (i - 1) % (slices - 2)

    worst = {}
    for dx, dz in DIRS:
        h = hold(dx, dz)
        for length in range(1, 15):
            g = gap_open(dx, dz, length, h)
            worst[(dx, dz)] = min(worst.get((dx, dz), 1.0), g)
            check(g >= 0.40, f"raised leaf ({dx},{dz}) L{length} covers the gap: only {g:.0%} open")
            x, z = cell(dx, dz, h)
            check(dx * x + dz * z > 1e-9, f"({dx},{dz}) hold {h}: top not shown (edge-on or underside)")
            fx, fz = cell(dx, dz, 0.0)
            check(abs(fx - dx) < 1e-9 and abs(fz - dz) < 1e-9, f"({dx},{dz}) angle 0 is not the flat deck (pop)")
            prev = -1.0
            for t in range(101):
                o = gap_open(dx, dz, length, h * t / 100.0)
                check(o >= prev - 1e-9, f"({dx},{dz}) L{length}: the gap closes again at rise {t}%")
                prev = o
            ss = [slice_for(i, length) for i in range(length)]
            check(ss[0] == 0 and (length == 1 or ss[-1] == slices - 1), f"L{length} slices {ss}: root/tip misplaced")
            check(all(0 < s < slices - 1 for s in ss[1:-1]), f"L{length} slices {ss}: a middle cell repeats root or tip")
            # handedness of the lane matrix: columns across=(dz,0,-dx), Y, along=(x,0,z); det = across.x*along.z - across.z*along.x
            ax, az = dz, -dx
            det = ax * z - az * x
            check(det > 0, f"({dx},{dz}) lane matrix flips the picture (det {det:.3f}): back face")

    art = open(ART, encoding="utf-8").read()
    up = body(art, "public static void DrawLeafUp(")
    check("DrawbridgeLeafPose.AngleDegrees(step.x, step.z, (double)l.progress / full)" in up, "DrawLeafUp does not turn the leaf by the pose")
    check("DrawbridgeLeafPose.CellVector(step.x, step.z, deg, out double vx, out double vz)" in up, "DrawLeafUp does not project the cell")
    check("LeafSlice(DrawbridgeLeafPose.SliceFor(i, length))" in up, "DrawLeafUp does not draw per-cell slices")
    check("new Vector4(step.z, 0f, -step.x, 0f)" in up, "the lane's across vector is not the one checked for handedness")
    check("new Vector3(1f, 1f, h)" not in up and "at.z += h" not in up, "the old full-height stretch is still drawn")

    print("worst gap open at hold: " + ", ".join(f"{d}: {w:.0%}" for d, w in worst.items()))
    if fails:
        print(f"FAIL ({len(fails)}): " + "; ".join(fails[:6]))
        return 1
    print("PASS drawbridge leaf pose")
    return 0


if __name__ == "__main__":
    cf = "--canfail" in sys.argv
    rc = main(cf)
    if cf:
        print("can-fail " + ("OK (failed as it must)" if rc else "BROKEN (passed on the old draw)"))
        sys.exit(0 if rc else 1)
    sys.exit(rc)
