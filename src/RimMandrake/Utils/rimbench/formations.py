"""Formations: composed set-pieces built from scatter + build + terrain.

This is where the ambition lives. Each formation is a recipe that takes a
centre point and produces something that reads as *found*, not placed.

Everything here is **mod-list independent** — vanilla defs only — so a
formation drops onto a 3-mod bench map or a 568-mod campaign identically. Where
a formation would be better with modded content, it takes the def as a
parameter rather than hardcoding it.

DESIGN PRINCIPLES, learned from the crater that did not work

1. **Silhouette before detail.** Get the shape right with zones and dithered
   edges; sprinkling detail on a bad silhouette does not rescue it.
2. **Ground colour is most of the read.** Objects scattered on unchanged grass
   look like litter. Where terrain cannot be painted, use a FLOOR to change the
   ground — it also clears the vegetation, which is half the battle.
3. **Asymmetry everywhere.** Squash, rotate, lobe. A round thing reads as a
   stamp.
4. **Density gradients, not uniform fills.** Real ruin is dense at the core and
   thins outward, with outliers well beyond the main mass.
"""
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import place
import scatter
from build import Blueprint, D, WALL, DOOR
from terrain import TerrainPainter

ASH = "Filth_Ash"
RUBBLE = "Filth_RubbleRock"
SLAG = "ChunkSlagSteel"
STEEL = "Steel"


# --------------------------------------------------------------- crater
# Ground palette, outermost first. Painted in this order so that where zones
# touch, the inner one wins — a crater reads from its centre outward.
#
# 🔑 TERRAIN CHOICE IS VEGETATION CONTROL. Verified live 2026-08-12: SetTerrain
# destroys a plant if and only if the plant cannot grow on the NEW terrain.
# Grass survives Gravel and dies on Sand, PackedDirt, rock and water; painting a
# cell its own existing terrain is a no-op and kills nothing. So the palette is
# chosen for BOTH colour and what it does to the plants standing there:
#
#   melt   Sand        sterile — nothing survives the middle of an impact
#   bowl   PackedDirt  sterile, and reads as compacted blast floor
#   rim    Soil        usually a no-op over soil; the rim SHOULD stay alive
#   ejecta Gravel      keeps the vegetation — debris scattered over living ground
#
# The bowl was Gravel until this was measured, which would have left a crater
# floor full of healthy grass. Do not swap these for their colour alone.
CRATER_GROUND = [("ejecta", "gravel"), ("rim", "soil"),
                 ("bowl", "packed"), ("melt", "sand")]


def crater(s, cx, cz, radius=12, seed=7, paint_ground=True,
           floor_the_bowl=False, reversible=False):
    """An impact crater: melt sheet, bowl, rim, ejecta rays.

    `paint_ground` paints REAL terrain through the companion — the thing this
    formation always wanted. Principle 2 says ground colour is most of the read,
    and until 2026-08-12 the only way to change it was to lay a floor, which
    left a deconstructable grey slab where soil should be. Now the whole
    four-zone ground goes down as one `jawa/set_terrain_batch` call.

    `floor_the_bowl` is kept, and is now OFF by default. Its remaining job is
    not colour but DESTRUCTION: flooring is the only proven way to clear the
    bushes and grass standing inside the crater. Whether painting terrain
    also clears them is an open question — see below — so turn this on if the
    site is vegetated and you cannot afford to find out the hard way.

    `reversible` captures every cell's original terrain first so `restore()` is
    exact. It costs ONE `get_cell_info` PER CELL — ~410 calls, ~7 s for a
    radius-12 crater, far more than the paint itself. Worth it on a live colony,
    wasteful on a scratch map.

    ⚠️ OPEN, needs the game: does `TerrainGrid.SetTerrain` destroy the plants
    standing on a cell? RimWorld destroys plants when terrain becomes
    unwalkable (water), but Sand and Gravel are perfectly plantable, so the
    likely answer is NO and a painted crater keeps its bushes. Unverified
    either way — do not assume. Queued for the next load.
    """
    tp = TerrainPainter(s)
    field = list(scatter.radial_field(cx, cz, radius, falloff=1.0,
                                      squash=0.82, rotation=0.6,
                                      lobe_count=3, lobe_dir=0.6,
                                      lobe_strength=0.35, reach=1.6))
    z = scatter.zones(field, [("melt", 0.72, 1.01),
                              ("bowl", 0.40, 0.72),
                              ("rim",  0.12, 0.40),
                              ("ejecta", 0.0, 0.12)])

    ground = {}
    if paint_ground:
        for zone, terrain in CRATER_GROUND:
            for x, zz, _d in z[zone]:
                ground[(x, zz)] = terrain
        if ground and tp.route() != "none":
            if reversible:
                tp.capture(ground)
            tp.paint_map(ground)

    if floor_the_bowl:
        tp.floor_cells([c for c in z["melt"]], kind="concrete")
        tp.floor_cells(scatter.pick(z["bowl"], 0.55, seed + 3), kind="concrete")

    # Every object is queued and sent in ONE call. Before batching, this section
    # was ~100 separate spawns and 98% of the formation's wall-clock -- the
    # terrain it sits on is a single hop.
    p = place.Placer(s)
    p.extend(ASH, scatter.pick(z["melt"], 0.95, seed))
    p.extend(ASH, scatter.pick(z["bowl"], 0.70, seed + 1))
    p.extend(RUBBLE, scatter.clumps(scatter.pick(z["rim"], 0.75, seed + 2),
                                    seed + 5, clump_scale=3.0, threshold=0.45))
    p.extend(SLAG, scatter.pick(z["ejecta"], 0.30, seed + 4))
    queued = len(p.queue)
    placed = p.flush()

    return {"placed": placed, "queued": queued, "ground": len(ground),
            "terrain": tp.report(), "objects": p.report(),
            "painter": tp, "placer": p}


