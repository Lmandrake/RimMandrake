import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r=rb.call("jawa/get_defs",{"defs":"JobDef/Psylink;JobDef/Meditate;JobDef/AnimaTreeLink;StatDef/MeditationPlantGrowthOffset","fields":"defName,label"})
    print([(x["requested"],x["found"]) for x in r.get("defs",[])])
    ch=rb.call("rimworld/list_debug_action_children", {"path":"Actions"})["children"]
    for c in ch:
        n=c["path"].split("\\")[-1]
        if any(k in n.lower() for k in ("grass","link","focus","subplant","tree")): print(repr(n))
    print("pawn MPGO:", json.dumps(rb.call("jawa/pawn_stats",{"pawn":"Human122","stats":"MeditationPlantGrowthOffset"}).get("stats"))[:300])
