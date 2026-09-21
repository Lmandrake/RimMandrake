import sys, json, os, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
PAWNS=["Human125","Human128","Human122"]
seen={p:None for p in PAWNS}
for i in range(14):
    with RimBridge(host, port, token) as rb:
        ps={p["id"]:p for p in rb.call("jawa/list_pawns",{"faction":"player","includeHealth":True}).get("pawns",[])}
        t=len(rb.call("jawa/list_things",{"defName":"RUT_FalseFruit"}).get("things",[]))
        row={}
        for pid in PAWNS:
            h={x.get("def"):x.get("severity") for x in (ps[pid].get("health") or {}).get("hediffs",[])}
            row[pid]=h.get("RUT_MatGrip")
            if h.get("RUT_MatGrip") is not None: seen[pid]=h.get("RUT_MatGrip")
        tg=rb.call("rimworld/get_game_info",{}).get("ticksGame")
        print(i,"ticks",tg,"fruitLeft",t,"MatGrip",row, flush=True)
        if t==0 and all(v is not None for v in seen.values()): break
    time.sleep(2)
print("SEEN:", seen)
