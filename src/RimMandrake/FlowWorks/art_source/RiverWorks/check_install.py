#!/usr/bin/env python3
"""Installed-art check for the bank stake + silt-trap looks (RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS fixes 8 and 10). The C#
selftest cannot see textures (winbuild does not stage Textures/), so this does: every texPath the defs name resolves to a
PNG, the ridge spans tile seamlessly along their run, and the canvases match RM_RiverMath's draw sizes.
Exit 0 = all PASS. Usage: check_install.py"""
import colorsys
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

MOD = Path(__file__).resolve().parents[2]
TEX = MOD / "Textures"
fails = []


def check(ok, what):
    print(("PASS  " if ok else "FAIL  ") + what)
    if not ok:
        fails.append(what)


xml = (MOD / "Defs" / "Rivers" / "RM_BankWorksStyles.xml").read_text() + (MOD / "Defs" / "Rivers" / "RM_BankWorks.xml").read_text()
paths = set(re.findall(r"<(?:texPath|uiIconPath)>(RimMandrake/FlowWorks/Rivers/[^<]+)</", xml))
check(len(paths) >= 8, f"defs name {len(paths)} river-works look paths (expect >= 8)")
for p in sorted(paths):
    check((TEX / (p + ".png")).is_file(), f"resolves {p}")
for look in ("Scrapper", "Industrial", "Modern", "Futuristic"):
    d = TEX / "RimMandrake" / "FlowWorks" / "Rivers" / look
    h = np.array(Image.open(d / "RM_BankStakeRidge_h.png").convert("RGBA")).astype(int)
    v = np.array(Image.open(d / "RM_BankStakeRidge_v.png").convert("RGBA")).astype(int)
    check(h.shape[:2] == (48, 128) and v.shape[:2] == (128, 64), f"{look} ridge canvases 128x48 / 64x128")
    check(np.abs(h[:, 0] - h[:, -1]).mean() < 12, f"{look} ridge_h seamless E-W (edge diff {np.abs(h[:, 0] - h[:, -1]).mean():.1f})")
    check(np.abs(v[0] - v[-1]).mean() < 12, f"{look} ridge_v seamless N-S (edge diff {np.abs(v[0] - v[-1]).mean():.1f})")
# SILT_TRAP_STYLES_REDRAW_HALF_RES_FLAT: the styled traps had been 128 px frontal panels beside a 256 px oblique base.
# Each look is now at the base's 256 px and camera (its silhouette's bottom edge slopes down left to right; a frontal
# panel measures ~0, the old base 0.31) and keeps its trim (fraction of opaque pixels in the trim's hue band).
TRIM = {"Scrapper": ("rust", (10, 35, .45, .3), 0.10), "Industrial": ("hazard yellow", (40, 60, .5, .4), 0.005),
        "Modern": ("red", (345, 370, .5, .4), 0.10), "Futuristic": ("cyan", (170, 200, .4, .5), 0.02)}
for look, (name, (h0, h1, smin, vmin), need) in TRIM.items():
    im = Image.open(TEX / "RimMandrake" / "FlowWorks" / "Rivers" / look / "RM_SiltTrap.png").convert("RGBA")
    check(im.size == (256, 256), f"{look} silt-trap canvas 256x256 (got {im.size[0]}x{im.size[1]})")
    a = np.array(im).astype(float)
    op = a[..., 3] > 40
    xs = np.nonzero(op.any(0))[0]
    slope = np.polyfit(xs, [np.nonzero(op[:, x])[0].max() for x in xs], 1)[0]
    check(slope >= 0.15, f"{look} silt-trap oblique (bottom-edge slope {slope:.2f} >= 0.15)")
    hsv = np.array([colorsys.rgb_to_hsv(*px) for px in a[..., :3][op][::7] / 255])
    hue = hsv[:, 0] * 360
    hue = np.where(hue < h0, hue + 360, hue) if h1 > 360 else hue
    frac = ((hue >= h0) & (hue <= h1) & (hsv[:, 1] >= smin) & (hsv[:, 2] >= vmin)).mean()
    check(frac >= need, f"{look} silt-trap keeps its {name} trim ({frac:.3f} >= {need})")
check((TEX / "RimMandrake" / "FlowWorks" / "Rivers" / "RM_SiltWedge.png").is_file(), "silt wedge installed")
print("\n" + ("PASS: 0 failure(s)" if not fails else f"FAIL: {len(fails)} failure(s)"))
sys.exit(1 if fails else 0)
