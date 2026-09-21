import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for c in ["RUT_SporeCloud","RUT_SheenExposureLock"]:
        r=rb.call("jawa/game_condition",{"action":"end","condition":c})
        print("end",c,r.get("success"),json.dumps(r.get("activeConditions"))[:200])
    r=rb.call("jawa/spawn_pawn",{"kindDef":"Colonist","x":64,"z":120,"faction":"player","count":3})
    ids=[p.get("id") for p in (r.get("pawns") or [])]
    print("fresh:",ids)
    ps={p["id"]:p for p in rb.call("jawa/list_pawns",{"faction":"player"}).get("pawns",[])}
    for pid in ids:
        p=ps[pid]
        rb.call("jawa/spawn_batch",{"ops":"RUT_Tea_AgeReversal:%d,%d,1"%(p["x"],p["z"])})
        a=rb.call("jawa/pawn_get",{"pawn":pid})["pawns"][0]
        print("BEFORE",pid,a["ageBiologicalYears"],a["developmentalStage"],(p["x"],p["z"]))
    json.dump(ids,open("Transient/_rot/fresh.json","w"))
