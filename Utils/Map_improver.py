#!/usr/bin/env python3
"""
Map_improver.py  —  creative RimWorld map-improvement agent  (practice)
=======================================================================

WHAT IT IS
----------
An agent that INHERITS a base map (a mapkit.GameMap semantic terrain grid) plus
this project's design context, and emits an *improved* map together with a
justification for every change — what it changed, where, and why — tied to the
campaign's concepts. It works at the terrain level and attaches NOTES for the
pawns / items / set-pieces to layer on top (it does not paint creatures into
terrain).

This is a PRACTICE tool (user framing 2026-08-05): the point is to test whether
the creative choices "pass the sniff test," so it operates on semantic maps and
renders sensible before/after images. No live save is touched; the shortHash
problem is deliberately ignored (we assign real terrain *names*).

DESIGN GOALS THE OPERATORS SERVE  (from the AskUserQuestion answers + context)
-----------------------------------------------------------------------------
  1. More realistic geography  — coherent terrain transitions, banks, aprons,
     talus at cliff feet, deltas where rivers meet the sea.
  2. More tactically interesting — a defensible landing apron, a natural
     chokepoint, cover-giving rubble, approach lanes.
  3. Exotic hand-placed set-pieces — abandoned mine, half-working oil/chem
     refinery, a dead droid in its impact crater, an improved cavern system,
     crashed-Factory-ship wreckage (the Jawa/Star-Wars theme).

Each operator is a function(analysis, gm_out, ctx) -> list[Change]. A Change
records region + rationale + optional feature notes, so the emitted report reads
like a designer's changelog.

USAGE
-----
  python3 Map_improver.py <base.map.json> [--out DIR] [--scale 5]
                          [--ops all|eco,tactical,mine,refinery,droid,cavern,wreck]
                          [--seed N]

Outputs (next to the base map, stem = base stem):
  <stem>_improved.map.json   the improved semantic map
  <stem>_improved.png        after-only render
  <stem>_beforeafter.png     side-by-side before/after
  <stem>_improvement.md      the justification report (what/where/why + notes)
  <stem>_improvement.json    machine-readable change list
"""

import os
import sys
import json
import math
import random
import argparse
from collections import Counter, deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapkit import GameMap, render, render_pair, tprop, TERRAIN  # noqa: E402


# ==========================================================================
# CHANGE RECORD
# ==========================================================================
class Change:
    def __init__(self, op, what, where, why, cells=0, features=None,
                 notes=None):
        self.op = op            # operator id
        self.what = what        # short headline
        self.where = where      # human location description
        self.why = why          # rationale tied to project concepts
        self.cells = cells      # terrain cells altered
        self.features = features or []   # placed feature markers (dicts)
        self.notes = notes or []         # pawn/item layering suggestions

    def to_dict(self):
        return {"op": self.op, "what": self.what, "where": self.where,
                "why": self.why, "cells": self.cells,
                "features": self.features, "notes": self.notes}


