import sys, json, os, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    print("state:", json.dumps(rb.call("rimbridge/get_bridge_status",{}).get("state"))[:300])
    ps={p["id"]:p for p in rb.call("jawa/list_pawns",{"faction":"player"}).get("pawns",[])}
    print("Giggles at", (ps["Human122"]["x"], ps["Human122"]["z"]))
    rb.call("jawa/set_game_speed",{"speed":"Normal"})
with RimBridge(host, port, token) as rb:
    r=rb.call("jawa/ordered_job",{"pawnId":"Human122","jobDef":"Meditate","targetAX":124,"targetAZ":124,"targetBId":"RUT_PaleTree37489","waitTicks":120,"timeoutSeconds":20})
    print("job:", json.dumps({k:v for k,v in r.items() if k!="operation"})[:700])
