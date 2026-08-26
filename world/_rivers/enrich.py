"""enrich.py — give the river corridors something to find.

Owner, 2026-08-25: *"Mutators, landforms, features... go crazy and have fun with it!
Make them seem to make sense with local context."*

Measured before this ran: the CHANNEL carried 2.07 mutators/tile, but the banks were
nearly bare — d1 39% empty, d2 46%, d3 57%, against 70% for open desert 4+ tiles away.
A river corridor on a desert world should be the most interesting ground on the planet.

🔑 EVERY placement is keyed to something true about the tile — its role in the network
(headwater / gorge / confluence / mouth / terminus), its elevation relative to the
channel, its hilliness, its biome. Nothing is scattered at random, and no RNG is used:
where several options fit, the choice is a hash of the tile id, so the result is
reproducible and there is no seed anyone could turn to roll a different planet.

⚠️ Every gate is checked against the live roster before writing. AddMutator fires the
def's Worker and the generator's whitelist is NOT a guard on the setter, so an illegal
write lands and then misbehaves.
"""
import csv, json, collections

W = "/mnt/d/Luke/dev/Rimworld/world/"
COLONY = 16869
tiles = {}
for r in csv.DictReader(open(W + "_verify/live_tiles.csv")):
    t = int(r["tile"])
    tiles[t] = dict(biome=r["biome"], elev=float(r["elev_m"]), hill=int(r["hilliness"] or 0),
                    region=r["region"], temp=float(r["temp_c"]), arc=float(r["arc"]),
                    water=int(r["water"] or 0))
nb = {}
for row in csv.reader(open(W + "world_neighbors_sub7b.csv")):
    if row[0] == "tile": continue
    nb[int(row[0])] = [int(x) for x in row[1:] if int(x) >= 0]
mut = collections.defaultdict(list)
for r in csv.DictReader(open(W + "_verify/live_mutators.csv")):
    mut[int(r["tile"])] = [x for x in r["mutators"].split(";") if x]

RANK = {"Creek": 1, "River": 2, "LargeRiver": 3, "HugeRiver": 4}
adj = collections.defaultdict(set); defs = {}
for l in csv.DictReader(open(W + "_verify/live_links.csv")):
    if l["kind"] != "river": continue
    a, b = int(l["a"]), int(l["b"]); adj[a].add(b); adj[b].add(a)
    for x in (a, b): defs[x] = max(defs.get(x, ""), l["def"], key=lambda y: RANK.get(y, 0))
riv = set(adj)
dist = {t: 0 for t in riv}; parent = {t: t for t in riv}; fr = list(riv)
for k in (1, 2, 3):
    nx = []
    for t in fr:
        for n in nb[t]:
            if n not in dist:
                dist[n] = k; parent[n] = parent[t]; nx.append(n)
    fr = nx

WATER = {"Ocean", "Lake", "SeaIce"}
HILL = {"Flat": 1, "SmallHills": 2, "LargeHills": 3, "Mountainous": 4, "Impassable": 5}
# gates read off the live roster, only for what this script places
GATE = {
 "Fish_Increased":      dict(not_biome={"AB_MechanoidIntrusion"}),
 "AnimalLife_Increased":dict(),
 "AnimalHabitat":       dict(),
 "Caves":               dict(),
 "CaveLakes":           dict(),
 "RiverIsland":         dict(),
 "Mountain":            dict(),
 "Cliffs":              dict(minhill=4, biome={"AridShrubland","Desert","ExtremeDesert",
                                               "ZBiome_Badlands","BiomeCypreJungle"}),
 "VEE_SerpentineCanyons":dict(minhill=4),
 "VEE_FloodPlains":     dict(maxhill=2),
 "VEE_RelictDelta":     dict(biome={"Desert","ExtremeDesert","AridShrubland","ZBiome_Grasslands",
                                    "ZBiome_Badlands"}),
 "Marshy":              dict(maxhill=2, biome={"ZBiome_Grasslands","AB_FeraliskInfestedJungle",
                                    "BiomeCypreJungle","AB_MiasmicMangrove",
                                    "COMIGO_GreaterSwamp_Tropical"}),
 "AncientRuins":        dict(not_biome={"AB_MechanoidIntrusion"}),
 "VEE_DeepOreRich":     dict(),
}
def legal(t, m):
    g = GATE[m]; d = tiles[t]
    if t == COLONY or t in nb[COLONY]: return False
    if d["water"] or d["biome"] in WATER: return False
    if "biome" in g and d["biome"] not in g["biome"]: return False
    if d["biome"] in g.get("not_biome", ()): return False
    if "minhill" in g and d["hill"] < g["minhill"]: return False
    if "maxhill" in g and d["hill"] > g["maxhill"]: return False
    if m in mut[t]: return False
    return True

