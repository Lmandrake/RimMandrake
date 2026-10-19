import sys,json; sys.path.insert(0, r"src/RimMandrake/Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t=resolve_endpoint()
with RimBridge(h,p,t) as rb:
    for _ in range(80):
        for tn in ("VEF.Factions.Dialog_NewFactionSpawning","DubsMintMinimap.MainTabWindow_MiniMap"):
            try: r=rb.call("jawa/window_list_close",{"typeName":tn,"action":"close","closeAll":True}); print(tn, json.dumps(r)[:250])
            except Exception as ex: print(tn,"ERR",str(ex)[:200])
    r=rb.call("jawa/window_list_close",{}); print("FINAL",[w["type"] for w in r.get("windows",[])])
