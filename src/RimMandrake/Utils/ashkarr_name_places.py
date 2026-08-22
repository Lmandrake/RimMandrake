#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ashkarr_name_places.py - write the drafted region names onto the map.

Half of Ash'karr carried an empty `region`: 11,107 of 21,872 tiles, one contiguous
blob spanning arc 40-152 deg. `design/Jawa/worldbuilding/named_places_draft.md` is the
draft the owner reviews; this reads the Name and seed columns out of it and writes the
names into `world/ASHKARR_WORLDMAP_tiles.csv`.

    python3 src/RimMandrake/Utils/ashkarr_name_places.py            # plan only
    python3 src/RimMandrake/Utils/ashkarr_name_places.py --apply

🔑 THE SEED IS THE CONTRACT. A block is identified by one tile id, not by its position
in a list, so the owner can reorder, delete or rename rows in the draft and this still
puts the right name on the right ground. The clustering is recomputed here by exactly
the rule that produced the draft - keyed by (band, terrain), contiguous, seeds walked
in ascending tile order - and it REFUSES if a seed's block comes back a different size
than the draft recorded, because that means the map moved underneath the draft.

⛔ A row whose Name is `-` is a deliberate rejection and stays unnamed.
"""
import argparse
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WORLD = os.path.join(REPO, "world")
STEM = os.path.join(WORLD, "ASHKARR_WORLDMAP")
NEIGHBOURS = os.path.join(WORLD, "world_neighbors_sub7b.csv")
DRAFT = os.path.join(REPO, "design", "Jawa", "worldbuilding", "named_places_draft.md")

ROW = re.compile(r"^\|\s*\*\*(?P<name>[^*|]+)\*\*\s*\|\s*(?P<n>\d+)\s*\|.*\|\s*`(?P<seed>\d+)`\s*\|\s*$")
ROW_PLAIN = re.compile(r"^\|\s*(?P<name>[^|]+?)\s*\|\s*(?P<n>\d+)\s*\|.*\|\s*`(?P<seed>\d+)`\s*\|\s*$")


def band(a):
    return ("day" if a < 60 else "daymargin" if a < 85 else "term" if a < 100
            else "nightmargin" if a < 125 else "night")


def terr(b):
    if b == "AB_RockyCrags":
        return "crags"
    if b in ("Desert", "ExtremeDesert"):
        return "desert"
    if b == "AridShrubland":
        return "shrub"
    if b == "ZBiome_Badlands":
        return "badlands"
    if b in ("AB_MycoticJungle", "BMT_FungalForest", "PoisonForest",
             "AB_FeraliskInfestedJungle", "AB_MiasmicMangrove", "AB_OcularForest"):
        return "fungal"
    if b in ("Wasteland", "Scarlands"):
        return "waste"
    if b in ("AB_PropaneLakes", "AB_TarPits", "AB_GelatinousSuperorganism"):
        return "chem"
    if b in ("Volcano", "LavaField", "AB_PyroclasticConflagration"):
        return "volcanic"
    if b == "BMT_CrystalCaverns":
        return "crystal"
    if b in ("ZBiome_Grasslands", "ZBiome_DesertOasis"):
        return "green"
    return b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    rows = list(csv.DictReader(open(STEM + "_tiles.csv", encoding="utf-8")))
    T = {int(r["tile"]): r for r in rows}
    nb = {}
    rd = csv.reader(open(NEIGHBOURS, encoding="utf-8"))
    next(rd)
    for row in rd:
        nb[int(row[0])] = [int(x) for x in row[1:] if x.strip() and int(x) >= 0]

    key = {t: (band(float(r["arc"])), terr(r["biome"]))
           for t, r in T.items() if not r["region"] and r["water"] == "0"}
    seen, blocks = set(), {}
    for s in sorted(key):
        if s in seen:
            continue
        st, c = [s], set()
        while st:
            x = st.pop()
            if x in c:
                continue
            c.add(x)
            st.extend(n for n in nb[x] if n in key and key[n] == key[s] and n not in c)
        seen |= c
        blocks[min(c)] = c

    draft = []
    for line in open(DRAFT, encoding="utf-8"):
        m = ROW.match(line.rstrip("\n")) or ROW_PLAIN.match(line.rstrip("\n"))
        if m and m.group("name").strip() not in ("Name",):
            draft.append((m.group("name").strip(), int(m.group("n")), int(m.group("seed"))))
    if not draft:
        sys.exit("REFUSED: no table rows parsed out of %s" % DRAFT)

    named, skipped, total = {}, [], 0
    for name, n, seed in draft:
        if name == "-":
            skipped.append((seed, "rejected in the draft"))
            continue
        if seed not in blocks:
            sys.exit("REFUSED: seed %d is not the seed of any unnamed block. The map moved "
                     "under the draft - re-cut it before applying." % seed)
        c = blocks[seed]
        if len(c) != n:
            sys.exit("REFUSED: block %d is %d tiles now, the draft recorded %d. The map moved "
                     "under the draft - re-cut it before applying." % (seed, len(c), n))
        for t in c:
            named[t] = name
        total += len(c)
        print("  %-22s %5d tiles   seed %d" % (name, len(c), seed))

    before = sum(1 for r in rows if not r["region"])
    print("\n%d blocks named, %d tiles gain a region name" % (len(draft) - len(skipped), total))
    print("unnamed tiles: %d -> %d of %d" % (before, before - total, len(rows)))
    for seed, why in skipped:
        print("  skipped seed %d: %s" % (seed, why))
    if not a.apply:
        print("plan only - re-run with --apply")
        return

    for r in rows:
        t = int(r["tile"])
        if t in named:
            r["region"] = named[t]
    with open(STEM + "_tiles.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("written: %s_tiles.csv" % STEM)


if __name__ == "__main__":
    main()
