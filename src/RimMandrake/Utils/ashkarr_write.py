#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ashkarr_write.py - RETIRED 2026-08-18. Do not use.

🔴 Owner: "Please don't write to the savegame file anymore, we are just not going to do
that anymore." The map is a data bundle now (world/ashkarr_*); this module is kept only
for the encodings it documents, and write() refuses.

Originally: splice the hand-authored planet into the savegame.

Companion to `ashkarr_paint.py`; it holds no design decisions, only the encodings.
It writes to a NEW file and never touches the source, so every iteration is
reversible by deleting one save.

Encodings all come from worldmap.py's calibration against the live engine:
elevation raw = m + 8192 · temperature raw = C*10 + 3000 · rainfall raw = mm ·
swampiness raw = frac*255 · hilliness raw = the enum byte.

⭐ drawCenter, calibrated 2026-08-18 against four features of the source world:
`drawCenter = (z, y, -x) * radius` for the unit vector (x, y, z) this repo uses.
Residual is the label anchor not being the exact tile centroid, which does not matter.
"""
import base64
import math
import os
import re
import struct
import sys
import zlib
from collections import Counter, deque

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from worldmap import WorldGrid, WorldObjects, load_hash_table, DEFAULT_DUMP
import apply_world


def enc(raw):
    co = zlib.compressobj(9, zlib.DEFLATED, -15)
    return base64.b64encode(co.compress(raw) + co.flush()).decode("ascii")


def splice(text, name, payload):
    tag = "<%sDeflate>" % name
    j = text.find('Class="SurfaceLayer"')
    a = text.find(tag, j)
    if a < 0:
        return text, False
    b = text.find("</%sDeflate>" % name, a)
    return text[:a + len(tag)] + payload + text[b:], True


# --------------------------------------------------------------------------
def hilliness_from(elev, nbl, sea):
    """RimWorld's enum: 1 Flat · 2 SmallHills · 3 LargeHills · 4 Mountainous ·
    5 Impassable. Derived from LOCAL RELIEF - the spread of a tile's neighbourhood -
    not from height, so a high flat plateau stays flat and a low broken scarp does
    not."""
    out = np.ones(len(elev), np.uint8)
    for t in range(len(elev)):
        if sea[t]:
            out[t] = 1
            continue
        vals = [elev[t]] + [elev[u] for u in nbl[t]]
        rel = max(vals) - min(vals)
        out[t] = (5 if rel > 1150 and elev[t] > 2400 else
                  4 if rel > 780 else 3 if rel > 430 else 2 if rel > 190 else 1)
    return out


def temperature_curve(th, elev):
    """Owner's ruling: +70 C at the substellar point, +14 C at the terminator,
    -80 C in deep night, minus an altitude lapse. Keyed on ANGLE from the substellar
    point, which is what the planet measurably does - not on latitude."""
    stops = [(0, 70.0), (30, 58.0), (60, 38.0), (90, 14.0),
             (120, -22.0), (150, -58.0), (180, -80.0)]
    xs = np.array([s[0] for s in stops], float)
    ys = np.array([s[1] for s in stops], float)
    return np.interp(th, xs, ys) - np.clip(elev, 0, None) / 1000.0 * 5.5


def rivers_from(w, dump=DEFAULT_DUMP):
    """Channel tiles -> undirected (tile, downstream) edges, sized by accumulated
    flow. Four RiverDefs, so the trunk reads as a trunk and the headwaters as creeks."""
    _, rev = load_hash_table("RiverDef", dump)
    acc, down, chan, sea = w["acc"], w["down"], w["chan"], w["sea"]
    edges = []
    for t in np.nonzero(chan)[0]:
        d = down[t]
        if d < 0:
            continue
        if not (chan[d] or sea[d]):
            continue
        a = acc[t]
        name = ("HugeRiver" if a > 3000 else "LargeRiver" if a > 1200
                else "River" if a > 300 else "Creek")
        edges.append((int(t), int(d), rev[name]))
    return edges


def roads_from(w, settlements, dump=DEFAULT_DUMP):
    """Roads as least-cost paths between neighbouring settlements, on the tile graph.

    The cost field is what stops them being rulers: mountains, sand seas and river
    crossings all cost, so a road bends around a massif exactly as a real one does.
    Only each settlement's three nearest partners are linked, so the network stays a
    regional web instead of a complete graph."""
    import heapq
    _, rev = load_hash_table("RoadDef", dump)
    n, nbl, geo = w["n"], w["nbl"], w["geo"]
    elev, sea, th = w["elev"], w["sea"], w["th"]
    cost = np.ones(n) * 1.0 + np.clip(elev, 0, None) / 900.0
    cost += 2.2 * (w["riparian"] <= 1)          # crossing the green costs
    cost += np.clip((th - 95.0) / 12.0, 0, 6)   # nobody builds into the dark
    cost[sea] = 1e6

    live = [s for s in settlements if not sea[s["tile"]]]
    pos = {s["tile"]: s for s in live}
    tiles = list(pos)
    edges, done = [], set()
    for a in tiles:
        d = sorted(tiles, key=lambda b: geo.arc_deg(a, b))[1:4]
        for b in d:
            if (min(a, b), max(a, b)) in done or geo.arc_deg(a, b) > 42:
                continue
            done.add((min(a, b), max(a, b)))
            dist = np.full(n, np.inf)
            prev = np.full(n, -1, np.int32)
            dist[a] = 0
            pq = [(0.0, a)]
            while pq:
                dd, t = heapq.heappop(pq)
                if dd > dist[t]:
                    continue
                if t == b:
                    break
                for u in nbl[t]:
                    nd = dd + cost[u]
                    if nd < dist[u]:
                        dist[u] = nd
                        prev[u] = t
                        heapq.heappush(pq, (nd, u))
            if not np.isfinite(dist[b]):
                continue
            path, t = [], b
            while t != a and t >= 0:
                path.append(t)
                t = prev[t]
            path.append(a)
            grade = "StoneRoad" if len(path) < 14 else "DirtRoad"
            for x, y in zip(path[:-1], path[1:]):
                edges.append((int(x), int(y), rev[grade]))
    return edges


# --------------------------------------------------------------------------
REGION_DEFS = {"sea": "Ocean", "massif": "MountainRange", "waste": "Desert"}


def rewrite_features(text, w, regions):
    """Replace the inherited vanilla region names with Ash'karr's own, and repoint
    every tile's feature index at them. The old painter left the planet labelled
    'Josephine's Pride Mountains'."""
    lo = text.find("<features>")
    hi = text.find("</features>", lo)
    if lo < 0:
        return text, np.full(w["n"], 0xFFFF, np.uint16)
    geo = w["geo"]
    body, idx = [], np.full(w["n"], 0xFFFF, np.uint16)
    for i, (name, kind, tiles) in enumerate(regions):
        tiles = np.asarray(tiles)
        if not len(tiles):
            continue
        c = geo.vec[tiles].mean(axis=0)
        c /= np.linalg.norm(c)
        size = max(1.4, min(9.0, 0.34 * math.sqrt(len(tiles))))
        body.append(
            "<li><def>%s</def><name>%s</name>"
            "<drawCenter>(%.6f, %.6f, %.6f)</drawCenter>"
            "<maxDrawSizeInTiles>%.4f</maxDrawSizeInTiles>"
            "<layer>PlanetLayer_0</layer></li>"
            % (REGION_DEFS.get(kind, "Desert"), name,
               c[2] * 100.0, c[1] * 100.0, -c[0] * 100.0, size))
        idx[tiles] = i
    return text[:lo] + "<features>" + "".join(body) + text[hi:], idx


