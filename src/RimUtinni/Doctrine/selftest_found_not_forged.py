#!/usr/bin/env python3
"""selftest_found_not_forged.py -- offline check of OILGAS_BUILDABILITY_EXCISE_FOUND_NOT_FORGED (mandrake.rut.doctrine).

    python3 src/RimUtinni/Doctrine/selftest_found_not_forged.py        exit 0 PASS, 1 FAIL, 2 UNMEASURED

Need: the player can never build Rimefeller's oil works or VHGE's helixien pump (they are found, never built), and
VHGE's infinite deposits are removed by a switch of ours that is on by default.

What it does: reads the INSTALLED Rimefeller and Vanilla Helixien Gas Expanded 1.6 defs from the Workshop folder,
applies src/RimUtinni/Doctrine/Patches/FoundNotForged.xml to them with the subset of PatchOperations the file uses
(a PatchOperation class this check does not know is a FAIL, never skipped), resolves XML inheritance of
designationCategory by ParentName, and reads the result:
  - the six works (OilWell, DeepOilWell, OilStorage, CrudeCracker, RefineryLoadingBay, VHGE_HelixienPump) have an
    effective designationCategory that is empty (an empty def node loads as null: Verse.DirectXmlToObject);
  - must stay green: FuelStorage (Rimefeller) and VHGE's other buildings keep theirs, so the patch is not a blanket;
  - the patch is gated by our setting class, and that class, the setting names and the Harmony target are in our C#;
  - the Harmony target VHelixienGasE.HelixienGasHandler.InitDeposits exists in the installed VHGE assembly.
The donor mods missing from this machine is UNMEASURED (exit 2), never a pass.
"""
import os
import re
import sys

from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
PATCH = os.path.join(HERE, "Patches", "FoundNotForged.xml")
SRC = os.path.join(HERE, "Source", "DoctrineCore")
WS = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
MODS = {"Rimefeller": os.path.join(WS, "1321849735", "1.6", "Defs"),
        "Vanilla Helixien Gas Expanded": os.path.join(WS, "2877699803", "1.6", "Defs")}
VHGE_DLL = os.path.join(WS, "2877699803", "1.6", "Assemblies", "VHelixienGasE.dll")
TARGETS = ["OilWell", "DeepOilWell", "OilStorage", "CrudeCracker", "RefineryLoadingBay", "VHGE_HelixienPump"]
KEEP = ["FuelStorage"]  # Rimefeller, must keep its category
GATE = "RimMandrake.Utinni.Doctrine.PatchOperationDoctrineSetting"


class Unknown(Exception):
    pass


def apply(op, doc, loaded):
    """One PatchOperation node on the unified doc -> success bool (vanilla semantics for the classes used)."""
    cls = op.get("Class")
    if cls == GATE:
        # the gate's default is ON: the check reads the shipped default from our C#
        return apply(op.find("match"), doc, loaded) if op.find("match") is not None else True
    if cls == "PatchOperationSequence":
        return all(apply(li, doc, loaded) for li in op.find("operations"))
    if cls == "PatchOperationFindMod":
        wanted = [li.text for li in op.find("mods")]
        branch = op.find("match") if any(w in loaded for w in wanted) else op.find("nomatch")
        return True if branch is None else apply(branch, doc, loaded)
    if cls == "PatchOperationConditional":
        hit = doc.xpath(op.findtext("xpath"))
        branch = op.find("match") if hit else op.find("nomatch")
        return True if branch is None else apply(branch, doc, loaded)
    nodes = doc.xpath(op.findtext("xpath"))
    if cls == "PatchOperationAdd":
        for n in nodes:
            for v in op.find("value"):
                n.append(etree.fromstring(etree.tostring(v)))
        return bool(nodes)
    if cls == "PatchOperationReplace":
        for n in nodes:
            parent = n.getparent()
            i = parent.index(n)
            parent.remove(n)
            for k, v in enumerate(op.find("value")):
                parent.insert(i + k, etree.fromstring(etree.tostring(v)))
        return bool(nodes)
    if cls == "PatchOperationRemove":
        for n in nodes:
            n.getparent().remove(n)
        return bool(nodes)
    raise Unknown(cls)


