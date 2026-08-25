import sys, json, csv
sys.path.insert(0,r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
rb = RimBridge(h,p,t); rb.connect()
b=lambda r:{k:v for k,v in r.items() if k!="operation"}
print("settleable 16770:", json.dumps(b(rb.call("jawa/tile_settleable",{"tiles":"16770"})))[:220])
print("move:", json.dumps(b(rb.call("jawa/world_objects_set",{"ids":"191","tile":16770})))[:70])
print("commit:", json.dumps(b(rb.call("jawa/world_commit",{})))[:70])
objs = rb.call("jawa/world_objects_get", {"limit":5000})["objects"]
json.dump(objs, open(r'D:\Luke\dev\Rimworld\world\_organic\objects_live9.json','w'))
T={int(r['tile']):r for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\world\_now7.csv'))}
nb={int(r['tile']):[int(r['n%d'%i]) for i in range(6) if int(r['n%d'%i])>=0] for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\world\_organic\neighbors.csv'))}
S={o['tile']:o for o in objs if o.get('isSettlement')}
o=[x for x in objs if x.get('name')=='Ashfoot'][0]; r=T[o['tile']]
print("VERIFY Ashfoot tile",o['tile'],o['factionName'],r['biome'],r['feature'],r['lat']+"N",r['long']+"E","elev",r['elevation'],"temp",r['temperature'],"adj",[S[x]['name'] for x in nb[o['tile']] if x in S])
v=rb.call("jawa/world_objects_validate",{})
print("validate:", {k:v[k] for k in ('settlements','nullFactionSettlements','badTileCount','settlementsOnWater','settlementsOnImpassable','stackedTiles')})
