#!/usr/bin/env python3
"""selftest_water_not_food.py -- WATER_NUTRITION_JUDGE_DRINKING_DINNER, owner by card 2026-10-15 ("Water isn't food").

Drinking any FlowWorks water -- toxic and salt included -- quenches only and never fills the food bar. Pins, offline:
  1. every drinkable container ThingDef FlowWorks ships (an <ingestible> beside RM_BottledLiquidExtension or DBH's
     WaterExt, any Defs file) has Nutrition 0 or none, and preferability NeverForNutrition (vanilla's ConfigErrors pairs
     the two: Nutrition 0 with any other preferability is a load error);
  2. RM_LiquidBottles.xml is exactly what generate_liquid_suite.build_bottle_thingdefs writes (edit the table, never the XML);
  3. can-fail: the pre-ruling block (Nutrition 0.05, DesperateOnlyForHumanlikes) is reported.
"""
import importlib.util
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOD = HERE.parent
WATER_EXT = ("RimMandrake.FlowWorks.LiquidTypes.RM_BottledLiquidExtension", "DubsBadHygiene.WaterExt")
fails = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        fails.append(msg)


def food_waters(path):
    """[(defName, nutrition text, preferability)] for each water container in `path` that still counts as food."""
    bad = []
    for td in ET.parse(path).getroot().iter("ThingDef"):
        ing = td.find("ingestible")
        exts = [li.get("Class") for li in td.findall("modExtensions/li")]
        if ing is None or not any(e in WATER_EXT for e in exts):
            continue
        nut = td.findtext("statBases/Nutrition")
        pref = ing.findtext("preferability")
        if (nut is not None and float(nut) != 0.0) or pref != "NeverForNutrition":
            bad.append((td.findtext("defName"), nut, pref))
    return bad


spec = importlib.util.spec_from_file_location("gls", HERE / "generate_liquid_suite.py")
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)

# 1 shipped defs
files = sorted((MOD / "Defs").rglob("*.xml"))
seen = 0
for f in files:
    txt = f.read_text(encoding="utf-8")
    if "<ingestible>" not in txt or not any(e in txt for e in WATER_EXT):
        continue
    seen += 1
    bad = food_waters(f)
    check(not bad, "%s: no water container is food %s" % (f.relative_to(MOD), bad[:4]))
# THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY: the coloured-water bottles are generated now (RM_Bottle_<Colour>Water), in the same file
check(seen >= 1, "the scan saw the generated bottles (%d files)" % seen)
gen_txt = (MOD / "Defs" / "LiquidTypes" / "ThingDefs" / "RM_LiquidBottles.xml").read_text(encoding="utf-8")
check("<defName>RM_Bottle_RustWater</defName>" in gen_txt, "the scan covers the coloured-water bottles (RM_Bottle_RustWater generated)")

# 2 generated file current
shipped = MOD / "Defs" / "LiquidTypes" / "ThingDefs" / "RM_LiquidBottles.xml"
with tempfile.TemporaryDirectory() as td:
    out, _ = G.build_bottle_thingdefs(Path(td))
    check(Path(out).read_bytes() == shipped.read_bytes(), "RM_LiquidBottles.xml matches the generator byte-for-byte")

# 3 can-fail
planted = """<Defs><ThingDef><defName>RM_Bottle_ToxicWater</defName>
<modExtensions><li Class="RimMandrake.FlowWorks.LiquidTypes.RM_BottledLiquidExtension"><liquid>x</liquid></li></modExtensions>
<statBases><Nutrition>0.05</Nutrition></statBases>
<ingestible><foodType>Fluid</foodType><preferability>DesperateOnlyForHumanlikes</preferability></ingestible></ThingDef></Defs>"""
with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False, encoding="utf-8") as fh:
    fh.write(planted)
check(food_waters(fh.name) == [("RM_Bottle_ToxicWater", "0.05", "DesperateOnlyForHumanlikes")],
      "can-fail: the pre-ruling toxic-water bottle (Nutrition 0.05) is reported as food")
Path(fh.name).unlink()

print("selftest_water_not_food: %s" % ("FAIL" if fails else "PASS"))
sys.exit(1 if fails else 0)
