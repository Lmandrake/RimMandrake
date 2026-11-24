#!/usr/bin/env python3
"""Offline proof for RIMMANDRAKE_FIX_THREE_WEIRD_EATERS_WITH_NO_THINK_TREE: a weird eater keeps a think tree when
Vanilla Expanded Framework (VEF) is not loaded.

A `<thinkTreeMain MayRequire="VEF">` in a child def replaces the inherited `Animal` in XML inheritance, and the field
is then skipped at parse when VEF is absent: the race has no tree and every job search throws. So:
  1. no def in any RimMandrake mod guards thinkTreeMain with MayRequire;
  2. each weird eater reads `Animal` when the VEF ThinkTreeDef is absent, and VEF_AnimalWeirdEater when it is loaded,
     after its own patch files ran on it.
A sanity probe plants the old shape and confirms check 1 goes red.

RM_CrystalMit (Cauldron) is not fixed: the owner holds that mod (mod_owner_hold.json). While the hold stands its row
prints HELD, never PASS, and it is not counted as a failure. With the hold lifted it is a failure like any other.
Run: python3 src/RimMandrake/Utils/selftest_weird_eater_think_tree.py
"""
import json
import sys
from pathlib import Path

from lxml import etree as ET

RM = Path(__file__).resolve().parents[1]
TREE = "VEF_AnimalWeirdEater"
EATERS = {"RM_Dustveil": "TheRot", "RM_Metallovore": "TheForge", "RM_CrystalMit": "Cauldron", "RM_DecayDrake": "Miasma"}
EATERS.update({d: "GelatinousSlime" for d in ("RM_Oomb", "RM_LesserOomb", "RM_GreaterOomb")})
PARENT_TREE = "Animal"   # Core AnimalThingBase


def guarded(root):
    return [(t.findtext("defName") or "?") for t in root.iter("ThingDef") for e in t.findall("race/thinkTreeMain")
            if e.get("MayRequire")]


def find_def(mod, name):
    for p in sorted((RM / mod / "Defs").rglob("*.xml")):
        for t in ET.parse(str(p)).getroot().iter("ThingDef"):
            if (t.findtext("defName") or "").strip() == name:
                return t
    return None


def apply(op, doc):
    """The patch classes the weird-eater patches use; any other class is not applied here."""
    cls, xp = op.get("Class"), op.findtext("xpath")
    if cls == "PatchOperationConditional":
        branch = op.find("match" if doc.xpath(xp) else "nomatch")
        if branch is not None:
            apply(branch, doc)
    elif cls == "PatchOperationSequence":
        for li in op.find("operations"):
            if isinstance(li.tag, str):
                apply(li, doc)
    elif cls in ("PatchOperationAdd", "PatchOperationReplace") and "thinkTreeMain" in ET.tostring(op).decode():
        for hit in doc.xpath(xp):
            new = [ET.fromstring(ET.tostring(v, with_tail=False)) for v in op.find("value")]
            if cls == "PatchOperationAdd":
                hit.extend(new)
            else:
                for v in new:
                    hit.addprevious(v)
                hit.getparent().remove(hit)


def tree_of(mod, name, vef):
    t = find_def(mod, name)
    if t is None:
        return "NO DEF"
    doc = ET.Element("Defs")
    doc.append(ET.fromstring(ET.tostring(t, with_tail=False)))
    if vef:
        ET.SubElement(ET.SubElement(doc, "ThinkTreeDef"), "defName").text = TREE
    for p in sorted((RM / mod / "Patches").rglob("*.xml")):
        for op in ET.parse(str(p)).getroot().findall("Operation"):
            if TREE in ET.tostring(op).decode():
                apply(op, doc)
    got = doc.findall("ThingDef/race/thinkTreeMain")
    if len(got) > 1:
        return "DUPLICATE thinkTreeMain"
    if not got:
        return PARENT_TREE
    if got[0].get("MayRequire") and not vef:
        return "NO TREE"
    return (got[0].text or "").strip()


def main():
    held = {h["mod"] for h in json.loads((RM / "rimflow" / "mod_owner_hold.json").read_text())["holds"]}
    fails, n_held, files = 0, 0, 0

    def row(ok, text, mod):
        nonlocal fails, n_held
        if ok:
            print("ok   ", text)
        elif mod in held:
            n_held += 1
            print("HELD ", text, "(%s is held by the owner; not fixed)" % mod)
        else:
            fails += 1
            print("FAIL ", text)

    for p in sorted(RM.glob("*/Defs/**/*.xml")):
        try:
            root = ET.parse(str(p)).getroot()
        except ET.XMLSyntaxError:
            continue   # unparsable XML is another test's finding
        files += 1
        for d in guarded(root):
            row(False, "%s: thinkTreeMain carries MayRequire" % d, p.relative_to(RM).parts[0])
    if not files:
        fails += 1
        print("FAIL  no def file was read")
    for name, mod in sorted(EATERS.items()):
        for vef, want in ((False, PARENT_TREE), (True, TREE)):
            got = tree_of(mod, name, vef)
            row(got == want, "%s, VEF %s: %s (want %s)" % (name, "loaded" if vef else "absent", got, want), mod)

    bad = ET.fromstring('<Defs><ThingDef><defName>X</defName><race><thinkTreeMain MayRequire="v">T</thinkTreeMain>'
                        '</race></ThingDef></Defs>')
    if guarded(bad) != ["X"]:
        fails += 1
        print("FAIL  sanity: the guard check did not see a planted MayRequire")
    print("%s: %d files read, %d failure(s), %d held" % ("FAIL" if fails else "PASS", files, fails, n_held))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
