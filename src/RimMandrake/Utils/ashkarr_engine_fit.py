#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ashkarr_engine_fit.py - make the bundle survive contact with RimWorld's own rules.

An independent mechanics review, 2026-08-22, read the 1.6 source rather than the docs
and found that the bundle is legal on paper and lossy in practice:

  * `Tile.AddMutator` REMOVES any existing mutator sharing a `categories` string when the
    incoming one has priority >=. Simulated over this bundle's own semicolon order, 267
    tiles silently lost 295 mutators - `Mountain <- Cliffs` 119 times - and 11 tiles threw
    a red "Detected mutator conflict". Nothing logs the 295. They just are not there.
  * `TileMutatorDef.IsValidTile` is NOT called on the direct-set path the bridge uses, so
    4,141 applications that violate their own def's biome whitelist, hilliness bounds,
    coast-sides range or canSpawnOnRiver import without complaint and then run workers on
    terrain nobody wrote them for.
  * `Tile.Roads` and `Tile.Rivers` are `allowRoads`/`allowRivers`-FILTERED views. Roads
    laid across `AB_PropaneLakes` and `AB_MechanoidIntrusion` exist in the data and are
    invisible in the game: the road graph is one component on paper and TWO after
    filtering, stranding four settlements with no road a player can see.

WHAT THIS DOES

  1 MUTATOR EVICTION   simulates AddMutator over each tile and writes back only the
                       survivors, so the CSV states what the engine will actually hold.
                       ⛔ REFUSES if a landmark's required mutator would be evicted -
                       that is a design conflict, not something to resolve silently.
  2 INVALID MUTATORS   drops applications that violate biomeWhitelist / biomeBlacklist /
                       min-maxHilliness / coastSidesRange / canSpawnOnRiver.
  3 LANDMARK BLOCKERS  drops a `preventsLandmarks` mutator from a tile that carries a
                       landmark which does not itself require it.
  4 VISIBLE ROADS      re-lays any road spur that crosses a biome hiding roads, routing
                       around it, so every settlement keeps a road the player can see.

    python3 src/RimMandrake/Utils/ashkarr_engine_fit.py            # plan only
    python3 src/RimMandrake/Utils/ashkarr_engine_fit.py --apply
