"""Close the two vanilla-biome survivors on Ash'karr (owner rulings, 2026-09-07).

1. 262 SeaIce tiles -> their parent sea. They sit INSIDE the Twilight Sea (171)
   and Grey Sea (91) regions and were skipped only because ashkarr_three_seas.py
   selected on (region, biome) pairs and their source biome was SeaIce, not Ocean.
   Elevation is already -350 and is NOT touched.

2. 10 vanilla Lake tiles -> dry land, keeping their existing lake MUTATORS.
   They already carry ToxicLake / VEE_SulfuricLake / AB_TarLakes, so the lake
   survives as a map feature while the world tile stops being a black hole.
   Biome by land-neighbour majority (water excluded); elevation set to the
   lowest land neighbour minus 10 m, floored at 1 m, so the tile stays a basin.

Mutators are never written here. Verified 2026-09-07 that TileMutatorDef's
biomeWhitelist/biomeBlacklist are consulted ONLY by IsValidTile during the
worldgen roll -- MapGenerator iterates map.TileInfo.Mutators with no biome
re-check -- so changing the biome under a placed mutator is safe.

Run with no args to PLAN. Run with --apply to write.
"""
import sys, csv, json, collections

sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

TILES_CSV = r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv"
NEIGHBOURS = r"D:\Luke\dev\Rimworld\Transient\neighbors.json"
SNAPSHOT = r"D:\Luke\dev\Rimworld\Transient\wm_fix_before_snapshot.json"

WATER_BIOMES = {"Ocean", "Lake", "SeaIce", "IceSheet",
                "RUT_TheScald", "RUT_GreySea", "RUT_TwilightSea", "RUT_PropaneLake"}
SEA_FOR_REGION = {"Twilight Sea": "RUT_TwilightSea", "Grey Sea": "RUT_GreySea"}

# Read live 2026-09-07 off jawa/world_mutators_get. Recorded here so the plan can
# SHOW what each cluster keeps; this script never writes mutators.
LAKE_MUTATORS = {
    957: ["ToxicLake"],
    1446: ["VEE_SaltPlains", "AB_TarLakes"],
    4161: ["DryGround", "VEE_SulfuricLake"],
    4924: ["DryGround", "VEE_SulfuricLake"],
    9784: ["AB_TarLakes"],
    12269: ["DryGround", "ToxicLake"],
    12271: ["VEE_SulfuricLake"],
    13026: ["VEE_SaltPlains", "AB_TarLakes"],
    13027: ["DryGround", "AB_TarLakes"],
    16042: ["DryGround", "ToxicLake"],
}

apply = "--apply" in sys.argv

rows = {int(r["tile"]): r for r in csv.DictReader(open(TILES_CSV))}
nbr = {}
for r in csv.DictReader(open(NEIGHBOURS)):
    nbr[int(r["tile"])] = [int(r["n%d" % i]) for i in range(6) if int(r["n%d" % i]) >= 0]

# ---- part 1: SeaIce -> parent sea -------------------------------------------
seaice = [t for t, r in rows.items() if r["biome"] == "SeaIce"]
sea_plan = collections.defaultdict(list)
sea_unmapped = []
for t in seaice:
    reg = rows[t]["region"]
    if reg in SEA_FOR_REGION:
        sea_plan[SEA_FOR_REGION[reg]].append(t)
    else:
        sea_unmapped.append((t, reg))

print("== PART 1: SeaIce -> parent sea ==")
for b, ts in sorted(sea_plan.items()):
    print("  %-18s %3d tiles   (elevation untouched, already -350)" % (b, len(ts)))
if sea_unmapped:
    print("  !! %d SeaIce tiles in an UNMAPPED region -- NOT touched: %s"
          % (len(sea_unmapped), sea_unmapped[:10]))
print("  total: %d of %d SeaIce tiles covered" % (sum(len(v) for v in sea_plan.values()), len(seaice)))

