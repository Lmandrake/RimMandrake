#!/usr/bin/env python3
"""Pins for the Cauldron trunk-deposits design
(design/Jawa/worldbuilding/biomes/cauldron_trunk_deposits_design_2026-11-02.md,
item CAULDRON_TRUNK_DEPOSITS_DESIGN_CRYSTAL_FANS).

1. Every source fact the design states about today's tree is still true (def, single texture, the flecks
   extension and its class, the print postfix, the settings it names). 1b: EVERY backticked citation in the
   doc resolves (def, class, member, path, skill, item, engine API, the cut def absent) or is declared a
   proposal; an unclassified citation fails. Mutant sweep: mutants_cauldron_trunk_deposits.sh.
2. The registration instrument of the design's section 5: share of an overlay's opaque pixels inside the
   tree's dilated silhouette. Sanity probe: the tree measured against itself is 100 % inside, and a
   blank-canvas overlay with every pixel opaque is far from it, so the instrument can see a miss.
3. While the fleck art is the pre-fix art (CAULDRON_FLECKS_FIX_NUGGETS_IN_MIDAIR open), it measures below
   the 95 % bar; once redrawn it must pass. Any deposit overlay on disk must pass the bar and its coverage
   band.

    python3 src/RimMandrake/Cauldron/selftest_cauldron_trunk_deposits.py
"""
import hashlib
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

# ---- 1b. EVERY backticked citation in the doc resolves -------------------------------------------
# Each `token` in the doc is classified below; an unclassified token is a FAIL, so a new citation cannot
# slip in unproven. EXISTING tokens are resolved against the tree; PROPOSED tokens are what the build item
# adds (they may or may not exist yet); ENGINE tokens must be used by some C# in src (the API exists).
import glob
import json
import re

BIOMES = os.path.join(REPO, "design/Jawa/worldbuilding/biomes")
SRC = os.path.join(REPO, "src")
CS = {p: read(p) for p in glob.glob(os.path.join(HERE, "Source", "**", "*.cs"), recursive=True)}
ALL_CS = None


def thingdef_names():
    names = set()
    for p in glob.glob(os.path.join(HERE, "Defs", "**", "*.xml"), recursive=True):
        for el in ET.parse(p).getroot().iter("ThingDef"):
            if el.findtext("defName"):
                names.add(el.findtext("defName"))
    return names


TDEFS = thingdef_names()


def has_def(name):
    return name in TDEFS


def has_class(name):
    return any(re.search(r"\bclass\s+%s\b" % re.escape(name), t) for t in CS.values())


def has_member(cls, member):
    # the member is declared (not merely called) in the file that declares the class
    pat = re.compile(r"\b(?:static\s+|private\s+|public\s+|internal\s+|const\s+|readonly\s+)+[\w<>\[\].]+\s+%s\b"
                     % re.escape(member))
    for t in CS.values():
        if re.search(r"\bclass\s+%s\b" % re.escape(cls), t) and pat.search(t):
            return True
    return False


def any_cs_uses(needle):
    global ALL_CS
    if ALL_CS is None:
        ALL_CS = [read(p) for p in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True)]
    pat = re.compile(re.escape(needle) + (r"\b" if needle[-1].isalnum() else ""))
    return any(pat.search(t) for t in ALL_CS)


def path_under(*bases):
    return lambda tok: any(os.path.exists(os.path.join(b, tok)) for b in bases)


def item_filed(tok):
    st = os.path.join(REPO, "infrastructure/state/items")
    return os.path.exists(os.path.join(st, tok + ".md")) or os.path.exists(os.path.join(st, "closed", tok + ".md"))


def roster_keeps_thornwood(_tok):
    with open(os.path.join(BIOMES, "rosters/cauldron.json"), encoding="utf-8") as f:
        text = json.load(f)
    hits = []

    def walk(o):
        if isinstance(o, dict):
            if str(o.get("def", "")).endswith("TwistingThornwood"):
                hits.append(str(o.get("law", "")))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(text)
    return any("owner favourite, keep" in h for h in hits)


