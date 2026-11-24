#!/usr/bin/env python3
"""Selftest: def_inventory._merge_into / resolve_inherit agree with the 1.6 engine.

Source of each expected value: Verse/XmlInheritance.cs RecursiveNodeCopyOverwriteElements (1.6.4871), read 2026-11-24.
The Muffalo case pins the comp list of a live capture; it runs only where the Core data folder exists, and says when it
did not run.

    python3 src/RimMandrake/Utils/selftest_def_inventory_merge.py
"""
import copy
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import def_inventory as d  # noqa: E402

FAILS = []


def check(name, got, want):
    ok = got == want
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got %r, want %r" % (got, want)))
    if not ok:
        FAILS.append(name)


def merged(parent, child):
    p = ET.fromstring(parent)
    c = ET.fromstring(child)
    before = ET.tostring(c)
    d._merge_into(c, p)
    check("  (the child node is not changed)", ET.tostring(c), before)
    return p


def lis(node, path="c"):
    return [x.text for x in node.find(path)]


def engine_cases():
    P = "<T><c><li>A</li></c></T>"
    check("a child's li list is appended to the parent's", lis(merged(P, "<T><c><li>B</li></c></T>")), ["A", "B"])
    check("Inherit=False replaces the list", lis(merged(P, '<T><c Inherit="False"><li>B</li></c></T>')), ["B"])
    check("Inherit=false with no items clears the list", lis(merged(P, '<T><c Inherit="false"/></T>')), [])
    check("an empty child keeps the parent's list", lis(merged(P, "<T><c/></T>")), ["A"])
    check("a child that does not declare the list keeps it", lis(merged(P, "<T/>")), ["A"])
    check("an equal item is appended again, not folded", lis(merged(P, "<T><c><li>A</li></c></T>")), ["A", "A"])
    check("a list that only the child has is taken whole", lis(merged("<T/>", "<T><c><li>B</li></c></T>")), ["B"])
    check("a list nested in a named node is appended",
          lis(merged("<T><race><c><li>A</li></c></race></T>", "<T><race><c><li>B</li></c></race></T>"), "race/c"),
          ["A", "B"])
    check("a container declared twice: both lists are appended",
          lis(merged(P, "<T><c><li>B</li></c><c><li>C</li></c></T>")), ["A", "B", "C"])
    check("items with element content are appended whole",
          [x.findtext("k") for x in merged("<T><c><li Class='X'><k>1</k></li></c></T>",
                                           "<T><c><li Class='X'><k>2</k></li></c></T>").find("c")], ["1", "2"])
    check("a named child merges by name, the child's value wins",
          [(x.tag, x.text) for x in merged("<T><s><a>1</a><b>2</b></s></T>", "<T><s><b>3</b><e>4</e></s></T>").find("s")],
          [("a", "1"), ("b", "3"), ("e", "4")])
    check("a field that allows duplicate nodes is appended (forcedTraits)",
          [(x.tag, x.text) for x in merged("<T><forcedTraits><Kind>0</Kind></forcedTraits></T>",
                                           "<T><forcedTraits><Kind>1</Kind></forcedTraits></T>").find("forcedTraits")],
          [("Kind", "0"), ("Kind", "1")])
    m = merged("<T><v>1</v></T>", "<T><v>2</v></T>")
    check("a text leaf is replaced", m.findtext("v"), "2")
    m = merged("<T><v><li>A</li></v></T>", "<T><v>2</v></T>")
    check("text over a list leaves only the text", (m.findtext("v"), len(m.find("v"))), ("2", 0))
    check("an empty child clears a text leaf", merged("<T><v>1</v></T>", "<T><v/></T>").find("v").text, None)
    check("a child node drops the parent node's attributes",
          merged("<T><v Class='X'><a>1</a></v></T>", "<T><v><a>2</a></v></T>").find("v").attrib, {})
    check("Inherit=False keeps the parent node's attributes and adds no Inherit",
          merged("<T><v Class='X'><a>1</a></v></T>", "<T><v Inherit='False' k='1'><a>2</a></v></T>").find("v").attrib,
          {"Class": "X", "k": "1"})


def chain_case():
    """Three levels through resolve_inherit, twice: the cached base is not changed by its first child."""
    gp = ET.fromstring('<T Name="G" Abstract="True"><c><li>G</li></c></T>')
    p = ET.fromstring('<T Name="P" ParentName="G" Abstract="True"><c><li>P</li></c></T>')
    kids = [ET.fromstring('<T ParentName="P"><defName>%s</defName><c><li>%s</li></c></T>' % (k, k)) for k in "xy"]
    by_name, cache = {"G": gp, "P": p}, {}
    raw = copy.deepcopy(gp)
    d.resolve_inherit(p, by_name, cache)
    for k in kids:
        r = d.resolve_inherit(k, by_name, cache)[0]
        check("grandparent, parent and child lists in order (%s)" % k.findtext("defName"),
              lis(r), ["G", "P", k.findtext("defName")])
    check("the indexed base is not changed", ET.tostring(gp), ET.tostring(raw))


# Live reading: capture 2026-11-24T11-26-11Z (314 mods) holds these four Core comps on Muffalo, in this order. Its other
# seven comps come from mods (CombatAI, Improved Workbenches, Pick Up And Haul, Common Sense, AM, Show Me Your Hands).
LIVE_MUFFALO_CORE = ["CompAttachBase", "CompProperties_HoldingPlatformTarget", "CompProperties_Studiable",
                     "CompProperties_Shearable"]


def core_case():
    folder = os.path.join(d.D_DATA, "Core", "Defs", "ThingDefs_Races")
    files = [os.path.join(folder, f) for f in ("Races_Animal_Base.xml", "Races_Animal_CowGroup.xml")]
    if not all(os.path.isfile(f) for f in files):
        print("NOT RUN  Muffalo from the Core data folder: %s is not on this machine" % folder)
        return
    nodes = [n for f in files for n in ET.parse(f).getroot()]
    by_name = {n.get("Name"): n for n in nodes if n.get("Name")}
    muffalo = [n for n in nodes if n.findtext("defName") == "Muffalo" and n.tag == "ThingDef"][0]
    resolved, _, unresolved = d.resolve_inherit(muffalo, by_name, {})
    check("Muffalo's whole chain is found", unresolved, "")
    check("Muffalo has the Core comps of the live capture",
          [(li.get("Class") if li.get("Class") not in (None, "CompProperties") else li.findtext("compClass"))
           .split(".")[-1] for li in resolved.find("comps")], LIVE_MUFFALO_CORE)


def main():
    engine_cases()
    chain_case()
    core_case()
    print("selftest_def_inventory_merge: %s" % ("FAIL (%d): %s" % (len(FAILS), "; ".join(FAILS)) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
