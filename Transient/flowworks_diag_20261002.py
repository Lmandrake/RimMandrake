import json, sys
sys.path.insert(0, "src/RimMandrake/Utils")
import rimbridge_client as rb
h,p,t = rb.resolve_endpoint(); S = rb.RimBridge(host=h,port=p,token=t,timeout=600.0); S.connect()
def call(n, **q):
    r = S.call(n, q) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
cz = 115
for (x,z,w,hh) in ((3,cz+9,3,7),(9,cz+9,3,7)):
    r = call("jawa/flowworks_excavation_rect", x=x, z=z, w=w, h=hh, includeTerrain=True)
    print("RECT", x, z)
    for q in sorted(r["rows"], key=lambda q:(-q["z"],q["x"])): print("  ", q["x"], q["z"], "d", q["d"], "f", q["f"], "src", q.get("isSource"), q.get("terrain"))
print(json.dumps(call("jawa/flowworks_engine_state"))[:800])
