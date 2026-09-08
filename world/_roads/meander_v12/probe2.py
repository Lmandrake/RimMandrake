import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/world_links_get", {"range": "0-40", "limit": 50})
    print(json.dumps(r, indent=1)[:2500])
    o = rb.call("jawa/world_objects_get", {"limit": 3})
    print("OBJ:", json.dumps(o, indent=1)[:1200])
    l = rb.call("jawa/world_landmarks_get", {"limit": 3})
    print("LM:", json.dumps(l, indent=1)[:900])
