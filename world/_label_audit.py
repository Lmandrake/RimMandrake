import sys, csv, json, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
geo={int(r['tile']):r for r in csv.DictReader(open(r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv"))}
cur={t:g['biome'] for t,g in geo.items()}
for pf in ('world/backside_reband_full.json','world/pf_terminator_plan.json','world/wasteland_reclaim_plan.json','world/crag_meander_plan.json','world/pf_meander_plan.json','world/graycrags_coldonly_plan.json'):
    for p in json.load(open(pf)): cur[p['tile']]=p['to']
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    feats=rb.call("jawa/world_features_get", {"limit":400, "sampleTiles":40}).get("features",[])
    print(f"total features: {len(feats)}")
    # for each feature: its label tile's biome, and the dominant biome of its member tiles
    rows=[]
    for f in feats:
        name=f.get('name'); samples=f.get('sampleTiles') or []
        # region tiles by CSV region name matching the feature name
        regtiles=[t for t,g in geo.items() if g['region']==name]
        pool=regtiles or samples
        if not pool: continue
        dc=f.get('drawCenter',{})
        biomes=collections.Counter(cur.get(t) for t in pool)
        dom=biomes.most_common(1)[0]
        # is this a nightside feature? arc median > 90
        arcs=[float(geo[t]['arc']) for t in pool if t in geo]
        if not arcs: continue
        arcmed=sorted(arcs)[len(arcs)//2]
        rows.append((arcmed, name, len(pool), dom[0], round(100*dom[1]/len(pool)), biomes.most_common(3)))
    rows.sort(reverse=True)
    print("=== NIGHTSIDE features (arc>90), label name | tiles | dominant biome | mix ===")
    for arcmed,name,n,dom,pct,mix in rows:
        if arcmed>90:
            print(f"  arc{arcmed:.0f} {name:16s} {n:4d} | {dom} {pct}% | {[(b,c) for b,c in mix]}")
