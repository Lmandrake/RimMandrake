import sys, csv
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
rows = list(csv.DictReader(open(r'D:\Luke\dev\Rimworld\Transient\v24_tiles_after_rot_tail.csv')))
auth = {int(r['tile']): r for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv'))}
targets = {
  'Greentide (BiomeCypreJungle)': [int(r['tile']) for r in rows if r['biome']=='BiomeCypreJungle'],
  'Webwork (AB_FeraliskInfestedJungle)': [int(r['tile']) for r in rows if r['biome']=='AB_FeraliskInfestedJungle'],
  'DuneSea region (any biome)': [int(t) for t,r in auth.items() if r['region']=='Dune Sea'],
}
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for name, tiles in targets.items():
        riv = 0; n = 0
        for i in range(0, len(tiles), 100):
            r = rb.call("jawa/world_tile_get", {"tiles": ",".join(map(str, tiles[i:i+100])), "limit": 100})
            for row in r.get("tiles", []):
                n += 1
                if row.get("riverCount", 0) > 0: riv += 1
        print(f"{name}: {n} tiles, {riv} with river ({100*riv/max(n,1):.0f}%)")
