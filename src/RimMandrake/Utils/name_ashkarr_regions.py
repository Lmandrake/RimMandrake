#!/usr/bin/env python3
"""Put Ash'karr's region names ON the regions they name.

The generated world labels territories from its own worldgen ("Orangefeather
Island"), and those labels float wherever worldgen put them - which after a
repaint means a "Reach" drawn across open ocean.

Two facts make this fixable, both measured 2026-08-16:

  1. `tileFeature` (2 bytes/tile, 0xFFFF = none) is the exact tile -> feature
     membership. Nothing has to be inferred from the label's position.

  2. 🔑 THE drawCenter CONVENTION, recovered by comparing stored centres against
     the centroid of each feature's own member tiles:

         drawCenter = (cosLat*sinLon,  sinLat,  -cosLat*cosLon) * 100

     i.e. game x = east, y = north, **z = NEGATIVE cos(lat)cos(long)**. An
     earlier guess of `long = atan2(x, z)` missed that negation and put mountain
     ranges on the sea floor, which is what caught it.

So: re-cut the features to OUR regions, name them, and write a centre that is
the real centroid of each one's tiles.

    python3 src/RimMandrake/Utils/name_ashkarr_regions.py [--dry]
"""
import csv
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from worldmap import WorldGrid

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SAVE = os.path.join(REPO, "world", "WORLDMAP_gen.rws")
TILES = os.path.join(REPO, "world", "world_tiles_lada.csv")
GAME = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
        "RimWorld by Ludeon Studios/Saves/WORLDMAP_gen.rws")

NONE = 0xFFFF


def angdiff(a, b):
    return abs((a - b + 180.0) % 360.0 - 180.0)


def quadrant(bear):
    """Four tracts around the substellar axis, so a huge region is not one label."""
    if angdiff(bear, 0) < 45:
        return "Gray"
    if angdiff(bear, 90) < 45:
        return "North"
    if angdiff(bear, 180) < 45:
        return "Twilight"
    return "South"


def region_name(arc, bear, biome):
    """The label a tile belongs under. Order matters; first match wins."""
    q = quadrant(bear)
    if biome == "Ocean":
        if arc < 55:
            return "The Scald"
        return "The Twilight Sea" if angdiff(bear, 170) < 70 else "The Gray Sea"
    if biome == "SeaIce":
        return "The Dead Ice"
    if biome == "AB_MechanoidIntrusion":
        return "The Rust Cathedral"
    if biome == "Scarlands" and arc < 26:
        return "The Scorch"
    if biome == "AB_PropaneLakes":
        return "The Ammonia Flats"
    if arc < 20:
        return "The Anvil"
    if arc < 26 and angdiff(bear, 185) < 70:
        return "The Scald Spine"
    if biome in ("Volcano", "LavaField", "AB_PyroclasticConflagration",
                 "AB_GallatrossGraveyard") and arc < 45:
        return "The Ashteeth"
    if 24 < arc < 62 and angdiff(bear, 0) < 22:
        return "The Fall Line"
    if 52 < arc < 92 and angdiff(bear, 178) < 24:
        return "The Dew Belt"
    if arc < 40:
        return "The Dune Sea"
    if arc < 58:
        return "The %s Ring" % q
    if arc < 78:
        return "The %s Barrens" % q
    if arc < 103:
        if angdiff(bear, 18) < 34:
            return "The Salt"
        if angdiff(bear, 196) < 34:
            return "The Nightspill"
        return "The %s Marches" % q
    if arc < 118:
        return "The %s Glow" % q
    if arc < 130 and angdiff(bear, 4) < 45:
        return "The Sunreach"
    if arc > 152:
        return "The Umbra"
    return "The %s Crags" % q


# def to file each label under - purely cosmetic, but a sea should not be a mountain
DEF_FOR = {
    "The Scald": "Ocean", "The Twilight Sea": "Ocean", "The Gray Sea": "Ocean",
    "The Dead Ice": "Ocean", "The Scald Spine": "MountainRange",
    "The Ashteeth": "MountainRange", "The Rust Cathedral": "MountainRange",
}


