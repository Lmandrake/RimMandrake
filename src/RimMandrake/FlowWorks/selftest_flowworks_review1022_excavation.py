#!/usr/bin/env python3
"""FlowWorks code review 2026-10-22, RM_MapComponent_Excavation.cs (offline, no game). Each check reads the source and
fails on the pre-fix code; each carries a planted regression that must fail (can-fail).

THIN_SHEET_RUNS_INTO_BED: RunIntoBeds (a dug square whose water stands above a neighbouring dry pond bed's floor pours
  into the pond through the return leg) judged the water in WHOLE notches: `int f = min(fillGrid, depthGrid)`, `f == 0 ->
  continue`, and the move was TakeLevelCore (refuses fillGrid == 0). A part-notch sheet (F 0, part > 0; exact-level water)
  therefore never ran into a dry bed, and a whole-notch cell's part was ignored by the surface test. Fixed: f is the
  water's notches rounded UP (ceil(W/U)), which for integer depths is exactly the decilitre surface test, and with
  exact-level water the move is up to one level's decilitres (TakeDlCore -> TryReturnDl, room checked first).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
FAILS = []


def check(name, ok, detail=""):
    print("  %-5s %s %s" % ("ok" if ok else "FAIL", name, detail if not ok else ""))
    if not ok:
        FAILS.append(name)


def read(rel):
    return open(os.path.join(SRC, rel), encoding="utf-8").read()


def body_of(src, sig):
    i = src.index(sig)
    j = src.index("{", i)
    d = 0
    for k in range(j, len(src)):
        d += {"{": 1, "}": -1}.get(src[k], 0)
        if d == 0:
            return src[j:k + 1]
    raise ValueError(sig)


def norm(s):
    s = re.sub(r"//[^\n]*", "", s)
    return re.sub(r"\s+", " ", s)


# ── THIN_SHEET_RUNS_INTO_BED ────────────────────────────────────────────────────────────────────────────────────────
def bed_problems(src):
    probs = []
    try:
        b = norm(body_of(src, "private void RunIntoBeds()"))
    except ValueError:
        return ["RunIntoBeds not found"]
    if not re.search(r"long w = System\.Math\.Min\(WaterDl\(i\), depthGrid\[i\] \* \(long\)RM_LevelSolve\.U\);", b):
        probs.append("water not read in decilitres (WaterDl, clamped to the brim)")
    if not re.search(r"int f = \(int\)\(\(w \+ RM_LevelSolve\.U - 1\) / RM_LevelSolve\.U\);", b):
        probs.append("f is not ceil(W/U)")
    if re.search(r"int f = fillGrid\[i\]", b):
        probs.append("f still taken from whole notches")
    if "RM_Volume.RunsIntoBed(depthGrid[i], f, NaturalBedDepthAt(n))" not in b:
        probs.append("production rule RunsIntoBed no longer used")
    m = re.search(r"if \(LevelExact\) \{(.*?)continue; \} if \(!CanReturnLevels\(beds\[p\], fluid, 1\)", b)
    if not m:
        probs.append("no exact-level decilitre move before the whole-level move")
    else:
        e = m.group(1)
        order = [e.find("ReturnRoomDl(beds[p], fluid, want)"), e.find("TakeDlCore(pours[p], room, out _)"),
                 e.find("TryReturnDl(beds[p], fluid, took)")]
        if -1 in order or order != sorted(order):
            probs.append("exact move is not room-check -> take -> return: %r" % order)
        if "ReportLiquidLost(" not in e:
            probs.append("defensive failure path not disclosed")
    return probs


src = read("RM_MapComponent_Excavation.cs")
check("thin_sheet_runs_into_bed: fixed shape", not bed_problems(src), "; ".join(bed_problems(src)))

pre = src.replace("int f = (int)((w + RM_LevelSolve.U - 1) / RM_LevelSolve.U);",
                  "int f = fillGrid[i] > depthGrid[i] ? depthGrid[i] : fillGrid[i];")
check("thin_sheet_runs_into_bed: planted pre-fix f fails", bool(bed_problems(pre)))
_rb = src.index("private void RunIntoBeds()")
_a = src.index("if (LevelExact)", _rb)
_b = src.index("if (!CanReturnLevels(beds[p], fluid, 1)", _a)
pre2 = src[:_a] + src[_b:]
check("thin_sheet_runs_into_bed: planted pre-fix whole-level-only move fails", pre2 != src and bool(bed_problems(pre2)))

# The rule itself: d - ceil(W/U) < bed (RM_Volume.RunsIntoBed with f = ceil) == "surface above the bed floor" in dL.
vol = read("RM_Volume.cs")
m = re.search(r"public static bool RunsIntoBed\(int dugDepth, int fill, int bedDepth\)\s*\{\s*return (.*?);\s*\}", vol, re.S)
check("RunsIntoBed rule is the one modelled", bool(m) and norm(m.group(1)).strip()
      == "dugDepth > 0 && fill > 0 && bedDepth > 0 && dugDepth - fill < bedDepth")


def runs(d, f, bed):
    return d > 0 and f > 0 and bed > 0 and d - f < bed


U = 2000  # any positive U; the equivalence holds for every U
bad = []
for d in range(1, 13):
    for bed in range(1, 13):
        for w in list(range(0, d * U + 1, 97)) + [1, U - 1, U, U + 1, d * U - 1, d * U]:
            if w > d * U:
                continue
            truth = w > 0 and d * U - w < bed * U
            if runs(d, (w + U - 1) // U, bed) != truth:
                bad.append((d, bed, w))
check("ceil(W/U) is exactly the decilitre surface test", not bad, str(bad[:3]))
# planted: the pre-fix whole-notch f misses the thin sheet (D 1, 900 dL, bed 2)
check("planted: floor(W/U) misses a thin sheet", runs(1, 900 // U, 2) is False and runs(1, (900 + U - 1) // U, 2) is True)

if FAILS:
    print("FAILED: %d check(s): %s" % (len(FAILS), ", ".join(FAILS)))
    sys.exit(1)
print("all checks passed")
