#!/usr/bin/env python3
"""Write the generated world into the savegame, and deploy it.

Consumes the four offline stages and nothing else:

    world/relief.npz   elevation, sea level
    world/hydro.npz    temperature, rainfall, rivers
    world/biomes.npz   biome, hilliness
    world/settle.npz   settlement sites, roads

⚠️ RIVERS AND ROADS ARE NOT WRITTEN, and this is deliberate. They are not per-tile
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
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from worldmap import WorldGrid, WorldObjects, DECODE

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "world", "WORLDMAP_source.rws")
DEST = os.path.join(REPO, "world", "WORLDMAP_gen.rws")
GAME = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
        "RimWorld by Ludeon Studios/Saves/WORLDMAP_gen.rws")

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
    hb = g.hash_by_biome

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
        lo_hi = POLLUTED.get(nm)
        p_arr[t] = int(round(rng.uniform(*lo_hi) * POLL_FULL)) if lo_hi else 0

    print("wrote %d tiles: %d biomes, elevation %.0f..%.0f m, temp %.0f..%.0f C, "
          "rain %.0f..%.0f mm" % (n, len(set(map(str, name))), elev.min(), elev.max(),
                                  T.min(), T.max(), mm.min(), mm.max()))

    if dry:
        print("--dry: nothing written")
        return
    g.write(DEST)

    text = open(DEST, encoding="utf-8").read()
    text, removed = strip_links(text)
    print("stripped inherited links: %s (they belong to a planet that no longer "
          "exists)" % (removed or "none found"))
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
    print("\n⚠️ NO RIVERS AND NO ROADS in this build - see the module docstring.")


if __name__ == "__main__":
    main()
