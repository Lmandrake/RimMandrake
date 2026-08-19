#!/usr/bin/env python3
"""Write the generated world into the savegame, and deploy it.

Consumes the four offline stages and nothing else:

    world/relief.npz   elevation, sea level
    world/hydro.npz    temperature, rainfall, rivers
    world/biomes.npz   biome, hilliness
    world/settle.npz   settlement sites, roads

✅ RIVERS AND ROADS ARE WRITTEN, as of 2026-08-18. They are not per-tile
arrays: each entry is (origin tile, ADJACENCY SLOT, def), and the slot indexes
RimWorld's own neighbour ordering for that tile. I tried to recover that ordering
offline by scoring every rotation and winding of my own neighbour list against the
rivers the ENGINE generated, on two independent signals - "does the implied target
lie on a river" and "is it downhill". Best score 0.197 against a 0.161 chance
baseline: no candidate ordering is distinguishable from random. Writing rivers on a
guessed ordering would produce a network of random one-tile hops.
So the fossil rivers and roads are STRIPPED rather than replaced, and authoring them
waits on one bridge call that reads GetTileNeighbors ordering out of the live game.
Nothing here is guessed. See skills/calibrating-binary-formats.

    python3 src/RimMandrake/Utils/apply_world.py [--dry] [--no-deploy]
"""
import base64
import os
import re
import shutil
import struct
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world_graph
from worldmap import WorldGrid, WorldObjects, DECODE

MUTATOR_DUMP = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
                "RimWorld by Ludeon Studios/DefDump/defs/TileMutatorDef.json")
# a mutator that only makes sense with water or a river next to it
SEA_WORDS = ("coast", "reef", "tide", "beach", "island", "sea", "shore", "atoll",
             "lagoon", "mangrove", "kelp")
RIVER_WORDS = ("river", "delta", "estuary", "oxbow", "waterfall", "confluence",
               "ford", "rapids")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "world", "WORLDMAP_sub7b_source.rws")
# 🔴 NEVER write over the world the owner is using. A bad write then costs a
# file they can delete instead of a cold load. Learned 2026-08-18.
DEST = os.path.join(REPO, "world", "WORLDMAP_ashkarr.rws")
GAME = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
        "RimWorld by Ludeon Studios/Saves/WORLDMAP_ashkarr.rws")

# pollution 0..1 -> raw. Calibrated in paint_ashkarr: the pristine world's own max is
# exactly 65535 and its 5% non-zero fraction matches its `pollution 0.05` setting.
POLL_FULL = 65535.0
POLLUTED = {"AB_MechanoidIntrusion": (0.55, 0.95), "Scarlands": (0.25, 0.60),
            "AB_TarPits": (0.20, 0.55), "HorrorWastes": (0.10, 0.40),
            "AB_PropaneLakes": (0.05, 0.20)}


def enc_deflate(raw):
    co = zlib.compressobj(9, zlib.DEFLATED, -15)
    return base64.b64encode(co.compress(raw) + co.flush()).decode("ascii")


def rainfall_mm(H, water):
    """Humidity rank -> mm/year. Cubed, so the planet stays a desert: the wet band is
    genuinely wet and everywhere else is hyper-arid, with nothing in between by
    accident."""
    mm = 18.0 + 1750.0 * np.clip(H, 0, 1) ** 3
    mm[water] = 90.0
    return mm


NEIGHBOURS = os.path.join(REPO, "world", "world_neighbors_sub7b.csv")
RIVER_DEF = {1: 8778, 2: 44073, 3: 21820}      # Creek / River / HugeRiver shortHash
ROAD_DEF = {1: 36088, 2: 42996}                # DirtPath / DirtRoad


def load_neighbours():
    """The engine's OWN neighbour ordering, from jawa/world_neighbors."""
    out = {}
    with open(NEIGHBOURS) as fh:
        for r in __import__("csv").DictReader(fh):
            out[int(r["tile"])] = [int(r["n%d" % k]) for k in range(6)
                                   if int(r["n%d" % k]) >= 0]
    return out


def pack_links(edges, ordering):
    """(tileA, tileB, defHash) -> the three parallel arrays.

    🔑 THE FORMAT, decoded 2026-08-18 and verified on a generated world: one entry per
    undirected EDGE, stored ONCE, owned by the LOWER-INDEX tile, adjacency = that
    tile's index of its partner in GetTileNeighbors order. Origin < target held in
    1.000 of 648 engine-written entries, and reciprocity was exactly 0.000.
    """
    rows, skipped = [], 0
    for a, b, dh in edges:
        lo, hi = (a, b) if a < b else (b, a)
        nb = ordering.get(lo)
        if not nb or hi not in nb:
            skipped += 1              # not actually adjacent in the ENGINE's grid
            continue
        rows.append((lo, nb.index(hi), dh))
    rows.sort(key=lambda r: (r[0], r[1]))          # origins ascending, as the engine writes
    seen, uniq = set(), []
    for lo, slot, dh in rows:
        if (lo, slot) in seen:
            continue                  # an edge written twice would draw twice
        seen.add((lo, slot))
        uniq.append((lo, slot, dh))
    org = struct.pack("<%dI" % len(uniq), *[r[0] for r in uniq])
    adj = bytes(r[1] for r in uniq)
    dfs = struct.pack("<%dH" % len(uniq), *[r[2] for r in uniq])
    return org, adj, dfs, len(uniq), skipped


