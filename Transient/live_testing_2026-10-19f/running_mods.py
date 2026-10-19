import json, os, sys
sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()
with RimBridge(h, p, t, timeout=120.0) as rb:
    r = rb.call("jawa/running_mods", {})
json.dump(r, open(sys.argv[1], "w"), indent=1)
ids = [ (m.get("packageId") if isinstance(m, dict) else m) for m in (r.get("mods") or r.get("running") or []) ]
print("running", len(ids))
