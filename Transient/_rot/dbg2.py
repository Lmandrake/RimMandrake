import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for root in ["Actions","Tools - General","Tools - Map","Tools - Pawns"]:
        try:
            r=rb.call("rimworld/list_debug_action_children", {"path":root})
        except Exception as e:
            print(root,"ERR",str(e)[:80]); continue
        for c in r.get("children",[]):
            n=c["path"].split("\\")[-1]
            if any(k in n.lower() for k in ("grow","plant","medit","psy","anima","subplant")): print(root,"|",repr(n))
