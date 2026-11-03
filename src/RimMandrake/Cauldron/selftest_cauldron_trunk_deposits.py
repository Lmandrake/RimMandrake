#!/usr/bin/env python3
"""Pins for the Cauldron trunk-deposits design
(design/Jawa/worldbuilding/biomes/cauldron_trunk_deposits_design_2026-11-02.md,
item CAULDRON_TRUNK_DEPOSITS_DESIGN_CRYSTAL_FANS).

1. Every source fact the design states about today's tree is still true (def, single texture, the flecks
   extension and its class, the print postfix, the settings it names).
2. The registration instrument of the design's section 5: share of an overlay's opaque pixels inside the
   tree's dilated silhouette. Sanity probe: the tree measured against itself is 100 % inside, and a
   blank-canvas overlay with every pixel opaque is far from it, so the instrument can see a miss.
3. While the fleck art is the pre-fix art (CAULDRON_FLECKS_FIX_NUGGETS_IN_MIDAIR open), it measures below
   the 95 % bar; once redrawn it must pass. Any deposit overlay on disk must pass the bar and its coverage
   band.

    python3 src/RimMandrake/Cauldron/selftest_cauldron_trunk_deposits.py
"""
import os
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DOC = os.path.join(REPO, "design/Jawa/worldbuilding/biomes/cauldron_trunk_deposits_design_2026-11-02.md")
TEX = os.path.join(HERE, "Textures/Things/Plant")
TREE_PNG = os.path.join(TEX, "RM_TwistingThornwood/TwistingThornwood_a.png")
ALPHA_MIN = 16
DILATE_PX = 9
BAR = 0.95
COVERAGE = {"Deposits_Scab": (0.08, 0.25), "Deposits_Slag": (0.20, 0.45)}

fails = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        fails.append(name)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def alpha_mask(path, dilate=0):
    a = Image.open(path).convert("RGBA").getchannel("A")
    if dilate:
        a = a.filter(ImageFilter.MaxFilter(2 * dilate + 1))
    return np.array(a) > ALPHA_MIN


def inside_share(overlay, tree_dilated):
    n = int(overlay.sum())
    return (float((overlay & tree_dilated).sum()) / n) if n else 1.0


def tree_def():
    root = ET.parse(os.path.join(HERE, "Defs/ThingDefs_Plants/RM_CauldronFlora.xml")).getroot()
    for d in root.findall("ThingDef"):
        if d.findtext("defName") == "RM_TwistingThornwood":
            return d
    return None


# ---- 1. the design's facts about the source -------------------------------------------------------
doc = read(DOC)
for needle in ("RM_TwistingThornwood", "RM_AssayFlecks", "RM_AssayFlecksExtension", "trunkDepositsEnabled",
               "CAULDRON_TRUNK_DEPOSITS_BUILD_SWEAT_SHOWS", "CAULDRON_FLECKS_FIX_NUGGETS_IN_MIDAIR"):
    check("doc names " + needle, needle in doc)

d = tree_def()
check("RM_TwistingThornwood def exists", d is not None)
if d is not None:
    gd = d.find("graphicData")
    check("tree graphic is Graphic_Random", gd.findtext("graphicClass") == "Graphic_Random", gd.findtext("graphicClass"))
    folder = os.path.join(TEX, gd.findtext("texPath").split("Things/Plant/", 1)[1])
    pngs = sorted(f for f in os.listdir(folder) if f.lower().endswith(".png"))
    check("tree has exactly one texture (overlay can be painted to its silhouette)", pngs == ["TwistingThornwood_a.png"], pngs)
    ext = d.find("modExtensions/li[@Class='RimMandrake.Cauldron.RM_AssayFlecksExtension']")
    check("tree carries RM_AssayFlecksExtension", ext is not None)
    check("tree is single-mesh (print replay valid)", d.findtext("plant/maxMeshCount") in (None, "1"))
    comp = d.find("comps/li[@Class='RimMandrake.Cauldron.RM_CompProperties_MetalYield']")
    check("tree carries the metal-yield comp the flecks read", comp is not None)

vis = read(os.path.join(HERE, "Source/RM_CauldronDewfallVisuals.cs"))
check("RM_AssayFlecks postfixes Plant.Print", "nameof(Plant.Print)" in vis and "Postfix_Print" in vis)
check("flecks are gated on the assay grade", "GradeFraction()" in vis)
mod = read(os.path.join(HERE, "Source/RM_CauldronMod.cs"))
for s in ("assayFlecksEnabled", "RemeshAllMaps"):
    check("settings carry " + s, s in mod)
kern = read(os.path.join(HERE, "Source/Kernel/RM_YieldKernel.cs"))
check("kernel holds FleckBand (DepositTier goes beside it)", "FleckBand(" in kern)

# ---- 2. the instrument, and its sanity probe ------------------------------------------------------
tree_d = alpha_mask(TREE_PNG, DILATE_PX)
check("probe: tree vs itself is 100% inside", inside_share(alpha_mask(TREE_PNG), tree_d) == 1.0)
full = np.ones_like(tree_d)
probe = inside_share(full, tree_d)
check("probe: a full-canvas overlay reads far below the bar", probe < 0.6, probe)

# ---- 3. the overlays on disk ----------------------------------------------------------------------
tree_px = alpha_mask(TREE_PNG)
for name in ("Flecks_Light", "Flecks_Heavy"):
    p = os.path.join(TEX, "RM_AssayFlecks", name + ".png")
    share = inside_share(alpha_mask(p), tree_d)
    item_open = os.path.exists(os.path.join(REPO, "infrastructure/state/items/CAULDRON_FLECKS_FIX_NUGGETS_IN_MIDAIR.md"))
    if item_open:
        check("%s pre-fix art measured off-trunk (%.3f inside, design says ~69%%)" % (name, share), 0.5 < share < BAR, share)
    else:
        check("%s registered to the trunk (%.3f inside >= %.2f)" % (name, share, BAR), share >= BAR, share)

dep = os.path.join(TEX, "RM_TrunkDeposits")
for name, (lo, hi) in COVERAGE.items():
    p = os.path.join(dep, name + ".png")
    if not os.path.exists(p):
        print("skip  %s not drawn yet (CAULDRON_TRUNK_DEPOSITS_BUILD_SWEAT_SHOWS)" % name)
        continue
    ov = alpha_mask(p)
    share = inside_share(ov, tree_d)
    check("%s registered (%.3f >= %.2f)" % (name, share, BAR), share >= BAR, share)
    cov = float((ov & tree_px).sum()) / float(tree_px.sum())
    check("%s covers %.3f of the tree (band %.2f-%.2f)" % (name, cov, lo, hi), lo <= cov <= hi, cov)

print("RESULT: " + ("FAIL " + ", ".join(fails) if fails else "PASS"))
sys.exit(1 if fails else 0)