# ---- part 2: Lake -> dry land -----------------------------------------------
lakes = sorted(t for t, r in rows.items() if r["biome"] == "Lake")

# A lake bed is one landform, not N independent tiles: cluster the Lake tiles by
# adjacency and give each cluster ONE biome and ONE elevation, decided by the
# pooled land-neighbour vote of the whole cluster. Per-tile voting scattered
# three biomes across five tiles and left a 117 m lump inside one basin.
lakeset = set(lakes)
clusters, seen = [], set()
for t in lakes:
    if t in seen:
        continue
    stack, comp = [t], []
    seen.add(t)
    while stack:
        c = stack.pop()
        comp.append(c)
        for n in nbr[c]:
            if n in lakeset and n not in seen:
                seen.add(n)
                stack.append(n)
    clusters.append(sorted(comp))
clusters.sort(key=lambda c: -len(c))

print("\n== PART 2: Lake -> dry land (mutators kept), %d cluster(s) ==" % len(clusters))
lake_plan = {}
for comp in clusters:
    land = {i for t in comp for i in nbr[t] if i not in lakeset
            and rows[i]["biome"] not in WATER_BIOMES}
    vote = collections.Counter(rows[i]["biome"] for i in land)
    if not vote:
        print("  cluster %s: NO LAND NEIGHBOUR -- SKIPPED" % comp)
        continue
    top = vote.most_common()
    best = sorted([b for b, c in top if c == top[0][1]])[0]
    lo = min(float(rows[i]["elev_m"]) for i in land)
    elev = max(1.0, round(lo - 10.0))
    muts = sorted({m for t in comp for m in LAKE_MUTATORS.get(t, [])})
    print("  cluster of %d: %s" % (len(comp), comp))
    print("     -> biome %-18s  elev %.0f m (flat; lowest land neighbour %.0f)" % (best, elev, lo))
    print("     was elev %s" % [rows[t]["elev_m"] for t in comp])
    print("     pooled vote: %s" % ", ".join("%s x%d" % (b, c) for b, c in top))
    print("     mutators kept: %s" % (", ".join(muts) or "(none recorded)"))
    for t in comp:
        lake_plan[t] = (best, elev)

if not apply:
    print("\nPLAN ONLY. Re-run with --apply to write.")
    sys.exit(0)

# ---- apply -------------------------------------------------------------------
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    touched = sorted(set(seaice) | set(lake_plan))
    before = {}
    for t in touched:
        g = rb.call("jawa/world_tile_get", {"tiles": str(t)})
        before[t] = (g.get("tiles") or g.get("rows") or [None])[0]
    json.dump(before, open(SNAPSHOT, "w"), indent=1)
    print("\nBEFORE snapshot of %d tiles -> %s" % (len(before), SNAPSHOT))

    for b, ts in sorted(sea_plan.items()):
        r = rb.call("jawa/world_tile_set",
                    {"tiles": ",".join(str(x) for x in ts), "biome": b, "readBack": 3})
        print("SET %-18s %3d -> success=%s changed=%s"
              % (b, len(ts), r.get("success"), r.get("changed") or r.get("updated")))

    by_biome = collections.defaultdict(list)
    for t, (b, e) in lake_plan.items():
        by_biome[b].append(t)
    for b, ts in sorted(by_biome.items()):
        r = rb.call("jawa/world_tile_set",
                    {"tiles": ",".join(str(x) for x in ts), "biome": b, "readBack": 3})
        print("SET %-18s %3d -> success=%s" % (b, len(ts), r.get("success")))
    for t, (b, e) in sorted(lake_plan.items()):
        r = rb.call("jawa/world_tile_set", {"tiles": str(t), "elevation": e, "readBack": 1})
        print("SET elev tile %-6d -> %5.0f m  success=%s" % (t, e, r.get("success")))

    c = rb.call("jawa/world_commit", {})
    print("COMMIT ->", json.dumps({k: v for k, v in c.items() if k != "operation"})[:300])
