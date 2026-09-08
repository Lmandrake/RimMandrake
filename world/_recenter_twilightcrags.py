import sys, csv, math, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
geo={int(r['tile']):r for r in csv.DictReader(open(r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv"))}
cur={t:g['biome'] for t,g in geo.items()}
for pf in ('world/backside_reband_full.json','world/pf_terminator_plan.json','world/wasteland_reclaim_plan.json','world/crag_meander_plan.json','world/pf_meander_plan.json','world/graycrags_coldonly_plan.json'):
    for p in json.load(open(pf)): cur[p['tile']]=p['to']
# crag tiles within the Twilight Crags region
tc_crags=[t for t,g in geo.items() if g['region']=='Twilight Crags' and cur[t]=='AB_RockyCrags']
tot=[t for t,g in geo.items() if g['region']=='Twilight Crags']
print(f"Twilight Crags region: {len(tot)} tiles, {len(tc_crags)} are crag")
def xyz(t):
    la,lo=math.radians(float(geo[t]['lat'])),math.radians(float(geo[t]['lon'])); return (math.cos(la)*math.cos(lo),math.cos(la)*math.sin(lo),math.sin(la))
pool=tc_crags or tot
cx=sum(xyz(t)[0] for t in pool)/len(pool); cy=sum(xyz(t)[1] for t in pool)/len(pool); cz=sum(xyz(t)[2] for t in pool)/len(pool)
center=max(pool, key=lambda t:(lambda p:p[0]*cx+p[1]*cy+p[2]*cz)(xyz(t)))
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    feats={f['name']:f for f in rb.call("jawa/world_features_get", {"limit":300}).get("features",[])}
    if 'Twilight Crags' not in feats: print("no Twilight Crags feature; names:", [n for n in feats if 'wilight' in n or 'rag' in n][:8]); sys.exit(1)
    fid=feats['Twilight Crags']['uniqueID']
    r=rb.call("jawa/world_features_set", {"action":"update","featureId":fid,"centerOnTile":center})
    rb.call("jawa/world_commit", {})
    print("recentered Twilight Crags on crag tile", center, "biome", cur[center], "success:", r.get('success'))
