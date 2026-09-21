import sys; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,T=resolve_endpoint(); b=RimBridge(token=T,timeout=60); b.connect()
print([t["name"] for t in b.list_tools() if any(k in t["name"] for k in ("quit","exit","shutdown","close_game","main_menu"))])
