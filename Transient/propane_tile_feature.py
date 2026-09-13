import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/world_tile_get", {"tiles": "215,22,78"})
    rows = r.get("tiles") or []
    if rows:
        print("fields:", list(rows[0].keys()))
        for row in rows: print({k: row[k] for k in row if k in ('tile','biome','feature','featureName','label')})
