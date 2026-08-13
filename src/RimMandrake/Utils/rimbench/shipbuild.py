#!/usr/bin/env python3
"""shipbuild.py — turn the LOCKED #15 hull into a tile-by-tile build sheet.

WHAT THIS IS FOR
================
`ship_deck_plan.md:143` names the next deliverable: *"the tile-level interior
blueprint drawn on #15."* This produces it, from the design that is already
locked and already verified — it does not re-design anything.

Three outputs, one source of truth:

  ship_tiles.json    every occupied tile: x, z, zone, foundation, terrain, things
  ship_build.md      a human-readable build order for authoring by hand in game
  ship_bridge.json   batched op strings for jawa/set_terrain_batch + spawn_batch

PROVENANCE — every number here is reproduced, not retyped
=========================================================
The hull comes from `src/RimMandrake/mapsynth/build_designs.py::d_falcon_halo_hollow`, run
live rather than transcribed. Re-running it reproduces the published figures
exactly, which is the check that the geometry has not drifted:

    total 4,057 tiles      cargo 1,443      factory 1,182 (6 x 197)
    shuttle 420            8 extenders      100% coverage, parts=1

Machine placement comes from `src/RimMandrake/mapsynth/runs/build_sheet_15.json` (91 elements:
18 machines, 51 hoppers, 8 heatsinks, 6 aprons, 6 belt stubs, 2 boosters).
**Verified to share the grid's coordinate space** — all 18 machine rects land on
tiles whose zone code equals their own wing letter, 0 misaligned.

DEF VOCABULARY — harvested, not remembered
==========================================
Every defName below was read out of the Gravship Exporter's own shipped example
(`3576790938/1.6/Defs/Advanced_Starter_Ship.xml`, 4,816 lines). That file is the
authority on what a valid exported ship may contain, because the mod wrote it.

    foundationDef   Substructure (the ONLY value, on all 354 of its cells)
    terrainDef      MetalTile, SterileTile, WoodPlankFloor, CarpetMarine
    things          GravshipHull, HiddenConduit, PowerConduit, PilotConsole,
                    SmallThruster, ChemfuelTank, Battery, Autodoor, ... (35 total)
    stuffDef        Steel, Cloth, WoodLog, BlocksMarble

⚠️ THE EXPORT IS ANCHORED ON THE GRAV ENGINE — read from the mod's assembly
string table, not guessed: "ExportV2: Starting BuildLayout for engine at {0}" and
"engine was null. Aborting export." That is why no `GravEngine` appears among the
example's 35 defs: a ship does not carry its own anchor. BUILD THE ENGINE BEFORE
EXPORTING.

`Extender` appears nowhere in the assembly in either encoding, so extenders get
no special-casing and are ordinary buildings that should ride along — INFERENCE,
not proof. The five-minute test (small ship, one extender, re-import) still comes
first. Full reasoning in `ship_build.md` §Read this before you build.

⚠️ THE GRID IS DESIGN SPACE, NOT MAP SPACE — and the two were silently equated
until 2026-08-13. The hull runs x 1-86, z 1-133 because that is where the
generator drew it. `jawa/spawn_batch` and `jawa/set_terrain_batch` read their
cells as ABSOLUTE map coordinates, so emitting the grid raw builds the ship hard
against the map's south-west corner, touching the edge on two sides. Nothing
chose that placement; it was the absence of a choice, and it is invisible in the
output because corner coordinates look exactly like intended coordinates.

So `ship_bridge.json` now REFUSES to emit without an explicit origin. Found by
CREATE reading the emitter rather than the output.

USAGE
=====
    python3 src/RimMandrake/Utils/rimbench/shipbuild.py --center 250,250   # centre on the map
    python3 src/RimMandrake/Utils/rimbench/shipbuild.py --origin 82,58     # explicit offset
    python3 src/RimMandrake/Utils/rimbench/shipbuild.py --corner           # edge-anchored, on purpose
    python3 src/RimMandrake/Utils/rimbench/shipbuild.py --selftest         # no game, no writes

The map size is not guessable offline — read it off any companion reply, since
`jawa/get_terrain_batch`, `jawa/set_terrain_batch` and `jawa/spawn_batch` all
return `mapSize {x,z}`.
"""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
MAPS = os.path.join(REPO, "src", "RimMandrake", "mapsynth")
OUT = os.path.join(REPO, "design", "Jawa", "worldbuilding", "ship_build")

# ---------------------------------------------------------------- the legend
# Recovered from build_designs.py (REQUIRED = 'MSUWH' 'ABCDEF' 'G' 'R' 'T')
# plus the keel/causeway codes the #15 generator writes directly.
ZONES = {
    "G": "cargo hold (ring body)",
    "K": "keel — utility spine, REPAIRED FIRST",
    ".": "causeway / consecrated floor",
    "T": "shrine-heart — scrap totem + grav engine seat",
    "M": "command cockpit (offset starboard)",
    "S": "stern — thrusters + main power",
    "U": "fuel bunkerage (port)",
    "W": "water tanks (starboard)",
    "H": "shuttle bay (mandible prong tips)",
    "R": "habitat ring pod",
    "A": "wing A — raw extraction",
    "B": "wing B — bulk/dirty/HOT",
    "C": "wing C — food",
    "D": "wing D — textile/ammo",
    "E": "wing E — advanced materials, HOTTEST",
    "F": "wing F — precision",
}

# zone -> terrainDef. Only the four terrains the exporter's own example uses.
TERRAIN = {
    "G": "MetalTile",
    "K": "MetalTile",
    ".": "MetalTile",
    "T": "CarpetMarine",      # consecrated floor at the shrine-heart
    "M": "SterileTile",       # command
    "S": "MetalTile",
    "U": "MetalTile",
    "W": "MetalTile",
    "H": "MetalTile",
    "R": "WoodPlankFloor",    # habitat reads warm against the metal
    "A": "MetalTile",
    "B": "MetalTile",
    "C": "SterileTile",       # food wing
    "D": "MetalTile",
    "E": "MetalTile",
    "F": "SterileTile",       # precision
}

# Utility runs. The keel is the connection backbone AND the power spine, so it
# carries conduit on every tile; ship_deck_plan.md §2 "keel is repaired first".
#
# WHICH conduit is not a free choice — measured against the exporter's own ship,
# which ships 90 HiddenConduit against 50 PowerConduit, i.e. 64% hidden. That
# split exists for a reason: conduit UNDER a structure has to be the hidden
# variant. An all-PowerConduit keel diverges from the only precedent there is,
# and it is what produced the EXT (45,58) collision — a node landing on a tile
# whose exposed conduit GenSpawn would wipe or refuse.
#
# So the rule is structural, not aesthetic: hidden wherever the tile also carries
# a building, exposed in the open.
KEEL_CONDUIT_OPEN = "PowerConduit"
KEEL_CONDUIT_UNDER = "HiddenConduit"

