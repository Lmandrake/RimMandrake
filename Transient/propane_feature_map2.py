import sys, json, csv
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
auth = {int(r['tile']): r['region'] for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv'))}
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    f = rb.call("jawa/world_features_get", {"limit": 100})
for ft in f.get("features", []):
    regs = Counter(auth.get(t) for t in (ft.get("sampleTiles") or []) if auth.get(t))
    hit = {r: n for r, n in regs.items() if r in ('Venom Wood','South Crags','Thornend')}
    if hit:
        print(f"live '{ft['name']}' ({ft['tileCount']} tiles) samples from old:", dict(regs))
