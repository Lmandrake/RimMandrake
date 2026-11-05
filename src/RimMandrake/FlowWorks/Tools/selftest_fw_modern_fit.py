#!/usr/bin/env python3
"""selftest_fw_modern_fit.py -- the Modern pipe system's FIT defects as offline checks (MODERN_FIT_REDRAW_ROUND_FOUR_PENDING).

The item listed five fit defects the art-eval pipeline found on the 2026-10-23 white-PVC candidates. Those candidates were
never installed: the owner accepted the Modern waterworks blue instead (2026-10-24, "I like the new blue pipes."), so each
defect is measured here on the INSTALLED Modern art, against the pipe's 0.136-cell bore (RM_PipePoleMath: 18 of 132
displayed px):

  flange_girth   Joins/Modern/Flange.png, drawn at LiquidJoinRule.FlangeSize 0.5 cell: its ring across the pipe >= RING_MIN
                 x bore. FAILS on the shipped ring (the red original's geometry, 33 of 128 px = 0.129 cell, thinner than
                 the pipe it bolts onto); PASSES installed (girth_fit.py).
  coupler_girth  Joins/Modern/Coupler.png (the machine-tank coupler, same quad): its rings >= RING_MIN x bore and no wider
                 across than the Modern pump's own end flange (so it is not "fatter than the pipe" by more than a flange
                 is). FAILS on the shipped 31 px = 0.121 cell; can-fail on the high side: the ring stretched past the pump's.
  tee_blind_lobe every Modern tee cell of UniversalPipe_Atlas (masks 7, 11, 13, 14): the hub's bulge past the bore on the
                 side with no branch <= LOBE_MAX x bore. Can-fail: a disc of 0.6 x bore pasted on each blind side.
  pinned         installed Flange/Coupler == girth_fit.build pixel for pixel.

The other two defects are the hose rig's and are measured by selftest_hose_fittings.py on the installed art: the pump's
stubs drawing over the hose coupler and the gap at the tank nipple both became the under-coupler design (owner ruling
2026-10-23: couplers "go UNDER the tank or pump"), and that gate reads 0 gap, coupler beneath, at every Modern pump and
tank port. This file runs that gate and requires its table to hold all four sides of the Modern pump and tank, each at 0
gap with the coupler beneath (so it cannot pass by not looking).
"""
# selftest-timeout: 400
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
FW = HERE.parent
TEX = FW / "Textures/RimMandrake/FlowWorks"
sys.path.insert(0, str(FW / "art_source" / "ModernStyle"))
import girth_fit as gf  # noqa: E402
import waterworks_blue as wb  # noqa: E402

BORE = 0.136          # cell (fw_offline_checks.BORE)
RING_MIN = 1.3        # a flange ring stands proud of its pipe
LOBE_MAX = 0.35       # a tee hub's bulge on its blind side, x bore
SHOWN = 132           # atlas px per displayed cell (176 px tile, 22 px pad each side)
ALPHA = 40
fails = []


