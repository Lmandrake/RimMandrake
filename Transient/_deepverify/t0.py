import sys, json; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,T=resolve_endpoint(); print("token",T[:6])
b=RimBridge(token=T,timeout=60); b.connect()
g=b.call("rimworld/get_game_info",{},check=False); print(json.dumps(g)[:400])
tools=b.list_tools(); names=sorted(t.get("name") for t in (tools.get("tools") if isinstance(tools,dict) else tools))
print(len(names), "jawa:", sum(n.startswith("jawa/") for n in names))
print([n for n in names if any(k in n for k in ("draft","job","order","light","glow","map","portal","save"))])
