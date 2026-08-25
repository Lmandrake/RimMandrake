import sys, json, csv, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0,r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
rb = RimBridge(h,p,t); rb.connect()
b=lambda r:{k:v for k,v in r.items() if k!="operation"}
print("settleable 9451:", json.dumps(b(rb.call("jawa/tile_settleable",{"tiles":"9451"})))[:200])
print("move:", json.dumps(b(rb.call("jawa/world_objects_set",{"ids":"159","tile":9451})))[:70])
print("commit:", json.dumps(b(rb.call("jawa/world_commit",{})))[:70])
objs = rb.call("jawa/world_objects_get", {"limit":5000})["objects"]
json.dump(objs, open(r'D:\Luke\dev\Rimworld\world\_organic\objects_live21.json','w'))
T={int(r['tile']):r for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\world\_now7.csv'))}
nb={int(r['tile']):[int(r['n%d'%i]) for i in range(6) if int(r['n%d'%i])>=0] for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\world\_organic\neighbors.csv'))}
S={o['tile']:o for o in objs if o.get('isSettlement')}
o=[x for x in objs if x.get('name')=="Deepwater Hold"][0]; r=T[o['tile']]
sea=[n for n in nb[o['tile']] if T[n]['biome'] in ('Ocean','Lake')]
print("VERIFY tile",o['tile'],o['factionName'],r['biome'],r['feature'],r['lat']+"N",r['long']+"E","oceanNeighbours",len(sea),"adj",[S[x]['name'] for x in nb[o['tile']] if x in S])
v=rb.call("jawa/world_objects_validate",{})
print("validate:", {k:v[k] for k in ('settlements','nullFactionSettlements','badTileCount','settlementsOnWater','settlementsOnImpassable','stackedTiles')})
