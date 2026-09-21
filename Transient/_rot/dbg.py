import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r=rb.call("rimworld/list_debug_action_children", {"path":"Actions"})
    names=[c["path"].split("\\")[-1] for c in r.get("children",[])]
    print(len(names))
    for n in names:
        if any(k in n.lower() for k in ("fuel","fire","refuel","fill")): print(repr(n))