FLECKS = os.path.join(TEX, "RM_AssayFlecks")
EXISTING = {
    # defs
    "RM_TwistingThornwood": lambda t: has_def(t),
    "RM_Fexxil": lambda t: has_def(t),
    "RM_CrystalFlower": lambda t: has_def(t),
    "RM_TreeMartyr": lambda t: not has_def(t),  # the doc says it is CUT
    "Graphic_Random": lambda t: tree_def() is not None and tree_def().findtext("graphicData/graphicClass") == t,
    # classes and members
    "RM_AssayFlecks": has_class,
    "RM_AssayFlecksExtension": has_class,
    "RM_CompMetalYield.GradeFraction": lambda t: has_member("RM_CompMetalYield", "GradeFraction"),
    "RM_YieldKernel.FleckBand": lambda t: has_member("RM_YieldKernel", "FleckBand"),
    "OverlayYOffset": lambda t: has_member("RM_AssayFlecks", "OverlayYOffset"),
    "Plant.Print": lambda t: "nameof(Plant.Print)" in read(os.path.join(HERE, "Source/RM_CauldronDewfallVisuals.cs")),
    "assayFlecksEnabled": lambda t: t in mod,
    "RemeshAllMaps": lambda t: t in mod,
    # paths
    "src/RimMandrake/Cauldron": path_under(REPO),
    "src/RimMandrake/Cauldron/selftest_cauldron_trunk_deposits.py": path_under(REPO),
    "selftest_cauldron_trunk_deposits.py": path_under(HERE),
    "Source/RM_CauldronDewfallVisuals.cs": path_under(HERE),
    "Textures/Things/Plant/RM_TwistingThornwood/TwistingThornwood_a.png": path_under(HERE),
    "TwistingThornwood_a.png": path_under(os.path.join(TEX, "RM_TwistingThornwood")),
    "RM_AssayFlecks/Flecks_Light.png": path_under(TEX),
    "Flecks_Light.png": path_under(FLECKS),
    "Flecks_Heavy.png": path_under(FLECKS),
    "design/Jawa/worldbuilding/biomes/cauldron.md": path_under(REPO),
    "cauldron_enrichment_audio_visuals_spec_2026-10-02.md": path_under(BIOMES),
    "rosters/cauldron.json": lambda t: os.path.exists(os.path.join(BIOMES, t)) and roster_keeps_thornwood(t),
    # skills
    "rimworld-art-evaluation": lambda t: os.path.exists(os.path.join(REPO, "skills", t, "SKILL.md")),
    "editing-images": lambda t: os.path.exists(os.path.join(REPO, "skills", t, "SKILL.md")),
    # items
    "CAULDRON_TRUNK_DEPOSITS_DESIGN_CRYSTAL_FANS": item_filed,
    "CAULDRON_TRUNK_DEPOSITS_BUILD_SWEAT_SHOWS": item_filed,
    "CAULDRON_FLECKS_FIX_NUGGETS_IN_MIDAIR": item_filed,
}
ENGINE = {"Plant": "Plant", "DefModExtension": ": DefModExtension", "ConfigErrors": "ConfigErrors()",
          "CompTickLong": "CompTickLong()", "TickLong()": "TickLong()", "Rand.Seed": "Rand.Seed",
          "Age": ".Age", "Growth": ".Growth"}
PROPOSED = {"RM_TrunkDepositsExtension", "DepositTier", "trunkDepositsEnabled", "scabTexPath", "slagTexPath",
            "scabFromGrowth", "slagFromAgeFraction", "Deposits_Slag.png",
            "Textures/Things/Plant/RM_TrunkDeposits/Deposits_Scab.png"}
# rule text: a token whose head word is one of the above (e.g. `scabFromGrowth = 0.5`, `Growth >= 0.5`,
# `DepositTier(growth, ...)`, `Age < 0.5 × LifespanTicks`) is classified by that head word.
head = re.compile(r"^[A-Za-z_][\w.]*")
for tok in sorted(set(re.findall(r"`([^`\n]+)`", doc))):
    h = head.match(tok)
    key = tok if (tok in EXISTING or tok in ENGINE or tok in PROPOSED) else (h.group(0) if h else tok)
    if key in EXISTING:
        check("doc cite resolves: " + tok, bool(EXISTING[key](key)))
    elif key in ENGINE:
        check("doc cite is a real engine API (used in src C#): " + tok, any_cs_uses(ENGINE[key]))
    elif key in PROPOSED:
        print("prop  " + tok + "  (proposed by the design; CAULDRON_TRUNK_DEPOSITS_BUILD_SWEAT_SHOWS)")
    else:
        check("doc cite is classified in this selftest: " + tok, False, "add it to EXISTING/ENGINE/PROPOSED")

# ---- 2. the instrument, and its sanity probe ------------------------------------------------------
tree_d = alpha_mask(TREE_PNG, DILATE_PX)
check("probe: tree vs itself is 100% inside", inside_share(alpha_mask(TREE_PNG), tree_d) == 1.0)
full = np.ones_like(tree_d)
probe = inside_share(full, tree_d)
check("probe: a full-canvas overlay reads far below the bar", probe < 0.6, probe)

# ---- 3. the overlays on disk ----------------------------------------------------------------------
tree_px = alpha_mask(TREE_PNG)
# Today's fleck art is pinned by content hash, not by whether a follow-on item file exists: on this art the
# instrument must SEE the miss (~69 % inside, ~31 % off-trunk). Redrawn art (CAULDRON_FLECKS_FIX_NUGGETS_IN_MIDAIR)
# has a new hash and must clear the bar.
PRE_FIX = {"Flecks_Light": "33c18a42d36c6ab2f94a835ae8b7a5d63e61c5e9daf79f4b858dfc2970d81403",
           "Flecks_Heavy": "f8efaeae0f4fa175a0c129b898f961ac4a2a432f08f59db1cb39d6d262ba9b46"}
PRE_FIX_INSIDE = (0.65, 0.72)
for name in ("Flecks_Light", "Flecks_Heavy"):
    p = os.path.join(TEX, "RM_AssayFlecks", name + ".png")
    with open(p, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    share = inside_share(alpha_mask(p), tree_d)
    if digest == PRE_FIX[name]:
        lo, hi = PRE_FIX_INSIDE
        check("%s pre-fix art measured off-trunk (%.3f inside = %.0f%% off; design: ~69%% inside, below the %.2f bar)"
              % (name, share, 100 * (1 - share), BAR), lo <= share <= hi and share < BAR, share)
    else:
        check("%s redrawn art registered to the trunk (%.3f inside >= %.2f)" % (name, share, BAR), share >= BAR, share)

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
