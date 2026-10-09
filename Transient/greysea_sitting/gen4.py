import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h,p,t = rb.resolve_endpoint(); S = rb.RimBridge(host=h,port=p,token=t,timeout=300.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    if isinstance(r, dict): r.pop("operation",None); r.pop("state",None)
    return r
T = int(sys.argv[1])
print("SURF", json.dumps(call("jawa/world_tile_set", tiles=str(T), biome="RM_GreySea"))[:400])
print("CACHE", json.dumps(call("jawa/world_tile_cache_reset", tiles=str(T)))[:300])
print("REASSERT", call("jawa/static_call", type="RimMandrake.DivingInteraction.RM_SeabedFloorLife", method="ReassertAll"))
g = call("jawa/world_tile_map_generate", tile=T, layer="RM_SeabedLayer", biome="RM_SeabedFloor_GreySea")
print("GEN", json.dumps(g)[:420])
call("jawa/set_current_map", mapId=g["mapId"])
print(call("jawa/static_call", type="RimMandrake.DivingInteraction.RM_SeaFloorIdentity", method="SeaBiomeOf", args="current"))
