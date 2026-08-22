#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ashkarr_quagmire_bed.py - flatten a lava plain so the magmatic quagmire can exist.

Owner, 2026-08-22: *"Do force magmaticquagmire somewhere, that's so cool. A little patch
would do."* It could not be honoured as the terrain stood. `AB_MagmaticQuagmire` requires
three mutators - AB_MagmaticQuagmire, AB_MagmaVents, AB_GeothermalHotspots - all
whitelisted to `AB_PyroclasticConflagration`, and the first also caps at
`maxHilliness = Flat`. Ash'karr has 31 pyroclastic tiles and every one is hilliness 3, 4
or 5. Nothing was flat, so nothing was legal.

🔑 The right answer is to change the GROUND, not the request. A magmatic quagmire IS flat
ground - a lava plain that has not finished setting - so a flat bed between the peaks is
what the feature implies anyway. Three contiguous pyroclastic tiles, inland, go to
hilliness 1. That is a direct one-off edit to the one map, which is the sanctioned method.
"""
import csv, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
STEM = os.path.join(REPO, "world", "ASHKARR_WORLDMAP")
NB_PATH = os.path.join(REPO, "world", "world_neighbors_sub7b.csv")
rows = list(csv.DictReader(open(STEM + "_tiles.csv", encoding="utf-8")))
T = {int(r["tile"]): r for r in rows}
nb = {}
rd = csv.reader(open(NB_PATH, encoding="utf-8")); next(rd)
for row in rd:
    nb[int(row[0])] = [int(x) for x in row[1:] if x.strip() and int(x) >= 0]
water = {t for t, r in T.items() if r["water"] == "1"}
cand = [t for t, r in T.items()
        if r["biome"] == "AB_PyroclasticConflagration"
        and not any(n in water for n in nb[t])]
if not cand:
    sys.exit("REFUSED: no inland pyroclastic tile to flatten")
cand.sort(key=lambda t: (-sum(1 for n in nb[t] if n in set(cand)), float(T[t]["elev_m"]), t))
seed = cand[0]
bed, frontier = [seed], [seed]
while len(bed) < 3 and frontier:
    nxt = []
    for x in frontier:
        for n in nb[x]:
            if n in cand and n not in bed and len(bed) < 3:
                bed.append(n); nxt.append(n)
    frontier = nxt
for t in bed:
    T[t]["hilliness"] = "1"
    print("  flattened tile %6d  %s  elev %s m -> hilliness 1"
          % (t, T[t]["biome"], T[t]["elev_m"]))
if "--apply" in sys.argv:
    with open(STEM + "_tiles.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("written: %d tiles flattened as the quagmire bed" % len(bed))
else:
    print("plan only - re-run with --apply")
