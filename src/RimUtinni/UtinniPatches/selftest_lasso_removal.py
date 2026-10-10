#!/usr/bin/env python3
"""LASSO_CHERRYPICKER_REMOVAL_1: no Melee Animation lasso can be crafted. Offline, no game.

Every Make_AM_Lasso* RecipeDef is IMPLIED from a ThingDef's <recipeMaker> (resolved through inheritance), so the
check simulates exactly that: apply MeleeAnimation_LassoRemoval.xml's xpath to Melee Animation's Lassos.xml, resolve
ParentName chains, and red if any concrete lasso still inherits or owns a <recipeMaker>. Sanity probe: WITHOUT the
patch the same resolver must find every concrete lasso craftable (3), or it proves nothing.

Uses the installed mod's Lassos.xml when the Steam workshop folder is reachable, else an embedded copy of its
def shape (so it runs on the Mac too). Also reds if the SHIP Cherry Picker profile drops a lasso RecipeDef cut.
"""
import copy
import os
import sys

from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PATCH = os.path.join(HERE, "Patches", "MeleeAnimation_LassoRemoval.xml")
SHIP = os.path.join(ROOT, "infrastructure", "state", "cherrypicker", "CherryPicker.SHIP.xml")
INSTALLED = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/2944488802/1.6/Defs/Lassos.xml"
EMBEDDED = b"""<Defs>
<ThingDef Name="AM_LassoBase" Abstract="True"><apparel><tags><li>Lasso</li></tags></apparel></ThingDef>
<ThingDef Name="AM_LassoBaseMakeable" ParentName="AM_LassoBase" Abstract="True">
  <recipeMaker><recipeUsers><li>ElectricTailoringBench</li><li>HandTailoringBench</li></recipeUsers></recipeMaker></ThingDef>
<ThingDef ParentName="AM_LassoBaseMakeable"><defName>AM_LassoCloth</defName>
  <recipeMaker><skillRequirements><Crafting>4</Crafting></skillRequirements></recipeMaker></ThingDef>
<ThingDef ParentName="AM_LassoBaseMakeable"><defName>AM_LassoDevilstrand</defName>
  <recipeMaker><skillRequirements><Crafting>6</Crafting></skillRequirements></recipeMaker></ThingDef>
<ThingDef ParentName="AM_LassoBaseMakeable"><defName>AM_LassoHyperwave</defName>
  <recipeMaker><skillRequirements><Crafting>6</Crafting></skillRequirements></recipeMaker></ThingDef>
</Defs>"""
FAILS = []


def check(name, ok, detail=""):
    print("%s  %s %s" % ("ok  " if ok else "FAIL", name, "" if ok else detail))
    if not ok:
        FAILS.append(name)


def craftable(defs):
    """defName -> True when the resolved def carries a recipeMaker (the engine would generate Make_<defName>)."""
    by_name = {t.get("Name"): t for t in defs.findall("ThingDef") if t.get("Name")}
    out = {}
    for t in defs.findall("ThingDef"):
        dn = t.findtext("defName")
        if not dn or t.get("Abstract") == "True":
            continue
        node, has = t, False
        while node is not None and not has:
            has = node.find("recipeMaker") is not None
            node = by_name.get(node.get("ParentName"))
        out[dn] = has
    return out


def main():
    src = "installed"
    if os.path.isfile(INSTALLED):
        defs = etree.parse(INSTALLED).getroot()
    else:
        src, defs = "embedded", etree.fromstring(EMBEDDED)
    patch = etree.parse(PATCH).getroot()
    mods = [li.text for li in patch.iter("li")]
    check("patch is FindMod-guarded on Melee Animation", "Melee Animation" in mods, str(mods))
    xp = patch.findtext(".//match/xpath")
    check("patch has a remove xpath", bool(xp))

    before = craftable(defs)
    lassos = sorted(k for k in before if k.startswith("AM_Lasso"))
    check("sanity probe: unpatched resolver finds 3 craftable lassos (%s)" % src,
          sum(before[k] for k in lassos) == 3, str(before))

    doc = etree.ElementTree(copy.deepcopy(etree.Element("Defs")))
    root = doc.getroot()
    for t in defs:
        root.append(copy.deepcopy(t))
    hits = doc.xpath("/" + xp)
    for n in hits:
        n.getparent().remove(n)
    check("xpath matches the parent + every child recipeMaker", len(hits) == 4, "matched %d" % len(hits))
    after = craftable(root)
    still = [k for k in lassos if after[k]]
    check("no lasso craftable after the patch", not still, "still craftable: %s" % still)

    ship = open(SHIP, encoding="utf-8").read()
    for r in ("Make_AM_LassoCloth", "Make_AM_LassoDevilstrand", "Make_AM_LassoHyperwave"):
        check("SHIP profile cuts RecipeDef/%s" % r, "RecipeDef/%s<" % r in ship)
    print("lasso removal: %d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
