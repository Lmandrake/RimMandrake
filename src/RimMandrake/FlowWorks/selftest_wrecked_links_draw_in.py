#!/usr/bin/env python3
"""WRECKED_LINKS_FIX_RUINS_SNUB_THEIR_PIPES (owner 2026-11-06: "For wrecked machines, they should ALL draw in the piping and
conduit the same way, not only at a certain value of fixedness."). Reads the SHIPPED XML: every *_Wrecked ThingDef whose higher
tiers take pipes or power carries the matching draw-in tag, and a tagged ruin holds no comp that could join a net. Tiers are
resolved through ParentName and read from Defs and Patches alike. Each rule has its can-fail below.
"""
import copy
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PIPE_TAG, CONDUIT_TAG = "RM_RuinDrawsPipes", "RM_RuinDrawsConduit"
# RM_LiquidNet.RoleOfKind's Machine classes and comps
LIQUID_CLASSES = ("Building_LiquidPump",)
LIQUID_COMPS = ("CompProperties_LiquidPipeAdapter", "CompProperties_LiquidConverter", "CompProperties_LiquidReactor")
TIERS = ("_Kludged", "_Refurbished", "_Repaired", "_Original")


def load_defs(root=ROOT):
    """defName or Name -> element, over every mod's Defs and Patches; a parse failure is a test failure, never a skip."""
    defs = {}
    for path in glob.glob(os.path.join(root, "*", "**", "*.xml"), recursive=True):
        if os.sep + "Defs" + os.sep not in path and os.sep + "Patches" + os.sep not in path:
            continue
        if not re.search(r"ThingDef", open(path, encoding="utf-8", errors="replace").read()):
            continue
        for el in ET.parse(path).getroot().iter("ThingDef"):
            for key in (el.findtext("defName"), el.get("Name")):
                if key:
                    defs[key] = el
    return defs


def chain(defs, el):
    """The def and its ancestors found in this repo, nearest first (a parent outside the repo ends the walk)."""
    out, seen = [], set()
    while el is not None and id(el) not in seen:
        seen.add(id(el))
        out.append(el)
        el = defs.get(el.get("ParentName"))
    return out


def tags(defs, el):
    return {li.text.strip() for a in chain(defs, el) for li in a.findall("building/buildingTags/li") if li.text}


def comp_classes(defs, el):
    return [li.get("Class") or "" for a in chain(defs, el) for li in a.findall("comps/li")]


def takes_power(defs, el):
    return any(c == "CompProperties_Power" for c in comp_classes(defs, el))


def takes_pipes(defs, el):
    if any(any(c.endswith(s) for s in LIQUID_COMPS) for c in comp_classes(defs, el)):
        return True
    return any((a.findtext("thingClass") or "").endswith(LIQUID_CLASSES) for a in chain(defs, el))


def findings(defs):
    """Every broken rule, and the (wrecked, pipes owed, conduit owed) rows it judged."""
    bad, rows = [], []
    for name, el in sorted(defs.items()):
        if not name.endswith("_Wrecked") or el.findtext("defName") != name:
            continue
        stem = name[: -len("_Wrecked")]
        higher = [defs[stem + t] for t in TIERS if stem + t in defs]
        own_power = takes_power(defs, el)
        owe_pipes = any(takes_pipes(defs, h) for h in higher)
        # a ruin with a real power comp (the vanometric cell) already wires up as the game's own connector
        owe_conduit = any(takes_power(defs, h) for h in higher) and not own_power
        rows.append((name, owe_pipes, owe_conduit))
        have = tags(defs, el)
        if owe_pipes and PIPE_TAG not in have:
            bad.append(name + ": its higher tiers take pipes, no " + PIPE_TAG)
        if owe_conduit and CONDUIT_TAG not in have:
            bad.append(name + ": its higher tiers take power, no " + CONDUIT_TAG)
        if PIPE_TAG in have and not owe_pipes:
            bad.append(name + ": " + PIPE_TAG + " but no higher tier takes pipes")
        if CONDUIT_TAG in have and not owe_conduit:
            bad.append(name + ": " + CONDUIT_TAG + " but no higher tier takes power, or it has its own comp")
        if have & {PIPE_TAG, CONDUIT_TAG}:
            if own_power or takes_pipes(defs, el):
                bad.append(name + ": a tagged ruin holds a comp that joins a net")
            if any("CompProperties_Power" in c or "Transmitter" in c for c in comp_classes(defs, el)):
                bad.append(name + ": a tagged ruin carries power")
    return bad, rows


