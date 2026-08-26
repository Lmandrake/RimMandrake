"""dehump.py — take the uphill out of the rivers my meander pass put it into.

🔴 MY BUG, found by the owner at 22.72S 10.22W on 2026-08-25. meander.py costed a climb
at `max(0, dElev)/400`, so 516 m of ridge cost 1.29 against a curve penalty that was
often larger — and Dijkstra cheerfully routed a creek over the top. Measured after the
fact: 21 humps before the meander, 36 after. 22 are mine, 828 m of climb in total.

A HUMP is a degree-2 river tile strictly higher than BOTH its river neighbours: water
would have to flow up into it from both sides. This finds a replacement path between the
same two neighbours that never rises above the higher of them, and swaps it in.

⛔ It does NOT touch the 14 humps that pre-date the meander. Those are someone else's
call, and several sit on authored terrain.
"""
import csv, json, math, heapq, collections

W = "/mnt/d/Luke/dev/Rimworld/world/"
COLONY = 16869
tiles = {}
for r in csv.DictReader(open(W + "_verify/live_tiles.csv")):
    t = int(r["tile"])
    tiles[t] = dict(elev=float(r["elev_m"]), biome=r["biome"], hill=int(r["hilliness"] or 0),
                    arc=float(r["arc"]), water=int(r["water"] or 0), region=r["region"])
nb = {}
for row in csv.reader(open(W + "world_neighbors_sub7b.csv")):
    if row[0] == "tile": continue
    nb[int(row[0])] = [int(x) for x in row[1:] if int(x) >= 0]

RANK = {"Creek": 1, "River": 2, "LargeRiver": 3, "HugeRiver": 4}
adj = collections.defaultdict(set); defs = {}
for l in csv.DictReader(open(W + "_verify/live_links.csv")):
    if l["kind"] != "river": continue
    a, b = int(l["a"]), int(l["b"]); adj[a].add(b); adj[b].add(a)
    for x in (a, b): defs[x] = max(defs.get(x, ""), l["def"], key=lambda y: RANK.get(y, 0))

WATER = {"Ocean", "Lake", "SeaIce"}
blocked = {COLONY} | set(nb[COLONY])
for t, d in tiles.items():
    if d["hill"] >= 5 or d["arc"] > 80: blocked.add(t)

def route(a, b, cap, avoid):
    """Shortest a->b whose interior never rises above cap and never re-uses a river tile."""
    dist = {a: 0}; prev = {}; pq = [(0, a)]
    while pq:
        d0, cur = heapq.heappop(pq)
        if cur == b: break
        if d0 > dist.get(cur, 1e9): continue
        if d0 > 5: continue                      # keep the detour short
        for n in nb[cur]:
            if n == b:
                nd = d0 + 1
            else:
                if n in avoid or n in blocked: continue
                if tiles[n]["elev"] > cap: continue
                if tiles[n]["biome"] in WATER or tiles[n]["water"]: continue
                nd = d0 + 1
            if nd < dist.get(n, 1e9):
                dist[n] = nd; prev[n] = cur; heapq.heappush(pq, (nd, n))
    if b not in prev: return None
    p = [b]; cur = b
    while cur != a:
        cur = prev[cur]; p.append(cur)
    p.reverse(); return p

if __name__ == "__main__":
    mine = set(json.load(open(W + "_rivers/humps.json"))["created"])
    fixes, stuck = [], []
    river_tiles = set(adj)
    for t in sorted(mine, key=lambda x: -(tiles[x]["elev"])):
        if t not in adj or len(adj[t]) != 2: continue
        a, b = sorted(adj[t], key=lambda x: tiles[x]["elev"])   # a = lower = downstream
        cap = max(tiles[a]["elev"], tiles[b]["elev"])
        avoid = (river_tiles - {a, b, t}) | {t}
        p = route(a, b, cap, avoid)
        if not p:
            stuck.append((t, cap)); continue
        prof = [tiles[x]["elev"] for x in p]
        fixes.append({"hump": t, "a": a, "b": b, "path": p, "cap": cap,
                      "def": defs[t], "profile": prof})
        river_tiles |= set(p)
    print("humps of mine: %d   rerouted: %d   no route found: %d" % (len(mine), len(fixes), len(stuck)))
    for f in fixes:
        print("  drop %5d (%.0fm) -> %s" % (
            f["hump"], tiles[f["hump"]]["elev"],
            " ".join("%d(%.0f)" % (x, tiles[x]["elev"]) for x in f["path"])))
    for t, cap in stuck:
        print("  STUCK %5d %.0fm  cap %.0fm  %s" % (t, tiles[t]["elev"], cap, tiles[t]["region"]))
    json.dump(fixes, open(W + "_rivers/dehump_plan.json", "w"), indent=1)
