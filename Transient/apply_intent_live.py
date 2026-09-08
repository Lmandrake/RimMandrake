"""Apply the three ruled biome changes to the LIVE WORLD, not to the CSV.

Doctrine, 2026-09-07: the savegame is the world; the CSV is a record exported
from it. So these land through the bridge and the CSV is re-exported afterwards.
Editing the CSV and importing it back is the exact failure we just undid.

Assignment sources are the same ones the offline scripts use, read directly so
that no CSV write path is involved:
  seas      (region, source-biome) selectors, per LIQUID_BIOMES_MAP_1
  nightside design/Jawa/worldbuilding/horrorwastes_dissolve_mosaic.json
  contagion design/Jawa/worldbuilding/contagion_tile_candidates.csv

Dry by default; --apply writes and commits.
"""
import sys, csv, json, os, collections

sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

REPO = r"D:\Luke\dev\Rimworld"
CANON = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv")
MOSAIC = os.path.join(REPO, "design", "Jawa", "worldbuilding", "horrorwastes_dissolve_mosaic.json")
CAND = os.path.join(REPO, "design", "Jawa", "worldbuilding", "contagion_tile_candidates.csv")

apply = "--apply" in sys.argv
rows = {int(r["tile"]): r for r in csv.DictReader(open(CANON))}

want = {}          # tile -> target biome
prov = {}          # tile -> which wave

# ---- 1. the three seas ------------------------------------------------------
SEAS = [("Scald", "Lake", "RUT_TheScald"),
        ("Twilight Sea", "Ocean", "RUT_TwilightSea"),
        ("Grey Sea", "Ocean", "RUT_GreySea")]
for region, src, dst in SEAS:
    for t, r in rows.items():
        if r["region"] == region and r["biome"] == src:
            want[t] = dst
            prov[t] = "seas"

# ---- 2. the nightside mosaic ------------------------------------------------
mos = json.load(open(MOSAIC))
if isinstance(mos, dict):
    items = mos.items()
else:
    items = [(m["tile"], m.get("target") or m.get("to") or m.get("biome")) for m in mos]
for t, dst in items:
    t = int(t)
    if rows[t]["biome"] != dst:
        want[t] = dst
        prov[t] = "nightside"

# ---- 3. the widened Contagion ----------------------------------------------
for r in csv.DictReader(open(CAND)):
    t = int(r["tile"])
    if rows[t]["biome"] != "AB_OcularForest":
        want[t] = "AB_OcularForest"
        prov[t] = "contagion"

by_target = collections.defaultdict(list)
for t, d in want.items():
    by_target[d].append(t)

print("PLAN — %d tiles across %d target biomes" % (len(want), len(by_target)))
for w in ("seas", "nightside", "contagion"):
    n = sum(1 for t in want if prov[t] == w)
    print("   %-10s %5d tiles" % (w, n))
print()
for d, ts in sorted(by_target.items(), key=lambda kv: -len(kv[1])):
    src = collections.Counter(rows[t]["biome"] for t in ts)
    print("   -> %-20s %5d tiles   from %s" % (d, len(ts), dict(src.most_common(4))))

if not apply:
    print("\nDRY RUN. --apply to write.")
    sys.exit(0)

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    # the live world must still be the one the canon was exported from
    v = rb.call("jawa/world_tile_validate", {"path": CANON, "limit": 5, "maxRows": 0})
    print("\npre-flight: live matches the canon CSV? matched=%s mismatched=%s"
          % (v.get("matched"), v.get("mismatched")))
    if v.get("mismatched"):
        print("REFUSED — the live world is not the world this CSV describes.")
        sys.exit(1)

    for d, ts in sorted(by_target.items(), key=lambda kv: -len(kv[1])):
        CH = 400
        okd = 0
        for i in range(0, len(ts), CH):
            chunk = ts[i:i + CH]
            r = rb.call("jawa/world_tile_set",
                        {"tiles": ",".join(str(x) for x in chunk), "biome": d, "readBack": 2})
            if r.get("success"):
                okd += len(chunk)
        print("SET %-20s %5d/%d  success" % (d, okd, len(ts)))

    c = rb.call("jawa/world_commit", {})
    print("COMMIT failedSteps=%s" % c.get("failedSteps"))
