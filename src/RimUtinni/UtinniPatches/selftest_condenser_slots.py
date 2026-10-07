#!/usr/bin/env python3
"""WEEPINGSTONES_CONDENSER_QUESTS_1 — the campaign maps the condenser buyer slot to the Hutt Cartel.

Applies Patches/RUT_CondenserQuestSlots.xml to the free mod's slot defs with lxml (the
PatchOperationConditional > PatchOperationInsert(Prepend) semantics) and checks:
  * the buyer slot's preferredFactions becomes [RUT_Jawa_HuttCartel, Empire] — head, not tail;
  * the settlers/hunters slots are untouched;
  * RUT_Jawa_HuttCartel is a real FactionDef in UtinniPatches (a guessed defName is skipped silently);
  * with the slot absent, the conditional matches nothing (no-op without the free mod).
"""
import copy
import os
import sys

from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(HERE))
PATCH = os.path.join(HERE, "Patches", "RUT_CondenserQuestSlots.xml")
SLOTS = os.path.join(SRC, "RimMandrake", "WeepingStones", "Defs", "FactionSlotDefs",
                     "RM_CondenserQuestSlots.xml")
FACTION = os.path.join(HERE, "Defs", "FactionDefs", "JawaHuttCartel.xml")
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def apply(patch_root, doc):
    """Minimal PatchOperationConditional/Insert interpreter over a document; returns targets hit."""
    applied = 0
    for op in patch_root.findall("Operation"):
        assert op.get("Class") == "PatchOperationConditional"
        if not doc.xpath("/" + op.findtext("xpath")):
            continue
        m = op.find("match")
        assert m.get("Class") == "PatchOperationInsert"
        order = (m.findtext("order") or "Prepend").strip()
        for tgt in doc.xpath("/" + m.findtext("xpath")):
            for v in list(m.find("value")):
                v = copy.deepcopy(v)
                if order == "Prepend":
                    tgt.addprevious(v)
                else:
                    tgt.addnext(v)
            applied += 1
    return applied


def prefs(doc, slot):
    return [li.text for li in doc.xpath(
        '/Defs/RimMandrake.WeepingStones.RM_FactionSlotDef[defName="%s"]/preferredFactions/li' % slot)]


def main():
    patch = etree.parse(PATCH).getroot()
    doc = etree.parse(SLOTS)   # document node: RimWorld xpaths start at it
    before = {s: prefs(doc, s) for s in ("RM_FactionSlot_CondenserSettlers",
                                         "RM_FactionSlot_CondenserHunters")}
    check(prefs(doc, "RM_FactionSlot_CondenserBuyer") == ["Empire"], "free buyer slot is [Empire]")
    n = apply(patch, doc)
    check(n == 1, "patch applies exactly once (got %d)" % n)
    check(prefs(doc, "RM_FactionSlot_CondenserBuyer") == ["RUT_Jawa_HuttCartel", "Empire"],
          "campaign buyer slot is [RUT_Jawa_HuttCartel, Empire] (got %r)"
          % prefs(doc, "RM_FactionSlot_CondenserBuyer"))
    check(all(prefs(doc, s) == v for s, v in before.items()), "settlers and hunters slots untouched")
    fdefs = etree.parse(FACTION).getroot().xpath('//FactionDef/defName/text()')
    check("RUT_Jawa_HuttCartel" in fdefs, "RUT_Jawa_HuttCartel is a real FactionDef")
    check(apply(patch, etree.ElementTree(etree.fromstring(b"<Defs/>"))) == 0, "no slot def -> no-op")
    print("ALL PASS" if not FAILS else "%d FAIL" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
