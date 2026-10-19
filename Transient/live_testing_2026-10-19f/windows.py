import json, os, sys
sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()
with RimBridge(h, p, t, timeout=60.0) as rb:
    r = rb.call("jawa/window_list_close", {})
print([ (w.get("type"), w.get("forcePause")) for w in r.get("windows", [])])
