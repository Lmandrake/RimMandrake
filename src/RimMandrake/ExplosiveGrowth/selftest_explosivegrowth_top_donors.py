#!/usr/bin/env python3
"""Every top chain in validation.py fires a plant whose ROSTER ROW carries that top (EGROWTH_TINDER_HAY_PROVE_COMES_UP_EMPTY).

    python3 src/RimMandrake/ExplosiveGrowth/selftest_explosivegrowth_top_donors.py

The 2026-10-22 northstar run read `tinder_leaves_fuel` FAIL (Hay=0): the chain fired RM_FE_Plant_Quickgrass, whose row
has been top=Churn since the 2026-10-16 C3 ruling, so RM_TopResolver never reached Burst(tinder: true). This pins
validation.TOP_DONORS to the shipped rosters: each name is a non-tree ThingDef in src/ with a roster row of exactly that
top, every _top_chain call names a TOP_DONORS key, and an empty list is allowed only while no non-tree row of that top
exists. A built-in control runs the same check on the pre-fix donor and must FAIL.
"""
import ast
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(REPO, "src")
VALIDATION = os.path.join(HERE, "validation.py")
ROSTER_TAG = "RimMandrake.ExplosiveGrowth.RM_ExplosiveGrowthRosterDef"
fails = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        fails.append(name)


def xml_files():
    for root, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in (".git", "Textures", "Assemblies")]
        for f in files:
            if f.endswith(".xml"):
                yield os.path.join(root, f)


def load_xml():
    """-> (rows {plant: set(tops)}, thingdefs {defName: [Element]}) over every Defs XML in src/."""
    rows, defs = {}, {}
    for p in xml_files():
        try:
            with open(p, encoding="utf-8-sig") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        if ROSTER_TAG not in text and "<ThingDef" not in text:
            continue
        try:
            root = ET.fromstring(text)
        except ET.ParseError:
            continue
        if root.tag != "Defs":
            continue
        for el in root:
            if el.tag == ROSTER_TAG:
                for li in el.findall("./plants/li"):
                    plant, top = li.findtext("plant"), li.findtext("top")
                    if plant and top:
                        rows.setdefault(plant.strip(), set()).add(top.strip())
            elif el.tag == "ThingDef" and el.findtext("defName"):
                defs.setdefault(el.findtext("defName").strip(), []).append(el)
    return rows, defs


def is_tree(els):
    for el in els:
        if el.find("./plant/treeCategory") is not None or "Tree" in (el.get("ParentName") or ""):
            return True
    return False


def donor_errors(donors, rows, defs):
    """Every reason `donors` ({top: names}) is wrong against the rosters and defs; [] when right."""
    errs = []
    for top, names in donors.items():
        for n in names:
            if n not in defs:
                errs.append("%s: %s has no ThingDef in src/" % (top, n))
            elif is_tree(defs[n]):
                errs.append("%s: %s is a tree (its forced top is TreeBurst)" % (top, n))
            if rows.get(n) != {top}:
                errs.append("%s: %s's roster top is %s" % (top, n, sorted(rows.get(n, ())) or "absent"))
        if not names:
            live = [p for p, tops in rows.items() if top in tops and p in defs and not is_tree(defs[p])]
            if live:
                errs.append("%s: list is empty but non-tree rows exist: %s" % (top, ", ".join(sorted(live))))
    return errs


def parse_validation():
    tree = ast.parse(open(VALIDATION, encoding="utf-8").read())
    donors, chain_tops, literal_places = None, [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(x, ast.Name) and x.id == "TOP_DONORS" for x in node.targets):
            donors = ast.literal_eval(node.value)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "_top_chain" and len(node.args) >= 4:
                a = node.args[3]
                chain_tops.append(a.value if isinstance(a, ast.Constant) else ast.dump(a))
            if node.func.id in ("_place", "_top_donor") and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                literal_places.append((node.func.id, node.args[1].value, node.lineno))
    return donors, chain_tops, literal_places


def main():
    rows, defs = load_xml()
    check("sanity: the rosters parse (rows found)", len(rows) >= 20, len(rows))
    check("sanity: ScorchFruit is a Tinder row", rows.get("RM_FE_Plant_ScorchFruit") == {"Tinder"},
          rows.get("RM_FE_Plant_ScorchFruit"))
    check("sanity: Quickgrass is a Churn row", rows.get("RM_FE_Plant_Quickgrass") == {"Churn"},
          rows.get("RM_FE_Plant_Quickgrass"))
    donors, chain_tops, literal_places = parse_validation()
    check("validation.py defines TOP_DONORS", isinstance(donors, dict), donors)
    if not isinstance(donors, dict):
        return 1
    check("TOP_DONORS covers the five own-odds tops", set(donors) == {"Burst", "Tinder", "Slime", "Rupture", "Flush"},
          sorted(donors))
    errs = donor_errors(donors, rows, defs)
    check("every TOP_DONORS name is a non-tree row of its own top", not errs, "; ".join(errs))
    check("the Tinder chain's donor is RM_FE_Plant_ScorchFruit", tuple(donors.get("Tinder", ()))[:1] == ("RM_FE_Plant_ScorchFruit",),
          donors.get("Tinder"))
    check("five _top_chain calls, each naming a TOP_DONORS key", len(chain_tops) == 5 and all(c in donors for c in chain_tops),
          chain_tops)
    placed = [p for p in literal_places if p[0] == "_place" and p[1] in rows]
    check("no chain places a hard-coded roster plant", not placed, placed)
    control = donor_errors({"Tinder": ("RM_FE_Plant_Quickgrass",)}, rows, defs)
    check("control: the pre-fix Tinder donor (Quickgrass) is refused", bool(control), control)
    print("%d check(s) failed" % len(fails) if fails else "ALL PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
