#!/usr/bin/env python3
"""Offline selftest: after RSW_OdysseyAsteroidNoPlasteel.xml no Odyssey def still places plasteel or industrial
components from rock, and every resource an asteroid quest can pick still has a count in its GenStep
(ASTEROIDQUEST_FIX_PLASTEEL_PICK_NO_COUNT).
    python3 src/RimStarWars/Armoury/selftest_odyssey_asteroid_pick_counts.py [--patch PATH]

GenStep_Asteroid.SpawnOres (decomp RimWorld/GenStep_Asteroid.cs:157) takes the map parent's preciousResource and
looks up its count in mineableCounts; no count -> Debug.LogError "No count found for resource" and no ore. The quest
OpportunitySite_Asteroid (QuestScriptDefs/Script_SpaceSites.xml) sets preciousResource from its mineables list on an
AsteroidMiningSite (mapGenerator Asteroid). The patch dropped MineablePlasteel from GenStep Asteroid and not from
the quest list.
1. Every Odyssey Defs XML file is loaded and the patch's Remove ops replayed on it (lxml xpath).
2. No MineablePlasteel / MineableComponentsIndustrial text or tag is left anywhere in Odyssey Defs.
3. Every QuestNode_Root_Asteroid mineables entry has a mineableCounts child in GenStepDef Asteroid.
4. The instrument can see: unpatched, Odyssey holds >= 8 such references and the quest lists MineablePlasteel.
--patch replays another copy (`git show <old>:...RSW_OdysseyAsteroidNoPlasteel.xml` -> red).
Odyssey not installed -> UNMEASURED, exit 2.
"""
import argparse
import glob
import os
import sys

from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
PATCH = os.path.join(HERE, "Patches", "RSW_OdysseyAsteroidNoPlasteel.xml")
ODYSSEY = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data/Odyssey/Defs"
DROP = ("MineablePlasteel", "MineableComponentsIndustrial")
QUEST_PICKS = '//QuestScriptDef[defName="OpportunitySite_Asteroid"]//li[@Class="QuestNode_Root_Asteroid"]/mineables/li/text()'


def load():
    roots = []
    for p in sorted(glob.glob(os.path.join(ODYSSEY, "**", "*.xml"), recursive=True)):
        try:
            roots.append(etree.parse(p, etree.XMLParser(remove_comments=True)).getroot())
        except etree.XMLSyntaxError:
            continue
    return roots


def refs(roots):
    n = 0
    for r in roots:
        for el in r.iter():
            if not isinstance(el.tag, str) or el.tag == "defName":
                continue
            n += el.tag in DROP
            n += (el.text or "").strip() in DROP
    return n


def replay(patch, roots):
    for op in etree.parse(patch).getroot().iter("Operation"):
        if op.get("Class") != "PatchOperationRemove":
            raise SystemExit("unexpected op class %r: this replay only simulates Remove" % op.get("Class"))
        xp = op.findtext("xpath")
        for r in roots:
            for hit in r.getroottree().xpath(xp):
                hit.getparent().remove(hit)


def problems(roots):
    out = []
    if refs(roots):
        out.append("%d MineablePlasteel/MineableComponentsIndustrial references left in Odyssey Defs" % refs(roots))
    counts = set()
    picks = []
    for r in roots:
        for el in r.xpath('//GenStepDef[defName="Asteroid"]/genStep/mineableCounts/*'):
            counts.add(el.tag)
        picks += r.xpath(QUEST_PICKS)
    for p in picks:
        if p not in counts:
            out.append("quest OpportunitySite_Asteroid can pick %s, which GenStep Asteroid has no count for" % p)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--patch", default=PATCH)
    a = ap.parse_args(argv)
    if not os.path.isdir(ODYSSEY):
        print("UNMEASURED: %s not readable" % ODYSSEY)
        return 2
    fails = []
    raw = load()
    n0 = refs(raw)
    picks0 = [p for r in raw for p in r.xpath(QUEST_PICKS)]
    if n0 < 8 or "MineablePlasteel" not in picks0:
        fails.append("instrument blind: unpatched Odyssey has %d references, quest picks %r" % (n0, picks0))
    replay(a.patch, raw)
    fails += problems(raw)
    if fails:
        print("FAIL (%d)" % len(fails))
        for m in fails:
            print("  - " + m)
        return 1
    print("OK: %d references removed, quest picks all have a GenStep Asteroid count" % n0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
