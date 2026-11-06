#!/usr/bin/env python3
"""The config errors CONFIGERRORS_FIX_THREE_LEFTOVER_CLASSES removed stay removed, read from XML with no game load.

Three engine rules, each walked over every ThingDef under src/ through its ParentName chain (children append list
entries to what they inherit, which is how the duplicates were made):
  duplicate thingCategory   ThingDef.ConfigErrors: a category listed twice anywhere in the chain.
  forcedMiss                VerbProperties.ConfigErrors: forcedMissRadius > 0 must equal CausesExplosion
                            (Projectile_Explosive, Projectile_DoomsdayRocket or CompProperties_Explosive).
  zero nutrition            a plant under vanilla's PlantBase with no Nutrition must say NeverForNutrition.
A vanilla ancestor is not under src/, so the two it matters for are named: FurnitureBase's category and PlantBase's
RawBad food (Data/Core/Defs/ThingDefs_Buildings/Buildings_Furniture.xml, ThingDefs_Plants/Plants_Bases.xml).
Exit 0 clean, 1 a def breaks a rule, 2 UNMEASURED (the walk could not see the defs it must see)."""
import glob
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
VANILLA_CATEGORIES = {"FurnitureBase": ["BuildingsFurniture"]}
VANILLA_FURNITURE_CHILDREN = {"FurnitureWithQualityBase": "FurnitureBase", "ArtableFurnitureBase": "FurnitureWithQualityBase",
                              "BedBase": "FurnitureBase", "ShelfBase": "FurnitureBase", "StorageShelfBase": "ShelfBase"}
EXPLOSIVE_CLASSES = {"Projectile_Explosive", "Projectile_DoomsdayRocket"}
# Vanilla parents whose thingClass is Projectile_Explosive (Data/Core/Defs, BaseGrenadeProjectile etc.).
VANILLA_EXPLOSIVE_PARENTS = {"BaseGrenadeProjectile", "BaseIncendiaryProjectile"}
# The defs this item fixed: the walk must find each of them, or it proves nothing.
MUST_SEE = ["RM_AncientStasisLocker_Kludged", "RSW_RakatanStasisVault_Original", "RM_AmberAgedFruit",
            "guy762_bowcaster_ceremonial", "guy762_hvyrepeater_massdriver", "guy762_lgtrepeater_onderon", "RM_TalusClasp"]


def load_defs():
    """Every ThingDef under src/ -> (by defName, by Name). A file that does not parse is not read here: the XML
    validators own that."""
    named, abstract = {}, {}
    for path in glob.glob(os.path.join(ROOT, "src", "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        if root.tag != "Defs":
            continue
        for d in root.findall("ThingDef"):
            if d.findtext("defName"):
                named.setdefault(d.findtext("defName"), d)
            if d.get("Name"):
                abstract.setdefault(d.get("Name"), d)
    return named, abstract


def chain(d, abstract):
    """The def and its ancestors under src/, then the first ancestor name src/ does not hold (vanilla or a donor)."""
    out, seen = [d], set()
    parent = d.get("ParentName")
    while parent and parent in abstract and parent not in seen:
        seen.add(parent)
        out.append(abstract[parent])
        parent = abstract[parent].get("ParentName")
    return out, parent


def inherited(d, abstract, path):
    """The nearest value of a single-valued field along the chain."""
    for link in chain(d, abstract)[0]:
        if link.findtext(path) is not None:
            return link.findtext(path)
    return None


def categories(d, abstract):
    links, outside = chain(d, abstract)
    cats = []
    for link in links:
        node = link.find("thingCategories")
        if node is not None:
            cats += [li.text for li in node.findall("li")]
            if node.get("Inherit", "").lower() == "false":
                return cats
    while outside in VANILLA_FURNITURE_CHILDREN:
        outside = VANILLA_FURNITURE_CHILDREN[outside]
    return cats + VANILLA_CATEGORIES.get(outside, [])


def findings(named, abstract):
    out = []
    for name, d in sorted(named.items()):
        if d.get("Abstract", "").lower() == "true":
            continue
        cats = categories(d, abstract)
        for cat in sorted({c for c in cats if cats.count(c) > 1}):
            out.append("%s: has duplicate thingCategory %s" % (name, cat))
        verbs = next((v for v in (x.find("verbs") for x in chain(d, abstract)[0]) if v is not None), None)
        for i, verb in enumerate(verbs if verbs is not None else []):
            miss = float(verb.findtext("forcedMissRadius") or 0)
            shot = verb.findtext("defaultProjectile")
            if miss <= 0 or shot not in named:
                continue
            links, outside = chain(named[shot], abstract)
            cls = inherited(named[shot], abstract, "thingClass")
            if cls and "." in cls:
                continue  # a mod's own projectile class: its base is in C#, and this walk reads XML
            explosive = cls in EXPLOSIVE_CLASSES or (cls is None and outside in VANILLA_EXPLOSIVE_PARENTS) or any(
                li.get("Class") == "CompProperties_Explosive" for x in links for li in x.findall("comps/li"))
            if not explosive:
                out.append("%s: verb %d: forcedMissRadius %s on non-explosive %s" % (name, i, miss, shot))
        if chain(d, abstract)[1] == "PlantBase" and inherited(d, abstract, "statBases/Nutrition") is None:
            food = inherited(d, abstract, "ingestible/preferability") or "RawBad"
            if food != "NeverForNutrition":
                out.append("%s: Nutrition 0 but preferability %s" % (name, food))
    return out


def probe():
    """The rules can see a break: one made-up def per rule, each of which must be reported."""
    defs = ET.fromstring("""<Defs>
      <ThingDef Name="ProbeBase" ParentName="ShelfBase" Abstract="True"><thingCategories><li>BuildingsFurniture</li></thingCategories></ThingDef>
      <ThingDef ParentName="ProbeBase"><defName>ProbeDouble</defName></ThingDef>
      <ThingDef ParentName="BaseBullet"><defName>ProbeBolt</defName></ThingDef>
      <ThingDef><defName>ProbeGun</defName><verbs><li><forcedMissRadius>2</forcedMissRadius><defaultProjectile>ProbeBolt</defaultProjectile></li></verbs></ThingDef>
      <ThingDef ParentName="PlantBase"><defName>ProbePlant</defName></ThingDef>
    </Defs>""")
    named = {d.findtext("defName"): d for d in defs if d.findtext("defName")}
    abstract = {d.get("Name"): d for d in defs if d.get("Name")}
    return findings(named, abstract)


def main():
    seen = probe()
    if len(seen) != 3:
        print("UNMEASURED: the rules saw %d of 3 planted breaks: %s" % (len(seen), seen))
        return 2
    named, abstract = load_defs()
    blind = [n for n in MUST_SEE if n not in named]
    if blind:
        print("UNMEASURED: the walk did not find %s" % ", ".join(blind))
        return 2
    found = findings(named, abstract)
    for line in found:
        print("FAIL " + line)
    print("%d ThingDefs walked, %d findings" % (len(named), len(found)))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
