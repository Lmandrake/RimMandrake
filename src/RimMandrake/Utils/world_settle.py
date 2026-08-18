#!/usr/bin/env python3
"""Step 8 (and the siting it needs): where people live, and the roads between them.

⚠️ Step 7 - anisotropic biome mass growth - is NOT done. It was skipped in favour of
this, because roads dead-ending in sand was the defect the owner could see. The biome
masses still grow isotropically in world_biomes.py.

🔴 WHY ROADS COME LAST. In the shipped world the roads were fragmented, dead-ending
in open sand, because they were INHERITED from vanilla worldgen and then had their
drowned segments deleted. A road is not scenery: it is the cheapest path between two
places people actually live. So it cannot be laid until the places exist, and the
places cannot be chosen until the land, the water and the climate exist.

    habitability   what makes a tile worth living on: water within reach, ground you
                   can build on, a biome that will not kill you, a climate you can
                   stand. Read off the fields the earlier steps produced.
    siting         greedy pick of the best tiles with a minimum spacing, so
                   settlements do not clump into one oasis
    roads          Dijkstra over the tile graph with a real cost - slope, biome and
                   river crossings - then a spanning tree over the settlements, plus
                   the shortcuts that make a network rather than a spider

Reads  world/relief.npz, world/hydro.npz, world/biomes.npz
Writes world/settle.npz   site tiles, road tiles, road class
       world/settle.png   the network over the planet

    python3 src/RimMandrake/Utils/world_settle.py
"""
import heapq
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world_graph
import world_relief as wr
import world_biomes as wb

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT_NPZ = os.path.join(REPO, "world", "settle.npz")
OUT_PNG = os.path.join(REPO, "world", "settle.png")

MIN_SPACING = 4             # tiles between settlements

# 🔑 SITING IS NOT PURE HABITABILITY. On the first run all 40 settlements landed on
# the terminator ring, because that is where the water is - and the faction plan does
# not ask for that. The Geonosians live at an ore seam, the Junkers in the Sunreach,
# the Free Droids on the volcanics. People live in hostile places FOR REASONS, and the
# reasons are in populate_ashkarr.py's PLAN.
#
# ⚠️ These counts mirror PLAN. If PLAN changes, change them: nothing enforces it.
ZONE_DEMAND = [
    ("capital", 1), ("ore_seams", 1), ("plateau", 2), ("fall_line", 2),
    ("imperial", 2), ("volcanic", 3), ("sunreach", 3), ("terminator", 3),
    ("dew_belt", 5), ("twilight_shore", 9), ("ring", 9),
]


def zones(arc, bear, elev, slope, name, water, nb):
    """Each zone is a mask over the NEW fields. No zone is a lat/long box alone -
    where it can be said in terms of what the land does, it is."""
    def angdiff(a, b):
        return np.abs((a - b + 180.0) % 360.0 - 180.0)

    land = ~water
    coast = np.zeros(len(arc), dtype=bool)
    for i in np.flatnonzero(water):
        for j in nb[i]:
            coast[j] = True
    coast &= land
    near_volcano = np.zeros(len(arc), dtype=bool)
    vol = np.array([nm in ("Volcano", "LavaField", "AB_PyroclasticConflagration")
                    for nm in name])
    for i in np.flatnonzero(vol):
        near_volcano[i] = True
        for j in nb[i]:
            near_volcano[j] = True
    near_volcano &= land

    return {
        "capital":        land & (arc > 45) & (arc < 95),
        "ore_seams":      land & (slope > 220) & (elev > 1400),
        "plateau":        land & (arc < 24),
        "fall_line":      land & (arc > 24) & (arc < 64) & (angdiff(bear, 0.0) < 26),
        "imperial":       land & (arc > 52) & (arc < 88),
        "volcanic":       near_volcano,
        "sunreach":       land & (arc > 96) & (arc < 124),
        "terminator":     land & (arc > 84) & (arc < 106),
        "dew_belt":       land & (arc > 42) & (arc < 92) & (angdiff(bear, 178.0) < 24),
        "twilight_shore": coast & (arc > 70),
        "ring":           land & (arc > 36) & (arc < 82),
    }

# a biome people will not build a town in, and how much it costs to cross
HOSTILE = {"LavaField": 9.0, "Volcano": 7.0, "AB_PyroclasticConflagration": 9.0,
           "HorrorWastes": 6.0, "AB_GelatinousSuperorganism": 6.0,
           "AB_PropaneLakes": 5.0, "AB_TarPits": 4.0, "Scarlands": 3.0,
           "AB_MechanoidIntrusion": 5.0, "ExtremeDesert": 2.2,
           "AB_RockyCrags": 2.0, "SeaIce": 6.0}


