#!/usr/bin/env python3
"""
map_agent.py  —  toolbox for the LLM-in-the-loop map improver
=============================================================

ARCHITECTURE (per user direction, 2026-08-05)
---------------------------------------------
The earlier all-Python improver was wrong (deleted 2026-08-13): it baked all
judgment into fixed Python heuristics with blind coordinates, so placements
couldn't respond to the actual map — "ridiculous and unjustified." Heuristics
that never look at the map cannot justify where they put things. The correct
design puts the LLM's reasoning
IN the loop each iteration; Python is only the HANDS:

    perceive (Python)  →  decompose + judge + propose (LLM)  →  execute (Python
    primitives, args chosen by the LLM)  →  re-perceive + re-judge (LLM)  →
    retry regions that didn't improve  →  stop when good.

This module provides the three non-reasoning capabilities:
  1. PERCEPTION   — turn a map into an LLM-readable briefing (coarse labeled
                    grid + connected-region segmentation + histogram). The LLM
                    also views the PNG directly with vision.
  2. PRIMITIVES   — a library of parameterized edit operations the LLM calls
                    with map-specific coordinates it reasoned out. Plus a
                    freehand paint escape hatch.
  3. METRICS      — cheap, objective structural measures (transition coherence,
                    fragmentation, diversity). These are GUARDRAILS / tie-break
                    optimizations, NOT the subjective judge. Realism / interest /
                    tactical quality remain the LLM's call.

Nothing here decides WHAT to change or WHERE — that is the LLM's job. This file
just makes those decisions perceivable and executable.

Depends on mapkit.py (palette + GameMap + renderer).
"""

import os
import sys
import math
import json
import random
from collections import Counter, deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapkit import GameMap, tprop, tcolor, TERRAIN, render, render_pair  # noqa

# ==========================================================================
# family → single display glyph for the coarse ASCII briefing
# ==========================================================================
FAMILY_GLYPH = {
    "sand": ".",       # open arid
    "soil": "s",       # fertile
    "rock": ":",       # gravel / rubble / forsaken rock (passable stone)
    "mountain": "#",   # solid rock (impassable)
    "cave": "c",       # hollowed cave floor
    "volcanic": "v",   # lava rock / obsidian
    "mud": "~",        # mud / marsh
    "water": "W",      # any water (see water kind in region detail)
    "crafted": "=",    # asphalt / metal / concrete (built floors)
    "?": "?",
}


# ==========================================================================
# PERCEPTION
# ==========================================================================
def _field(gm, key, default=None):
    return [[tprop(gm.grid[z][x], key, default) for x in range(gm.w)]
            for z in range(gm.h)]


def coarse_grid(gm, cols=32):
    """Downsample the map to a cols-wide grid of family glyphs, majority vote
    per block. Returns (rows list of strings, block_w, block_h). Rows are
    printed TOP (high z) first so it matches the rendered image orientation."""
    w, h = gm.w, gm.h
    rows_n = max(1, round(cols * h / w))
    bw = w / cols
    bh = h / rows_n
    out = []
    for r in range(rows_n):
        z1 = h - 1 - int(r * bh)          # top row = high z
        z0 = h - 1 - int((r + 1) * bh) + 1
        line = []
        for c in range(cols):
            x0 = int(c * bw)
            x1 = int((c + 1) * bw)
            fam = Counter()
            for z in range(max(0, z0), min(h, z1 + 1)):
                for x in range(x0, min(w, x1)):
                    fam[tprop(gm.grid[z][x], "family", "?")] += 1
            top = fam.most_common(1)[0][0] if fam else "?"
            line.append(FAMILY_GLYPH.get(top, "?"))
        out.append("".join(line))
    return out, bw, bh