def write_links(text, kind, edges, ordering):
    org, adj, dfs, n, skipped = pack_links(edges, ordering)
    j = text.find('Class="SurfaceLayer"')
    for raw, tag in ((org, "Origins"), (adj, "Adjacency"), (dfs, "Def")):
        name = "tile%s%sDeflate" % (kind, tag)
        m = re.search(r"<%s>([^<]*)</%s>" % (name, name), text[j:j + 900000])
        if not m:
            continue
        text = text.replace(m.group(0), "<%s>%s</%s>"
                            % (name, enc_deflate(raw), name), 1)
        j = text.find('Class="SurfaceLayer"')
    return text, n, skipped


def strip_links(text):
    """Remove the inherited rivers and roads. Each is three parallel arrays; emptying
    all three together leaves a consistent, empty set rather than a dangling one."""
    out, removed = text, {}
    j = out.find('Class="SurfaceLayer"')
    for kind in ("Road", "River"):
        for tag in ("Origins", "Adjacency", "Def"):
            name = "tile%s%sDeflate" % (kind, tag)
            m = re.search(r"<%s>([^<]*)</%s>" % (name, name), out[j:j + 900000])
            if not m:
                continue
            if tag == "Origins" and m.group(1).strip():
                raw = zlib.decompress(base64.b64decode(m.group(1)), -15)
                removed[kind] = len(raw) // 4
            out = out.replace(m.group(0),
                              "<%s>%s</%s>" % (name, enc_deflate(b""), name), 1)
            j = out.find('Class="SurfaceLayer"')
    return out, removed


def fix_mutators(text, water, hill, nb):
    """Recompute the water-linked tile mutators against the NEW coastline.

    The shipped world carried 5,423 `Coast` mutators placed for the ORIGINAL sea
    layout; the repaint moved the water and nothing moved them. Same for the reef
    and tide mutators, and for every river mutator on a planet that now has no
    rivers at all. Names are matched by word, so a mod adding its own coast mutator
    is caught without being listed here.
    """
    import json
    h2n = {}
    for d in json.load(open(MUTATOR_DUMP))["defs"]:
        if "shortHash" in d:
            h2n[int(d["shortHash"])] = d["defName"]

    j = text.find('Class="SurfaceLayer"')

    def grab(tag):
        m = re.search(r"<%s>([^<]*)</%s>" % (tag, tag), text[j:j + 900000])
        raw = (zlib.decompress(base64.b64decode(m.group(1)), -15)
               if m and m.group(1).strip() else b"")
        return m, raw

    mt, traw = grab("tileMutatorTilesDeflate")
    md, draw = grab("tileMutatorDefsDeflate")
    if not traw:
        return text, {}
    cnt = len(traw) // 4
    tiles = list(struct.unpack("<%dI" % cnt, traw[:cnt * 4]))
    hashes = list(struct.unpack("<%dH" % cnt, draw[:cnt * 2]))

    coastal = np.zeros(len(water), dtype=bool)
    for i in np.flatnonzero(water):
        for k in nb[i]:
            coastal[k] = True
    coastal &= ~water

    coast_hash = None
    keep_t, keep_h = [], []
    stat = {"coast_dropped": 0, "coast_kept": 0, "coast_added": 0,
            "marine_inland_dropped": 0, "river_dropped": 0, "mountain_dropped": 0}
    for t, h in zip(tiles, hashes):
        nm = h2n.get(h, "")
        low = nm.lower()
        if t >= len(water):
            continue
        if nm == "Coast":
            coast_hash = h
            if coastal[t]:
                stat["coast_kept"] += 1
            else:
                stat["coast_dropped"] += 1
                continue
        elif any(w in low for w in RIVER_WORDS):
            stat["river_dropped"] += 1
            continue
        elif any(w in low for w in SEA_WORDS):
            if not (coastal[t] or water[t]):
                stat["marine_inland_dropped"] += 1
                continue
        elif nm == "Mountain" and hill[t] < 4:
            stat["mountain_dropped"] += 1
            continue
        keep_t.append(t)
        keep_h.append(h)

    if coast_hash is not None:
        have = {t for t, h in zip(keep_t, keep_h) if h == coast_hash}
        for t in np.flatnonzero(coastal):
            if int(t) not in have:
                keep_t.append(int(t))
                keep_h.append(coast_hash)
                stat["coast_added"] += 1

    for m, raw, tag in ((mt, struct.pack("<%dI" % len(keep_t), *keep_t), "Tiles"),
                        (md, struct.pack("<%dH" % len(keep_h), *keep_h), "Defs")):
        name = "tileMutator%sDeflate" % tag
        text = text.replace(m.group(0), "<%s>%s</%s>"
                            % (name, enc_deflate(raw), name), 1)
    stat["entries"] = "%d -> %d" % (cnt, len(keep_t))
    return text, stat


