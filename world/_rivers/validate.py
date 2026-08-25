"""Offline check of plan.json before a single write reaches the game."""
import json, csv, collections, sys
sys.path.insert(0, "/mnt/d/Luke/dev/Rimworld/world/_rivers")
from meander import tiles, nb, blocked, COLONY, river_edges, adj, arc, WATER

plan = json.load(open("/mnt/d/Luke/dev/Rimworld/world/_rivers/plan.json"))
bad = collections.Counter(); seen_new = collections.Counter()
for e in plan:
    o, n = e["old"], e["new"]
    if n[0] != o[0] or n[-1] != o[-1]: bad["endpoints moved"] += 1
    if len(set(n)) != len(n): bad["path visits a tile twice"] += 1
    for i in range(len(n) - 1):
        if n[i + 1] not in nb[n[i]]: bad["non-adjacent step"] += 1
    for t in n[1:-1]:
        if t in blocked:
            d = tiles[t]
            bad["interior tile blocked (%s arc%.0f hill%d)" % (d["biome"], d["arc"], d["hill"])] += 1
        seen_new[t] += 1
    # elevation: how much does the new path climb going downstream?
for t, c in seen_new.items():
    if c > 1: bad["tile used by two new paths"] += 1

print("plan entries:", len(plan))
if bad:
    for k, v in bad.most_common(): print("  DEFECT %-46s %d" % (k, v))
else:
    print("  ✅ all endpoints fixed, every step adjacent, no interior tile blocked,")
    print("     no tile reused within or across the new paths")

newt = set(seen_new) - {t for a, b, _ in river_edges for t in (a, b)}
print("\nnew river tiles: %d" % len(newt))
bio = collections.Counter(tiles[t]["biome"] for t in newt)
print("  biomes they cross:", dict(bio.most_common(6)))
print("  arc range: %.0f - %.0f (ceiling 80)" % (min(tiles[t]["arc"] for t in newt),
                                                 max(tiles[t]["arc"] for t in newt)))
print("  colony 16869 or its ring touched:", bool(newt & ({COLONY} | set(nb[COLONY]))))
