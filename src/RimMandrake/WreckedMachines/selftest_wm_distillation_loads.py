#!/usr/bin/env python3
"""T_DISTILLATION_LOADS (tree check C_distillation_loads, bar inv_distillation_module): the distillation machine's patch
still applies to FlowWorks' defs, read offline from the shipped files of both mods.

    python3 src/RimMandrake/WreckedMachines/selftest_wm_distillation_loads.py

The machine is outside the promise of 0.1.0 (rule R_riders): it works as built until its working form moves to FlowWorks. So
this test reads only that the patch still LOADS against FlowWorks as FlowWorks is today:

  finds_flowworks      the patch's one top-level operation is a PatchOperationFindMod that names FlowWorks by the <name> of
                       FlowWorks' own About.xml (a FindMod matches the mod's name, not its packageId)
  adds_three_levels    with FlowWorks loaded the patch's xpath matches and adds exactly the three level defs
  quiet_without        without FlowWorks the patch adds nothing and does not fail (the mod loads clean alone)
  no_collision         no added defName is a def that FlowWorks ships itself (the day the machine moves, this goes red and
                       this patch is deleted)
  classes_resolve      every Class="RimMandrake.FlowWorks..." in the added defs is a class in FlowWorks' Source, and every
                       child element is a public field of that class or of a base the game gives it
  values_resolve       the converter's tier is a value of FlowWorks' enum, and its product is a LiquidDef that FlowWorks ships
  config_rules         FlowWorks' own ConfigErrors rules for the converter hold on each added def (a product for distillsAny,
                       the Rare ticker); read from the def as the patch writes it

Left out, and why: the base game's parent def and textures (BuildingBase, the placeholder texPaths) are the game's files, not
FlowWorks'; whether the machine distills is play, and no bar of 0.1.0 judges it.

Verdicts per row PASS / FAIL. Exit 0 all PASS; 1 a FAIL; 2 COULD NOT LOOK (a file of either mod is missing or unreadable),
which is never a verdict on the patch. The planted faults at the end show each row able to fail: a row that a fault does not
turn red fails the run.
"""
import copy
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
FLOW = os.path.normpath(os.path.join(HERE, "..", "FlowWorks"))
PATCH = os.path.join(HERE, "Patches", "WreckedMachines_DistillationModule.xml")
LEVELS = ("RM_WM_Distillation_Wrecked", "RM_WM_Distillation_Kludged", "RM_WM_Distillation_Repaired")
NS = "RimMandrake.FlowWorks"
CONVERTER = NS + ".Machinery.CompProperties_LiquidConverter"
# Fields the game's own base classes give (Verse.CompProperties, Verse.DefModExtension), read through RimSage 2026-11-27.
BASE_FIELDS = {"CompProperties": {"compClass"}, "DefModExtension": set()}


class CouldNotLook(Exception):
    pass


def _read(path):
    try:
        return open(path, encoding="utf-8").read()
    except OSError as e:
        raise CouldNotLook("%s: %s" % (path, e))


def flowworks_name():
    root = ET.fromstring(_read(os.path.join(FLOW, "About", "About.xml")))
    name = (root.findtext("name") or "").strip()
    if not name:
        raise CouldNotLook("FlowWorks' About.xml holds no <name>")
    return name


def flowworks_defs():
    """(every defName FlowWorks ships -> its element tag), over Defs and the defs its own patches add."""
    out, files = {}, 0
    for sub in ("Defs", "Patches"):
        for dp, _, fs in os.walk(os.path.join(FLOW, sub)):
            for f in fs:
                if not f.endswith(".xml"):
                    continue
                files += 1
                try:
                    root = ET.fromstring(_read(os.path.join(dp, f)))
                except ET.ParseError as e:
                    raise CouldNotLook("%s does not parse: %s" % (os.path.join(dp, f), e))
                for el in root.iter():
                    dn = el.findtext("defName")
                    if dn:
                        out[dn.strip()] = el.tag
    if files < 5 or len(out) < 20:
        raise CouldNotLook("FlowWorks read %d xml files and %d defs: the reader cannot see (sanity probe)" % (files, len(out)))
    return out


