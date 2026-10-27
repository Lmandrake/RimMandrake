#!/usr/bin/env python3
"""Offline selftest (ROAST_STICK_FIX_DISABLED_COOK_STAT_ERRORS): the roast-on-a-stick recipes are open to
Cooking-incapable pawns (BasicWorker bill), so they must not depend on Cooking: workSpeedStat/efficiencyStat
may not be CookSpeed and workSkill may not be Cooking, else vanilla logs 'disabled stat' ErrorOnce.
1. Every RSW_CookRoastOnAStick* RecipeDef in the Cuisine mod is checked. 2. Instrument can see: >= 2 recipes found
and each has requiredGiverWorkType BasicWorker."""
import glob, os, sys
import xml.etree.ElementTree as ET
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
fails, n = [], 0
for f in glob.glob(os.path.join(REPO, "src/RimStarWars/Cuisine/Defs/*.xml")):
    for r in ET.parse(f).getroot().iter("RecipeDef"):
        name = (r.findtext("defName") or "")
        if not name.startswith("RSW_CookRoastOnAStick"):
            continue
        n += 1
        if r.findtext("requiredGiverWorkType") != "BasicWorker":
            fails.append(name + ": not BasicWorker")
        for tag in ("workSpeedStat", "efficiencyStat"):
            if r.findtext(tag) == "CookSpeed":
                fails.append("%s: %s is CookSpeed" % (name, tag))
        if r.findtext("workSkill") == "Cooking":
            fails.append(name + ": workSkill is Cooking")
if n < 2:
    fails.append("instrument blind: found %d roast recipes" % n)
for m in fails:
    print("FAIL", m)
print("OK" if not fails else "RED", n, "recipes")
sys.exit(1 if fails else 0)
