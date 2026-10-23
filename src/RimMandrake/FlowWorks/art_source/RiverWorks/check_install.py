#!/usr/bin/env python3
"""Installed-art check for the bank stake + silt-trap looks (RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS fixes 8 and 10). The C#
selftest cannot see textures (winbuild does not stage Textures/), so this does: every texPath the defs name resolves to a
PNG, the ridge spans tile seamlessly along their run, and the canvases match RM_RiverMath's draw sizes.
Exit 0 = all PASS. Usage: check_install.py"""
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
check((TEX / "RimMandrake" / "FlowWorks" / "Rivers" / "RM_SiltWedge.png").is_file(), "silt wedge installed")
print("\n" + ("PASS: 0 failure(s)" if not fails else f"FAIL: {len(fails)} failure(s)"))
sys.exit(1 if fails else 0)
