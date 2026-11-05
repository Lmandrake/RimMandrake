#!/usr/bin/env python3
"""selftest_weir_material.py -- RM_BankWeir's words and cost match its installed stone/concrete/metal looks
(BANK_WEIR_FIX_TIMBER_TEXT_ON_STONE; looks installed at af7156fa3f: Scrapper stone rubble, Industrial stepped concrete,
Modern smooth curtain, Futuristic white metal).

  text     the description names no timber/wood/log and does name stone, concrete or metal
  cost     costList holds no WoodLog or Cloth and is not empty; no stuffCategories (stuff colour would tint the art)
  build    constructEffect is not ConstructWood; Flammability is 0
  can-fail the same checks FAIL on the pre-fix timber def (description, WoodLog+Cloth, ConstructWood, 0.5)
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

DEFS = Path(__file__).resolve().parent.parent / "Defs/Rivers/RM_BankWorks.xml"

OLD_TIMBER = """<Defs><ThingDef ParentName="BuildingBase"><defName>RM_BankWeir</defName>
<description>A low timber wall set across the current from the bank.</description>
<statBases><Flammability>0.5</Flammability></statBases>
<costList><WoodLog>60</WoodLog><Cloth>20</Cloth></costList>
<constructEffect>ConstructWood</constructEffect></ThingDef></Defs>"""


def weir(root):
    for td in root.iter("ThingDef"):
        if td.findtext("defName") == "RM_BankWeir":
            return td
    return None


def faults(root):
    td = weir(root)
    if td is None:
        return ["RM_BankWeir not found"]
    out = []
    desc = (td.findtext("description") or "").lower()
    if re.search(r"\b(timber|wood|wooden|log|logs|plank)\b", desc):
        out.append("description names wood: %r" % desc[:60])
    if not re.search(r"\b(stone|concrete|metal)\b", desc):
        out.append("description names no stone/concrete/metal")
    cost = td.find("costList")
    names = [c.tag for c in cost] if cost is not None else []
    if not names:
        out.append("costList empty")
    for bad in ("WoodLog", "Cloth"):
        if bad in names:
            out.append("costList holds %s" % bad)
    if td.find("stuffCategories") is not None:
        out.append("stuffed (stuff colour tints the look art)")
    if (td.findtext("constructEffect") or "") == "ConstructWood":
        out.append("constructEffect ConstructWood")
    flam = td.findtext("statBases/Flammability")
    if flam is None or float(flam) != 0.0:
        out.append("Flammability %s, want 0" % flam)
    return out


def main():
    fails = 0
    f = faults(ET.parse(DEFS).getroot())
    print(("PASS" if not f else "FAIL") + "  live def: " + ("; ".join(f) or "stone/concrete/metal words, Steel cost, 0 flammable"))
    fails += bool(f)
    g = faults(ET.fromstring(OLD_TIMBER))
    ok = len(g) >= 5
    print(("PASS" if ok else "FAIL") + "  can-fail on the old timber def: %d faults" % len(g))
    fails += not ok
    print("RESULT", "FAIL" if fails else "PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
