import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def health(rb,pid):
    for p in rb.call("jawa/list_pawns",{"faction":"player","includeHealth":True}).get("pawns",[]):
        if p["id"]==pid:
            return {"xz":(p["x"],p["z"]),"hediffs":sorted((h.get("def"),round(h.get("severity") or 0,4),h.get("part")) for h in (p.get("health") or {}).get("hediffs",[]))}
with RimBridge(host, port, token) as rb:
    for pid in ["Human125","Human128","Human122"]:
        print("AFTER",pid,json.dumps(health(rb,pid)))
    for d in ["RUT_AgelessCap","RUT_RegenerantVeil","RUT_FalseFruit","RUT_ChokingSpores","RUT_LiveIngredient_AgelessCap","RUT_LiveIngredient_RegenerantVeil","RawFungus"]:
        t=rb.call("jawa/list_things",{"defName":d,"limit":200})
        print(d, len(t.get("things",[])))
