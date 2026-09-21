import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
ids=json.load(open("Transient/_rot/fresh.json"))
with RimBridge(host, port, token) as rb:
    rb.call("jawa/set_game_speed",{"speed":"Normal"})
for pid in ids:
    with RimBridge(host, port, token) as rb:
        p=rb.call("jawa/pawn_get",{"pawn":pid})["pawns"][0]["position"]
        t=rb.call("jawa/list_things",{"defName":"RUT_Tea_AgeReversal","rect":"%d,%d,3,3"%(p["x"]-1,p["z"]-1)}).get("things",[])
        if not t: print(pid,"no tea near",p); continue
        r=rb.call("jawa/ordered_job",{"pawnId":pid,"jobDef":"Ingest","targetAId":t[0]["id"],"waitTicks":30,"timeoutSeconds":15})
        print("cup1",pid,r.get("afterJobDef"),r.get("nowRunningRequested"))
