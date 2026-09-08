import sys, csv
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
geo={int(r['tile']):r for r in csv.DictReader(open(r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv"))}
level_tiles=[t for t,g in geo.items() if g['region']=='Level']
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    feats={f['name']:f for f in rb.call("jawa/world_features_get", {"limit":300}).get("features",[])}
    kn_id=feats['Knuckles']['uniqueID']; lvl_id=feats['Level']['uniqueID']
    print("Knuckles uid", kn_id, "| Level uid", lvl_id, "| Level tiles", len(level_tiles))
    r=rb.call("jawa/world_features_set", {"action":"assign","featureId":kn_id,"tiles":",".join(map(str,level_tiles))})
    print("assign:", r.get('success'), {k:r.get(k) for k in ('assigned','written','tileCount','message') if r.get(k) is not None})
    d=rb.call("jawa/world_features_set", {"action":"delete","featureId":lvl_id})
    print("delete Level:", d.get('success'), d.get('message'))
    rb.call("jawa/world_commit", {})
    n2={f['name']:f for f in rb.call("jawa/world_features_get", {"limit":300}).get("features",[])}
    print("Level exists?", 'Level' in n2, "| Knuckles tileCount:", n2.get('Knuckles',{}).get('tileCount'))
