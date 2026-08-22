#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ashkarr_minerals.py - give Ash'karr an ore geography worth scavenging.

Owner, 2026-08-22: *"Did you place the old mineral mining site?"* It was already there -
`AncientQuarry` on tile 12411, "the mine the sandcrawlers were stolen from", one of the
original sixteen, and one of the ten whose required mutators were repaired earlier that
night. But it was the ONLY one, and `MineralRich` was on exactly **1 tile of 21,872**.

For a clan whose entire economy is digging up what is left, that is the map saying
nothing about the one question the clan actually asks: where is it worth digging?

WHAT THIS WRITES

  ORE PROVINCES   `MineralRich` in contiguous blobs, not a scatter. Ore comes in
                  provinces; a random sprinkle would read as noise and would make
                  prospecting meaningless. Provinces are seeded on high, broken
                  ground - crags, badlands, mountain - and two are ANCHORED on ground
                  the fiction already committed to: the old quarry, and the Geonosian
                  Foundry Hive's ore seams.
  DEEP ORE        `VEE_DeepOreRich` on the core of the richest provinces only.
  DEAD GROUND     `VEE_MineralDevoid` and `VEE_DeepOreDevoid` across the sand seas and
                  the salt. 🔑 This is the half that makes the other half mean
                  something - if nowhere is barren, "rich" is not information.
  OLD WORKINGS    more `AncientQuarry` landmarks, placed INSIDE ore provinces and near
                  a road, because that is where somebody would already have dug.

    python3 src/RimMandrake/Utils/ashkarr_minerals.py            # plan only
    python3 src/RimMandrake/Utils/ashkarr_minerals.py --apply

Deterministic - provinces grow from ranked seeds, no seed value and no randomness.
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

N_PROVINCES = 14
PROVINCE_SIZE = 34          # tiles per province
DEEP_CORE = 10              # of those, how many also get deep ore
N_QUARRIES = 9              # new AncientQuarry landmarks
QUARRY_MAX_HOPS = 6         # an old working somebody could still reach

# ground where a province may seed: broken, high, diggable
def is_ore_ground(d):
    return (d["water"] == 0 and d["hill"] >= 3
            and d["biome"] in ("AB_RockyCrags", "ZBiome_Badlands", "ExtremeDesert",
                               "Wasteland", "Scarlands", "BMT_CrystalCaverns",
                               "AB_PyroclasticConflagration", "Volcano"))


