import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
PID="Human36838"
with RimBridge(host, port, token) as rb:
    p=rb.call("jawa/pawn_get",{"pawn":PID})["pawns"][0]
    print("BEFORE 2nd cup: bioAge",p["ageBiologicalYears"],"pos",p["position"])
    x,z=p["position"]["x"],p["position"]["z"]
    rb.call("jawa/spawn_batch",{"ops":"RUT_Tea_AgeReversal:%d,%d,1"%(x,z)})
    tid=[t["id"] for t in rb.call("jawa/list_things",{"defName":"RUT_Tea_AgeReversal","rect":"%d,%d,1,1"%(x,z)}).get("things",[])][0]
    rb.call("jawa/set_draft",{"pawnId":PID,"drafted":False})
    rb.call("jawa/set_game_speed",{"speed":"Normal"})
with RimBridge(host, port, token) as rb:
    r=rb.call("jawa/ordered_job",{"pawnId":PID,"jobDef":"Ingest","targetAId":tid,"waitTicks":30,"timeoutSeconds":15})
    print("job",r.get("afterJobDef"),r.get("nowRunningRequested"))
