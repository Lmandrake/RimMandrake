import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h,p,t = rb.resolve_endpoint(); S = rb.RimBridge(host=h,port=p,token=t,timeout=120.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
print(json.dumps(call("rimworld/get_game_info"))[:600])
L = call("jawa/world_layers"); print(json.dumps(L)[:1500])
m = call("jawa/set_current_map", mapId=-987654); print(json.dumps(m)[:800])
print(json.dumps(call("jawa/world_tile_map_generate", tile=0, layer="RM_SeabedLayer", biome="RM_SeabedFloor_GreySea", dryRun=True)))
