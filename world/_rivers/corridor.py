"""corridor.py — learn Ash'karr's OWN river-corridor rule, then find what broke.

⛔ Not a generator. It reads the corridors that are already right and reports the rule
they follow; the repair is applied only to tiles whose distance-to-river actually moved.
"""
import csv, json, math, collections, os

W = "/mnt/d/Luke/dev/Rimworld/world/"
LUSH = ("Jungle", "Forest", "Grassland", "Swamp", "Oasis", "Wood", "Mangrove")

tiles = {}
for r in csv.DictReader(open(W + "_final/live_tiles.csv")):
    t = int(r["tile"])
    tiles[t] = dict(tile=t, lat=float(r["lat"]), lon=float(r["lon"]), arc=float(r["arc"]),
                    biome=r["biome"], elev=float(r["elev_m"]), rain=float(r["rain_mm"]),
                    temp=float(r["temp_c"]), swamp=float(r["swampiness"]),
                    hill=int(r["hilliness"] or 0), region=r["region"],
                    water=int(r["water"] or 0))
nb = {}
for row in csv.reader(open(W + "world_neighbors_sub7b.csv")):
    if row[0] == "tile": continue
    nb[int(row[0])] = [int(x) for x in row[1:] if int(x) >= 0]

def rivers(path):
    """tile -> best river def on it, by size."""
    RANK = {"Creek": 1, "River": 2, "LargeRiver": 3, "HugeRiver": 4}
    out = {}
    for l in csv.DictReader(open(path)):
        if l["kind"] != "river": continue
        for t in (int(l["a"]), int(l["b"])):
            if RANK.get(l["def"], 0) > RANK.get(out.get(t, ""), 0):
                out[t] = l["def"]
    return out

def dist_map(riverset, maxd=4):
    d = {t: 0 for t in riverset}
    frontier = list(riverset)
    for k in range(1, maxd + 1):
        nxt = []
        for t in frontier:
            for n in nb[t]:
                if n not in d:
                    d[n] = k; nxt.append(n)
        frontier = nxt
        if not frontier: break
    return d

OLD = rivers(W + "_now/live_links.csv")
NEW = rivers(W + "_final/live_links.csv")
dold, dnew = dist_map(set(OLD)), dist_map(set(NEW))

def lush(b): return any(k in b for k in LUSH)

if __name__ == "__main__":
    print("river tiles: %d -> %d" % (len(OLD), len(NEW)))
    stable = [t for t in tiles if dold.get(t, 9) == dnew.get(t, 9)]
    print("tiles whose distance-to-river is UNCHANGED: %d" % len(stable))

    print("\n== THE RULE, learned from the %d unchanged tiles ==" % len(stable))
    print("dist  n      lush%   top biomes")
    for k in range(0, 4):
        g = [t for t in stable if dnew.get(t, 9) == k]
        if not g: continue
        b = collections.Counter(tiles[t]["biome"] for t in g)
        print("  %d  %5d  %5.1f%%   %s" % (
            k, len(g), 100 * sum(1 for t in g if lush(tiles[t]["biome"])) / len(g),
            ", ".join("%s %d%%" % (n, 100 * c / len(g)) for n, c in b.most_common(4))))
    g = [t for t in stable if dnew.get(t, 9) >= 4]
    b = collections.Counter(tiles[t]["biome"] for t in g)
    print("  4+ %5d  %5.1f%%   %s" % (len(g), 100*sum(1 for t in g if lush(tiles[t]["biome"]))/len(g),
                                      ", ".join("%s %d%%" % (n, 100*c//len(g)) for n, c in b.most_common(3))))

    print("\n== band width by river SIZE (unchanged corridors only) ==")
    for size in ("Creek", "River", "LargeRiver", "HugeRiver"):
        src = [t for t in NEW if NEW[t] == size and dold.get(t) == 0]
        if not src: continue
        d = dist_map(set(src), 3)
        line = []
        for k in range(0, 4):
            g = [t for t in d if d[t] == k and t in stable]
            if g:
                line.append("d%d %.0f%%" % (k, 100*sum(1 for t in g if lush(tiles[t]["biome"]))/len(g)))
        print("  %-11s (%4d tiles)  lush by distance: %s" % (size, len(src), "  ".join(line)))