def segment_regions(gm, min_area=25):
    """Connected-component segmentation by terrain FAMILY (8-conn). Returns a
    list of region dicts sorted by area desc: id, family, area, bbox
    (x0,z0,x1,z1), centroid (cx,cz), dominant terrain name, water kind,
    passable fraction, edge_touch (which map edges it reaches)."""
    w, h = gm.w, gm.h
    fam = _field(gm, "family", "?")
    label = [[-1] * w for _ in range(h)]
    regions = []
    for z in range(h):
        for x in range(w):
            if label[z][x] != -1:
                continue
            f0 = fam[z][x]
            cells = []
            dq = deque([(x, z)])
            label[z][x] = len(regions)
            while dq:
                cx, cz = dq.popleft()
                cells.append((cx, cz))
                for dx in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        if dx or dz:
                            nx, nz = cx + dx, cz + dz
                            if 0 <= nx < w and 0 <= nz < h \
                                    and label[nz][nx] == -1 \
                                    and fam[nz][nx] == f0:
                                label[nz][nx] = len(regions)
                                dq.append((nx, nz))
            regions.append({"family": f0, "cells": cells})

    out = []
    for i, rg in enumerate(regions):
        cells = rg["cells"]
        if len(cells) < min_area:
            continue
        xs = [c[0] for c in cells]
        zs = [c[1] for c in cells]
        terr = Counter(gm.grid[z][x] for x, z in cells)
        water_kinds = Counter(tprop(gm.grid[z][x], "water", "none")
                              for x, z in cells)
        passable = sum(1 for x, z in cells
                       if tprop(gm.grid[z][x], "passable", True))
        edges = set()
        for x, z in cells:
            if x == 0:
                edges.add("W")
            if x == w - 1:
                edges.add("E")
            if z == 0:
                edges.add("S")
            if z == h - 1:
                edges.add("N")
        out.append({
            "id": len(out),
            "family": rg["family"],
            "area": len(cells),
            "bbox": [min(xs), min(zs), max(xs), max(zs)],
            "centroid": [round(sum(xs) / len(xs), 1),
                         round(sum(zs) / len(zs), 1)],
            "dominant_terrain": terr.most_common(1)[0][0],
            "terrain_mix": dict(terr.most_common(4)),
            "water": (water_kinds.most_common(1)[0][0]
                      if rg["family"] == "water" else "none"),
            "passable_frac": round(passable / len(cells), 2),
            "touches_edges": sorted(edges),
        })
    out.sort(key=lambda r: r["area"], reverse=True)
    for i, r in enumerate(out):
        r["id"] = i
    return out


def perceive(gm, cols=32, min_region=25):
    """Full LLM-readable briefing of a map (no judgment)."""
    grid, bw, bh = coarse_grid(gm, cols=cols)
    regions = segment_regions(gm, min_area=min_region)
    hist = gm.terrain_histogram()
    total = gm.w * gm.h
    return {
        "name": gm.name,
        "size": [gm.w, gm.h],
        "coarse_cols": cols,
        "block_size": [round(bw, 2), round(bh, 2)],
        "glyph_legend": FAMILY_GLYPH,
        "coarse_grid_top_first": grid,
        "histogram_pct": {k: round(100 * v / total, 1)
                          for k, v in hist.most_common()},
        "regions": regions,
        "feature_count": len(gm.features),
    }


