import sys, json, csv
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
auth = {int(r['tile']): r for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv'))}
probe = {}
for name in ('Venom Wood','South Crags','Thornend'):
    probe[name] = [t for t,r in auth.items() if r['region']==name][:3]
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    f = rb.call("jawa/world_features_get", {"limit": 100})
    feats = f.get("features", [])
    k = feats[0].keys() if feats else []
    print("feature fields:", list(k))
    # map tile -> live feature if tiles are listed
    t2f = {}
    for ft in feats:
        for t in (ft.get("tiles") or []):
            t2f[t] = ft.get("name")
    for name, ts in probe.items():
        print(name, "->", [(t, t2f.get(t, "?")) for t in ts])
