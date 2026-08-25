import sys, json, csv, math
sys.path.insert(0,r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
rb = RimBridge(h,p,t); rb.connect()
b=lambda r:{k:v for k,v in r.items() if k!="operation"}
print("settleable 10104:", json.dumps(b(rb.call("jawa/tile_settleable",{"tiles":"10104"})))[:220])
print("move:", json.dumps(b(rb.call("jawa/world_objects_set",{"ids":"188","tile":10104,"name":"Razorsand"})))[:70])
print("commit:", json.dumps(b(rb.call("jawa/world_commit",{})))[:70])
objs = rb.call("jawa/world_objects_get", {"limit":5000})["objects"]
json.dump(objs, open(r'D:\Luke\dev\Rimworld\world\_organic\objects_live10.json','w'))
T={int(r['tile']):r for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\world\_now7.csv'))}
nb={int(r['tile']):[int(r['n%d'%i]) for i in range(6) if int(r['n%d'%i])>=0] for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\world\_organic\neighbors.csv'))}
S={o['tile']:o for o in objs if o.get('isSettlement')}
o=[x for x in objs if x.get('name')=='Razorsand'][0]; r=T[o['tile']]
print("VERIFY Razorsand tile",o['tile'],o['factionName'],r['biome'],r['feature'],r['lat']+"N",r['long']+"E","adj",[S[x]['name'] for x in nb[o['tile']] if x in S])
print("Dry Moot gone?", not any(x.get('name')=='The Dry Moot' for x in objs))
def xyz(la,lo):
    la=math.radians(la);lo=math.radians(lo); return (math.cos(la)*math.cos(lo),math.cos(la)*math.sin(lo),math.sin(la))
def gc(x,y):
    dd=sum(p*q for p,q in zip(x,y));return math.degrees(math.acos(max(-1,min(1,dd))))
sf=T[15509]
print("degrees to Sufferband:", round(gc(xyz(float(r['lat']),float(r['long'])),xyz(float(sf['lat']),float(sf['long']))),2))
v=rb.call("jawa/world_objects_validate",{})
print("validate:", {k:v[k] for k in ('settlements','nullFactionSettlements','badTileCount','settlementsOnWater','settlementsOnImpassable','stackedTiles')})
