#!/usr/bin/env python3
"""The config errors CONFIGERRORS_FIX_FIVE_MORE_ON_LATEST_LOAD removed stay removed, read from src/ with no game load.

  HediffDef comps      Every HediffDef with comps needs a hediffClass, on it or up its ParentName chain under src/. An
                       unresolved parent is a vanilla or donor base and is not judged. One with no parent and no class is
                       plain Hediff: the engine logs a config error and never runs its comps.
  beskar deposit       Armoury zeroes OuterRim_Beskar's deepCommonality, so it must also zero the deepLumpSizeRange Outer
                       Rim ships (ThingDef.ConfigErrors wants both set or both empty).
  research cells       Dubs Bad Hygiene Lite's C#, in Lite mode, writes private x,y for four projects after relaxation,
                       and ResearchProjectDef.ConfigErrors compares x,y. Hearth nodes must stay off those cells, so Cocoa
                       (native 1,0) must have its Y moved by ResearchRetag.
  coodler roe          Its def and recipe stay, and ColdStorage's committed DLL holds the comp type the def needs.
  retired donor biome  No src/ XML list names ZBiome_Grasslands as a value.
Exit 0 clean, 1 a rule broken, 2 UNMEASURED (the walk could not see what it must see)."""
import glob
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
DBH_LITE_CELLS = {"ModernFixtures": (0.0, 0.0), "HotTubs": (1.0, 0.0), "AdvancedShowers": (2.0, 0.0), "AdvancedToilets": (3.0, 0.0)}
COCOA_NATIVE = (1.0, 0.0)   # Data/Core/Defs/ResearchProjectDefs/ResearchProjects_1.xml
RETAG = "src/RimUtinni/ResearchRetag/Patches/RUT_ResearchTabAssign.xml"
BESKAR = "src/RimStarWars/Armoury/Patches/RSW_BeskarNeverReforged.xml"
DISHES = "src/RimStarWars/Cuisine/Defs/RSW_PreservedDishes.xml"
COLD_DLL = "src/RimMandrake/ColdStorage/Assemblies/RimMandrakeColdStorage.dll"


def src_xml():
    for path in glob.glob(os.path.join(ROOT, "src", "**", "*.xml"), recursive=True):
        try:
            yield path, ET.parse(path).getroot()
        except ET.ParseError:
            continue


def hediff_findings(roots):
    """Returns (names seen, findings) for the comps rule."""
    named, by_name = {}, {}
    for _path, root in roots:
        if root.tag != "Defs":
            continue
        for d in root.iter("HediffDef"):
            if d.get("Name"):
                by_name[d.get("Name")] = d
            if d.findtext("defName"):
                named[d.findtext("defName")] = d
    bad = []
    for name, d in named.items():
        node, has_comps, has_class, resolved = d, False, False, True
        for _ in range(20):
            has_comps = has_comps or node.find("comps") is not None
            has_class = has_class or node.find("hediffClass") is not None
            parent = node.get("ParentName")
            if not parent:
                break
            if parent not in by_name:
                resolved = False
                break
            node = by_name[parent]
        if has_comps and not has_class and resolved:
            bad.append(name)
    return set(named), sorted(bad)


def patch_values(root, xpath_end):
    """The value text of each PatchOperationReplace/Add in this patch whose xpath ends with xpath_end."""
    out = []
    for op in root.iter():
        xp = op.findtext("xpath")
        value = op.find("value")
        if xp and value is not None and xp.endswith(xpath_end):
            out.extend(child.text for child in value)
    return out


def main():
    roots = list(src_xml())
    bad, unmeasured = [], []
    seen, hediffs = hediff_findings(roots)
    if "RM_Dehydration" not in seen or len(seen) < 50:
        unmeasured.append("the HediffDef walk is blind: %d defs" % len(seen))
    bad += ["%s has comps with no hediffClass" % n for n in hediffs]

    for rel in (RETAG, BESKAR, DISHES, COLD_DLL):
        if not os.path.exists(os.path.join(ROOT, rel)):
            unmeasured.append("missing " + rel)
    if unmeasured:
        print("UNMEASURED: " + "; ".join(unmeasured))
        return 2

    beskar = ET.parse(os.path.join(ROOT, BESKAR)).getroot()
    tail = '[defName="OuterRim_Beskar"]/'
    if "0" not in patch_values(beskar, tail + "deepCommonality"):
        unmeasured.append("no deepCommonality zero op for OuterRim_Beskar: this rule no longer applies as written")
    if patch_values(beskar, tail + "deepLumpSizeRange") != ["0~0"]:
        bad.append("OuterRim_Beskar deepCommonality is zeroed, its deepLumpSizeRange is not")

    retag = ET.parse(os.path.join(ROOT, RETAG)).getroot()
    ys = patch_values(retag, '[defName="Cocoa"]/researchViewY')
    xs = patch_values(retag, '[defName="Cocoa"]/researchViewX')
    cocoa = (float(xs[0]) if xs else COCOA_NATIVE[0], float(ys[0]) if ys else COCOA_NATIVE[1])
    if cocoa in DBH_LITE_CELLS.values():
        bad.append("Cocoa sits on a Dubs Bad Hygiene Lite cell: %s" % (cocoa,))
    if patch_values(retag, '[defName="HotTubs"]/researchViewX'):
        bad.append("a raw HotTubs pin is back; it cannot reach the x,y the check reads")

    dishes = ET.parse(os.path.join(ROOT, DISHES)).getroot()
    things = {d.findtext("defName"): d for d in dishes.iter("ThingDef")}
    recipes = {d.findtext("defName"): d for d in dishes.iter("RecipeDef")}
    roe = things.get("RSW_BrinedCoodlerRoe")
    if roe is None or "RSW_BrineCoodlerRoe" not in recipes:
        bad.append("the brined coodler roe def or its recipe is gone")
    else:
        if roe.get("MayRequire") != recipes["RSW_BrineCoodlerRoe"].get("MayRequire"):
            bad.append("roe def and recipe carry different MayRequire")
        if recipes["RSW_BrineCoodlerRoe"].find("products/RSW_BrinedCoodlerRoe") is None:
            bad.append("the recipe no longer makes RSW_BrinedCoodlerRoe")
    with open(os.path.join(ROOT, COLD_DLL), "rb") as fh:
        if b"CompProperties_ColdAging" not in fh.read():
            bad.append("ColdStorage's committed DLL lacks CompProperties_ColdAging")

    named = [os.path.relpath(p, ROOT) for p, root in roots
             if any((e.tag == "li" and (e.text or "").strip() == "ZBiome_Grasslands") for e in root.iter())]
    bad += ["%s lists ZBiome_Grasslands" % p for p in named]

    if unmeasured:
        print("UNMEASURED: " + "; ".join(unmeasured))
        return 2
    for b in bad:
        print("FAIL " + b)
    print("selftest_config_errors_five: %d HediffDefs walked, %s" % (len(seen), "FAIL" if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