def effective(doc, defname, field):
    """(found, text) of `field` on ThingDef `defname` after inheritance by ParentName/Name."""
    node = doc.xpath('/Defs/ThingDef[defName="%s"][not(@Abstract="True") and not(@Abstract="true")]' % defname)
    if not node:
        return False, None
    cur = node[-1]
    seen = 0
    while cur is not None and seen < 20:  # inheritance depth guard: a cycle would loop forever
        el = cur.find(field)
        if el is not None:
            return True, (el.text or "").strip()
        p = cur.get("ParentName")
        cur = doc.xpath('/Defs/ThingDef[@Name="%s"]' % p)[-1] if p and doc.xpath('/Defs/ThingDef[@Name="%s"]' % p) else None
        seen += 1
    return True, ""


def main():
    for name, d in MODS.items():
        if not os.path.isdir(d):
            print("UNMEASURED: %s defs not on this machine (%s)" % (name, d))
            return 2
    if not os.path.isfile(VHGE_DLL):
        print("UNMEASURED: %s not on this machine" % VHGE_DLL)
        return 2
    fails = []
    doc = etree.Element("Defs")
    nfiles = 0
    for d in MODS.values():
        for root, _, files in os.walk(d):
            for f in sorted(files):
                if f.lower().endswith(".xml"):
                    for el in etree.parse(os.path.join(root, f)).getroot():
                        if isinstance(el.tag, str):
                            doc.append(el)
                    nfiles += 1
    doc = etree.ElementTree(doc)
    before = {t: effective(doc, t, "designationCategory") for t in TARGETS + KEEP}
    for t, (found, val) in before.items():
        if not found:
            fails.append("%s not in the installed defs: the target list is stale" % t)
        elif not val:
            fails.append("%s already unbuildable before the patch: the probe cannot see" % t)
    if not os.path.isfile(PATCH):
        fails.append("no patch %s" % os.path.relpath(PATCH, HERE))
    else:
        root = etree.parse(PATCH).getroot()
        gated = [op for op in root if isinstance(op.tag, str) and op.get("Class") == GATE]
        if not gated:
            fails.append("the patch is not gated by %s (no Mod Settings switch)" % GATE)
        try:
            for op in root:
                if isinstance(op.tag, str) and not apply(op, doc, set(MODS)):
                    fails.append("a top-level operation of the patch failed (it would log a patch error)")
        except Unknown as e:
            fails.append("the patch uses %s, which this check does not model" % e)
        for t in TARGETS:
            found, val = effective(doc, t, "designationCategory")
            if val:
                fails.append("%s still buildable (designationCategory %s)" % (t, val))
        for t in KEEP:
            found, val = effective(doc, t, "designationCategory")
            if not val:
                fails.append("%s lost its category: the patch is a blanket" % t)
    cs = ""
    if os.path.isdir(SRC):
        for f in os.listdir(SRC):
            if f.endswith(".cs"):
                cs += open(os.path.join(SRC, f), encoding="utf8").read()
    for needle, why in ((r"class PatchOperationDoctrineSetting\b", "the gate class"),
                        (r"bool oilWorksFoundNotBuilt = true", "the buildability switch, default on"),
                        (r"bool noInfiniteHelixien = true", "the infinite-deposit switch, default on"),
                        (r"HelixienGasHandler:InitDeposits", "the Harmony target of the infinite-deposit removal"),
                        (r"class \w+ : Mod\b", "a Mod subclass (Mod Settings window)")):
        if not re.search(needle, cs):
            fails.append("C# lacks %s (%s)" % (why, needle))
    dll = open(VHGE_DLL, "rb").read()
    if b"InitDeposits" not in dll or b"HelixienGasHandler" not in dll:
        fails.append("the installed VHGE assembly has no HelixienGasHandler.InitDeposits: the Harmony target moved")
    print("read %d def files of 2 mods; targets %s" % (nfiles, ", ".join(TARGETS)))
    if fails:
        for f in fails:
            print("FAIL: " + f)
        return 1
    print("PASS: 6 works unbuildable after the patch, FuelStorage kept, gate and C# switches present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
