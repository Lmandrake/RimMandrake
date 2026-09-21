import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
IDS=["Human36859","Human36862","Human36844","Human36838"]
with RimBridge(host, port, token) as rb:
    ps={p["id"]:p for p in rb.call("jawa/list_pawns",{"faction":"player","includeHealth":True}).get("pawns",[])}
    for pid in IDS:
        p=ps.get(pid)
        if not p: print(pid,"GONE"); continue
        a=rb.call("jawa/pawn_get",{"pawn":pid})["pawns"][0]
        print(pid,"bioAge",a["ageBiologicalYears"],"dev",a["developmentalStage"],
              sorted((h["def"],round(h.get("severity") or 0,3)) for h in (p.get("health") or {}).get("hediffs",[])))
