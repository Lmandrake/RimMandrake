import sys, csv, random, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

CSV = r"D:\Luke\dev\Rimworld\Transient\BIOME_ENRICHMENT_POISON_FOREST_1_plan.csv"
rows = []
with open(CSV) as f:
    r = csv.DictReader(f)
    for row in r:
        rows.append((row["tile"], row["def"]))

random.seed(42)
sample = random.sample(rows, 12)

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    tiles_csv = ",".join(t for t, d in sample)
    res = rb.call("jawa/world_mutators_get", {"tiles": tiles_csv, "limit": 100})
    by_tile = {}
    for row in res.get("tiles", []):
        by_tile[str(row["tile"])] = [m["def"] for m in row.get("mutators", [])]
    print("INDEPENDENT SAMPLE CHECK (12 tiles):")
    ok = 0
    for t, d in sample:
        got = by_tile.get(t, [])
        present = d in got
        ok += present
        print(f"  tile={t} expect={d} present={present} full_mutators={got}")
    print(f"{ok}/{len(sample)} sample pairs confirmed present")