# Nodes that must not share a cell with exposed conduit. Verified placement for
# the shrine-heart engine seating (100% coverage, 8 extenders, chain-legal).
NODES = [("ENGINE", 45, 92), ("EXT", 45, 58), ("EXT", 55, 30), ("EXT", 45, 114),
         ("EXT", 11, 92), ("EXT", 79, 92), ("EXT", 56, 8), ("EXT", 35, 39),
         ("EXT", 55, 39)]

FOUNDATION = "Substructure"
HULL_WALL = "GravshipHull"
HULL_STUFF = "Steel"

# ------------------------------------------------- the grav nodes, read not guessed
# defNames and sizes READ OUT OF THE GAME on 2026-08-13, from
# Data/Odyssey/Defs/ThingDefs_Buildings/Buildings_Gravship.xml -- not remembered,
# not inferred from the exporter's example (which cannot contain them: the export
# is anchored ON the engine, so a ship never carries its own anchor).
#
#   GravEngine          grav engine          size (3,3)   terrainAffordanceNeeded None
#   GravFieldExtender   grav field extender  size (1,1)   terrainAffordanceNeeded Substructure
#
# ⚠️ THE ENGINE IS 3x3 AND ITS COORDINATE IS THE CENTRE, not a corner. RimWorld
# spawns an odd-sized building centred on its position, so ENGINE at (45,92)
# occupies x 44-46, z 91-93. Emitting it as though the coordinate were a corner
# would shift the whole engine one cell and put it off the seating the design
# verified.
NODE_DEF = {"ENGINE": "GravEngine", "EXT": "GravFieldExtender"}
NODE_SIZE = {"ENGINE": (3, 3), "EXT": (1, 1)}
# populated after node_cells() is defined; see below
NODE_CELLS = set()


def load_grid():
    """The hull, re-run from its generator rather than read from a stale copy."""
    import numpy as np
    npy = os.path.join(MAPS, "design_15_falcon_halo_hollow.npy")
    if not os.path.isfile(npy):
        raise IOError("missing %s — run src/RimMandrake/mapsynth/build_designs.py first" % npy)
    return np.load(npy)


def load_elements():
    p = os.path.join(MAPS, "build_sheet_15.json")
    return json.load(open(p, encoding="utf-8"))["elements"]


# ---------------------------------- the build sheet is PINNED, and here is why
# ⚠️ `build_sheet_15.json` and its generator `build_sheet_15.py` have DIVERGED,
# deliberately, as of 2026-08-13 (CREATE, e95eb26). The generator's orientation
# choice used to fall out of set-iteration order — reproducible but unintentional,
# and not even self-consistent: the wider form won for five machines and the
# taller form for Autofarmer. Making it explicit with sorted() was the right fix
# and it CHANGES the answer: five of the nine non-square machines (Conveyor Oven,
# Cannery, Autoloom, Neutro Synth, Medicine Granulator) are placed 5x3 in the
# committed json, and sorted() picks 3x5.
#
# So for this file the standing "regenerate, never hand-edit" rule is SUSPENDED:
# the json predates the rule, is checked against the deck plan, and is
# authoritative. Regenerating the sheet would silently move five machines and
# change the rotation flags this module emits.
#
# This fingerprint exists so that cannot happen quietly. If it fires, the sheet
# changed — do not update the constant to make the test pass. Re-verify the
# affected machines against the deck plan first, then update it deliberately.
SHEET_SHA256 = "1182c13597ae5bdf24bdb44317fa45f49e5ca0606a2ac4aeed16c0f83aab60da"


def sheet_fingerprint():
    """sha256 over the sheet's ELEMENTS, canonicalised — formatting-independent."""
    import hashlib
    els = json.load(open(os.path.join(MAPS, "build_sheet_15.json"),
                         encoding="utf-8"))["elements"]
    canon = json.dumps(els, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode()).hexdigest()


# Every element type the sheet can contain must be either EMITTED or listed here
# with a reason. Without this, a type the emitter does not recognise is dropped in
# silence -- which is exactly how 8 heatsinks and 2 boosters went missing.
EMITTED_TYPES = {"machine", "hopper", "booster", "heatsink"}
NOT_EMITTED = {
    "apron": "floor area, not a building — the tiles get terrain, nothing spawns",
    "belt_stub": "conveyor stubs; VFEFactory_Conveyor exists but the sheet does "
                 "not say which way each stub runs, and a conveyor placed at the "
                 "wrong facing is worse than none. CREATE's call, not mine.",
}


def load_machine_decl():
    """Declared (w, h) per machine, parsed from build_sheet_15.py's MACHINES.

    Read from the source that produced the placements rather than retyped, so a
    change there cannot silently desync the rotation derivation below.
    """
    import re
    src = open(os.path.join(MAPS, "build_sheet_15.py"), encoding="utf-8").read()
    m = re.search(r"MACHINES\s*=\s*\{(.*?)\n\}", src, re.S)
    if not m:
        return {}
    return {g.group(1): (int(g.group(2)), int(g.group(3)))
            for g in re.finditer(r"\('([^']+)',(\d+),(\d+),(\d+)\)", m.group(1))}


MACHINE_DECL = load_machine_decl()

# ------------------------------------------------- build-sheet label -> defName
# RESOLVED OFFLINE from Vanilla Factions Expanded — Factory's own ThingDefs
# (workshop 3686924415, packageId vanillaexpanded.vfefactory, ACTIVE in
# ModsConfig). The build sheet names machines by human label; these are the real
# defNames, read out of the mod rather than guessed.
#
# The mapping is not a straight lowercase match — VFE labels most of them
# "automated <thing>" while the sheet says "<thing>", and two are irregular:
# Crematorium is labelled "conveyor crematorium", and Neutro Synth is
# "neutroamine synthesizer".
#
# ⚠️ RESOLVED, NOT LIVE-VERIFIED. Reading a defName out of a mod's XML proves the
# def is DECLARED, not that it REGISTERED — a failed load, a LoadFolders quirk or
# a later patch could still remove it. That is a weaker claim than jawa/get_def
# against the running game, and the difference is exactly the kind this project
# keeps getting caught by. Confirm on the next live session; until then treat
# these as high-confidence rather than proven.
MACHINE_DEFS = {
    "Autofarmer": "VFEFactory_Autofarmer",
    "Drill Platform": "VFEFactory_AutomatedDrillPlatform",
    "Fishfarm": "VFEFactory_AutomatedFishfarm",
    "Smelter": "VFEFactory_AutomatedSmelter",
    "Masonry Saw": "VFEFactory_AutomatedMasonrySaw",
    "Mincer": "VFEFactory_AutomatedMincer",
    "Crematorium": "VFEFactory_AutomatedCrematorium",
    "Biofuel Refinery": "VFEFactory_AutomatedBiofuelRefinery",
    "Conveyor Oven": "VFEFactory_ConveyorOven",
    "Cannery": "VFEFactory_AutomatedCannery",
    "Distillery": "VFEFactory_AutomatedDistillery",
    "Autoloom": "VFEFactory_Autoloom",
    "Ammo Press": "VFEFactory_AutomatedAmmunitionPress",
    "Assembler": "VFEFactory_AutomatedAssembler",
    "Alloy Forge": "VFEFactory_AutomatedAlloyForge",
    "Neutro Synth": "VFEFactory_NeutroamineSynthesizer",
    "Medicine Granulator": "VFEFactory_MedicineGranulator",
    "Machining Bay": "VFEFactory_AutomatedMachiningBay",
    # support furniture the build sheet places by type rather than by name
    "hopper": "VFEFactory_FactoryHopper",
    "heatsink": "VFEFactory_Heatsink",
    "booster": "VFEFactory_Booster",
}


