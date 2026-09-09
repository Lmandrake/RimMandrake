import sys, os, csv, json
sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint

TILES_CSV = os.path.join("world", "ASHKARR_WORLDMAP_tiles.csv")
BACKUP_CSV = os.path.join("Transient", "desert_band_repair_backup_2026-09-09", "ASHKARR_WORLDMAP_tiles_PRE_REPAIR.csv")

backup = {r["tile"]: r["biome"] for r in csv.DictReader(open(BACKUP_CSV, encoding="utf-8"))}
all_tiles = list(backup.keys())

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    live = {}
    CHUNK = 200
    for i in range(0, len(all_tiles), CHUNK):
        chunk = all_tiles[i:i+CHUNK]
        r = rb.call("jawa/world_tile_get", {"tiles": ",".join(chunk)})
        assert r.get("success"), r
        assert not r.get("truncated"), r
        for t in r["tiles"]:
            live[str(t["tile"])] = t["biome"]
    print("live tiles read:", len(live), "of", len(all_tiles))

applied = json.load(open(os.path.join("Transient", "desert_band_repair_applied_tiles.json")))
expectedA = set(applied["bandA"])
expectedD = set(applied["bandD"])

changed = []
for tid in all_tiles:
    if backup[tid] != live.get(tid):
        changed.append((tid, backup[tid], live.get(tid)))

print("total changed tiles vs backup:", len(changed))
unexpected = [c for c in changed if c[0] not in expectedA and c[0] not in expectedD]
print("UNEXPECTED changes (should be 0):", len(unexpected))
for c in unexpected[:20]:
    print("  ", c)

# confirm all expectedA now ExtremeDesert, all expectedD now Wasteland
badA = [t for t in expectedA if live.get(t) != "ExtremeDesert"]
badD = [t for t in expectedD if live.get(t) != "Wasteland"]
print("bandA tiles NOT ExtremeDesert:", len(badA), badA[:10])
print("bandD tiles NOT Wasteland:", len(badD), badD[:10])
print("bandA total", len(expectedA), "bandD total", len(expectedD))
