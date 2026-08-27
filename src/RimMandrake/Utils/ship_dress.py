#!/usr/bin/env python3
"""
ship_dress.py - dress The Helpful Transport: Aurebesh signage, landing pads,
gutted factory bays, and in-map design notes. Run under WINDOWS python.

VERSION 1.0  (2026-08-27)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/

Owner's brief, 2026-08-27, going AFK: "take risks, do interesting unusual things.
Place wreckage and ruin on the vessel to indicate where the beautiful factories
once were. Make the squares on the bottom into landing pads rather than big square
rooms. Keep different save games. You can place text labels in the game."

PHASES, each independently runnable so a save can sit between any two:
  labels   36 Aurebesh word decals exist (Outer Rim). Each is 2x1, Standable,
           altitudeLayer Floor - so it lies ON the deck and pawns walk over it.
           Every bay gets the word for what it USED to be. This is the whole
           "floors tell you what the ship was" idea, in-world and diegetic.
  pads     the two feet stop being rooms: outer walls opened, a real 7x5
           Spaceports_ShuttleLandingPad laid in each, corner beacons, grate lip.
  gut      three bays lose their working machines to ruins and slag. The Aurebesh
           word stays. That contrast IS the story.
  breach   the largest blister eats the hull itself, not just the deck.
  notes    my own out-of-world reasoning, as named ZONES - a zone label renders on
           the map, which is the only text this game will draw where you can read it.

Saving is done by `--save NAME`, which does NOT trust `save_game`'s reported path:
it stats the Saves folder before and after and copies whatever actually changed to
the name asked for. `rimworld/save_game` was measured on 2026-08-24 writing the
CURRENT slot while reporting the requested filename.
"""

import argparse
import collections
import io
import json
import os
import shutil
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rimbridge_client import RimBridge, resolve_endpoint     # noqa: E402

SAVES = ("C:\\Users\\Mandrake\\AppData\\LocalLow\\Ludeon Studios\\"
         "RimWorld by Ludeon Studios\\Saves")
WORD = "OuterRim_AurebeshWord%s"

# bay -> (centre x, centre z, the word for what it used to be, why)
BAYS = [
    (146, 182, "Smelting",  "assembler + alloy forge + neutroamine still stand here"),
    (107, 181, "Refinery",  "smelter, crematorium, biofuel, mincer, masonry saw"),
    (103, 117, "Medical",   "machining bay + medicine granulator"),
    (92, 166, "Kitchen",    "conveyor oven, distillery, cannery - this fed the crew"),
    (159, 166, "Farming",   "drill platform, autofarmer, fishfarm"),
    (89, 134, "Armory",     "autoloom + ammunition press"),
    (130, 150, "Control",   "the pilot console"),
    (127, 154, "Reactor",   "the grav engine chamber"),
    (126, 176, "Command",   "the spine, the one processional axis"),
    (156, 88, "Cargo",      "the pod - and it is eaten out"),
    (92, 150, "Engineer",   "the new stern: thrusters vent west, she flies right"),
    (160, 150, "Storage",   "the old thruster nacelle, walled up again"),
    (117, 66, "Landing",    "west foot"),
    (135, 66, "Landing",    "east foot"),
]

# the three bays that become graves, and what replaces them
GUT = {
    "Refinery": (102, 112, 177, 185),
    "Kitchen": (88, 96, 163, 169),
    "Armory": (85, 93, 131, 138),
}
RUINS = ["AncientCraneBase", "AncientCraneColumn", "AncientDestroyedConsoleLarge",
         "AB_Mech_RuinedAssembler", "AncientBox_SteelSlag", "AncientPallet_SteelSlag",
         "AM_DamagedEmptyShelves", "AncientForklift", "AncientExcavator",
         "AncientChembarrel", "AncientCratePallet", "AncientTunnelerHusk"]

FEET = [("west", 109, 121, 60, 71), ("east", 132, 141, 60, 71)]

NOTES = [
    (125, 196, "NOTE: rust connects, plate = industry, grate = plating GONE"),
    (100, 190, "NOTE: 37 blisters from noise, not placed by hand"),
    (150, 190, "NOTE: 8 biggest ate through the substrate - you see ground"),
    (95, 62, "NOTE: feet were rooms, now pads - the ship LANDS"),
    (150, 62, "NOTE: Aurebesh names what each bay used to be"),
    (90, 148, "NOTE: thrusters moved west - she flies RIGHT"),
]