def perimeter(grid):
    """Tiles on the hull boundary — these get GravshipHull walls.

    A tile is boundary if it is occupied and any 4-neighbour is empty or off
    canvas. Deliberately 4-connected, not 8: a diagonal-only neighbour does not
    leave a gap a pawn or the atmosphere can pass through, and counting it would
    thicken every corner into a double wall.
    """
    h, w = grid.shape
    out = set()
    for z in range(h):
        for x in range(w):
            if grid[z, x] == "":
                continue
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, nz = x + dx, z + dz
                if nx < 0 or nz < 0 or nx >= w or nz >= h or grid[nz, nx] == "":
                    out.add((x, z))
                    break
    return out


def build(grid, elements):
    """One dict per occupied tile. This is the deliverable."""
    h, w = grid.shape
    wall = perimeter(grid)

    # machines/hoppers/etc from the build sheet, indexed by tile
    things_at = {}
    footprint = {}
    conflicts = []          # cell -> machine name, so nothing else claims it
    for e in elements:
        t = e.get("type")
        if t == "machine":
            x, z, mw, mh = e["rect"]
            # ROTATION IS RECOVERABLE, and dropping it was the review's top
            # finding. build_sheet_15.py's spaced_pack tries both (w,h) and
            # (h,w), so a placed rect whose dimensions are SWAPPED relative to
            # the declared MACHINES entry is a 90-degree rotation. Three of the
            # eighteen are: Conveyor Oven, Cannery, Autoloom.
            #
            # ⚠️ The footprint cannot distinguish EAST from WEST — both are 90
            # degrees and both give the same rect. So this records "rotated",
            # not a specific Rot4, and says so rather than guessing a facing that
            # would be wrong half the time.
            # ⚠️ ASK THE DEF, NOT THE SHEET. This compared the placed rect against
            # MACHINE_DECL (parsed from build_sheet_15.py) and called Autofarmer
            # "unrotated" — because the sheet's own declaration, (3,7), is the
            # TRANSPOSE of the def's (7,3). Sheet and placement agreed with each
            # other and both disagreed with the game. A cross-check between two
            # numbers from the same source proves consistency, never truth.
            dn_ = MACHINE_DEFS.get(e["name"])
            size = DEF_SIZES.get(dn_) or (MACHINE_DECL.get(e["name"]) or (None,))[0:2]
            size = tuple(size) if size and size[0] else None
            if size and (mw, mh) == (size[1], size[0]) and size[0] != size[1]:
                rot_note = "ROTATED 90 (east or west — footprint cannot tell)"
            elif size and (mw, mh) == size:
                rot_note = "unrotated"
            else:
                rot_note = "rotation unknown (no declared size)"
            for dz in range(mh):
                for dx in range(mw):
                    footprint[(x + dx, z + dz)] = e["name"]
            things_at.setdefault((x, z), []).append(
                {"defName": MACHINE_DEFS.get(e["name"], e["name"]),
                 "label": e["name"],
                 "resolved": e["name"] in MACHINE_DEFS,
                 "note": "machine %dx%d wing %s — %s" % (mw, mh, e["wing"], rot_note),
                 "footprint": [mw, mh]})
        elif t in ("hopper", "booster", "heatsink"):
            # ⚠️ THE SHEET USES TWO SHAPES AND THIS ONLY READ ONE. Hoppers carry
            # `at` (a point); heatsinks and boosters carry `rect` ([x,z,w,h]).
            # Reading only `at` silently dropped ALL 8 heatsinks and BOTH
            # boosters — 10 buildings the design specifies, never emitted, and
            # invisible because they never reached the unresolved-label path
            # either. Found 2026-08-13 by the owner asking whether the plan
            # placed every VFE Factory building; it placed 19 of 26.
            at, rect = e.get("at"), e.get("rect")
            if not at and rect:
                at = [rect[0], rect[1]]
            if at and tuple(at) in footprint:
                # ⚠️ CONFLICT: this support element is anchored on a cell a
                # machine already occupies. Emitting it would spawn one building
                # inside another. Held back and REPORTED rather than emitted --
                # same rule as an unresolved machine label. Surfaced 2026-08-13
                # the moment heatsinks stopped being dropped: 2 of the 8 collide,
                # with Mincer and Neutro Synth. That is a build-sheet defect, not
                # an emitter one, so it is CREATE's to resolve.
                conflicts.append({"type": t, "at": list(at),
                                  "insideMachine": footprint[tuple(at)],
                                  "rect": rect})
            elif at:
                rec = {"defName": MACHINE_DEFS.get(t, t),
                       "label": t,
                       "resolved": t in MACHINE_DEFS,
                       "note": "%s wing %s" % (t, e.get("wing"))}
                # a rect element carries its own footprint, so the corner->centre
                # shift uses the PLACED size exactly as it does for machines
                if rect and len(rect) == 4:
                    rec["footprint"] = [rect[2], rect[3]]
                things_at.setdefault(tuple(at), []).append(rec)
            else:
                raise ValueError(
                    "sheet element %r has neither `at` nor `rect`: %r" % (t, e))

    tiles = []
    for z in range(h):
        for x in range(w):
            code = grid[z, x]
            if code == "":
                continue
            things = []
            if (x, z) in wall:
                things.append({"defName": HULL_WALL, "stuffDef": HULL_STUFF, "rotInteger": 0})
            if code == "K":
                # hidden under anything structural, exposed in the open —
                # and never exposed under a node, which is what collided before
                under = ((x, z) in wall or (x, z) in footprint
                         or (x, z) in NODE_CELLS)
                things.append({"defName": KEEL_CONDUIT_UNDER if under else KEEL_CONDUIT_OPEN,
                               "rotInteger": 0})
            for extra in things_at.get((x, z), []):
                things.append(extra)
            rec = {
                "x": x, "z": z, "zone": code,
                "foundationDef": FOUNDATION,
                "terrainDef": TERRAIN.get(code),
                "things": things,
            }
            if (x, z) in footprint and (x, z) not in things_at:
                # inside a machine's footprint but not its anchor — record it so
                # nothing else claims the cell later
                rec["occupiedBy"] = footprint[(x, z)]
            tiles.append(rec)
    build.conflicts = conflicts
    return tiles, wall


