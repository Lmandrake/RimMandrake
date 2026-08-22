#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ashkarr_break_ring.py - take the compass out of the settlement pattern.

An independent fiction review, 2026-08-22, found the artefact `the_one_map.md` bans, in
the one field nobody renders: **six of the nine Deep Desert Tribes sit at arc exactly
78.6**, and two of those are mirrored latitude pairs - Redscarp +47.634 / The Dry Moot
-47.634, Ashfoot +70.718 / Knife Canyon -70.718. Three more rings behind it: four at
63.4, three Hutt holdings at 70.1, three at 99.4.

🔑 THE CAUSE IS THE GRID, NOT THE PLACER. Ash'karr's tiles are the dual of a subdivided
icosahedron, so the sphere is riddled with tiles that share an exact angular distance from
the substellar point by symmetry. Any placement rule that ranks candidates by a scalar
lands on them together. It is the same failure as the temperature bullseye: a real
structure in the substrate, faithfully reproduced, reading as machinery.

TWO CHANGES

  1 THE SAND PEOPLE GO IN THE SAND. The review's second finding: The Dune Sea is 1,692
    tiles - the planet's signature emptiness - and held no Deep Desert Tribes at all,
    though every spec puts them there. They are moved into it.
  2 NO MORE THAN TWO SETTLEMENTS SHARE A ROUNDED ARC, and no mirrored latitude pair
    survives. Anything over the cap is nudged to a nearby tile with a free arc.

⛔ Roads are NOT re-laid here. Run `ashkarr_engine_fit.py` afterwards; it owns road
connectivity and will route to wherever these end up.
"""
import csv, collections, os, sys

def _hops(a, b, nb, limit):
    if a == b: return True
    seen, frontier = {a}, [a]
    for _ in range(limit):
        nxt = []
        for x in frontier:
            for n in nb[x]:
                if n in seen: continue
                if n == b: return True
                seen.add(n); nxt.append(n)
        frontier = nxt
    return False
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
W = os.path.join(REPO, "world"); STEM = os.path.join(W, "ASHKARR_WORLDMAP")
APPLY = "--apply" in sys.argv
MAX_PER_ARC = 2
HIDE = {"AB_MechanoidIntrusion", "AB_PropaneLakes", "Ocean", "Lake", "IceSheet", "SeaIce"}

T = {int(r["tile"]): r for r in csv.DictReader(open(STEM + "_tiles.csv", encoding="utf-8"))}
nb = {}
rd = csv.reader(open(os.path.join(W, "world_neighbors_sub7b.csv"), encoding="utf-8")); next(rd)
for row in rd: nb[int(row[0])] = [int(x) for x in row[1:] if x.strip() and int(x) >= 0]
S = list(csv.DictReader(open(STEM + "_settlements.csv", encoding="utf-8")))
L = list(csv.DictReader(open(STEM + "_landmarks.csv", encoding="utf-8")))
occupied = {int(r["tile"]) for r in S} | {int(r["tile"]) for r in L}

def free(t):
    r = T[t]
    return (t not in occupied and r["water"] == "0" and r["biome"] not in HIDE
            and int(r["hilliness"]) < 5 and r["region"])

def place(s, t):
    occupied.discard(int(s["tile"])); occupied.add(t)
    s["tile"] = str(t); s["lat"] = T[t]["lat"]; s["lon"] = T[t]["lon"]
    s["arc"] = T[t]["arc"]; s["biome"] = T[t]["biome"]

# ── 1. the sand people into the sand ─────────────────────────────────────────
dune = [t for t in T if T[t]["region"] == "The Dune Sea" and free(t)
        and T[t]["biome"] in ("Desert", "ExtremeDesert", "ZBiome_Badlands")]
tribes = [s for s in S if s["faction"] == "Deep Desert Tribes"]
moved = 0
if dune and tribes:
    # farthest-first inside the Dune Sea so they do not clump
    chosen, used = [], []
    dist = {}
    q = collections.deque()
    for t in occupied:
        dist[t] = 0; q.append(t)
    while q:
        x = q.popleft()
        for n in nb[x]:
            if n not in dist: dist[n] = dist[x] + 1; q.append(n)
    pool = sorted(dune, key=lambda t: (-dist.get(t, 0), t))
    for s in tribes:
        pick = next((t for t in pool if t not in used and free(t)
                     and all(_hops(t, u, nb, 4) is False for u in used)), None)
        if pick is None: continue
        used.append(pick); place(s, pick); moved += 1
print("1 SAND PEOPLE     moved %d Deep Desert Tribes into The Dune Sea" % moved)

# ── 2. break the arc rings ───────────────────────────────────────────────────
def rings(S):
    c = collections.defaultdict(list)
    for s in S: c[round(float(s["arc"]), 1)].append(s)
    return c

nudged = 0
for _ in range(6):
    c = rings(S)
    over = [(a, g) for a, g in c.items() if len(g) > MAX_PER_ARC]
    if not over: break
    for arc, g in over:
        for s in g[MAX_PER_ARC:]:
            src = int(s["tile"])
            dest = None
            seen, frontier = {src}, [src]
            for _d in range(4):
                nxt = []
                for x in frontier:
                    for n in nb[x]:
                        if n in seen: continue
                        seen.add(n); nxt.append(n)
                        if free(n) and len(rings(S)[round(float(T[n]["arc"]), 1)]) < MAX_PER_ARC:
                            dest = n; break
                    if dest: break
                if dest: break
                frontier = nxt
            if dest: place(s, dest); nudged += 1
c = rings(S)
worst = max((len(g) for g in c.values()), default=0)
lat = collections.defaultdict(set)
for s in S: lat[round(abs(float(s["lat"])), 3)].add(round(float(s["lat"]), 3))
mirror = sum(1 for k, v in lat.items() if len(v) > 1)
print("2 ARC RINGS       nudged %d settlements; largest ring now %d; mirrored lat pairs %d"
      % (nudged, worst, mirror))

if APPLY:
    with open(STEM + "_settlements.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(S[0].keys())); w.writeheader(); w.writerows(S)
    print("\nwritten: settlements  (now run ashkarr_engine_fit.py to re-lay roads)")
else:
    print("\nplan only - re-run with --apply")
