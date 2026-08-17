#!/usr/bin/env python3
"""Give Ash'karr its people and its place-names.

Runs AFTER paint_ashkarr.py, on world/WORLDMAP_gen.rws, and does three things:

  1. CONVERTS every settlement to one of our ratified factions. Nothing is deleted -
     converting rewrites one <faction> tag, where deleting a faction would tear a
     hole in the save's reference graph.
  2. MOVES each settlement to a tile its faction would actually hold, chosen from
     the painted world by arc, bearing and biome, then NAMES it from that faction's
     own register.
  3. RENAMES the world features. Their generated names ("Orangefeather Island") are
     wrong for this planet.
     ⚠️ Renamed BY TYPE ONLY. A feature's <drawCenter> could not be decoded into
     lat/long - MountainRange centres resolved to -350 m, i.e. the sea floor - so
     no geographic claim is made about any feature name.

    python3 src/RimMandrake/Utils/populate_ashkarr.py [--dry]
"""
import csv
import math
import os
import random
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

random.seed(20260816)

# The ratified keep list: the eight Jawa_* factions plus SECTION 4 of
# infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md. Everything else on the
# planet is converted into one of these.
OURS = [
    "Empire", "OuterRim_GalacticEmpire", "Jawa_DeepwaterCompact", "Jawa_HuttCartel",
    "Jawa_WildsteamClan", "Jawa_IndigenousTribes", "Jawa_FreeDroidEnclaves",
    "Jawa_Junkers", "Jawa_AscendantHelix", "Jawa_GeonosianFoundryHive",
    "OuterRim_MoistureFarmers", "OuterRim_BinaryStarRaiders", "JDSCIS_CIS_Faction",
    "guy762_KotORFaction_RogueDroids",
]

# how many settlements each faction gets, and where it wants them
PLAN = [
    # (defName, count, region predicate key, name list)
    ("Empire", 1, "capital", ["Sunspire"]),
    ("Empire", 2, "imperial", ["Ashgarrison", "Oxalate Watch"]),
    ("Jawa_DeepwaterCompact", 8, "twilight_shore",
     ["Butora", "Deepwater Hold", "Coldquay", "Fogmoor", "The Wharves", "Saltless",
      "Greenhaven", "Tidewatch", "Anchor Deep"]),
    ("Jawa_HuttCartel", 6, "twilight_shore",
     ["Spicehead", "Sarlacc Ground", "Itunt", "The Yards", "Bellyrock", "Slaver's Rest"]),
    ("Jawa_WildsteamClan", 5, "terminator",
     ["Rego", "Steamreach", "Marrowmarsh", "The Wet Dark", "Bogholt", "Fenrun"]),
    ("OuterRim_MoistureFarmers", 9, "dew_belt",
     ["Dewhome", "Condenser Flats", "Thiussia", "Vaporhead", "Bell Cistern",
      "Dryrun", "The Trellis", "Mistcatch", "Farside Wells", "Hollowdew", "Stillmarket"]),
    ("Jawa_FreeDroidEnclaves", 6, "volcanic",
     ["The Trade Socket", "Arlor", "Solder Deep", "Vent Nine", "Cold Solder",
      "The Repair Yard", "Springhouse"]),
    ("Jawa_Junkers", 5, "sunreach",
     ["The Fuel Works", "The Gray Fleet", "Cryohaul", "Ammonia Landing",
      "The Crooks", "Sump"]),
    ("Jawa_IndigenousTribes", 7, "ring",
     ["Barno", "The Black Ram", "Duneward", "Stone Moot", "Farwater", "Redscarp",
      "The Long Camp", "Ashfoot"]),
    ("Jawa_AscendantHelix", 3, "ring",
     ["The Shattered Empire", "Helix Landing", "Ascendant Reach", "The Coil"]),
    ("Jawa_GeonosianFoundryHive", 3, "volcanic",
     ["The Black Ape Zato", "Foundry Hive", "Chitin Works"]),
    ("guy762_KotORFaction_RogueDroids", 4, "deep_dark",
     ["The Hopeless Call", "Rust Choir", "Null Station", "The Listening Dark"]),
    ("JDSCIS_CIS_Faction", 3, "dayside",
     ["Separatist Landing", "Foundry Remnant", "The Cold Line"]),
    ("OuterRim_BinaryStarRaiders", 3, "fall_line",
     ["Wreckfall", "The Debris Camp", "Binary Roost"]),
    ("OuterRim_GalacticEmpire", 1, "imperial", ["Garrison Tertius"]),
]

FEATURE_NAMES = {
    "Island":        ["Kesh Rise", "Anvil Rock", "The Solder Rise", "Karr Holdfast",
                      "Dun Rise", "Ossa Rock", "The Cinder Rise", "Vek Holdfast",
                      "Ash Rise", "Tessin Rock", "The Quiet Rise"],
    "Archipelago":   ["The Scatter", "Broken Chain", "The Nine Stones"],
    "Peninsula":     ["Long Reach", "Sarlacc Reach", "The Hook", "Dust Reach",
                      "Kessa Reach", "The Claw", "Iron Reach", "Grey Reach",
                      "The Spur"],
    "MountainRange": ["The Scald Spine", "Ashteeth", "The Forge Ridge",
                      "Cinderwall", "The Broken Teeth"],
    "Desert":        ["The Great Waste", "Dune Sea", "The Long Burn"],
    "AridShrubland": ["The Scrub", "Thornflats", "Grey Scrub", "Bitterbrush",
                      "The Open Ground"],
    "ZBiome_Badlands": ["The Sunken Badlands"],
}