"""
import argparse
import collections
import csv
import heapq
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

    MD = defs_of("TileMutatorDef", ["categories", "priority", "biomeWhitelist",
                                    "biomeBlacklist", "minHilliness", "maxHilliness",
                                    "coastSidesRange", "canSpawnOnRiver", "preventsLandmarks"])
    LD = defs_of("LandmarkDef", ["mutatorChances"])
    BD = defs_of("BiomeDef", ["allowRoads", "allowRivers"])
    REQ = {k: [m["mutator"] for m in (v.get("mutatorChances") or []) if m.get("required")]
           for k, v in LD.items()}
    NOROAD = {k for k, v in BD.items() if v.get("allowRoads") is False}

    trows = list(csv.DictReader(open(STEM + "_tiles.csv", encoding="utf-8")))
    T = {int(r["tile"]): r for r in trows}
    nb = {}
    rd = csv.reader(open(NEIGHBOURS, encoding="utf-8"))
    next(rd)
    for row in rd:
        nb[int(row[0])] = [int(x) for x in row[1:] if x.strip() and int(x) >= 0]
    mrows = list(csv.DictReader(open(STEM + "_mutators.csv", encoding="utf-8")))
    MU = {int(r["tile"]): [x for x in re.split(r"[;|,]", r["mutators"]) if x.strip()]
          for r in mrows}
    lrows = list(csv.DictReader(open(STEM + "_landmarks.csv", encoding="utf-8")))
    LMOF = {int(r["tile"]): r["landmark"] for r in lrows}
    srows = list(csv.DictReader(open(STEM + "_settlements.csv", encoding="utf-8")))
    links = list(csv.reader(open(STEM + "_links.csv", encoding="utf-8")))
    header, body = links[0], links[1:]

    water = {t for t, r in T.items() if r["water"] == "1"}
    river_t = {int(x) for k, p, q, d in body if k == "river" for x in (p, q)}
    coast_n = {t: sum(1 for n in nb[t] if n in water) for t in T}

    # ── 2. invalid applications (done first; no point keeping an illegal one) ──
    dropped_invalid = collections.Counter()
    for t, ms in MU.items():
        r = T[t]
        keep = []
        for m in ms:
            d = MD.get(m)
            if d is None:
                keep.append(m)
                continue
            wl, bl = d.get("biomeWhitelist"), d.get("biomeBlacklist")
            if wl and r["biome"] not in wl:
                dropped_invalid[m] += 1
                continue
            if bl and r["biome"] in bl:
                dropped_invalid[m] += 1
                continue
            lo, hi = HILL.get(d.get("minHilliness")), HILL.get(d.get("maxHilliness"))
            h = int(r["hilliness"])
            if (lo is not None and h < lo) or (hi is not None and h > hi):
                dropped_invalid[m] += 1
                continue
            cs = d.get("coastSidesRange") or {}
            cmin, cmax = cs.get("min", -1), cs.get("max", -1)
            if cmin >= 0 and not (cmin <= coast_n[t] <= cmax):
                dropped_invalid[m] += 1
                continue
            if d.get("canSpawnOnRiver") is False and t in river_t:
                dropped_invalid[m] += 1
                continue
            keep.append(m)
        MU[t] = keep
    print("2 INVALID MUTATORS  dropped %d applications that break their own def's rules"
          % sum(dropped_invalid.values()))
    for m, n in dropped_invalid.most_common(6):
        print("      %-28s %d" % (m, n))

    # ── 3. landmark blockers ──────────────────────────────────────────────────
    unblocked = 0
    for t, lm in LMOF.items():
        req = set(REQ.get(lm, []))
        keep = []
        for m in MU.get(t, []):
            if MD.get(m, {}).get("preventsLandmarks") and m not in req:
                unblocked += 1
                continue
            keep.append(m)
        if t in MU:
            MU[t] = keep
    print("3 LANDMARK BLOCKERS dropped %d preventsLandmarks mutators from landmark tiles"
          % unblocked)

    # ── 1. simulate AddMutator and keep only what the engine would keep ───────
    evicted = collections.Counter()
    conflicts = []
    for t, ms in MU.items():
        held = []                                  # (name, categories, priority)
        for m in ms:
            d = MD.get(m, {})
            cats = set(d.get("categories") or [])
            pri = d.get("priority") or 0
            if cats:
                survivors = []
                for (hm, hc, hp) in held:
                    if cats & hc:
                        if pri >= hp:
                            evicted[(hm, m)] += 1
                            continue           # engine removes the older one
                        conflicts.append((t, hm, m))
                    survivors.append((hm, hc, hp))
                held = survivors
            held.append((m, cats, pri))
        MU[t] = [h[0] for h in held]
    lost = sum(evicted.values())
    print("1 MUTATOR EVICTION  %d applications the engine would have silently deleted are "
          "now gone from the CSV too" % lost)
    for (a_, b_), n in evicted.most_common(5):
        print("      %-22s evicted by %-22s %d" % (a_, b_, n))
    if conflicts:
        print("      %d tiles would have thrown a red 'mutator conflict'; the lower-priority"
              " one is kept and the CSV now says so" % len(conflicts))

    # refuse if a landmark lost something it requires
    broken = []
    for t, lm in LMOF.items():
        miss = [m for m in REQ.get(lm, []) if m not in MU.get(t, [])]
        if miss:
            broken.append((t, lm, miss))
    if broken:
        for t, lm, miss in broken[:10]:
            print("   ! tile %d %s lost required %s" % (t, lm, miss))
        sys.exit("REFUSED: %d landmarks would lose a required mutator. That is a design "
                 "conflict between a landmark and the terrain under it, and it must be "
                 "resolved by moving the landmark, not by dropping the requirement."
                 % len(broken))

    # ── 4. roads a player can actually see ────────────────────────────────────
    def visible(t):
        return T[t]["biome"] not in NOROAD and T[t]["water"] == "0"

    road_rows = [r for r in body if r[0] == "road"]
    other = [r for r in body if r[0] != "road"]
    hidden = [r for r in road_rows if not visible(int(r[1])) or not visible(int(r[2]))]
    keepr = [r for r in road_rows if r not in hidden]
    g = collections.defaultdict(set)
    for _, p, q, _d in keepr:
        g[int(p)].add(int(q))
        g[int(q)].add(int(p))
    stiles = [int(r["tile"]) for r in srows]
    # the biggest surviving component is the trunk network
    seen, comps = set(), []
    for n in list(g):
        if n in seen:
            continue
        st, c = [n], set()
        while st:
            x = st.pop()
            if x in c:
                continue
            c.add(x)
            st.extend(g[x] - c)
        seen |= c
        comps.append(c)
    comps.sort(key=len, reverse=True)
    trunk = comps[0] if comps else set()
    stranded = [t for t in stiles if t not in trunk]
    print("4 VISIBLE ROADS     %d road links crossed a biome that hides them; %d settlements"
          " were left with no visible road" % (len(hidden), len(stranded)))

    added = 0
    have = {frozenset((int(p), int(q))) for _, p, q, _d in keepr}
    for t in stranded:
        if not visible(t):
            print("      ! settlement tile %d is itself in %s, which hides roads - it needs "
                  "moving, not rerouting" % (t, T[t]["biome"]))
            continue
        dist, prev, pq = {t: 0.0}, {t: None}, [(0.0, t)]
        hit = None
        while pq:
            d, x = heapq.heappop(pq)
            if x in trunk and x != t:
                hit = x
                break
            if d > dist.get(x, 1e18):
                continue
            for n in nb[x]:
                if not visible(n):
                    continue
                step = 1.0 + max(0.0, float(T[n]["elev_m"]) - float(T[x]["elev_m"])) / 200.0 \
                    + int(T[n]["hilliness"]) * 0.4
                if d + step < dist.get(n, 1e18):
                    dist[n] = d + step
                    prev[n] = x
                    heapq.heappush(pq, (d + step, n))
        if hit is None:
            print("      ! no visible route from settlement tile %d" % t)
            continue
        path, x = [], hit
        while x is not None:
            path.append(x)
            x = prev[x]
        for i in range(len(path) - 1):
            e = frozenset((path[i], path[i + 1]))
            if e in have:
                continue
            have.add(e)
            keepr.append(["road", str(path[i]), str(path[i + 1]), "DirtRoad"])
            added += 1
        trunk.update(path)
    print("      re-laid %d links around the hiding biomes" % added)
    body = other + keepr

    if not a.apply:
        print("\nplan only - re-run with --apply")
        return
    with open(STEM + "_mutators.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["tile", "mutators"])
        for t in sorted(MU):
            if MU[t]:
                w.writerow([t, ";".join(MU[t])])
    with open(STEM + "_links.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(body)
    print("\nwritten: mutators and links")


if __name__ == "__main__":
    main()
