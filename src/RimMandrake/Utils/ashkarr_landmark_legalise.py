#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ashkarr_landmark_legalise.py - move landmarks onto ground their own mutators allow.

THE DEFECT. `ashkarr_landmarks.py` checked where a LANDMARK may go and never checked
where the TILE MUTATORS it drags along may go. Every LandmarkDef carries
`mutatorChances` marked `required: true`, and each of those mutators has its own
`biomeWhitelist`, `min/maxHilliness`, `coastSidesRange` and `canSpawnOnRiver`. Measured
2026-08-22 against the def dump: **276 of 497 landmarks sit on a tile where at least one
of their required mutators is illegal.**

It imports without complaint - `TileMutatorDef.IsValidTile` is not called on the direct-set
path the bridge uses - so the symptom is a mutator worker running on terrain nobody wrote
it for, which is exactly the silent class this project keeps getting caught by.

WHAT THIS DOES. For every landmark, tests all of its required mutators against the tile.
If any fails, walks outward to the nearest FREE tile where all of them pass, and moves the
landmark there. If no legal tile is within reach, the landmark is DROPPED and named - a
landmark that cannot legally exist is not a landmark.

    python3 src/RimMandrake/Utils/ashkarr_landmark_legalise.py            # plan only
    python3 src/RimMandrake/Utils/ashkarr_landmark_legalise.py --apply

