"""corridor_plan.py — relay the biome corridor around the rivers that moved.

The rule is LEARNED from Ash'karr's own untouched corridors, never invented:
    d0 CypreJungle -> d1 FeraliskJungle -> d2 DesertOasis/AridShrubland
    -> d3 Grasslands/Badlands -> d4+ Desert,   the band widening with river size.

🔑 Owner, 2026-08-25: *"occasional violations of the rules I just gave you make it look
more natural anyway... not hard and fast math."* So the band is NOT applied as a clean
function of distance. It is modulated by the TERRAIN, which breaks it irregularly and
for a reason a reader can see: ground BELOW the river holds moisture and the green
reaches further; bluffs and steep hillside above it pinch the band off. No RNG is
involved — a seed would be a knob that could roll a different planet.
"""
import sys, csv, collections, json
sys.path.insert(0, "/mnt/d/Luke/dev/Rimworld/world/_rivers")
from corridor import tiles, nb, NEW, OLD, dold, dnew, lush, W

RANK = {"Creek": 1, "River": 2, "LargeRiver": 3, "HugeRiver": 4}

# the learned band, measured from unchanged corridors (corridor.py output)
BAND = {"Creek":      [0.70, 0.49, 0.39, 0.31],
        "River":      [0.89, 0.80, 0.56, 0.48],
        "LargeRiver": [0.91, 0.84, 0.71, 0.63],
        "HugeRiver":  [0.85, 0.73, 0.61, 0.50]}   # d0 raised: measured 0.74 is a gap, not a rule
# ⭐ ACCEPTABLE, not mandatory. Measured from the unchanged corridors: the biomes that
# together cover 85% of real tiles at that distance. A tile ALREADY inside its set is
# left alone — that is where most of the corridor's natural irregularity comes from, and
# forcing every tile to one biome per ring is exactly the manufactured look to avoid.
ACC = {0: {"BiomeCypreJungle", "AridShrubland", "AB_MiasmicMangrove", "Volcano", "Lake"},
       1: {"AB_FeraliskInfestedJungle", "AridShrubland", "Lake", "COMIGO_GreaterSwamp_Tropical",
           "ZBiome_Badlands", "ZBiome_Grasslands", "AB_MiasmicMangrove", "ZBiome_DesertOasis"},
       2: {"ZBiome_DesertOasis", "AridShrubland", "Lake", "ZBiome_Badlands",
           "AB_MiasmicMangrove", "ZBiome_Grasslands", "Ocean", "Wasteland"},
       3: {"ZBiome_Grasslands", "ZBiome_Badlands", "Desert", "Lake", "AridShrubland",
           "Ocean", "Wasteland"}}
WET = {0: "BiomeCypreJungle", 1: "AB_FeraliskInfestedJungle",
       2: "ZBiome_DesertOasis", 3: "ZBiome_Grasslands"}
DRY = {0: "AridShrubland", 1: "AridShrubland", 2: "ZBiome_Badlands", 3: "Desert"}
KEEP = {"Ocean", "Lake", "SeaIce", "Volcano", "LavaField", "AB_PyroclasticConflagration",
        "AB_MechanoidIntrusion", "Scarlands", "AB_TarPits", "AB_PropaneLakes",
        "BMT_CrystalCaverns", "BMT_FungalForest", "AB_GelatinousSuperorganism",
        "HorrorWastes", "Wasteland", "AB_OcularForest"}
COLONY = 16869                       # 🔴 the live colony and its ring are never touched

def nearest_river(t):
    """(river tile, its size) at the tile's own BFS distance."""
    d = dnew.get(t, 9)
    if d == 0: return t, NEW[t]
    seen, frontier = {t}, [t]
    for _ in range(d):
        nxt = []
        for x in frontier:
            for n in nb[x]:
                if n not in seen:
                    seen.add(n); nxt.append(n)
        frontier = nxt
    cands = [x for x in frontier if x in NEW]
    if not cands: return None, None
    best = max(cands, key=lambda x: RANK.get(NEW[x], 0))
    return best, NEW[best]

def plan():
    moved = [t for t in tiles if dold.get(t, 9) != dnew.get(t, 9)]
    forbidden = {COLONY} | set(nb[COLONY])
    out, reasons = [], collections.Counter()
    for t in sorted(moved):
        if t in forbidden:
            reasons["colony ring — never touched"] += 1; continue
        d = dnew.get(t, 9)
        cur = tiles[t]["biome"]
        if cur in KEEP:
            reasons["left alone: deliberate terrain"] += 1; continue
        if d >= 4:
            if lush(cur):
                out.append((t, cur, "Desert", 4, "stranded", 0.0))
                reasons["stranded green, dried back"] += 1
            else:
                reasons["already dry (far from water)"] += 1
            continue
        if cur in ACC[d]:
            reasons["already inside its tier's set"] += 1; continue
        r, size = nearest_river(t)
        if r is None:
            reasons["no river found"] += 1; continue
        base = BAND.get(size, BAND["Creek"])[d]
        # 🔑 the terrain modulation — what stops the band being a clean ring
        drop = tiles[t]["elev"] - tiles[r]["elev"]        # +ve: tile sits ABOVE the river
        wet = max(-0.38, min(0.38, -drop / 260.0))
        hill = 0.07 * tiles[t]["hill"]
        p = base + wet - hill
        want = WET[d] if p > 0.5 else DRY[d]
        if want == cur:
            reasons["already correct"] += 1; continue
        out.append((t, cur, want, d, "wet" if p > 0.5 else "dry", round(p, 2)))
        reasons["out of tier, retiered"] += 1
    return out, reasons


if __name__ == "__main__":
    p, reasons = plan()
    print("moved tiles considered: %d" % len([t for t in tiles if dold.get(t,9)!=dnew.get(t,9)]))
    for k, v in reasons.most_common(): print("  %-32s %d" % (k, v))
    print("\nbiome changes planned: %d" % len(p))
    by = collections.Counter("%s -> %s" % (a, b) for _, a, b, _, _, _ in p)
    for k, v in by.most_common(14): print("  %-56s %d" % (k, v))
    print("\nirregularity check — of the tiles at each distance, how many go AGAINST the plain rule:")
    for d in range(0, 4):
        g = [e for e in p if e[3] == d]
        if not g: continue
        base_wet = sum(1 for e in g if e[4] == "wet")
        print("  d%d: %3d changes, %3d wet / %3d dry" % (d, len(g), base_wet, len(g) - base_wet))
    json.dump([{"tile": t, "from": a, "to": b, "d": d, "mode": m, "p": pp}
               for t, a, b, d, m, pp in p], open(W + "_rivers/biome_plan.json", "w"), indent=1)
    print("\nwrote biome_plan.json")
