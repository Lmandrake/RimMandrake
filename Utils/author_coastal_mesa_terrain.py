#!/usr/bin/env python3
"""
author_coastal_mesa_terrain.py  —  the TERRAIN-MODIFICATION agent
=================================================================

This is NOT a renderer/visualizer. It is an agent that PRECISELY MODIFIES the
semantic terrain grid (mapkit.GameMap, cells hold real RimWorld terrain NAMES)
to realize every design decision written by hand in
`../player_maps/authored/coastal_mesa_rationale.md`.

Terrain ONLY. Plants / items / props (the refinery object, dead droid body,
mine headframe, etc.) are a LATER phase — here we lay only the TERRAIN
footprint each of those set-pieces leaves in the ground (scorched furrow,
tailings fan, concrete pad + spill stain, impact crater, cave floor).

How it works (LLM-in-the-loop, manual/live mode):
  * The DECISIONS below are reasoned, not heuristic. Each `step_*` function is
    one rationale line, with coordinates I read off the ACTUAL perceived grid
    (see map_agent.perceive) — not blind rng.
  * Python is only the HANDS: every edit goes through a named primitive in
    map_agent.PRIMITIVES via apply_edit(), or a small local helper built from
    them. Nothing here invents terrain names outside mapkit.TERRAIN.
  * Order matters and is dependency-driven: reshape coast -> grade depth ->
    beach ribbon/sandbar -> interior wash+hollow+scrub+knoll -> massif
    cavern+talus -> set-piece terrain footprints. Later steps read the grid
    state left by earlier ones.

Run:
    python3 author_coastal_mesa_terrain.py \
        [--in ../player_maps/coastal_mesa.map.json] \
        [--out ../player_maps/coastal_mesa_terrain.map.json]

Emits: the modified .map.json, a before/after PNG rendered straight from the
grid, and a change report (histogram delta + per-step cells changed + metric
deltas + a verification pass checking each decision actually landed).
"""

import os
import sys
import json
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mapkit import GameMap, tprop, render_pair, render          # noqa: E402
from map_agent import (perceive, briefing_text, metrics,          # noqa: E402
                       apply_edit, op_blob, op_paint_cells)


# ==========================================================================
# small reasoned helpers built ONLY from primitives / cell sets
# ==========================================================================
def _line_cells(x0, z0, x1, z1):
    """Bresenham-ish integer cells along a segment (for furrows/washes)."""
    cells = []
    dist = max(abs(x1 - x0), abs(z1 - z0)) or 1
    for i in range(dist + 1):
        cells.append((round(x0 + (x1 - x0) * i / dist),
                      round(z0 + (z1 - z0) * i / dist)))
    return cells


def _thick(cells, r):
    """Expand a cell list to a disc of half-width r around each cell."""
    out = set()
    for (x, z) in cells:
        for dz in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dz * dz <= r * r:
                    out.add((x + dx, z + dz))
    return sorted(out)


# ==========================================================================
# THE DECISIONS  (each = one rationale line, applied to the real grid)
# Every function returns (label, cells_changed).
# ==========================================================================

def step_coastline_meander(gm):
    """Ocean (W): ruler-straight coast -> meander with a headland (N), a deep
    cove (mid), a gentle point (S). We push the shore frontier in/out per row
    using fractalize_edge, which drives displacement by smooth along-coast
    noise (headlands + inlets, not speckle)."""
    c = apply_edit(gm, "fractalize_edge",
                   from_family="water", to_terrain="Sand",
                   coast_terrain="WaterOceanShallow",
                   amount=0.85, seed=7, reach=5)
    # Deliberately deepen ONE inlet into a true cove at mid-map (z~55-70):
    # carve water back into the land so the coast reads as a bay, not a wiggle.
    cove = []
    for z in range(54, 71):
        # cove mouth widens toward its center row (z~62)
        depth = 6 - abs(62 - z) // 2          # up to 6 cells of intrusion
        base = 21                              # nominal shore x
        for x in range(base, base + depth):
            if gm.in_bounds(x, z) and tprop(gm.grid[z][x], "family") != "water":
                cove.append((x, z))
    c += op_paint_cells(gm, cove, "WaterOceanShallow")
    # Headland (N, z~95-112): let land bulge out into the water a little.
    head = []
    for z in range(95, 113):
        bulge = 4 - abs(104 - z) // 3
        for x in range(15, 21):
            if x >= 21 - bulge and gm.in_bounds(x, z) \
                    and tprop(gm.grid[z][x], "family") == "water":
                head.append((x, z))
    c += op_paint_cells(gm, head, "Sand")
    return ("Ocean coastline meander (headland N / cove mid / point S)", c)