def habitability(T, H, riv, hill, name, water, elev):
    """0..1. Deliberately made of few terms, each one arguable out loud."""
    n = len(T)
    # climate comfort: this is a desert world, so the curve is wide and warm-shifted
    comfort = np.exp(-((T - 20.0) / 34.0) ** 2)
    # water within reach beats water underfoot: a river tile floods
    near = np.where(riv == 0, 0.75, np.where(riv <= 2, 1.0, 0.0))
    wet = np.maximum(0.55 * H, near)
    build = np.clip(1.0 - (hill - 1) * 0.28, 0.10, 1.0)
    hostile = np.array([1.0 / (1.0 + HOSTILE.get(nm, 0.0)) for nm in name])
    h = comfort * (0.35 + 0.65 * wet) * build * hostile
    h[water] = 0.0
    return h


def site(hab, nb, zmask, spacing=MIN_SPACING):
    """Best habitable tile inside each zone the plan asks for, with a spacing veto.

    Zones are filled in demand order and the small, story-critical ones go FIRST -
    the same lesson populate_ashkarr.py already learned when the Geonosians and the
    Ascendant Helix ended up with zero settlements because they were last in line.
    """
    taken, blocked = [], np.zeros(len(hab), dtype=bool)
    out = {}
    for zone, count in ZONE_DEMAND:
        m = zmask[zone]
        got = _fill(hab, nb, m, count, blocked, spacing)
        out[zone] = got
        taken.extend(got)
        if len(got) < count:
            print("  ⚠️ zone %-15s asked %d, got %d - nowhere left that it fits"
                  % (zone, count, len(got)))
    return taken, out


def _fill(hab, nb, mask, count, blocked, spacing):
    order = np.argsort(-np.where(mask, hab, -1.0))
    taken = []
    for i in order:
        if len(taken) >= count or not mask[i] or hab[i] <= 0 or blocked[i]:
            continue
        taken.append(int(i))
        front = {int(i)}
        for _ in range(spacing):
            nxt = set()
            for t in front:
                blocked[t] = True
                nxt.update(int(u) for u in nb[t])
            front = nxt
        for t in front:
            blocked[t] = True
    return taken


def travel_cost(elev, hill, name, water, grade, nb):
    """Per-tile cost of moving through. Water is impassable; a river costs a bridge."""
    n = len(elev)
    c = np.ones(n)
    c += (hill - 1) * 0.55
    c += np.array([HOSTILE.get(nm, 0.0) * 0.45 for nm in name])
    c += np.where(grade > 0, 3.5 + 1.5 * grade, 0.0)      # fording, then bridging
    c[water] = np.inf
    return c


def dijkstra(src, cost, nb):
    n = len(cost)
    dist = np.full(n, np.inf)
    prev = np.full(n, -1, dtype=np.int64)
    dist[src] = 0.0
    h = [(0.0, src)]
    while h:
        d, i = heapq.heappop(h)
        if d > dist[i]:
            continue
        for j in nb[i]:
            if not np.isfinite(cost[j]):
                continue
            nd = d + 0.5 * (cost[i] if np.isfinite(cost[i]) else 0.0) + 0.5 * cost[j]
            if nd < dist[j]:
                dist[j] = nd
                prev[j] = i
                heapq.heappush(h, (nd, int(j)))
    return dist, prev


def path(prev, a, b):
    out, t = [], b
    while t != -1 and t != a:
        out.append(int(t))
        t = int(prev[t])
    out.append(int(a))
    return out[::-1]


def network(sites, cost, nb, shortcut_gain=2.4, shortcut_reach=1.9):
    """Spanning tree over the settlements, then the shortcuts.

    A pure MST gives a spider: everything routes through one hub and there is no way
    round anything. Adding any pair whose direct path is much cheaper than its
    in-tree path turns it into a road network people would actually have built.
    """
    tabs = {s: dijkstra(s, cost, nb) for s in sites}
    m = len(sites)
    D = np.array([[tabs[a][0][b] for b in sites] for a in sites])

    inb, used = {sites[0]}, []
    while len(inb) < m:
        best = None
        for a in inb:
            ia = sites.index(a)
            for ib, b in enumerate(sites):
                if b in inb or not np.isfinite(D[ia][ib]):
                    continue
                if best is None or D[ia][ib] < best[0]:
                    best = (D[ia][ib], a, b)
        if best is None:
            break
        _, a, b = best
        inb.add(b)
        used.append((a, b))

    # in-tree distances, for deciding what deserves a shortcut
    adj = {s: [] for s in sites}
    for a, b in used:
        adj[a].append(b)
        adj[b].append(a)

    def tree_dist(a, b):
        seen, stack = {a: 0.0}, [a]
        while stack:
            t = stack.pop()
            for u in adj[t]:
                if u not in seen:
                    seen[u] = seen[t] + D[sites.index(t)][sites.index(u)]
                    stack.append(u)
        return seen.get(b, np.inf)

    extra = []
    for ia, a in enumerate(sites):
        for ib in range(ia + 1, m):
            b = sites[ib]
            if (a, b) in used or (b, a) in used or not np.isfinite(D[ia][ib]):
                continue
            # and only between places that are actually near each other: a shortcut
            # across the whole planet is a trade route nobody walks.
            if (D[ia][ib] < shortcut_reach * np.median(D[np.isfinite(D)])
                    and tree_dist(a, b) > shortcut_gain * D[ia][ib]):
                extra.append((a, b))
    for a, b in extra:
        adj[a].append(b)
        adj[b].append(a)

    tiles = {}
    for a, b in used + extra:
        for t in path(tabs[a][1], a, b):
            tiles[t] = max(tiles.get(t, 1), 1)
    # a road carrying more of the network is a bigger road
    for a, b in used:
        for t in path(tabs[a][1], a, b):
            tiles[t] = 2
    return tiles, used, extra