# ------------------------------------------------------------ ship wreck
def wreck(s, cx, cz, length=18, width=7, rotation=0.0, seed=11,
          hull=WALL, debris=SLAG):
    """A broken hull: a floored deck, a partial shell, and a debris trail.

    Gaps in the shell are noise-driven, so the break reads as damage rather
    than as a wall with holes punched at regular intervals. The debris trail
    follows the impact direction.
    """
    tp = TerrainPainter(s)
    deck = []
    for dx in range(-length // 2, length // 2 + 1):
        for dz in range(-width // 2, width // 2 + 1):
            # taper the nose so it is a hull, not a box
            taper = 1.0 - abs(dx) / float(length * 0.7)
            if abs(dz) <= max(1, width * 0.5 * taper):
                c, sn = math.cos(rotation), math.sin(rotation)
                deck.append((cx + int(dx * c - dz * sn), cz + int(dx * sn + dz * c)))
    tp.floor_cells(deck, kind="metal")

    bp = Blueprint(s, "wreck hull")
    edge = set()
    for x, z in deck:
        for ox, oz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + ox, z + oz) not in set(deck):
                edge.add((x, z))
    for x, z in sorted(edge):
        if scatter.noise(x, z, seed) > 0.38:        # blow holes in the shell
            bp.add(hull, x, z, 1, 1, "hull")
    bp.build(verbose=False)

    trail = scatter.walk(cx, cz, cx + int(math.cos(rotation) * length * 2),
                         cz + int(math.sin(rotation) * length * 2),
                         wander=0.5, seed=seed + 2, width=2)
    p = place.Placer(s)
    p.extend(debris, [(x, z) for x, z in trail
                      if scatter.noise(x, z, seed + 9) < 0.35])
    # Scorch the ground the hull ploughed through. Sand kills the vegetation it
    # lands on (Gravel would not — see CRATER_GROUND), so the trail reads as a
    # gouge rather than as litter dropped on tidy grass.
    tp.paint_map({(x, z): "sand" for x, z in trail})
    n = p.flush()
    return {"deck": len(deck), "hull": len(edge), "debris": n,
            "terrain": tp.report(), "objects": p.report()}


# ---------------------------------------------------------------- cavern
def cavern(s, cx, cz, chambers=3, radius=9, seed=23, floor_terrain="rock_smooth",
           floor_kind=None):
    """A chambered cavern system: blobs joined by wandering tunnels.

    Chambers are irregular blobs, not circles, and tunnels wander.

    The floor is now PAINTED as smooth natural rock in one call, not laid as a
    built floor. That is both cheaper and more honest: a cavern floor is stone,
    not a deconstructable slab a colonist could rip up. It also clears the
    vegetation, since nothing grows on rock. Pass `floor_kind` as well if you
    want an actual built floor on top.

    ⚠️ Stone terrain is generated per rock type at runtime, so `rock_smooth`
    resolves to a Sandstone default that may not match this map's stone. Read a
    nearby cell and pass the map's own `<Stone>_Smooth` if it matters.

    Terrain does not block movement. The walls still have to be BUILT, so this
    returns `wall_cells` for a caller that wants to place real rock.
    """
    tp = TerrainPainter(s)
    all_cells, centres = set(), []
    ang = 0.0
    x, z = cx, cz
    for i in range(chambers):
        r = radius * (0.7 + 0.5 * scatter.noise(i, seed, 3))
        b = scatter.blob(x, z, r, seed=seed + i, roughness=0.5)
        centres.append((x, z))
        for cx2, cz2, _d in b:
            all_cells.add((cx2, cz2))
        ang += 1.4 + scatter.noise(i, i, seed) * 1.2
        x += int(math.cos(ang) * r * 2.1)
        z += int(math.sin(ang) * r * 2.1)
    for i in range(len(centres) - 1):
        for c in scatter.walk(centres[i][0], centres[i][1],
                              centres[i + 1][0], centres[i + 1][1],
                              wander=0.6, seed=seed + i, width=2):
            all_cells.add(c)
    if floor_terrain:
        tp.paint_map({c: floor_terrain for c in all_cells})
    if floor_kind:
        tp.floor_cells(sorted(all_cells), kind=floor_kind)

    interior = set(all_cells)
    walls = set()
    for x, z in interior:
        for ox in (-1, 0, 1):
            for oz in (-1, 0, 1):
                if (x + ox, z + oz) not in interior:
                    walls.add((x + ox, z + oz))
    return {"floor": len(interior), "wall_cells": sorted(walls),
            "chambers": centres, "terrain": tp.report()}


# ----------------------------------------------------------------- outpost
def outpost(s, cx, cz, rooms=3, seed=31):
    """A small settlement: connected rooms with plausible interiors.

    Rooms are placed on a jittered grid, each validated before building, so an
    obstructed site loses one room rather than producing a half-built mess.
    Better than a single big box because silhouette variety is what makes a
    settlement read as built-over-time.
    """
    built = []
    for i in range(rooms):
        w = 9 + int(scatter.noise(i, seed, 1) * 5)
        h = 8 + int(scatter.noise(seed, i, 2) * 4)
        ox = int((scatter.noise(i, 7, seed) - 0.5) * 6)
        oz = int((scatter.noise(7, i, seed) - 0.5) * 6)
        x = cx + (i % 2) * (w + 3) + ox
        z = cz + (i // 2) * (h + 3) + oz
        bp = Blueprint(s, "room %d" % (i + 1))
        bp.room(x, z, w, h, floor="woodplankfloor")
        from build import furnish_bunkroom
        furnish_bunkroom(bp, x, z, w, h)
        ok, _f = bp.plan(verbose=False)
        placed, skipped = bp.build(verbose=False)
        built.append({"x": x, "z": z, "w": w, "h": h,
                      "placed": placed, "skipped": skipped})
    return built


# ------------------------------------------------------------ geyser field
def geyser_field(s, cx, cz, count=5, spread=18, seed=41,
                 vent_def="Filth_Ash", hazard_def=SLAG):
    """Scattered vents with stained ground and debris haloes.

    A stand-in for the explosive-fumes idea: the *placement* logic is real and
    reusable; the defs are parameters, so once a fumes mod exists it drops in
    without touching this function.
    """
    # One Placer across ALL vents, flushed once. Batching per vent would be five
    # calls where one does; the queue exists precisely so a generator can emit
    # objects in whatever order suits it and still pay for a single hop.
    p = place.Placer(s)
    tp = TerrainPainter(s)
    stain = {}
    out = []
    for i in range(count):
        a = scatter.noise(i, seed, 5) * math.tau
        r = spread * (0.3 + 0.7 * scatter.noise(seed, i, 6))
        vx, vz = cx + int(math.cos(a) * r), cz + int(math.sin(a) * r)
        halo = scatter.pick(
            list(scatter.radial_field(vx, vz, 4, falloff=1.6, squash=0.9)),
            0.8, seed + i)
        p.extend(vent_def, halo)
        p.extend(hazard_def, scatter.pick(halo, 0.2, seed + i + 50))
        for x, z, _d in halo:
            stain[(x, z)] = "packed"       # sterile ground around a vent
        out.append((vx, vz, len(halo)))
    tp.paint_map(stain)
    p.flush()
    return {"vents": out, "terrain": tp.report(), "objects": p.report()}