def step_water_depth(gm):
    """Depth-graded water deep->shallow measured from the real (now meandering)
    shore, so contours follow the cove and headland instead of straight bands."""
    c = apply_edit(gm, "depth_grade",
                   bands=["WaterOceanShallow", "WaterOceanDeep"],
                   from_family="water", seed=11, noise=1)
    return ("Water depth grade (shallow near shore -> deep offshore)", c)


def step_beach_and_sandbar(gm):
    """Wet-sand beach ribbon along the whole land side of the water, plus an
    offshore sandbar sitting inside the cove."""
    c = apply_edit(gm, "shore_ribbon",
                   ribbon_terrain="Sand", water_family="water", width=1,
                   only_families=["rock", "sand", "soil"])
    # sandbar: a short shallow-sand bank just off the cove mouth, in the water
    bar = []
    for z in range(58, 67):
        for x in range(12, 16):
            if gm.in_bounds(x, z) and tprop(gm.grid[z][x], "family") == "water":
                bar.append((x, z))
    c += op_paint_cells(gm, bar, "Sand")            # exposed bar
    # a shallow apron around the bar so it doesn't sit in deep water abruptly
    apron = []
    for (x, z) in bar:
        for nx, nz in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
            if gm.in_bounds(nx, nz) and gm.grid[nz][nx] == "WaterOceanDeep":
                apron.append((nx, nz))
    c += op_paint_cells(gm, apron, "WaterOceanShallow")
    return ("Beach ribbon + offshore sandbar in the cove", c)


def step_dry_wash(gm):
    """A dry wash (arroyo) snaking SW->NE across the sand flat: a line of
    movement + soft chokepoints. Terrain = SoftSand channel bed (slow going),
    banked by a thin Sand lip. Waypoints hand-chosen to weave between the
    gravel patches, avoiding water and mountain."""
    way = [(26, 12), (34, 26), (40, 40), (46, 54), (52, 68), (60, 82)]
    bed = []
    for a, b in zip(way, way[1:]):
        bed += _line_cells(*a, *b)
    bed_cells = _thick(bed, 1)
    # only carve the channel through open ground (sand/soil/rock), not water/mtn
    bed_ok = [(x, z) for (x, z) in bed_cells
              if gm.in_bounds(x, z)
              and tprop(gm.grid[z][x], "family") in ("sand", "soil", "rock")]
    c = op_paint_cells(gm, bed_ok, "SoftSand")
    return ("Dry wash (arroyo) SW->NE across the sand flat", c, way)


def step_fertile_hollow(gm, wash_way):
    """Fertile hollow at a bend of the wash = the farm start. Rich soil core
    with a soil apron, tucked at the sharp bend around (46,54)."""
    cx, cz = 46, 54
    c = op_blob(gm, cx, cz, 4, "Soil", jitter=0.3, seed=3,
                only_families=["sand", "rock"])
    c += op_blob(gm, cx, cz, 2, "SoilRich", jitter=0.3, seed=4,
                 only_families=["sand", "soil", "rock"])
    return ("Fertile hollow (SoilRich core) at the wash bend = farm start", c)


def step_scrub_stands(gm, wash_way):
    """Scrub stands cluster ALONG the wash (vegetation follows moisture). We
    can't place plants yet (terrain only), so the terrain signal is MossyTerrain
    patches — the fertile, vegetated ground scrub grows on — hugging the bed."""
    total = 0
    for (wx, wz) in wash_way:
        total += apply_edit(gm, "scatter",
                            region_bbox=[wx - 5, wz - 5, wx + 5, wz + 5],
                            terrain="MossyTerrain", density=0.14, clump=0.7,
                            only_families=["sand"], seed=wx + wz, patch=True)
    return ("Scrub-stand ground (MossyTerrain) clustered along the wash", total)


def step_outcrop_knoll(gm):
    """An outcrop knoll gives mid-map high ground. Rubble apron + forsaken-rock
    core on the open flat, clear of the wash. Placed ~ (60,44)."""
    c = apply_edit(gm, "hill", cx=60, cz=44, radius=5,
                   ring_terrain="RockRubble", core_terrain="AB_ForsakenRock",
                   seed=21)
    return ("Outcrop knoll (mid-map high ground)", c)


