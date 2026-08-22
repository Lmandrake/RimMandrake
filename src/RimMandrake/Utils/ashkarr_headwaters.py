#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ashkarr_headwaters.py - give a wet massif the streams it should already have.

Owner, 2026-08-22: *"Any very tall mountain cluster on the sunlit side should have at
least a short river coming out of it, it's ok if it just peters out into a salt flat
too."* Measured, eleven tall sunlit clusters had no river at all. Four of them have
the rainfall to justify one; the other two on the shortlist do not and were ruled OUT
by name - see REFUSE_DRY below, which is a guard, not a comment.

⚠️ The Ammonia Flats is NOT one of the two and never was: it sits 136-158 deg from the
substellar point at -70 to -49 C - the night-side ice cap. It reached the shortlist only
because a first pass tested |lon| < 90, which says nothing at high latitude.

    python3 src/RimMandrake/Utils/ashkarr_headwaters.py            # plan only
    python3 src/RimMandrake/Utils/ashkarr_headwaters.py --apply

HOW A STREAM IS TRACED. From the wettest high tile in the cluster, take the steepest
DOWNHILL step each move, never uphill, never revisiting, never onto a tile that
already carries a river. Stop at open water (that is a mouth), at an existing river
(that is a confluence, and the link is still written so the two join), or when the
land goes flat - which is the peter-out the owner explicitly allowed.

🔑 ROWS ARE WRITTEN MOUTH-FIRST, downstream end in column `a`, and PREPENDED, because
`jawa/world_links_import` applies rivers in file order and builds `riverDist` forward
from the mouth. Getting this backwards fails silently - `RIVER_LINKS_EMITTED_BACKWARDS_1`.

⚠️ Edits the artifact, not the producer. `ashkarr_paint.py` does not know about these.
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

TALL = 1200          # m; what counts as a tall cluster
MIN_RAIN = 300       # mm; below this a stream is not defensible on this planet
MAX_LEN = 14         # tiles; "a short river", not a trunk
MIN_LEN = 3          # shorter than this is not worth drawing

# 🔴 Ruled OUT by the owner, 2026-08-22, and refused here so a later run cannot
# quietly re-add them. Liquid water is not possible at either.
REFUSE_DRY = {
    "The Rust Cathedral": "substellar, 61 C, ~0 mm rain - anything liquid boils off",
    "The Ammonia Flats": "-30 C and 19 mm over 606 tiles; the name says the liquid is not water",
}


def load():
    tiles = list(csv.DictReader(open(STEM + "_tiles.csv", encoding="utf-8")))
    T = {}
    for r in tiles:
        t = int(r["tile"])
        T[t] = dict(row=r, elev=float(r["elev_m"]), rain=float(r["rain_mm"]),
                    water=int(r["water"]), region=r["region"], biome=r["biome"],
                    flow=float(r["river_flow"]))
    nb = {}
    rd = csv.reader(open(NEIGHBOURS, encoding="utf-8"))
    next(rd)
    for row in rd:
        nb[int(row[0])] = [int(x) for x in row[1:] if x.strip() and int(x) >= 0]
    rows = list(csv.reader(open(STEM + "_links.csv", encoding="utf-8")))
    return tiles, T, nb, rows


def clusters_of(T, nb):
    # 🔴 SUNLIT is `arc` < 90 - the angle from the SUBSTELLAR point, which the bundle
    # already carries per tile. It is NOT |lon| < 90: longitude is meaningless near a
    # pole, and reading it that way put The Ammonia Flats (arc 136-158 deg, -70 to
    # -49 C, i.e. the night-side ice cap) on the sunlit list on 2026-08-22. `arc`
    # bands track temperature exactly: 0-30 deg averages +59 C, 150-180 deg -68 C.
    tall = {t for t in T if T[t]["elev"] >= TALL and float(T[t]["row"]["arc"]) < 90.0}
    seen, out = set(), []
    for s in tall:
        if s in seen:
            continue
        st, c = [s], set()
        while st:
            x = st.pop()
            if x in c:
                continue
            c.add(x)
            st.extend(n for n in nb[x] if n in tall and n not in c)
        seen |= c
        out.append(c)
    return sorted(out, key=len, reverse=True)


