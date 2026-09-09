import sys, json, csv
from collections import defaultdict

sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

CSV = r"D:\Luke\dev\Rimworld\Transient\BIOME_ENRICHMENT_POISON_FOREST_1_plan.csv"
OUTDIR = r"D:\Luke\dev\Rimworld\Transient"

by_def = defaultdict(list)
with open(CSV) as f:
    r = csv.DictReader(f)
    for row in r:
        by_def[row["def"]].append(row["tile"])

host, port, token = resolve_endpoint()
print("endpoint:", host, port)

with RimBridge(host, port, token) as rb:
    ui = rb.call("rimworld/get_ui_state", {})
    print("programState:", ui.get("programState"), "hasCurrentGame:", ui.get("hasCurrentGame"))

    before = rb.call("jawa/world_stats", {})
    print("world_stats before keys:", list(before.keys()))

    total_added = 0
    total_failed = []
    for defname, tiles in by_def.items():
        tiles_csv = ",".join(tiles)
        res = rb.call("jawa/world_mutators_set", {
            "action": "add",
            "mutators": defname,
            "tiles": tiles_csv,
            "readBack": 5,
        })
        added = res.get("added")
        print(defname, "tiles=%d" % len(tiles), "success=%s added=%s" % (res.get("success"), added))
        if not res.get("success"):
            total_failed.append((defname, res))
        else:
            total_added += (added if isinstance(added, int) else len(tiles))

    print("TOTAL rows attempted:", sum(len(v) for v in by_def.values()), "reported added:", total_added)
    if total_failed:
        print("FAILURES:", json.dumps(total_failed, indent=2)[:3000])

    commit = rb.call("jawa/world_commit", {})
    print("world_commit:", commit.get("success"))

    after = rb.call("jawa/world_stats", {})
    print("world_stats after captured")

    with open(OUTDIR + r"\world_stats_before.json", "w") as fo:
        json.dump(before, fo, indent=2)
    with open(OUTDIR + r"\world_stats_after.json", "w") as fo:
        json.dump(after, fo, indent=2)

    all_tiles = sorted(set(t for v in by_def.values() for t in v), key=int)
    readback = {}
    for i in range(0, len(all_tiles), 100):
        chunk = all_tiles[i:i+100]
        r2 = rb.call("jawa/world_mutators_get", {"tiles": ",".join(chunk), "limit": 100})
        for row in r2.get("tiles", []):
            readback[str(row["tile"])] = row
    with open(OUTDIR + r"\poison_forest_readback.json", "w") as fo:
        json.dump(readback, fo, indent=2)
    print("readback tiles captured:", len(readback))

    missing = []
    for defname, tiles in by_def.items():
        for t in tiles:
            row = readback.get(t)
            if row is None:
                missing.append((t, defname, "NO READBACK ROW"))
                continue
            got = [m["def"] for m in row.get("mutators", [])]
            if defname not in got:
                missing.append((t, defname, "not present; tile has: %s" % got))
    print("MISSING/DISPLACED pairs:", len(missing))
    for m in missing[:40]:
        print("  ", m)
    with open(OUTDIR + r"\poison_forest_missing.json", "w") as fo:
        json.dump(missing, fo, indent=2)