def move_objects(text, w):
    """Nothing may stand in the new sea. Settlements walk to the nearest land tile;
    landmarks that drowned are deleted, because a landmark has no identity to keep."""
    sea, nbl = w["sea"], w["nbl"]
    o = WorldObjects.__new__(WorldObjects)
    o.text, o.save_path = text, None
    moved = 0
    for s in o.settlements():
        if not sea[s["tile"]]:
            continue
        seen, q = {s["tile"]}, deque([s["tile"]])
        while q:
            t = q.popleft()
            if not sea[t]:
                o.move_settlement(s["id"], t)
                moved += 1
                break
            for u in nbl[t]:
                if u not in seen:
                    seen.add(u)
                    q.append(u)
    drowned = [m["tile"] for m in o.landmarks() if sea[m["tile"]]]
    if drowned:
        lo, hi, ks, vs = o._landmark_spans()
        keys = re.findall(r"<li>(-?\d+),(\d+)</li>", o.text[ks[0]:ks[1]])
        vals = re.findall(r"<li>.*?</li>", o.text[vs[0]:vs[1]], re.S)
        if len(vals) != len(keys):
            return o.text, moved, 0        # shapes disagree - drown nothing, say so
        keep = [i for i, (t, _) in enumerate(keys) if int(t) not in set(drowned)]
        nk = "".join("<li>%s,%s</li>" % keys[i] for i in keep)
        nv = "".join(vals[i] for i in keep)
        o.text = (o.text[:vs[0]] + nv + o.text[vs[1]:])
        o.text = (o.text[:ks[0]] + nk + o.text[ks[1]:])
    return o.text, moved, len(drowned)


