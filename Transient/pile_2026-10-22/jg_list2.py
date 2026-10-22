import json, os, sys
sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()
with RimBridge(h, p, t) as B:
    r = B.call("jawa/list_things", {"rect": sys.argv[1], "limit": 500})
    for x in r.get("things") or []:
        if not sys.argv[2:] or any(k in (x.get("def") or "") for k in sys.argv[2:]):
            print(x.get("def"), x.get("x"), x.get("z"), x.get("rot"), x.get("label"))
