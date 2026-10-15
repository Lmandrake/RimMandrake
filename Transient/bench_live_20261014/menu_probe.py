import sys,json,time; sys.path.insert(0, r"D:\Luke\dev\_rmscratch\bench_live_20261014\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t=resolve_endpoint(); out={}
with RimBridge(h,p,t) as rb:
    out["qt"]=rb.call("rimworld/get_game_info",{})
    out["start"]=rb.call("jawa/safe_advance",{"action":"start","ticks":20000,"timeoutMs":0})
    time.sleep(1.5)
    out["mid"]=rb.call("jawa/safe_advance",{"action":"status"})
    out["menu"]=rb.call("rimworld/go_to_main_menu",{})
    time.sleep(4)
    out["status"]=rb.call("jawa/safe_advance",{"action":"status"})
json.dump(out,open("menu_probe.json","w"),indent=1,default=str)
print(json.dumps(out["status"],default=str)[:1500]); print(json.dumps(out["mid"],default=str)[:400])
