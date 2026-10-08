import sys, json, os
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    for x in rb.list_tools():
        if x.get("name") in ("jawa/mod_settings_field","rimworld/get_mod_settings"):
            print(x["name"], json.dumps(x.get("inputSchema"))[:900], x.get("description","")[:500])
