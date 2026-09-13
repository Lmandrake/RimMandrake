import sys, csv
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
rows = list(csv.DictReader(open(r'D:\Luke\dev\Rimworld\Transient\v24_tiles_after_rot_tail.csv')))
ww = [int(r['tile']) for r in rows if r['biome']=='AB_FeraliskInfestedJungle']
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    riv = []
    for i in range(0, len(ww), 100):
        r = rb.call("jawa/world_tile_get", {"tiles": ",".join(map(str, ww[i:i+100])), "limit": 100})
        riv += [row for row in r.get("tiles", []) if row.get("riverCount",0) > 0]
    for row in riv:
        print(f"tile {row['tile']}: riverCount {row['riverCount']}, riverDist {row['riverDist']}, feature {row.get('feature')}")
