import sys, csv
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
rot = [int(r['tile']) for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\Transient\v24_tiles_after_rot_tail.csv')) if r['biome']=='AB_MycoticJungle']
host, port, token = resolve_endpoint()
cnt = Counter()
with RimBridge(host, port, token) as rb:
    for i in range(0, len(rot), 100):
        r = rb.call("jawa/world_tile_get", {"tiles": ",".join(map(str, rot[i:i+100])), "limit": 100})
        for row in r.get("tiles", []): cnt[row.get('feature') or '(none)'] += 1
print("total:", sum(cnt.values()))
print(dict(cnt.most_common(8)), f"... +{len(cnt)-8} more")