def audit(sites, tiles, cost, nb, water, grade):
    road = np.zeros(len(cost), dtype=bool)
    road[list(tiles)] = True
    on_water = int((road & water).sum())
    # every road tile must touch another road tile or a settlement: no orphans
    ss = set(sites)
    orphan = sum(1 for t in tiles
                 if t not in ss and not any(u in tiles for u in nb[t]))
    # connectivity over the road graph alone
    seen, stack = {sites[0]}, [sites[0]]
    while stack:
        t = stack.pop()
        for u in nb[t]:
            if u in tiles and u not in seen:
                seen.add(u)
                stack.append(int(u))
    unreached = [s for s in sites if s not in seen]
    print("roads: %d tiles, %d bridges over rivers" % (len(tiles),
          int((road & (grade > 0)).sum())))
    print("🔴 road tiles on water: %d" % on_water)
    print("🔴 orphan road fragments: %d" % orphan)
    print("🔴 settlements not reachable by road: %d %s"
          % (len(unreached), unreached[:6]))
    return on_water + orphan + len(unreached)


def render(name, sites, tiles, water, elev, V, nb, size=520, pad=14):
    W, H, discs = wr.disc_maps(V, size, pad)
    keys = sorted(wb.COLOUR)
    idx = np.array([keys.index(nm) if nm in wb.COLOUR else 0 for nm in name])
    lut = np.array([wb.COLOUR[k] for k in keys], dtype=np.int16)
    road = np.zeros(len(elev), dtype=np.int8)
    for t, k in tiles.items():
        road[t] = k
    seat = np.zeros(len(elev), dtype=bool)
    seat[list(sites)] = True
    img = wr.blank(W, H)
    for x0, y0, inside, near in discs:
        c = lut[idx[near]].astype(np.int16)
        r = road[near]
        c[r == 1] = (118, 96, 74)
        c[r == 2] = (86, 66, 48)
        c[seat[near]] = (250, 236, 120)
        tile = np.zeros((size, size, 3), dtype=np.uint8)
        tile[:, :] = (10, 10, 14)
        tile[inside] = np.clip(c, 0, 255).astype(np.uint8)
        img[y0:y0 + size, x0:x0 + size] = tile
    return img


def main():
    r = np.load(os.path.join(REPO, "world", "relief.npz"))
    hy = np.load(os.path.join(REPO, "world", "hydro.npz"))
    bi = np.load(os.path.join(REPO, "world", "biomes.npz"), allow_pickle=True)
    elev, water = r["elev"].astype(float), r["water"]
    T, grade = hy["temp"], hy["grade"]
    name, hill, Hu, riv = bi["name"], bi["hill"], bi["humidity"], bi["riparian"]
    nb, lat, lon, V = world_graph.load()
    V = np.asarray(V, dtype=np.float64)

    slope = np.array([np.abs(elev[x] - elev[i]).max() for i, x in enumerate(nb)])
    hab = habitability(T, Hu, riv, hill, name, water, elev)
    zmask = zones(r["arc"], r["bear"], elev, slope, name, water, nb)
    sites, by_zone = site(hab, nb, zmask)
    print("sited %d settlements; habitability at the sites %.2f .. %.2f (planet p99 %.2f)"
          % (len(sites), hab[sites].min(), hab[sites].max(),
             np.percentile(hab[~water], 99)))
    on_river = sum(1 for s in sites if riv[s] <= 2)
    print("  %d of %d are within reach of a river" % (on_river, len(sites)))

    cost = travel_cost(elev, hill, name, water, grade, nb)
    tiles, used, extra = network(sites, cost, nb)
    print("network: %d trunk links, %d shortcuts" % (len(used), len(extra)))
    bad = audit(sites, tiles, cost, nb, water, grade)

    np.savez_compressed(OUT_NPZ, sites=np.array(sites),
                        road_tiles=np.array(sorted(tiles)),
                        road_class=np.array([tiles[t] for t in sorted(tiles)]),
                        habitability=hab.astype(np.float32))
    print("wrote", OUT_NPZ)
    wr.write_png(OUT_PNG, render(name, sites, tiles, water, elev, V, nb))
    print("wrote", OUT_PNG)
    return bad


if __name__ == "__main__":
    main()