def flowworks_classes():
    """namespace.Class -> (base name, set of public instance fields), and enum name -> values; by brace matching on the
    Source files. A reader, not a compiler: it is checked by the sanity probe below and by the planted faults."""
    classes, enums, files = {}, {}, 0
    for dp, _, fs in os.walk(os.path.join(FLOW, "Source")):
        if os.sep + "obj" in dp or os.sep + "bin" in dp:
            continue
        for f in fs:
            if not f.endswith(".cs"):
                continue
            files += 1
            txt = re.sub(r"//[^\n]*", "", _read(os.path.join(dp, f)))
            txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
            ns = (re.search(r"\bnamespace\s+([\w.]+)", txt) or [None, ""])[1]
            for m in re.finditer(r"\b(class|enum)\s+(\w+)(?:\s*:\s*([\w.<>, ]+?))?\s*\{", txt):
                kind, name, base = m.group(1), m.group(2), (m.group(3) or "").split(",")[0].strip()
                depth, i = 1, m.end()
                while i < len(txt) and depth:
                    depth += {"{": 1, "}": -1}.get(txt[i], 0)
                    i += 1
                body = txt[m.end():i - 1]
                if kind == "enum":
                    enums[name] = [v.split("=")[0].strip() for v in body.split(",") if v.strip()]
                    continue
                flat, d = [], 0                      # the class's own level only: no field of a nested type or a method
                for ch in body:
                    if ch == "{":
                        d += 1
                    elif ch == "}":
                        d -= 1
                    elif d == 0:
                        flat.append(ch)
                fields = set(re.findall(r"\bpublic\s+(?!static\b|const\b|override\b|class\b|enum\b)[\w.<>\[\], ]+?\s+(\w+)\s*(?:=[^;]*)?;",
                                        "".join(flat)))
                classes["%s.%s" % (ns, name)] = (base, fields)
    if files < 20 or CONVERTER not in classes:
        raise CouldNotLook("FlowWorks' Source read %d files and %s the converter's properties class (sanity probe)"
                           % (files, "holds" if CONVERTER in classes else "does not hold"))
    return classes, enums


def apply_patch(patch_root, loaded_mods):
    """The defs the patch adds under <Defs> with `loaded_mods` in the game, and why it did not apply (None when it did)."""
    ops = patch_root.findall("Operation")
    added = []
    for op in ops:
        if op.get("Class") != "PatchOperationFindMod":
            return added, "top-level operation %s is not a PatchOperationFindMod" % op.get("Class")
        mods = {(li.text or "").strip() for li in op.findall("mods/li")}
        if not mods & loaded_mods:              # the game's rule: any one of the names loaded takes the match branch
            continue
        match = op.find("match")
        if match is None or match.get("Class") != "PatchOperationAdd":
            return added, "the match branch is %s, not a PatchOperationAdd" % (None if match is None else match.get("Class"))
        if (match.findtext("xpath") or "").strip().strip("/") != "Defs":
            return added, "the add's xpath %r does not select <Defs>" % match.findtext("xpath")
        value = match.find("value")
        added += [] if value is None else list(value)
    return added, None