# ==========================================================================
# ANALYSIS  (answer-independent structural read of the map)
# ==========================================================================
def analyze(gm):
    w, h = gm.w, gm.h
    hist = gm.terrain_histogram()
    # boolean fields
    passable = [[tprop(gm.grid[z][x], "passable", True) for x in range(w)]
                for z in range(h)]
    buildable = [[tprop(gm.grid[z][x], "buildable", False) for x in range(w)]
                 for z in range(h)]
    family = [[tprop(gm.grid[z][x], "family", "?") for x in range(w)]
              for z in range(h)]

    # region-label the passable space (4-conn) to find the main open area
    label = [[-1] * w for _ in range(h)]
    regions = []
    for z in range(h):
        for x in range(w):
            if passable[z][x] and label[z][x] == -1:
                cells = []
                dq = deque([(x, z)])
                label[z][x] = len(regions)
                while dq:
                    cx, cz = dq.popleft()
                    cells.append((cx, cz))
                    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, nz = cx + dx, cz + dz
                        if 0 <= nx < w and 0 <= nz < h and passable[nz][nx] \
                                and label[nz][nx] == -1:
                            label[nz][nx] = len(regions)
                            dq.append((nx, nz))
                regions.append(cells)
    regions.sort(key=len, reverse=True)

    # buildable "open flats": large contiguous buildable & family in soil/sand/rock
    def is_open(x, z):
        return buildable[z][x] and family[z][x] in ("sand", "soil", "rock",
                                                    "volcanic", "cave")
    # find biggest open rectangle-ish cluster centroid via sampling
    open_cells = [(x, z) for z in range(h) for x in range(w) if is_open(x, z)]

    # water presence
    water_cells = [(x, z) for z in range(h) for x in range(w)
                   if family[z][x] == "water"]
    water_kind = Counter(gm.grid[z][x] for x, z in water_cells)
    has_fresh = any(tprop(gm.grid[z][x], "water") == "fresh"
                    for x, z in water_cells)
    has_saline = any(tprop(gm.grid[z][x], "water") == "saline"
                     for x, z in water_cells)

    # mountain/rock mass
    rock_cells = [(x, z) for z in range(h) for x in range(w)
                  if family[z][x] == "mountain"]

    # existing structures (from features on the base map)
    structures = [f for f in gm.features if f["kind"] == "structure"]

    # edge openness: fraction of each border that is passable (approach lanes)
    def edge_open(cells):
        return sum(1 for (x, z) in cells if passable[z][x]) / max(1, len(cells))
    edges = {
        "N": edge_open([(x, h - 1) for x in range(w)]),
        "S": edge_open([(x, 0) for x in range(w)]),
        "E": edge_open([(w - 1, z) for z in range(h)]),
        "W": edge_open([(0, z) for z in range(h)]),
    }

    # centroid of the largest open cluster (rough "best base site")
    if open_cells:
        ox = sum(c[0] for c in open_cells) / len(open_cells)
        oz = sum(c[1] for c in open_cells) / len(open_cells)
    else:
        ox, oz = w / 2, h / 2

    return {
        "w": w, "h": h, "hist": hist,
        "passable": passable, "buildable": buildable, "family": family,
        "regions": regions,
        "open_cells": open_cells, "open_centroid": (ox, oz),
        "water_cells": water_cells, "water_kind": water_kind,
        "has_fresh": has_fresh, "has_saline": has_saline,
        "rock_cells": rock_cells, "structures": structures,
        "edges": edges,
        "dominant_family": family_mode(family),
    }


def family_mode(family):
    c = Counter()
    for row in family:
        for f in row:
            c[f] += 1
    return c.most_common(1)[0][0] if c else "?"


# ---- small geometry helpers ----------------------------------------------
def stamp_disc(gm, cx, cz, r, terrain, mask_family=None, jitter=0.0,
               rng=None):
    """Paint a rough disc of `terrain`; returns cells changed."""
    changed = 0
    r2 = r * r
    for z in range(max(0, cz - r), min(gm.h, cz + r + 1)):
        for x in range(max(0, cx - r), min(gm.w, cx + r + 1)):
            d2 = (x - cx) ** 2 + (z - cz) ** 2
            edge = r2 * (1.0 + (rng.uniform(-jitter, jitter) if rng and jitter
                                else 0.0))
            if d2 <= edge:
                if mask_family and tprop(gm.grid[z][x], "family") \
                        not in mask_family:
                    continue
                if gm.grid[z][x] != terrain:
                    gm.set(x, z, terrain)
                    changed += 1
    return changed


def stamp_rect(gm, x0, z0, x1, z1, terrain):
    changed = 0
    for z in range(max(0, z0), min(gm.h, z1 + 1)):
        for x in range(max(0, x0), min(gm.w, x1 + 1)):
            if gm.grid[z][x] != terrain:
                gm.set(x, z, terrain)
                changed += 1
    return changed


def ring(gm, cx, cz, r_in, r_out, terrain, mask_family=None):
    changed = 0
    for z in range(max(0, cz - r_out), min(gm.h, cz + r_out + 1)):
        for x in range(max(0, cx - r_out), min(gm.w, cx + r_out + 1)):
            d2 = (x - cx) ** 2 + (z - cz) ** 2
            if r_in * r_in <= d2 <= r_out * r_out:
                if mask_family and tprop(gm.grid[z][x], "family") \
                        not in mask_family:
                    continue
                if gm.grid[z][x] != terrain:
                    gm.set(x, z, terrain)
                    changed += 1
    return changed


def neighbors8(x, z):
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            if dx or dz:
                yield x + dx, z + dz


