#!/usr/bin/env python3
"""prove_alloy_forge_offline.py -- SHIP_ALLOY_FORGE_1's offline proof: one verdict per criterion, from files only.

    python3 prove_alloy_forge_offline.py --vfef <VFE Factory mod dir> [--capture <DefDump capture dir>] [--out <file>]

Needs lxml (full XPath, attribute predicates). What it does:
  1. Loads VFE Factory's real 1.6 Defs (the forge ThingDef, its ProcessDefs), our research defs, the Armoury's
     RSW_Durasteel / RSW_Zersium defs, and applies OUR shipped patches to them in load order (WreckedMachines gates,
     Armoury durasteel process, ResearchRetag tab rows): PatchOperationFindMod (VFE Factory counted as loaded),
     Sequence, Conditional, Add (append/prepend), Replace. An unknown op class raises, so nothing is skipped silently.
  2. Reads the patched forge: research gate, process order, the durasteel process's inputs/outputs, research chain.
  3. Mirrors WreckedMachinesPatcher.EarlyForgeCost (C#) on the patched cost. This is a MIRROR of the C# rule, read
     from the same stock list; the live chain alloy_forge_gated/forge_costs_no_advanced_components reads the real one.
  4. With --capture (a DefDump capture of a full load): census of every RecipeDef and PipeSystem.ProcessDef whose
     products include Plasteel / RSW_Durasteel / RSW_Zersium. A capture predates the newest source; the verdict
     names its capture time.
Verdicts: PASS / FAIL / UNMEASURED. Exit 0 only with no FAIL.
"""
import argparse, json, os, sys
from lxml import etree as LX

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", ".."))
ARM = os.path.join(SRC, "RimStarWars", "Armoury")
WM = HERE
RR = os.path.join(SRC, "RimUtinni", "ResearchRetag")
UP = os.path.join(SRC, "RimUtinni", "UtinniPatches")
LOADED_MODS = {"Vanilla Furniture Expanded - Factory"}
PATCHES = [os.path.join(WM, "Patches", "WreckedMachines_AlloyForgeGates.xml"),
           os.path.join(ARM, "Patches", "RSW_AlloyForge_Durasteel.xml"),
           os.path.join(RR, "Patches", "RUT_ResearchTabAssign.xml")]


def _xp(x):
    x = x.strip()
    return x if x.startswith("/") else "/" + x


def apply(op, doc):
    cls = op.get("Class")
    if cls == "PatchOperationFindMod":
        mods = {li.text for li in op.findall("mods/li")}
        branch = op.find("match") if mods <= LOADED_MODS else op.find("nomatch")
        return apply(branch, doc) if branch is not None else True
    if cls == "PatchOperationSequence":
        return all(apply(li, doc) for li in op.findall("operations/li"))
    if cls == "PatchOperationConditional":
        branch = op.find("match") if doc.xpath(_xp(op.findtext("xpath"))) else op.find("nomatch")
        return apply(branch, doc) if branch is not None else True
    nodes = doc.xpath(_xp(op.findtext("xpath")))
    if cls == "PatchOperationAdd":
        prepend = (op.findtext("order") or "Append") == "Prepend"
        for n in nodes:
            kids = [LX.fromstring(LX.tostring(k)) for k in op.find("value")]
            for i, k in enumerate(kids):
                n.insert(i, k) if prepend else n.append(k)
        return bool(nodes)
    if cls == "PatchOperationReplace":
        for n in nodes:
            par = n.getparent(); idx = par.index(n); par.remove(n)
            for i, k in enumerate(op.find("value")):
                par.insert(idx + i, LX.fromstring(LX.tostring(k)))
        return bool(nodes)
    raise ValueError("unsupported patch op %s" % cls)


def load(vfef):
    doc = LX.ElementTree(LX.Element("Defs"))
    root = doc.getroot()
    files = []
    for d in (os.path.join(vfef, "1.6", "Defs"),):
        for dp, _, fs in os.walk(d):
            files += [os.path.join(dp, f) for f in fs if f.endswith(".xml")]
    files += [os.path.join(WM, "Defs", "ResearchProjectDefs", "ResearchProjects_WreckedMachines.xml"),
              os.path.join(ARM, "Defs", "ThingDefs", "RSW_Durasteel.xml"),
              os.path.join(ARM, "Defs", "ThingDefs", "RSW_Zersium.xml")]
    for f in files:
        r = LX.parse(f, LX.XMLParser(remove_comments=True)).getroot()
        if r.tag == "Defs":
            root.extend(list(r))
    for p in PATCHES:
        for op in LX.parse(p, LX.XMLParser(remove_comments=True)).getroot().findall("Operation"):
            apply(op, doc)
    return doc, len(files)


