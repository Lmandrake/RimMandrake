import sys, json; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,T=resolve_endpoint(); b=RimBridge(token=T,timeout=180); b.connect()
r=b.call("rimworld/go_to_main_menu",{},check=False); print("menu:", r.get("success"), str(r.get("message"))[:100])
