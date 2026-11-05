#!/usr/bin/env python3
"""POND_DRAWN_FIX_VERYSHALLOW_NEVER_MUDS: a drawn-down flat pond's residue is mud, not 25 very-shallow sources.

Live (plot_D, 2026-10-24): a 5x5 pond (bed 2, 50 levels) drawn to stock 0.00 by a D=3 channel kept all 25 squares
RM_WaterVeryShallow, isSource true, recededCount 0, for every later pulse. Cause: StagePond's exact path laid the last
litres EXACTLY level over every square and RM_PondDepthMath.StageForExact called anything >= 0.5 dL (0.05 L) a square
water. The fix: a film (PondFilmDl, 1 cm) below which a wet square is mud, and a re-wet line (PondRewetDl, twice it)
a dry square must reach, so a pond balanced near the film does not flicker.

Offline, no dotnet (the C# twin is LevelExactChecks.Exact_pond_drawn_flat_residue_is_mud, run by
selftest_flowworks_stock.py): reads the constants from the PRODUCTION C# source, pins the StagePond / StageForExact
lines that apply them, and sweeps the item's pond through level_water's exact surface (the C# twin of
RM_LevelSolve.PondSurfaceHeight / PondSquareWater).

    python3 src/RimMandrake/Utils/selftest_flowworks_pond_film.py
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "FlowWorks", "Source"))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "FlowWorks", "northstar")))

import level_water as lw  # noqa: E402

FAILS = []


def check(ok, what):
    print(("ok    " if ok else "FAIL  ") + what)
    if not ok:
        FAILS.append(what)


def src(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def strip_comments(text):
    return "\n".join(line for line in text.splitlines() if not line.strip().startswith("//"))


def main():
    pdm = src("RM_PondDepthMath.cs")
    stock = strip_comments(src("RM_LiquidStock.cs"))
    U = lw.U
    check(U == 10000, "U read from RM_Volume.cs is 10,000 dL a notch (got %r)" % U)

    m = re.search(r"public const double PondFilmDl\s*=\s*RM_LevelSolve\.U\s*/\s*([0-9.]+)\s*;", pdm)
    check(m is not None, "RM_PondDepthMath declares PondFilmDl = RM_LevelSolve.U / k")
    film = U / float(m.group(1)) if m else float("nan")
    check(abs(film * lw.M_PER_UNIT - 0.01) < 1e-9, "the film is 1 cm of water (%.4f m)" % (film * lw.M_PER_UNIT))
    check(re.search(r"public const double PondRewetDl\s*=\s*2\.0\s*\*\s*PondFilmDl\s*;", pdm) is not None,
          "PondRewetDl is twice the film")
    rewet = 2.0 * film

    body = re.search(r"public static Stage StageForExact\(double waterDl, int bed, bool wetNow = true\)\s*\{(.*?)\n\t\t\}", pdm, re.S)
    check(body is not None, "StageForExact takes wetNow")
    b = body.group(1) if body else ""
    check(re.search(r"if \(waterDl < \(wetNow \? PondFilmDl : PondRewetDl\)\)\s*\{\s*return Stage\.Mud;", b) is not None,
          "StageForExact: under the film (wet) / re-wet line (dry) is Mud")
    check("0.5" not in b, "StageForExact no longer dries at half a decilitre")

    sp = re.search(r"private void StagePond\(.*?\n\t\t\}\n", stock, re.S)
    check(sp is not None, "StagePond found")
    s = sp.group(0) if sp else ""
    check(re.search(r"bool wetNow = owner\.IsWaterNow\(c\);\s*if \(exact\)", s) is not None,
          "StagePond reads wetNow before staging the exact path")
    check(re.search(r"st = RM_PondDepthMath\.StageForExact\(wd, bed, wetNow\);\s*w = st == RM_PondDepthMath\.Stage\.Mud \? 0 : 1;", s)
          is not None, "StagePond's wet/dry follows StageForExact (wetNow passed; Mud means dry)")
    check("wd >= 0.5" not in s, "StagePond no longer calls 0.5 dL water")
    check(s.count("bool wetNow") == 1, "one wetNow in StagePond")

    def stage_dry(wd, wet_now):
        """True when StageForExact (as pinned above) says Mud for wd dL on a bed-2 square."""
        return wd < (film if wet_now else rewet)

    # the item's pond: 25 squares, bed 2, drawn to stock "0.00" (< 50 dL) or any residue under 25 cm of film
    h = lw.histogram([2] * 25)
    for left in (1, 5, 40, 49, 500, 2500, 25 * 199):
        wd = lw.pond_square_water(2, h, left)
        old_wet = wd >= 0.5
        check(stage_dry(wd, True), "%d dL left on the 5x5 pond (%.2f dL a square): every square muds%s"
              % (left, wd, " (was VeryShallow before the fix)" if old_wet else ""))
    # a real sheet stays water; the receded count on the item's pond goes 0 -> 25 at its residue
    wd = lw.pond_square_water(2, h, 25 * 2000)
    check(not stage_dry(wd, True), "10 cm over the pond stays water")
    receded = sum(1 for _ in range(25) if stage_dry(lw.pond_square_water(2, h, 40), True))
    check(receded == 25, "the drawn pond at 40 dL reads recededCount 25 (live read 0)")
    # hysteresis: walk the stock up and down across the film; a square flips at most once per crossing
    wet, flips = True, 0
    for left in list(range(0, 25 * 600, 25 * 10)) + list(range(25 * 600, 0, -25 * 10)):
        wd = lw.pond_square_water(2, h, left)
        now_wet = not stage_dry(wd, wet)
        flips += now_wet != wet
        wet = now_wet
    check(flips <= 3, "a stock swept 0 -> 3 cm -> 0 flips a square at most 3 times (got %d)" % flips)
    # a dry square between the film and twice it stays dry; at twice it, water returns
    check(stage_dry(1.5 * film, False) and not stage_dry(1.5 * film, True), "between film and re-wet: dry stays dry, wet stays wet")
    check(not stage_dry(rewet, False), "a dry square re-wets at twice the film")

    print("\n%d failing" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
