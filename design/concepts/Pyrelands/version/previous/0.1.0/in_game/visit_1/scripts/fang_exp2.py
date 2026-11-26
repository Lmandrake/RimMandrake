import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
x,z = 40,230
with RimBridge(h,p,tk) as rb:
    c = rb.call("jawa/spawn_pawn", {"kindDef":"Colonist","x":x,"z":z,"faction":"player","count":1}); cid = c["pawns"][0]["id"]
    d = rb.call("jawa/set_draft", {"pawnId":cid,"drafted":True}); print("draft", d.get("success"), str(d)[:200])
    f = rb.call("jawa/spawn_pawn", {"kindDef":"RM_Flamefang","x":x+1,"z":z,"faction":"none","count":1}); fid = f["pawns"][0]["id"]
    rb.call("jawa/pawn_mental", {"pawn":fid,"action":"start","state":"ManhunterPermanent"})
    def hed():
        r = rb.call("jawa/pawn_get", {"pawn":cid}); q=(r.get("pawns") or [{}])[0]
        return q.get("position"), [(hh.get("def") or hh.get("defName"), hh.get("severity"), hh.get("part")) for hh in q.get("hediffs") or []]
    got=False
    for i in range(24):
        rb.call("jawa/safe_advance", {"ticks":250,"timeException":False})
        pos,hs = hed(); print(i, pos, hs[:6])
        if any("Venom" in str(h0[0]) for h0 in hs): got=True; break
    rb.call("jawa/damage", {"damageDef":"Cut","amount":500.0,"thingId":fid})
    if got:
        for hr in range(7):
            pos,hs = hed(); print("hour", hr, [h0 for h0 in hs if "Venom" in str(h0[0])])
            rb.call("jawa/safe_advance", {"ticks":2500,"timeException":False})
    print("cid", cid)