# ==========================================================================
# IMPROVEMENT OPERATORS
# Each: (analysis, gm_out, ctx) -> list[Change]
# ==========================================================================
def op_ecological(a, gm, ctx):
    """Make terrain transitions believable: fertile banks by fresh water,
    salt-tolerant fringe by the sea, talus rubble at cliff feet, and kill
    single-cell 'confetti' by majority-smoothing."""
    changes = []
    w, h = a["w"], a["h"]
    rng = ctx["rng"]

    # 1. fertile banks: soil/rich-soil hugging FRESH water where it's currently
    #    bare sand/gravel (rivers carry silt -> green banks).
    bank = 0
    for (x, z) in a["water_cells"]:
        if tprop(gm.grid[z][x], "water") != "fresh":
            continue
        for nx, nz in neighbors8(x, z):
            if 0 <= nx < w and 0 <= nz < h:
                fam = tprop(gm.grid[nz][nx], "family")
                if fam in ("sand", "rock"):
                    gm.set(nx, nz, "SoilRich" if rng.random() < 0.4 else "Soil")
                    bank += 1
    if bank:
        changes.append(Change(
            "eco", "Silt banks along the fresh water",
            "1-cell fringe on both sides of the river/lake",
            "Rivers deposit silt; bare sand abutting moving fresh water is "
            "ecologically wrong. Fertile banks also give the colony its only "
            "no-irrigation farmland — a deliberate scarcity anchor (desert_"
            "world_design 'why land here').", cells=bank,
            notes=["Layer riverbank flora (reeds, a few trees) on the SoilRich "
                   "cells.",
                   "This is the natural farm start — expect raids to approach "
                   "along the open banks."]))

    # 2. coastal salt fringe: sand between ocean and interior -> compacted/again
    salt = 0
    for (x, z) in a["water_cells"]:
        if tprop(gm.grid[z][x], "water") != "saline":
            continue
        for nx, nz in neighbors8(x, z):
            if 0 <= nx < w and 0 <= nz < h and \
                    tprop(gm.grid[nz][nx], "family") == "sand":
                if rng.random() < 0.5:
                    gm.set(nx, nz, "Mud")  # tidal mud
                    salt += 1
    if salt:
        changes.append(Change(
            "eco", "Tidal mud flat along the sea",
            "saline shoreline",
            "A hard sand/ocean edge looks stamped-on. A brackish mud flat is "
            "the real transition and doubles as a movement-slowing tidal "
            "barrier on that approach.", cells=salt,
            notes=["Salt water is a non-potable trap: note for the water-"
                   "scarcity layer (must desalinate)."]))

    # 3. talus at cliff feet: rubble ring around impassable rock/mountain
    talus = 0
    seen = set()
    for (x, z) in a["rock_cells"]:
        for nx, nz in neighbors8(x, z):
            if 0 <= nx < w and 0 <= nz < h and (nx, nz) not in seen \
                    and tprop(gm.grid[nz][nx], "family") == "sand" \
                    and rng.random() < 0.5:
                gm.set(nx, nz, "RockRubble")
                seen.add((nx, nz))
                talus += 1
    if talus:
        changes.append(Change(
            "eco", "Talus (scree) at the cliff feet",
            "base of the rock massif",
            "Cliffs shed rock; a sand-to-vertical-stone jump with no debris "
            "reads as artificial. Scree also gives light cover for a defense "
            "anchored on the mountain.", cells=talus,
            notes=["Scatter chunk-stone haulables on the talus for early "
                   "construction material."]))

    # 4. de-confetti: any lone cell whose 8 neighbors are all one *other*
    #    family gets absorbed (removes single-pixel noise).
    fixed = 0
    for z in range(1, h - 1):
        for x in range(1, w - 1):
            here = gm.grid[z][x]
            fam_here = tprop(here, "family")
            nb = Counter(tprop(gm.grid[nz][nx], "family")
                         for nx, nz in neighbors8(x, z))
            top_fam, cnt = nb.most_common(1)[0]
            if cnt >= 7 and top_fam != fam_here and top_fam != "water":
                # replace with a representative neighbor terrain
                for nx, nz in neighbors8(x, z):
                    if tprop(gm.grid[nz][nx], "family") == top_fam:
                        gm.set(x, z, gm.grid[nz][nx])
                        fixed += 1
                        break
    if fixed:
        changes.append(Change(
            "eco", "Smoothed single-cell terrain noise",
            "scattered across the map",
            "Isolated 1-tile terrain specks look like generator artifacts. "
            "Absorbing them into the surrounding material makes the map read "
            "as a real place.", cells=fixed))
    return changes


