import sys, json, collections
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h,p,t = rb.resolve_endpoint(); S = rb.RimBridge(host=h,port=p,token=t,timeout=300.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
TILE=int(sys.argv[1]) if len(sys.argv)>1 else 49211
g = call("jawa/world_tile_map_generate", tile=TILE, layer="RM_SeabedLayer", biome="RM_SeabedFloor_GreySea")
g.pop("operation",None); g.pop("state",None); print("GEN", json.dumps(g)[:1500])
m = call("jawa/set_current_map", mapId=-987654); print("MAPS", json.dumps(m.get("details")))
