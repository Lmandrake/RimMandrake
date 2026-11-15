import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
x,z = 40,225
with RimBridge(h,p,tk) as rb:
    c = rb.call("jawa/spawn_pawn", {"kindDef":"Colonist","x":x,"z":z,"faction":"player","count":1})
    cid = c["pawns"][0]["id"]
    f = rb.call("jawa/spawn_pawn", {"kindDef":"RM_Flamefang","x":x+1,"z":z,"faction":"none","count":1})
    fid = f["pawns"][0]["id"]
    m = rb.call("jawa/pawn_mental", {"pawn":fid,"action":"start","state":"ManhunterPermanent"})
    print("mental", json.dumps(m)[:300])
    def st():
        r = rb.call("jawa/site_state", {})
        out = {}
        for q in r.get("pawns") or []:
            if q.get("id") in (cid,fid): out[q["id"][-6:]] = {k:q.get(k) for k in ("x","z","job","mentalState","downed","dead","mental")}
        return out
    print(st())
    for i in range(8):
        rb.call("jawa/safe_advance", {"ticks":250,"timeException":False})
        print(i, st())
    pg = rb.call("jawa/pawn_get", {"pawn":fid})
    print("fang", json.dumps(pg)[:1200])
