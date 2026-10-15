import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t,timeout=120.0) as rb:
    c = lambda tool, **kw: rb.call(tool, kw)
    mi = c("jawa/map_info"); print("map", {k: mi.get(k) for k in ("tile","mapId","mapBiome")})
    r = c("jawa/set_current_map", mapId=-1); print("loadedMaps", (r.get("details") or {}).get("loadedMaps", r.get("loadedMaps")), "success", r.get("success"))
    g = c("jawa/static_call", type="RimMandrake.FlowWorks.Rivers.RM_RiverWorksProof", method="ProofGrid", args="-"); print("grid", str(g.get("result"))[:300])
    hp = c("jawa/list_pawns", faction="hostile", limit=200); print("hostiles", [x.get("id") for x in hp.get("pawns") or []])