# ground with nothing in it: sand seas and salt pans
def is_dead_ground(d):
    return (d["water"] == 0 and d["hill"] <= 1
            and d["biome"] in ("Desert", "ExtremeDesert", "Wasteland", "AridShrubland"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    tiles = list(csv.DictReader(open(STEM + "_tiles.csv", encoding="utf-8")))
    T = {}
    for r in tiles:
        T[int(r["tile"])] = dict(
            elev=float(r["elev_m"]), water=int(r["water"]), biome=r["biome"],
            region=r["region"], hill=int(r["hilliness"]), arc=float(r["arc"]))
    nb = {}
    rd = csv.reader(open(NEIGHBOURS, encoding="utf-8"))
    next(rd)
    for row in rd:
        nb[int(row[0])] = [int(x) for x in row[1:] if x.strip() and int(x) >= 0]

    mrows = list(csv.DictReader(open(STEM + "_mutators.csv", encoding="utf-8")))
    MU = {int(r["tile"]): [x for x in re.split(r"[;|,]", r["mutators"]) if x.strip()]
          for r in mrows}
    lrows = list(csv.DictReader(open(STEM + "_landmarks.csv", encoding="utf-8")))
    lm_tiles = {int(r["tile"]) for r in lrows}
    srows = list(csv.DictReader(open(STEM + "_settlements.csv", encoding="utf-8")))
    s_tiles = {int(r["tile"]) for r in srows}
    links = list(csv.reader(open(STEM + "_links.csv", encoding="utf-8")))
    road = {int(x) for k, p, q, d in links[1:] if k == "road" for x in (p, q)}

    print("BEFORE: MineralRich on %d tiles, DeepOreRich on %d, MineralDevoid on %d, "
          "AncientQuarry landmarks %d"
          % (sum(1 for v in MU.values() if "MineralRich" in v),
             sum(1 for v in MU.values() if "VEE_DeepOreRich" in v),
             sum(1 for v in MU.values() if "VEE_MineralDevoid" in v),
             sum(1 for r in lrows if r["landmark"] == "AncientQuarry")))

    # ── anchors: ground the fiction already committed to ──────────────────────
    anchors = [int(r["tile"]) for r in lrows if r["landmark"] == "AncientQuarry"]
    anchors += [int(r["tile"]) for r in srows
                if r["faction"] == "Geonosian Foundry Hive" and "ore seams" in r["why"]]
    anchors = [t for t in anchors if is_ore_ground(T[t])
               or any(is_ore_ground(T[n]) for n in nb[t])]
    print("  anchored on %d committed sites (the old quarry, the Geonosian ore seams)"
          % len(anchors))

    # ── grow the provinces ────────────────────────────────────────────────────
    seeds = list(dict.fromkeys(anchors))
    pool = sorted((t for t, d in T.items() if is_ore_ground(d)),
                  key=lambda t: (-T[t]["hill"], -T[t]["elev"], t))
    claimed = set()
    for t in pool:
        if len(seeds) >= N_PROVINCES:
            break
        if t in claimed or any(_within(t, s, nb, 8) for s in seeds):
            continue
        seeds.append(t)

    provinces = []
    for s in seeds[:N_PROVINCES]:
        blob, frontier = {s}, [s]
        while len(blob) < PROVINCE_SIZE and frontier:
            nxt = []
            for x in frontier:
                for n in nb[x]:
                    if len(blob) >= PROVINCE_SIZE:
                        break
                    if n in blob or n in claimed or T[n]["water"] == 1:
                        continue
                    if not is_ore_ground(T[n]):
                        continue
                    blob.add(n)
                    nxt.append(n)
            frontier = nxt
        claimed |= blob
        provinces.append(sorted(blob, key=lambda t: (-T[t]["hill"], -T[t]["elev"], t)))

    rich = deep = 0
    for p in provinces:
        for i, t in enumerate(p):
            MU.setdefault(t, [])
            if "MineralRich" not in MU[t]:
                MU[t].append("MineralRich")
                rich += 1
            if i < DEEP_CORE and "VEE_DeepOreRich" not in MU[t]:
                MU[t].append("VEE_DeepOreRich")
                deep += 1
    print("  %d ore provinces: %d tiles MineralRich, %d of them DeepOreRich"
          % (len(provinces), rich, deep))

    # ── dead ground ───────────────────────────────────────────────────────────
    # every third qualifying flat tile, walked in tile order - dense enough to be the
    # rule out on the sand, sparse enough that it is not the whole planet.
    dead = 0
    for i, t in enumerate(sorted(t for t, d in T.items() if is_dead_ground(d))):
        if t in claimed or i % 3:
            continue
        MU.setdefault(t, [])
        if "VEE_MineralDevoid" not in MU[t]:
            MU[t].append("VEE_MineralDevoid")
            MU[t].append("VEE_DeepOreDevoid")
            dead += 1
    print("  %d tiles of dead ground (MineralDevoid + DeepOreDevoid)" % dead)

    # ── old workings ──────────────────────────────────────────────────────────
    LD = _landmark_reqs()
    dist = _hops_from(road | s_tiles, nb)
    cand = [t for p in provinces for t in p
            if t not in lm_tiles and t not in s_tiles
            and dist.get(t, 999) <= QUARRY_MAX_HOPS]
    cand.sort(key=lambda t: (dist.get(t, 999), -T[t]["hill"], t))
    new_lm, used = [], []
    for t in cand:
        if len(new_lm) >= N_QUARRIES:
            break
        # 🔑 2 hops against the EXISTING landmarks, not 4. At 492 landmarks on the map
        # a 4-hop guard leaves almost no tile eligible and this returned 0 quarries -
        # the same starvation that emptied the small-biome rules in ashkarr_landmarks.
        if any(_within(t, u, nb, 5) for u in used) or any(_within(t, u, nb, 2) for u in lm_tiles):
            continue
        used.append(t)
        lm_tiles.add(t)
        new_lm.append({"tile": str(t), "landmark": "AncientQuarry",
                       "why": "an old working in an ore province - somebody dug here first"})
        for m in LD.get("AncientQuarry", []):
            MU.setdefault(t, [])
            if m not in MU[t]:
                MU[t].append(m)
    print("  %d new AncientQuarry landmarks (all within %d hops of a road or town)"
          % (len(new_lm), QUARRY_MAX_HOPS))

    print("\nAFTER:  MineralRich %d, DeepOreRich %d, MineralDevoid %d, AncientQuarry %d"
          % (sum(1 for v in MU.values() if "MineralRich" in v),
             sum(1 for v in MU.values() if "VEE_DeepOreRich" in v),
             sum(1 for v in MU.values() if "VEE_MineralDevoid" in v),
             sum(1 for r in lrows if r["landmark"] == "AncientQuarry") + len(new_lm)))
    if not a.apply:
        print("plan only - re-run with --apply")
        return

    with open(STEM + "_mutators.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["tile", "mutators"])
        for t in sorted(MU):
            if MU[t]:
                w.writerow([t, ";".join(MU[t])])
    with open(STEM + "_landmarks.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["tile", "landmark", "why"])
        w.writeheader()
        w.writerows(lrows + new_lm)
    print("written: mutators and landmarks")


def _within(a, b, nb, limit):
    if a == b:
        return True
    seen, frontier = {a}, [a]
    for _ in range(limit):
        nxt = []
        for x in frontier:
            for n in nb[x]:
                if n in seen:
                    continue
                if n == b:
                    return True
                seen.add(n)
                nxt.append(n)
        frontier = nxt
    return False


def _hops_from(src, nb):
    dist = {t: 0 for t in src}
    q = collections.deque(src)
    while q:
        x = q.popleft()
        for n in nb[x]:
            if n not in dist:
                dist[n] = dist[x] + 1
                q.append(n)
    return dist


def _landmark_reqs():
    out = subprocess.run(["python3", MEASURE, "--rows", "200", "sql",
                          "SELECT def_name || '\t' || json FROM defs WHERE def_type='LandmarkDef'"],
                         capture_output=True, text=True).stdout
    LD = {}
    for line in out.split("\n"):
        if "\t{" not in line:
            continue
        try:
            d = json.loads(line[line.index("\t{") + 1:])
        except Exception:
            continue
        f = d["fields"]
        LD[f["defName"]] = [m["mutator"] for m in f.get("mutatorChances", []) if m.get("required")]
    if not LD:
        sys.exit("REFUSED: could not read LandmarkDefs from the def dump")
    return LD


if __name__ == "__main__":
    main()
