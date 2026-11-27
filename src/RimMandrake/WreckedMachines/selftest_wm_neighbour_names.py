#!/usr/bin/env python3
"""T_NEIGHBOUR_NAMES (tree check C_neighbour_names, rule R_neighbour_names): every name that another mod of this repo reads from
Wrecked Machines still resolves. A patch that matches nothing logs nothing, so each neighbour's patch is counted as applied.

    python3 src/RimMandrake/WreckedMachines/selftest_wm_neighbour_names.py

It reads every .xml (Defs, Patches, About) and .cs file under src/ OUTSIDE this mod's folder, with comments taken out, and this
mod's own Defs, Patches, About.xml and Source.

ROWS
  defs_resolve       every RM_WM_ name a neighbour writes is a def of this mod (a ThingDef, a ResearchProjectDef, ...)
  classes_resolve    every RimMandrake.WreckedMachines.<Class> a neighbour writes is a class of this mod's Source, and every child
                     element the neighbour gives it in XML is a public field of that class
  reflection_holds   what Cold Storage reads by reflection is there: the level extension, its public field `grade`, and the public
                     static method RatioFor that takes a MachineGrade and returns a float; the enum holds the level names used
  patches_land       every def of this mod that a neighbour xpath names is there, and every neighbour operation that the game
                     would take on it (a Conditional goes down the branch its test picks) selects at least one node of this
                     mod's defs (read with lxml on the mod's Defs and the defs its own patches add)
  mod_found          a neighbour that looks for this mod by PatchOperationFindMod or MayRequire uses its real name or packageId

Left out: what a neighbour does with the name in play (its own mod's tests), and names in prose, tests and tooling.
Exit 0 all PASS; 1 a FAIL; 2 COULD NOT LOOK (a file does not parse, or fewer neighbours read than the sanity probe wants), never
a verdict on the mod. Planted faults at the end show each row able to fail.
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

from lxml import etree as LX

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", ".."))
NS = "RimMandrake.WreckedMachines"
ROWS = ("defs_resolve", "classes_resolve", "reflection_holds", "patches_land", "mod_found")
BASE_FIELDS = {"DefModExtension": set(), "PlaceWorker": set(), "CompProperties": {"compClass"}}


class CouldNotLook(Exception):
    pass


def _read(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except OSError as e:
        raise CouldNotLook("%s: %s" % (p, e))


def _no_xml_comments(txt):
    return re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), txt, flags=re.S)


def _no_cs_comments(txt):
    txt = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), txt, flags=re.S)
    return re.sub(r"//[^\n]*", "", txt)


def own(mod=HERE):
    """This mod: (def names, {class: (base, public fields, public static methods)}, {enum: values}, name, packageId, lxml doc)."""
    names, doc = set(), LX.Element("Defs")
    for sub in ("Defs", "Patches"):
        for f in sorted(glob.glob(os.path.join(mod, sub, "**", "*.xml"), recursive=True)):
            try:
                root = LX.fromstring(_no_xml_comments(_read(f)).encode("utf-8"))
            except LX.XMLSyntaxError as e:
                raise CouldNotLook("%s: %s" % (f, e))
            for d in root.iter():
                if d.tag == "defName" and d.text:
                    names.add(d.text.strip())
            if root.tag == "Defs":
                doc.extend(list(root))
            else:                                   # a patch file of ours: the defs it adds whole are defs too
                for v in root.iter("value"):
                    doc.extend([k for k in v if k.find("defName") is not None])
    classes, enums = {}, {}
    for f in glob.glob(os.path.join(mod, "Source", "**", "*.cs"), recursive=True):
        if os.sep + "SelfTest" + os.sep in f or os.sep + "tests" + os.sep in f or os.sep + "obj" + os.sep in f:
            continue
        txt = _no_cs_comments(_read(f))
        for m in re.finditer(r"\b(class|enum)\s+(\w+)(?:\s*:\s*([\w.<>, ]+?))?\s*\{", txt):
            depth, i = 1, m.end()
            while i < len(txt) and depth:
                depth += {"{": 1, "}": -1}.get(txt[i], 0)
                i += 1
            body = txt[m.end():i - 1]
            if m.group(1) == "enum":
                enums[m.group(2)] = [v.split("=")[0].strip() for v in body.split(",") if v.strip()]
                continue
            flat, d = [], 0
            for ch in body:
                d += {"{": 1, "}": -1}.get(ch, 0)
                if d == 0 and ch not in "{}":
                    flat.append(ch)
            flat = "".join(flat)
            fields = set(re.findall(r"\bpublic\s+(?!static\b|const\b|override\b|class\b|enum\b)[\w.<>\[\], ]+?\s+(\w+)\s*(?:=[^;]*)?;", flat))
            statics = dict((n, (ret, args)) for ret, n, args in
                           re.findall(r"\bpublic\s+static\s+([\w.<>\[\]]+)\s+(\w+)\s*\(([^)]*)\)", flat))
            classes[m.group(2)] = ((m.group(3) or "").split(",")[0].strip(), fields, statics)
    about = ET.fromstring(_read(os.path.join(mod, "About", "About.xml")))
    return names, classes, enums, (about.findtext("name") or "").strip(), (about.findtext("packageId") or "").strip(), LX.ElementTree(doc)


def neighbour_files(src=SRC, mod=HERE):
    out = []
    for dp, dn, fs in os.walk(src):
        if os.path.normpath(dp).startswith(os.path.normpath(mod)):
            dn[:] = []
            continue
        dn[:] = [d for d in dn if d not in ("obj", "bin", "Textures", "art_source", "node_modules", "__pycache__")]
        for f in fs:
            if f.endswith((".xml", ".cs")):
                out.append(os.path.join(dp, f))
    return sorted(out)


def _select(doc, xp, rel):
    try:
        return doc.xpath(xp if xp.startswith("/") else "/" + xp)
    except LX.XPathError as e:
        raise CouldNotLook("%s: xpath %s: %s" % (rel, xp, e))


def _walk(op, doc, rel, bad, n):
    """One operation as the game takes it, on this mod's defs as shipped: a Conditional goes down the branch its test picks (a
    branch that is not there does nothing), a Sequence and a FindMod go down their parts, and any other operation whose xpath
    names a def of this mod must select at least one node. Nothing is changed in the defs, so an operation that leans on an
    earlier one of the same file having added its target would read as landing on nothing; none does today."""
    cls = op.get("Class") or ""
    xp = (op.findtext("xpath") or "").strip()
    if cls == "PatchOperationConditional":
        branch = op.find("match") if xp and _select(doc, xp, rel) else op.find("nomatch")
        if branch is not None:
            _walk(branch, doc, rel, bad, n)
    elif cls == "PatchOperationSequence":
        for li in op.findall("operations/li"):
            _walk(li, doc, rel, bad, n)
    elif cls == "PatchOperationFindMod":
        if op.find("match") is not None:
            _walk(op.find("match"), doc, rel, bad, n)
    elif "RM_WM_" in xp:
        n["ops"] = n.get("ops", 0) + 1
        if not _select(doc, xp, rel):
            bad.append("%s: %s on %s lands on nothing in this mod's defs" % (rel, cls.replace("PatchOperation", ""), xp[:150]))


def rows_for(files, names, classes, enums, mod_name, package, doc, src=SRC):
    bad = {r: [] for r in ROWS}
    n = {"files": 0, "defs": 0, "classes": 0, "xpaths": 0, "finds": 0}
    for f in files:
        raw = _read(f)
        if "RM_WM_" not in raw and "WreckedMachines" not in raw and "Wrecked Machines" not in raw and "wreckedmachines" not in raw:
            continue
        rel = os.path.relpath(f, src)
        is_xml = f.endswith(".xml")
        txt = _no_xml_comments(raw) if is_xml else _no_cs_comments(raw)
        if not is_xml:                                   # in C# only what is inside a string literal is a name that is read
            txt = "\n".join(re.findall(r'"((?:[^"\\\n]|\\.)*)"', txt))
        hit = False
        for name in sorted(set(re.findall(r"\bRM_WM_\w+", txt))):
            hit = True
            n["defs"] += 1
            if name not in names:
                bad["defs_resolve"].append("%s names %s, which is no def of this mod" % (rel, name))
        for cls in sorted(set(re.findall(r"\b%s\.(\w+)" % re.escape(NS), txt))):
            hit = True
            n["classes"] += 1
            if cls not in classes:
                bad["classes_resolve"].append("%s names class %s.%s, which is not in this mod's Source" % (rel, NS, cls))
        if is_xml:
            try:
                root = LX.fromstring(txt.encode("utf-8"))
            except LX.XMLSyntaxError as e:
                raise CouldNotLook("%s: %s" % (f, e))
            for node in root.iter():
                cls = (node.get("Class") or "")
                if cls.startswith(NS + ".") and cls.split(".")[-1] in classes:
                    base, fields, _ = classes[cls.split(".")[-1]]
                    for kid in node:
                        if isinstance(kid.tag, str) and kid.tag not in fields | BASE_FIELDS.get(base, set()):
                            bad["classes_resolve"].append("%s gives %s a field %s it does not have" % (rel, cls.split(".")[-1], kid.tag))
                if node.tag == "xpath" and node.text and "RM_WM_" in node.text:
                    # the def that the xpath names must be there, whatever the operation then does with it
                    n["xpaths"] += 1
                    m = re.match(r'(.*?\[defName\s*=\s*"RM_WM_\w+"\])', node.text.strip())
                    if m and not _select(doc, m.group(1), rel):
                        bad["patches_land"].append("%s: %s selects nothing in this mod's defs" % (rel, m.group(1)[:140]))
                if node.tag == "mods" and node.getparent() is not None and node.getparent().get("Class") == "PatchOperationFindMod":
                    for li in node.findall("li"):
                        if li.text and "wreck" in li.text.lower():
                            hit = True
                            n["finds"] += 1
                            if li.text.strip() != mod_name:
                                bad["mod_found"].append("%s looks for the mod %r; its name is %r" % (rel, li.text.strip(), mod_name))
                for att in ("MayRequire", "MayRequireAnyOf"):
                    v = node.get(att) or ""
                    for p in [x.strip() for x in v.split(",") if "wreckedmachines" in x.lower()]:
                        hit = True
                        n["finds"] += 1
                        if p.lower() != package.lower():
                            bad["mod_found"].append("%s has %s=%r; the packageId is %r" % (rel, att, p, package))
            if root.tag == "Patch":
                for op in root.findall("Operation"):
                    _walk(op, doc, rel, bad["patches_land"], n)
        if hit:
            n["files"] += 1
    # what Cold Storage reads by reflection (ColdStorage/Source/ColdStorageStartup.cs): the type, the field `grade`, RatioFor(MachineGrade) -> float
    ext = classes.get("WreckedMachineGrade")
    if ext is None:
        bad["reflection_holds"].append("no class WreckedMachineGrade")
    else:
        if "grade" not in ext[1] or "line" not in ext[1]:
            bad["reflection_holds"].append("WreckedMachineGrade has no public field grade or line (has %s)" % sorted(ext[1]))
        ret, args = ext[2].get("RatioFor", (None, ""))
        if ret != "float" or not re.match(r"\s*MachineGrade\s+\w+\s*$", args or ""):
            bad["reflection_holds"].append("WreckedMachineGrade.RatioFor is %s(%s), want a public static float RatioFor(MachineGrade)" % (ret, args))
    if [v for v in ("Wrecked", "Kludged", "Refurbished", "Original") if v not in enums.get("MachineGrade", [])]:
        bad["reflection_holds"].append("the enum MachineGrade reads %s, the neighbours write Wrecked, Kludged, Refurbished and Original" % enums.get("MachineGrade"))
    return bad, n


def _planted(names, classes, enums, how):
    import copy
    names, classes, enums = set(names), copy.deepcopy(classes), copy.deepcopy(enums)
    name, package = "Wrecked Machines", "mandrake.rm.wreckedmachines"
    if how == "def_renamed":
        names.discard("RM_WM_AncientComponent")
    elif how == "class_gone":
        classes.pop("PlaceWorker_BuildOverLowerGrade", None)
    elif how == "field_renamed":
        b, f, s = classes["WreckedMachineGrade"]
        classes["WreckedMachineGrade"] = (b, (f - {"line"}) | {"machineLine"}, s)
    elif how == "ratio_for_gone":
        b, f, s = classes["WreckedMachineGrade"]
        classes["WreckedMachineGrade"] = (b, f, {})
    elif how == "level_renamed":
        enums["MachineGrade"] = ["Wrecked", "Kludged", "Repaired", "Original"]
    elif how == "mod_renamed":
        name = "Wrecked Machines Reborn"
    return names, classes, enums, name, package


PLANTS = (("def_renamed", "defs_resolve"), ("class_gone", "classes_resolve"), ("field_renamed", "classes_resolve"),
          ("ratio_for_gone", "reflection_holds"), ("level_renamed", "reflection_holds"), ("mod_renamed", "mod_found"),
          ("smelter_levels_gone", "patches_land"))


def main():
    try:
        names, classes, enums, mod_name, package, doc = own()
        files = neighbour_files()
        bad, n = rows_for(files, names, classes, enums, mod_name, package, doc)
        if n["files"] < 4 or n["defs"] < 5 or n["classes"] < 2 or len(names) < 10 or len(classes) < 5:
            raise CouldNotLook("read %d neighbour files that name this mod, %d def names, %d class names; this mod has %d defs and %d "
                               "classes (sanity probe: at least 4, 5, 2, 10, 5)" % (n["files"], n["defs"], n["classes"], len(names), len(classes)))
        blind = []
        for how, want in PLANTS:
            if how == "smelter_levels_gone":
                d2 = LX.ElementTree(LX.fromstring(LX.tostring(doc)))
                for el in d2.xpath('/Defs/ThingDef[starts-with(defName,"RM_WM_AutomatedSmelter_")]'):
                    el.getparent().remove(el)
                b2, _ = rows_for(files, names, classes, enums, mod_name, package, d2)
            else:
                nm, cl, en, mn, pk = _planted(names, classes, enums, how)
                b2, _ = rows_for(files, nm, cl, en, mn, pk, doc)
            if len(b2[want]) <= len(bad[want]):
                blind.append("%s did not turn %s red" % (how, want))
    except CouldNotLook as e:
        print("T_NEIGHBOUR_NAMES: COULD NOT LOOK: %s" % e)
        return 2
    cases = {"defs_resolve": n["defs"], "classes_resolve": n["classes"], "reflection_holds": 3, "patches_land": n["xpaths"], "mod_found": n["finds"]}
    for r in ROWS:
        print("%-17s %-4s worst %d broken, limit 0, %d cases%s" % (r, "PASS" if not bad[r] else "FAIL", len(bad[r]), cases[r],
                                                                 "".join("\n    " + b for b in bad[r][:8])
                                                                 + ("\n    ... %d more" % (len(bad[r]) - 8) if len(bad[r]) > 8 else "")))
    print("planted faults: %d of %d caught%s" % (len(PLANTS) - len(blind), len(PLANTS), "; " + "; ".join(blind) if blind else ""))
    print("read: %d neighbour files name this mod (of %d xml and C# files under src outside it)" % (n["files"], len(files)))
    red = [r for r in ROWS if bad[r]]
    fail = bool(red or blind)
    print("T_NEIGHBOUR_NAMES: %s (%d rows, %d not PASS)" % ("FAIL" if fail else "PASS", len(ROWS), len(red)))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
