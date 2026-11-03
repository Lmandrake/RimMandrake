#!/usr/bin/env python3
"""Selftest for FALL_LINE_MUTATOR_PLACEMENT_1's plan (world/ASHKARR_FALL_LINE_MUTATOR_plan.json).

Proves, offline, against the canonical save the plan names:
- the committed plan rebuilds byte for byte from that save (sha256 recorded);
- it is the 308 tiles the Fall Line spec names (155 "Fall Line" + 153 "The Breaks"), and they are exactly
  the tiles the 2026-08-24 CSV record calls region "Fall Line" / "Fall Line Barrens";
- the start tile 17007 is on it;
- the mutator def exists, and both feature names are in FallLineGate.FeatureNames, so the gate's
  name fallback already holds on this save before the mutator is painted;
- the paint list item carries the plan.
It then feeds the checker broken plans and requires each to be caught, so a green run means it can see.
"""
import copy
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fall_line_mutator_plan as P  # noqa: E402

REPO = P.REPO
GATE_CS = os.path.join(REPO, "src/RimUtinni/FallLineArrivals/Source/FallLineArrivalsMod.cs")
DEF_XML = os.path.join(REPO, "src/RimUtinni/FallLineArrivals/Defs/TileMutatorDefs/RUT_FallLine.xml")
CSV_RECORD = os.path.join(REPO, "world/ASHKARR_VIVIFIED_2026-08-24_tiles.csv")
PAINT_ITEM = os.path.join(REPO, "infrastructure/state/items/BIOME_PAINT_ONCE_AT_THE_END_1.md")
EXPECT = {"Fall Line": 155, "The Breaks": 153}


def gate_names():
    src = open(GATE_CS, encoding="utf-8").read()
    m = re.search(r"FeatureNames\s*=\s*\{([^}]*)\}", src)
    return set(re.findall(r'"([^"]+)"', m.group(1))) if m else set()


def csv_tiles():
    with open(CSV_RECORD, encoding="utf-8") as fh:
        return {int(r["tile"]) for r in csv.DictReader(fh) if r["region"] in ("Fall Line", "Fall Line Barrens")}


def problems(plan, rebuilt, record):
    out = []
    if plan.get("mutator") != P.MUTATOR:
        out.append("mutator is %r, want %s" % (plan.get("mutator"), P.MUTATOR))
    tiles = plan.get("tiles", [])
    if len(tiles) != len(set(tiles)):
        out.append("duplicate tiles")
    if plan.get("count") != len(tiles):
        out.append("count %r != %d listed" % (plan.get("count"), len(tiles)))
    if plan.get("features") != EXPECT:
        out.append("features %r, want %r" % (plan.get("features"), EXPECT))
    if set(tiles) != set(rebuilt["tiles"]):
        out.append("tiles differ from the save's features (%d extra, %d missing)" % (
            len(set(tiles) - set(rebuilt["tiles"])), len(set(rebuilt["tiles"]) - set(tiles))))
    if set(tiles) != record:
        out.append("tiles differ from the CSV record's Fall Line regions")
    if P.START_TILE not in tiles:
        out.append("start tile %d missing" % P.START_TILE)
    return out


def main():
    fails = []
    rebuilt = P.build()
    record = csv_tiles()
    # instrument sanity: the reader sees other features too, so a match is not an artefact of a blind decode
    by_name, ntiles = P.feature_tiles()
    if len(by_name) < 50 or ntiles < 20000:
        fails.append("feature reader looks blind: %d features over %d tiles" % (len(by_name), ntiles))
    if len(record) != 308:
        fails.append("CSV record has %d Fall Line tiles, spec says 308" % len(record))
    try:
        with open(P.PLAN, encoding="utf-8") as fh:
            committed_text = fh.read()
    except OSError as e:
        print("FAIL: %s: %s" % (P.PLAN_REL, e))
        return 1
    if committed_text != P.dumps(rebuilt):
        fails.append("%s does not rebuild byte for byte from %s" % (P.PLAN_REL, P.SAVE_REL))
    import json
    plan = json.loads(committed_text)
    fails += problems(plan, rebuilt, record)
    names = gate_names()
    for n in P.FEATURES:
        if n not in names:
            fails.append("FallLineGate.FeatureNames lacks %r (have %s)" % (n, sorted(names)))
    if "<defName>%s</defName>" % P.MUTATOR not in open(DEF_XML, encoding="utf-8").read():
        fails.append("%s def not found in %s" % (P.MUTATOR, DEF_XML))
    if P.PLAN_REL not in open(PAINT_ITEM, encoding="utf-8").read():
        fails.append("paint list item does not name %s" % P.PLAN_REL)
    # the checker must see breakage
    other = next(t for t in range(ntiles) if t not in set(rebuilt["tiles"]))
    breakers = {
        "dropped tile": lambda p: p["tiles"].pop(),
        "foreign tile": lambda p: p["tiles"].append(other),
        "wrong mutator": lambda p: p.__setitem__("mutator", "RUT_ZeddosYard"),
        "start tile gone": lambda p: p["tiles"].remove(P.START_TILE),
        "duplicate": lambda p: p["tiles"].append(p["tiles"][0]),
    }
    for label, brk in breakers.items():
        bad = copy.deepcopy(plan)
        brk(bad)
        if not problems(bad, rebuilt, record):
            fails.append("checker missed a broken plan: %s" % label)
    if fails:
        for f in fails:
            print("FAIL:", f)
        return 1
    print("PASS: %d tiles %s, start tile %d on it, gate names %s, %d broken plans caught" % (
        plan["count"], plan["features"], P.START_TILE, sorted(names), len(breakers)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