def load_geo():
    geo = {}
    for r in csv.DictReader(open(TILES)):
        lat, lon = math.radians(float(r["lat"])), math.radians(float(r["long"]))
        arc = math.degrees(math.acos(max(-1.0, min(1.0, math.cos(lon) * math.cos(lat)))))
        bear = math.degrees(math.atan2(math.sin(lat), math.cos(lat) * math.sin(lon))) % 360.0
        geo[int(r["tile"])] = (arc, bear)
    return geo


def angdiff(a, b):
    return abs((a - b + 180.0) % 360.0 - 180.0)


def main():
    dry = "--dry" in sys.argv
    geo = load_geo()
    g = WorldGrid(SAVE)
    bn = g.biome_names()
    n = len(bn)
    WATERB = ("Ocean", "SeaIce")

    def near_water(t, within=2):
        """Land tile whose neighbourhood holds water - a coast, approximately."""
        arc, bear = geo[t]
        for u in range(max(0, t - 60), min(n, t + 60)):
            if bn[u] in WATERB:
                a2, b2 = geo[u]
                if abs(a2 - arc) < within and angdiff(b2, bear) < within * 2:
                    return True
        return False

    def pool(key):
        out = []
        for t in range(n):
            arc, bear = geo[t]
            b = bn[t]
            if b in WATERB:
                continue
            if key == "capital":
                ok = 26 < arc < 46 and angdiff(bear, 185) < 40 and near_water(t, 3)
            elif key == "imperial":
                ok = 30 < arc < 70 and b in ("AridShrubland", "Desert", "Wasteland")
            elif key == "twilight_shore":
                ok = 78 < arc < 105 and angdiff(bear, 170) < 55 and near_water(t, 3)
            elif key == "terminator":
                ok = 80 < arc < 103
            elif key == "dew_belt":
                ok = 52 < arc < 92 and angdiff(bear, 178) < 24
            elif key == "volcanic":
                ok = 18 < arc < 40 and angdiff(bear, 185) < 70
            elif key == "sunreach":
                ok = 95 < arc < 130 and angdiff(bear, 4) < 45
            elif key == "ring":
                ok = 40 < arc < 78
            elif key == "deep_dark":
                ok = arc > 120
            elif key == "fall_line":
                ok = 24 < arc < 62 and angdiff(bear, 0) < 20
            else:                                   # dayside
                ok = 25 < arc < 75
            if ok:
                out.append(t)
        return out

    # ---- build the assignment
    text = open(SAVE, encoding="utf-8").read()
    fac_seg = text[text.find("<allFactions>"):text.find("</allFactions>")]
    fac_defs = re.findall(r"<def>([\w.]+)</def>\s*<name>", fac_seg)
    idx_of = {}
    for i, dn in enumerate(fac_defs):
        idx_of.setdefault(dn, i)
    missing = [f for f, *_ in PLAN if f not in idx_of]
    if missing:
        print("WARNING: not in this world:", sorted(set(missing)))

    assign, used = [], set()
    for defname, count, key, names in PLAN:
        if defname not in idx_of:
            continue
        cands = [t for t in pool(key) if t not in used]
        random.shuffle(cands)
        if not cands:
            print("  no tiles for", defname, key)
            continue
        for k in range(min(count, len(cands))):
            t = cands[k]
            used.add(t)
            assign.append((idx_of[defname], t, names[k % len(names)], defname))

    blocks = list(re.finditer(r'<li Class="Settlement">.*?</li>', text, re.S))
    print("settlements in save: %d   placements planned: %d" % (len(blocks), len(assign)))

    out, prev, moved = [], 0, 0
    for i, m in enumerate(blocks):
        blk = m.group(0)
        if i < len(assign):
            fidx, tile, name, defname = assign[i]
            blk = re.sub(r"<tile>[^<]*</tile>", "<tile>%d,0</tile>" % tile, blk, count=1)
            blk = re.sub(r"<faction>Faction_\d+</faction>",
                         "<faction>Faction_%d</faction>" % fidx, blk, count=1)
            if "<nameInt>" in blk:
                blk = re.sub(r"<nameInt>[^<]*</nameInt>",
                             "<nameInt>%s</nameInt>" % name, blk, count=1)
            moved += 1
        out.append(text[prev:m.start()])
        out.append(blk)
        prev = m.end()
    out.append(text[prev:])
    text = "".join(out)

    # ---- feature names, BY TYPE ONLY
    pools = {k: list(v) for k, v in FEATURE_NAMES.items()}
    renamed = 0

    def rename(mo):
        nonlocal renamed
        dfn, rest, old = mo.group(1), mo.group(2), mo.group(3)
        if dfn in pools and pools[dfn]:
            renamed += 1
            return "<def>%s</def>%s<name>%s</name>" % (dfn, rest, pools[dfn].pop(0))
        return mo.group(0)

    i = text.find("<features>")
    j = text.find("</features>", i + 10)
    seg = re.sub(r"<def>(\w+)</def>(\s*(?:<uniqueID>\d+</uniqueID>\s*)?)<name>([^<]*)</name>",
                 rename, text[i:j])
    text = text[:i] + seg + text[j:]

    print("settlements rewritten: %d   features renamed: %d" % (moved, renamed))
    by = {}
    for fidx, tile, name, defname in assign:
        by[defname] = by.get(defname, 0) + 1
    for k in sorted(by, key=lambda x: -by[x]):
        print("   %-34s %d" % (k, by[k]))

    if dry:
        print("\n--dry: nothing written")
        return
    open(SAVE, "w", encoding="utf-8").write(text)
    with open(SAVE, "rb") as a, open(GAME, "wb") as b:
        b.write(a.read())
    print("\nwrote and deployed")


if __name__ == "__main__":
    main()
