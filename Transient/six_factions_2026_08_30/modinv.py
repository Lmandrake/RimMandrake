import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for t in rb.list_tools():
        if t["name"]=="jawa/mod_inventory":
            print("SCHEMA", json.dumps((t.get("inputSchema") or {}).get("properties",{}))[:600])
    for q in ["raidprotectionfee","outposts"]:
        try:
            r=rb.call("jawa/mod_inventory", {"filter":q})
        except Exception as e:
            r=rb.call("jawa/mod_inventory", {})
        s=json.dumps(r, ensure_ascii=False)
        i=s.lower().find(q)
        print("==",q,"::", s[max(0,i-500):i+300] if i>=0 else s[:400])
