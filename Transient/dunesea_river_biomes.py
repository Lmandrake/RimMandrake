import sys, csv
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
auth = {int(r['tile']): r for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv'))}
ds = [t for t,r in auth.items() if r['region']=='Dune Sea']
host, port, token = resolve_endpoint()
riv = []
with RimBridge(host, port, token) as rb:
    for i in range(0, len(ds), 100):
        r = rb.call("jawa/world_tile_get", {"tiles": ",".join(map(str, ds[i:i+100])), "limit": 100})
        riv += [row for row in r.get("tiles", []) if row.get("riverCount", 0) > 0]
print(f"Dune Sea river tiles: {len(riv)}")
print("by biome:", dict(Counter(r['biome'] for r in riv).most_common()))