def pick(t, n):
    """deterministic choice — no seed, so no knob that could roll a second planet"""
    return (t * 2654435761) % n

def role(t):
    deg = len(adj[t]); e = tiles[t]["elev"]
    wet = any(tiles[n]["biome"] in WATER or tiles[n]["water"] for n in nb[t])
    if wet: return "mouth"
    if deg == 1 and all(tiles[n]["elev"] < e for n in adj[t]): return "headwater"
    if deg == 1: return "terminus"
    if deg >= 3: return "confluence"
    if tiles[t]["hill"] >= 4: return "gorge"
    if e < 50: return "lowland"
    return "reach"


def plan():
    add = collections.defaultdict(list)
    why = collections.Counter()
    def give(t, m, reason):
        if legal(t, m):
            add[m].append(t); mut[t].append(m); why[reason] += 1; return True
        return False

    # ---------- the channel itself -------------------------------------------
    for t in sorted(riv):
        r = role(t)
        # ⚠️ fish in EVERY reach read as mechanical, and a creek at 1500 m in a gorge
        # holds no fish. A real channel, or low ground where the water slows.
        if RANK.get(defs.get(t, ""), 0) >= 2 or tiles[t]["elev"] < 400:
            give(t, "Fish_Increased", "fish in the channel")
        if r == "headwater":
            # a spring emerging from rock: caves, and pools inside them
            give(t, "CaveLakes" if tiles[t]["hill"] >= 3 else "AnimalHabitat", "headwater spring")
            if tiles[t]["hill"] >= 4: give(t, "Caves", "headwater in rock")
        elif r == "gorge":
            give(t, "Cliffs" if pick(t, 2) else "VEE_SerpentineCanyons", "gorge reach")
            if pick(t, 4) == 0: give(t, "VEE_DeepOreRich", "the cut exposes ore")
        elif r == "confluence":
            give(t, "RiverIsland", "channel splits and rejoins")
        elif r == "lowland":
            give(t, "VEE_FloodPlains", "lowland reach floods")
        elif r == "terminus":
            give(t, "Marshy", "the river dies here")

    # ---------- the banks ----------------------------------------------------
    for t in sorted(dist):
        k = dist[t]
        if k == 0 or t in riv: continue
        src = parent[t]
        below = tiles[t]["elev"] <= tiles[src]["elev"]
        big = RANK.get(defs.get(src, ""), 0) >= 2
        if k == 1:
            # ground beside the water: animals come to drink; low ground floods
            if below and give(t, "VEE_FloodPlains", "floodplain beside the channel"): pass
            elif give(t, "Marshy", "wet bank"): pass
            # ⚠️ not EVERY bank tile. A corridor with no gaps reads as generated;
            # roughly half, chosen by tile id so the gaps are stable.
            elif pick(t, 2) == 0 and give(t, "AnimalLife_Increased", "animals gather at water"): pass
            if tiles[t]["hill"] >= 4: give(t, "Cliffs", "the bank is a bluff")
        elif k == 2:
            if big and pick(t, 3) == 0: give(t, "AnimalLife_Increased", "game trails to the river")
            elif tiles[t]["hill"] >= 3 and pick(t, 3) == 0: give(t, "Caves", "caves in the valley wall")
        elif k == 3:
            if pick(t, 5) == 0 and tiles[t]["hill"] >= 3: give(t, "Caves", "caves above the valley")

    # ---------- the courses the water left ------------------------------------
    old = set()
    for l in csv.DictReader(open(W + "_now/live_links.csv")):
        if l["kind"] == "river": old.update((int(l["a"]), int(l["b"])))
    for t in sorted(old - riv):
        give(t, "VEE_RelictDelta", "a fan the river abandoned")

    # ---------- people settled by the water ------------------------------------
    # a scavenger world: what is worth finding sits where people once lived
    cands = [t for t in sorted(dist) if dist[t] in (1, 2) and tiles[t]["hill"] <= 3]
    for t in cands:
        if pick(t, 14) == 0:
            give(t, "AncientRuins", "someone lived by the water once")
    return add, why


if __name__ == "__main__":
    add, why = plan()
    print("placements planned: %d across %d mutators\n" % (sum(len(v) for v in add.values()), len(add)))
    for m, ts in sorted(add.items(), key=lambda kv: -len(kv[1])):
        print("  %-24s %4d tiles" % (m, len(ts)))
    print("\nreasons:")
    for r, c in why.most_common(): print("  %-36s %d" % (r, c))
    json.dump({k: v for k, v in add.items()}, open(W + "_rivers/enrich_plan.json", "w"), indent=1)
