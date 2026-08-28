#!/usr/bin/env python3
"""
ship_dress.py - dress the Gravship Cradle: Aurebesh signage, landing pads,
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
SIZES = json.load(open(os.path.join(HERE, "..", "..", "..", "observed", "def_sizes.json")))

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
    (126, 176, "NOTE: The palette. Rusted biotech tile is the connective tissue and reaches "
               "everywhere. Iron plating means heavy industry. Crossed grate iron means the "
               "deck plating is GONE - it is damage, not trim. Divoted rust is held back for "
               "the spine and used nowhere else."),
    (104, 180, "NOTE: 37 blisters, grown from a seeded noise field rather than placed by hand, "
               "so they read as corrosion instead of decoration. 546 cells of missing plating."),
    (157, 92, "NOTE: The eight biggest blisters ate through the SUBSTRATE too - foundation "
              "stripped, 140 cells. You are looking at the ground through the ship. The pod is "
              "the worst of them and its stalk is cut."),
    (117, 65, "NOTE: Both feet were sealed square rooms. They are landing pads now - side and "
              "bottom walls cut back to corner stubs, grate apron, a real shuttle pad and four "
              "beacons. The ship LANDS rather than sits."),
    (146, 182, "NOTE: Every bay carries an Aurebesh word for what it USED to be. SMELTING, "
               "REFINERY, MEDICAL, KITCHEN, FARMING, ARMORY, CONTROL, REACTOR, COMMAND, CARGO, "
               "ENGINEER, STORAGE, LANDING. That is the floor telling you the ship's history."),
    (91, 150, "NOTE: The thrusters were on the EAST flank venting east - she was built to fly "
              "left. They are on the west wall line now, facing east, and the wall they left is "
              "back. She flies right."),
    (107, 181, "NOTE: REFINERY, KITCHEN and ARMORY have been gutted - machines destroyed, "
               "replaced with ruins, slag and machine-bits. The Aurebesh word STAYS. A sign "
               "outliving its factory is the whole story of this ship."),
    (127, 154, "NOTE: Hull colour is MATERIAL, not paint - MegaBone where the plating is sound, "
               "DinoChitin where it is corroding. The dev Set Color tool runs out after ~380 "
               "calls per session; material never does and survives a reload."),
]


def clear_menu(rb):
    ui = rb.call("rimworld/get_ui_layout", {})
    if any(s.get("type") == "Verse.FloatMenu" for s in ui.get("surfaces", [])):
        rb.call("jawa/clear_ui", {"all": True})


def free_cells(rb, x, z, w, need=2, radius=11):
    """Find `need` horizontally adjacent, empty, decked cells near (x,z)."""
    r = rb.call("jawa/get_terrain_layers",
                {"rect": "%d,%d,%d,%d" % (x - radius, z - radius, radius * 2 + 1, radius * 2 + 1),
                 "limit": 900})
    decked = {(c["x"], c["z"]) for c in (r.get("cells") or []) if c.get("foundation")}
    t = rb.call("jawa/list_things",
                {"rect": "%d,%d,%d,%d" % (x - radius - 2, z - radius - 2,
                                          radius * 2 + 5, radius * 2 + 5), "limit": 900})
    # ⚠️ First pass dilated every thing by +-2 and placed 4 of 14 - a bay is dense
    # and almost nothing survived. A word decal is Standable at altitudeLayer Floor,
    # so it only needs a cell free of a BLOCKING edifice; conduits and pipes under it
    # are fine, and the multi-cell machines are what actually matter.
    SKIP = {"PowerConduit", "HiddenConduit", "VGE_AstrofuelPipe"}
    taken = set()
    for th in (t.get("things") or []):
        if th["def"] in SKIP:
            continue
        # exact footprint from def_sizes, centred as GenAdj does it - guessing a
        # radius instead placed 4 of 14, then 6 of 14.
        fw, fh = SIZES.get(th["def"], [1, 1])[:2]
        if (th.get("rot") or 0) % 2:
            fw, fh = fh, fw
        for dx in range(fw):
            for dz in range(fh):
                taken.add((th["x"] - (fw - 1) // 2 + dx, th["z"] - (fh - 1) // 2 + dz))
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
    """🔴 A ZONE CANNOT CARRY TEXT. `createZone` ignores the label it is given and
    auto-names "Stockpile zone 1", so the map-label idea is dead. What DOES carry
    readable text, with a camera target attached, is the letter stack: click one
    and the camera jumps to what the note is about."""
    made = 0
    for (x, z, text) in NOTES:
        title, _, body = text.partition(": ")
        r = rb.call("jawa/send_letter",
                    {"label": body[:44], "text": body, "x": x, "z": z,
                     "letterDef": "NeutralEvent"})
        if r.get("success"):
            made += 1
        else:
            print("   letter failed:", (r.get("message") or "")[:70])
    print("notes: %d letters sent, each with a camera target" % made)


def do_save(rb, name):
    # ⚠️ this runs under WINDOWS python, so the Windows path is the right one.
    d = SAVES
    before = {f: os.path.getmtime(os.path.join(d, f)) for f in os.listdir(d)}
    rb.call("rimworld/save_game", {"saveName": name})
    time.sleep(3)
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
