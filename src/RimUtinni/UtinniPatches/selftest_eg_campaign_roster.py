#!/usr/bin/env python3
"""selftest_eg_campaign_roster.py -- EGROSTER_DEAD_ROWS_PRUNE_SILENT_SKIPS, L0.

RM_ExplosiveGrowthRosterDef skips a row whose plant no loaded def has, silently. The campaign roster
(Defs/ExplosiveGrowth/RUT_ExplosiveGrowthRoster.xml) carried six such dead rows (renamed or never-ported plants).

Rows:
  1. every <plants><li><plant> with our prefix (RM_/RUT_/RSW_) names a ThingDef some src/**/Defs folder defines
     (bare donor names, Plant_*_Wild, are allowed absent: the roster lists both spellings on purpose);
  2. instrument: the def index is read with an XML parser, so a comment between <ThingDef> and <defName> does not
     hide a def; it must see the four SWBestiary RSW_Plant_*_Wild the roster keeps (each has such a comment or
     lives in a port subfolder) and more than 1000 ThingDefs;
  3. planted break: a copy of the roster with RUT_Placeholder_GreentideGiantTree put back must redden row 1.

Run bare: python3 src/RimUtinni/UtinniPatches/selftest_eg_campaign_roster.py   (exit 0 = clean)
"""
import glob
import os
import sys

from lxml import etree as E

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(HERE))
ROSTER = os.path.join(HERE, "Defs", "ExplosiveGrowth", "RUT_ExplosiveGrowthRoster.xml")
PREFIX = ("RM_", "RUT_", "RSW_")
KEPT = ("RSW_Plant_HubbaGourd_Wild", "RSW_Plant_Chakroot_Wild", "RSW_Plant_HydenockTree_Wild", "RSW_Plant_JoganTree_Wild")
FAILS = []
PARSER = E.XMLParser(remove_comments=True, recover=True)


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def thingdefs():
    """Every ThingDef defName under any src/<Tier>/<Mod>/**/Defs/**/*.xml, parsed (comments dropped)."""
    names = set()
    for p in glob.glob(os.path.join(SRC, "**", "Defs", "**", "*.xml"), recursive=True):
        try:
            root = E.parse(p, PARSER).getroot()
        except (E.XMLSyntaxError, OSError):
            continue
        if root is None:
            continue
        for d in root:
            if isinstance(d.tag, str) and d.tag.split(".")[-1] == "ThingDef":
                dn = d.findtext("defName")
                if dn:
                    names.add(dn.strip())
    return names


def dead_rows(roster_root, known):
    out = []
    for li in roster_root.iter("li"):
        plant = li.findtext("plant")
        if plant is None or li.getparent() is None or li.getparent().tag != "plants":
            continue
        plant = plant.strip()
        if plant.startswith(PREFIX) and plant not in known:
            out.append(plant)
    return out


def main():
    known = thingdefs()
    check("instrument: def index sees the four kept SWBestiary RSW_Plant_*_Wild", all(k in known for k in KEPT),
          "missing " + ", ".join(k for k in KEPT if k not in known))
    check("instrument: def index holds > 1000 ThingDefs", len(known) > 1000, "saw %d" % len(known))
    root = E.parse(ROSTER, PARSER).getroot()
    n_rows = sum(1 for li in root.iter("li") if li.findtext("plant") is not None)
    check("instrument: roster rows read (>= 15)", n_rows >= 15, "saw %d" % n_rows)
    dead = dead_rows(root, known)
    check("every prefixed campaign roster plant is a defined ThingDef", not dead, "dead rows: " + ", ".join(dead))

    broken = E.parse(ROSTER, PARSER).getroot()
    plants = broken.find(".//plants")
    plants.append(E.fromstring("<li><plant>RUT_Placeholder_GreentideGiantTree</plant><top>None</top></li>"))
    check("break caught: the deleted placeholder row put back", "RUT_Placeholder_GreentideGiantTree" in dead_rows(broken, known),
          "stayed clean")
    print("RESULT", "FAIL %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
