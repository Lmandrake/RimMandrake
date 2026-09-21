import sys, json, os, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("jawa/set_game_speed",{"speed":"Paused"})
    t1=rb.call("rimworld/get_game_info",{}).get("ticksGame")
time.sleep(3)
with RimBridge(host, port, token) as rb:
    s=rb.call("rimbridge/get_bridge_status",{}).get("state",{})
    t2=rb.call("rimworld/get_game_info",{}).get("ticksGame")
    print("paused",s.get("paused"),"speed",s.get("timeSpeed"),"ticks",t1,"->",t2,"(delta %d)"%(t2-t1))
    print("mapBiome", rb.call("jawa/map_info",{}).get("mapBiome"), "programState", s.get("programState"))
