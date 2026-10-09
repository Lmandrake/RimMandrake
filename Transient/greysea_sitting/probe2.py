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
r = call("jawa/biome_probe", biomes="RM_SeabedFloor_GreySea,RM_GreySea")
r.pop("operation",None); r.pop("state",None)
open(r"Transient\greysea_sitting\biome_probe.json","w").write(json.dumps(r, indent=1))
print(json.dumps(r)[:3000])
