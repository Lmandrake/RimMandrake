"""validation.py -- first script for RimMandrake: Deep Drill (mandrake.rm.deepdrill). DEEP_DRILL_HOME_BIOME_1.

THE MOD: Harmony postfix on CompDeepScanner.ChooseLumpThingDef; off a deposit's home biome (Defs/RM_DeepHomeTable.xml, generated from
design/RimMandrake/mineral_abundance_registry_2026-10-03.csv) the pick becomes steel. One setting, homeFilterEnabled.

STATIC (no game): `python3 validation.py` -> `STATIC: PASS (0 findings)`.
LIVE CHAIN (owed, needs the bridge; recorded here so the next poking session fills it in rather than inventing one):
  1. new map on a biome that is nobody's home (e.g. RUT_AridShrubland): call CompDeepScanner.ChooseLumpThingDef 200x on a scanner
     building; every result is Steel.      [UNMEASURED: no live run yet]
  2. map on RM_LanternDeeps: results include Diamond/Ruby/Sapphire/DV_Pyrinth/RM_Lanternstone over 400 picks.   [UNMEASURED]
  3. homeFilterEnabled off: step 1 returns non-steel lumps again.                                              [UNMEASURED]
  4. the Harmony census line "Harmony: patched N, missing X" in Player.log names no 'Deep deposits follow the biome' failure. [UNMEASURED]
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def static_checks():
    bad = []
    src = open(os.path.join(HERE, "Source", "RM_DeepDrillMod.cs"), encoding="utf-8").read()
    body = src.split("class RM_DeepDrillSettings", 1)[1].split("public static void Draw", 1)[0]
    fields = re.findall(r"public\s+static\s+bool\s+(\w+)\s*=", re.sub(r"//[^\n]*", "", body))
    if fields != ["homeFilterEnabled"]:
        bad.append("settings fields changed: %s" % fields)
    for n in fields:
        if '"%s"' % n not in body or n not in src.split("Draw", 1)[1]:
            bad.append("setting %s is not scribed or has no control" % n)
    proj = open(os.path.join(HERE, "Source", "RimMandrake_DeepDrill.csproj"), encoding="utf-8").read()
    for dp, _, files in os.walk(os.path.join(HERE, "Source")):
        if "SelfTest" in dp:
            continue
        for fn in files:
            if fn.endswith(".cs") and fn not in proj:
                bad.append("%s is not in the csproj" % fn)
    patch = open(os.path.join(HERE, "Source", "Patch_DeepHome.cs"), encoding="utf-8").read()
    for needle in ('[HarmonyPatch(typeof(CompDeepScanner), "ChooseLumpThingDef")]', "homeFilterEnabled", "ThingDefOf.Steel"):
        if needle not in patch:
            bad.append("Patch_DeepHome.cs lacks %s" % needle)
    t = ET.parse(os.path.join(HERE, "Defs", "RM_DeepHomeTable.xml")).getroot()
    rows = t.findall(".//rows/li")
    if len(rows) < 20:
        bad.append("table has %d rows (sanity probe: expected >= 20)" % len(rows))
    things = [r.findtext("thing") for r in rows]
    if "Steel" in things:
        bad.append("Steel must never be a table row (it is the planet-wide deep resource)")
    if len(things) != len(set(things)):
        bad.append("duplicate thing rows")
    for must in ("Gold", "RM_Lanternstone", "RM_LivePatternMetal", "Jade"):
        if must not in things:
            bad.append("table lacks %s" % must)
    return bad


if __name__ == "__main__":
    b = static_checks()
    print("STATIC: %s (%d findings)" % ("PASS" if not b else "FAIL", len(b)))
    for x in b:
        print("  -", x)
    sys.exit(1 if b else 0)
