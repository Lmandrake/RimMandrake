import sys, csv, json
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
live = [int(r['tile']) for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\Transient\v24_tiles_live.csv')) if r['biome'] in ('AB_PropaneLakes','RUT_PropaneLake')]
host, port, token = resolve_endpoint()
cnt, lakecnt = Counter(), Counter()
with RimBridge(host, port, token) as rb:
    for i in range(0, len(live), 100):
        chunk = live[i:i+100]
        r = rb.call("jawa/world_tile_get", {"tiles": ",".join(map(str, chunk)), "limit": 100})
        for row in r.get("tiles", []):
            (lakecnt if row['biome']=='RUT_PropaneLake' else cnt)[row.get('feature') or '(none)'] += 1
print("AB_PropaneLakes live features:", dict(cnt.most_common()))
print("RUT_PropaneLake live features:", dict(lakecnt.most_common()))
print("total:", sum(cnt.values()), "+", sum(lakecnt.values()))
