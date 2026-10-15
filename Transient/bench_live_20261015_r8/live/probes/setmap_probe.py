"""r8: what does jawa/set_current_map(mapId=-1) return? river_site.loaded_maps reads loadedMaps from its refusal."""
import sys, os, json
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()
with RimBridge(h, p, t) as rb:
    r = rb.call("jawa/set_current_map", {"mapId": -1})
    print(json.dumps(r, default=str)[:1500])
    print(json.dumps(rb.call("jawa/map_info", {}), default=str)[:300])
