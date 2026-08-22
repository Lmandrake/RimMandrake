#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ashkarr_final_fit.py - the last two structural defects the 2026-08-22 reviews found.

  1 STRANDED SEATS  Hollow Nave (6482) and No Master (19350) sit ON `AB_MechanoidIntrusion`,
                    a biome whose `allowRoads` is false, so no road to either is visible in
                    game however it is routed. Both settlements' OWN why-text says they sit
                    *beside* the Rust Cathedral, not on it - so moving them one tile off the
                    mechanoid ground restores the fiction and the road at the same time.
  2 UPHILL RIVERS   28 of 291 river rows had the downstream end (`a`) HIGHER than the
                    upstream end (`b`). `jawa/world_links_import` builds riverDist forward
                    from `a`, so a reversed row lays the river backwards and logs nothing.
                    Rows are swapped where elevation is decisive; ties are left alone and
                    counted, because a flat pair carries no evidence either way.
"""
import csv, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
W = os.path.join(REPO, "world"); STEM = os.path.join(W, "ASHKARR_WORLDMAP")
APPLY = "--apply" in sys.argv
trows = list(csv.DictReader(open(STEM + "_tiles.csv", encoding="utf-8")))
T = {int(r["tile"]): r for r in trows}
nb = {}
rd = csv.reader(open(os.path.join(W, "world_neighbors_sub7b.csv"), encoding="utf-8")); next(rd)
for row in rd: nb[int(row[0])] = [int(x) for x in row[1:] if x.strip() and int(x) >= 0]
srows = list(csv.DictReader(open(STEM + "_settlements.csv", encoding="utf-8")))
lrows = list(csv.DictReader(open(STEM + "_landmarks.csv", encoding="utf-8")))
links = list(csv.reader(open(STEM + "_links.csv", encoding="utf-8")))
header, body = links[0], links[1:]
occupied = {int(r["tile"]) for r in srows} | {int(r["tile"]) for r in lrows}
HIDE = {"AB_MechanoidIntrusion", "AB_PropaneLakes", "Ocean", "Lake", "IceSheet", "SeaIce"}

moved = 0
for s in srows:
    t = int(s["tile"])
    if T[t]["biome"] not in HIDE: continue
    dest = None
    for n in sorted(nb[t], key=lambda n: (int(T[n]["hilliness"]), n)):
        if n in occupied or T[n]["biome"] in HIDE or T[n]["water"] == "1" or int(T[n]["hilliness"]) >= 5:
            continue
        dest = n; break
    if dest is None:
        print("  ! %s (tile %d) has no free neighbour off the hiding biome" % (s["name"], t)); continue
    occupied.discard(t); occupied.add(dest)
    print("  moved %-22s %6d (%s) -> %6d (%s)" % (s["name"], t, T[t]["biome"], dest, T[dest]["biome"]))
    s["tile"] = str(dest); s["lat"] = T[dest]["lat"]; s["lon"] = T[dest]["lon"]
    s["arc"] = T[dest]["arc"]; s["biome"] = T[dest]["biome"]
    moved += 1
print("1 STRANDED SEATS  moved %d settlements off a road-hiding biome" % moved)

swapped = tied = 0
for row in body:
    if row[0] != "river": continue
    a_, b_ = int(row[1]), int(row[2])
    ea, eb = float(T[a_]["elev_m"]), float(T[b_]["elev_m"])
    if ea > eb: row[1], row[2] = str(b_), str(a_); swapped += 1
    elif ea == eb: tied += 1
print("2 UPHILL RIVERS   swapped %d rows so `a` is downstream; %d flat pairs left alone" % (swapped, tied))

if APPLY:
    with open(STEM + "_settlements.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(srows[0].keys())); w.writeheader(); w.writerows(srows)
    with open(STEM + "_links.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(header); w.writerows(body)
    print("\nwritten: settlements and links")
else:
    print("\nplan only - re-run with --apply")
