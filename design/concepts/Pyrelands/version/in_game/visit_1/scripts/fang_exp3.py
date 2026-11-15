import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
cid = "Human85510"; x,z = 40,230
with RimBridge(h,p,tk) as rb:
    rb.call("jawa/damage", {"damageDef":"Cut","amount":500.0,"thingId":"RM_Flamefang85411"})
    f = rb.call("jawa/spawn_pawn", {"kindDef":"RM_Flamefang","x":x+1,"z":z,"faction":"none","count":1}); fid = f["pawns"][0]["id"]
    m = rb.call("jawa/pawn_mental", {"pawn":fid,"action":"start","state":"ManhunterPermanent"}); print("mental", m.get("started"), m.get("currentState"))
    def st():
        r = rb.call("jawa/site_state", {}); o={}
        for q in r.get("pawns") or []:
            if q["id"] in (cid,fid): o[q["id"][-5:]]=(q.get("x"),q.get("z"),q.get("job"))
        g = rb.call("jawa/pawn_get", {"pawn":cid}); qq=(g.get("pawns") or [{}])[0]
        o["hed"]=[(hh.get("def") or hh.get("defName"), round(hh.get("severity") or 0,3)) for hh in qq.get("hediffs") or [] if "Heatstroke" not in str(hh)]
        return o
    print(st())
    for i in range(12):
        rb.call("jawa/safe_advance", {"ticks":60,"timeException":False}); s=st(); print(i, s)
        if any("Venom" in str(a) for a in s["hed"]): break