⚠️ Run this BEFORE `ashkarr_engine_fit.py`, which refuses while any landmark would lose a
required mutator - correctly, because dropping the requirement would be resolving a design
conflict by deleting the evidence.
"""
import argparse
import collections
import csv
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WORLD = os.path.join(REPO, "world")
STEM = os.path.join(WORLD, "ASHKARR_WORLDMAP")
NEIGHBOURS = os.path.join(WORLD, "world_neighbors_sub7b.csv")
MEASURE = os.path.expanduser("~/.claude/skills/measuring-large-artifacts/scripts/measure/cli.py")

HILL = {"Undefined": None, "Flat": 1, "SmallHills": 2, "LargeHills": 3,
        "Mountainous": 4, "Impassable": 5}
SEARCH = 7          # hexes to walk looking for legal ground


def defs_of(dtype, keep):
    out = subprocess.run(["python3", MEASURE, "--rows", "500", "sql",
                          "SELECT def_name || '\t' || json FROM defs WHERE def_type='%s'" % dtype],
                         capture_output=True, text=True).stdout
    D = {}
    for line in out.split("\n"):
        if "\t{" not in line:
            continue
        try:
            f = json.loads(line[line.index("\t{") + 1:])["fields"]
        except Exception:
            continue
        D[f["defName"]] = {k: f.get(k) for k in keep}
    if not D:
        sys.exit("REFUSED: could not read %s from the def dump" % dtype)
    return D


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    MD = defs_of("TileMutatorDef", ["biomeWhitelist", "biomeBlacklist", "minHilliness",
                                    "maxHilliness", "coastSidesRange", "canSpawnOnRiver"])
    LD = defs_of("LandmarkDef", ["mutatorChances"])
    REQ = {k: [m["mutator"] for m in (v.get("mutatorChances") or []) if m.get("required")]
           for k, v in LD.items()}

    trows = list(csv.DictReader(open(STEM + "_tiles.csv", encoding="utf-8")))
    T = {int(r["tile"]): r for r in trows}
    nb = {}
    rd = csv.reader(open(NEIGHBOURS, encoding="utf-8"))
    next(rd)
    for row in rd:
        nb[int(row[0])] = [int(x) for x in row[1:] if x.strip() and int(x) >= 0]
    lrows = list(csv.DictReader(open(STEM + "_landmarks.csv", encoding="utf-8")))
    srows = list(csv.DictReader(open(STEM + "_settlements.csv", encoding="utf-8")))
    mrows = list(csv.DictReader(open(STEM + "_mutators.csv", encoding="utf-8")))
    MU = {int(r["tile"]): [x for x in re.split(r"[;|,]", r["mutators"]) if x.strip()]
          for r in mrows}
    links = list(csv.reader(open(STEM + "_links.csv", encoding="utf-8")))
    river_t = {int(x) for k, p, q, d in links[1:] if k == "river" for x in (p, q)}
    water = {t for t, r in T.items() if r["water"] == "1"}
    coast_n = {t: sum(1 for n in nb[t] if n in water) for t in T}
    s_tiles = {int(r["tile"]) for r in srows}
    occupied = {int(r["tile"]) for r in lrows} | s_tiles

    def legal(m, t):
        d = MD.get(m)
        if d is None:
            return True
        r = T[t]
        wl, bl = d.get("biomeWhitelist"), d.get("biomeBlacklist")
        if wl and r["biome"] not in wl:
            return False
        if bl and r["biome"] in bl:
            return False
        lo, hi = HILL.get(d.get("minHilliness")), HILL.get(d.get("maxHilliness"))
        h = int(r["hilliness"])
        if (lo is not None and h < lo) or (hi is not None and h > hi):
            return False
        cs = d.get("coastSidesRange") or {}
        cmin, cmax = cs.get("min", -1), cs.get("max", -1)
        if cmin >= 0 and not (cmin <= coast_n[t] <= cmax):
            return False
        if d.get("canSpawnOnRiver") is False and t in river_t:
            return False
        return True

    def ok_tile(lm, t):
        return (T[t]["water"] == "0" and all(legal(m, t) for m in REQ.get(lm, [])))

    bad = [(i, r) for i, r in enumerate(lrows) if not ok_tile(r["landmark"], int(r["tile"]))]
    print("%d of %d landmarks sit where a required mutator is illegal\n" % (len(bad), len(lrows)))
    why = collections.Counter(r["landmark"] for _, r in bad)
    for k, n in why.most_common(10):
        print("   %-28s %d" % (k, n))

    moved, droppedl, stayed = 0, [], 0
    for i, r in bad:
        src = int(r["tile"])
        lm = r["landmark"]
        found = None
        seen, frontier = {src}, [src]
        for _ in range(SEARCH):
            nxt = []
            for x in frontier:
                for n in nb[x]:
                    if n in seen:
                        continue
                    seen.add(n)
                    nxt.append(n)
                    if n not in occupied and ok_tile(lm, n):
                        found = n
                        break
                if found:
                    break
            if found:
                break
            frontier = nxt
        if found is None:
            droppedl.append((src, lm))
            continue
        occupied.discard(src)
        occupied.add(found)
        # carry the required mutators to the new tile, take them off the old one
        req = REQ.get(lm, [])
        MU[src] = [m for m in MU.get(src, []) if m not in req]
        MU.setdefault(found, [])
        for m in req:
            if m not in MU[found]:
                MU[found].append(m)
        r["tile"] = str(found)
        moved += 1

    lrows = [r for r in lrows if (int(r["tile"]), r["landmark"]) not in set(droppedl)]
    print("\nmoved %d landmarks onto legal ground; dropped %d that had none within %d hexes"
          % (moved, len(droppedl), SEARCH))
    if droppedl:
        c = collections.Counter(lm for _, lm in droppedl)
        for k, n in c.most_common(8):
            print("   dropped %-26s %d" % (k, n))
    left = [r for r in lrows if not ok_tile(r["landmark"], int(r["tile"]))]
    print("still illegal after the pass: %d" % len(left))
    print("landmarks %d -> %d" % (len(lrows) + len(droppedl), len(lrows)))

    if not a.apply:
        print("\nplan only - re-run with --apply")
        return
    with open(STEM + "_landmarks.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["tile", "landmark", "why"])
        w.writeheader()
        w.writerows(lrows)
    with open(STEM + "_mutators.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["tile", "mutators"])
        for t in sorted(MU):
            if MU[t]:
                w.writerow([t, ";".join(MU[t])])
    print("\nwritten: landmarks and mutators")


if __name__ == "__main__":
    main()
