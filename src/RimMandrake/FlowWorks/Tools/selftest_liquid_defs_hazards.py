#!/usr/bin/env python3
"""selftest_liquid_defs_hazards.py -- GPT review batch B (2026-10-23). Pins, offline, in the shipped XML:
  1. LIQUID_CONVERTER_FIX_PICKS_CRUDE_FIRST: each LiquidDef's <conversions> lists higher tiers first (StepFor takes the first eligible);
  2. FILL_TERRAIN_FIX_HAZARDS_DRUNK_AS_WATER: every RM_Fill_{Oil,Poison,Blood,Chemfuel,Propane,Astrofuel}_* terrain carries
     RM_DrinkableTerrainExtension -> a row with useClass Never;  RM_DeepSand likewise (DEEP_SAND_FIX_READS_AS_FRESHWATER);
  3. NATURAL_LIQUID_FIX_PUMPS_AS_FRESH_WATER: the toxic-water row has a canalFluid."""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent
fails = []
TIER = {"Crude": 0, "Household": 1, "Industrial": 2}
EXT = "RimMandrake.FlowWorks.LiquidTypes.RM_DrinkableTerrainExtension"


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        fails.append(msg)


rows = {}
for li in ET.parse(MOD / "Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml").getroot():
    rows[li.findtext("defName")] = li
for name, li in rows.items():
    tiers = [TIER[c.findtext("tier")] for c in li.findall("conversions/li")]
    check(tiers == sorted(tiers, reverse=True), f"{name}: conversions highest tier first {tiers}")
check(rows["RM_Liquid_ToxicWater"].findtext("canalFluid") == "RM_Fluid_Poison", "toxic water has a canalFluid")
check(rows["RM_Liquid_NotDrinkable"].findtext("useClass") == "Never", "RM_Liquid_NotDrinkable is Never")


def undrinkable(t):
    for e in t.findall("modExtensions/li"):
        if e.get("Class") == EXT:
            return e.findtext("liquid") == "RM_Liquid_NotDrinkable"
    return False


n = 0
for path, pat in (("Defs/Canals/TerrainDefs/FlowWorks_PitFluidTerrain.xml", r"RM_Fill_(Oil|Poison|Blood|Chemfuel|Propane|Astrofuel)_"),
                  ("Defs/ManyWaters/TerrainDefs/RM_DeepSand.xml", r"RM_DeepSand$")):
    for t in ET.parse(MOD / path).getroot().findall("TerrainDef"):
        d = t.findtext("defName") or ""
        if re.match(pat, d):
            n += 1
            check(undrinkable(t), f"{d} is not a drink")
check(n == 25, f"covered 25 terrains (24 fill + deep sand), got {n}")
sys.exit(1 if fails else 0)
