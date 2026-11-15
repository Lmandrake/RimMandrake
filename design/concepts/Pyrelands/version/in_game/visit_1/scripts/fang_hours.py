import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
cid = "Human85510"
with RimBridge(h,p,tk) as rb:
    r = rb.call("jawa/site_state", {})
    for q in r.get("pawns") or []:
        if "Flamefang" in q["id"]: rb.call("jawa/damage", {"damageDef":"Cut","amount":500.0,"thingId":q["id"]}); print("killed", q["id"])
    ser=[]
    for hr in range(7):
        g = rb.call("jawa/pawn_get", {"pawn":cid}); qq=(g.get("pawns") or [{}])[0]
        v=[hh.get("severity") for hh in qq.get("hediffs") or [] if "Venom" in str(hh)]
        ser.append(v[0] if v else None); print(hr, v, qq.get("dead"), [hh.get("def") or hh.get("defName") for hh in qq.get("hediffs") or []])
        rb.call("jawa/safe_advance", {"ticks":2500,"timeException":False})
    print("series", ser)
