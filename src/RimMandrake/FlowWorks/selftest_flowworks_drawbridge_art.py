"""DRAWBRIDGE_LOOKS_WIRE_PICTURES_IN_WINGS: every drawbridge picture the code can ask for resolves to an installed PNG
(no magenta, no silent stand-in) for every material x look, through the same candidate order the game uses
(Source/RM_DrawbridgeMath.cs DrawbridgeArtPaths: the material's picture, else the look's;
DRAWBRIDGE_LOOKS_FIX_HIS_PICKS_OUTRANK, owner by card 2026-10-22 "Material picks win"). Multi pictures need their
facing files: winch _south/_east/_north, gate _south/_east (north reuses south). Also: every Drawbridge/ texPath a def
names exists, and the laid raid plank's two pieces exist.

Nothing is owed now: the shut Timber gate and the Scrapper shut gate were installed 2026-10-22 (owner card, drafts A-D). A newly missing picture FAILS.

Pair honesty: the candidate formulas below are mirrored from the C#; each C# formula string is checked to be present.

Can-fail: --canfail points the Textures root at an empty folder and must FAIL.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_drawbridge_art.py [--canfail]
"""
from __future__ import annotations

import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "Textures")
MATH = os.path.join(HERE, "Source", "RM_DrawbridgeMath.cs")
DEFS = os.path.join(HERE, "Defs", "Pits", "ThingDefs", "RM_Drawbridge.xml")
DIR = "Things/Building/FlowWorks/Drawbridge/"
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
MATS = ["Timber", "Steel"]
VIEWS = ["Face", "Underside", "Edge"]

# (part, material, look) that resolve to NO picture today; the stand-in draws. Owed art, not a code gap.
OWED: set = set()

# the C# formulas this file mirrors (whitespace-collapsed source must contain each)
CS_FORMULAS = [
    'Dir + "RM_DrawbridgeLeafUp_" + view + "_" + look, Dir + "RM_DrawbridgeLeafUp_" + Material(t) + "_" + view',
    'Dir + "RM_DrawbridgePlanks_" + look, Dir + "RM_DrawbridgePlanks_" + Material(t)',
    'Dir + "RM_DrawbridgeWinch_" + Material(t) + "_" + look, Dir + "RM_DrawbridgeWinch_" + Material(t)',
    'Dir + "RM_DrawbridgeGate_" + state + "_" + look, Dir + "RM_DrawbridgeGate_" + Material(t) + "_" + state',
    'return look == null ? new[] { materialPath } : new[] { materialPath, lookPath };',
    'public const string RaidPlankLaid = Dir + "RM_RaidPlank_Laid";',
    'public const string RaidPlankLaidEnd = Dir + "RM_RaidPlank_LaidEnd";',
]


def cands(look, look_path, mat_path):
    return [mat_path] if look is None else [mat_path, look_path]


def parts(m, look):
    """(part, candidate base paths, facing suffixes every candidate must have to count)."""
    out = []
    for v in VIEWS:
        out.append(("LeafUp_" + v, cands(look, DIR + "RM_DrawbridgeLeafUp_" + v + "_" + str(look), DIR + "RM_DrawbridgeLeafUp_" + m + "_" + v), [""]))
    out.append(("Planks", cands(look, DIR + "RM_DrawbridgePlanks_" + str(look), DIR + "RM_DrawbridgePlanks_" + m), [""]))
    out.append(("Winch", cands(look, DIR + "RM_DrawbridgeWinch_" + m + "_" + str(look), DIR + "RM_DrawbridgeWinch_" + m), ["_south", "_east", "_north"]))
    for state in ("Closed", "Open"):
        out.append(("Gate" + state, cands(look, DIR + "RM_DrawbridgeGate_" + state + "_" + str(look), DIR + "RM_DrawbridgeGate_" + m + "_" + state), ["_south", "_east"]))
    return out


def exists(tex, path):
    return os.path.isfile(os.path.join(tex, path + ".png"))


def run(tex):
    fails, lines, fallbacks = [], [], 0
    src = re.sub(r"\s+", " ", open(MATH, encoding="utf-8").read())
    for f in CS_FORMULAS:
        if f not in src:
            fails.append("C# formula drifted from this mirror: " + f)
    for m in MATS:
        for look in [None] + LOOKS:
            for part, cs, facings in parts(m, look):
                hit = None
                for c in cs:
                    # a candidate counts only with every facing; the game checks the facing it draws, so a half set is a defect too
                    have = [exists(tex, c + f) for f in facings]
                    if any(have) and not all(have):
                        fails.append("%s: half a facing set (%s)" % (c, [f for f, h in zip(facings, have) if not h]))
                    if all(have):
                        hit = c
                        break
                key = (part, m, look)
                if hit is None and key not in OWED:
                    fails.append("no picture for %s %s %s (candidates %s)" % (part, m, look, cs))
                elif hit is not None and key in OWED:
                    fails.append("OWED picture now installed, drop it from OWED: %s -> %s" % (key, hit))
                elif hit is not None and hit != cs[0]:
                    fallbacks += 1
                    lines.append("  fallback %-14s %-6s %-10s -> %s" % (part, m, look, hit.split("/")[-1]))
    for p in ("RM_RaidPlank_Laid", "RM_RaidPlank_LaidEnd", "RM_RaidPlank"):
        if not exists(tex, DIR + p):
            fails.append("raid plank picture missing: " + p)
    xml = open(DEFS, encoding="utf-8").read()
    for tp in re.findall(r"<texPath>(Things/Building/FlowWorks/Drawbridge/[^<]+)</texPath>", xml):
        if not exists(tex, tp):
            fails.append("def texPath not installed (would load magenta): " + tp)
    return fails, lines, fallbacks


def main():
    if "--canfail" in sys.argv:
        with tempfile.TemporaryDirectory() as empty:
            fails, _, _ = run(empty)
        if not fails:
            print("CANFAIL BROKEN: an empty Textures root passed")
            return 1
        print("canfail ok: empty Textures root -> %d failures" % len(fails))
        return 0
    fails, lines, fallbacks = run(TEX)
    for l in lines:
        print(l)
    for k in sorted(OWED, key=str):
        print("  owed (stand-in draws): %s %s %s" % k)
    if fails:
        for f in fails:
            print("FAIL", f)
        return 1
    print("ok: drawbridge art resolves for 2 materials x 5 looks (incl. none); %d fall back to the look picture; %d owed" % (fallbacks, len(OWED)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