def rows_for(patch_root, name, shipped, classes, enums):
    """One (row, ok, detail) per rule, plus the counts read."""
    rows, n = [], {"defs": 0, "classes": 0, "fields": 0, "values": 0}
    ops = patch_root.findall("Operation")
    mods = [(li.text or "").strip() for op in ops for li in op.findall("mods/li")]
    ok = len(ops) == 1 and ops[0].get("Class") == "PatchOperationFindMod" and mods == [name]
    rows.append(("finds_flowworks", ok, "FindMod names %s; FlowWorks' About.xml says %r" % (mods, name)))
    added, why = apply_patch(patch_root, {name})
    names = [d.findtext("defName") for d in added]
    n["defs"] = len(added)
    rows.append(("adds_three_levels", why is None and sorted(names) == sorted(LEVELS),
                 why or "added %s, want %s" % (names, list(LEVELS))))
    quiet, why2 = apply_patch(patch_root, {"Core"})
    rows.append(("quiet_without", why2 is None and not quiet, why2 or "adds %d defs without FlowWorks" % len(quiet)))
    hit = sorted(d for d in names if d in shipped)
    rows.append(("no_collision", not hit, "FlowWorks ships %s itself" % hit if hit else "none of %d names in FlowWorks' %d defs"
                 % (len(names), len(shipped))))
    bad_c, bad_v, bad_r = [], [], []
    for d in added:
        dn = d.findtext("defName")
        for node in d.iter():
            cls = node.get("Class") or ""
            if not cls.startswith(NS + "."):
                continue
            n["classes"] += 1
            if cls not in classes:
                bad_c.append("%s: class %s is not in FlowWorks' Source" % (dn, cls))
                continue
            base, fields = classes[cls]
            known = fields | BASE_FIELDS.get(base, set())
            for kid in node:
                n["fields"] += 1
                if kid.tag not in known:
                    bad_c.append("%s: %s has no public field %s" % (dn, cls.rsplit(".", 1)[1], kid.tag))
            if cls == CONVERTER:
                n["values"] += 2
                tier, product = (node.findtext("tier") or "").strip(), (node.findtext("distillProduct") or "").strip()
                if tier and tier not in enums.get("LiquidConversionTier", []):
                    bad_v.append("%s: tier %r is not one of %s" % (dn, tier, enums.get("LiquidConversionTier")))
                if product and "LiquidDef" not in shipped.get(product, ""):
                    bad_v.append("%s: distillProduct %r is %s in FlowWorks" % (dn, product, shipped.get(product) or "no def"))
                distills = (node.findtext("distillsAny") or "").strip() == "true"
                if not distills and node.find("processes/li") is None:
                    bad_r.append("%s: no processes and not distillsAny" % dn)
                if distills and not product:
                    bad_r.append("%s: distillsAny with no distillProduct" % dn)
                if (d.findtext("tickerType") or "").strip() != "Rare":
                    bad_r.append("%s: tickerType %r, the converter works on the Rare tick" % (dn, d.findtext("tickerType")))
    rows.append(("classes_resolve", n["classes"] > 0 and not bad_c,
                 "; ".join(bad_c) or "%d class references, %d fields" % (n["classes"], n["fields"])))
    rows.append(("values_resolve", n["values"] > 0 and not bad_v, "; ".join(bad_v) or "%d values" % n["values"]))
    rows.append(("config_rules", n["values"] > 0 and not bad_r, "; ".join(bad_r) or "%d converters" % (n["values"] // 2)))
    return rows, n


def _plant(root, how):
    r = copy.deepcopy(root)
    conv = [x for x in r.iter() if x.get("Class") == CONVERTER]
    kl = [d for d in r.iter("ThingDef") if d.findtext("defName") == LEVELS[1]][0]
    if how == "mod_name":
        r.find("Operation/mods/li").text = "FlowWorks"
    elif how == "drop_level":
        val = r.find("Operation/match/value")
        val.remove(val[0])
    elif how == "collision":
        return r, {LEVELS[2]: "ThingDef"}
    elif how == "class":
        conv[0].set("Class", NS + ".Machinery.CompProperties_LiquidConvertor")
    elif how == "field":
        ET.SubElement(conv[0], "litresPerHour").text = "10"
    elif how == "tier":
        conv[0].find("tier").text = "Kludged"
    elif how == "product":
        conv[0].find("distillProduct").text = "RM_Liquid_PotableWater"
    elif how == "ticker":
        kl.find("tickerType").text = "Normal"
    return r, {}


PLANTS = (("mod_name", "finds_flowworks"), ("drop_level", "adds_three_levels"), ("collision", "no_collision"),
          ("class", "classes_resolve"), ("field", "classes_resolve"), ("tier", "values_resolve"),
          ("product", "values_resolve"), ("ticker", "config_rules"))


def main():
    try:
        name, shipped = flowworks_name(), flowworks_defs()
        classes, enums = flowworks_classes()
        patch_root = ET.fromstring(_read(PATCH))
    except (CouldNotLook, ET.ParseError) as e:
        print("T_DISTILLATION_LOADS: COULD NOT LOOK: %s" % e)
        return 2
    rows, n = rows_for(patch_root, name, shipped, classes, enums)
    for row, ok, detail in rows:
        print("%-18s %-4s %s" % (row, "PASS" if ok else "FAIL", detail))
    bad = [r for r, ok, _ in rows if not ok]
    blind = []
    for how, want in PLANTS:
        planted, extra = _plant(patch_root, how)
        prow, _ = rows_for(planted, name, dict(shipped, **extra), classes, enums)
        if dict((r, ok) for r, ok, _ in prow)[want]:
            blind.append("%s did not turn %s red" % (how, want))
    print("planted faults: %d of %d caught%s" % (len(PLANTS) - len(blind), len(PLANTS), "; " + "; ".join(blind) if blind else ""))
    print("read: FlowWorks %d defs, %d classes; the patch adds %d defs with %d FlowWorks class references and %d fields"
          % (len(shipped), len(classes), n["defs"], n["classes"], n["fields"]))
    fail = bool(bad or blind)
    print("T_DISTILLATION_LOADS: %s (%d rows, %d not PASS)" % ("FAIL" if fail else "PASS", len(rows), len(bad)))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