def main():
    dry = "--dry" in sys.argv
    g = WorldGrid(SAVE)
    bn = g.biome_names()
    n = len(bn)
    geo = {}
    for r in csv.DictReader(open(TILES)):
        lat, lon = float(r["lat"]), float(r["long"])
        la, lo = math.radians(lat), math.radians(lon)
        arc = math.degrees(math.acos(max(-1.0, min(1.0, math.cos(lo) * math.cos(la)))))
        bear = math.degrees(math.atan2(math.sin(la), math.cos(la) * math.sin(lo))) % 360.0
        geo[int(r["tile"])] = (lat, lon, arc, bear)

    members = {}
    for t in range(n):
        lat, lon, arc, bear = geo[t]
        members.setdefault(region_name(arc, bear, bn[t]), []).append(t)

    text = open(SAVE, encoding="utf-8").read()
    i = text.find("<features>")
    j = text.find("</features>", i + 10)
    blocks = re.findall(r"<li>.*?</li>", text[i:j], re.S)
    slots = len(blocks)

    def centre_of(mem):
        vs = []
        for t in mem:
            la, lo = math.radians(geo[t][0]), math.radians(geo[t][1])
            vs.append((math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)))
        cx = sum(v[0] for v in vs) / len(vs)
        cy = sum(v[1] for v in vs) / len(vs)
        cz = sum(v[2] for v in vs) / len(vs)
        m = math.sqrt(cx * cx + cy * cy + cz * cz) or 1.0
        return cx / m, cy / m, cz / m

    # 🔴 Labels that sit too close pile on top of each other on the globe. Accept
    # biggest-first and drop any region whose centre is within MIN_SEP of one already
    # accepted - its tiles simply carry no feature, which is what 40% of the pristine
    # world's tiles do anyway.
    # 🔴 Priority, NOT size. Sorting by tile count let generic tracts crowd out
    # The Scald and the Rust Cathedral - the places the world exists for.
    CANON = ["The Scald", "The Rust Cathedral", "The Anvil", "The Scald Spine",
             "The Ashteeth", "The Scorch", "The Twilight Sea", "The Gray Sea",
             "The Dew Belt", "The Fall Line", "The Salt", "The Nightspill",
             "The Sunreach", "The Umbra", "The Ammonia Flats", "The Dead Ice"]
    MIN_SEP = 11.0
    rank = {nm: i for i, nm in enumerate(CANON)}
    cand = sorted(members.items(),
                  key=lambda kv: (rank.get(kv[0], 999), -len(kv[1])))
    ordered, centres, dropped = [], [], []
    for name, mem in cand:
        c = centre_of(mem)
        far = all(math.degrees(math.acos(max(-1.0, min(1.0,
                  c[0] * o[0] + c[1] * o[1] + c[2] * o[2])))) >= MIN_SEP for o in centres)
        if far:
            ordered.append((name, mem))
            centres.append(c)
        else:
            dropped.append(name)
    if dropped:
        print("labels dropped for crowding: %s" % ", ".join(dropped))
    if len(ordered) > slots:
        print("!! %d regions but only %d feature slots - dropping the smallest %d"
              % (len(ordered), slots, len(ordered) - slots))
    ordered = ordered[:slots]

    new_blocks, tf = [], [NONE] * n
    print("%-22s %6s  %s" % ("region", "tiles", "centre lat/long"))
    for k, (name, mem) in enumerate(ordered):
        vs = []
        for t in mem:
            lat, lon = math.radians(geo[t][0]), math.radians(geo[t][1])
            vs.append((math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon),
                       math.sin(lat)))
        cx = sum(v[0] for v in vs) / len(vs)
        cy = sum(v[1] for v in vs) / len(vs)
        cz = sum(v[2] for v in vs) / len(vs)
        m = math.sqrt(cx * cx + cy * cy + cz * cz) or 1.0
        cx, cy, cz = cx / m, cy / m, cz / m
        # the recovered convention
        gx, gy, gz = cx * 0 + cy * 100, cz * 100, -cx * 100
        clat = math.degrees(math.asin(cz))
        clon = math.degrees(math.atan2(cy, cx))
        # vanilla scaling: its own features run 2.4..19.2 at up to ~1950 tiles
        size = max(2.4, min(19.2, 0.44 * math.sqrt(len(mem))))
        blk = blocks[k]
        blk = re.sub(r"<def>\w+</def>", "<def>%s</def>" % DEF_FOR.get(name, "AridShrubland"), blk, count=1)
        blk = re.sub(r"<name>[^<]*</name>", "<name>%s</name>" % name, blk, count=1)
        blk = re.sub(r"<drawCenter>[^<]*</drawCenter>",
                     "<drawCenter>(%.6f, %.6f, %.6f)</drawCenter>" % (gx, gy, gz), blk, count=1)
        if "<maxDrawSizeInTiles>" in blk:
            blk = re.sub(r"<maxDrawSizeInTiles>[^<]*</maxDrawSizeInTiles>",
                         "<maxDrawSizeInTiles>%.4f</maxDrawSizeInTiles>" % size, blk, count=1)
        new_blocks.append(blk)
        for t in mem:
            tf[t] = k
        print("%-22s %6d  %7.1f %8.1f" % (name, len(mem), clat, clon))

    for k in range(len(ordered), slots):
        new_blocks.append(blocks[k])

    seg = text[i:j]
    for old, new in zip(blocks, new_blocks):
        seg = seg.replace(old, new, 1)
    text = text[:i] + seg + text[j:]

    if dry:
        print("\n--dry: nothing written")
        return
    open(SAVE, "w", encoding="utf-8").write(text)

    g2 = WorldGrid(SAVE)
    for t in range(n):
        g2.arrays["tileFeature"][t] = tf[t]
    g2.write(SAVE)
    with open(SAVE, "rb") as a, open(GAME, "wb") as b:
        b.write(a.read())
    print("\nwrote %d named regions, reassigned tileFeature, deployed" % len(ordered))


if __name__ == "__main__":
    main()
