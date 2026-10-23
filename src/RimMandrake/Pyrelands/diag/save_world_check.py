#!/usr/bin/env python3
"""Offline read of a savegame's WORLD for two Pyrelands GPT-hunt findings (2026-10-15), no game:

  Leftover furnace herds  The furnace-beast world migration was CUT 2026-10-23 (design/RimMandrake/fluff_cuts_2026-10-23.md):
      a save that still holds RM_FurnaceHerd world objects or the old seeder component would log missing-def errors on load.
      Counts both; any found is a FAIL.
  TRIBES_LOOKUP_DIAGNOSE_FIRST_ONE_FALLS  PyrelandsFactions.TribesOrNull takes the FIRST TribeCivil faction; with one, moot.

    python3 src/RimMandrake/Pyrelands/diag/save_world_check.py [path.rws]     (default: the canonical start save)

Prints one JSON line.
Sanity: `worldComponents` and `worldObjects` must be > 0, or the reader is blind and the verdict is UNMEASURED.
"""
import json
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Utils"))
from game_paths import SAVES  # noqa: E402 - the one seam for the LocalLow Saves folder


SAVE_NAME = "CANONICAL_ASHKARR_START_2026-09-12.rws"   # canon.yml planet.start_savegame (owner-ruled 2026-09-12)
SEEDER = "RimMandrake.Pyrelands.WorldComponent_RM_FurnaceHerdSeeder"   # cut 2026-10-23; only its absence is checked


def default_save():
    p = os.path.join(SAVES, SAVE_NAME)
    return p if os.path.exists(p) else None


def read_world(path):
    out = {"save": path, "seederPresent": False, "seeded": None, "herds": 0, "worldObjects": 0,
           "worldComponents": 0, "tribeCivil": []}
    stack = []
    for ev, el in ET.iterparse(path, events=("start", "end")):
        if ev == "start":
            stack.append(el.tag)
            continue
        parent = stack[-2] if len(stack) >= 2 else None
        grand = stack[-3] if len(stack) >= 3 else None
        if el.tag == "li" and parent == "components" and grand == "world":
            out["worldComponents"] += 1
            if el.get("Class") == SEEDER:
                out["seederPresent"] = True
                out["seeded"] = (el.findtext("rm_furnaceHerdSeeded") or "False").strip()
        elif el.tag == "li" and parent == "worldObjects":
            out["worldObjects"] += 1
            if (el.findtext("def") or "").strip() == "RM_FurnaceHerd":
                out["herds"] += 1
        elif el.tag == "li" and parent == "allFactions":
            if (el.findtext("def") or "").strip() == "TribeCivil":
                out["tribeCivil"].append({"name": el.findtext("name"), "loadID": el.findtext("loadID"),
                                          "defeated": (el.findtext("defeated") or "False").strip()})
            el.clear()
        if el.tag in ("thing", "map", "maps"):
            el.clear()
        stack.pop()
    return out


def verdicts(w):
    """(herd verdict, tribes verdict) as (PASS|FAIL|UNMEASURED, why)."""
    if w["worldComponents"] == 0 or w["worldObjects"] == 0:
        blind = ("UNMEASURED", "reader is blind: %d world components, %d world objects" % (w["worldComponents"], w["worldObjects"]))
        return blind, blind
    if w["seederPresent"] or w["herds"] > 0:
        herd = ("FAIL", "the save still holds the cut furnace-herd world leg (seeder component %s, %d RM_FurnaceHerd objects): "
                "it would log missing-def errors on load" % (w["seederPresent"], w["herds"]))
    else:
        herd = ("PASS", "no furnace-herd seeder or RM_FurnaceHerd world object in the save")
    alive = [f for f in w["tribeCivil"] if f["defeated"] != "True"]
    if len(w["tribeCivil"]) <= 1:
        tribes = ("PASS", "%d TribeCivil faction(s): the first-one lookup is moot" % len(w["tribeCivil"]))
    elif w["tribeCivil"][0]["defeated"] == "True" and alive:
        tribes = ("FAIL", "the FIRST TribeCivil faction is defeated while %d survive: TribesOrNull returns null" % len(alive))
    else:
        tribes = ("UNMEASURED", "%d TribeCivil factions: latent until the first is defeated" % len(w["tribeCivil"]))
    return herd, tribes


def main(argv):
    path = argv[0] if argv else default_save()
    if not path or not os.path.exists(path):
        print(json.dumps({"error": "save not found", "path": path}))
        return 2
    w = read_world(path)
    h, tr = verdicts(w)
    w["herdVerdict"], w["tribesVerdict"] = list(h), list(tr)
    print(json.dumps(w))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
