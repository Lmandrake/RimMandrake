import sys, os, json
sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/world_tile_set", {"tiles": "22,53,138", "biome": "RUT_BlueDesert", "readBack": 3})
    print(json.dumps(r, indent=2, default=str))