def briefing_text(brief):
    """Render the briefing as compact text for an LLM prompt / for me to read."""
    L = []
    L.append("MAP '%s'  %dx%d   (coarse %d cols, block ~%sx%s cells)"
             % (brief["name"], brief["size"][0], brief["size"][1],
                brief["coarse_cols"], brief["block_size"][0],
                brief["block_size"][1]))
    L.append("glyphs: " + "  ".join("%s=%s" % (v, k)
             for k, v in brief["glyph_legend"].items() if k != "?"))
    L.append("")
    L.append("COARSE MAP (top row = north / high z; each char is one block):")
    # column ruler every 8
    cols = brief["coarse_cols"]
    ruler = "".join(str((c // 10) % 10) if c % 8 == 0 else " "
                    for c in range(cols))
    ruler2 = "".join(str(c % 10) if c % 8 == 0 else " " for c in range(cols))
    L.append("    " + ruler)
    L.append("    " + ruler2)
    for i, row in enumerate(brief["coarse_grid_top_first"]):
        L.append("%3d %s" % (i, row))
    L.append("")
    L.append("HISTOGRAM (%% of map): " + ", ".join(
        "%s %.1f" % (k, v) for k, v in list(brief["histogram_pct"].items())))
    L.append("")
    L.append("REGIONS (family, area, bbox[x0,z0,x1,z1], centroid, terrain):")
    for r in brief["regions"]:
        L.append("  #%d %-9s area=%-5d bbox=%s cen=%s terr=%s%s%s"
                 % (r["id"], r["family"], r["area"], r["bbox"], r["centroid"],
                    r["dominant_terrain"],
                    "  water=%s" % r["water"] if r["water"] != "none" else "",
                    "  edges=%s" % ",".join(r["touches_edges"])
                    if r["touches_edges"] else ""))
    return "\n".join(L)


# ==========================================================================
# METRICS  (objective guardrails — NOT the subjective judge)
# ==========================================================================
def _neighbors4(x, z):
    yield x + 1, z
    yield x - 1, z
    yield x, z + 1
    yield x, z - 1


def metric_transition_coherence(gm):
    """Fraction of adjacent-cell family boundaries that are 'plausible'
    transitions (not a hard jump between incompatible families). Higher=better.

    Plausible neighbor families encode 'these can sit next to each other in
    nature'. e.g. sand<->soil ok; sand<->mountain needs rock/rubble between."""
    ok_pairs = {
        frozenset(["sand", "soil"]), frozenset(["sand", "rock"]),
        frozenset(["soil", "rock"]), frozenset(["soil", "mud"]),
        frozenset(["mud", "water"]), frozenset(["sand", "mud"]),
        frozenset(["rock", "mountain"]), frozenset(["rock", "cave"]),
        frozenset(["cave", "mountain"]), frozenset(["rock", "water"]),
        frozenset(["sand", "water"]), frozenset(["volcanic", "rock"]),
        frozenset(["volcanic", "mountain"]), frozenset(["crafted", "sand"]),
        frozenset(["crafted", "soil"]), frozenset(["crafted", "rock"]),
        frozenset(["soil", "water"]), frozenset(["volcanic", "sand"]),
        frozenset(["crafted", "mud"]), frozenset(["crafted", "volcanic"]),
        frozenset(["crafted", "mountain"]), frozenset(["mud", "rock"]),
    }
    w, h = gm.w, gm.h
    fam = _field(gm, "family", "?")
    total = 0
    good = 0
    for z in range(h):
        for x in range(w):
            f = fam[z][x]
            for nx, nz in ((x + 1, z), (x, z + 1)):
                if 0 <= nx < w and 0 <= nz < h:
                    g = fam[nz][nx]
                    if f == g:
                        continue
                    total += 1
                    if frozenset([f, g]) in ok_pairs:
                        good += 1
    return round(good / total, 4) if total else 1.0


def metric_fragmentation(gm, min_area=6):
    """Count of tiny disconnected family patches (< min_area). Lower=better —
    high fragmentation reads as generator 'confetti'."""
    regions = segment_regions(gm, min_area=1)
    return sum(1 for r in regions if r["area"] < min_area)


def metric_family_diversity(gm):
    """Shannon evenness of terrain families (0..1). Very low = monotonous;
    this is informational, not inherently good or bad — the LLM interprets."""
    fam = Counter()
    for row in gm.grid:
        for n in row:
            fam[tprop(n, "family", "?")] += 1
    tot = sum(fam.values())
    if len(fam) <= 1:
        return 0.0
    ent = -sum((c / tot) * math.log(c / tot) for c in fam.values())
    return round(ent / math.log(len(fam)), 4)


def metrics(gm):
    return {
        "transition_coherence": metric_transition_coherence(gm),
        "fragmentation_tiny_patches": metric_fragmentation(gm),
        "family_diversity": metric_family_diversity(gm),
    }


# ==========================================================================
# EDIT PRIMITIVES
# Each takes the map + LLM-chosen args and returns cells changed. They do the
# HOW; the LLM decides the WHAT/WHERE and passes coordinates.
# ==========================================================================
def _rng(seed):
    return random.Random(seed)


def _val_noise(w, h, freq, seed):
    rnd = random.Random(seed)
    gw, gh = max(2, int(w * freq)) + 2, max(2, int(h * freq)) + 2
    g = [[rnd.random() for _ in range(gw)] for _ in range(gh)]
    sm = lambda t: t * t * (3 - 2 * t)
    out = [[0.0] * w for _ in range(h)]
    for z in range(h):
        fy = z * (gh - 2) / max(1, h)
        y0 = int(fy)
        ty = sm(fy - y0)
        for x in range(w):
            fx = x * (gw - 2) / max(1, w)
            x0 = int(fx)
            tx = sm(fx - x0)
            a = g[y0][x0] + (g[y0][x0 + 1] - g[y0][x0]) * tx
            b = g[y0 + 1][x0] + (g[y0 + 1][x0 + 1] - g[y0 + 1][x0]) * tx
            out[z][x] = a + (b - a) * ty
    return out


def op_terrain_gradient(gm, region_bbox, order, seed=0, noise=0.12, axis=None,
                        reverse=False):
    """Repaint a rectangular region as a smooth gradient through an ordered list
    of terrains (e.g. ['WaterOceanShallow','Sand','Soil','SoilRich']) along an
    axis, with a little noise so the bands aren't ruler-straight. Use to build
    believable ecological transitions. Returns cells changed.

    axis: 'h' (west→east), 'v' (south→north), or None to auto-pick by aspect.
    reverse: flip the ordering direction along the chosen axis."""
    x0, z0, x1, z1 = region_bbox
    x0, x1 = sorted((max(0, x0), min(gm.w - 1, x1)))
    z0, z1 = sorted((max(0, z0), min(gm.h - 1, z1)))
    n = len(order)
    if n == 0:
        return 0
    if axis == "h":
        horiz = True
    elif axis == "v":
        horiz = False
    else:
        horiz = (x1 - x0) >= (z1 - z0)
    nz = _val_noise(gm.w, gm.h, 0.06, seed + 41)
    changed = 0
    for z in range(z0, z1 + 1):
        for x in range(x0, x1 + 1):
            t = ((x - x0) / max(1, x1 - x0)) if horiz \
                else ((z - z0) / max(1, z1 - z0))
            if reverse:
                t = 1.0 - t
            t = min(0.999, max(0.0, t + (nz[z][x] - 0.5) * noise * 2))
            gm.set(x, z, order[int(t * n)])
            changed += 1
    return changed


def op_fractalize_edge(gm, from_family, to_terrain, coast_terrain,
                       amount=0.6, seed=0, reach=3):
    """Roughen the boundary of `from_family` against everything else so a smooth
    stamped coastline/cliff becomes an irregular natural one — WITHOUT turning it
    into salt-and-pepper noise.

    Coherence: instead of an independent coin-flip per border cell (which just
    makes speckle), we drive the displacement with a smooth 1-D noise indexed by
    position ALONG the coast. Where the noise is high we advance the shore into
    the land by up to `reach` cells; where low we cut it back into the water by
    up to `reach`. `amount` scales how far. This yields headlands and inlets, not
    static. Returns cells changed."""
    w, h = gm.w, gm.h
    fam = _field(gm, "family", "?")

    # decide the coast's principal axis: vertical coast (varies in z) vs
    # horizontal (varies in x), by the spread of border cells.
    border = []
    for z in range(h):
        for x in range(w):
            if fam[z][x] == from_family:
                for nx, nz in _neighbors4(x, z):
                    if 0 <= nx < w and 0 <= nz < h and fam[nz][nx] != from_family:
                        border.append((x, z))
                        break
    if not border:
        return 0
    xs = [b[0] for b in border]
    zs = [b[1] for b in border]
    vertical = (max(zs) - min(zs)) >= (max(xs) - min(xs))

    # smooth 1-D displacement profile along the coast axis
    axis_len = h if vertical else w
    nprofile = _val_noise(axis_len, 1, 0.10, seed + 71)[0]
    disp = [int(round((nprofile[i] - 0.5) * 2 * reach * amount))
            for i in range(axis_len)]

    changed = 0
    # For each row (vertical coast) / col (horizontal), find the current
    # land/water frontier and move it by disp.
    if vertical:
        for z in range(h):
            # frontier = leftmost land x that touches water on this row, or the
            # rightmost water x. Use the mean border x on this row.
            rowb = [x for (x, bz) in border if bz == z]
            if not rowb:
                continue
            fx = sum(rowb) // len(rowb)
            d = disp[z]
            if d > 0:                     # advance land: convert d water cells
                for k in range(1, d + 1):
                    cx = fx - k           # water side is smaller x (ocean W)
                    if gm.in_bounds(cx, z) and \
                            tprop(gm.grid[z][cx], "family") == from_family:
                        gm.set(cx, z, to_terrain)
                        changed += 1
            elif d < 0:                   # cut back: convert -d land cells
                for k in range(0, -d):
                    cx = fx + k
                    if gm.in_bounds(cx, z) and \
                            tprop(gm.grid[z][cx], "family") != from_family:
                        gm.set(cx, z, coast_terrain)
                        changed += 1
    else:
        for x in range(w):
            colb = [z for (bx, z) in border if bx == x]
            if not colb:
                continue
            fz = sum(colb) // len(colb)
            d = disp[x]
            if d > 0:
                for k in range(1, d + 1):
                    cz = fz - k
                    if gm.in_bounds(x, cz) and \
                            tprop(gm.grid[cz][x], "family") == from_family:
                        gm.set(x, cz, to_terrain)
                        changed += 1
            elif d < 0:
                for k in range(0, -d):
                    cz = fz + k
                    if gm.in_bounds(x, cz) and \
                            tprop(gm.grid[cz][x], "family") != from_family:
                        gm.set(x, cz, coast_terrain)
                        changed += 1
    return changed


def op_scatter(gm, region_bbox, terrain, density=0.15, clump=0.5,
               only_families=None, seed=0, patch=True):
    """Sprinkle `terrain` into a region as small COHERENT patches (default) or
    as independent specks (patch=False). Coherent patches read as vegetation
    stands / rubble fields rather than confetti.

    density ~ fraction of region covered. clump biases patches toward the
    high-noise areas. only_families restricts what may be overwritten."""
    x0, z0, x1, z1 = region_bbox
    x0, x1 = max(0, x0), min(gm.w - 1, x1)
    z0, z1 = max(0, z0), min(gm.h - 1, z1)
    rnd = _rng(seed + 13)
    nz = _val_noise(gm.w, gm.h, 0.14, seed + 99)
    changed = 0

    def eligible(x, z):
        if not gm.in_bounds(x, z):
            return False
        if only_families and tprop(gm.grid[z][x], "family") not in only_families:
            return False
        return True

    if not patch:
        for z in range(z0, z1 + 1):
            for x in range(x0, x1 + 1):
                if eligible(x, z) and rnd.random() < density * (
                        1 + clump * (nz[z][x] - 0.5) * 2):
                    gm.set(x, z, terrain)
                    changed += 1
        return changed

    # coherent patches: pick seed points, grow each into a little blob
    area = (x1 - x0 + 1) * (z1 - z0 + 1)
    n_seeds = max(1, int(area * density / 9))   # ~3x3 avg patch
    for _ in range(n_seeds):
        sx = rnd.randint(x0, x1)
        sz = rnd.randint(z0, z1)
        # bias by noise: skip low-noise seeds when clumped
        if clump > 0 and nz[sz][sx] < 0.5 - 0.3 * clump and rnd.random() < 0.6:
            continue
        r = rnd.choice([1, 1, 2])
        for dz in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dz * dz <= r * r and rnd.random() < 0.8:
                    xx, zz = sx + dx, sz + dz
                    if eligible(xx, zz) and gm.grid[zz][xx] != terrain:
                        gm.set(xx, zz, terrain)
                        changed += 1
    return changed


def op_path(gm, waypoints, terrain="Gravel", width=1):
    """Lay a path/road of `terrain` through a list of (x,z) waypoints, straight
    segments between them, given half-width. Use for old roads, haul routes,
    game trails. Returns cells changed."""
    changed = 0
    def stamp(cx, cz):
        nonlocal changed
        for dz in range(-width, width + 1):
            for dx in range(-width, width + 1):
                if dx * dx + dz * dz <= width * width:
                    xx, zz = cx + dx, cz + dz
                    if gm.in_bounds(xx, zz) and gm.grid[zz][xx] != terrain:
                        gm.set(xx, zz, terrain)
                        changed += 1
    for (x0, z0), (x1, z1) in zip(waypoints, waypoints[1:]):
        dist = max(abs(x1 - x0), abs(z1 - z0)) or 1
        for i in range(dist + 1):
            stamp(round(x0 + (x1 - x0) * i / dist),
                  round(z0 + (z1 - z0) * i / dist))
    return changed


def op_blob(gm, cx, cz, radius, terrain, only_families=None, jitter=0.25,
            seed=0):
    """Organic blob of `terrain` centered at (cx,cz). Use for hills, ponds,
    clearings, sludge, patches. only_families restricts overwrite targets."""
    rnd = _rng(seed + 5)
    r2 = radius * radius
    changed = 0
    for z in range(max(0, cz - radius), min(gm.h, cz + radius + 1)):
        for x in range(max(0, cx - radius), min(gm.w, cx + radius + 1)):
            d2 = (x - cx) ** 2 + (z - cz) ** 2
            if d2 <= r2 * (1 + rnd.uniform(-jitter, jitter)):
                if only_families and tprop(gm.grid[z][x], "family") \
                        not in only_families:
                    continue
                gm.set(x, z, terrain)
                changed += 1
    return changed


def op_ring(gm, cx, cz, r_in, r_out, terrain, only_families=None):
    changed = 0
    for z in range(max(0, cz - r_out), min(gm.h, cz + r_out + 1)):
        for x in range(max(0, cx - r_out), min(gm.w, cx + r_out + 1)):
            d2 = (x - cx) ** 2 + (z - cz) ** 2
            if r_in * r_in <= d2 <= r_out * r_out:
                if only_families and tprop(gm.grid[z][x], "family") \
                        not in only_families:
                    continue
                gm.set(x, z, terrain)
                changed += 1
    return changed


def op_rect(gm, x0, z0, x1, z1, terrain):
    changed = 0
    for z in range(max(0, z0), min(gm.h, z1 + 1)):
        for x in range(max(0, x0), min(gm.w, x1 + 1)):
            if gm.grid[z][x] != terrain:
                gm.set(x, z, terrain)
                changed += 1
    return changed


def op_hill(gm, cx, cz, radius, ring_terrain="RockRubble",
            core_terrain="AB_ForsakenRock", seed=0):
    """A small hill/outcrop: rubble apron + rock core. Use to break up flats or
    extend a mountain foot. Returns cells changed."""
    c = op_blob(gm, cx, cz, radius, ring_terrain, jitter=0.35, seed=seed)
    c += op_blob(gm, cx, cz, max(1, radius // 2), core_terrain, jitter=0.3,
                 seed=seed + 1)
    return c


def op_carve_chamber(gm, cx, cz, radius, floor="CaveFloor",
                     require_family=("mountain",), seed=0):
    """Hollow a chamber of `floor` but ONLY through cells whose family is in
    require_family (default solid rock). Refuses to carve open ground, so caves
    stay inside stone. Returns cells changed (0 if nothing eligible)."""
    rnd = _rng(seed + 17)
    w, h = gm.w, gm.h
    # flood a rough disc but gated on family
    changed = 0
    frontier = deque([(cx, cz)])
    seen = {(cx, cz)}
    while frontier:
        x, z = frontier.popleft()
        if (x - cx) ** 2 + (z - cz) ** 2 > radius * radius * (1 + 0.2):
            continue
        if not gm.in_bounds(x, z):
            continue
        if tprop(gm.grid[z][x], "family") not in require_family:
            continue
        gm.set(x, z, floor)
        changed += 1
        for nx, nz in _neighbors4(x, z):
            if (nx, nz) not in seen:
                seen.add((nx, nz))
                if rnd.random() < 0.9:
                    frontier.append((nx, nz))
    return changed


def op_depth_grade(gm, bands, from_family="water", seed=0, noise=1):
    """Repaint every cell of `from_family` by its distance to the nearest cell of
    a DIFFERENT family (the shore), so an undifferentiated water body becomes a
    believable depth ramp: far-from-shore -> bands[0] (deepest), nearest-shore ->
    bands[-1] (shallowest). Works on any coast shape (it measures real distance,
    not a rectangle), so it respects meanders/coves. `noise` jitters the band
    thresholds by +/- that many cells so the depth contours aren't clean rings.
    Returns cells changed."""
    w, h = gm.w, gm.h
    fam = _field(gm, "family", "?")
    INF = 10 ** 9
    dist = [[INF] * w for _ in range(h)]
    dq = deque()
    for z in range(h):
        for x in range(w):
            if fam[z][x] != from_family:          # shore / land seed
                dist[z][x] = 0
                dq.append((x, z))
    # multi-source BFS (4-conn) distance-to-shore, only through water
    while dq:
        x, z = dq.popleft()
        for nx, nz in _neighbors4(x, z):
            if 0 <= nx < w and 0 <= nz < h and fam[nz][nx] == from_family \
                    and dist[nz][nx] == INF:
                dist[nz][nx] = dist[z][x] + 1
                dq.append((nx, nz))
    maxd = max((dist[z][x] for z in range(h) for x in range(w)
                if fam[z][x] == from_family and dist[z][x] < INF), default=0)
    if maxd == 0:
        return 0
    rnd = _rng(seed + 23)
    nb = len(bands)
    # band i covers deepest..shallowest as distance decreases
    changed = 0
    for z in range(h):
        for x in range(w):
            if fam[z][x] != from_family or dist[z][x] == INF:
                continue
            d = dist[z][x] + (rnd.randint(-noise, noise) if noise else 0)
            frac = 1.0 - min(1.0, max(0.0, d / maxd))   # 0 near shore..1 deep
            bi = min(nb - 1, int(frac * nb))
            # bands listed shallow->deep for readability; index from deep end
            name = bands[nb - 1 - bi]
            if gm.grid[z][x] != name:
                gm.set(x, z, name)
                changed += 1
    return changed


def op_shore_ribbon(gm, ribbon_terrain, water_family="water", width=1,
                    only_families=None):
    """Lay a `width`-cell ribbon of `ribbon_terrain` on the LAND side of the
    water boundary (a beach / wet-sand strip). Only overwrites `only_families`
    if given. Returns cells changed."""
    w, h = gm.w, gm.h
    fam = _field(gm, "family", "?")
    # cells within `width` (chebyshev) of water, that are themselves not water
    changed = 0
    targets = set()
    for z in range(h):
        for x in range(w):
            if fam[z][x] == water_family:
                continue
            near = False
            for dz in range(-width, width + 1):
                for dx in range(-width, width + 1):
                    nx, nz = x + dx, z + dz
                    if 0 <= nx < w and 0 <= nz < h and fam[nz][nx] == water_family:
                        near = True
                        break
                if near:
                    break
            if near:
                targets.add((x, z))
    for x, z in targets:
        if only_families and tprop(gm.grid[z][x], "family") not in only_families:
            continue
        if gm.grid[z][x] != ribbon_terrain:
            gm.set(x, z, ribbon_terrain)
            changed += 1
    return changed


def op_paint_cells(gm, cells, terrain):
    """Freehand escape hatch: set an explicit list of [x,z] cells to `terrain`.
    For anything the templated ops can't express. Returns cells changed."""
    changed = 0
    for x, z in cells:
        if gm.in_bounds(x, z) and gm.grid[z][x] != terrain:
            gm.set(x, z, terrain)
            changed += 1
    return changed


def op_smooth(gm, only_families=None, passes=1):
    """Majority-family smoothing to kill single-cell confetti. Optional filter
    so you only smooth certain families. Returns cells changed."""
    w, h = gm.w, gm.h
    changed = 0
    for _ in range(passes):
        snap = [row[:] for row in gm.grid]
        for z in range(1, h - 1):
            for x in range(1, w - 1):
                here = snap[z][x]
                fh = tprop(here, "family")
                if only_families and fh not in only_families:
                    continue
                nb = Counter()
                rep = {}
                for dx in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        if dx or dz:
                            t = snap[z + dz][x + dx]
                            f = tprop(t, "family")
                            nb[f] += 1
                            rep.setdefault(f, t)
                top, cnt = nb.most_common(1)[0]
                if cnt >= 6 and top != fh and top != "water":
                    gm.set(x, z, rep[top])
                    changed += 1
    return changed


# registry so a harness (or I) can dispatch by name with kwargs
PRIMITIVES = {
    "terrain_gradient": op_terrain_gradient,
    "fractalize_edge": op_fractalize_edge,
    "scatter": op_scatter,
    "path": op_path,
    "blob": op_blob,
    "ring": op_ring,
    "rect": op_rect,
    "hill": op_hill,
    "carve_chamber": op_carve_chamber,
    "depth_grade": op_depth_grade,
    "shore_ribbon": op_shore_ribbon,
    "paint_cells": op_paint_cells,
    "smooth": op_smooth,
}


def apply_edit(gm, op_name, **kwargs):
    """Dispatch a named primitive with LLM-chosen kwargs. Returns cells changed.
    Unknown ops raise, so a bad plan fails loudly instead of silently."""
    if op_name not in PRIMITIVES:
        raise KeyError("unknown primitive %r; have %s"
                       % (op_name, list(PRIMITIVES)))
    return PRIMITIVES[op_name](gm, **kwargs)


# ==========================================================================
# CLI: perceive a map so I (or a harness) can read it
# ==========================================================================
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="perceive a map (LLM briefing)")
    ap.add_argument("map")
    ap.add_argument("--cols", type=int, default=32)
    ap.add_argument("--json", action="store_true", help="dump full JSON too")
    args = ap.parse_args()
    gm = GameMap.load_json(args.map)
    brief = perceive(gm, cols=args.cols)
    print(briefing_text(brief))
    print("\nMETRICS:", json.dumps(metrics(gm)))
    if args.json:
        p = os.path.splitext(args.map)[0] + ".briefing.json"
        with open(p, "w") as fh:
            json.dump(brief, fh, indent=2)
        print("\nwrote", p)
