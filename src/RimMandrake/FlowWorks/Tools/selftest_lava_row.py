#!/usr/bin/env python3
"""selftest_lava_row.py -- LAVA_LIQUID_BUILD_PROMISED_BY_CARD: the lava LiquidDef row exists with the matrix's faces.

Pins, offline (design/RimMandrake/flowworks_liquid_matrix.md, row "Lava"; card 2026-09-24 "Promote lava now"):
  1. the shipped registry carries RM_Liquid_Lava, Odyssey-guarded, adopting LavaShallow/LavaDeep;
  2. the Forge actually paints that terrain (its BiomeDef names LavaDeep), so the row describes the Forge's lava;
  3. the faces the matrix rules NO stay absent: no canalFluid (ground pump NO), no bottled form, no worldTag
     (ocean NO), no weather (rain NO), and not `hot` (RM_LiquidHeat would add heat to every lava cell);
  4. the pumping-station ruin site excludes lava by name, and the validator's C# carries that field and skips it;
  5. a mutated registry without the row turns check 1 red (the check can fail).
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOD = HERE.parent
SRC = MOD.parent
REG = MOD / "Defs" / "LiquidTypes" / "LiquidDefs" / "RM_LiquidDefRegistry.xml"
TAG = "RimMandrake.FlowWorks.LiquidTypes.LiquidDef"
fails = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


def lava_of(root):
    for d in root.iter(TAG):
        if d.findtext("defName") == "RM_Liquid_Lava":
            return d
    return None


root = ET.parse(REG).getroot()
rows = [d.findtext("defName") for d in root.iter(TAG)]
check(len(rows) >= 15 and "RM_Liquid_Tar" in rows, "sanity: registry parsed (%d rows, tar present)" % len(rows))
lava = lava_of(root)
check(lava is not None, "1 RM_Liquid_Lava is in the shipped registry")
if lava is not None:
    check(lava.get("MayRequire") == "Ludeon.RimWorld.Odyssey", "1 the row is Odyssey-guarded")
    check(lava.findtext("terrainSuite/shallow") == "LavaShallow" and lava.findtext("terrainSuite/deep") == "LavaDeep",
          "1 terrainSuite adopts LavaShallow/LavaDeep")
    for absent in ("canalFluid", "bottled", "worldTag", "weather", "hot", "surfaceLook"):
        check(lava.find(absent) is None, "3 no <%s> on the lava row" % absent)

forge = (SRC / "TheForge" / "Defs" / "BiomeDefs" / "RM_TheForge_Biome.xml").read_text(encoding="utf-8")
check("<terrain>LavaDeep</terrain>" in forge, "2 the Forge paints LavaDeep")

scatter = (MOD / "Defs" / "Machinery" / "RM_LiquidWorksScatter.xml").read_text(encoding="utf-8")
m = re.search(r"<defName>RM_PumpingStation_RuinScatter</defName>(.*?)</GenStepDef>", scatter, re.S)
check(m is not None, "sanity: pumping-station scatter found")
if m:
    check(re.search(r"<excludeLiquids>\s*<li[^>]*>RM_Liquid_Lava</li>", m.group(1)) is not None,
          "4 the pumping-station ruin excludes RM_Liquid_Lava")
cs = (MOD / "Source" / "Machinery" / "RM_LiquidWorksRuins.cs").read_text(encoding="utf-8")
check("public List<LiquidDef> excludeLiquids" in cs and "excludeLiquids.Contains(l)" in cs,
      "4 RM_ScattererValidator_NearLiquid declares excludeLiquids and skips it in Matches")

mutated = ET.fromstring(REG.read_text(encoding="utf-8").replace("RM_Liquid_Lava", "RM_Liquid_NotLava").encode())
check(lava_of(mutated) is None, "5 a registry without the row reads as missing (the check can fail)")

print("%d FAIL" % len(fails) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