def one(doc, xp):
    r = doc.xpath(xp)
    return r[0] if r else None


def early_cost(cost):
    """Mirror of WreckedMachinesPatcher.EarlyForgeCost: spacer components become industrial ones."""
    out = {k: v for k, v in cost.items() if k != "ComponentSpacer"}
    if cost.get("ComponentSpacer"):
        out["ComponentIndustrial"] = out.get("ComponentIndustrial", 0) + cost["ComponentSpacer"]
    return out


def prereq_chain(doc, name, seen=None):
    seen = set() if seen is None else seen
    for li in doc.xpath('/Defs/ResearchProjectDef[defName="%s"]/prerequisites/li' % name):
        if li.text not in seen:
            seen.add(li.text); prereq_chain(doc, li.text, seen)
    return seen


def census(capture):
    out = {"capture": None, "Plasteel": [], "RSW_Durasteel": [], "RSW_Zersium": []}
    man = json.load(open(os.path.join(capture, "manifest.json")))
    out["capture"] = "%s (%d mods)" % (man.get("capturedUtc"), len(man.get("mods") or []))
    rec = json.load(open(os.path.join(capture, "defs", "RecipeDef.json")))["defs"]
    for d in rec:
        prods = [p.get("thingDef") for p in (d["fields"].get("products") or [])]
        for t in out:
            if t in prods:
                out[t].append("RecipeDef %s [%s] research=%s" % (d["defName"], d.get("packageId"), d["fields"].get("researchPrerequisite")))
    pro = json.load(open(os.path.join(capture, "defs", "ProcessDef.json")))["defs"]
    for d in pro:
        res = [r.get("thing") for r in (d["fields"].get("results") or [])]
        ing = [(i.get("thing"), i.get("countNeeded")) for i in d["fields"].get("ingredients") or []]
        for t in out:
            if t in res:
                out[t].append("ProcessDef %s [%s] %s research=%s" % (d["defName"], d.get("packageId"), ing, d["fields"].get("researchPrerequisites")))
    out["sanity"] = "%d RecipeDefs, %d ProcessDefs read" % (len(rec), len(pro))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vfef", required=True)
    ap.add_argument("--capture")
    ap.add_argument("--out")
    a = ap.parse_args()
    lines, verdicts = [], {}

    def say(s=""):
        lines.append(s)

    def verdict(cid, v, why):
        verdicts[cid] = v
        say("%-3s %-10s %s" % (cid, v, why))

    doc, nfiles = load(a.vfef)
    forge = one(doc, '/Defs/ThingDef[defName="VFEFactory_AutomatedAlloyForge"]')
    say("SHIP_ALLOY_FORGE_1 offline proof; %d def files merged, %d ThingDefs, %d ProcessDefs (sanity probe)" % (
        nfiles, len(doc.xpath("/Defs/ThingDef")), len(doc.xpath("/Defs/PipeSystem.ProcessDef"))))
    if forge is None:
        say("UNMEASURED: VFEFactory_AutomatedAlloyForge not found under %s" % a.vfef)
        print("\n".join(lines)); return 2
    research = [li.text for li in forge.findall("researchPrerequisites/li")]
    procs = [li.text for li in forge.xpath('comps/li[@Class="PipeSystem.CompProperties_AdvancedResourceProcessor"]/processes/li')]
    stock_cost = {c.tag: int(c.text) for c in forge.find("costList")}
    say("forge (patched): researchPrerequisites=%s" % research)
    say("forge (patched): processes, in bill order=%s" % procs)
    say("forge cost: stock %s -> gated (C# mirror) %s" % (stock_cost, early_cost(stock_cost)))
    dura = one(doc, '/Defs/PipeSystem.ProcessDef[defName="RSW_AlloyDurasteel"]')
    plas = one(doc, '/Defs/PipeSystem.ProcessDef[defName="VFEFactory_AlloyPlasteel"]')
    def ings(p):
        return [(i.findtext("thing"), i.findtext("countNeeded")) for i in p.findall("ingredients/li")] if p is not None else None
    def ress(p):
        return [(r.findtext("thing"), r.findtext("count")) for r in p.findall("results/li")] if p is not None else None
    say("RSW_AlloyDurasteel: %s -> %s, research=%s" % (ings(dura), ress(dura), [li.text for li in dura.findall("researchPrerequisites/li")] if dura is not None else None))
    say("VFEFactory_AlloyPlasteel: %s -> %s, research=%s" % (ings(plas), ress(plas), [li.text for li in plas.findall("researchPrerequisites/li")] if plas is not None else None))
    chain = prereq_chain(doc, "RM_WM_PlasteelAlloying")
    say("RM_WM_PlasteelAlloying prerequisite closure (in this file set): %s" % sorted(chain))
    tabs = {n: doc.xpath('string(/Defs/ResearchProjectDef[defName="%s"]/tab)' % n) or "(none: Main)" for n in
            ("RM_WM_AlloyForgeRestoration", "RM_WM_PlasteelAlloying")}
    say("research tabs after RUT_ResearchTabAssign: %s" % tabs)
    zers = one(doc, '/Defs/ThingDef[defName="RSW_Zersium"]')
    rock = one(doc, '/Defs/ThingDef[defName="RSW_MineableZersium"]')
    gs = LX.parse(os.path.join(UP, "Defs", "MapGeneration", "RUT_ZersiumForgeLumps.xml")).getroot()
    biomes = [li.text for li in gs.iter("li") if li.getparent().tag == "allowedBiomes"]
    say("RSW_Zersium description: %s" % (zers.findtext("description") if zers is not None else None))
    say("RSW_MineableZersium: scatter=%s preventMeteorite=%s; deepCommonality on RSW_Zersium=%s; GenStep RUT_ZersiumForgeLumps allowedBiomes=%s" % (
        rock.findtext("building/mineableScatterCommonality"), rock.findtext("building/mineablePreventMeteorite"),
        zers.findtext("deepCommonality") or "(unset = 0)", biomes))
    cen = census(a.capture) if a.capture else None
    if cen:
        say("capture census %s, %s:" % (cen["capture"], cen["sanity"]))
        for t in ("Plasteel", "RSW_Durasteel", "RSW_Zersium"):
            for r in cen[t]:
                say("  %s <- %s" % (t, r))
    say()
    # L1: zersium's home is The Forge, only.
    ok1 = (biomes == ["RM_TheForge"] and rock is not None and rock.findtext("building/mineableScatterCommonality") == "0"
           and rock.findtext("building/mineablePreventMeteorite") == "true" and not zers.findtext("deepCommonality"))
    verdict("L1", "PASS" if ok1 else "FAIL", "zersium placed only by the Forge-gated GenStep (no scatter, no meteorite, no deep deposit)")
    # L2
    ok2 = (zers is not None and one(doc, '/Defs/ThingDef[defName="RSW_Durasteel"]') is not None and dura is not None
           and sorted(t for t, _ in ings(dura)) == ["RSW_Zersium", "Steel"] and ress(dura)[0][0] == "RSW_Durasteel"
           and procs[:1] == ["RSW_AlloyDurasteel"])
    verdict("L2", "PASS" if ok2 else "FAIL", "steel + RSW_Zersium -> RSW_Durasteel is the alloy forge's first process")
    # L3
    fabricated = [r for r in (cen or {}).get("Plasteel", []) if "Slag" not in r and "slag" not in r]
    ok3 = (plas is not None and "VFEFactory_AlloyPlasteel" in procs and "RM_WM_PlasteelAlloying" in [li.text for li in plas.findall("researchPrerequisites/li")]
           and "RM_WM_AlloyForgeRestoration" in chain and not dura.findall("researchPrerequisites/li")
           and procs.index("RSW_AlloyDurasteel") < procs.index("VFEFactory_AlloyPlasteel"))
    if cen is None:
        verdict("L3", "UNMEASURED" if ok3 else "FAIL", "gate order holds; no capture given for the only-route census")
    else:
        only = len(fabricated) == 1 and fabricated[0].startswith("ProcessDef VFEFactory_AlloyPlasteel")
        verdict("L3", "PASS" if ok3 and only else "FAIL",
                "plasteel needs RM_WM_PlasteelAlloying (after the forge's own project; durasteel needs none); fabricated plasteel routes in the capture: %d (%s), the rest are slag re-melt" % (len(fabricated), "; ".join(r.split(" [")[0] for r in fabricated)))
    ok_early = "ComponentSpacer" not in early_cost(stock_cost) and research == ["RM_WM_AlloyForgeRestoration"] \
        and all(v == "RUT_Tree_Workshop" for v in tabs.values())
    verdict("E", "PASS" if ok_early else "FAIL", "the forge is early: gated by the smelter's follow-on, no advanced components, research on the smelter's tab")
    print("\n".join(lines))
    if a.out:
        open(a.out, "w").write("\n".join(lines) + "\n")
    return 1 if "FAIL" in verdicts.values() else 0


if __name__ == "__main__":
    sys.exit(main())