def source_rules():
    """The net never reads the tags; the draw code does. The tag strings match the XML."""
    bad = []
    src = lambda *p: open(os.path.join(ROOT, *p), encoding="utf-8").read()
    joins = src("FlowWorks", "Source", "Machinery", "RM_LiquidJoins.cs")
    net = src("FlowWorks", "Source", "Machinery", "RM_LiquidNet.cs")
    visuals = src("GimmeSomeSlack", "Source", "ConduitVisuals.cs")
    adapter = src("GimmeSomeSlack", "Source", "CordWorldAdapter.cs")
    if 'RuinPipeTag = "%s"' % PIPE_TAG not in joins:
        bad.append("RM_LiquidJoins.RuinPipeTag is not " + PIPE_TAG)
    if 'RuinConduitTag = "%s"' % CONDUIT_TAG not in visuals:
        bad.append("ConduitVisuals.RuinConduitTag is not " + CONDUIT_TAG)
    part = re.search(r"public static Thing PartnerAt.*?\n        }", joins, re.S)
    if not part or "IsPartner(l[i])" not in part.group(0):
        bad.append("PartnerAt does not ask IsPartner, so a tagged ruin draws no pipe")
    role = re.search(r"public static bool IsPartner.*?\n        }", joins, re.S)
    if not role or "IsPipeRuin(t)" not in role.group(0):
        bad.append("IsPartner does not read the ruin tag")
    if "IsPipeRuin" in net or "RuinPipeTag" in net or "RuinDraws" in net:
        bad.append("RM_LiquidNet reads the ruin tag: a ruin would join the liquid net")
    if "AddRuinHookups(map, world, fog);" not in adapter or "HookupPick.PickRuin(world, m)" not in adapter:
        bad.append("the cord snapshot never hooks a ruin")
    return bad


def main():
    defs = load_defs()
    bad, rows = findings(defs)
    bad += source_rules()
    by = {r[0]: r for r in rows}
    # sanity probes: the instrument sees the shipped ladders, or an empty census would pass
    for name, pipes, conduit in (("RM_PumpingStation_Wrecked", True, True), ("RM_DesalPlant_Wrecked", True, True),
                                 ("RM_DetoxWorks_Wrecked", True, True), ("RM_TarRefinery_Wrecked", True, True),
                                 ("RM_WM_Distillation_Wrecked", True, True), ("RM_WM_AutomatedSmelter_Wrecked", False, True),
                                 ("RM_WM_PsychicEmanator_Wrecked", False, True), ("RM_WM_PowerCell_Wrecked", False, False),
                                 ("RM_AncientStasisLocker_Wrecked", False, False)):
        if by.get(name) != (name, pipes, conduit):
            bad.append("census misread %s: %s" % (name, by.get(name)))
    # can-fail: strip the pump's tags from a copy; add a power comp to a copy
    mutant = copy.deepcopy(defs)
    base = mutant["RM_LiquidWorksRuinBase"]
    base.find("building").remove(base.find("building/buildingTags"))
    if not any(s.startswith("RM_PumpingStation_Wrecked:") for s in findings(mutant)[0]):
        bad.append("can-fail: the census passed with the ruin base's tags stripped")
    mutant = copy.deepcopy(defs)
    comps = mutant["RM_PumpingStation_Wrecked"].find("comps")
    ET.SubElement(comps, "li", {"Class": "CompProperties_Power"})
    if not any("carries power" in s for s in findings(mutant)[0]):
        bad.append("can-fail: the census passed with a power comp on a tagged ruin")
    for b in bad:
        print("FAIL " + b)
    print("wrecked_links: %d wrecked defs judged, %d owe pipes, %d owe conduit, %d problems"
          % (len(rows), sum(r[1] for r in rows), sum(r[2] for r in rows), len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
