import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch=rb.call("rimworld/list_debug_action_children", {"path":"Actions"})["children"]
    P=next(c["path"] for c in ch if c["path"].endswith("T: Grow plant to maturity"))
    print("path:",repr(P))
    r=rb.call("rimworld/execute_debug_action",{"path":P,"x":122,"z":124})
    print("grow:", json.dumps({k:v for k,v in r.items() if k!="operation"})[:250])
    ins=rb.call("jawa/inspect_string",{"defName":"RUT_PaleTree"})
    print("inspect:", json.dumps(ins.get("things"))[:600])
    print("moss:", rb.call("jawa/list_things",{"defName":"RUT_PaleMoss"}).get("message"))
