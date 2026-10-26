#!/usr/bin/env python3
"""LIQUID_TERRAINS_FIX_DRUNK_AS_FRESHWATER -- every Water-tagged TerrainDef our mods ship must NAME the liquid a pawn
drinks there, or RM_ThirstUtility.DrinkLiquidAt's fallback (Water tag, no LiquidDef lists it) reads it as plain,
Potable FreshWater. A terrain names its liquid by (a) an RM_DrinkableTerrainExtension <liquid>, or (b) being a
terrainSuite shallow/deep/chestDeep of some LiquidDef. Fresh by design (the fallback IS the answer) is the explicit
FRESH_BY_DESIGN list below; adding a terrain there is a claim that drinking it as fresh water is right.

    python3 src/RimMandrake/FlowWorks/Tools/selftest_water_terrains_name_liquid.py
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # src/RimMandrake
FRESH_BY_DESIGN = re.compile(r"^RM_Fill_Water_(Trace|Half|Brim|Superdeep)$")
FRESH_BY_DESIGN_NAMES = {"RM_WaterChestDeepStill", "RM_WaterThin", "RM_WaterVeryShallow"}  # pond stages
VANILLA_WATER_PARENTS = re.compile(r"^(Water|River|Lake|Ocean)")
PARENTS = {}  # Name -> TerrainDef element, abstract or not


def load():
    terrains, suite, patched = {}, set(), set()
    for f in ROOT.glob("*/Defs/**/*.xml"):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for d in root:
            if d.tag == "TerrainDef" or d.tag.endswith(".TerrainDef"):
                name = (d.findtext("defName") or "").strip()
                if name:
                    terrains[name] = d
                if d.get("Name"):  # abstract parents carry no defName; ParentName resolves against Name
                    PARENTS[d.get("Name")] = d
            elif d.tag.endswith("LiquidDef"):
                for k in ("shallow", "deep", "chestDeep"):
                    v = (d.findtext(f"terrainSuite/{k}") or "").strip()
                    if v:
                        suite.add(v)
    # a patch may add the extension (foreign mods that do not depend on FlowWorks)
    for f in ROOT.glob("*/Patches/**/*.xml"):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for op in root.iter("match"):
            x = op.findtext("xpath") or ""
            m = re.search(r'TerrainDef\[defName="([^"]+)"\]', x)
            if m and "RM_DrinkableTerrainExtension" in ET.tostring(op, encoding="unicode") \
                    and (op.findtext(".//liquid") or "").strip():
                patched.add(m.group(1))
    return terrains, suite | patched


def is_water(d, terrains, depth=0):
    # a child's <tags> list MERGES with its parent's (RimWorld list inheritance) unless Inherit="False", so a
    # terrain with tags of its own under WaterShallowBase is still Water: keep climbing
    tags = d.find("tags")
    if tags is not None:
        if any((li.text or "").strip() == "Water" for li in tags):
            return True
        if (tags.get("Inherit") or "").strip().lower() == "false":
            return False
    parent = d.get("ParentName")
    if not parent or depth > 10:
        return False
    pd = PARENTS.get(parent)
    if pd is not None:
        return is_water(pd, terrains, depth + 1)
    return bool(VANILLA_WATER_PARENTS.match(parent))


def names_liquid(d, terrains, depth=0):
    for li in d.findall("modExtensions/li"):
        if li.get("Class", "").endswith("RM_DrinkableTerrainExtension") and (li.findtext("liquid") or "").strip():
            return True
    return False


def main():
    terrains, suite = load()
    water = [n for n, d in terrains.items() if is_water(d, terrains)]
    bad = [n for n in sorted(water)
           if n not in suite and not names_liquid(terrains[n], terrains)
           and not FRESH_BY_DESIGN.match(n) and n not in FRESH_BY_DESIGN_NAMES]
    # sanity probe: the instrument must see the known cases
    assert len(water) > 60, f"instrument blind: only {len(water)} Water terrains found"
    assert "RM_Fill_Tar_Brim" in water and "RM_AmmoniaShallow" in water, "probe terrains not seen"
    # inherited-tag probe: RM_Water_Rust lists only WaterFresh* tags and gets Water from WaterShallowBase
    assert "RM_Water_Rust" in water, "instrument blind to Water tags inherited through a child's own <tags>"
    if bad:
        print(f"FAIL {len(bad)} Water-tagged terrain(s) name no liquid (drunk as Potable FreshWater):")
        for n in bad:
            print("  ", n)
        return 1
    print(f"PASS {len(water)} Water-tagged terrains all name a liquid or are fresh by design")
    return 0


if __name__ == "__main__":
    sys.exit(main())
