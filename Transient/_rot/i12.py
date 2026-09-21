import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
TARGETS=["Human42056","Human42059","Human36844"]
with RimBridge(host, port, token) as rb:
    alive={p["id"] for p in rb.call("jawa/list_pawns",{"faction":"player"}).get("pawns",[])}
    T=[t for t in TARGETS if t in alive]
    for pid in T:
        p=rb.call("jawa/pawn_get",{"pawn":pid})["pawns"][0]
        print("BEFORE cup2",pid,p["ageBiologicalYears"],p["position"])
        rb.call("jawa/spawn_batch",{"ops":"RUT_Tea_AgeReversal:%d,%d,1"%(p["position"]["x"],p["position"]["z"])})
        rb.call("jawa/set_draft",{"pawnId":pid,"drafted":False})
    rb.call("jawa/set_game_speed",{"speed":"Normal"})
    json.dump(T,open("Transient/_rot/t2.json","w"))
for pid in T:
    with RimBridge(host, port, token) as rb:
        p=rb.call("jawa/pawn_get",{"pawn":pid})["pawns"][0]["position"]
        th=rb.call("jawa/list_things",{"defName":"RUT_Tea_AgeReversal","rect":"%d,%d,3,3"%(p["x"]-1,p["z"]-1)}).get("things",[])
        if not th: print(pid,"no tea"); continue
        r=rb.call("jawa/ordered_job",{"pawnId":pid,"jobDef":"Ingest","targetAId":th[0]["id"],"waitTicks":30,"timeoutSeconds":15})
        print("cup2",pid,r.get("afterJobDef"),r.get("nowRunningRequested"))
