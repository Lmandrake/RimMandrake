import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h,p,t = rb.resolve_endpoint(); S = rb.RimBridge(host=h,port=p,token=t,timeout=120.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    if isinstance(r, dict): r.pop("operation",None); r.pop("state",None)
    return r
call("jawa/set_current_map", mapId=int(sys.argv[1]))
print(json.dumps(call("rimworld/get_cell_info", x=125, z=125))[:1200])
print(json.dumps(call("jawa/static_call", type="RimMandrake.DivingInteraction.RM_SeaFloorIdentity", method="SeaBiomeOf", args="current"))[:300])
