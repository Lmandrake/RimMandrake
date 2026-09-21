import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ps=rb.call("jawa/list_pawns",{"faction":"player"}).get("pawns",[])
    print(len(ps), [(p["id"],p["name"],p["x"],p["z"],p.get("dead")) for p in ps])
    print(json.dumps({k:v for k,v in rb.call("jawa/pawn_get",{"pawn":ps[0]["id"]}).items() if k!="operation"})[:900])
