#!/usr/bin/env python3
"""The 16 stray roster rows of REGEN_GAPS_DECIDE_STRAYS_AND_FLYERS stay cut from every biome of ours.

Owner, by card 2026-10-19: "Sixteen roster rows cast donor defs we have no def of: what happens? -> Cut them from
their biome sheets" (and "Cut them as the card said" for the eight vanilla/DLC rows). Enacted in 8e87a9649 and
03ac7f26a; five were already gone (RM_Cauldron casts our RM_Visceral port; LeaningScrub's RG_Plant_* repointed in
460a7fe81). This test keeps them cut: no BiomeDef under src/ and no PatchOperation whose xpath reaches a roster
casts any of these defNames as a roster ROW (an XML element under wildAnimals / wildPlants or any *WildAnimals /
*WildPlants list). Comments, label patches, tolerances and non-roster lists are not rows and are not checked.

The item's other half, the 21 flight flip-book frame sets, is not this test's to prove: it waits for a joint
session with the owner and is carried by FLYER_STABLE_BODY_GATE_1 and its FLYER_TIER_* splits. The test asserts
those items are still live, so the half can never be dropped silently.

Sanity probe: the parser must see at least 20 of our BiomeDefs and 500 roster rows, and must find a known row
(RM_Abyss casts RSW_Taozin through WildAnimals_Abyss.xml), or it is reading nothing.
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

EXACT = {"Visceral", "LavaSnail", "Plant_Fireweed", "Plant_Ambrosia", "Plant_GrayGrass", "Plant_Toxipotato",
         "Plant_TreePolux", "Plant_Brambles", "Plant_MagmaCactus"}
PREFIXES = ("IronScruff_", "RG_Plant_")
FLYER_ITEMS = ("FLYER_STABLE_BODY_GATE_1",)
FLYER_GLOB = "FLYER_TIER_*.md"


def is_roster_tag(tag):
    t = tag.lower()
    return t.endswith("wildanimals") or t.endswith("wildplants")


def is_stray(name):
    return name in EXACT or name.startswith(PREFIXES)


def rows_under(el):
    return [c.tag for c in el if isinstance(c.tag, str) and c.tag != "li"]


def main():
    bad, biomes, rows, probe = [], 0, 0, False
    for p in sorted(glob.glob(os.path.join(ROOT, "src", "**", "*.xml"), recursive=True)):
        rel = os.path.relpath(p, ROOT)
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue  # unparseable XML is other lints' business
        for b in root.iter("BiomeDef"):
            biomes += 1
            name = b.findtext("defName") or "?"
            for el in b:
                if isinstance(el.tag, str) and is_roster_tag(el.tag):
                    for r in rows_under(el):
                        rows += 1
                        if is_stray(r):
                            bad.append("%s: BiomeDef %s %s casts %s" % (rel, name, el.tag, r))
        for op in root.iter():
            xp = op.find("xpath")
            val = op.find("value")
            if xp is None or val is None or not xp.text:
                continue
            last = re.split(r"/", xp.text.strip())[-1]
            if is_roster_tag(re.sub(r"\[.*\]$", "", last)):
                for r in rows_under(val):
                    rows += 1
                    if r == "RSW_Taozin" and "RM_Abyss" in xp.text:
                        probe = True
                    if is_stray(r):
                        bad.append("%s: patch onto %s casts %s" % (rel, xp.text.strip(), r))
    items = os.path.join(ROOT, "infrastructure", "state", "items")
    live = [i for i in FLYER_ITEMS if os.path.exists(os.path.join(items, i + ".md"))]
    tiers = glob.glob(os.path.join(items, FLYER_GLOB))
    if biomes < 20 or rows < 500 or not probe:
        print("FAIL sanity: biomes=%d rows=%d taozin_probe=%s (the parser is blind)" % (biomes, rows, probe))
        return 1
    if not live and not tiers:
        bad.append("flyer flip-book half has no live carrier: neither %s nor %s in %s"
                   % (FLYER_ITEMS, FLYER_GLOB, os.path.relpath(items, ROOT)))
    for b in bad:
        print("FAIL", b)
    if bad:
        return 1
    print("PASS regen strays cut: biomes=%d roster_rows=%d strays=0; flyer half carried by %d live item(s)"
          % (biomes, rows, len(live) + len(tiers)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