def main():
    dry = "--dry" in sys.argv
    r = np.load(os.path.join(REPO, "world", "relief.npz"))
    hy = np.load(os.path.join(REPO, "world", "hydro.npz"))
    bi = np.load(os.path.join(REPO, "world", "biomes.npz"), allow_pickle=True)
    se = np.load(os.path.join(REPO, "world", "settle.npz"))
    elev, water = r["elev"].astype(float), r["water"]
    T = hy["temp"].astype(float)
    name, hill, H = bi["name"], bi["hill"], bi["humidity"].astype(float)
    sites = [int(x) for x in se["sites"]]

    if not dry:
        if os.path.exists(DEST):
            shutil.copy2(DEST, DEST + ".bak")
            print("backed up the previous generated world -> WORLDMAP_gen.rws.bak")
        shutil.copy2(SRC, DEST)

    g = WorldGrid(DEST if not dry else SRC)
    n = len(g.biome_names())
    assert n == len(elev), "tile count mismatch: save %d, fields %d" % (n, len(elev))

    enc_t = DECODE["tileTemperature"][1]
    enc_r = DECODE["tileRainfall"][1]
    enc_e = DECODE["tileElevation"][1]
    b_arr = g.arrays["tileBiome"]
    e_arr = g.arrays["tileElevation"]
    t_arr = g.arrays["tileTemperature"]
    rn_arr = g.arrays["tileRainfall"]
    h_arr = g.arrays["tileHilliness"]
    p_arr = g.arrays["tilePollution"]
    sw_arr = g.arrays["tileSwampiness"]
    hb = g.hash_by_biome

    # 🔴 swampiness was INHERITED and never rewritten: the live game was reporting
    # "Desert ... swampiness=28%". Encoding verified 2026-08-18 as raw/255.
    riv = bi["riparian"]
    swamp = np.where(water, 0.0,
                     np.where(riv == 0, 0.45, np.where(riv <= 2, 0.20, 0.0)))
    swamp = np.minimum(swamp + 0.30 * np.clip(H - 0.85, 0, 1) / 0.15, 0.85)
    swamp[water] = 0.0

    elev = np.clip(elev, -350.0, 5000.0)
    mm = rainfall_mm(H, water)
    rng = np.random.default_rng(20260818)
    for t in range(n):
        nm = str(name[t])
        b_arr[t] = hb[nm]
        e_arr[t] = enc_e(float(elev[t]))
        t_arr[t] = enc_t(float(np.clip(T[t], -95.0, 92.0)))
        rn_arr[t] = enc_r(float(mm[t]))
        h_arr[t] = int(hill[t])
        sw_arr[t] = int(round(float(swamp[t]) * 255.0))
        lo_hi = POLLUTED.get(nm)
        p_arr[t] = int(round(rng.uniform(*lo_hi) * POLL_FULL)) if lo_hi else 0

    print("wrote %d tiles: %d biomes, elevation %.0f..%.0f m, temp %.0f..%.0f C, "
          "rain %.0f..%.0f mm" % (n, len(set(map(str, name))), elev.min(), elev.max(),
                                  T.min(), T.max(), mm.min(), mm.max()))
    print("swampiness: %d tiles wet (was inherited on 7,825 incl. deserts)"
          % int((swamp > 0).sum()))

    if dry:
        print("--dry: nothing written")
        return
    g.write(DEST)

    text = open(DEST, encoding="utf-8").read()
    text, removed = strip_links(text)
    print("stripped inherited links: %s" % (removed or "none found"))

    ordering = load_neighbours()
    hy2 = np.load(os.path.join(REPO, "world", "hydro.npz"))
    grade, recv = hy2["grade"], hy2["recv"]
    redges = []
    for i in range(n):
        if grade[i] > 0 and recv[i] >= 0:
            redges.append((int(i), int(recv[i]), RIVER_DEF[int(grade[i])]))
    text, nriv, sk1 = write_links(text, "River", redges, ordering)

    rd = se["road_edges"]
    dedges = [(int(a), int(b), ROAD_DEF[int(k)]) for a, b, k in rd]
    text, nrd, sk2 = write_links(text, "Road", dedges, ordering)
    print("WROTE %d river links (%d skipped as non-adjacent), %d road links (%d skipped)"
          % (nriv, sk1, nrd, sk2))
    nb, _, _, _ = world_graph.load()
    text, mstat = fix_mutators(text, water, hill, nb)
    print("mutators:", mstat)
    open(DEST, "w", encoding="utf-8").write(text)

    # settlements: the repaint moved the land under them. Put each on a sited tile,
    # so nothing is left standing in an ocean or on a lava field.
    wo = WorldObjects(DEST)
    st = wo.settlements()
    moved = 0
    for k, s in enumerate(st):
        wo.move_settlement(s["id"], sites[k % len(sites)])
        moved += 1
    wo.write(DEST)
    print("settlements moved onto sited tiles: %d (of %d sites)" % (moved, len(sites)))

    if "--no-deploy" not in sys.argv:
        shutil.copy2(DEST, GAME)
        print("deployed ->", GAME)



if __name__ == "__main__":
    main()
