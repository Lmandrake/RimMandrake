"""Write (or check) the golden tables of FlowWorks/Source/SelfTest/PitSteppedReliefChecks.cs from pitrule.py, the offline twin
of RM_PitReliefMath's stepped-pit rule (RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM).

    python3 gen_golden.py --write     rewrite the tables between the BEGIN/END GOLDEN markers
    python3 gen_golden.py             exit 1 when the C# file's tables differ from what pitrule.py gives now

Depths in the C# are notches (0.5 m); pitrule.py works in metres.
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pitrule as R  # noqa: E402

CS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "src", "RimMandrake", "FlowWorks", "Source", "SelfTest",
                                   "PitSteppedReliefChecks.cs"))

# the sweep's cases plus a wet one; metres, rows north first
CASES = {
    "L": [[4, 4, 8], [4, 8, 8], [8, 8, 8]],
    "step26": [[2] * 4, [2] * 4, [6] * 4, [6] * 4],
    "step62": [[6] * 4, [6] * 4, [2] * 4, [2] * 4],
    "stepNS": [[2, 2, 6, 6]] * 4,
    "three": [[1] * 3, [3] * 3, [6] * 3],
    "corner": [[2, 2, 2], [2, 2, 2], [2, 2, 6]],
    "hole": [[1, 1, 1], [1, 6, 1], [1, 1, 1]],
    "island": [[6, 6, 6], [6, 1, 6], [6, 6, 6]],
    "trench3": [[3], [3], [3], [3]],
    "trench8": [[8], [8], [8]],
    "single4": [[4]],
}
LIT_CASES = ["L", "step26", "step62", "stepNS", "three", "hole", "island", "trench8"]
LIT_SAMPLES = [0.1, 0.3, 0.5, 0.7, 0.9]


def f(v: float) -> str:
    return f"{v:.5f}f"


def window(grid, r, c):
    """The 5x5 depths (notches) centred on (r, c), north row first; off the grid reads as ground."""
    out = []
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            out.append(int(round(R._at(grid, r + dr, c + dc) * 2)))
    return out


def tables() -> str:
    L = ["\t\t// BEGIN GOLDEN (design/specs/2026-11-22-stepped-pit-inner-cliff/gen_golden.py --write)"]
    L.append("\t\t// notches -> H, W, K")
    L.append("\t\tinternal static readonly float[,] CurveGolden =\n\t\t{")
    for n in range(0, 41):
        z = n * 0.5
        L.append(f"\t\t\t{{ {n}f, {f(R.H(z))}, {f(R.W(z))}, {f(R.K(z))} }},")
    L.append("\t\t};")
    L.append("\t\t// d n s w e nw ne lv(notches) -> t l r lt rt hvL hvR sl cnwW cnwH cneW cneH lipN0 lipN1 lipW0 lipE0 (-1: no line)"
             " edgeN edgeS edgeW edgeE")
    L.append("\t\tinternal static readonly float[,] PlanGolden =\n\t\t{")
    rows = []
    for grid in CASES.values():
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if grid[r][c] > 0:
                    for lv in (0.0, 1.0):
                        rows.append((grid, r, c, lv))
    seen = set()
    for grid, r, c, lv in rows:
        nb = tuple(int(round(R._at(grid, r + dr, c + dc) * 2)) for dr, dc in
                   ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1)))
        key = nb + (lv,)
        if key in seen:
            continue
        seen.add(key)
        p = R.plan_cell(grid, r, c, lv * 0.5)
        lipn = p["lip_n"] or (-1.0, -1.0)
        lipw = p["lip_w"][0] if p["lip_w"] else -1.0
        lipe = p["lip_e"][0] if p["lip_e"] else -1.0
        vals = list(nb) + [lv * 1.0, p["t"], p["l"], p["r"], p["lt"], p["rt"], p["hv_l"], p["hv_r"], p["sl"], *p["cnw"], *p["cne"],
                           lipn[0], lipn[1], lipw, lipe] + [1.0 if p[k] else 0.0 for k in ("edge_n", "edge_s", "edge_w", "edge_e")]
        L.append("\t\t\t{ " + ", ".join(f(v) for v in vals) + " },")
    L.append("\t\t};")
    L.append("\t\t// 25 depths (5x5 notches, north row first, the square at the centre), fx, fy (y down) -> lit")
    L.append("\t\tinternal static readonly float[,] LitGolden =\n\t\t{")
    for name in LIT_CASES:
        grid = CASES[name]
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if grid[r][c] <= 0:
                    continue
                win = window(grid, r, c)
                for fy in LIT_SAMPLES:
                    for fx in LIT_SAMPLES:
                        v = R.lit_at(grid, c + fx, r + fy)
                        L.append("\t\t\t{ " + ", ".join(f"{d}f" for d in win) + f", {f(fx)}, {f(fy)}, {f(v)} }},")
    L.append("\t\t};")
    L.append(f"\t\tinternal const float FaceLightN = {f(R.face_light('n'))}, FaceLightW = {f(R.face_light('w'))}, "
             f"FaceLightE = {f(R.face_light('e'))}, ShadowDark = {f(R.shadow_dark())};")
    L.append("\t\t// END GOLDEN")
    return "\n".join(L)


def main() -> int:
    src = open(CS).read()
    m = re.search(r"\t\t// BEGIN GOLDEN.*?// END GOLDEN", src, re.S)
    if not m:
        print(f"FAIL no GOLDEN markers in {CS}")
        return 2
    new = tables()
    if "--write" in sys.argv:
        open(CS, "w").write(src[:m.start()] + new + src[m.end():])
        print(f"WROTE {CS}")
        return 0
    if m.group(0) != new:
        print("FAIL the golden tables differ from pitrule.py: run gen_golden.py --write")
        return 1
    print("PASS the golden tables match pitrule.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
