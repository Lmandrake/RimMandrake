"""Planet-wide road audit for Ash'karr. Read-only."""
import json, csv, collections, math

R = "/mnt/d/Luke/dev/Rimworld/Transient"
links = json.load(open(R + "/links_raw.json"))
objs = json.load(open(R + "/objects_raw.json"))
lms = json.load(open(R + "/landmarks_raw.json"))
tiles = {int(r["tile"]): r for r in csv.DictReader(open("/mnt/d/Luke/dev/Rimworld/world/ASHKARR_WORLDMAP_tiles.csv"))}

by_tile = {r["tile"]: r for r in links}

# ---- build the road edge set ------------------------------------------------
edges = set()
defs = {}
for r in links:
    t = r["tile"]
    for pr in r.get("potentialRoads") or []:
        n = pr.get("neighbor", pr.get("neighbour", pr.get("tile")))
        d = pr.get("def") or pr.get("road")
        if n is None:
            continue
        e = (min(t, n), max(t, n))
        edges.add(e)
        defs[e] = d

adj = collections.defaultdict(set)
for a, b in edges:
    adj[a].add(b)
    adj[b].add(a)

print("=" * 74)
print("ROAD NETWORK, live: %d edges over %d tiles" % (len(edges), len(adj)))
print("road def histogram:", dict(collections.Counter(defs.values())))

# ---- components -------------------------------------------------------------
seen, comps = set(), []
for t in adj:
    if t in seen:
        continue
    stack, c = [t], []
    seen.add(t)
    while stack:
        x = stack.pop()
        c.append(x)
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    comps.append(c)
comps.sort(key=len, reverse=True)
print("\ncomponents: %d   sizes: %s%s" % (
    len(comps), [len(c) for c in comps[:12]], " ..." if len(comps) > 12 else ""))

# ---- what sits on a tile ----------------------------------------------------
settle = {o["tile"] for o in objs if o.get("isSettlement")}
anyobj = {o["tile"] for o in objs}
lmk = {l["tile"] for l in lms}
print("settlements: %d   all world objects: %d   landmarks: %d" % (len(settle), len(anyobj), len(lms)))

# ---- dead ends --------------------------------------------------------------
ends = [t for t in adj if len(adj[t]) == 1]
cat = collections.Counter()
orphan = []
for t in ends:
    if t in settle:
        cat["ends at a SETTLEMENT"] += 1
    elif t in anyobj:
        cat["ends at another world object"] += 1
    elif t in lmk:
        cat["ends at a LANDMARK"] += 1
    else:
        cat["ends at NOTHING"] += 1
        orphan.append(t)
print("\n" + "=" * 74)
print("DEAD ENDS (degree-1 road tiles): %d" % len(ends))
for k, v in cat.most_common():
    print("   %-32s %d" % (k, v))

# how long is each orphan stub, walking back to the first junction?
def stub_len(t):
    prev, cur, n = None, t, 0
    while True:
        n += 1
        nxt = [x for x in adj[cur] if x != prev]
        if len(nxt) != 1:
            return n, cur
        prev, cur = cur, nxt[0]

if orphan:
    lens = []
    for t in orphan:
        n, j = stub_len(t)
        lens.append((n, t, j))
    lens.sort(reverse=True)
    print("\n   orphan stubs by length (tiles from the dead end back to a junction):")
    hist = collections.Counter(n for n, _, _ in lens)
    print("   length histogram: %s" % dict(sorted(hist.items())))
    print("   longest 15: %s" % [(n, "tile %d" % t) for n, t, _ in lens[:15]])

# ---- roads that touch no settlement at all ----------------------------------
print("\n" + "=" * 74)
print("COMPONENTS THAT REACH NO SETTLEMENT:")
bad = [c for c in comps if not (set(c) & settle)]
print("   %d of %d components, %d tiles total" % (len(bad), len(comps), sum(len(c) for c in bad)))
for c in sorted(bad, key=len, reverse=True)[:10]:
    b = collections.Counter(tiles[t]["biome"] for t in c if t in tiles)
    rg = collections.Counter(tiles[t]["region"] for t in c if t in tiles)
    print("   %3d tiles  regions=%s  defs=%s" % (
        len(c), dict(rg.most_common(3)),
        dict(collections.Counter(defs[e] for e in edges if e[0] in set(c)).most_common(3))))

# ---- undrawable roads -------------------------------------------------------
hidden = [r for r in links if r.get("hiddenByBiome") and (r.get("potentialRoads"))]
noroad = [r for r in links if not r.get("allowRoads") and r.get("potentialRoads")]
print("\n" + "=" * 74)
print("ROADS THAT CANNOT BE DRAWN:")
print("   tiles with roads on allowRoads=false: %d" % len(noroad))
print("   by biome: %s" % dict(collections.Counter(r["biome"] for r in noroad)))