# --------------------------------------------------------------------------
def write(w, out_path, regions=(), dump=DEFAULT_DUMP):
    raise SystemExit("ashkarr_write is RETIRED - the owner ruled 2026-08-18 that\nnothing writes to a savegame any more. The map is world/ashkarr_*.")
    grid, n, nbl = w["grid"], w["n"], w["nbl"]
    text = grid.text
    _, bhash = load_hash_table("BiomeDef", dump)

    missing = sorted({b for b in w["biome"] if b not in bhash})
    if missing:
        raise SystemExit("no BiomeDef in the dump for: %s" % missing)

    elev = np.round(w["elev"]).astype(int) + 8192
    temp = np.round(temperature_curve(w["th"], w["elev"]) * 10).astype(int) + 3000
    rain = np.clip(18.0 + 1650.0 * np.clip(w["rain_src"] / 2.6, 0, 1) ** 2.2, 12, 4800)
    rain[w["sea"]] = 90
    hill = hilliness_from(w["elev"], nbl, w["sea"])
    swamp = np.zeros(n)
    swamp[w["riparian"] <= 1] = 0.45
    swamp[w["delta"]] = 0.80
    swamp[w["sea"]] = 0.0

    arrays = {
        "tileBiome": ("H", [bhash[b] for b in w["biome"]]),
        "tileElevation": ("H", np.clip(elev, 0, 65535).tolist()),
        "tileTemperature": ("H", np.clip(temp, 0, 65535).tolist()),
        "tileRainfall": ("H", np.round(rain).astype(int).tolist()),
        "tilePollution": ("H", [0] * n),
        "tileHilliness": ("B", hill.tolist()),
        "tileSwampiness": ("B", np.round(swamp * 255).astype(int).tolist()),
    }
    if regions:
        text, fidx = rewrite_features(text, w, regions)
        arrays["tileFeature"] = ("H", fidx.tolist())

    for name, (code, vals) in arrays.items():
        text, ok = splice(text, name, enc(struct.pack("<%d%s" % (len(vals), code), *vals)))
        if not ok:
            print("   ! no array %s in the save" % name)

    # rivers and roads
    ordering = {t: nbl[t] for t in range(n)}
    text, nriv, _ = apply_world.write_links(text, "River", rivers_from(w, dump), ordering)
    o = WorldObjects.__new__(WorldObjects)
    o.text = text
    setl = o.settlements()
    text, nrd, _ = apply_world.write_links(text, "Road", roads_from(w, setl, dump), ordering)
    rd = bfs_river_distance(w)
    text, _ = splice(text, "tileRiverDistances", enc(bytes(rd)))

    text, moved, drowned = move_objects(text, w)
    with open(out_path, "w", encoding="utf-8", errors="surrogateescape") as fh:
        fh.write(text)
    export_table(w, os.path.join(os.path.dirname(out_path), "ashkarr_tiles.csv"))
    print("wrote %s\n   %d river links, %d road links, settlements moved %d, "
          "landmarks drowned %d" % (out_path, nriv, nrd, moved, drowned))
    return out_path


def export_table(w, path):
    """🔑 WHERE THE MAP LIVES. The savegame is a build output and is gitignored; the
    PNG and SVG are pictures of it. This CSV is the map's contents in a form a human
    can read, grep and diff, one row per tile, and it is what gets committed."""
    import csv as _csv
    g = w["geo"]
    temp = temperature_curve(w["th"], w["elev"])
    with open(path, "w", newline="", encoding="utf-8") as fh:
        wr = _csv.writer(fh)
        wr.writerow(["tile", "lat", "lon", "arc", "bearing", "elev_m", "temp_c",
                     "biome", "water", "river_flow", "region"])
        reg = {}
        for name, kind, tiles in w.get("regions", []):
            for t in tiles:
                reg.setdefault(int(t), name)
        for t in range(w["n"]):
            wr.writerow([t, round(float(g.lat[t]), 4), round(float(g.lon[t]), 4),
                         round(float(w["arc"][t]), 2), round(float(w["bear"][t]), 2),
                         int(round(w["elev"][t])), round(float(temp[t]), 1),
                         w["biome"][t], int(bool(w["sea"][t])),
                         int(w["acc"][t]) if w["chan"][t] else 0,
                         reg.get(t, "")])
    return path


def bfs_river_distance(w):
    d = np.full(w["n"], 255, np.int32)
    q = deque()
    for t in np.nonzero(w["chan"])[0]:
        d[t] = 0
        q.append(t)
    while q:
        t = q.popleft()
        if d[t] >= 8:
            continue
        for u in w["nbl"][t]:
            if d[u] > d[t] + 1:
                d[u] = d[t] + 1
                q.append(u)
    return np.clip(d, 0, 255).astype(np.uint8).tolist()
