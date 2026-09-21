import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch=rb.call("rimworld/list_debug_action_children", {"path":"Actions"})["children"]
    P=next(c["path"] for c in ch if c["path"].endswith("T: Grow plant to maturity"))
    for d in ["Plant_TreeAnima","RUT_PaleTree"]:
        for t in rb.call("jawa/list_things",{"defName":d}).get("things",[]):
            rb.call("rimworld/execute_debug_action",{"path":P,"x":t["x"],"z":t["z"]})
    for d in ["Plant_TreeAnima","RUT_PaleTree"]:
        for t in rb.call("jawa/inspect_string",{"defName":d}).get("things",[]):
            print(d, (t["x"],t["z"]), t.get("inspect"))
