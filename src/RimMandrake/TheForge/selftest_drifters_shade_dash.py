#!/usr/bin/env python3
"""Offline selftest: a vapour-column drifter is never pulled out of its pasture by the shade dash.

RIMMANDRAKE_SETTLE_BULLOO_HOMING_VERSUS_SHADE_HOP_WALKS_THROUGH_SUN (measured on ArchSmall 2026-11-27): on the Forge,
CreatureBehaviors' RM_JobGiver_SunEscape (Animal_PreMain, priority 10) and RM_JobGiver_ShadeHop pull every wild animal
into shade, and TheForge's RM_JobGiver_SkyPastureHoming (Animal_PreMain) walks a column-bound drifter back to its
vapour column, which is open sun (vapour columns cast no shade). The two fought: 3 of 3 bulloo left shade and walked
30-50 cells across the sun. Ruling taken (delegated, evidence-for-ask): the pasture wins for a column drifter, as the
firehawk and the furnace-beast already are exempt (a creature whose life is the heat). So every ThingDef that carries
CompProperties_VaporDrifter must carry RM_SunDashExtension exempt=true, and RM_ShadeHop.Eligible must honour it.

Run: python3 src/RimMandrake/TheForge/selftest_drifters_shade_dash.py   (exit 0 pass, 1 fail, 2 could not look)
"""
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
SRC = os.path.join(ROOT, "src")
DRIFTER = "RimMandrake.EnvironmentalHazards.CompProperties_VaporDrifter"
EXEMPT = "RimMandrake.CreatureBehaviors.RM_SunDashExtension"
SHADEHOP = os.path.join(SRC, "RimMandrake", "CreatureBehaviors", "Source", "RM_ShadeHop.cs")


def drifter_defs():
    """(path, defName, exempt) for every ThingDef with a vapour-drifter comp under src/."""
    out = []
    for dirpath, _, files in os.walk(SRC):
        if os.sep + "Defs" not in dirpath:
            continue
        for f in files:
            if not f.endswith(".xml"):
                continue
            p = os.path.join(dirpath, f)
            try:
                root = ET.parse(p).getroot()
            except ET.ParseError:
                continue
            for td in root.iter("ThingDef"):
                comps = td.find("comps")
                if comps is None or not any(li.get("Class") == DRIFTER for li in comps.findall("li")):
                    continue
                ext = td.find("modExtensions")
                lis = [] if ext is None else [li for li in ext.findall("li") if li.get("Class") == EXEMPT]
                exempt = any((li.findtext("exempt") or "").strip().lower() == "true" for li in lis)
                out.append((os.path.relpath(p, ROOT), td.findtext("defName"), exempt))
    return out


def main():
    fails = []
    defs = drifter_defs()
    if not defs:
        print("COULD NOT LOOK: no ThingDef with %s found under %s" % (DRIFTER, SRC))
        return 2
    for path, name, exempt in defs:
        print("%s  %s (%s) carries RM_SunDashExtension exempt" % ("ok  " if exempt else "FAIL", name, path))
        if not exempt:
            fails.append(name)
    try:
        with open(SHADEHOP, encoding="utf-8") as fh:
            src = fh.read()
    except OSError as e:
        print("COULD NOT LOOK: %s (%s)" % (SHADEHOP, e))
        return 2
    honours = "GetModExtension<RM_SunDashExtension>()" in src and "race.exempt" in src
    print("%s  RM_ShadeHop.Eligible honours RM_SunDashExtension.exempt" % ("ok  " if honours else "FAIL"))
    if not honours:
        fails.append("Eligible")
    print("%d drifter def(s); %s" % (len(defs), "PASS" if not fails else "FAIL: " + ", ".join(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
