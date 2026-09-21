import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("jawa/set_draft",{"pawnId":"Human122","drafted":False})
    r=rb.call("jawa/order_pawn",{"pawnId":"Human122","x":124,"z":124,"draft":True,"waitTicks":600,"unpause":True,"undraftAfter":True,"timeoutSeconds":60})
    print("walk:", (r.get("pawns") or [{}])[0].get("end"))
    r=rb.call("jawa/ordered_job",{"pawnId":"Human122","jobDef":"Meditate","targetAX":124,"targetAZ":124,"targetBId":"RUT_PaleTree37489","waitTicks":300,"timeoutSeconds":40})
    print("job:", json.dumps({k:v for k,v in r.items() if k!="operation"})[:600])