def clear_menu(rb):
    ui = rb.call("rimworld/get_ui_layout", {})
    if any(s.get("type") == "Verse.FloatMenu" for s in ui.get("surfaces", [])):
        rb.call("jawa/clear_ui", {"all": True})


def free_cells(rb, x, z, w, need=2, radius=7):
    """Find `need` horizontally adjacent, empty, decked cells near (x,z)."""
    r = rb.call("jawa/get_terrain_layers",
                {"rect": "%d,%d,%d,%d" % (x - radius, z - radius, radius * 2 + 1, radius * 2 + 1),
                 "limit": 900})
    decked = {(c["x"], c["z"]) for c in (r.get("cells") or []) if c.get("foundation")}
    t = rb.call("jawa/list_things",
                {"rect": "%d,%d,%d,%d" % (x - radius - 2, z - radius - 2,
                                          radius * 2 + 5, radius * 2 + 5), "limit": 900})
    taken = set()
    for th in (t.get("things") or []):
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                taken.add((th["x"] + dx, th["y"] if False else th["z"] + dz))
    best = None
    for (cx, cz) in decked:
        run = [(cx + i, cz) for i in range(need)]
        if all(c in decked and c not in taken for c in run):
            d = abs(cx - x) + abs(cz - z)
            if best is None or d < best[0]:
                best = (d, cx, cz)
    return (best[1], best[2]) if best else None


def phase_labels(rb):
    placed, failed = 0, []
    for (x, z, word, why) in BAYS:
        spot = free_cells(rb, x, z, None, need=2)
        if not spot:
            failed.append((word, x, z, "no free 2x1"))
            continue
        r = rb.call("jawa/build_batch",
                    {"ops": "%s:%d,%d" % (WORD % word, spot[0], spot[1]),
                     "faction": "PlayerColony", "readBack": 0})
        if (r.get("placed") or 0) >= 1:
            placed += 1
            print("  %-10s at %d,%d   (%s)" % (word.upper(), spot[0], spot[1], why))
        else:
            failed.append((word, spot[0], spot[1], str(r.get("failed"))[:60]))
    print("labels: %d placed, %d failed %s" % (placed, len(failed), failed[:4]))


def phase_pads(rb):
    for (name, x0, x1, z0, z1) in FEET:
        w, h = x1 - x0 + 1, z1 - z0 + 1
        # open the room: drop the two side walls so it reads as a platform, not a box
        for wx in (x0 - 1, x1 + 1):
            rb.call("jawa/destroy_batch",
                    {"rects": "%d,%d,1,%d" % (wx, z0 + 2, h - 4), "categories": "Building"})
        # grate lip around the edge, plate in the middle
        rb.call("jawa/set_terrain_batch",
                {"ops": "guy762_FloorTiles_XGrate_iron:%d,%d,%d,%d" % (x0, z0, w, h),
                 "layer": "top", "refresh": False})
        rb.call("jawa/set_terrain_batch",
                {"ops": "guy762_FloorTiles_DoomgiverFoorMetal_dark:%d,%d,%d,%d"
                        % (x0 + 2, z0 + 2, w - 4, h - 4), "layer": "top", "refresh": False})
        cx, cz = (x0 + x1) // 2, (z0 + z1) // 2
        r = rb.call("jawa/build_batch",
                    {"ops": "Spaceports_ShuttleLandingPad:%d,%d" % (cx, cz),
                     "faction": "PlayerColony", "readBack": 0})
        print("  %s foot: pad placed %s" % (name, r.get("placed")))
        beacons = ";".join("LandingPadBeacon:%d,%d" % (bx, bz)
                           for bx in (x0 + 1, x1 - 1) for bz in (z0 + 1, z1 - 1))
        r = rb.call("jawa/build_batch",
                    {"ops": beacons, "faction": "PlayerColony", "readBack": 0})
        print("  %s foot: %s corner beacons" % (name, r.get("placed")))


