import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("jawa/destroy_batch",{"rects":"123,123,4,4","categories":"All"})
    s=rb.call("jawa/spawn_batch",{"ops":"MeditationSpot:125,124,1"})
    print("spot:", s.get("message"))
    print("there:", [(t["id"],t["x"],t["z"]) for t in rb.call("jawa/list_things",{"defName":"MeditationSpot"}).get("things",[])])
    print("psylink:", json.dumps({k:v for k,v in rb.call("jawa/pawn_psychic",{"pawn":"Human122","action":"psylink","level":1}).items() if k!="operation"})[:300])
    print("psyfocus:", json.dumps({k:v for k,v in rb.call("jawa/pawn_psychic",{"pawn":"Human122","action":"psyfocus","psyfocus":0.0}).items() if k!="operation"})[:250])
    print("tt:", json.dumps({k:v for k,v in rb.call("jawa/timetable",{"pawnId":"Human122","hour":-1,"assignment":"Meditate"}).items() if k!="operation"})[:250])
    rb.call("jawa/set_draft",{"pawnId":"Human122","drafted":False})
    r=rb.call("jawa/order_pawn",{"pawnId":"Human122","x":126,"z":124,"draft":True,"waitTicks":900,"unpause":True,"undraftAfter":True,"timeoutSeconds":60})
    print("walk:", (r.get("pawns") or [{}])[0].get("end"))
