import sys, json; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,T=resolve_endpoint(); b=RimBridge(token=T,timeout=120); b.connect()
b.call("jawa/set_current_map",{"mapId":4},check=False)
mi=b.call("jawa/map_info",{},check=False); print("map_info:", json.dumps({k:v for k,v in mi.items() if k!="operation"})[:700])
names=sorted(t.get("name") for t in b.list_tools())
print([n for n in names if any(k in n for k in ("component","glow","light","eval","reflect","field","invoke","inspect","probe"))])
