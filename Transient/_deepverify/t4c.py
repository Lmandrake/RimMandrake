import sys, json; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,T=resolve_endpoint(); b=RimBridge(token=T,timeout=120); b.connect()
for t in b.list_tools():
    if t.get("name") in ("jawa/mod_settings_field","jawa/type_probe","jawa/inspect_string"):
        print(t.get("name"), "|", str(t.get("description"))[:300], "|", json.dumps(t.get("inputSchema",{}).get("properties",{}))[:400])
