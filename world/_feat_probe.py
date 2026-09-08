import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    feats=rb.call("jawa/world_features_get", {"limit":300}).get("features",[])
    for f in feats:
        if f.get('name') in ('Level','Knuckles'):
            print(json.dumps(f))
