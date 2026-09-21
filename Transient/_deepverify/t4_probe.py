import sys, json; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,T=resolve_endpoint(); b=RimBridge(token=T,timeout=120); b.connect()
b.call("jawa/set_current_map",{"mapId":4},check=False)
mi=b.call("jawa/map_info",{},check=False); print("map_info:", json.dumps({k:v for k,v in mi.items() if k!="operation"})[:600])
g1=b.call("rimworld/get_game_info",{},check=False)["ticksGame"]
r=b.call("rimworld/step_game_ticks",{"ticks":500},check=False)
g2=b.call("rimworld/get_game_info",{},check=False)["ticksGame"]
print("ticks advanced:", g2-g1, "effects:", json.dumps(r.get("effects"))[:300])
print([n for n in sorted(t.get("name") for t in b.list_tools().get("tools",[])) if any(k in n for k in ("component","glow","light","eval","reflect","field","invoke"))])
