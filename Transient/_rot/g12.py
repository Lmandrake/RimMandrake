import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("jawa/pawn_gear",{"pawn":"Human122","action":"clear","clearWhat":"apparel"})
    r=rb.call("jawa/order_pawn",{"pawnId":"Human122","x":42,"z":40,"draft":True,"waitTicks":2500,"unpause":True,"undraftAfter":True,"timeoutSeconds":120})
    print("walk:", (r.get("pawns") or [{}])[0].get("arrived"), (r.get("pawns") or [{}])[0].get("end"))
with RimBridge(host, port, token) as rb:
    print("explain:", json.dumps(rb.call("jawa/stat_explain",{"subject":"Human122","stats":"MeditationPlantGrowthOffset"}).get("stats"))[:400])
