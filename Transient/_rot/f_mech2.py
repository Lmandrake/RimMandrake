import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
IDS=["Mech_Scyther37426","Mech_Scyther37427","Mech_Scyther37428","Muffalo37429","Muffalo37430","Muffalo37431"]
with RimBridge(host, port, token) as rb:
    ps={p["id"]:p for p in rb.call("jawa/list_pawns",{"includeHealth":True,"limit":500}).get("pawns",[])}
    for i in IDS:
        p=ps.get(i)
        if not p: print(i,"GONE"); continue
        hed={h.get("def"):h.get("severity") for h in (p.get("health") or {}).get("hediffs",[])}
        ci=rb.call("rimworld/get_cell_info",{"x":p["x"],"z":p["z"]})["cell"]
        print(i,"mech",p.get("isMechanoid"),"flesh",p.get("isFlesh"),(p["x"],p["z"]),"roof",ci.get("roofDefName"),"SporesBuildup",hed.get("RUT_SporesBuildup"),"SheenCoating",hed.get("RUT_SheenCoating"))