def op_tactical(a, gm, ctx):
    """Give the map a defensible landing apron + a legible chokepoint."""
    changes = []
    w, h = a["w"], a["h"]
    ox, oz = a["open_centroid"]
    ox, oz = int(ox), int(oz)

    # 1. landing apron: a flat buildable pad of firm ground at the open centroid
    apron_terrain = "Gravel"
    if a["dominant_family"] == "volcanic":
        apron_terrain = "AB_VolcanicGravel"
    r = max(6, min(w, h) // 12)
    cells = stamp_disc(gm, ox, oz, r, apron_terrain,
                       mask_family=("sand", "soil", "rock", "volcanic"),
                       jitter=0.25, rng=ctx["rng"])
    if cells:
        changes.append(Change(
            "tactical", "Firm landing/base apron",
            "map center-of-open-space (~%d,%d), radius %d" % (ox, oz, r),
            "The gravship sets down on soft sand/soil that is slow to build on "
            "and offers no natural footing. A firm gravel apron gives an "
            "immediate buildable core and a clean field of fire around the "
            "hull.", cells=cells,
            features=[{"kind": "structure", "x": ox, "z": oz,
                       "label": "gravship set-down"}],
            notes=["Place the gravship + starting crew on the apron.",
                   "Keep the apron's perimeter clear for turrets/killbox."]))

    # 2. chokepoint: if there's a rock mass, carve a single 3-wide pass and
    #    wall the rest with rubble so approach funnels through it.
    if a["rock_cells"]:
        # pick the rock cell nearest the most-open edge to place the pass
        best_edge = max(a["edges"], key=a["edges"].get)
        # a short rubble berm across the open centroid toward that edge
        berm = 0
        if best_edge in ("E", "W"):
            zc = oz
            xline = 4 if best_edge == "W" else w - 5
            for z in range(h):
                if abs(z - zc) > 2:   # leave a 5-wide gap at zc
                    if tprop(gm.grid[z][xline], "family") in ("sand", "soil"):
                        gm.set(xline, z, "RockRubble")
                        berm += 1
        else:
            xc = ox
            zline = 4 if best_edge == "S" else h - 5
            for x in range(w):
                if abs(x - xc) > 2:
                    if tprop(gm.grid[zline][x], "family") in ("sand", "soil"):
                        gm.set(x, zline, "RockRubble")
                        berm += 1
        if berm:
            changes.append(Change(
                "tactical", "Approach berm with a single choked pass",
                "across the open %s approach" % best_edge,
                "The widest raid approach (%s edge, %.0f%% open) had no natural "
                "funnel. A low scree berm with one 5-tile gap turns a broad "
                "front into a defensible chokepoint without walling the player "
                "in." % (best_edge, 100 * a["edges"][best_edge]), cells=berm,
                notes=["Anchor the killbox on the 5-tile gap.",
                       "Berm is passable-but-slow cover, not a hard wall — "
                       "raiders will still path through it, just slowly."]))
    return changes


def op_mine(a, gm, ctx):
    """Abandoned mine: a bitten-out notch in rock (or a sunk pit in flats) with
    tailings, a timber-framed adit, and a resource note."""
    rng = ctx["rng"]
    w, h = a["w"], a["h"]
    # prefer to site it on/next to rock; else a pit in the flats near an edge
    if a["rock_cells"]:
        cx, cz = rng.choice(a["rock_cells"])
        site = "rock flank"
        kind_word = "strip mine + adit into the rock"
    else:
        cx, cz = int(w * rng.uniform(0.15, 0.3)), int(h * rng.uniform(0.6, 0.85))
        site = "open-pit dig in the flats"
        kind_word = "open-pit mine"
    c = 0
    c += stamp_disc(gm, cx, cz, 5, "RockRubble", jitter=0.3, rng=rng)   # tailings
    c += stamp_disc(gm, cx, cz, 3, "CaveFloor", jitter=0.2, rng=rng)    # cut floor
    c += stamp_rect(gm, cx - 1, cz - 6, cx + 1, cz, "Gravel")           # haul road
    feats = [
        {"kind": "mine", "x": cx, "z": cz, "label": "mine adit (collapsed)"},
        {"kind": "relic", "x": cx + 1, "z": cz + 1, "label": "rusted ore cart"},
    ]
    return [Change(
        "mine", "Abandoned %s" % kind_word,
        "%s at (%d,%d)" % (site, cx, cz),
        "An exotic 'someone was here first' set-piece. The cut floor, tailings "
        "apron and haul road tell a story and seed a resource pocket — but the "
        "collapsed adit is the anti-exponential catch: reopening it costs labor "
        "and risks an infestation/roof-fall, so the ore isn't free.",
        cells=c, features=feats,
        notes=["Layer: a small deep-ore vein + steel/components chunks in the "
               "adit; a dead prospector corpse w/ a note; 1-2 stone chunks on "
               "the tailings.",
               "Hazard hook (Family-11 pre-placed): a dormant insect hive just "
               "inside the adit — mining vibration wakes it."])]


def op_refinery(a, gm, ctx):
    """Half-working oil/chem refinery: cracked asphalt pad, pipe runs, a fouled
    tar/sludge pond, and a still-flickering flare — industrial ruin."""
    rng = ctx["rng"]
    w, h = a["w"], a["h"]
    cx = int(w * rng.uniform(0.55, 0.8))
    cz = int(h * rng.uniform(0.15, 0.4))
    c = 0
    c += stamp_rect(gm, cx - 7, cz - 5, cx + 7, cz + 5, "AB_AsphaltFloor")  # pad
    # pipe runs = asphalt fingers
    for k in range(-6, 7, 3):
        c += stamp_rect(gm, cx + k, cz - 9, cx + k, cz - 5, "AB_AsphaltFloor")
    # fouled sludge pond (use mud as stand-in for tar sludge)
    c += stamp_disc(gm, cx - 4, cz + 2, 3, "Mud", jitter=0.3, rng=rng)
    # cracked/leaking edges
    c += ring(gm, cx, cz, 8, 10, "AB_CrackedMud", mask_family=("sand", "soil"))
    feats = [
        {"kind": "refinery", "x": cx, "z": cz, "label": "cracking tower (flare lit)"},
        {"kind": "refinery", "x": cx - 4, "z": cz + 2, "label": "sludge pond"},
        {"kind": "relic", "x": cx + 5, "z": cz - 2, "label": "chemfuel drums"},
    ]
    return [Change(
        "refinery", "Half-working chem/oil refinery",
        "hardpan at (%d,%d)" % (cx, cz),
        "A landmark ruin that reads instantly as 'industrial past'. The lit "
        "flare implies it still runs on a trickle — a reason to fight over it. "
        "The leaking sludge ring is the price: fouled ground you must contain, "
        "supporting the terrain-souring / water-denial hazard axis.",
        cells=c, features=feats,
        notes=["Layer: a working chemfuel source (slow), a few steel/plasteel "
               "drums, an ancient security mech guarding it.",
               "Hazard: sludge pond as toxic terrain; wildlife avoids it — a "
               "visual tell for the poison layer."])]


def op_droid(a, gm, ctx):
    """A dead droid in its impact crater — it fell from orbit and never got up.
    Concentric crater: scorched center, ejecta ring, one long debris streak."""
    rng = ctx["rng"]
    w, h = a["w"], a["h"]
    # site in open ground away from center
    cx = int(w * rng.uniform(0.2, 0.45))
    cz = int(h * rng.uniform(0.2, 0.45))
    c = 0
    c += stamp_disc(gm, cx, cz, 4, "AB_Obsidian", jitter=0.15, rng=rng)  # fused glass
    c += ring(gm, cx, cz, 4, 6, "AB_SolidifiedLava")                     # scorch
    c += ring(gm, cx, cz, 6, 9, "RockRubble")                            # ejecta
    # impact streak (came in at a low angle from the NE)
    for t in range(1, 22):
        sx, sz = cx + t, cz + t
        if 0 <= sx < w and 0 <= sz < h and t % 2 == 0:
            c += stamp_disc(gm, sx, sz, 1, "RockRubble", rng=rng)
    feats = [
        {"kind": "droid", "x": cx, "z": cz, "label": "dead droid (impact)"},
        {"kind": "relic", "x": cx, "z": cz, "label": "salvageable core"},
    ]
    return [Change(
        "droid", "Dead droid in its impact crater",
        "open ground at (%d,%d) with a NE debris streak" % (cx, cz),
        "Pure Star-Wars-theme flavor and a scavenge magnet: a machine that fell "
        "from space and augered in. The fused-glass center + ejecta ring + "
        "entry streak make the physics legible at a glance. Fits the crashed-"
        "Factory-ship / Jawa scavenger premise directly.",
        cells=c, features=feats,
        notes=["Layer: an inert mechanoid/droid corpse w/ salvage (components, "
               "a unique weapon or AI core relic).",
               "Jawa hook: this is exactly what the scavengers came for — a "
               "quest/relic seed.",
               "Optional risk: the core is dormant, not dead (reactivation "
               "event) — keeps the loot from being free."])]


def _mountain_interior_cells(a, gm):
    """Return impassable rock/mountain cells that are *interior* to a rock mass
    (all 4 orthogonal neighbors are also impassable rock/mountain). Carving
    starts here so the cavern lives inside stone, never out on the flats."""
    w, h = a["w"], a["h"]
    interior = []
    for (x, z) in a["rock_cells"]:
        if not tprop(gm.grid[z][x], "passable", True):  # solid stone only
            ok = True
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, nz = x + dx, z + dz
                if not (0 <= nx < w and 0 <= nz < h) or \
                        tprop(gm.grid[nz][nx], "passable", True):
                    ok = False
                    break
            if ok:
                interior.append((x, z))
    return interior


def op_cavern(a, gm, ctx):
    """Improve a cave system.

    A cavern needs a host rock formation. We carve ONLY into solid stone
    interior cells and stop at the rock's edge, so the chamber never sprawls
    out across open sand (that earlier bug produced an implausible surface
    blob). If the map has no real rock mass to host a cave, this operator
    declines rather than fabricate one — an honest 'no plausible placement'
    result the report will note."""
    rng = ctx["rng"]
    w, h = a["w"], a["h"]

    interior = _mountain_interior_cells(a, gm)
    if len(interior) < 12:
        # Not enough solid stone to host a believable cavern. Decline.
        return [Change(
            "cavern", "Cavern system — SKIPPED (no host rock mass)",
            "n/a",
            "The map lacks a solid mountain/rock formation large enough to "
            "hollow a believable cave into. Rather than carve a cave across "
            "open ground (which reads as a generator artifact), the operator "
            "declines. Add a rock massif first, or run --ops without 'cavern'.",
            cells=0,
            notes=["To host a cavern here, first grow a rock mass on an edge "
                   "(a future 'op_massif' operator), then re-run cavern."])]

    start = rng.choice(interior)
    solid = ("mountain",)          # carve only through impassable stone
    c = 0
    heads = [start]
    carved = 0
    steps = 0
    budget = min(len(interior) - 2, (w * h) // 60)   # keep it compact
    while heads and carved < budget and steps < 6000:
        steps += 1
        hx, hz = heads[0]
        dx, dz = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        nx, nz = hx + dx, hz + dz
        if 0 <= nx < w and 0 <= nz < h and \
                tprop(gm.grid[nz][nx], "family") in solid and \
                not tprop(gm.grid[nz][nx], "passable", True):
            gm.set(nx, nz, "CaveFloor")
            c += 1
            carved += 1
            heads[0] = (nx, nz)
            if rng.random() < 0.07 and len(heads) < 5:   # branch
                heads.append((nx, nz))
            if rng.random() < 0.03 and len(heads) > 1:
                heads.pop()
        else:
            # blocked (hit the rock edge or non-stone): retire this head
            if len(heads) > 1:
                heads.pop(0)
            else:
                break

    # find the cavern "mouth": a CaveFloor cell adjacent to open ground
    mouth = start
    for z in range(h):
        for x in range(w):
            if gm.grid[z][x] == "CaveFloor":
                for nx, nz in neighbors8(x, z):
                    if 0 <= nx < w and 0 <= nz < h and \
                            tprop(gm.grid[nz][nx], "passable", True) and \
                            tprop(gm.grid[nz][nx], "family") != "cave":
                        mouth = (x, z)
    feats = [{"kind": "cave", "x": mouth[0], "z": mouth[1],
              "label": "cavern mouth"}]
    return [Change(
        "cavern", "Branching cavern system",
        "hollowed inside the rock mass; mouth near (%d,%d)"
        % (mouth[0], mouth[1]),
        "A solid stone massif becomes a branching cavern with a single "
        "defensible mouth and interior chambers — a natural fortress option "
        "AND a high-risk/high-reward space. Carving is bounded to the rock "
        "interior so the cave stays enclosed in living stone (no surface "
        "sprawl).", cells=c, features=feats,
        notes=["Layer: cave flora / a water seep deep inside; ancient danger "
               "or infestation in the far chamber (why the cave isn't free "
               "real estate).",
               "Tactical: the single mouth is the anti-siege play — but "
               "infestations love the enclosed warmth."])]


def op_wreck(a, gm, ctx):
    """Crashed-Factory-ship wreckage: a long hull-scar of metal/ancient concrete
    with a debris scatter — the campaign's central Star Wars set-piece."""
    rng = ctx["rng"]
    w, h = a["w"], a["h"]
    # a long diagonal crash scar across an open quadrant
    x0 = int(w * rng.uniform(0.1, 0.25))
    z0 = int(h * rng.uniform(0.55, 0.75))
    ang = rng.uniform(-0.5, 0.2)
    length = int(min(w, h) * rng.uniform(0.45, 0.6))
    c = 0
    hull = []
    for t in range(length):
        hx = int(x0 + t * math.cos(ang))
        hz = int(z0 + t * math.sin(ang))
        if not (0 <= hx < w and 0 <= hz < h):
            break
        width = 3 if t < length * 0.7 else 2   # narrows toward the nose
        for dz in range(-width, width + 1):
            for dx in range(-width, width + 1):
                if dx * dx + dz * dz <= width * width:
                    xx, zz = hx + dx, hz + dz
                    if 0 <= xx < w and 0 <= zz < h:
                        terr = "MetalTile" if abs(dz) <= 1 else "AncientConcrete"
                        if gm.grid[zz][xx] != terr:
                            gm.set(xx, zz, terr)
                            c += 1
        hull.append((hx, hz))
    # gouge of churned ground + scattered debris on both sides of the scar
    for (hx, hz) in hull[::3]:
        c += stamp_disc(gm, hx, hz, rng.randint(3, 5), "RockRubble",
                        mask_family=("sand", "soil"), jitter=0.4, rng=rng)
    nose = hull[-1] if hull else (x0, z0)
    tail = hull[0] if hull else (x0, z0)
    feats = [
        {"kind": "wreck", "x": nose[0], "z": nose[1],
         "label": "Factory-ship prow (buried)"},
        {"kind": "wreck", "x": tail[0], "z": tail[1],
         "label": "torn stern section"},
        {"kind": "relic", "x": (nose[0] + tail[0]) // 2,
         "z": (nose[1] + tail[1]) // 2, "label": "intact cargo bay"},
    ]
    return [Change(
        "wreck", "Crashed Factory-ship hull-scar",
        "long diagonal gouge from (%d,%d) to the buried prow (%d,%d)"
        % (tail[0], tail[1], nose[0], nose[1]),
        "THE anchor set-piece of the campaign: the derelict the Jawa-analog "
        "crew scavenges. A narrowing metal/concrete scar with a churned-earth "
        "gouge and debris field reads unmistakably as a ship that came in hard "
        "and skidded. It gives the map a narrative spine and a central objective.",
        cells=c, features=feats,
        notes=["Layer: salvageable hull plating, a sealed cargo bay (loot), "
               "dormant factory mechs, and Jawa scavenger camp hooks.",
               "This is the 'why this map' — expedition destination, not free "
               "loot: mechs + structural collapse gate the reward."])]


OPERATORS = {
    "eco": op_ecological,
    "tactical": op_tactical,
    "mine": op_mine,
    "refinery": op_refinery,
    "droid": op_droid,
    "cavern": op_cavern,
    "wreck": op_wreck,
}
# a sensible default order (eco first to clean up, big set-pieces last)
DEFAULT_ORDER = ["eco", "tactical", "cavern", "mine", "refinery", "droid",
                 "wreck"]


# ==========================================================================
# DRIVER
# ==========================================================================
def run(base_path, out_dir, ops, scale, seed):
    base = GameMap.load_json(base_path)
    stem = os.path.splitext(os.path.basename(base_path))[0]
    if stem.endswith(".map"):
        stem = stem[:-4]
    rng = random.Random(seed)
    ctx = {"rng": rng, "base": base}

    a = analyze(base)
    improved = base.copy()
    # re-point features list to a fresh copy (keep the base's existing structs)
    improved.features = list(base.features)

    all_changes = []
    for op in ops:
        fn = OPERATORS[op]
        chs = fn(a, improved, ctx)
        for ch in chs:
            for feat in ch.features:
                improved.add_feature(feat.get("kind", "relic"),
                                     feat["x"], feat["z"],
                                     feat.get("label", ""))
        all_changes.extend(chs)

    improved.name = base.name + "_improved"

    # ---- write artifacts ----
    os.makedirs(out_dir, exist_ok=True)
    jmap = os.path.join(out_dir, "%s_improved.map.json" % stem)
    improved.save_json(jmap)
    after_png = os.path.join(out_dir, "%s_improved.png" % stem)
    render(improved, after_png, scale=scale,
           title="IMPROVED: %s" % base.name)
    ba_png = os.path.join(out_dir, "%s_beforeafter.png" % stem)
    render_pair(base, improved, ba_png, scale=scale,
                titles=("BEFORE: %s" % base.name, "AFTER"))

    # ---- report ----
    total_cells = sum(c.cells for c in all_changes)
    md = []
    md.append("# Map improvement report — `%s`\n" % base.name)
    md.append("Generated by `Utils/Map_improver.py` (practice agent). "
              "Base map: `%s` (%d×%d). Seed %d.\n"
              % (os.path.basename(base_path), base.w, base.h, seed))
    md.append("## What the agent saw (analysis)\n")
    md.append("- **Dominant terrain family:** %s" % a["dominant_family"])
    md.append("- **Open buildable cells:** %d; best base site ≈ (%d, %d)"
              % (len(a["open_cells"]), int(a["open_centroid"][0]),
                 int(a["open_centroid"][1])))
    md.append("- **Water:** %s%s"
              % ("fresh " if a["has_fresh"] else "",
                 "saline" if a["has_saline"] else
                 ("none" if not a["has_fresh"] else "")))
    md.append("- **Rock/mountain cells:** %d" % len(a["rock_cells"]))
    md.append("- **Edge openness (approach lanes):** "
              + ", ".join("%s %.0f%%" % (k, 100 * v)
                          for k, v in a["edges"].items()))
    md.append("- **Existing structures on base map:** %d\n"
              % len(a["structures"]))

    md.append("## Changes (what / where / why)\n")
    md.append("Total terrain cells altered: **%d** across **%d** improvements.\n"
              % (total_cells, len(all_changes)))
    for i, c in enumerate(all_changes, 1):
        md.append("### %d. %s  _(op: `%s`, %d cells)_\n" %
                  (i, c.what, c.op, c.cells))
        md.append("- **Where:** %s" % c.where)
        md.append("- **Why:** %s" % c.why)
        if c.features:
            md.append("- **Set-piece markers:** "
                      + ", ".join("%s @(%d,%d)" % (f.get("label", f["kind"]),
                                                   f["x"], f["z"])
                                  for f in c.features))
        if c.notes:
            md.append("- **Pawn / item layering notes:**")
            for n in c.notes:
                md.append("    - %s" % n)
        md.append("")

    md.append("## Legend (feature markers on the AFTER render)\n")
    md.append("wreck = red · mine = purple · refinery = amber · droid = teal · "
              "cavern mouth = violet · relic/loot = gold · hazard = magenta · "
              "structure/pawn = dark/red dots.\n")
    md.append("## Honest caveats\n")
    md.append("- This is a **semantic** map (terrain *names* we assign), not a "
              "live save — the shortHash reversal problem is intentionally out "
              "of scope for this practice pass.\n")
    md.append("- Terrain names are drawn from the campaign's verified "
              "`biome_terrain_palette.md`; a few crafted floors (`MetalTile`, "
              "`AncientConcrete`) are generic stand-ins for wreck/ruin flooring "
              "and would map to specific mod defs when made real.\n")
    md_path = os.path.join(out_dir, "%s_improvement.md" % stem)
    with open(md_path, "w") as fh:
        fh.write("\n".join(md))

    jchanges = os.path.join(out_dir, "%s_improvement.json" % stem)
    with open(jchanges, "w") as fh:
        json.dump({"base": os.path.basename(base_path), "seed": seed,
                   "analysis": {
                       "dominant_family": a["dominant_family"],
                       "open_cells": len(a["open_cells"]),
                       "open_centroid": a["open_centroid"],
                       "has_fresh": a["has_fresh"],
                       "has_saline": a["has_saline"],
                       "rock_cells": len(a["rock_cells"]),
                       "edges": a["edges"]},
                   "total_cells_changed": total_cells,
                   "changes": [c.to_dict() for c in all_changes]}, fh, indent=2)

    # ---- console ----
    print("Improved '%s': %d changes, %d cells altered." %
          (base.name, len(all_changes), total_cells))
    for c in all_changes:
        print("  [%-9s] %-38s %s" % (c.op, c.what, c.where))
    print("\nBefore/after: %s" % ba_png)
    print("Report:       %s" % md_path)
    return ba_png, md_path


def main():
    ap = argparse.ArgumentParser(description="creative RimWorld map improver")
    ap.add_argument("base", help="base map (mapkit .map.json)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--scale", type=int, default=5)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--ops", default="all",
                    help="comma list from: " + ",".join(OPERATORS) +
                         " (or 'all')")
    args = ap.parse_args()

    if args.ops == "all":
        ops = [o for o in DEFAULT_ORDER]
    else:
        ops = [o.strip() for o in args.ops.split(",") if o.strip() in OPERATORS]
    out_dir = args.out or os.path.dirname(os.path.abspath(args.base))
    run(args.base, out_dir, ops, args.scale, args.seed)


if __name__ == "__main__":
    main()
