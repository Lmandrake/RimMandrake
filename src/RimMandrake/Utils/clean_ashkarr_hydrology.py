#!/usr/bin/env python3
"""Strip the roads and rivers the repaint stranded.

🔑 Roads and rivers are NOT graphs. They are three parallel per-tile arrays each,
inside the SurfaceLayer, and they can be edited like any other array:

    tileRoadOriginsDeflate    4 bytes/entry   tile index
    tileRoadAdjacencyDeflate  1 byte/entry    neighbour slot
    tileRoadDefDeflate        2 bytes/entry   RoadDef shortHash
    tileRiver*Deflate         same shapes
    tileRiverDistancesDeflate 1 byte/TILE     (not per entry - left alone)

⚠️ This corrects a standing note in skills/rimworld-world-editing that called them
"graphs, deliberately untouched". They are arrays and they are editable.

Two problems the repaint created, both measured:
  * 41 of 607 road tiles ended up under the new seas.
  * 38 of 237 river tiles ended up under them, and 79 more run across the frozen
    nightside - where the fiction says there is no liquid water at all.

Removing an entry ends a road or river at that tile, which is what a coast does
anyway. Nothing is added, so no new connection can dangle.

    python3 src/RimMandrake/Utils/clean_ashkarr_hydrology.py [--dry]
"""
import base64
import csv
import math
import os
import re
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from worldmap import WorldGrid

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SAVE = os.path.join(REPO, "world", "WORLDMAP_gen.rws")
TILES = os.path.join(REPO, "world", "world_tiles_lada.csv")
GAME = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
        "RimWorld by Ludeon Studios/Saves/WORLDMAP_gen.rws")

WATER = {"Ocean", "SeaIce"}
NIGHT_ARC = 100.0        # past this, liquid water does not exist on this planet


def dec(b64):
    return zlib.decompress(base64.b64decode(b64), -15)


def enc(raw):
    co = zlib.compressobj(9, zlib.DEFLATED, -15)
    return base64.b64encode(co.compress(raw) + co.flush()).decode("ascii")


def main():
    dry = "--dry" in sys.argv
    text = open(SAVE, encoding="utf-8").read()
    g = WorldGrid(SAVE)
    bn = g.biome_names()
    n = len(bn)

    arc = {}
    for r in csv.DictReader(open(TILES)):
        la, lo = math.radians(float(r["lat"])), math.radians(float(r["long"]))
        arc[int(r["tile"])] = math.degrees(math.acos(max(-1.0, min(1.0,
                                math.cos(lo) * math.cos(la)))))

    j = text.find('Class="SurfaceLayer"')

    def grab(tag):
        m = re.search(r"<%s>([^<]*)</%s>" % (tag, tag), text[j:j + 900000])
        return m, (dec(m.group(1)) if m and m.group(1).strip() else None)

    for kind, drop_night in (("Road", False), ("River", True)):
        mo, org = grab("tile%sOriginsDeflate" % kind)
        ma, adj = grab("tile%sAdjacencyDeflate" % kind)
        md, dfs = grab("tile%sDefDeflate" % kind)
        if not org:
            print("%s: no data" % kind)
            continue
        cnt = len(org) // 4
        tiles = list(struct.unpack("<%dI" % cnt, org[:cnt * 4]))
        defs = list(struct.unpack("<%dH" % cnt, dfs[:cnt * 2]))
        adjs = list(adj[:cnt])

        keep, cut_water, cut_night = [], 0, 0
        for k, t in enumerate(tiles):
            if t < n and bn[t] in WATER:
                cut_water += 1
                continue
            if drop_night and t < n and arc.get(t, 0) > NIGHT_ARC:
                cut_night += 1
                continue
            keep.append(k)

        print("%s: %d entries -> %d kept  (cut %d in water%s)"
              % (kind, cnt, len(keep), cut_water,
                 ", %d on the nightside" % cut_night if drop_night else ""))

        new_org = struct.pack("<%dI" % len(keep), *[tiles[k] for k in keep])
        new_adj = bytes(adjs[k] for k in keep)
        new_def = struct.pack("<%dH" % len(keep), *[defs[k] for k in keep])
        for mm, raw, tag in ((mo, new_org, "Origins"), (ma, new_adj, "Adjacency"),
                             (md, new_def, "Def")):
            old = mm.group(0)
            new = "<tile%s%sDeflate>%s</tile%s%sDeflate>" % (kind, tag, enc(raw), kind, tag)
            text = text.replace(old, new, 1)
        j = text.find('Class="SurfaceLayer"')

    if dry:
        print("\n--dry: nothing written")
        return
    open(SAVE, "w", encoding="utf-8").write(text)
    with open(SAVE, "rb") as a, open(GAME, "wb") as b:
        b.write(a.read())
    print("\nwrote and deployed")


if __name__ == "__main__":
    main()
