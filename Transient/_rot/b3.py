import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/world_tile_set", {"tiles":"67860","biome":"RUT_TheRot"})
    print("set:", json.dumps(r)[:500])
    print("commit:", json.dumps(rb.call("jawa/world_commit", {}))[:300])
    mi = rb.call("jawa/map_info", {})
    print("mapBiome:", mi.get("mapBiome"), "outdoorTempNow:", mi.get("outdoorTempNow"), "tileBiome:", mi.get("tileInfo",{}).get("biome"))