def rects_from(cells):
    """Greedy maximal-row-run rectangles — an EXACT COVER, no overlap.

    Same decomposition the terrain generator uses, and the same reason: cost on
    the bridge tracks CALLS, not cells, so the op string wants runs not points.
    """
    todo = set(cells)
    out = []
    for (x, z) in sorted(todo, key=lambda c: (c[1], c[0])):
        if (x, z) not in todo:
            continue
        wlen = 0
        while (x + wlen, z) in todo:
            wlen += 1
        hgt = 1
        while all((x + i, z + hgt) in todo for i in range(wlen)):
            hgt += 1
        for dz in range(hgt):
            for dx in range(wlen):
                todo.discard((x + dx, z + dz))
        out.append((x, z, wlen, hgt))
    return out


# ---------------------------------------- def sizes, and why they are needed
# ⚠️ THE PLAN EMITS A CELL; GenSpawn READS IT AS THE BUILDING'S CENTRE.
# `build()` anchors a machine at the MIN CORNER of its footprint (footprint[
# (x+dx, z+dz)] over range(mw)), and `jawa/spawn_batch` hands the op straight to
# GenSpawn.Spawn(thing, cell, ...) where `cell` is the loc RimWorld centres on:
# GenAdj.OccupiedRect computes minX = loc.x - (w-1)/2. So emitting the corner
# puts every multi-cell building half its own size off, and a 7x3 Autofarmer
# lands 3 cells west of where the deck plan drew it.
#
# 1x1 things are unaffected -- shift is (0,0) -- which is why 782 hull walls, 185
# conduit and 51 hoppers looked perfect and hid the bug in the 20 things that
# were wrong. Found 2026-08-13 by auditing sizes, not by looking at output.
#
# Sizes are read from the game's own XML into def_sizes.json (see _provenance in
# that file) and re-derived by the selftest, so a mod update that resizes a
# machine fails a test instead of silently shifting it.
def load_def_sizes():
    p = os.path.join(OUT, "def_sizes.json")
    if not os.path.isfile(p):
        return {}
    return {k: tuple(v) for k, v in json.load(open(p, encoding="utf-8"))["sizes"].items()}


DEF_SIZES = load_def_sizes()


def spawn_cell(th, x, z):
    """Corner -> centre. Returns the cell to EMIT for a thing anchored at (x,z).

    Prefers the PLACED footprint over the def's declared size: the design decides
    which rect the machine occupies, and the def only has to agree with it modulo
    rotation. Falls back to the def size for things with no recorded footprint
    (hoppers, boosters, heatsinks, hull, conduit).
    """
    fp = th.get("footprint")
    w, h = tuple(fp) if fp else DEF_SIZES.get(th.get("defName"), (1, 1))
    return x + (w - 1) // 2, z + (h - 1) // 2


