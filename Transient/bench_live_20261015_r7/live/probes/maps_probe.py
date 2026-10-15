import sys, os, json
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()
with RimBridge(h, p, t) as rb:
    r = rb.call("jawa/set_current_map", {"mapId": 99999})
    print("maps", json.dumps(r.get("loadedMaps") or r)[:1500])
    g = rb.call("jawa/static_call", {"type": "RimMandrake.FlowWorks.Rivers.RM_RiverWorksProof", "method": "ProofGrid", "args": "-"})
    print("grid now", g.get("result"))
    print("map", rb.call("jawa/map_info", {}).get("tile"))
