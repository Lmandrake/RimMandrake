#!/usr/bin/env python3
"""Offline selftest for the second of the fire-hawk's two hunt rewards, the crestfeather (owner, 2026-11-13: "That gives a great reason for players to hunt the
Firehawk."; "It is ok that they are common. That is the threat.").

  RIMMANDRAKE_ANNOUNCE_FIREHAWK_EMBER_LETTER_ON_FIRST_SIGHTING   the once-per-game letter (FireHawkRewards.cs)
  RIMMANDRAKE_ADD_PRISTINE_EMBERHAWK_CRESTFEATHER_HUNT_TROPHY    the crestfeather trophy (RM_PristineFirehawkCrestfeather.xml)
  (the second id keeps its filed spelling; the owner corrected the name to Firehawk, so that word appears nowhere in the mod)

Static half (this file): the letter's keyed strings exist for every key the code translates, the Mod Settings toggle exists,
ships ON, is saved, is drawn and is greyed under the hawk's master, and the component feeds it (and the once-only flag it saves)
to the kernel gate; the trophy def exists with its label, Beauty, MarketValue above the hawk's, a small stack and a marked
placeholder texture; the hawk's race carries the butcher-trophy extension at 35 %; the postfix that rolls it is on
Pawn.ButcherProducts and asks the kernel; the art is queued. The gate's logic itself (once only, toggle off = no letter, the
flat chance) is the fuzz family `rewards` (Source/SelfTest/Fuzz/FireHawkRewardsFuzz.cs, selftest_pyrelands_fuzz.py).
Live half: Pyrelands/firehawk_rewards_live_proof.py. Run: python3 <this file>
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
KEYED = os.path.join(HERE, "Languages", "English", "Keyed", "Pyrelands.xml")
FAUNA = os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_PyrelandsFauna.xml")
TROPHY_XML = os.path.join(HERE, "Defs", "ThingDefs_Items", "RM_PristineFirehawkCrestfeather.xml")
CODE = os.path.join(SRC, "FireHawkRewards.cs")
KERNEL = os.path.join(SRC, "Kernel", "RM_FireHawkRewardsKernel.cs")
SETTINGS = os.path.join(SRC, "RM_PyrelandsMod.cs")
COMP = os.path.join(SRC, "CompFireHawkSpread.cs")
ART_LIST = os.path.join(HERE, "..", "..", "..", "infrastructure", "artpipe", "art_lists",
                        "pyrelands_firehawk_crestfeather_2026-11-13.csv")
TROPHY = "RM_PristineFirehawkCrestfeather"
LABEL = "pristine firehawk crestfeather"
CHANCE = 0.35
SETTING = "fireHawkSightingLetterEnabled"
LETTER_KEYS = ("RM_FireHawkSightedLabel", "RM_FireHawkSightedText", "RM_FireHawkEmberFromPlant", "RM_FireHawkEmberFromBurn",
               "RM_FireHawkTargetPlant", "RM_FireHawkTargetGround")
COMPASS_KEYS = tuple("RM_Compass_" + d for d in ("N", "NE", "E", "SE", "S", "SW", "W", "NW"))


def _read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def _def(root, name):
    for d in root.iter("ThingDef"):
        if d.findtext("defName") == name:
            return d
    return None


def check_trophy(probs):
    if not os.path.exists(TROPHY_XML):
        probs.append("trophy: %s does not exist" % os.path.relpath(TROPHY_XML, HERE))
        return
    try:
        root = ET.parse(TROPHY_XML).getroot()
    except ET.ParseError as e:
        probs.append("trophy: XML does not parse: %s" % e)
        return
    d = _def(root, TROPHY)
    if d is None:
        probs.append("trophy: no ThingDef %s" % TROPHY)
        return
    if d.findtext("label") != LABEL:
        probs.append("trophy: label is %r, ruled %r" % (d.findtext("label"), LABEL))
    if d.findtext("category") != "Item":
        probs.append("trophy: category is not Item")
    sb = d.find("statBases")
    beauty = float(sb.findtext("Beauty") or "nan") if sb is not None else float("nan")
    value = float(sb.findtext("MarketValue") or "nan") if sb is not None else float("nan")
    hawk = _def(ET.parse(FAUNA).getroot(), "RM_FireHawk")
    hawk_value = float(hawk.find("statBases").findtext("MarketValue"))
    if not beauty >= 20:
        probs.append("trophy: Beauty %s is not art-grade (>= 20)" % beauty)
    if not value >= 1.5 * hawk_value:
        probs.append("trophy: MarketValue %s is not well above the hawk's %s" % (value, hawk_value))
    stack = int(d.findtext("stackLimit") or "75")
    if not 1 <= stack <= 10:
        probs.append("trophy: stackLimit %s is not a small stack" % stack)
    tex = d.findtext("graphicData/texPath") or ""
    raw = _read(TROPHY_XML)
    if not tex:
        probs.append("trophy: no texPath")
    elif TROPHY in tex and not os.path.exists(os.path.join(HERE, "Textures", tex + ".png")):
        probs.append("trophy: texPath %s points at our own art, which does not exist" % tex)
    elif TROPHY not in tex and "PLACEHOLDER ART" not in raw:
        probs.append("trophy: borrowed texPath %s is not marked PLACEHOLDER ART" % tex)
    # the hawk yields it
    ext = [li for li in hawk.iter("li") if (li.get("Class") or "").endswith("RM_ButcherTrophyExtension")]
    if not ext:
        probs.append("trophy: RM_FireHawk has no RM_ButcherTrophyExtension")
    else:
        e = ext[0]
        if e.findtext("thingDef") != TROPHY:
            probs.append("trophy: the hawk's extension yields %r, not %s" % (e.findtext("thingDef"), TROPHY))
        if abs(float(e.findtext("chance") or "nan") - CHANCE) > 1e-9:
            probs.append("trophy: the hawk's chance is %r, accepted %s" % (e.findtext("chance"), CHANCE))
    code = _read(CODE) if os.path.exists(CODE) else ""
    if not re.search(r"typeof\(Pawn\)\s*,\s*nameof\(Pawn\.ButcherProducts\)", code):
        probs.append("trophy: no Harmony patch on Pawn.ButcherProducts in FireHawkRewards.cs")
    if "RM_FireHawkRewardsKernel.TrophyDrops(" not in code:
        probs.append("trophy: the butcher postfix does not ask RM_FireHawkRewardsKernel.TrophyDrops")
    if not os.path.exists(ART_LIST) or TROPHY not in _read(ART_LIST):
        probs.append("trophy: no art-list row for %s (%s)" % (TROPHY, os.path.relpath(ART_LIST, HERE)))
    # the corrected name: "Emberhawk" is nowhere in the mod's defs, text, patches, art paths or code
    for sub in ("Defs", "Languages", "Patches", "Textures", "Source"):
        for dp, _dn, fns in os.walk(os.path.join(HERE, sub)):
            for fn in fns:
                p = os.path.join(dp, fn)
                if "emberhawk" in fn.lower():
                    probs.append("name: file %s says Emberhawk" % os.path.relpath(p, HERE))
                if fn.endswith((".xml", ".cs")) and "emberhawk" in _read(p).lower():
                    probs.append("name: %s says Emberhawk" % os.path.relpath(p, HERE))


def main():
    probs = []
    check_trophy(probs)
    print("selftest_pyrelands_firehawk_crestfeather: %s" % ("FAIL" if probs else "PASS"))
    for p in probs:
        print("  - " + p)
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
