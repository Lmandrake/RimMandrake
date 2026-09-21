import sys, json, os, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def health(rb,pid):
    for p in rb.call("jawa/list_pawns",{"faction":"player","includeHealth":True}).get("pawns",[]):
        if p["id"]==pid:
            return {"xz":(p["x"],p["z"]),"hediffs":sorted((h.get("def"),round(h.get("severity") or 0,4)) for h in (p.get("health") or {}).get("hediffs",[]))}
    return None
PAIRS=[("Human125","RUT_AgelessCap37671",100,135),("Human128","RUT_FalseFruit37673",120,135),("Human122","RUT_RegenerantVeil37672",110,135)]
with RimBridge(host, port, token) as rb:
    for pid,_,_,_ in PAIRS: print("BEFORE",pid,json.dumps(health(rb,pid)))
    rb.call("jawa/set_game_speed",{"speed":"Normal"})
for pid,tid,x,z in PAIRS:
    with RimBridge(host, port, token) as rb:
        rb.call("jawa/set_draft",{"pawnId":pid,"drafted":False})
        r=rb.call("jawa/ordered_job",{"pawnId":pid,"jobDef":"Harvest","targetAId":tid,"waitTicks":30,"timeoutSeconds":15})
        print("job",pid,tid,json.dumps({k:v for k,v in r.items() if k!="operation"})[:300])
