#!/usr/bin/env python3
"""salvage_lift_policy.py - evaluate the one lift list against building facts.

The list is design/RimMandrake/salvage_lift_policy.json (ordered category rules, first match wins);
the design is design/RimMandrake/salvage_lift_policy_2026-11-01.md. This tool is the reference
evaluator: the game-side pass must agree with `classify` row for row.

  salvage_lift_policy.py --write      rebuild the census from the installed game's Data folder
  salvage_lift_policy.py --summary    counts per category from the committed census
"""
import argparse
import csv
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
POLICY = os.path.join(REPO, "design", "RimMandrake", "salvage_lift_policy.json")
CENSUS = os.path.join(REPO, "design", "RimMandrake", "salvage_lift_census_2026-11-01.csv")
GAME_DATA = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"
PACKS = ["Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey"]
FIELDS = ["defName", "pack", "thingClass", "designation", "minifiedDef", "cells", "flags", "comps", "modExtensions", "hasCost"]
ROUTES = {"minify_reinstall", "scrap_for_yield", "none"}
ACTORS = {"colonist", "colonist_after_claim", "droid", "none"}


def load_policy(path=POLICY):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def cells_of(size_text):
    if not size_text:
        return 1
    nums = re.findall(r"\d+", size_text)
    return int(nums[0]) * int(nums[1])


def facts_from_game(data=GAME_DATA):
    """Every concrete Building ThingDef in Core and the DLCs, ParentName inheritance applied."""
    named, defs = {}, []
    for pack in PACKS:
        files = glob.glob(os.path.join(data, pack, "Defs", "**", "*.xml"), recursive=True)
        if not files:
            raise SystemExit("no Defs under %s/%s" % (data, pack))
        for path in files:
            for node in ET.parse(path).getroot():
                if node.tag != "ThingDef":
                    continue
                if node.get("Name"):
                    named[node.get("Name")] = node
                defs.append((pack, node))

    def chain(node):
        out = [node]
        while out[-1].get("ParentName") in named:
            out.append(named[out[-1].get("ParentName")])
        return out

    def find(node, path):
        for link in chain(node):
            hit = link.find(path)
            if hit is not None:
                return hit
        return None

    def text(node, path):
        hit = find(node, path)
        return hit.text if hit is not None else None

    rows = []
    for pack, node in defs:
        if node.get("Abstract", "").lower() == "true" or node.findtext("defName") is None:
            continue
        if text(node, "category") != "Building":
            continue
        comps = sorted({li.get("Class") for link in chain(node) for li in (link.find("comps") if link.find("comps") is not None else []) if li.get("Class")})
        flags = [name for name, path in (("mineable", "mineable"), ("isNaturalRock", "building/isNaturalRock")) if (text(node, path) or "").lower() == "true"]
        flags += [name for name, path in (("noClaim", "building/claimable"), ("noDeconstruct", "building/deconstructible")) if (text(node, path) or "").lower() == "false"]
        rows.append({
            "defName": node.findtext("defName"), "pack": pack, "thingClass": text(node, "thingClass") or "",
            "designation": text(node, "designationCategory") or "", "minifiedDef": text(node, "minifiedDef") or "",
            "cells": str(cells_of(text(node, "size"))), "flags": ";".join(flags), "comps": ";".join(comps), "modExtensions": "",
            "hasCost": "1" if find(node, "costList") is not None or find(node, "costStuffCount") is not None else "",
        })
    return sorted(rows, key=lambda r: (r["defName"], r["pack"]))


def _clause_hits(clause, row):
    buildable = bool(row["designation"])
    minified = bool(row["minifiedDef"])
    cells = int(row["cells"])
    comps = row["comps"].split(";") if row["comps"] else []
    flags = row["flags"].split(";") if row["flags"] else []
    extensions = row["modExtensions"].split(";") if row["modExtensions"] else []
    name = row["defName"]
    tests = {
        "defName": lambda v: name in v,
        "defName_prefix": lambda v: any(name.startswith(p) for p in v),
        "defName_suffix": lambda v: any(name.endswith(p) for p in v),
        "thingClass_base": lambda v: any(row["thingClass"].startswith(p) for p in v),
        "thingClass_is": lambda v: row["thingClass"] in v,
        "designation": lambda v: row["designation"] in v,
        "comp": lambda v: any(c in comps for c in v),
        "flag": lambda v: any(f in flags for f in v),
        "modExtension": lambda v: any(e in extensions for e in v),
        "buildable": lambda v: buildable == v,
        "has_minified": lambda v: minified == v,
        "max_cells": lambda v: cells <= v,
        "min_cells": lambda v: cells >= v,
    }
    for field, wanted in clause.items():
        if field not in tests:
            raise ValueError("unknown match field " + field)
        if not tests[field](wanted):
            return False
    return True


def classify(row, policy):
    for category in policy["categories"]:
        if any(_clause_hits(clause, row) for clause in category["match"]):
            return category["id"]
    raise ValueError("no category for " + row["defName"])


def read_census(path=CENSUS):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_census(rows, policy, path=CENSUS):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS + ["category"], lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row, category=classify(row, policy)))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    policy = load_policy()
    if args.write:
        write_census(facts_from_game(), policy)
    rows = read_census()
    counts = {}
    for row in rows:
        counts.setdefault(row["category"], []).append(row)
    for category in policy["categories"]:
        got = counts.get(category["id"], [])
        new = sum(1 for r in got if not r["minifiedDef"]) if category["adds_minified"] else 0
        print("%-16s %4d  route=%-16s actor=%-20s adds_minified_to=%d" % (category["id"], len(got), category["route"], category["actor"], new))
    print("total", len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
