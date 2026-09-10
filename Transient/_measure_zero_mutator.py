import sys, csv, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

TILES_CSV = r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv"
tiles = []
with open(TILES_CSV) as f:
    r = csv.DictReader(f)
    for row in r:
        if row["biome"] == "PoisonForest":
            tiles.append(row["tile"])

print("PoisonForest tiles from CSV:", len(tiles))

host, port, token = resolve_endpoint()
zero = 0
nonzero = 0
missing = 0
with RimBridge(host, port, token) as rb:
    for i in range(0, len(tiles), 100):
        chunk = tiles[i:i+100]
        res = rb.call("jawa/world_mutators_get", {"tiles": ",".join(chunk), "limit": 100})
        got = {str(row["tile"]): row.get("mutators", []) for row in res.get("tiles", [])}
        for t in chunk:
            row = got.get(t)
            if row is None:
                missing += 1
                continue
            if len(row) == 0:
                zero += 1
            else:
                nonzero += 1

total = zero + nonzero + missing
print(f"total={total} zero={zero} nonzero={nonzero} missing_readback={missing}")
print(f"zero-mutator pct = {100.0*zero/total:.1f}%")