def want(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


def pump_flange_cells():
    """The Modern pump's widest end-flange extent across its east stub (outer 15% of the 1-cell sprite), cells."""
    a = np.asarray(Image.open(TEX / "Pump/Modern/RM_LiquidPump.png").convert("RGBA"))[..., 3] > ALPHA
    w = a.shape[1]
    band = a[:, int(w * 0.85):]
    return float(band.sum(0).max()) / a.shape[0]


def girth():
    pump = pump_flange_cells()
    want(pump > RING_MIN * BORE, "pump end flange is a real flange (%.3f cell > %.3f): the coupler's upper bound is not vacuous"
         % (pump, RING_MIN * BORE))
    for rel, upper in (("Joins/Modern/Flange.png", None), ("Joins/Modern/Coupler.png", pump)):
        name = rel.split("/")[-1][:-4]
        shipped = gf.across_cells(Image.open(wb.RED / rel))
        live = gf.across_cells(Image.open(TEX / rel))

        def ok(c):
            return c >= RING_MIN * BORE and (upper is None or c <= upper)
        bar = ">= %.3f%s" % (RING_MIN * BORE, "" if upper is None else " and <= %.3f" % upper)
        want(not ok(shipped), "%s girth FAILS on the shipped ring: %.3f cell (x%.2f bore), bar %s" % (name, shipped, shipped / BORE, bar))
        want(ok(live), "%s girth passes installed: %.3f cell (x%.2f bore), bar %s" % (name, live, live / BORE, bar))
        if upper is not None:
            fat = gf.across_cells(gf.fit(Image.open(wb.RED / rel), cells=upper + 0.03))
            want(not ok(fat), "%s can-fail: stretched to %.3f cell it is fatter than the pump's flange %.3f" % (name, fat, upper))
        want(np.array_equal(np.asarray(gf.build(rel)), np.asarray(Image.open(TEX / rel).convert("RGBA"))),
             "%s installed == girth_fit.build pixel for pixel" % name)


TEES = ((7, "W"), (11, "S"), (13, "E"), (14, "N"))   # link mask (N1 E2 S4 W8) -> its side with no branch


def blind_bulges(atlas):
    a = np.asarray(atlas.convert("RGBA"))[..., 3] > ALPHA
    t = a.shape[0] // 4
    out = {}
    for m, blind in TEES:
        cell = a[(3 - m // 4) * t:(4 - m // 4) * t, (m % 4) * t:(m % 4 + 1) * t]
        mid = t / 2.0
        if blind in "WE":
            idx = np.where(cell.any(0))[0]
            px = mid - idx[0] if blind == "W" else idx[-1] + 1 - mid
        else:
            idx = np.where(cell.any(1))[0]
            px = mid - idx[0] if blind == "N" else idx[-1] + 1 - mid
        out[blind] = round(float(px * (176.0 / t) / SHOWN - BORE / 2), 4)
    return out


def lobed(atlas):
    im = atlas.convert("RGBA").copy()
    t = im.size[1] // 4
    d = ImageDraw.Draw(im)
    r = 0.6 * BORE / 2 * SHOWN * t / 176.0
    reach = (BORE / 2 + 0.6 * BORE) * SHOWN * t / 176.0   # the disc's far edge 0.6 bore past the pipe wall
    for m, blind in TEES:
        x0, y0 = (m % 4) * t, (3 - m // 4) * t
        cx, cy = x0 + t / 2.0, y0 + t / 2.0
        dx, dy = {"W": (-1, 0), "E": (1, 0), "N": (0, -1), "S": (0, 1)}[blind]
        px, py = cx + dx * (reach - r), cy + dy * (reach - r)
        d.ellipse((px - r, py - r, px + r, py + r), fill=(90, 150, 200, 255))
    return im


def tees():
    atlas = Image.open(TEX / "Pipe/Modern/UniversalPipe_Atlas.png")
    for lab, im, exp in (("installed", atlas, True), ("can-fail: a lobe pasted on each blind side", lobed(atlas), False)):
        b = blind_bulges(im)
        ok = all(v <= LOBE_MAX * BORE for v in b.values())
        want(ok == exp, "tee_blind_lobe %s on the %s: bulge past the bore %s cell, bar <= %.3f"
             % ("PASSES" if exp else "FAILS", lab, {k: round(v, 3) for k, v in b.items()}, LOBE_MAX * BORE))


def hose_gate_sees_pump():
    """Defects 4 and 5 are selftest_hose_fittings' rows: run it and read its table for the Modern pump and tank ports."""
    import re
    import subprocess
    r = subprocess.run([sys.executable, str(FW / "selftest_hose_fittings.py"), "--table"], capture_output=True, text=True,
                       timeout=300)
    want(r.returncode == 0, "selftest_hose_fittings is green (exit %d)" % r.returncode)
    row = re.compile(r"^\s+(RM_LiquidPump|RM_LiquidTank)\s+Modern\s+(\w+)\s+lane \d+ .*with coupler ([\d.]+), beneath by ([\d.]+)",
                     re.M)
    seen = {}
    for kind, side, gap, under in row.findall(r.stdout):
        seen.setdefault(kind, []).append((side, float(gap), float(under)))
    for kind, sides in (("RM_LiquidPump", 4), ("RM_LiquidTank", 4)):
        got = seen.get(kind, [])
        ok = len({s for s, _, _ in got}) == sides and all(g == 0.0 and u > 0.0 for _, g, u in got)
        want(ok, "%s Modern: %d port rows on %d sides, every one 0 gap with the coupler beneath (%s)"
             % (kind, len(got), len({s for s, _, _ in got}), got))


if __name__ == "__main__":
    girth()
    tees()
    hose_gate_sees_pump()
    print("selftest_fw_modern_fit.py: %d failure(s)" % len(fails))
    sys.exit(1 if fails else 0)
