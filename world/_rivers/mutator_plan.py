"""mutator_plan.py — put the river-flavoured per-tile assignments where the rivers ARE.

Two jobs. First a CORRECTION: the meander moved channels and left the `River` mutator
behind on the old course while the new course carries none. Second an ENRICHMENT: the
planet has vanilla mutators that say what a river is DOING at a tile — Headwater,
RiverConfluence, RiverDelta — and almost none of them were in use.

⚠️ Every gate below is read from the live mutator roster, not guessed. A mutator whose
biome-lock the tile fails is NOT written: AddMutator fires the def's Worker, and the
generator's whitelist is not a guard on the setter, so an illegal write lands and then
misbehaves.

🔴 NOT RE-RUNNABLE SINCE 2026-08-27. This script's OLD-side input, `world/_now/`, was
deleted in a clean-up: a reference check grepped for the literal `world/_now/` and the
path here is built by concatenation (`W + "_now/..."`), so the match never fired. The
directory was untracked, so git cannot restore it and the planet has since moved on —
an export today returns the NEW state, not the OLD one.

⛔ Do NOT "fix" this by pointing OLD at `_organic/` or any other surviving bundle. They
are different exports from different days; substituting one would produce a DIFFERENT
diff while looking like this one.

✅ What survives and is still true: the plans this produced, `world/_rivers/*.json`
(2026-08-25), and the `_final/` bundle. The open item WORLD_MUTATOR_LANDMARK_IMPORTERS_1
depends only on `_final/`, which is intact.
"""
import sys, csv, collections, json
sys.path.insert(0, "/mnt/d/Luke/dev/Rimworld/world/_rivers")
from corridor import tiles, nb, NEW, OLD, dnew, dold, W

RANK = {"Creek": 1, "River": 2, "LargeRiver": 3, "HugeRiver": 4}
WATER = {"Ocean", "Lake", "SeaIce"}
COLONY = 16869

mut = {}
for r in csv.DictReader(open(W + "_now/live_mutators.csv")):
    mut[int(r["tile"])] = [x for x in r["mutators"].split(";") if x]

adj = collections.defaultdict(set)
for l in csv.DictReader(open(W + "_final/live_links.csv")):
    if l["kind"] == "river":
        a, b = int(l["a"]), int(l["b"]); adj[a].add(b); adj[b].add(a)

riv = set(NEW)
abandoned = set(OLD) - riv
forbidden = {COLONY} | set(nb[COLONY])
# biome gates, from the roster
DRYRIVER_OK = {"Desert", "ExtremeDesert", "AridShrubland", "ZBiome_Badlands", "Wasteland"}
MARSHY_OK = {"AB_FeraliskInfestedJungle", "ZBiome_Grasslands", "BiomeCypreJungle",
             "COMIGO_GreaterSwamp_Tropical"}

add = collections.defaultdict(list)     # defName -> [tiles]
rem = collections.defaultdict(list)

# ---- 1. the correction ------------------------------------------------------
for t in riv:
    if t in forbidden: continue
    if "River" not in mut.get(t, []): add["River"].append(t)
for t in tiles:
    if t in forbidden or t in riv: continue
    if "River" in mut.get(t, []): rem["River"].append(t)

# ---- 2. what the river is DOING here ---------------------------------------
for t in riv:
    if t in forbidden: continue
    have = mut.get(t, [])
    deg = len(adj[t])
    touches_water = any(tiles[n]["biome"] in WATER or tiles[n]["water"] for n in nb[t])
    if deg >= 3 and "RiverConfluence" not in have:
        add["RiverConfluence"].append(t)
    elif deg == 1 and not touches_water:
        # a single-ended reach that does not meet water: source if it is the high end
        up = next(iter(adj[t]), None)
        if up is not None and tiles[t]["elev"] > tiles[up]["elev"] and "Headwater" not in have:
            add["Headwater"].append(t)
    if touches_water and RANK.get(NEW[t], 0) >= 3 and "RiverDelta" not in have:
        add["RiverDelta"].append(t)

# ---- 3. the abandoned course becomes a dry bed ------------------------------
for t in abandoned:
    if t in forbidden: continue
    have = mut.get(t, [])
    if "VEE_StagnantRivulet" in have:
        rem["VEE_StagnantRivulet"].append(t)      # nothing flows here any more
    if tiles[t]["biome"] in DRYRIVER_OK and "VEE_DryRiver" not in have:
        add["VEE_DryRiver"].append(t)

# ---- 4. wet ground beside the water ----------------------------------------
for t in tiles:
    if t in forbidden or t in riv: continue
    if dnew.get(t, 9) != 1: continue
    if tiles[t]["biome"] not in MARSHY_OK: continue
    if "Marshy" in mut.get(t, []): continue
    # only where the ground actually sits low against the channel
    # ⚠️ Marsh beside a desert CREEK is a stretch, and a first cut tripled the planet's
    # marsh count. Require a real channel and ground that actually sits at or below it.
    low = [n for n in nb[t] if n in riv and RANK.get(NEW[n], 0) >= 2
           and tiles[t]["elev"] <= tiles[n]["elev"]]
    if low and tiles[t]["hill"] <= 1:
        add["Marshy"].append(t)

if __name__ == "__main__":
    print("river tiles %d   abandoned course %d" % (len(riv), len(abandoned)))
    print("\nADD:")
    for k, v in sorted(add.items(), key=lambda kv: -len(kv[1])):
        cur = sum(1 for t in tiles if k in mut.get(t, []))
        print("  %-22s %4d tiles   (planet currently holds %d)" % (k, len(v), cur))
    print("REMOVE:")
    for k, v in sorted(rem.items(), key=lambda kv: -len(kv[1])):
        print("  %-22s %4d tiles" % (k, len(v)))
    json.dump({"add": {k: v for k, v in add.items()}, "remove": {k: v for k, v in rem.items()}},
              open(W + "_rivers/mutator_plan.json", "w"), indent=1)
    print("\nwrote mutator_plan.json")
