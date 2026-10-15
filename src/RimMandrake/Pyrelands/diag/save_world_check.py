#!/usr/bin/env python3
"""Offline read of a savegame's WORLD for two Pyrelands GPT-hunt findings (2026-10-15), no game:

  FURNACE_SEED_DIAGNOSE_SHIPPED_SAVE_HERDLESS  WorldComponent_RM_FurnaceHerdSeeder latches `rm_furnaceHerdSeeded` BEFORE its
      gates, so a world first loaded with herds off (or with no Deep Desert tile) never gets a herd. Reads the latch and counts
      RM_FurnaceHerd world objects.
  TRIBES_LOOKUP_DIAGNOSE_FIRST_ONE_FALLS  PyrelandsFactions.TribesOrNull takes the FIRST TribeCivil faction; with one, moot.

    python3 src/RimMandrake/Pyrelands/diag/save_world_check.py [path.rws]     (default: the canonical start save)

Prints one JSON line. `seederPresent` false means the save was written without Pyrelands loaded: nothing latched yet, the
herds seed on the first load that has Pyrelands with furnaceThermalEnabled + furnaceWorldMigrationEnabled on.
Sanity: `worldComponents` and `worldObjects` must be > 0, or the reader is blind and the verdict is UNMEASURED.
"""
import json
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Utils"))
from game_paths import SAVES  # noqa: E402 - the one seam for the LocalLow Saves folder


SAVE_NAME = "CANONICAL_ASHKARR_START_2026-09-12.rws"   # canon.yml planet.start_savegame (owner-ruled 2026-09-12)
SEEDER = "RimMandrake.Pyrelands.WorldComponent_RM_FurnaceHerdSeeder"


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
    if not w["seederPresent"]:
        herd = ("UNMEASURED", "the save was written without Pyrelands loaded (no seeder component): nothing latched; "
                "herds seed on the first load with Pyrelands and both furnace settings on. Re-run on the freeze candidate.")
    elif w["seeded"] == "True" and w["herds"] == 0:
        herd = ("FAIL", "the seeder latched with NO RM_FurnaceHerd on the world: this world never gets furnace herds")
    elif w["herds"] > 0:
        herd = ("PASS", "%d RM_FurnaceHerd world objects" % w["herds"])
    else:
        herd = ("UNMEASURED", "seeder present but not latched (seeded=%r): it seeds on the next load" % w["seeded"])
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