def node_cells():
    """Every cell a node OCCUPIES, not just the cell it is anchored at.

    ⚠️ The engine is 3x3 and centred, so it covers nine cells. Guards that test
    only the anchor pass for a reason unrelated to the guard: today the keel and
    the engine simply do not intersect, so the conduit exception has never had to
    be right. Move the engine onto the keel and eight of its nine cells would take
    EXPOSED conduit while the check still reported "clashes: none".
    """
    cells = set()
    for kind, x, z in NODES:
        w, h = NODE_SIZE[kind]
        # odd sizes are centred on their coordinate; even sizes anchor at it
        x0 = x - (w // 2 if w % 2 else 0)
        z0 = z - (h // 2 if h % 2 else 0)
        for dx in range(w):
            for dz in range(h):
                cells.add((x0 + dx, z0 + dz))
    return cells


def node_plan(origin=(0, 0)):
    """The grav engine and the field extenders, as spawn calls.

    These are NOT in `tiles`. The tile grid describes the hull the exporter would
    carry, and the exporter deliberately excludes the engine because the export is
    anchored on it. For a LIVE build that reasoning inverts: nothing places the
    engine for us, so if this plan omits it we get a ship-shaped building with no
    engine, and the omission is invisible because every other call succeeds.
    """
    ox, oz = origin
    by_kind = {}
    for kind, x, z in NODES:
        by_kind.setdefault(kind, []).append((x + ox, z + oz))
    calls = []
    for kind, cells in sorted(by_kind.items()):
        w, h = NODE_SIZE[kind]
        calls.append({
            "tool": "jawa/spawn_batch",
            "defName": NODE_DEF[kind], "stuff": None, "rot": 0,
            "needsManualRotation": False,
            "size": "%dx%d" % (w, h),
            "coordIs": "centre" if (w % 2 and w > 1) else "cell",
            "count": len(cells),
            "ops": ";".join("%s:%d,%d" % (NODE_DEF[kind], x, z) for (x, z) in cells),
        })
    return calls


def foundation_plan(tiles, origin=(0, 0)):
    """Substructure for every tile, on the FOUNDATION layer.

    ⚠️ This is not decoration and it is not the floor. `Substructure` is what
    `terrainAffordanceNeeded` demands on GravshipHull, GravFieldExtender and
    PilotConsole -- 10 defs in Buildings_Gravship.xml. Lay it FIRST: it is the
    surface the rest of the ship is placed on.

    It goes to layer='foundation', a third grid distinct from 'under'. The
    companion gained that layer on 2026-08-13; before then this could not be
    emitted at all, and the plan silently omitted it while looking complete.
    """
    ox, oz = origin
    cells = [(t["x"] + ox, t["z"] + oz) for t in tiles]
    rects = rects_from(cells)
    return {
        "tool": "jawa/set_terrain_batch",
        "layer": "foundation",
        "terrainDef": FOUNDATION,
        "cells": len(cells),
        "rects": len(rects),
        "ops": ";".join("%s:%d,%d,%d,%d" % (FOUNDATION, x, z, w, h)
                        for (x, z, w, h) in rects),
    }


NODE_CELLS = node_cells()


def grid_extent(tiles):
    """(minx, minz, maxx, maxz) of the design in its own grid space."""
    xs = [t["x"] for t in tiles]
    zs = [t["z"] for t in tiles]
    return min(xs), min(zs), max(xs), max(zs)


def centred_origin(tiles, map_w, map_h):
    """Origin that centres the design on a map_w x map_h map.

    Raises if the hull cannot fit — a ship larger than the map is not a placement
    problem to be solved by clamping, it is a design that cannot be built.
    """
    minx, minz, maxx, maxz = grid_extent(tiles)
    w, h = maxx - minx + 1, maxz - minz + 1
    if w > map_w or h > map_h:
        raise ValueError(
            "hull is %dx%d and does not fit a %dx%d map" % (w, h, map_w, map_h))
    return (map_w - w) // 2 - minx, (map_h - h) // 2 - minz


def bridge_plan(tiles, origin=(0, 0)):
    """Batched ops for jawa/set_terrain_batch, grouped by terrain.

    `origin` is added to every emitted cell. See `resolve_origin` for why there
    is no usable default.
    """
    ox, oz = origin
    by_terrain = {}
    for t in tiles:
        if t["terrainDef"]:
            by_terrain.setdefault(t["terrainDef"], []).append((t["x"] + ox, t["z"] + oz))
    plan = {}
    for terr, cells in by_terrain.items():
        rects = rects_from(cells)
        plan[terr] = {
            "cells": len(cells),
            "rects": len(rects),
            "ops": ";".join("%s:%d,%d,%d,%d" % (terr, x, z, w, h) for (x, z, w, h) in rects),
        }
    return plan


MAX_OPS = 4096          # the companion's compiled-in guard, mirrored here


def spawn_plan(tiles, origin=(0, 0)):
    """Batched ops for jawa/spawn_batch, grouped by (def, stuff, rot).

    `stuff` and `rot` are call-level on the companion, so the grouping key IS the
    call boundary. That is not a limitation in practice — a hull is one material
    at one facing, which is exactly one call.

    Things whose name came from the BUILD SHEET are held back as unresolved
    rather than emitted. Those are VFE machines the sheet names by human label,
    and emitting them would produce a call that dies at run time on 'unknown
    ThingDef'. A plan that looks complete while being unbuildable is worse than
    one that says plainly what it cannot do.

    ⚠️ THE TEST IS PROVENANCE, NOT SHAPE. The first version of this asked
    `" " in name` — treating a space as the mark of a label. That is a proxy, and
    it failed on exactly the cases that matter: `Autoloom`, `Smelter`, `Cannery`
    and `Fishfarm` are single words and sailed straight into the ops as if they
    were verified defNames. Some may even be real, which is worse — it would work
    until the one that isn't.

    So the rule is where a name CAME FROM, not what it looks like: anything
    carrying a `note` was merged in from the build sheet and is a label until a
    live `jawa/get_def` says otherwise. Only names emitted from the vocabulary
    harvested out of the exporter's own ship are treated as resolved.
    """
    ox, oz = origin
    groups = {}
    unresolved = {}
    for t in tiles:
        for th in t["things"]:
            name = th["defName"]
            # Provenance still decides, but a build-sheet thing whose label has
            # been resolved to a real VFE defName is now emittable. Anything
            # still unresolved is held back exactly as before.
            if th.get("note") and not th.get("resolved"):
                cx, cz = spawn_cell(th, t["x"] + ox, t["z"] + oz)
                unresolved.setdefault(th.get("label", name), []).append((cx, cz))
                continue
            # A machine we KNOW is rotated must not go out at rot=0 as though it
            # were not. We cannot derive east-vs-west from a footprint, so the op
            # is emitted with a flag rather than a silent default — a wrong facing
            # placed confidently is worse than one the sheet admits it cannot fix.
            needs_rot = "ROTATED" in (th.get("note") or "")
            key = (name, th.get("stuffDef"), th.get("rotInteger", 0), needs_rot)
            groups.setdefault(key, []).append(spawn_cell(th, t["x"] + ox, t["z"] + oz))

    calls = []
    for (name, stuff, rot, needs_rot), cells in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        # split against the companion guard rather than discovering it live
        for i in range(0, len(cells), MAX_OPS):
            chunk = cells[i:i + MAX_OPS]
            calls.append({
                "tool": "jawa/spawn_batch",
                "defName": name, "stuff": stuff, "rot": rot,
                "needsManualRotation": needs_rot,
                "count": len(chunk),
                "ops": ";".join("%s:%d,%d" % (name, x, z) for (x, z) in chunk),
            })
    return calls, unresolved


def selftest():
    import numpy as np
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        print("  %-4s %s   %s" % ("ok" if cond else "FAIL", name, detail))
        ok = ok and cond

    print("shipbuild selftest — no game, no writes\n")
    grid = load_grid()
    els = load_elements()
    tiles, wall = build(grid, els)

    occupied = int((grid != "").sum())
    chk("hull reproduces the locked figure", occupied == 4057, "%d tiles (want 4057)" % occupied)
    chk("one tile record per occupied cell", len(tiles) == occupied, "%d records" % len(tiles))

    counts = {}
    for t in tiles:
        counts[t["zone"]] = counts.get(t["zone"], 0) + 1
    chk("cargo matches published", counts.get("G") == 1443, "G=%s (want 1443)" % counts.get("G"))
    chk("shuttle matches published", counts.get("H") == 420, "H=%s (want 420)" % counts.get("H"))
    fac = sum(counts.get(k, 0) for k in "ABCDEF")
    chk("factory matches published", fac == 1182, "A-F=%d (want 1182)" % fac)

    chk("every tile has a foundation", all(t["foundationDef"] == FOUNDATION for t in tiles))
    missing = sorted({t["zone"] for t in tiles if not t["terrainDef"]})
    chk("every zone maps to a terrain", not missing, "unmapped: %s" % (missing or "none"))
    chk("every zone code is documented", not (set(counts) - set(ZONES)),
        "undocumented: %s" % sorted(set(counts) - set(ZONES)))

    # the wall must fully enclose: no occupied tile may touch empty without a wall
    h, w = grid.shape
    leaks = 0
    for (x, z) in wall:
        pass
    for z in range(h):
        for x in range(w):
            if grid[z, x] == "":
                continue
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, nz = x + dx, z + dz
                outside = nx < 0 or nz < 0 or nx >= w or nz >= h or grid[nz, nx] == ""
                if outside and (x, z) not in wall:
                    leaks += 1
    chk("hull is sealed (no unwalled edge tile)", leaks == 0, "%d leaks" % leaks)

    # rect decomposition must be an EXACT cover — the property the bridge relies on
    plan = bridge_plan(tiles)
    for terr, p in plan.items():
        cells = {(t["x"], t["z"]) for t in tiles if t["terrainDef"] == terr}
        covered = set()
        dup = 0
        for part in p["ops"].split(";"):
            _, rest = part.split(":")
            x, z, ww, hh = (int(v) for v in rest.split(","))
            for dz in range(hh):
                for dx in range(ww):
                    c = (x + dx, z + dz)
                    if c in covered:
                        dup += 1
                    covered.add(c)
        chk("%-14s exact cover" % terr, covered == cells and dup == 0,
            "%d cells -> %d rects, %d overlap" % (p["cells"], p["rects"], dup))

    calls, unresolved = spawn_plan(tiles)
    chk("every spawn call is within the op guard",
        all(c["count"] <= MAX_OPS for c in calls),
        "largest %d ops (guard %d)" % (max((c["count"] for c in calls), default=0), MAX_OPS))
    walls = [c for c in calls if c["defName"] == HULL_WALL]
    chk("hull walls emit as spawn ops", walls and sum(c["count"] for c in walls) == len(wall),
        "%d wall ops vs %d wall tiles" % (sum(c["count"] for c in walls), len(wall)))
    # The check that caught the proxy bug: every emitted defName must be one of
    # the names harvested from the exporter's own ship, not merely space-free.
    VERIFIED = {HULL_WALL, KEEL_CONDUIT_OPEN, KEEL_CONDUIT_UNDER} | set(MACHINE_DEFS.values())
    leaked = sorted({c["defName"] for c in calls} - VERIFIED)
    chk("only harvested defNames reach the ops", not leaked, "leaked: %s" % (leaked or "none"))
    chk("build-sheet labels are all resolved", not unresolved,
        "%d still unresolved: %s" % (len(unresolved), sorted(unresolved) or "none"))
    # DERIVED. This asserted a hardcoded 69, which was the count while 8
    # heatsinks and 2 boosters were being silently dropped -- the magic number
    # certified the bug. Expectation now comes from the sheet, minus whatever is
    # held back as a footprint conflict.
    machine_ops = sum(c["count"] for c in calls if c["defName"].startswith("VFEFactory_"))
    expect_vfe = sum(1 for e in els if e.get("type") in ("machine", "hopper", "booster", "heatsink")) \
        - len(getattr(build, "conflicts", []))
    chk("every VFE element in the sheet emits an op", machine_ops == expect_vfe,
        "%d ops for %d sheet element(s), %d held back as conflicts"
        % (machine_ops, expect_vfe, len(getattr(build, "conflicts", []))))

    # --- the three findings from PROJECT's review, asserted not assumed ---
    chk("machine sizes were read from source", len(MACHINE_DECL) == 18,
        "%d declared sizes parsed" % len(MACHINE_DECL))
    # ⚠️ This asserted `== 3` and was WRONG rather than stale: the real count is 4.
    # Autofarmer was missing because rotation was judged against the build sheet,
    # whose declaration is the transpose of the def's. The number is now DERIVED
    # from the defs, so it cannot encode a miscount again.
    rotated = [t for t in tiles for th in t["things"]
               if "ROTATED" in (th.get("note") or "")]
    expect_rot = sum(1 for t in tiles for th in t["things"]
                     if th.get("footprint") and th.get("defName") in DEF_SIZES
                     and tuple(th["footprint"]) == tuple(reversed(DEF_SIZES[th["defName"]]))
                     and DEF_SIZES[th["defName"]][0] != DEF_SIZES[th["defName"]][1])
    chk("rotation recovered, not dropped", len(rotated) == expect_rot,
        "%d machine(s) rotated 90 deg" % len(rotated))
    # DERIVED, not hardcoded. This asserted `261 - 18` and broke the moment
    # heatsinks stopped being dropped -- 2 of their anchors sit inside a machine
    # footprint, so those cells moved from "occupied by a machine" to "has a
    # thing on it". The magic number encoded a state that included a bug.
    fp = [t for t in tiles if t.get("occupiedBy")]
    machine_cells = set()
    anchors = set()
    for e in els:
        if e.get("type") != "machine":
            continue
        mx, mz, mw, mh = e["rect"]
        anchors.add((mx, mz))
        for dx in range(mw):
            for dz in range(mh):
                machine_cells.add((mx + dx, mz + dz))
    # Support anchors that WOULD sit in a machine footprint are held back as
    # conflicts, so none reaches things_at and the count is simply every machine
    # cell that is not an anchor. That equality IS the invariant: if a support
    # element ever gets emitted on top of a machine, this drops below expect_fp.
    expect_fp = len(machine_cells - anchors)
    chk("machine footprints recorded", len(fp) == expect_fp,
        "%d non-anchor footprint cells (%d machine cells - %d anchors); "
        "%d support anchor(s) held back as conflicts"
        % (len(fp), len(machine_cells), len(anchors),
           len(getattr(build, "conflicts", []))))

    idx = {(t["x"], t["z"]): t for t in tiles}
    bad = []
    for (nx, nz) in sorted(node_cells()):
        t = idx.get((nx, nz))
        if t and any(th["defName"] == KEEL_CONDUIT_OPEN for th in t["things"]):
            bad.append((nx, nz))
    # ⚠️ THIS CHECK CANNOT FAIL, and saying so is the point. build() decides
    # hidden-vs-exposed from NODE_CELLS, and this reads the same set back, so it
    # is a consistency check, not a safety net — it proves the generator applied
    # its own rule, never that the rule is right. The real protection is in
    # build(); measured 2026-08-13 with the engine moved onto the keel, the
    # anchor-only version laid EXPOSED conduit on 5 of the 9 footprint cells and
    # this check still said "clashes: none".
    chk("generator applied the node-footprint conduit rule (NOT a safety net)",
        not bad, "%d cell(s) checked, clashes: %s" % (len(node_cells()), bad or "none"))
    hid = sum(1 for t in tiles for th in t["things"] if th["defName"] == KEEL_CONDUIT_UNDER)
    opn = sum(1 for t in tiles for th in t["things"] if th["defName"] == KEEL_CONDUIT_OPEN)
    chk("keel conduit is split, not uniform", hid > 0 and opn > 0,
        "%d hidden / %d exposed" % (hid, opn))

    # ---- placement. The bug these guard against emitted a corner-anchored ship
    # that looked identical to a deliberate one, so check the SHIFT, not the ops.
    minx, minz, maxx, maxz = grid_extent(tiles)
    base = bridge_plan(tiles, (0, 0))
    moved = bridge_plan(tiles, (10, 20))
    shifted = all(
        [(x + 10, z + 20, w, h) for (x, z, w, h) in
         [tuple(int(n) for n in r.split(":")[1].split(",")) for r in base[t]["ops"].split(";")]]
        == [tuple(int(n) for n in r.split(":")[1].split(",")) for r in moved[t]["ops"].split(";")]
        for t in base)
    chk("origin shifts every terrain cell uniformly", shifted,
        "%d terrain group(s) translate by exactly (+10,+20)" % len(base))

    sb, _ = spawn_plan(tiles, (0, 0))
    sm, _ = spawn_plan(tiles, (10, 20))
    chk("origin does not change WHAT is built, only where",
        [c["count"] for c in sb] == [c["count"] for c in sm] and len(sb) == len(sm),
        "%d call(s), %d thing(s) either way" % (len(sb), sum(c["count"] for c in sb)))

    o = centred_origin(tiles, 250, 250)
    w, h = maxx - minx + 1, maxz - minz + 1
    chk("--center puts equal margin on both axes", o == ((250 - w) // 2 - minx, (250 - h) // 2 - minz),
        "hull %dx%d on 250x250 -> origin +%d,+%d, occupies x %d-%d z %d-%d"
        % (w, h, o[0], o[1], minx + o[0], maxx + o[0], minz + o[1], maxz + o[1]))

    try:
        centred_origin(tiles, 32, 32)
        fits = False
    except ValueError:
        fits = True
    chk("a hull too big for the map raises instead of clamping", fits,
        "86x133 on a 32x32 map is refused, not squeezed")

    try:
        resolve_origin([], tiles)
        refused = False
    except SystemExit:
        refused = True
    chk("no origin given -> REFUSES to emit", refused,
        "the corner is never a default; it must be chosen with --corner")

    # ---- the grav nodes and the foundation. Both were absent from the emitted
    # plan until 2026-08-13 and their absence was invisible: every other call
    # succeeded, so the plan looked complete while producing an engineless ship
    # on bare ground.
    nodes = node_plan((0, 0))
    by = {c["defName"]: c for c in nodes}
    # 🔴 OWNER'S RULE, 2026-08-13: EXACTLY ONE grav engine, EVER. Everything else
    # in the field is an extender. A second engine is not a tuning question, it is
    # illegal — so this asserts ==1, not >=1. If a future NODES edit adds one, this
    # fails rather than shipping a plan that places two.
    chk("EXACTLY ONE grav engine — owner's rule, never two",
        by.get("GravEngine", {}).get("count") == 1
        and sum(1 for k, _, _ in NODES if k == "ENGINE") == 1,
        "%d engine node(s), %d emitted" % (sum(1 for k, _, _ in NODES if k == "ENGINE"),
                                           by.get("GravEngine", {}).get("count", 0)))
    chk("the grav ENGINE is emitted", "GravEngine" in by,
        "%d x GravEngine, size %s" % (by["GravEngine"]["count"], by["GravEngine"]["size"])
        if "GravEngine" in by else "MISSING")
    chk("the field EXTENDERS are emitted", by.get("GravFieldExtender", {}).get("count") ==
        sum(1 for k, _, _ in NODES if k == "EXT"),
        "%d emitted, %d in NODES" % (by.get("GravFieldExtender", {}).get("count", 0),
                                     sum(1 for k, _, _ in NODES if k == "EXT")))
    chk("the engine's coordinate is flagged as its CENTRE, not a corner",
        by.get("GravEngine", {}).get("coordIs") == "centre",
        "3x3 spawns centred; a corner reading shifts it one cell off its seating")

    f = foundation_plan(tiles, (0, 0))
    chk("foundation covers EVERY tile", f["cells"] == len(tiles),
        "%d Substructure cells for %d tiles, %d rect(s)" % (f["cells"], len(tiles), f["rects"]))
    chk("foundation goes to the FOUNDATION layer, not 'under'", f["layer"] == "foundation",
        "underGrid and foundationGrid are different arrays; Substructure lives in the latter")
    chk("everything needing the Substructure affordance has it under them",
        f["cells"] == len(tiles) and f["terrainDef"] == FOUNDATION,
        "GravshipHull/GravFieldExtender/PilotConsole all demand it")

    # ---- corner -> centre. The defect these guard: build() anchors a machine at
    # its min corner and GenSpawn reads the emitted cell as the CENTRE, so every
    # multi-cell thing landed half its own size off while all the 1x1 ops looked
    # perfect.
    chk("def sizes are loaded from the game's XML", len(DEF_SIZES) > 0,
        "%d def size(s) in def_sizes.json" % len(DEF_SIZES))

    drift = []
    for n, (w, h) in sorted(DEF_SIZES.items()):
        got = spawn_cell({"defName": n}, 100, 100)
        if got != (100 + (w - 1) // 2, 100 + (h - 1) // 2):
            drift.append(n)
    chk("every def shifts by (w-1)//2, (h-1)//2", not drift, "drift: %s" % (drift or "none"))

    chk("a 1x1 thing is NOT shifted", spawn_cell({"defName": HULL_WALL}, 50, 60) == (50, 60),
        "GravshipHull emits at its own cell — which is why 782 walls hid this bug")

    big = [t for t in tiles for th in t["things"] if th.get("footprint")
           and tuple(th["footprint"]) != (1, 1)]
    moved = 0
    for t in tiles:
        for th in t["things"]:
            if spawn_cell(th, t["x"], t["z"]) != (t["x"], t["z"]):
                moved += 1
    chk("multi-cell things ARE shifted off their anchor", moved > 0,
        "%d op(s) now emit a centre instead of a corner" % moved)

    fp_mismatch = []
    for t in tiles:
        for th in t["things"]:
            fp, dn = th.get("footprint"), th.get("defName")
            if not fp or dn not in DEF_SIZES:
                continue
            dw, dh = DEF_SIZES[dn]
            if tuple(fp) not in ((dw, dh), (dh, dw)):
                fp_mismatch.append((dn, tuple(fp), (dw, dh)))
    chk("every placed footprint matches its def size, modulo rotation",
        not fp_mismatch, "mismatches: %s" % (fp_mismatch or "none"))

    rotated = [(t["x"], t["z"], th["defName"]) for t in tiles for th in t["things"]
               if th.get("footprint") and th.get("defName") in DEF_SIZES
               and tuple(th["footprint"]) == tuple(reversed(DEF_SIZES[th["defName"]]))
               and DEF_SIZES[th["defName"]][0] != DEF_SIZES[th["defName"]][1]]
    flagged = [(t["x"], t["z"], th["defName"]) for t in tiles for th in t["things"]
               if "ROTATED" in (th.get("note") or "")]
    chk("every def-vs-placement transposition is flagged as rotated",
        sorted(rotated) == sorted(flagged),
        "%d transposed, %d flagged" % (len(rotated), len(flagged)))
    chk("rotation is judged against the DEF, not the build sheet",
        any(d == "VFEFactory_Autofarmer" for _, _, d in flagged),
        "Autofarmer is def (7,3) placed 3x7. The sheet USED to declare (3,7), "
        "which hid it; corrected at source in 7b89b7e, so this now guards a fixed bug")

    got = sheet_fingerprint()
    chk("build sheet is the PINNED one (regeneration would move 5 machines)",
        got == SHEET_SHA256,
        "sha256 %s" % (got[:16] if got == SHEET_SHA256 else
                       "%s != pinned %s — the sheet CHANGED. Re-verify the "
                       "non-square machines against the deck plan before "
                       "updating SHEET_SHA256." % (got[:16], SHEET_SHA256[:16])))

    seen = {e.get("type") for e in els}
    unaccounted = seen - EMITTED_TYPES - set(NOT_EMITTED)
    chk("every sheet element type is emitted or explicitly excluded",
        not unaccounted, "unaccounted: %s" % (sorted(unaccounted) or "none"))

    counts = {}
    for e in els:
        counts[e.get("type")] = counts.get(e.get("type"), 0) + 1
    emitted = {}
    for t in tiles:
        for th in t["things"]:
            lbl = th.get("label")
            if lbl in EMITTED_TYPES:
                emitted[lbl] = emitted.get(lbl, 0) + 1
    held = {}
    for c in getattr(build, "conflicts", []):
        held[c["type"]] = held.get(c["type"], 0) + 1
    short = {k: (counts.get(k, 0), emitted.get(k, 0), held.get(k, 0))
             for k in ("hopper", "booster", "heatsink")
             if counts.get(k, 0) != emitted.get(k, 0) + held.get(k, 0)}
    chk("every hopper, booster and heatsink is emitted OR held as a conflict",
        not short, "sheet = emitted + held for all three; mismatches: %s"
        % (short or "none"))

    chk("footprint conflicts are REPORTED, never silently emitted",
        all(c.get("insideMachine") for c in getattr(build, "conflicts", [])),
        "%d conflict(s): %s" % (len(getattr(build, "conflicts", [])),
                                [(c["type"], tuple(c["at"]), c["insideMachine"])
                                 for c in getattr(build, "conflicts", [])] or "none"))

    print("\n%s" % ("ALL PASS" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1


ORIGIN_HELP = """
ship_bridge.json needs a MAP ORIGIN and there is no safe default.

The grid is design space: it starts at (1,1) because that is where the hull
starts, not because the ship belongs in the map's south-west corner. Emitting
those coordinates raw makes `jawa/spawn_batch` treat them as absolute map cells
and builds the ship hard against the map edge — a placement nothing chose.

Pass one of:

  --origin X,Z          add (X,Z) to every cell; you have chosen the corner
  --center W,H          centre the hull on a WxH map, e.g. --center 250,250
  --corner              emit at the grid's own coords, edge-anchored, on purpose

Read the map size off any companion reply — `jawa/get_terrain_batch`,
`jawa/set_terrain_batch` and `jawa/spawn_batch` all return `mapSize {x,z}`.
""".rstrip()


def resolve_origin(argv, tiles):
    """(origin, how) from argv, or raise SystemExit with an explanation.

    ⚠️ THERE IS DELIBERATELY NO DEFAULT. An offset of (0,0) is a real choice —
    it builds against the map edge — and it is not distinguishable in the output
    from "nobody thought about placement". This module's own rule is that a plan
    which looks complete while being wrong is worse than one that refuses, which
    is why unresolved machine labels are held back rather than emitted. Placement
    gets the same treatment.
    """
    def arg(flag):
        for i, a in enumerate(argv):
            if a == flag:
                return argv[i + 1] if i + 1 < len(argv) else ""
            if a.startswith(flag + "="):
                return a.split("=", 1)[1]
        return None

    if "--corner" in argv:
        return (0, 0), "corner (explicit): grid coords used as absolute map cells"
    v = arg("--origin")
    if v:
        x, z = (int(n) for n in v.replace(" ", "").split(","))
        return (x, z), "origin (explicit): +%d,+%d" % (x, z)
    v = arg("--center") or arg("--centre")
    if v:
        mw, mh = (int(n) for n in v.replace(" ", "").split(","))
        o = centred_origin(tiles, mw, mh)
        return o, "centred on a %dx%d map: +%d,+%d" % (mw, mh, o[0], o[1])
    raise SystemExit(ORIGIN_HELP)


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if "--selftest" in argv:
        return selftest()

    grid = load_grid()
    els = load_elements()
    tiles, wall = build(grid, els)
    origin, how = resolve_origin(argv, tiles)
    minx, minz, maxx, maxz = grid_extent(tiles)
    plan = bridge_plan(tiles, origin)
    os.makedirs(OUT, exist_ok=True)

    json.dump({"source": "src/RimMandrake/mapsynth/build_designs.py::d_falcon_halo_hollow",
               "tiles": len(tiles), "wallTiles": len(wall), "zones": ZONES,
               "tileList": tiles},
              open(os.path.join(OUT, "ship_tiles.json"), "w", encoding="utf-8"), indent=1)
    calls, unresolved = spawn_plan(tiles, origin)
    # BUILD ORDER IS LOAD-BEARING: foundation, then floors, then everything that
    # stands on them. GravshipHull and GravFieldExtender both demand the
    # Substructure affordance, so a hull call that runs before the foundation call
    # is placing onto bare ground.
    foundation = foundation_plan(tiles, origin)
    nodes = node_plan(origin)
    calls = nodes + calls
    # The origin is stamped INTO the plan so the file can always answer "where
    # does this build" without re-deriving it from the ops.
    json.dump({"origin": {"x": origin[0], "z": origin[1], "how": how},
               "hullExtent": {"w": maxx - minx + 1, "h": maxz - minz + 1},
               "mapCells": {"x0": minx + origin[0], "z0": minz + origin[1],
                            "x1": maxx + origin[0], "z1": maxz + origin[1]},
               "buildOrder": ["foundation", "terrain", "spawn"],
               "footprintConflicts": getattr(build, "conflicts", []),
               "foundation": foundation,
               "terrain": plan, "spawn": calls,
               "unresolvedLabels": {k: len(v) for k, v in sorted(unresolved.items())}},
              open(os.path.join(OUT, "ship_bridge.json"), "w", encoding="utf-8"), indent=1)
    print("  origin     %s" % how)
    print("  foundation %s x%d cells in %d rect(s)  [layer=foundation]"
          % (foundation["terrainDef"], foundation["cells"], foundation["rects"]))
    for c in nodes:
        print("  grav node  %-18s x%-3d size %s (coord is %s)"
              % (c["defName"], c["count"], c["size"], c["coordIs"]))
    for c in getattr(build, "conflicts", []):
        print("  ⚠ CONFLICT  %-10s at %-12s sits inside machine %s — HELD BACK"
              % (c["type"], tuple(c["at"]), c["insideMachine"]))
    print("  occupies   x %d-%d, z %d-%d"
          % (minx + origin[0], maxx + origin[0], minz + origin[1], maxz + origin[1]))

    counts = {}
    for t in tiles:
        counts[t["zone"]] = counts.get(t["zone"], 0) + 1
    total_rects = sum(p["rects"] for p in plan.values())
    print("wrote %s" % OUT)
    print("  tiles      %d" % len(tiles))
    print("  hull walls %d" % len(wall))
    print("  terrain    %d rect(s) across %d call(s)" % (total_rects, len(plan)))
    print("  spawn      %d call(s), %d thing(s)"
          % (len(calls), sum(c["count"] for c in calls)))
    for c in calls:
        flag = "  <-- ROTATE BY HAND (east/west undetermined)" if c["needsManualRotation"] else ""
        print("    %-38s stuff=%-6s rot=%d  %5d%s"
              % (c["defName"], c["stuff"] or "-", c["rot"], c["count"], flag))
    if unresolved:
        print("  UNRESOLVED labels (need a live jawa/get_def before placing):")
        for k, v in sorted(unresolved.items()):
            print("    %-26s %d site(s)" % (k, len(v)))
    print("  TOTAL BRIDGE CALLS for the shell: %d" % (len(plan) + len(calls)))
    for z, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print("    %-2s %-45s %5d" % (z, ZONES.get(z, "?"), n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
