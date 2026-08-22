#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ashkarr_join_mouths.py - join river mouths that stop short of open water.

Seven of Ash'karr's rivers ended ONE hex from the Scald and simply stopped, the
richest of them carrying 28,936 units of accumulation into a green jungle tile that
had no river on it. Owner, 2026-08-22, looking at the globes: *"the river that leaves
the Scald towards the Scorch needs to be joined to the Scald (a green tile isn't
occupied by river)"*. This is that fix, for all seven, not just the one he saw.

    python3 src/RimMandrake/Utils/ashkarr_join_mouths.py           # plan only
    python3 src/RimMandrake/Utils/ashkarr_join_mouths.py --apply   # write

🔑 DIRECTION MATTERS AND IS EASY TO GET BACKWARDS. `jawa/world_links_import` applies
rivers IN FILE ORDER and expects each row's `a` to be the DOWNSTREAM end, mouth
first - see `RIVER_LINKS_EMITTED_BACKWARDS_1`, where the whole bundle was once
emitted the other way round and every riverDist came back wrong with nothing logged.
So each new pair is written as

    river, <lake tile>, <mid tile>, <def>      a = downstream (the lake)
    river, <mid tile>,  <old end>,  <def>

and both rows are PREPENDED to the river block, because they are downstream of every
row already in it.

⚠️ This edits the artifact, not the producer. `ashkarr_paint.py` will re-emit the
same seven gaps if the bundle is ever regenerated. That is accepted: the map is
hand-authored and one-off, and regeneration is not planned.
"""
import argparse
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WORLD = os.path.join(REPO, "world")
STEM = os.path.join(WORLD, "ASHKARR_WORLDMAP")
NEIGHBOURS = os.path.join(WORLD, "world_neighbors_sub7b.csv")

# (loose end, the green tile between, the Scald tile it should reach)
# Each triple was found by breadth-first search from every degree-1 river tile to the
# nearest water tile; these are every one that came back at a distance of exactly one.
MOUTHS = [
    (2020,  19404, 19361),
    (4380,  17343, 17342),
    (11924, 15173, 15175),
    (85,    7791,  2931),
    (2932,  15141, 1310),
    (19366, 2014,  19369),
    (2015,  19371, 8493),
]


def load_neighbours():
    nb = {}
    with open(NEIGHBOURS, encoding="utf-8") as fh:
        rd = csv.reader(fh)
        next(rd)
        for row in rd:
            nb[int(row[0])] = [int(x) for x in row[1:] if x.strip() and int(x) >= 0]
    return nb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write; otherwise plan only")
    a = ap.parse_args()

    nb = load_neighbours()
    with open(STEM + "_tiles.csv", encoding="utf-8") as fh:
        tiles = list(csv.DictReader(fh))
    by_tile = {int(r["tile"]): r for r in tiles}
    with open(STEM + "_links.csv", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    header, body = rows[0], rows[1:]

    # the def already carried by the segment that reaches each loose end - a river does
    # not shrink at its mouth, so the new segments inherit it rather than guessing.
    terminal = {}
    for kind, x, y, d in body:
        if kind != "river":
            continue
        for end, _, _ in MOUTHS:
            if int(x) == end or int(y) == end:
                terminal[end] = d

    new = []
    for end, mid, lake in MOUTHS:
        if mid not in nb.get(end, []) or lake not in nb.get(mid, []):
            sys.exit("REFUSED: %d-%d-%d is not a chain of adjacent tiles" % (end, mid, lake))
        if by_tile[lake]["water"] != "1":
            sys.exit("REFUSED: tile %d is not water" % lake)
        d = terminal[end]
        new.append(["river", str(lake), str(mid), d])
        new.append(["river", str(mid), str(end), d])
        print("  %-10s  %6d --> %6d --> %6d   flow %9.0f  through %s"
              % (d, end, mid, lake, float(by_tile[end]["river_flow"]), by_tile[mid]["biome"]))

    # the intervening tile carries the same water as the end it continues
    flows = {mid: float(by_tile[end]["river_flow"]) for end, mid, _ in MOUTHS}

    print("\n%d new river links across %d mouths; %d tiles gain river_flow"
          % (len(new), len(MOUTHS), len(flows)))
    if not a.apply:
        print("plan only - re-run with --apply")
        return

    first_river = next(i for i, r in enumerate(body) if r[0] == "river")
    body[first_river:first_river] = new
    with open(STEM + "_links.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(body)

    for r in tiles:
        t = int(r["tile"])
        if t in flows:
            r["river_flow"] = "%.1f" % flows[t]
    with open(STEM + "_tiles.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tiles[0].keys()))
        w.writeheader()
        w.writerows(tiles)
    print("written: %s_links.csv (%d rows) and %s_tiles.csv"
          % (STEM, len(body), STEM))


if __name__ == "__main__":
    main()