def trace(src, T, nb, on_river, claimed):
    """steepest descent from src; returns the tile path, source first."""
    path, seen = [src], {src}
    while len(path) < MAX_LEN:
        cur = path[-1]
        cand = [n for n in nb[cur]
                if n not in seen and n not in claimed
                and T[n]["elev"] < T[cur]["elev"]]
        if not cand:
            break
        nxt = min(cand, key=lambda n: T[n]["elev"])
        path.append(nxt)
        seen.add(nxt)
        if T[nxt]["water"] == 1 or nxt in on_river:
            break                      # a mouth, or a confluence
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--per-massif", type=int, default=3,
                    help="how many streams to try per cluster (big clusters only)")
    a = ap.parse_args()

    tiles, T, nb, rows = load()
    header, body = rows[0], rows[1:]
    on_river = {int(x) for k, p, q, d in body if k == "river" for x in (p, q)}
    have = {frozenset((int(p), int(q))) for k, p, q, d in body if k == "river"}

    new_links, new_flow, claimed = [], {}, set()
    for c in clusters_of(T, nb):
        if c & on_river:
            continue                                   # already has water off it
        regions = {T[t]["region"] for t in c if T[t]["region"]}
        blocked = regions & set(REFUSE_DRY)
        wet = [t for t in c if T[t]["rain"] >= MIN_RAIN]
        name = max(regions, key=lambda r: sum(1 for t in c if T[t]["region"] == r)) if regions else "-"
        if blocked:
            r = blocked.pop()
            print("  SKIP  %-20s %3d tiles  RULED OUT: %s" % (r, len(c), REFUSE_DRY[r]))
            continue
        if not wet:
            print("  skip  %-20s %3d tiles  driest %d mm - under the %d mm floor"
                  % (name, len(c), max(T[t]["rain"] for t in c), MIN_RAIN))
            continue

        want = a.per_massif if len(c) >= 100 else (2 if len(c) >= 15 else 1)
        drawn = 0
        for src in sorted(wet, key=lambda t: (-T[t]["rain"], -T[t]["elev"])):
            if drawn >= want:
                break
            if src in claimed or src in on_river:
                continue
            p = trace(src, T, nb, on_river, claimed)
            if len(p) < MIN_LEN:
                continue
            claimed |= set(p[:-1])
            drawn += 1
            end = p[-1]
            fate = ("reaches water" if T[end]["water"] == 1 else
                    "joins an existing river" if end in on_river else
                    "peters out in " + T[end]["biome"])
            print("  DRAW  %-20s %2d tiles  %5.0f m -> %4.0f m  %s"
                  % (name, len(p), T[p[0]]["elev"], T[end]["elev"], fate))
            # mouth-first: walk the path backwards so `a` is always downstream
            for i in range(len(p) - 1, 0, -1):
                down, up = p[i], p[i - 1]
                if frozenset((down, up)) in have:
                    continue
                have.add(frozenset((down, up)))
                # a stream gains a little as it descends; Creek is the honest default
                d = "River" if (len(p) - i) > 8 else "Creek"
                new_links.append(["river", str(down), str(up), d])
            for i, t in enumerate(p):
                if T[t]["water"] == 1:
                    continue
                new_flow[t] = max(new_flow.get(t, 0.0), T[t]["flow"], 20.0 + 25.0 * i)

    print("\n%d new links, %d tiles gain river_flow" % (len(new_links), len(new_flow)))
    if not new_links:
        return
    if not a.apply:
        print("plan only - re-run with --apply")
        return

    first = next(i for i, r in enumerate(body) if r[0] == "river")
    body[first:first] = new_links
    with open(STEM + "_links.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(body)
    for r in tiles:
        t = int(r["tile"])
        if t in new_flow:
            r["river_flow"] = "%.1f" % new_flow[t]
    with open(STEM + "_tiles.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tiles[0].keys()))
        w.writeheader()
        w.writerows(tiles)
    print("written: %s_links.csv (%d rows)" % (STEM, len(body)))


if __name__ == "__main__":
    main()