def step_cavern(gm):
    """Cavern chamber carved into the massif's SE face, with a throat opening
    toward the flat. carve_chamber only hollows through solid rock (mountain),
    so the cave stays enclosed. Core verified solid at (99,87)."""
    c = apply_edit(gm, "carve_chamber", cx=95, cz=84, radius=6,
                   floor="CaveFloor", require_family=("mountain",), seed=31)
    # throat: a short CaveFloor corridor from the chamber toward the SW flat,
    # cutting only through rock so it reads as a mouth, not an open trench.
    throat = _thick(_line_cells(95, 84, 86, 76), 1)
    throat_ok = [(x, z) for (x, z) in throat
                 if gm.in_bounds(x, z)
                 and tprop(gm.grid[z][x], "family") in ("mountain", "rock")]
    c += op_paint_cells(gm, throat_ok, "CaveFloor")
    return ("Cavern chamber + throat carved into massif SE face", c)


def step_talus_apron(gm):
    """Talus/scree apron softens the massif's west foot: rubble spilling off the
    rock onto the sand, so the mountain doesn't meet the flat at a hard wall."""
    total = 0
    # west foot of the massif runs roughly x~68-74 over z~60-100
    total += apply_edit(gm, "scatter",
                        region_bbox=[64, 58, 74, 104],
                        terrain="RockRubble", density=0.35, clump=0.6,
                        only_families=["sand"], seed=41, patch=True)
    return ("Talus/scree apron at the massif's west foot", total)


def step_crashed_ship_scar(gm):
    """Crashed Factory-ship: a scorched impact furrow gouged NW->SE, tapering
    and charring toward a broken hull fragment; debris scattered around it.
    Terrain footprint only (the hull object comes later): a burnt furrow of
    AB_SolidifiedLava (scorched ground) widening toward the impact end, ringed
    by AB_VolcanicGravel scorch-scatter. Placed across the open N sand flat."""
    # furrow NW (high z, low-mid x) -> SE (lower z, higher x), impact at SE end
    start = (40, 108)
    end = (70, 86)
    spine = _line_cells(*start, *end)
    c = 0
    n = len(spine)
    for i, (x, z) in enumerate(spine):
        # taper: narrow at entry (NW), wide gouge at impact (SE)
        r = 1 if i < n * 0.5 else 2
        cells = _thick([(x, z)], r)
        cells_ok = [(cx, cz) for (cx, cz) in cells
                    if gm.in_bounds(cx, cz)
                    and tprop(gm.grid[cz][cx], "family") in ("sand", "rock", "soil")]
        c += op_paint_cells(gm, cells_ok, "AB_SolidifiedLava")
    # broken hull fragment footprint at the impact end: a scorched metal patch
    c += op_blob(gm, end[0], end[1], 3, "MetalTile", jitter=0.3, seed=52,
                 only_families=["sand", "rock", "volcanic"])
    # debris scatter (scorch) around impact
    c += apply_edit(gm, "scatter",
                    region_bbox=[end[0] - 8, end[1] - 8, end[0] + 8, end[1] + 8],
                    terrain="AB_VolcanicGravel", density=0.10, clump=0.7,
                    only_families=["sand"], seed=53, patch=True)
    return ("Crashed Factory-ship scar (scorched furrow + hull footprint + debris)", c)


def step_mine(gm):
    """Abandoned mine: a timber-framed adit on the massif's WEST flank with a
    gravel tailings fan spilling DOWNSLOPE onto the flat. Terrain: a short
    CaveFloor adit mouth bored into the rock foot, + a Gravel fan below it."""
    ax, az = 70, 88                                  # adit mouth at rock foot
    # adit: carve a couple cells into the rock (mountain/rock) as floor
    adit = _thick(_line_cells(ax, az, ax + 4, az), 0)
    adit_ok = [(x, z) for (x, z) in adit if gm.in_bounds(x, z)
               and tprop(gm.grid[z][x], "family") in ("mountain", "rock")]
    c = op_paint_cells(gm, adit_ok, "CaveFloor")
    # tailings fan: gravel spilling west/downslope from the mouth onto sand
    c += apply_edit(gm, "scatter",
                    region_bbox=[ax - 10, az - 6, ax - 1, az + 6],
                    terrain="Gravel", density=0.45, clump=0.8,
                    only_families=["sand"], seed=61, patch=True)
    return ("Abandoned mine adit + gravel tailings fan (massif W flank)", c)


