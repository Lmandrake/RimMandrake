import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
G={"BARE":(["Human36838","Human36841","Human36844"],[(137,129),(138,130),(139,131)],(140,130)),
   "HELM":(["Human36856","Human36859","Human36862"],[(145,129),(146,130),(147,131)],(147,132)),
   "SYM":(["Human36865","Human36868","Human36871"],[(153,129),(154,130),(155,131)],(155,128)),
   "ROOF":(["Human36847","Human36850","Human36853"],[(192,102),(193,102),(194,102)],(196,103))}
with RimBridge(host, port, token) as rb:
    for g,(ids,cells,door) in G.items():
        for pid in ids:
            rb.call("jawa/pawn_health",{"pawn":pid,"action":"remove","hediff":"RUT_SheenCoating"})
    for g,(ids,cells,door) in G.items():
        for pid,(x,z) in zip(ids,cells):
            r=rb.call("jawa/order_pawn",{"pawnId":pid,"x":x,"z":z,"draft":True,"waitTicks":1500,"unpause":True,"timeoutSeconds":90})
            row=(r.get("pawns") or [{}])[0]
            print(g,pid,"arrived",row.get("arrived"),"end",row.get("end"))