def phase_gut(rb):
    import hashlib
    for word, (x0, x1, z0, z1) in GUT.items():
        rect = "%d,%d,%d,%d" % (x0, z0, x1 - x0 + 1, z1 - z0 + 1)
        keep = rb.call("jawa/list_things", {"rect": rect, "limit": 400})
        machines = [t for t in (keep.get("things") or [])
                    if t["def"].startswith("VFEFactory") or t["def"].startswith("VFE_")]
        r = rb.call("jawa/destroy_batch", {"rects": rect, "categories": "Building"})
        print("  %s: destroyed %d buildings (%d were factory machines)"
              % (word.upper(), r.get("destroyed") or 0, len(machines)))
        ops, n = [], 0
        for i, d in enumerate(RUINS):
            h = int(hashlib.md5((word + d).encode()).hexdigest()[:8], 16)
            px = x0 + 2 + (h % max(1, (x1 - x0 - 3)))
            pz = z0 + 2 + ((h >> 8) % max(1, (z1 - z0 - 3)))
            ops.append("%s:%d,%d" % (d, px, pz))
            n += 1
        r = rb.call("jawa/build_batch",
                    {"ops": ";".join(ops), "faction": "", "readBack": 0})
        print("  %s: %s ruins placed of %d attempted" % (word.upper(), r.get("placed"), n))
        slag = ";".join("ChunkSlagSteel:%d,%d,%d" % (x0 + 1 + (i * 3) % (x1 - x0 - 1),
                                                     z0 + 1 + (i * 5) % (z1 - z0 - 1), 1)
                        for i in range(14))
        rb.call("jawa/spawn_batch", {"ops": slag})
        rb.call("jawa/spawn_batch",
                {"ops": ";".join("Filth_MachineBits:%d,%d,3"
                                 % (x0 + 1 + (i * 2) % (x1 - x0 - 1),
                                    z0 + 1 + (i * 3) % (z1 - z0 - 1)) for i in range(20))})
        # put the word back - the sign outlives the factory, which is the point
        spot = free_cells(rb, (x0 + x1) // 2, (z0 + z1) // 2, None, need=2)
        if spot:
            rb.call("jawa/build_batch", {"ops": "%s:%d,%d" % (WORD % word, spot[0], spot[1]),
                                         "faction": "PlayerColony", "readBack": 0})


def phase_notes(rb):
    made = 0
    for (x, z, text) in NOTES:
        r = rb.call("jawa/map_zones", {"action": "createZone", "zone": text,
                                       "kind": "growing"})
        if not r.get("success"):
            r = rb.call("jawa/map_zones", {"action": "createZone", "zone": text})
        p = rb.call("jawa/map_zones", {"action": "paintZone", "zone": text,
                                       "ops": "%d,%d,2,2" % (x, z)})
        if p.get("success"):
            made += 1
        else:
            print("   note failed:", text[:40], (p.get("message") or "")[:50])
    print("notes: %d zone labels placed" % made)


def do_save(rb, name):
    before = {f: os.path.getmtime(os.path.join(SAVES.replace("C:\\", "/mnt/c/").replace("\\", "/"), f))
              for f in os.listdir(SAVES.replace("C:\\", "/mnt/c/").replace("\\", "/"))}
    rb.call("rimworld/save_game", {"saveName": name})
    time.sleep(2)
    d = SAVES.replace("C:\\", "/mnt/c/").replace("\\", "/")
    after = {f: os.path.getmtime(os.path.join(d, f)) for f in os.listdir(d)}
    changed = [f for f in after if before.get(f) != after[f]]
    print("  save_game touched: %s" % changed)
    target = os.path.join(d, name + ".rws")
    if name + ".rws" in changed:
        print("  -> %s.rws written directly" % name)
        return
    for f in changed:
        if f.endswith(".rws"):
            shutil.copy2(os.path.join(d, f), target)
            print("  -> copied %s to %s.rws (save_game did NOT honour the name)" % (f, name))
            return
    print("  !! nothing changed in the Saves folder; the save did not happen")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", action="append", default=[],
                    choices=["labels", "pads", "gut", "breach", "notes"])
    ap.add_argument("--save")
    ap.add_argument("--shot")
    args = ap.parse_args()
    host, port, token = resolve_endpoint()
    with RimBridge(host, port, token, timeout=900.0) as rb:
        clear_menu(rb)
        for p in args.phase:
            print("== phase %s" % p)
            {"labels": phase_labels, "pads": phase_pads, "gut": phase_gut,
             "notes": phase_notes}[p](rb)
        if args.phase:
            rb.call("jawa/refresh_rect", {"rect": "83,59,86,133"})
            rb.call("jawa/map_commit", {})
        if args.shot:
            rb.call("jawa/clear_ui", {})
            rb.call("rimworld/set_camera_zoom", {"rootSize": 42})
            rb.call("rimworld/jump_camera_to_cell", {"x": 125, "z": 125})
            rb.call("jawa/clear_ui", {})
            print("shot:", rb.call("rimworld/take_screenshot",
                                   {"fileName": args.shot}).get("path"))
        if args.save:
            do_save(rb, args.save)
    return 0


if __name__ == "__main__":
    sys.exit(main())