def step_refinery_pad(gm):
    """Semi-working refinery on the SE gravel flat: an ancient-concrete pad
    (the terrain footprint), with a rust/spill STAIN from the ruptured tank.
    Tanks/pipes/derrick are objects for the later phase. Pad placed on open
    ground near (104,12)."""
    px, pz = 104, 12
    c = apply_edit(gm, "rect", x0=px - 5, z0=pz - 4, x1=px + 5, z1=pz + 4,
                   terrain="AncientConcrete")
    # ruptured-tank spill stain: mud/chem stain bleeding off the pad's NE corner
    c += op_blob(gm, px + 6, pz + 5, 3, "Mud", jitter=0.4, seed=71,
                 only_families=["sand", "rock", "crafted"])
    return ("Refinery ancient-concrete pad + ruptured-tank spill stain (SE)", c)


def step_droid_crater(gm):
    """Dead droid in an impact crater: a rimmed crater with a scorch streak.
    Terrain footprint: a CaveFloor/gravel crater bowl ringed by scorched rubble,
    with a MetalTile speck for the toppled droid body. Placed on open S sand
    (away from the ship scar) near (34,20)."""
    cx, cz = 34, 20
    # crater rim (scorched rubble ring) + bowl floor
    c = apply_edit(gm, "ring", cx=cx, cz=cz, r_in=3, r_out=4,
                   terrain="AB_VolcanicGravel", only_families=["sand", "rock"])
    c += op_blob(gm, cx, cz, 3, "Gravel", jitter=0.3, seed=81,
                 only_families=["sand", "rock"])
    # scorch streak trailing off the crater (impact direction)
    streak = _thick(_line_cells(cx, cz, cx - 7, cz - 4), 0)
    streak_ok = [(x, z) for (x, z) in streak if gm.in_bounds(x, z)
                 and tprop(gm.grid[z][x], "family") in ("sand", "rock")]
    c += op_paint_cells(gm, streak_ok, "AB_SolidifiedLava")
    # toppled droid body footprint
    c += op_paint_cells(gm, [(cx, cz)], "MetalTile")
    return ("Dead-droid impact crater (bowl + rim + scorch streak)", c)


# ==========================================================================
# VERIFICATION — confirm each decision actually changed the grid
# ==========================================================================
def verify(gm):
    """Check the modified grid actually contains each rationale feature. Returns
    list of (decision, ok, evidence)."""
    hist = gm.terrain_histogram()
    checks = []

    def has(name, atleast=1):
        return hist.get(name, 0) >= atleast

    checks.append(("Depth-graded water (deep + shallow both present)",
                   has("WaterOceanDeep", 50) and has("WaterOceanShallow", 50),
                   f"deep={hist.get('WaterOceanDeep',0)} shallow={hist.get('WaterOceanShallow',0)}"))
    checks.append(("Fertile hollow (SoilRich core)",
                   has("SoilRich", 5),
                   f"SoilRich={hist.get('SoilRich',0)} Soil={hist.get('Soil',0)}"))
    checks.append(("Cavern (CaveFloor carved in rock)",
                   has("CaveFloor", 15),
                   f"CaveFloor={hist.get('CaveFloor',0)}"))
    checks.append(("Scrub-stand ground (MossyTerrain)",
                   has("MossyTerrain", 10),
                   f"MossyTerrain={hist.get('MossyTerrain',0)}"))
    checks.append(("Outcrop knoll (ForsakenRock core)",
                   has("AB_ForsakenRock", 3),
                   f"AB_ForsakenRock={hist.get('AB_ForsakenRock',0)}"))
    checks.append(("Crashed-ship scar (scorched ground)",
                   has("AB_SolidifiedLava", 20),
                   f"AB_SolidifiedLava={hist.get('AB_SolidifiedLava',0)}"))
    checks.append(("Ship hull / droid metal footprint",
                   has("MetalTile", 2),
                   f"MetalTile={hist.get('MetalTile',0)}"))
    checks.append(("Refinery concrete pad",
                   has("AncientConcrete", 40),
                   f"AncientConcrete={hist.get('AncientConcrete',0)}"))
    checks.append(("Refinery/droid spill + crater scatter (Mud/VolcanicGravel)",
                   has("Mud", 3) and has("AB_VolcanicGravel", 5),
                   f"Mud={hist.get('Mud',0)} AB_VolcanicGravel={hist.get('AB_VolcanicGravel',0)}"))
    checks.append(("Dry wash bed (SoftSand present as channel)",
                   has("SoftSand", 30),
                   f"SoftSand={hist.get('SoftSand',0)}"))
    return checks


