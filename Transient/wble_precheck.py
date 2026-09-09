"""WORLD_BOUNDARY_LAND_AT_SEA_ELEVATION_1 - pre-fix safety check.
Checks mutators/objects/settlements on the 181 flagged tiles before any write.
Run: python.exe Transient/wble_precheck.py
"""
import sys, os, json

sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402

plan = json.load(open(os.path.join("Transient", "wble_fix_plan.json")))
all_tiles = plan["twilight"] + plan["grey"] + plan["damp"]

host, port, token = resolve_endpoint()
if not token:
    print("NO TOKEN")
    sys.exit(2)

with RimBridge(host, port, token) as rb:
    mut = rb.call("jawa/world_mutators_get", {"tiles": ",".join(str(t) for t in all_tiles), "limit": 300})
    json.dump(mut, open(os.path.join("Transient", "wble_precheck_mutators.json"), "w"), indent=2)
    nonempty = [r for r in mut.get("tiles", []) if r.get("mutators")]
    print("tiles with mutators:", len(nonempty))
    for r in nonempty:
        print(" ", r)

    obj = rb.call("jawa/world_objects_get", {"tiles": ",".join(str(t) for t in all_tiles), "limit": 300})
    json.dump(obj, open(os.path.join("Transient", "wble_precheck_objects.json"), "w"), indent=2)
    print("objects on flagged tiles:", obj.get("count"))

    # neighbor elevations for the 10 Damp tiles, to pick a sane re-elevation
    nbr_csv = os.path.join("world", "world_neighbors_sub7b.csv")
    import csv as csvmod
    nbr_of = {}
    with open(nbr_csv, encoding="utf-8") as f:
        for row in csvmod.DictReader(f):
            tid = int(row["tile"])
            nbr_of[tid] = [int(row[f"n{k}"]) for k in range(6) if int(row[f"n{k}"]) >= 0]

    damp_nbrs = set()
    for t in plan["damp"]:
        damp_nbrs.update(nbr_of.get(t, []))
    damp_nbrs -= set(plan["damp"])
    r2 = rb.call("jawa/world_tile_get", {"tiles": ",".join(str(x) for x in sorted(damp_nbrs))})
    json.dump(r2, open(os.path.join("Transient", "wble_precheck_damp_neighbors.json"), "w"), indent=2)
    land_elevs = [row["elevation"] for row in r2.get("tiles", []) if row.get("elevation", -9999) > 0]
    print("Damp cluster LAND neighbor elevations:", sorted(land_elevs))
    print("min land neighbor elevation:", min(land_elevs) if land_elevs else None)
