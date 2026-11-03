#!/usr/bin/env python3
"""FALL_LINE_MUTATOR_PLACEMENT_1: the tile list that gets the RUT_FallLine mutator at the final painting.

The Fall Line is two named world features on the canonical save: "Fall Line" and "The Breaks" (the old
CSV calls the second one "Fall Line Barrens"). The tiles that get the mutator are every surface tile whose
tileFeature value is the uniqueID of one of those two features. The plan is rebuilt from the save, so the
tile list cannot drift from it.

Only BIOME_PAINT_ONCE_AT_THE_END_1 writes this to the planet. This script never writes a save.

    python3 src/RimMandrake/Utils/fall_line_mutator_plan.py           # print a summary
    python3 src/RimMandrake/Utils/fall_line_mutator_plan.py --write   # write the plan
    python3 src/RimMandrake/Utils/fall_line_mutator_plan.py --check   # exit 1 unless the committed plan matches
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import worldmap  # noqa: E402

SAVE_REL = "world/ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws"
SAVE = os.path.join(REPO, SAVE_REL)
PLAN_REL = "world/ASHKARR_FALL_LINE_MUTATOR_plan.json"
PLAN = os.path.join(REPO, PLAN_REL)
MUTATOR = "RUT_FallLine"
FEATURES = ("Fall Line", "The Breaks")
START_TILE = 17007
NONE = 0xFFFF


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def feature_tiles(save=SAVE):
    """{feature name: sorted tile ids} for every named feature, joined on uniqueID (never list position)."""
    grid = worldmap.WorldGrid(save)
    objs = worldmap.WorldObjects(save)
    name_by_uid = {f["uid"]: f["name"] for f in objs.features()}
    out = {}
    for t, v in enumerate(grid.arrays["tileFeature"]):
        if v != NONE:
            out.setdefault(name_by_uid.get(v, "<uid %d unnamed>" % v), []).append(t)
    return out, grid.tiles


def build(save=SAVE, save_rel=SAVE_REL):
    by_name, ntiles = feature_tiles(save)
    missing = [n for n in FEATURES if n not in by_name]
    if missing:
        raise SystemExit("feature(s) %s not on %s" % (missing, save_rel))
    tiles = sorted(t for n in FEATURES for t in by_name[n])
    return {
        "item": "FALL_LINE_MUTATOR_PLACEMENT_1",
        "what": "Every surface tile of the world features %s gets the tile mutator %s." % (
            " and ".join('"%s"' % n for n in FEATURES), MUTATOR),
        "ruling": ("BIOME_PAINT_ONCE_AT_THE_END_1: the planet is painted once, at the end. This list is "
                   "applied then and never as its own pass on the canonical save before that."),
        "inputs": {"save": save_rel, "save_sha256": sha256(save), "surface_tiles": ntiles},
        "mutator": MUTATOR,
        "features": {n: len(by_name[n]) for n in FEATURES},
        "start_tile": START_TILE,
        "start_tile_on_fall_line": START_TILE in tiles,
        "count": len(tiles),
        "tiles": tiles,
        "apply": ("At the terminal world painting (BIOME_PAINT_ONCE_AT_THE_END_1), on the save being painted: "
                  "rebuild with --check first. If that save is a different file, point SAVE at it and --write. "
                  "Then jawa/world_mutators_set {action:add, mutators:%s, tiles:<csv>} in batches, "
                  "jawa/world_commit, and read back with jawa/world_mutators_get (limit<=100 rows per call). "
                  "Never trust the write's return value. Back up the start save first." % MUTATOR),
    }


def dumps(plan):
    return json.dumps(plan, indent=1, sort_keys=True) + "\n"


def main(argv):
    plan = build()
    text = dumps(plan)
    if "--write" in argv:
        with open(PLAN, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print("wrote %s: %d tiles %s" % (PLAN_REL, plan["count"], plan["features"]))
        return 0
    if "--check" in argv:
        try:
            with open(PLAN, encoding="utf-8") as fh:
                have = fh.read()
        except OSError as e:
            print("FAIL: %s unreadable: %s" % (PLAN_REL, e))
            return 1
        if have != text:
            print("FAIL: %s does not match a rebuild from %s" % (PLAN_REL, SAVE_REL))
            return 1
        print("OK: %s matches a rebuild (%d tiles)" % (PLAN_REL, plan["count"]))
        return 0
    print("%d tiles %s, start tile %d on it: %s" % (plan["count"], plan["features"], START_TILE,
                                                    plan["start_tile_on_fall_line"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