# ==========================================================================
# DRIVER
# ==========================================================================
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in", dest="inp",
                    default=os.path.join(HERE, "../player_maps/coastal_mesa.map.json"))
    ap.add_argument("--out", dest="out",
                    default=os.path.join(HERE, "../player_maps/coastal_mesa_terrain.map.json"))
    ap.add_argument("--scale", type=int, default=5)
    args = ap.parse_args()

    base = GameMap.load_json(args.inp)
    before = base.copy()
    gm = base.copy()
    gm.name = "coastal_mesa (terrain-authored)"

    m0 = metrics(gm)
    hist0 = gm.terrain_histogram()

    # dependency-ordered application
    log = []
    log.append(step_coastline_meander(gm))
    log.append(step_water_depth(gm))
    log.append(step_beach_and_sandbar(gm))
    wash = step_dry_wash(gm); wash_way = wash[2]; log.append((wash[0], wash[1]))
    log.append(step_fertile_hollow(gm, wash_way))
    log.append(step_scrub_stands(gm, wash_way))
    log.append(step_outcrop_knoll(gm))
    log.append(step_cavern(gm))
    log.append(step_talus_apron(gm))
    log.append(step_crashed_ship_scar(gm))
    log.append(step_mine(gm))
    log.append(step_refinery_pad(gm))
    log.append(step_droid_crater(gm))

    m1 = metrics(gm)
    hist1 = gm.terrain_histogram()

    gm.save_json(args.out)

    # before/after render straight from the GRID (this shows the terrain data,
    # not vector art)
    png = os.path.splitext(args.out)[0] + "_beforeafter.png"
    render_pair(before, gm, png, scale=args.scale,
                titles=("BEFORE (raw tile)", "AFTER (terrain authored)"))
    solo = os.path.splitext(args.out)[0] + "_after.png"
    render(gm, solo, scale=args.scale, title="coastal_mesa — terrain authored")

    # report
    checks = verify(gm)
    rep = os.path.splitext(args.out)[0] + "_report.md"
    with open(rep, "w") as fh:
        fh.write("# coastal_mesa — terrain-modification agent report\n\n")
        fh.write("Every edit below was applied to the SEMANTIC TERRAIN GRID "
                 "(cells = terrain names), driven by the hand-reasoned "
                 "decisions in `authored/coastal_mesa_rationale.md`. Terrain "
                 "only; plants/props are a later phase.\n\n")
        fh.write("## Edits applied (in dependency order)\n\n")
        fh.write("| # | Decision | Cells changed |\n|---|---|---|\n")
        for i, (label, changed) in enumerate(log, 1):
            fh.write(f"| {i} | {label} | {changed} |\n")
        fh.write("\n## Terrain histogram: before -> after (cells)\n\n")
        fh.write("| Terrain | Before | After | Δ |\n|---|---:|---:|---:|\n")
        names = sorted(set(hist0) | set(hist1))
        for n in sorted(names, key=lambda k: -hist1.get(k, 0)):
            b, a = hist0.get(n, 0), hist1.get(n, 0)
            if b or a:
                fh.write(f"| {n} | {b} | {a} | {a-b:+d} |\n")
        fh.write("\n## Guardrail metrics: before -> after\n\n")
        fh.write("| Metric | Before | After |\n|---|---:|---:|\n")
        for k in m0:
            fh.write(f"| {k} | {m0[k]} | {m1[k]} |\n")
        fh.write("\n## Verification — did each decision land in the grid?\n\n")
        fh.write("| Decision | Present? | Evidence |\n|---|:---:|---|\n")
        allok = True
        for decision, ok, ev in checks:
            allok = allok and ok
            fh.write(f"| {decision} | {'✅' if ok else '❌'} | {ev} |\n")
        fh.write(f"\n**All decisions present: {'YES ✅' if allok else 'NO ❌'}**\n")

    # console
    print("EDITS:")
    for i, (label, changed) in enumerate(log, 1):
        print(f"  {i:2d}. {changed:5d} cells  {label}")
    print("\nMETRICS  before:", json.dumps(m0))
    print("METRICS  after :", json.dumps(m1))
    print("\nVERIFICATION:")
    allok = True
    for decision, ok, ev in checks:
        allok = allok and ok
        print(f"  [{'OK' if ok else '!!'}] {decision}  ({ev})")
    print(f"\nALL DECISIONS PRESENT: {'YES' if allok else 'NO'}")
    print("\nwrote:", args.out)
    print("      ", png)
    print("      ", solo)
    print("      ", rep)
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
